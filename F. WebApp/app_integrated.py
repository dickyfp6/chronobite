"""
Nutrition DSS - Flask Web Application (Fully Integrated)
Sistem Rekomendasi Nutrisi berbasis Algoritma Genetika dan Greedy

Integration dengan:
- C. System Flow (NutritionService for calculations)
- D. Model (Greedy Algorithm for menu generation)
- Frontend (React with Vite)
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
import json
import pandas as pd
from datetime import datetime
import importlib.util

# Add parent directories untuk imports (F. WebApp is one level deep, so one .. to get to root)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'C. System Flow'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'D. Model'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'D. Model', 'Greedy Algorithm'))

# Import system components
try:
    from nutrition_service import NutritionService  # pyright: ignore
    from meal_schema import FoodItem  # type: ignore
    print("✓ NutritionService and FoodItem imported successfully")
except ImportError as e:
    print(f"❌ Failed to import NutritionService or FoodItem: {e}")
    NutritionService = None
    FoodItem = None

# Special handling for Greedy Algorithm (folder has space in name)
GreedyAlgorithmInterface = None
try:
    greedy_path = os.path.join(os.path.dirname(__file__), '..', 'D. Model', 'greedy', 'greedy_interface.py')
    spec = importlib.util.spec_from_file_location("greedy_interface", greedy_path)
    if spec is not None and spec.loader is not None:
        greedy_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(greedy_module)
        GreedyAlgorithmInterface = greedy_module.GreedyAlgorithmInterface
        print("✓ GreedyAlgorithmInterface imported successfully")
    else:
        print("❌ Failed to create spec for GreedyAlgorithmInterface")
except Exception as e:
    print(f"❌ Failed to import GreedyAlgorithmInterface: {e}")

# Initialize Flask app (pure API, no static files)
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Enable CORS for React frontend (Vercel deployment)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Global service instances (initialize on first request)
nutrition_service = None
greedy_algorithm = None

def init_services():
    """Initialize NutritionService and GreedyAlgorithm on first use"""
    global nutrition_service, greedy_algorithm
    
    if nutrition_service is None and NutritionService:
        try:
            nutrition_service = NutritionService()
            print("✓ NutritionService initialized")
        except Exception as e:
            print(f"❌ Failed to initialize NutritionService: {e}")
    
    if greedy_algorithm is None and GreedyAlgorithmInterface:
        try:
            greedy_algorithm = GreedyAlgorithmInterface()
            print("✓ GreedyAlgorithmInterface initialized")
        except Exception as e:
            print(f"❌ Failed to initialize GreedyAlgorithmInterface: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# LEGACY HELPER FUNCTIONS (For compatibility)
# ═══════════════════════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def sanitize_infinity(obj):
    """
    Recursively replace float('inf') dengan null untuk JSON serialization
    """
    if isinstance(obj, dict):
        return {k: sanitize_infinity(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_infinity(v) for v in obj]
    elif isinstance(obj, float):
        if obj == float('inf'):
            return None
        return obj
    return obj


def calculate_bmi(weight, height):
    h = height / 100
    bmi = weight / (h ** 2)
    if bmi < 18.5:
        cat = "Underweight"
        color = "blue"
    elif bmi < 25:
        cat = "Normal"
        color = "green"
    elif bmi < 30:
        cat = "Overweight"
        color = "yellow"
    else:
        cat = "Obesitas"
        color = "red"
    return round(bmi, 1), cat, color


def calculate_bbi(height, gender):
    if gender == "M":
        return round((height - 100) * 0.9, 1)
    return round((height - 100) * 0.85, 1)


def calculate_bmr(weight, height, age, gender):
    if gender == "M":
        return round(88.362 + 13.397 * weight + 4.799 * height - 5.677 * age, 0)
    return round(447.593 + 9.247 * weight + 3.098 * height - 4.330 * age, 0)


def calculate_tdee(bmr, activity):
    return round(bmr * float(activity), 0)


def _course_to_item(course):
    candidate = course.candidates[0] if getattr(course, 'candidates', None) and len(course.candidates) > 0 else None
    if candidate is None:
        return {
            'name': course.course_type,
            'serving_size': 100,
            'calories': 0,
            'score': 0,
            'main_ingredients': [],
            'macros': {'carbs': 0, 'protein': 0, 'fat': 0},
        }

    return {
        'fdc_id': getattr(candidate, 'fdc_id', 'unknown'),
        'name': candidate.food_name,
        'food_group': getattr(candidate, 'food_group', 'Unknown'),
        'cuisine_label': getattr(candidate, 'cuisine_label', 'Unknown'),
        'serving_size': round(getattr(candidate, 'portion_gram', 100), 1),
        'calories': round(getattr(candidate, 'energy_kcal', 0), 1),
        'score': 100,
        'food_category': getattr(candidate, 'consumption_label', course.course_type),
        'main_ingredients': [candidate.food_name],
        'macros': {
            'carbs': round(getattr(candidate, 'carbohydrate_g', 0), 2),
            'protein': round(getattr(candidate, 'protein_g', 0), 2),
            'fat': round(getattr(candidate, 'fat_g', 0), 2),
        },
        'micronutrients': [],
        'halal_status': 'unknown',
    }


def _meal_to_frontend(meal):
    items = []
    if getattr(meal, 'courses', None):
        for course in meal.courses.values():
            items.append(_course_to_item(course))

    total_calories = sum(item['calories'] for item in items)
    total_carbs = sum(item['macros']['carbs'] for item in items)
    total_protein = sum(item['macros']['protein'] for item in items)
    total_fat = sum(item['macros']['fat'] for item in items)

    return {
        'total_calories': total_calories,
        'items': items,
        'macros': {
            'carbs': total_carbs,
            'protein': total_protein,
            'fat': total_fat,
        }
    }


def _menu_plan_to_frontend(menu_plan):
    return {
        'algorithm_used': getattr(menu_plan, 'algorithm_used', 'Greedy'),
        'user_profile': getattr(menu_plan, 'user_profile', {}),
        'breakfast': _meal_to_frontend(getattr(menu_plan, 'breakfast', None)),
        'lunch': _meal_to_frontend(getattr(menu_plan, 'lunch', None)),
        'dinner': _meal_to_frontend(getattr(menu_plan, 'dinner', None)),
        'snack': _meal_to_frontend(getattr(menu_plan, 'snack', None)),
        'total_calories': getattr(menu_plan, 'total_calories', getattr(menu_plan, 'total_daily_calories', 0)),
        'feasible': getattr(menu_plan, 'feasible', True),
        'violations': getattr(menu_plan, 'violations', []),
    }


def classify_age_group(age):
    """Klasifikasi usia berdasarkan WHO guidelines"""
    if age <= 17:
        return {"group": "minors", "label": "Minors", "range": "0-17 years"}
    elif age <= 65:
        return {"group": "young_people", "label": "Young People", "range": "18-65 years"}
    elif age <= 79:
        return {"group": "middle_aged", "label": "Middle-Aged", "range": "66-79 years"}
    elif age <= 99:
        return {"group": "elderly", "label": "Elderly People", "range": "80-99 years"}
    else:
        return {"group": "very_elderly", "label": "Very Elderly", "range": "100+ years"}


# ═══════════════════════════════════════════════════════════════════════════════
# DISEASE & CONFIGURATION CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

DISEASE_MACROS = {
    "normal":       {"carbs": (45, 65), "protein": (10, 35), "fat": (20, 35)},
    "dm2":          {"carbs": (45, 55), "protein": (15, 20), "fat": (25, 35)},
    "hypertension": {"carbs": (50, 60), "protein": (15, 20), "fat": (25, 30)},
    "cvd":          {"carbs": (45, 55), "protein": (15, 25), "fat": (20, 30)},
    "cholesterol":  {"carbs": (45, 55), "protein": (15, 20), "fat": (20, 30)},
    "ckd":          {"carbs": (50, 60), "protein": (5,  10), "fat": (25, 35)},
}

DISEASE_LABELS = {
    "normal":       "Normal",
    "dm2":          "Diabetes Tipe 2",
    "hypertension": "Hipertensi",
    "cvd":          "Penyakit Kardiovaskular",
    "cholesterol":  "Kolesterol Tinggi",
    "ckd":          "Penyakit Ginjal Kronis",
}

ACTIVITY_LABELS = {
    "1.545": "Sedentary or Light Activity",
    "1.845": "Active or Moderately Active",
    "2.2":   "Vigorous or Vigorously Active",
}

# Map activity labels (from Frontend) to numeric factors
ACTIVITY_MAP = {
    "sedentary": 1.545,
    "light": 1.545,
    "moderate": 1.845,
    "active": 1.845,
    "vigorous": 2.2,
    "very_active": 2.2,
    # Also accept numeric strings directly
    "1.545": 1.545,
    "1.845": 1.845,
    "2.2": 2.2,
}

FOOD_PREFERENCES_LABELS = {
    "Western":       "Western",
    "Asian":         "Asian",
    "Mediterranean": "Mediterranean",
}

ALGORITHM_LABELS = {
    "greedy": "⚡ Greedy (Fast)",
    "genetic": "🧬 Genetic (Optimal - Coming Soon)",
}


# ═══════════════════════════════════════════════════════════════════════════════
# HEALTH CHECK ENDPOINT
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "Nutrition DSS Backend API"}), 200


# ═══════════════════════════════════════════════════════════════════════════════
# API ENDPOINTS: CALCULATION & ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/api/analyze", methods=["POST"])
def analyze():
    """
    ENDPOINT 1: Analyze user profile dan calculate nutrition needs
    
    Input (JSON from form):
    {
        "gender": "M",
        "age": 30,
        "weight": 70.0,
        "height": 170.0,
        "activity": "1.845",
        "diseases": ["normal"] atau ["dm2", "hypertension"],
        "food_preferences": [] atau ["Asian", "Western"]
    }
    
    Output:
    {
        "success": true,
        "user_input": {...},
        "anthropometrics": {
            "bmi": 24.2,
            "bmi_category": "Normal",
            "bmi_color": "green",
            "bbi": 63.0,
            "age_group": {...},
            ...
        },
        "energy": {
            "bmr": 1750,
            "tdee": 3228
        },
        "guidelines": {
            "nutrients": {...}
        },
        "meal_distribution": {
            "breakfast": 0.2375,
            "lunch": 0.3375,
            ...
        },
        "food_data": {
            "total_items": 1234
        }
    }
    """
    try:
        init_services()
        
        if nutrition_service is None:
            return jsonify({
                "success": False,
                "error": "NutritionService not available"
            }), 500
        
        data = request.get_json()
        
        # Parse activity level (map label to numeric if needed)
        activity_input = data.get('activity', '1.845')
        if isinstance(activity_input, str):
            activity_input = activity_input.lower()
            activity_factor = ACTIVITY_MAP.get(activity_input, 1.845)
        else:
            activity_factor = float(activity_input)
        
        # Parse user input
        user_input = {
            'gender': data.get('gender', 'M'),
            'age': int(data.get('age', 30)),
            'weight': float(data.get('weight', 70)),
            'height': float(data.get('height', 170)),
            'activity_factor': activity_factor,
            'disease': data.get('diseases', ['normal']),
            'food_preferences': data.get('food_preferences', [])
        }
        
        # Validate input ranges (dari System Flow)
        errors = []
        if not 18 <= user_input['age'] <= 100:
            errors.append("Age must be 18-100")
        if not 100 <= user_input['height'] <= 300:
            errors.append("Height must be 100-300 cm")
        if user_input['weight'] <= 0:
            errors.append("Weight must be positive")
        
        if errors:
            error_msg = ", ".join(errors)
            print(f"⚠️ /api/analyze validation error: {error_msg}")
            return jsonify({
                "success": False,
                "error": error_msg
            }), 400
        
        # Calculate nutrition needs
        result = nutrition_service.calculate_nutrition_needs(user_input)
        
        if not result.get('success'):
            print(f"⚠️ /api/analyze calculation error: {result.get('error', 'Unknown error')}")
            return jsonify(result), 400
        
        # Add meal distribution untuk display
        result['meal_distribution'] = {
            'breakfast': 0.2375,  # 23.75%
            'lunch': 0.3375,      # 33.75%
            'snack': 0.1375,      # 13.75%
            'dinner': 0.2875      # 28.75%
        }

        # Remove non-JSON-serializable objects before response
        if isinstance(result.get('food_data'), dict):
            result['food_data'].pop('dataframe', None)
        
        # Sanitize infinity values to null for JSON serialization
        result = sanitize_infinity(result)
        
        return jsonify(result), 200
    
    except Exception as e:
        print(f"❌ /api/analyze error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/get-drinks", methods=["POST"])
def get_drinks():
    """
    PHASE 1: Generate 3 drink options for each meal
    """
    try:
        data = request.json
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
            
        analysis_data = data.get('analysis_data', {})
        user_input = data.get('user_input') or {}
        tdee = analysis_data.get('energy', {}).get('tdee', 2100)
        
        init_services()
        
        if greedy_algorithm is None:
            return jsonify({"success": False, "error": "Greedy Algorithm not available"}), 500
        
        # Setup database
        food_database = None
        if nutrition_service and nutrition_service.guideline_loader and nutrition_service.guideline_loader.food_df is not None:
            food_database = nutrition_service.guideline_loader.food_df.copy()
            
        if food_database is None:
            return jsonify({"success": False, "error": "Food database not available"}), 500
            
        # Initialize
        nutrition_guidelines = analysis_data.get('guidelines', {})
        greedy_algorithm.initialize(food_database, nutrition_guidelines)
        
        # Generate drinks
        drinks = greedy_algorithm.generate_drink_options(
            meal_distribution={
                'breakfast': 0.2375,
                'lunch': 0.3375,
                'snack': 0.1375,
                'dinner': 0.2875
            },
            user_tdee=tdee
        )
        
        if not drinks:
            return jsonify({"success": False, "error": "No drinks found"}), 500
            
        # Format for frontend
        formatted_drinks = {}
        for meal_time, items in drinks.items():
            formatted_drinks[meal_time] = []
            for item in items:
                # Wrap in a fake MealCourse for _course_to_item to work
                # Use local import for MealCourse to avoid circularity if any
                from meal_schema import MealCourse
                temp_course = MealCourse(course_type='Drink', candidates=[item], 
                                         total_calories=item.energy_kcal, total_protein_g=item.protein_g,
                                         total_carb_g=item.carbohydrate_g, total_fat_g=item.fat_g)
                formatted_drinks[meal_time].append(_course_to_item(temp_course))
                
        return jsonify({
            "success": True,
            "drinks": formatted_drinks
        }), 200
        
    except Exception as e:
        print(f"❌ /api/get-drinks error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/generate-final-menu", methods=["POST"])
def generate_final_menu():
    """
    PHASE 2: Generate final menu with fixed-drink selection
    """
    try:
        data = request.json
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
            
        analysis_data = data.get('analysis_data', {})
        user_input = data.get('user_input') or {}
        selected_drinks_json = data.get('selected_drinks', {})
        tdee = analysis_data.get('energy', {}).get('tdee', 2100)
        
        # Reconstruct FoodItems from JSON
        selected_drinks = {}
        if FoodItem is None:
            return jsonify({"success": False, "error": "FoodItem schema missing"}), 500
            
        for meal_time, drink_json in selected_drinks_json.items():
            if drink_json:
                selected_drinks[meal_time.lower()] = FoodItem(
                    fdc_id=str(drink_json.get('fdc_id', '0')),
                    food_name=drink_json.get('name', ''),
                    food_group=drink_json.get('food_group', ''),
                    consumption_label='Drink',
                    cuisine_label=drink_json.get('cuisine_label', ''),
                    portion_gram=float(drink_json.get('serving_size', 100)),
                    energy_kcal=float(drink_json.get('calories', 0)),
                    protein_g=float(drink_json.get('macros', {}).get('protein', 0)),
                    carbohydrate_g=float(drink_json.get('macros', {}).get('carbs', 0)),
                    fat_g=float(drink_json.get('macros', {}).get('fat', 0))
                )
        
        init_services()
        
        if greedy_algorithm is None:
            return jsonify({"success": False, "error": "Greedy Algorithm not available"}), 500
        
        # Setup database
        food_database = None
        if nutrition_service and nutrition_service.guideline_loader and nutrition_service.guideline_loader.food_df is not None:
            food_database = nutrition_service.guideline_loader.food_df.copy()
            
        if food_database is None:
            return jsonify({"success": False, "error": "Food database not available"}), 500
            
        # Initialize
        nutrition_guidelines = analysis_data.get('guidelines', {})
        greedy_algorithm.initialize(food_database, nutrition_guidelines)
        
        # Generate final plan
        menu_plan = greedy_algorithm.generate_menu_with_drinks(
            user_profile=user_input,
            meal_distribution={
                'breakfast': 0.2375,
                'lunch': 0.3375,
                'snack': 0.1375,
                'dinner': 0.2875
            },
            user_tdee=tdee,
            selected_drinks=selected_drinks
        )
        
        if not menu_plan:
            return jsonify({
                "success": False, 
                "error": "Failed to generate menu with chosen drinks. The drinks might be too caloric."
            }), 500
            
        return jsonify({
            "success": True,
            "menu_plan": _menu_plan_to_frontend(menu_plan)
        }), 200
        
    except Exception as e:
        print(f"❌ /api/generate-final-menu error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/generate-menu", methods=["POST"])
def generate_menu():
    """
    ENDPOINT 2: Generate meal menu menggunakan algorithm
    
    Input:
    {
        "algorithm": "greedy" atau "genetic",
        "user_profile": {...dari analyze result...},
        "analysis_data": {...dari analyze result...},
        "user_input": {...dari analyze result...}
    }
    
    Output:
    {
        "success": true,
        "menu_plan": {
            "algorithm_used": "Greedy",
            "breakfast": {...},
            "lunch": {...},
            "dinner": {...},
            "snack": {...},
            "total_calories": 2100,
            ...
        }
    }
    """
    try:
        init_services()
        
        if greedy_algorithm is None:
            return jsonify({
                "success": False,
                "error": "Greedy Algorithm not available"
            }), 500
        
        data = request.get_json()
        algorithm_choice = data.get('algorithm', 'greedy')
        
        if algorithm_choice != 'greedy':
            return jsonify({
                "success": False,
                "error": "Only Greedy algorithm is available. Genetic coming soon!"
            }), 400
        
        # Extract required data
        analysis_data = data.get('analysis_data', {})
        user_input = data.get('user_input') or data.get('user_profile') or {}
        if isinstance(user_input, dict) and 'user_input' in user_input:
            user_input = user_input.get('user_input', {})
        tdee = analysis_data.get('energy', {}).get('tdee', 2100)

        # Initialize Greedy Algorithm using server-side food database
        food_database = None
        if nutrition_service is not None and nutrition_service.guideline_loader is not None:
            base_df = nutrition_service.guideline_loader.food_df
            if base_df is not None:
                food_database = base_df.copy()

        # Optional cuisine filtering from user preferences
        food_preferences = user_input.get('food_preferences', []) if isinstance(user_input, dict) else []
        if food_database is not None and food_preferences:
            if 'cuisine' in food_database.columns:
                food_database = food_database[food_database['cuisine'].isin(food_preferences)].copy()
            elif 'cuisine_label' in food_database.columns:
                food_database = food_database[food_database['cuisine_label'].isin(food_preferences)].copy()

        nutrition_guidelines = analysis_data.get('guidelines', {})
        
        if food_database is None or nutrition_guidelines is None:
            return jsonify({
                "success": False,
                "error": "Missing food database or guidelines"
            }), 400
        
        success = greedy_algorithm.initialize(food_database, nutrition_guidelines)
        if not success:
            return jsonify({
                "success": False,
                "error": "Failed to initialize algorithm"
            }), 500
        
        # Generate menu
        menu_plan = greedy_algorithm.generate_menu_plan(
            user_profile=user_input,
            meal_distribution={
                'breakfast': 0.2375,
                'lunch': 0.3375,
                'snack': 0.1375,
                'dinner': 0.2875
            },
            user_tdee=tdee
        )
        
        if menu_plan is None:
            return jsonify({
                "success": False,
                "error": "Failed to generate menu (insufficient candidates)"
            }), 500
        
        # Convert to frontend-friendly dict for JSON response
        menu_dict = _menu_plan_to_frontend(menu_plan)
        
        # Sanitize infinity values to null for JSON serialization
        menu_dict = sanitize_infinity(menu_dict)
        
        return jsonify({
            "success": True,
            "menu_plan": menu_dict
        }), 200
    
    except Exception as e:
        print(f"❌ /api/generate-menu error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/refresh-menu", methods=["POST"])
def refresh_menu():
    """
    ENDPOINT 3: Regenerate menu dengan alternative candidates
    Same as generate-menu tapi dengan fresh random generation
    """
    # Same sebagai generate_menu - greedy algorithm otomatis generate alternatives
    return generate_menu()


@app.route("/api/health-check", methods=["GET"])
def health_check_services():
    """Health check endpoint untuk debugging"""
    return jsonify({
        "status": "ok",
        "services": {
            "nutrition_service": nutrition_service is not None,
            "greedy_algorithm": greedy_algorithm is not None,
        },
        "timestamp": datetime.now().isoformat()
    })


# ═════════════════════════════════════════════════════════════════════════════════
# ERROR HANDLERS
# ═════════════════════════════════════════════════════════════════════════════════

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Internal server error"}), 500


# ═════════════════════════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    init_services()
    app.run(debug=True, port=5000)

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
import uuid
import threading

# Global job store
jobs = {}

# Add parent directories untuk imports (F. WebApp is one level deep, so one .. to get to root)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'C. System Flow'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'D. Model'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'D. Model', 'greedy'))

# Import system components
try:
    from nutrition_service import NutritionService  # pyright: ignore
    from meal_schema import FoodItem  # type: ignore
    print("[OK] NutritionService and FoodItem imported successfully")
except ImportError as e:
    print(f"[ERROR] Failed to import NutritionService or FoodItem: {e}")
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
        print("[OK] GreedyAlgorithmInterface imported successfully")
    else:
        print("[ERROR] Failed to create spec for GreedyAlgorithmInterface")
except Exception as e:
    print(f"[ERROR] Failed to import GreedyAlgorithmInterface: {e}")

# Special handling for Genetic Algorithm
GeneticAlgorithmInterface = None
try:
    ga_path = os.path.join(os.path.dirname(__file__), '..', 'D. Model', 'Genetic Algorithm', 'ga_interface.py')
    spec = importlib.util.spec_from_file_location("ga_interface", ga_path)
    if spec is not None and spec.loader is not None:
        ga_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ga_module)
        GeneticAlgorithmInterface = ga_module.GeneticAlgorithmInterface
        print("[OK] GeneticAlgorithmInterface imported successfully")
    else:
        print("[ERROR] Failed to create spec for GeneticAlgorithmInterface")
except Exception as e:
    print(f"[ERROR] Failed to import GeneticAlgorithmInterface: {e}")

# Initialize Flask app (pure API, no static files)
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Enable CORS for React frontend (allow all origins for Vercel/production deployment)
CORS_CONFIG = {
    "origins": "*",
    "methods": ["GET", "POST", "OPTIONS"],
    "allow_headers": ["Content-Type"]
}

CORS(app, resources={r"/api/*": CORS_CONFIG}) # type: ignore

def get_allowed_origin():
    """Reads allowed origin from CORS_CONFIG and matches it with Request Origin"""
    origins = CORS_CONFIG.get("origins", "*")
    if origins == "*":
        return "*"
    
    # Check if request has an Origin header
    origin_header = request.headers.get("Origin")
    if not origin_header:
        return ""
        
    if isinstance(origins, list):
        if origin_header in origins:
            return origin_header
    elif isinstance(origins, str):
        if origin_header == origins:
            return origin_header
            
    return ""


# Global service instances (initialize on first request)
nutrition_service = None
greedy_algorithm = None
genetic_algorithm = None

def init_services():
    """Initialize NutritionService and Algorithms on first use"""
    global nutrition_service, greedy_algorithm, genetic_algorithm
    
    if nutrition_service is None and NutritionService:
        try:
            nutrition_service = NutritionService()
            print("[OK] NutritionService initialized")
        except Exception as e:
            print(f"[ERROR] Failed to initialize NutritionService: {e}")
    
    if greedy_algorithm is None and GreedyAlgorithmInterface:
        try:
            greedy_algorithm = GreedyAlgorithmInterface(pd.DataFrame(), {})
            print("[OK] GreedyAlgorithmInterface initialized")
        except Exception as e:
            print(f"[ERROR] Failed to initialize GreedyAlgorithmInterface: {e}")
            
    if genetic_algorithm is None and GeneticAlgorithmInterface:
        try:
            genetic_algorithm = GeneticAlgorithmInterface(pd.DataFrame(), {})
            print("[OK] GeneticAlgorithmInterface initialized")
        except Exception as e:
            print(f"[ERROR] Failed to initialize GeneticAlgorithmInterface: {e}")

# Eagerly initialize services on module load (avoids request-time cold-start latency)
init_services()


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


def _course_to_all_candidates(course):
    """Return all 3 candidates for a course"""
    if not getattr(course, 'candidates', None):
        return []
    
    candidates = []
    for idx, candidate in enumerate(course.candidates):
        candidates.append({
            'fdc_id': getattr(candidate, 'fdc_id', 'unknown'),
            'name': candidate.food_name,
            'food_group': getattr(candidate, 'food_group', ''),
            'cuisine_label': getattr(candidate, 'cuisine_label', ''),
            'consumption_label': getattr(candidate, 'consumption_label', ''),
            'serving_size': round(getattr(candidate, 'portion_gram', 100), 1),
            'calories': round(getattr(candidate, 'energy_kcal', 0), 1),
            'protein': round(getattr(candidate, 'protein_g', 0), 2),
            'carbs': round(getattr(candidate, 'carbohydrate_g', 0), 2),
            'fat': round(getattr(candidate, 'fat_g', 0), 2),
            'is_selected': idx == 0,
        })
    return candidates


def _menu_plan_to_frontend(menu_plan):
    def meal_to_dict(meal):
        if meal is None:
            return None
        
        if getattr(meal, 'meal_type', '') == 'Snack':
            return {
                'meal_type': 'Snack',
                'target_calories': round(getattr(meal, 'target_calories', 0), 1),
                'actual_calories': round(getattr(meal, 'actual_calories', 0), 1),
                'candidates': _course_to_all_candidates(
                    type('obj', (object,), {'candidates': meal.candidates})()
                )
            }
        
        courses = {}
        if getattr(meal, 'courses', None):
            for course_type, course in meal.courses.items():
                courses[course_type] = {
                    'course_type': course_type,
                    'candidates': _course_to_all_candidates(course)
                }
        
        return {
            'meal_type': getattr(meal, 'meal_type', ''),
            'target_calories': round(getattr(meal, 'target_calories', 0), 1),
            'actual_calories': round(getattr(meal, 'actual_calories', 0), 1),
            'courses': courses
        }
    
    return {
        'algorithm_used': getattr(menu_plan, 'algorithm_used', 'Greedy'),
        'breakfast': meal_to_dict(getattr(menu_plan, 'breakfast', None)),
        'lunch': meal_to_dict(getattr(menu_plan, 'lunch', None)),
        'dinner': meal_to_dict(getattr(menu_plan, 'dinner', None)),
        'snack': meal_to_dict(getattr(menu_plan, 'snack', None)),
        'total_daily_calories': round(getattr(menu_plan, 'total_daily_calories', 0), 1),
        'total_daily_protein_g': round(getattr(menu_plan, 'total_daily_protein_g', 0), 2),
        'total_daily_carb_g': round(getattr(menu_plan, 'total_daily_carb_g', 0), 2),
        'total_daily_fat_g': round(getattr(menu_plan, 'total_daily_fat_g', 0), 2),
        'daily_micronutrients': getattr(menu_plan, 'daily_micronutrients', {}),
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
            print(f"[WARNING] /api/analyze validation error: {error_msg}")
            return jsonify({
                "success": False,
                "error": error_msg
            }), 400
        
        # Calculate nutrition needs
        result = nutrition_service.calculate_nutrition_needs(user_input)
        
        if not result.get('success'):
            print(f"[WARNING] /api/analyze calculation error: {result.get('error', 'Unknown error')}")
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
        print(f"[ERROR] /api/analyze error: {e}")
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
        
        algorithm_choice = data.get('algorithm', 'greedy')
        
        algorithm_engine = genetic_algorithm if algorithm_choice == 'genetic' else greedy_algorithm
        
        if algorithm_engine is None:
            return jsonify({"success": False, "error": f"{algorithm_choice} algorithm not available"}), 500
        
        # Setup database
        food_database = None
        if nutrition_service and nutrition_service.guideline_loader and nutrition_service.guideline_loader.food_df is not None:
            food_database = nutrition_service.guideline_loader.food_df.copy()
            
        if food_database is None:
            return jsonify({"success": False, "error": "Food database not available"}), 500
            
        # Initialize
        nutrition_guidelines = analysis_data.get('guidelines', {})
        algorithm_engine.initialize(food_database, nutrition_guidelines)
        
        # Generate drinks
        drinks = algorithm_engine.generate_drink_options(
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
                from meal_schema import MealCourse
                temp_course = MealCourse(course_type='Drink', candidates=[item], 
                                         total_calories=item.energy_kcal, total_protein_g=item.protein_g,
                                         total_carb_g=item.carbohydrate_g, total_fat_g=item.fat_g)
                formatted_drinks[meal_time].append(_course_to_all_candidates(temp_course)[0])
                
        return jsonify({
            "success": True,
            "drinks": formatted_drinks
        }), 200
        
    except Exception as e:
        print(f"[ERROR] /api/get-drinks error: {e}")
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
        
        algorithm_choice = data.get('algorithm', 'greedy')
        
        algorithm_engine = genetic_algorithm if algorithm_choice == 'genetic' else greedy_algorithm
        
        if algorithm_engine is None:
            return jsonify({"success": False, "error": f"{algorithm_choice} algorithm not available"}), 500
        
        # Setup database
        food_database = None
        if nutrition_service and nutrition_service.guideline_loader and nutrition_service.guideline_loader.food_df is not None:
            food_database = nutrition_service.guideline_loader.food_df.copy()
            
        if food_database is None:
            return jsonify({"success": False, "error": "Food database not available"}), 500
            
        # Initialize
        nutrition_guidelines = analysis_data.get('guidelines', {})
        algorithm_engine.initialize(food_database, nutrition_guidelines)
        
        # Generate final plan
        import time
        kwargs = {}
        if algorithm_choice == 'genetic':
            kwargs['deadline'] = time.time() + 150.0  # Apply Solution 1: 150s deadline
        menu_plan = algorithm_engine.generate_menu_with_drinks(
            user_profile=user_input,
            meal_distribution={
                'breakfast': 0.2375,
                'lunch': 0.3375,
                'snack': 0.1375,
                'dinner': 0.2875
            },
            user_tdee=tdee,
            selected_drinks=selected_drinks,
            **kwargs
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
        print(f"[ERROR] /api/generate-final-menu error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


def _run_ga_job(job_id, algorithm_choice, food_database, nutrition_guidelines, tdee, user_input):
    """
    Background worker function to run Genetic or Greedy optimization.
    """
    import time
    start_time = time.time()
    try:
        if algorithm_choice == 'genetic':
            if genetic_algorithm is None:
                jobs[job_id] = {"status": "error", "result": None, "error": "Genetic Algorithm not available"}
                return
            if food_database is None:
                jobs[job_id] = {"status": "error", "result": None, "error": "Food database not available"}
                return
            
            genetic_algorithm.initialize(food_database, nutrition_guidelines)
            # Apply Solution 1: 150s deadline
            menu_plan = genetic_algorithm.generate_menu_plan(
                user_profile=user_input,
                tdee=tdee,
                deadline=start_time + 150.0
            )
        else:
            if greedy_algorithm is None:
                jobs[job_id] = {"status": "error", "result": None, "error": "Greedy Algorithm not available"}
                return
            if food_database is None or nutrition_guidelines is None:
                jobs[job_id] = {"status": "error", "result": None, "error": "Missing food database or guidelines"}
                return
            
            try:
                greedy_algorithm.initialize(food_database, nutrition_guidelines)
            except Exception as init_err:
                jobs[job_id] = {"status": "error", "result": None, "error": f"Failed to initialize algorithm: {init_err}"}
                return
                
            menu_plan = greedy_algorithm.generate_menu_plan(
                user_profile=user_input,
                tdee=tdee
            )
            
        if menu_plan is None:
            jobs[job_id] = {
                "status": "error",
                "result": None,
                "error": f"Failed to generate menu with {algorithm_choice} algorithm"
            }
            return
            
        menu_dict = _menu_plan_to_frontend(menu_plan)
        menu_dict = sanitize_infinity(menu_dict)
        
        jobs[job_id] = {
            "status": "done",
            "result": menu_dict,
            "error": None
        }
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[ERROR] _run_ga_job exception: {e}\n{error_details}")
        jobs[job_id] = {
            "status": "error",
            "result": None,
            "error": str(e)
        }


@app.route("/api/generate-menu", methods=["POST"])
def generate_menu():
    """
    ENDPOINT 2: Generate meal menu menggunakan algorithm (Async Background Job)
    """
    req_data = None
    try:
        init_services()
        
        req_data = request.get_json() or {}
        algorithm_choice = req_data.get('algorithm', 'greedy').lower()
        
        analysis_data = req_data.get('analysis_data', {})
        user_input = req_data.get('user_input') or req_data.get('user_profile') or {}
        if isinstance(user_input, dict) and 'user_input' in user_input:
            user_input = user_input.get('user_input', {})
        tdee = analysis_data.get('energy', {}).get('tdee', 2100)
        
        # Prepare guidelines and database in main thread
        nutrition_guidelines = analysis_data.get('guidelines', {})
        
        food_database = None
        if nutrition_service and nutrition_service.guideline_loader:
            base_df = nutrition_service.guideline_loader.food_df
            if base_df is not None:
                food_database = base_df.copy()
                
        # Apply cuisine preference filtering (shared logic)
        food_preferences = user_input.get('food_preferences', []) if isinstance(user_input, dict) else []
        if food_database is not None and food_preferences:
            normalized_prefs = [p.title() if isinstance(p, str) else p for p in food_preferences]
            
            if algorithm_choice == 'genetic':
                # Genetic algorithm filters cuisine using generic fallback
                allowed = normalized_prefs + ['Generic']
                if 'cuisine_label' in food_database.columns:
                    filtered = food_database[food_database['cuisine_label'].isin(allowed)].copy()
                    if len(filtered) >= 50:
                        food_database = filtered
            else:
                # Greedy algorithm filter
                if 'cuisine' in food_database.columns:
                    food_database = food_database[food_database['cuisine'].isin(normalized_prefs)].copy()
                elif 'cuisine_label' in food_database.columns:
                    food_database = food_database[food_database['cuisine_label'].isin(normalized_prefs)].copy()
                    
        # Check database availability
        if food_database is None or len(food_database) == 0:
            print("[WARNING] food_database is empty or missing before algorithm execution")
            
        # Create job_id
        job_id = str(uuid.uuid4())
        
        # Set jobs initial status
        jobs[job_id] = {"status": "running", "result": None, "error": None}
        
        # Start background thread calling _run_ga_job()
        job_thread = threading.Thread(
            target=_run_ga_job,
            args=(job_id, algorithm_choice, food_database, nutrition_guidelines, tdee, user_input)
        )
        job_thread.daemon = True
        job_thread.start()
        
        # Return immediately
        return jsonify({"success": True, "job_id": job_id}), 202
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[ERROR] /api/generate-menu error: {e}")
        print(f"Full traceback:\n{error_details}")
        
        algo_name = 'unknown'
        if isinstance(req_data, dict):
            algo_name = req_data.get('algorithm', 'unknown')
            
        return jsonify({
            "success": False,
            "error": str(e),
            "algorithm": algo_name
        }), 500


@app.route("/api/job-status/<job_id>", methods=["GET"])
def get_job_status(job_id):
    """
    ENDPOINT: Check the status of a menu generation job
    """
    if job_id not in jobs:
        return jsonify({"success": False, "error": "Job not found"}), 404
        
    job = jobs[job_id]
    status = job.get("status")
    
    if status == "running":
        return jsonify({"success": True, "status": "running"}), 200
        
    elif status == "done":
        result = job.get("result")
        jobs.pop(job_id, None)
        return jsonify({"success": True, "status": "done", "menu_plan": result}), 200
        
    elif status == "error":
        error = job.get("error")
        jobs.pop(job_id, None)
        return jsonify({"success": False, "status": "error", "error": error}), 500
        
    return jsonify({"success": False, "status": "unknown"}), 500


@app.route("/api/refresh-menu", methods=["POST"])
def refresh_menu():
    """
    ENDPOINT 3: Regenerate menu dengan alternative candidates
    Same as generate-menu tapi dengan fresh random generation
    """
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
# CORS CATCH-ALL & ERROR HANDLERS
# ═════════════════════════════════════════════════════════════════════════════════

@app.after_request
def add_cors_headers(response):
    origin = get_allowed_origin()
    if origin:
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, PUT, DELETE'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response


@app.errorhandler(404)
def not_found(error):
    response = jsonify({"error": "Not found"})
    origin = get_allowed_origin()
    if origin:
        response.headers['Access-Control-Allow-Origin'] = origin
    return response, 404


@app.errorhandler(500)
def server_error(error):
    import traceback
    traceback.print_exc()
    response = jsonify({"error": "Internal server error", "details": str(error)})
    origin = get_allowed_origin()
    if origin:
        response.headers['Access-Control-Allow-Origin'] = origin
    return response, 500


# ═════════════════════════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    init_services()
    app.run(debug=True, port=5000)

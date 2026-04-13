"""
Nutrition DSS - Flask Web Application (Fully Integrated)
Sistem Rekomendasi Nutrisi berbasis Algoritma Genetika dan Greedy

Integration dengan:
- C. System Flow (NutritionService for calculations)
- D. Model (Greedy Algorithm for menu generation)
- Frontend (Alpine.js state management)
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
import sys
import os
import json
import pandas as pd
from datetime import datetime

# Add parent directories untuk imports (F. WebApp is one level deep, so one .. to get to root)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'C. System Flow'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'D. Model'))

# Import system components
try:
    from nutrition_service import NutritionService  # pyright: ignore
    print("✓ NutritionService imported successfully")
except ImportError as e:
    print(f"❌ Failed to import NutritionService: {e}")
    NutritionService = None

try:
    from Greedy_Algorithm.greedy_interface import GreedyAlgorithmInterface  # pyright: ignore
    print("✓ GreedyAlgorithmInterface imported successfully")
except ImportError as e:
    print(f"❌ Failed to import GreedyAlgorithmInterface: {e}")
    GreedyAlgorithmInterface = None

# Initialize Flask app
app = Flask(__name__, static_folder='static', static_url_path='/static')
app.config['JSON_SORT_KEYS'] = False

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
    "cholesterol":  {"carbs": (45, 55), "protein": (15,), "fat": (20, 30)},
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
# ROUTES: STATIC PAGES
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/")
def landing():
    """Landing page"""
    return render_template("landing.html")


@app.route("/app")
def index():
    """Main application"""
    return render_template("index.html")


@app.route("/manifest.json")
def manifest():
    """Serve manifest.json untuk PWA"""
    return send_from_directory('static', 'manifest.json', mimetype='application/manifest+json')


@app.route("/sw.js")
def service_worker():
    """Serve service worker"""
    return send_from_directory('static/js', 'sw.js', mimetype='application/javascript')


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
        
        # Parse user input
        user_input = {
            'gender': data.get('gender', 'M'),
            'age': int(data.get('age', 30)),
            'weight': float(data.get('weight', 70)),
            'height': float(data.get('height', 170)),
            'activity_factor': float(data.get('activity', 1.845)),
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
            return jsonify({
                "success": False,
                "error": ", ".join(errors)
            }), 400
        
        # Calculate nutrition needs
        result = nutrition_service.calculate_nutrition_needs(user_input)
        
        if not result.get('success'):
            return jsonify(result), 400
        
        # Add meal distribution untuk display
        result['meal_distribution'] = {
            'breakfast': 0.2375,  # 23.75%
            'lunch': 0.3375,      # 33.75%
            'snack': 0.1375,      # 13.75%
            'dinner': 0.2875      # 28.75%
        }
        
        return jsonify(result), 200
    
    except Exception as e:
        print(f"❌ /api/analyze error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


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
        user_input = data.get('user_input', {})
        tdee = analysis_data.get('energy', {}).get('tdee', 2100)
        
        # Initialize Greedy Algorithm dengan food database
        food_database = analysis_data.get('food_data', {}).get('dataframe')
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
        
        # Convert to dict for JSON response
        menu_dict = menu_plan.to_dict()
        
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
def health_check():
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

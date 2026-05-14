"""
Nutrition DSS - Flask Web Application
Sistem Rekomendasi Nutrisi berbasis Algoritma Genetika dan Greedy
"""

from flask import Flask, render_template, request, jsonify, send_from_directory, make_response
from flask_cors import CORS
import json
import math
import os
import sys

app = Flask(__name__, static_folder='static', static_url_path='/static')
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})
app.config['JSON_SORT_KEYS'] = False

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'C. System Flow'))
try:
    from nutrition_service import NutritionService
except Exception:
    NutritionService = None

_nutrition_service = None


def get_nutrition_service():
    global _nutrition_service
    if _nutrition_service is None:
        if NutritionService is None:
            raise RuntimeError("NutritionService not available")
        _nutrition_service = NutritionService()
    return _nutrition_service



# ─── Helper: Nutrition Calculations ─────────────────────────────────────────

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


def parse_activity_factor(activity):
    """Accept either numeric activity factor or common labels and return a float factor."""
    if activity is None:
        return 1.845
    # If it's already numeric or numeric string, try to convert
    try:
        return float(activity)
    except Exception:
        pass

    s = str(activity).strip().lower()
    mapping = {
        "sedentary": 1.545,
        "light": 1.375,
        "moderate": 1.55,
        "moderately active": 1.55,
        "active": 1.845,
        "vigorous": 2.2,
        "very active": 2.2,
        "active or moderately active": 1.845,
        "sedentary or light activity": 1.545,
    }
    return mapping.get(s, 1.845)


def sanitize_for_json(value):
    """Recursively replace non-finite numbers so JSON stays valid for the browser."""
    if isinstance(value, dict):
        return {key: sanitize_for_json(item) for key, item in value.items()}
    if isinstance(value, list):
        return [sanitize_for_json(item) for item in value]
    if isinstance(value, tuple):
        return [sanitize_for_json(item) for item in value]
    if isinstance(value, float):
        if not math.isfinite(value):
            return None
    return value


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


# ─── Disease Macro Targets (% dari TDEE) ─────────────────────────────────────
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

FOOD_PREFERENCES_LABELS = {
    "Western":       "Western",
    "Asian":         "Asian",
    "Mediterranean": "Mediterranean",
    "Generic":       "Generic",
}

ACTIVITY_LABELS = {
    "1.545": "Sedentary or Light Activity",
    "1.845": "Active or Moderately Active",
    "2.2":   "Vigorous or Vigorously Active",
}

# ─── Sample Menu Data (placeholder until algorithm integrated) ────────────────
SAMPLE_MENU = {
    "breakfast": [
        {"name": "Nasi Tim Ayam", "calories": 320, "carbs": 45, "protein": 22, "fat": 8, "emoji": "🍚"},
        {"name": "Telur Rebus", "calories": 78, "carbs": 1, "protein": 6, "fat": 5, "emoji": "🥚"},
        {"name": "Jus Jeruk", "calories": 112, "carbs": 26, "protein": 2, "fat": 0, "emoji": "🍊"},
    ],
    "lunch": [
        {"name": "Nasi Putih", "calories": 204, "carbs": 44, "protein": 4, "fat": 0, "emoji": "🍚"},
        {"name": "Ikan Bakar Bumbu", "calories": 210, "carbs": 5, "protein": 30, "fat": 8, "emoji": "🐟"},
        {"name": "Tumis Kangkung", "calories": 95, "carbs": 12, "protein": 3, "fat": 5, "emoji": "🥬"},
        {"name": "Tempe Mendoan", "calories": 145, "carbs": 11, "protein": 10, "fat": 7, "emoji": "🫘"},
    ],
    "dinner": [
        {"name": "Nasi Merah", "calories": 218, "carbs": 46, "protein": 5, "fat": 2, "emoji": "🍚"},
        {"name": "Sup Ayam Sayur", "calories": 180, "carbs": 14, "protein": 18, "fat": 6, "emoji": "🍲"},
        {"name": "Tahu Bacem", "calories": 120, "carbs": 8, "protein": 10, "fat": 6, "emoji": "🫘"},
    ],
    "snack": [
        {"name": "Pisang", "calories": 89, "carbs": 23, "protein": 1, "fat": 0, "emoji": "🍌"},
        {"name": "Yogurt Plain", "calories": 100, "carbs": 10, "protein": 9, "fat": 3, "emoji": "🥛"},
    ],
}


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route("/")
def landing():
    """Landing page - homepage"""
    return render_template("landing.html")


@app.route("/app")
def index():
    """Main application"""
    return render_template("index.html")


@app.route("/manifest.json")
def manifest():
    """Serve manifest.json for PWA"""
    return send_from_directory('static', 'manifest.json', mimetype='application/manifest+json')


@app.route("/sw.js")
def service_worker():
    """Serve service worker"""
    return send_from_directory('static/js', 'sw.js', mimetype='application/javascript')


@app.route("/api/analyze", methods=["POST", "OPTIONS"])
def analyze():
    """Endpoint untuk analisis nutrisi dari form slide 1 & 2"""
    if request.method == 'OPTIONS':
        return make_response('', 204)

    try:
        print(f"[ANALYZE] Content-Type: {request.content_type}")
        print(f"[ANALYZE] Raw Data: {request.data}")
        data = request.get_json()
        print(f"[ANALYZE] Parsed JSON: {data}")
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        gender = data.get("gender", "M")
        # Defensive parsing: ensure numeric values are valid
        try:
            age = int(data.get("age", 30))
        except Exception:
            return jsonify({"error": "Invalid age value"}), 400
        try:
            weight = float(data.get("weight", 70))
        except Exception:
            return jsonify({"error": "Invalid weight value"}), 400
        try:
            height = float(data.get("height", 170))
        except Exception:
            return jsonify({"error": "Invalid height value"}), 400

        activity = data.get("activity", "1.845")

        # Normalize lists: sometimes frontend sends objects like { value, label }
        raw_diseases = data.get("diseases", ["normal"]) or ["normal"]
        diseases = []
        for d in raw_diseases:
            if isinstance(d, str):
                diseases.append(d)
            elif isinstance(d, dict):
                # prefer common keys
                diseases.append(d.get("value") or d.get("id") or d.get("label") or str(d))
            else:
                diseases.append(str(d))

        raw_prefs = data.get("food_preferences", ["Generic"]) or ["Generic"]
        food_prefs = []
        for p in raw_prefs:
            if isinstance(p, str):
                food_prefs.append(p)
            elif isinstance(p, dict):
                food_prefs.append(p.get("value") or p.get("id") or p.get("label") or str(p))
            else:
                food_prefs.append(str(p))

        activity_factor = parse_activity_factor(activity)

        service_input = {
            "gender": gender,
            "age": age,
            "weight": weight,
            "height": height,
            "activity_factor": activity_factor,
            "disease": diseases,
            "food_preferences": food_prefs,
        }

        try:
            service_result = get_nutrition_service().calculate_nutrition_needs(service_input)
        except Exception as service_error:
            print(f"[ANALYZE] NutritionService fallback error: {service_error}")
            service_result = None

        # Keep the existing macro card shape for the frontend.
        bmi, bmi_cat, bmi_color = calculate_bmi(weight, height)
        bbi = calculate_bbi(height, gender)
        bmr = calculate_bmr(weight, height, age, gender)
        tdee = calculate_tdee(bmr, activity_factor)

        macros = {"carbs": [0, 100], "protein": [0, 100], "fat": [0, 100]}
        for disease in diseases:
            d = DISEASE_MACROS.get(disease, DISEASE_MACROS["normal"])
            macros["carbs"][0] = max(macros["carbs"][0], d["carbs"][0])
            macros["carbs"][1] = min(macros["carbs"][1], d["carbs"][1])
            macros["protein"][0] = max(macros["protein"][0], d["protein"][0])
            macros["protein"][1] = min(macros["protein"][1], d["protein"][1])
            macros["fat"][0] = max(macros["fat"][0], d["fat"][0])
            macros["fat"][1] = min(macros["fat"][1], d["fat"][1])

        carbs_g = round(tdee * (sum(macros["carbs"]) / 2 / 100) / 4, 0)
        protein_g = round(tdee * (sum(macros["protein"]) / 2 / 100) / 4, 0)
        fat_g = round(tdee * (sum(macros["fat"]) / 2 / 100) / 9, 0)

        disease_labels = [DISEASE_LABELS.get(d, d) for d in diseases]

        response = {
            "bmi": bmi,
            "bmi_category": bmi_cat,
            "bmi_color": bmi_color,
            "bbi": bbi,
            "bmr": int(bmr),
            "tdee": int(tdee),
            "age_group": classify_age_group(age),
            "activity_label": ACTIVITY_LABELS.get(activity, activity),
            "diseases": disease_labels,
            "macros": {
                "carbs": {"pct": macros["carbs"], "gram": int(carbs_g)},
                "protein": {"pct": macros["protein"], "gram": int(protein_g)},
                "fat": {"pct": macros["fat"], "gram": int(fat_g)},
            },
            "menu": SAMPLE_MENU,
        }

        if service_result and service_result.get("success"):
            clean_service_result = dict(service_result)
            food_data = clean_service_result.get("food_data")
            if isinstance(food_data, dict):
                food_data = dict(food_data)
                food_data.pop("dataframe", None)
                clean_service_result["food_data"] = food_data

            response.update(clean_service_result)
            response["macros"] = {
                "carbs": {
                    "pct": [response["guidelines"]["nutrients"]["carbohydrate_g"]["min"], response["guidelines"]["nutrients"]["carbohydrate_g"]["max"]]
                    if "carbohydrate_g" in response.get("guidelines", {}).get("nutrients", {}) else macros["carbs"],
                    "gram": int(carbs_g),
                },
                "protein": {
                    "pct": [response["guidelines"]["nutrients"]["protein_g"]["min"], response["guidelines"]["nutrients"]["protein_g"]["max"]]
                    if "protein_g" in response.get("guidelines", {}).get("nutrients", {}) else macros["protein"],
                    "gram": int(protein_g),
                },
                "fat": {
                    "pct": [response["guidelines"]["nutrients"]["fat_g"]["min"], response["guidelines"]["nutrients"]["fat_g"]["max"]]
                    if "fat_g" in response.get("guidelines", {}).get("nutrients", {}) else macros["fat"],
                    "gram": int(fat_g),
                },
            }

        return jsonify(sanitize_for_json(response))
    except Exception as e:
        import traceback
        print(f"ERROR in /api/analyze: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": str(e), "type": type(e).__name__}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)

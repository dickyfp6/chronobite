"""
Nutrition DSS - Flask Web Application
Sistem Rekomendasi Nutrisi berbasis Algoritma Genetika dan Greedy
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
import json
import math
import os

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.config['JSON_SORT_KEYS'] = False


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


# ─── Disease Macro Targets (% dari TDEE) ─────────────────────────────────────
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

FOOD_PREFERENCES_LABELS = {
    "Western":       "Western",
    "Asian":         "Asian",
    "Mediterranean": "Mediterranean",
    "Generic":       "Generic",
}

ACTIVITY_LABELS = {
    "1.2":   "Sedentary",
    "1.375": "Lightly Active",
    "1.55":  "Moderately Active",
    "1.725": "Very Active",
    "1.9":   "Extremely Active",
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


@app.route("/api/analyze", methods=["POST"])
def analyze():
    """Endpoint untuk analisis nutrisi dari form slide 1 & 2"""
    data = request.get_json()

    gender = data.get("gender", "M")
    age = int(data.get("age", 25))
    weight = float(data.get("weight", 70))
    height = float(data.get("height", 170))
    activity = data.get("activity", "1.375")
    diseases = data.get("diseases", ["normal"])
    food_prefs = data.get("food_preferences", ["Generic"])

    # Calculations
    bmi, bmi_cat, bmi_color = calculate_bmi(weight, height)
    bbi = calculate_bbi(height, gender)
    bmr = calculate_bmr(weight, height, age, gender)
    tdee = calculate_tdee(bmr, activity)

    # Determine macro targets (most restrictive of all selected diseases)
    macros = {"carbs": [0, 100], "protein": [0, 100], "fat": [0, 100]}
    for disease in diseases:
        d = DISEASE_MACROS.get(disease, DISEASE_MACROS["normal"])
        macros["carbs"][0]   = max(macros["carbs"][0],   d["carbs"][0])
        macros["carbs"][1]   = min(macros["carbs"][1],   d["carbs"][1])
        macros["protein"][0] = max(macros["protein"][0], d["protein"][0])
        macros["protein"][1] = min(macros["protein"][1], d["protein"][1])
        macros["fat"][0]     = max(macros["fat"][0],     d["fat"][0])
        macros["fat"][1]     = min(macros["fat"][1],     d["fat"][1])

    # Convert % to gram targets (midpoint)
    carbs_g   = round(tdee * (sum(macros["carbs"])   / 2 / 100) / 4, 0)
    protein_g = round(tdee * (sum(macros["protein"]) / 2 / 100) / 4, 0)
    fat_g     = round(tdee * (sum(macros["fat"])     / 2 / 100) / 9, 0)

    disease_labels = [DISEASE_LABELS.get(d, d) for d in diseases]

    return jsonify({
        "bmi": bmi,
        "bmi_category": bmi_cat,
        "bmi_color": bmi_color,
        "bbi": bbi,
        "bmr": int(bmr),
        "tdee": int(tdee),
        "activity_label": ACTIVITY_LABELS.get(activity, activity),
        "diseases": disease_labels,
        "macros": {
            "carbs":   {"pct": macros["carbs"],   "gram": int(carbs_g)},
            "protein": {"pct": macros["protein"], "gram": int(protein_g)},
            "fat":     {"pct": macros["fat"],     "gram": int(fat_g)},
        },
        "menu": SAMPLE_MENU,
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)

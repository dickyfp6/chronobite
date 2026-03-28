import pandas as pd
import os


# ======================================================
# PATH SETUP
# ======================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))

AKG_PATH = os.path.join(PROJECT_ROOT, "Data Raw", "akg.csv")


# ======================================================
# LOAD AKG
# ======================================================

def load_akg():
    akg = pd.read_csv(AKG_PATH)
    akg["gender"] = akg["gender"].astype(str).str.lower()
    return akg


# ======================================================
# BMI
# ======================================================

def calculate_bmi(weight, height_cm):

    height_m = height_cm / 100
    bmi = weight / (height_m ** 2)

    return round(bmi, 2)


# ======================================================
# BERAT BADAN IDEAL (BROCA)
# ======================================================

def ideal_body_weight(height_cm, gender):

    if gender.lower() in ["male", "laki", "laki-laki"]:
        ibw = (height_cm - 100) * 0.9
    else:
        ibw = (height_cm - 100) * 0.85

    return round(ibw, 2)


# ======================================================
# BMR (MIFFLIN ST JEORE)
# ======================================================

def calculate_bmr(weight, height_cm, age, gender):

    if gender.lower() in ["male", "laki", "laki-laki"]:
        s = 5
    else:
        s = -161

    bmr = (10 * weight) + (6.25 * height_cm) - (5 * age) + s

    return round(bmr, 2)


# ======================================================
# KEBUTUHAN ENERGI HARIAN
# ======================================================

def calculate_energy_need(bmr, activity):

    activity_factor = {
        "ringan": 1.375,
        "sedang": 1.55,
        "berat": 1.725
    }

    energy = bmr * activity_factor[activity]

    return round(energy, 2)


# ======================================================
# AMBIL TARGET AKG
# ======================================================

def get_akg_targets(age, gender):

    akg = load_akg()

    gender = gender.lower()

    if gender in ["male", "laki", "laki-laki"]:
        gender_values = ["male", "laki", "laki-laki", "l"]
    else:
        gender_values = ["female", "perempuan", "p"]

    row = akg[
        (akg["gender"].isin(gender_values)) &
        (akg["age_min"] <= age) &
        (akg["age_max"] >= age)
    ]

    if row.empty:
        raise ValueError("AKG tidak ditemukan")

    return row.iloc[0].to_dict()


# ======================================================
# BUILD USER PROFILE
# ======================================================

def build_user_profile():

    user = {
        "gender": "male",
        "weight": 50,
        "height": 170,
        "age": 35,
        "activity": "berat",
        "health_condition": ["hypertension"],
        "food_preference": "other"
    }

    bmi = calculate_bmi(user["weight"], user["height"])

    ideal_weight = ideal_body_weight(user["height"], user["gender"])

    bmr = calculate_bmr(
        user["weight"],
        user["height"],
        user["age"],
        user["gender"]
    )

    energy_need = calculate_energy_need(bmr, user["activity"])

    akg_target = get_akg_targets(user["age"], user["gender"])

    user_profile = {
        "user_info": user,
        "bmi": bmi,
        "ideal_weight": ideal_weight,
        "bmr": bmr,
        "energy_need": energy_need,
        "akg_target": akg_target
    }

    return user_profile


# ======================================================
# MAIN TEST
# ======================================================

if __name__ == "__main__":

    profile = build_user_profile()

    user = profile["user_info"]

    print("\n===== USER INFORMATION =====")

    print("Gender:", user["gender"])
    print("Age:", user["age"])
    print("Weight:", user["weight"])
    print("Height:", user["height"])

    print("\n===== BODY ANALYSIS =====")

    print("BMI:", profile["bmi"])
    print("Ideal body weight:", profile["ideal_weight"])

    print("\n===== ENERGY NEED =====")

    print("Daily energy need:", profile["energy_need"], "kcal")

    print("\n===== USER HEALTH CONDITION =====")

    if user["health_condition"]:
        print(", ".join(user["health_condition"]))
    else:
        print("Normal")

    print("\n===== FOOD PREFERENCE =====")

    print(user["food_preference"])

    print("\n===== AKG TARGET SAMPLE =====")

    akg = profile["akg_target"]

    print({
        "protein_g": akg.get("protein_g"),
        "fat_g": akg.get("fat_g"),
        "carb_g": akg.get("carb_g"),
        "fiber_g": akg.get("fiber_g")
    })
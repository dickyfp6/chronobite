import pandas as pd
import os

from step3_user_nutrition_needs import build_user_profile


# ======================================================
# PATH SETUP
# ======================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))

FOOD_PATH = os.path.join(
    PROJECT_ROOT,
    "Data Processed",
    "06_final_cek_cuisine_manual.csv"
)


# ======================================================
# LOAD DATASET MAKANAN
# ======================================================

def load_food_dataset():

    df = pd.read_csv(FOOD_PATH)

    df = df.fillna(0)

    return df


# ======================================================
# FILTER CUISINE
# ======================================================

def filter_by_cuisine(df, preference):

    preference = preference.lower()

    if preference == "no preference":
        return df

    df["cuisine"] = df["cuisine"].astype(str).str.lower()

    filtered = df[df["cuisine"] == preference]

    return filtered


# ======================================================
# SPLIT FOOD TYPES
# ======================================================

def split_food_types(df):

    main_course = df[df["food_type"] == "Main Course"]

    side_dish = df[df["food_type"] == "Side Dish"]

    drink = df[df["food_type"] == "Drink"]

    dessert_snack = df[df["food_type"].isin(["Dessert", "Snack"])]

    return main_course, side_dish, drink, dessert_snack


# ======================================================
# BUILD FOOD POOL
# ======================================================

def build_food_pool():

    user_profile = build_user_profile()

    preference = user_profile["user_info"]["food_preference"]

    food_df = load_food_dataset()

    filtered_food = filter_by_cuisine(food_df, preference)

    main_course, side_dish, drink, dessert_snack = split_food_types(filtered_food)

    food_pool = {
        "main_course": main_course,
        "side_dish": side_dish,
        "drink": drink,
        "dessert_snack": dessert_snack
    }

    return food_pool, preference


# ======================================================
# MAIN TEST
# ======================================================

if __name__ == "__main__":

    food_pool, preference = build_food_pool()

    print("\n===== USER FOOD PREFERENCE =====")
    print(preference)

    print("\n===== FOOD POOL SUMMARY =====")

    print("Main course:", len(food_pool["main_course"]))
    print("Side dish:", len(food_pool["side_dish"]))
    print("Drink:", len(food_pool["drink"]))
    print("Dessert/Snack:", len(food_pool["dessert_snack"]))
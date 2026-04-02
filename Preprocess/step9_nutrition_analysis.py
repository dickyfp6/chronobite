import json
import pandas as pd

from step1_load_data import load_food_dataset
from step3_user_nutrition_needs import build_user_profile
from step6_fitness_function import calculate_menu_nutrition, NUTRIENT_MAP


# ======================================================
# LOAD DATA
# ======================================================

food_df = load_food_dataset()

user_profile = build_user_profile()

akg_target = user_profile["akg_target"]


# ======================================================
# LOAD MENU PILIHAN USER
# ======================================================

with open("Algoritma/Genetic Algorithm/File/user_selected_menu.json", "r") as f:
    chromosome = json.load(f)


# ======================================================
# AMBIL DATA MAKANAN
# ======================================================

def get_food(fid):

    row = food_df[food_df["fdc_id"] == fid]

    if row.empty:
        return None

    return row.iloc[0]


# ======================================================
# TAMPILKAN MENU
# ======================================================

def show_menu(chromosome):

    meals = ["Breakfast", "Lunch", "Dinner"]

    idx = 0

    print("\n===================================")
    print("        FINAL SELECTED MENU")
    print("===================================")

    for meal in meals:

        main = get_food(chromosome[idx])
        side = get_food(chromosome[idx+1])
        drink = get_food(chromosome[idx+2])
        snack = get_food(chromosome[idx+3])

        print(f"\n{meal}")

        print("Main  :", main["food_name"])
        print("Side  :", side["food_name"])
        print("Drink :", drink["food_name"])
        print("Snack :", snack["food_name"])

        idx += 4


# ======================================================
# ANALISIS NUTRISI
# ======================================================

def show_nutrition_analysis(menu_nutrition):

    print("\n===================================")
    print("        NUTRITION ANALYSIS")
    print("===================================")

    print(f"\n{'Nutrient':30} {'Target':12} {'Actual':12} {'%AKG':10}")

    for dataset_name, internal_name in NUTRIENT_MAP.items():

        actual = menu_nutrition.get(internal_name, 0)

        target = akg_target.get(internal_name)

        if target:

            percent = (actual / target) * 100

            print(f"{dataset_name:30} {target:<12.2f} {actual:<12.2f} {percent:<10.1f}")

        else:

            print(f"{dataset_name:30} {'-':12} {actual:<12.2f} {'-':10}")


# ======================================================
# MAIN
# ======================================================

if __name__ == "__main__":

    show_menu(chromosome)

    menu_nutrition = calculate_menu_nutrition(chromosome)

    show_nutrition_analysis(menu_nutrition)
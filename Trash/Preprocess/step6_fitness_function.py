# import pandas as pd

# from step1_load_data import load_food_dataset
# from step2_prepare_guidelines import load_guideline
# from step3_user_nutrition_needs import build_user_profile


# # ======================================================
# # LOAD DATA
# # ======================================================

# food_df = load_food_dataset()
# guideline_df = load_guideline()
# user_profile = build_user_profile()

# akg_target = user_profile["akg_target"]
# user_diseases = user_profile["user_info"]["health_condition"]

# # bersihkan nama kolom
# food_df.columns = food_df.columns.str.strip()


# # ======================================================
# # MAPPING DATASET → NAMA INTERNAL
# # ======================================================

# NUTRIENT_MAP = {

#     # =========================
#     # MAKRO NUTRIEN
#     # =========================

#     "Energy": "energy_kcal",
#     "Protein": "protein_g",
#     "Total lipid (fat)": "fat_g",
#     "Carbohydrate, by difference": "carb_g",
#     "Fiber, total dietary": "fiber_g",
#     "Water": "water_ml",

#     # =========================
#     # MINERAL
#     # =========================

#     "Calcium, Ca": "calcium_mg",
#     "Phosphorus, P": "phosphorus_mg",
#     "Magnesium, Mg": "magnesium_mg",
#     "Iron, Fe": "iron_mg",
#     "Zinc, Zn": "zinc_mg",
#     "Selenium, Se": "selenium_mcg",
#     "Manganese, Mn": "manganese_mg",
#     "Copper, Cu": "copper_mcg",
#     "Fluoride, F": "fluoride_mg",
#     "Potassium, K": "potassium_mg",
#     "Sodium, Na": "sodium_mg",

#     # =========================
#     # VITAMIN
#     # =========================

#     "Vitamin A, RAE": "vitamin_a_rae_mcg",
#     "Vitamin D (D2 + D3)": "vitamin_d_mcg",
#     "Vitamin E (alpha-tocopherol)": "vitamin_e_mcg",
#     "Vitamin K (phylloquinone)": "vitamin_k_mcg",

#     "Thiamin": "vitamin_b1_mg",
#     "Riboflavin": "vitamin_b2_mg",
#     "Niacin": "vitamin_b3_mg",
#     "Pantothenic acid": "vitamin_b5_mg",
#     "Vitamin B-6": "vitamin_b6_mg",
#     "Folate, DFE": "folate_mcg",
#     "Vitamin B-12": "vitamin_b12_mcg",

#     "Vitamin C, total ascorbic acid": "vitamin_c_mg",

#     # =========================
#     # NUTRIEN TAMBAHAN
#     # =========================

#     "Choline, total": "choline_mg",

#     # =========================
#     # NON-AKG
#     # =========================

#     "Sugars, Total": "sugars_g",
#     "Fatty acids, total saturated": "sat_fat_g",
#     "Cholesterol": "cholesterol_mg"
# }

# ALL_NUTRIENTS = list(NUTRIENT_MAP.values())


# # ======================================================
# # NUMERIC CONVERSION
# # ======================================================

# for col in NUTRIENT_MAP.keys():

#     if col in food_df.columns:
#         food_df[col] = pd.to_numeric(food_df[col], errors="coerce").fillna(0)


# # ======================================================
# # GET FOOD DATA
# # ======================================================

# def get_food_nutrients(fdc_id):

#     row = food_df.loc[food_df["fdc_id"] == fdc_id]

#     if row.empty:
#         return None

#     return row.iloc[0]


# # ======================================================
# # HITUNG TOTAL NUTRISI MENU
# # ======================================================

# def calculate_menu_nutrition(chromosome):

#     total = {n:0.0 for n in ALL_NUTRIENTS}

#     for food_id in chromosome:

#         food = get_food_nutrients(food_id)

#         if food is None:
#             continue

#         for dataset_col, internal_name in NUTRIENT_MAP.items():

#             if dataset_col in food.index:

#                 value = food[dataset_col]

#                 if pd.notna(value):

#                     total[internal_name] += float(value)

#     return total


# # ======================================================
# # SOFT CONSTRAINT
# # ======================================================

# def calculate_soft_error(menu_nutrition):

#     error = 0

#     for nutrient, target in akg_target.items():

#         value = menu_nutrition.get(nutrient)

#         if value is None or target == 0:
#             continue

#         error += abs(value - target) / target

#     return error


# # ======================================================
# # HARD CONSTRAINT
# # ======================================================

# def calculate_hard_penalty(menu_nutrition):

#     penalty = 0

#     relevant = guideline_df[guideline_df["disease"].isin(user_diseases)]

#     for _, row in relevant.iterrows():

#         nutrient = row["nutrient"]
#         min_val = row["min"]
#         max_val = row["max"]

#         value = menu_nutrition.get(nutrient)

#         if value is None:
#             continue

#         if pd.notna(min_val) and value < min_val:
#             penalty += 1

#         if pd.notna(max_val) and value > max_val:
#             penalty += 1

#     return penalty


# # ======================================================
# # FITNESS FUNCTION
# # ======================================================

# def fitness_function(chromosome):

#     menu_nutrition = calculate_menu_nutrition(chromosome)

#     soft_error = calculate_soft_error(menu_nutrition)

#     hard_penalty = calculate_hard_penalty(menu_nutrition)

#     fitness = 1 / (1 + soft_error + (hard_penalty * 10))

#     return fitness, menu_nutrition


# # ======================================================
# # TEST
# # ======================================================

# if __name__ == "__main__":

#     from Trash.Preprocess.step5_generate_initial_population import generate_population
#     from step4_prepare_food_candidates import build_food_pool

#     food_pool, preference = build_food_pool()

#     population = generate_population(food_pool, population_size=3)

#     print("\n===== FITNESS TEST =====\n")

#     for i, chrom in enumerate(population):

#         fitness, nutrition = fitness_function(chrom)

#         print(f"Chromosome {i+1}")

#         print("Fitness:", round(fitness,4))

#         print("Nutrition:", nutrition)

#         print()
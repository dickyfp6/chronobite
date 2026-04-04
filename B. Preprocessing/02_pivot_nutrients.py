import pandas as pd

# ================= LOAD DATA =================
data = pd.read_csv("A. Data/Data Processed/01_hc_sc_filtered.csv")

# ================= PIVOT =================
pivot = data.pivot_table(
    index=["fdc_id", "food_name", "food_group"],
    columns="nutrient_name",
    values="amount"
).reset_index()

# ================= RENAME =================
rename_map = {
    # ===== HARD CONSTRAINT =====
    "Energy": "energy_kcal",
    "Protein": "protein_g",
    "Carbohydrate, by difference": "carbohydrate_g",
    "Total lipid (fat)": "fat_g",
    "Fiber, total dietary": "fiber_g",
    "Water": "water_g",

    "Vitamin A, RAE": "vitamin_a_rae_mg",
    "Cholesterol": "cholesterol_mg",
    "Fatty acids, total saturated": "saturated_fat_g",
    "Fatty acids, total trans": "trans_fat_g",

    "Phosphorus, P": "phosphorus_mg",
    "Sodium, Na": "sodium_mg",
    "Potassium, K": "potassium_mg",
    "Zinc, Zn": "zinc_mg",
    "Calcium, Ca": "calcium_mg",
    "Iron, Fe": "iron_mg",
    "Magnesium, Mg": "magnesium_mg",

    "Vitamin B-12": "vitamin_b12_mg",
    "Vitamin B-6": "vitamin_b6_mg",
    "Vitamin C, total ascorbic acid": "vitamin_c_mg",

    # ===== SOFT CONSTRAINT =====
    "Fluoride, F": "fluoride_mg",
    "Choline, total": "choline_mg",
    "Folate, DFE": "folate_mg",
    "Manganese, Mn": "manganese_mg",
    "Selenium, Se": "selenium_mg",
    "Copper, Cu": "copper_mg",
    "Thiamin": "vitamin_b1_thiamin_mg",
    "Riboflavin": "vitamin_b2_riboflavin_mg",
    "Niacin": "vitamin_b3_niacin_mg",
    "Pantothenic acid": "vitamin_b5_pantothenic_acid_mg",
    "Vitamin D (D2 + D3)": "vitamin_d_mg",
    "Vitamin E (alpha-tocopherol)": "vitamin_e_mg",
    "Vitamin K (phylloquinone)": "vitamin_k_mg",
    "Sugars, Total": "sugar_g"
}

pivot = pivot.rename(columns=rename_map)

# ================= VALIDASI (penting buat debug) =================
expected_columns = list(rename_map.values())
missing_cols = [col for col in expected_columns if col not in pivot.columns]

print("Pivot + Rename selesai")
print(pivot.shape)
print("Kolom yang tidak ditemukan:", missing_cols)

# ================= SAVE =================
pivot.to_csv(
    "A. Data/Data Processed/02_pivot_food_nutrients.csv",
    index=False
)
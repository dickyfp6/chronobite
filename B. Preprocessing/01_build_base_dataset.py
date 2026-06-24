import pandas as pd
import os

"""
Script 01: Build Base Dataset
Tujuan: Mengambil data mentah (raw) dari USDA, melakukan join tabel yang diperlukan,
kemudian melakukan pivot agar setiap jenis nutrisi menjadi kolom tersendiri.
Script ini juga akan mengubah satuan (misalnya microgram ke milligram) untuk konsistensi.
"""

def main():
    print("="*50)
    print("STEP 01: Build Base Dataset (Join & Pivot USDA)")
    print("="*50)

    # ======================
    # LOAD DATA
    # ======================
    print("[1/3] Membaca data raw USDA...")
    food = pd.read_csv("A. Data/Data Raw/food.csv")
    nutrient = pd.read_csv("A. Data/Data Raw/nutrient.csv")
    food_nutrient = pd.read_csv("A. Data/Data Raw/food_nutrient.csv")
    food_category = pd.read_csv("A. Data/Data Raw/food_category.csv")

    print(f"  Food: {food.shape}")
    print(f"  Nutrient: {nutrient.shape}")
    print(f"  Food Nutrient: {food_nutrient.shape}")
    print(f"  Food Category: {food_category.shape}")

    # ======================
    # JOIN TABLE
    # ======================
    print("\n[2/3] Melakukan proses join antar tabel...")
    df = food_nutrient.merge(
        nutrient,
        left_on="nutrient_id",
        right_on="id",
        how="left"
    )

    df = df.merge(
        food[["fdc_id", "description", "food_category_id"]],
        on="fdc_id",
        how="left"
    )

    df = df.merge(
        food_category[["id", "description"]],
        left_on="food_category_id",
        right_on="id",
        how="left"
    )

    df.rename(columns={
        "name": "nutrient_name",
        "description_x": "food_name",
        "description_y": "food_group"
    }, inplace=True)

    # Filter HC + SC Nutrients
    nutrient_ids = [
        # Hard Constraints
        1008, 1005, 1003, 1004, # Makro Nutrien
        1079, 1051, 1106, 1253, # Fiber, Water, Vit A, Cholesterol
        1258, 1257, 1091, 1092, # Saturated Fat, Trans fat, Phosphorus, Potassium
        1093, 1095, 1087, 1089, # Sodium, Zinc, Calcium, Iron
        1090, 1178, 1175, 1162, # Magnesium, Vit B12, Vit B6, Vit C
        # Soft Constraints
        1099, 1180, 1190, # Fluoride, Choline, Folate DFE
        1101, 1103, 1098, # Manganese, Selenium, Copper
        1165, 1166, 1167, 1170, # Thiamin, Riboflavin, Niacin, Pantothenic acid
        1114, 1109, 1185, 2000, # Vit D, Vit E, Vit K, Sugars Total
    ]
    filtered = df[df["nutrient_id"].isin(nutrient_ids)]
    print(f"  Dataset setelah filter atribut penting: {filtered.shape}")

    # ======================
    # PIVOT DATA
    # ======================
    print("\n[3/3] Melakukan pivot data dan penyesuaian satuan...")
    pivot = filtered.pivot_table(
        index=["fdc_id", "food_name", "food_group"],
        columns="nutrient_name",
        values="amount"
    ).reset_index()

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

    # Konversi microgram ke milligram
    micro_to_mg_cols = [
        "vitamin_a_rae_mg", "vitamin_b12_mg", "fluoride_mg",
        "folate_mg", "selenium_mg", "vitamin_d_mg", "vitamin_k_mg"
    ]
    for col in micro_to_mg_cols:
        if col in pivot.columns:
            pivot[col] = pivot[col] * 0.001

    print("  Kolom yang belum ketemu (kalau ada):", 
          [c for c in rename_map.values() if c not in pivot.columns])

    # ======================
    # SAVE
    # ======================
    os.makedirs("A. Data/Data Processed", exist_ok=True)
    out_path = "A. Data/Data Processed/01_base_dataset.csv"
    pivot.to_csv(out_path, index=False)
    print(f"\n[OK] Selesai. Data dasar tersimpan di: {out_path}")
    print(f"Total Baris Data Awal: {len(pivot)}")
    print("="*50)

if __name__ == "__main__":
    main()

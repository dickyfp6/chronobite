"""
Debug script: cek hasil merge_disease_guidelines() untuk 13 case profile,
khususnya untuk lihat nutrient mana yang kena "Conflict" / "Expanding narrow range",
dan seberapa jauh range hasil merge dari kemampuan dataset makanan.

Cara pakai:
    Letakkan file ini di root project (sejajar folder "D. Model", "A. Data", dst)
    atau sesuaikan sys.path di bawah.

    python debug_guidelines.py
"""

import sys
import os

# ── Sesuaikan path ini sesuai struktur project kamu ──────────────────────────
# Biasanya project punya struktur:
#   <root>/D. Model/Genetic Algorithm/...
#   <root>/C. System Flow/...
#   <root>/A. Data/Data Raw/guideline.csv
#   <root>/A. Data/Data Processed/07_super_final.csv
#
# Jalankan script ini dari <root>, atau edit ROOT_DIR di bawah.
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

for sub in ["C. System Flow", "D. Model", os.path.join("D. Model", "Genetic Algorithm")]:
    p = os.path.join(ROOT_DIR, sub)
    if p not in sys.path:
        sys.path.insert(0, p)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import pandas as pd
from data_loader import get_guideline_loader


# ═════════════════════════════════════════════════════════════════════════════
# 13 PROFILE CASES (sama seperti ga_evaluation.py)
# ═════════════════════════════════════════════════════════════════════════════

PROFILES = [
    {'name': 'Normal',                                'disease': ['normal']},
    {'name': 'Diabetes Melitus Type 2',               'disease': ['dm2']},
    {'name': 'Hypertension',                          'disease': ['hypertension']},
    {'name': 'Cardiovascular Disease',                'disease': ['cvd']},
    {'name': 'Hypercholesterolemia',                  'disease': ['cholesterol']},
    {'name': 'Chronic Kidney Disease Stage 1',        'disease': ['ckd']},
    {'name': 'Diabetes + Hipertensi',                 'disease': ['dm2', 'hypertension']},
    {'name': 'Diabetes + Hiperkolesterolemia',        'disease': ['dm2', 'cholesterol']},
    {'name': 'Hipertensi + Kardiovaskular',           'disease': ['hypertension', 'cvd']},
    {'name': 'CKD + Hipertensi',                      'disease': ['ckd', 'hypertension']},
    {'name': 'Diabetes + Hipertensi + Hiperkolesterolemia', 'disease': ['dm2', 'hypertension', 'cholesterol']},
    {'name': 'CKD + Diabetes + Hipertensi',           'disease': ['ckd', 'dm2', 'hypertension']},
    {'name': 'Hipertensi + Hiperkolesterolemia + CVD','disease': ['hypertension', 'cholesterol', 'cvd']},
]

# Demografi standar (sesuai evaluasi sebelumnya)
AGE = 45
GENDER = 'M'
WEIGHT = 70
HEIGHT = 175

# user_params default (perkiraan; idealnya pakai TDEE actual dari NutritionCalculator,
# tapi untuk debug cepat kita pakai estimasi tetap supaya basis 'TDEE' bisa dikonversi)
USER_PARAMS = {
    'tdee': 2257,   # contoh TDEE untuk pria 45th, 70kg, 175cm, PAL 1.4 (≈ sesuaikan jika perlu)
    'weight': WEIGHT,
    'bbi': 67.5,    # (175-100) * 0.9
}


# ═════════════════════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════════════════════

def main():
    loader = get_guideline_loader()

    # Load food dataset untuk cross-check feasibility
    loader.load_food_data()
    food_df = loader.food_df

    nutrients_to_focus = [
        'protein_g', 'carbohydrate_g', 'fat_g', 'energy_kcal',
        'sodium_mg', 'potassium_mg', 'phosphorus_mg', 'cholesterol_mg',
    ]

    for profile in PROFILES:
        name = profile['name']
        diseases = profile['disease']

        print("\n" + "=" * 90)
        print(f"CASE: {name}  ->  diseases={diseases}")
        print("=" * 90)

        merged = loader.merge_disease_guidelines(
            diseases, AGE, GENDER, user_params=USER_PARAMS
        )

        if not merged:
            print("  [EMPTY] Tidak ada guideline ditemukan!")
            continue

        for nutrient in nutrients_to_focus:
            if nutrient not in merged:
                continue

            data = merged[nutrient]
            mn, mx = data['min'], data['max']
            mn_str = f"{mn:.2f}" if mn is not None else "None"
            mx_str = f"{mx:.2f}" if mx is not None else "None"

            # Cross-check feasibility terhadap dataset (per 100g basis)
            feasible_note = ""
            if food_df is not None and nutrient in food_df.columns and mn is not None and mx is not None:
                # Untuk macro/energy per 100g, range guideline biasanya DAILY TOTAL
                # (10 items @ ~100g tiap item -> total ~1000g basis).
                # Jadi guideline daily range dibagi 10 untuk approx "per-item average" yg dibutuhkan.
                approx_per_item_min = mn / 10
                approx_per_item_max = mx / 10 if mx < float('inf') else float('inf')

                col = food_df[nutrient].dropna()
                n_in_range = ((col >= approx_per_item_min) & (col <= approx_per_item_max)).sum()
                feasible_note = (
                    f"  | per-item target ~[{approx_per_item_min:.2f}, "
                    f"{approx_per_item_max if approx_per_item_max == float('inf') else round(approx_per_item_max,2)}]"
                    f" -> {n_in_range}/{len(col)} food items match"
                )

            print(f"  {nutrient:18} : [{mn_str:>10}, {mx_str:>10}]  "
                  f"(diseases={data['diseases']}){feasible_note}")

        print()


if __name__ == "__main__":
    main()
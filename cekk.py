"""
Debug script: Breakdown lengkap hasil 1x GA run untuk case Normal.
- Print menu per slot (nama makanan, label, gram, energy, protein, carb, fat)
- Print total per meal-time (breakfast/lunch/dinner/snack) + persentase vs TDEE
- Bandingkan persentase aktual vs target distribusi (23.75/33.75/28.75/13.75%)
- Cek apakah Drink <= Main Course & Side Dish di tiap meal

Cara pakai:
    Letakkan file ini di root project, lalu:
    python debug_menu_breakdown.py
"""

import sys
import os
import time

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

for sub in ["C. System Flow", "D. Model", os.path.join("D. Model", "Genetic Algorithm")]:
    p = os.path.join(ROOT_DIR, sub)
    if p not in sys.path:
        sys.path.insert(0, p)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from nutrition_service import NutritionService
from ga_v1 import (
    run_ga,
    local_search,
    calculate_portion_sizes_dynamic,
    SLOT_NAMES,
    SLOT_LABEL_MAP,
    MEAL_INDICES,
)


# ═════════════════════════════════════════════════════════════════════════════
# CONFIG - ganti 'disease' untuk cek case lain
# ═════════════════════════════════════════════════════════════════════════════

PROFILE = {
    'gender': 'M',
    'age': 45,
    'weight': 70,
    'height': 175,
    'activity_factor': 1.4,
    'disease': ['normal'],   # <-- ganti sesuai case yang mau dicek
    'food_preferences': [],
}

GA_PARAMS = dict(
    pop_size=110,
    generations=70,
    elite_ratio=0.10,
    mutation_rate=0.25,
    verbose=False,
)
LS_ITERATIONS = 30

# Target distribusi waktu makan (sesuai meal_ratio di calculate_portion_sizes_dynamic)
TARGET_MEAL_RATIO = {
    'breakfast': 0.2375,
    'lunch':     0.3375,
    'dinner':    0.2875,
    'snack':     0.1375,
}


def build_hard_soft_guidelines(nutrients_dict):
    hard, soft = {}, {}
    for nutrient, constraint in nutrients_dict.items():
        if constraint.get('hard_soft_type') == 'HARD':
            hard[nutrient] = constraint
        else:
            soft[nutrient] = constraint
    return {'hard': hard, 'soft': soft}


def main():
    print("=" * 100)
    print("STEP 1: Calculate nutrition needs & guidelines")
    print("=" * 100)

    service = NutritionService()
    result = service.calculate_nutrition_needs(PROFILE)

    if not result['success']:
        print(f"[ERROR] {result['error']}")
        return

    tdee = result['energy']['tdee']
    nutrients_dict = result['guidelines']['nutrients']
    food_df = result['food_data']['dataframe']
    guidelines = build_hard_soft_guidelines(nutrients_dict)

    print(f"Disease: {PROFILE['disease']}")
    print(f"TDEE: {tdee:.2f} kcal")

    print("\n" + "=" * 100)
    print("STEP 2: Run GA + Local Search")
    print("=" * 100)

    deadline = time.time() + 300
    best_solution, _ = run_ga(food_df, guidelines, tdee=tdee, deadline=deadline, **GA_PARAMS)
    refined_solution = local_search(
        best_solution, food_df, guidelines, tdee=tdee,
        iterations=LS_ITERATIONS, verbose=False, deadline=deadline
    )

    portion_df = calculate_portion_sizes_dynamic(refined_solution, tdee, guidelines)

    # ════════════════════════════════════════════════════════════════════════
    # STEP 3: Breakdown per slot
    # ════════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 100)
    print("STEP 3: MENU BREAKDOWN PER SLOT")
    print("=" * 100)

    meal_names = {0: 'BREAKFAST', 1: 'BREAKFAST', 2: 'BREAKFAST',
                   3: 'LUNCH', 4: 'LUNCH', 5: 'LUNCH',
                   6: 'DINNER', 7: 'DINNER', 8: 'DINNER',
                   9: 'SNACK'}

    print(f"\n{'Slot':<18} {'Label':<12} {'Food Name':<35} {'Gram':>7} {'Energy':>8} {'Protein':>8} {'Carb':>8} {'Fat':>8}")
    print("-" * 100)

    for idx in range(len(portion_df)):
        row = portion_df.iloc[idx]
        slot_name = SLOT_NAMES[idx]
        label = SLOT_LABEL_MAP.get(idx, '?')
        food_name = str(row.get('food_name', 'Unknown'))[:35]
        gram = row.get('gram', 0)
        energy = row.get('final_energy_kcal', 0)
        protein = row.get('final_protein_g', 0)
        carb = row.get('final_carbohydrate_g', 0)
        fat = row.get('final_fat_g', 0)

        print(f"{slot_name:<18} {label:<12} {food_name:<35} {gram:>6.0f}g {energy:>7.1f} {protein:>7.1f}g {carb:>7.1f}g {fat:>7.1f}g")

    # ════════════════════════════════════════════════════════════════════════
    # STEP 4: Total per meal-time vs target distribution
    # ════════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 100)
    print("STEP 4: DISTRIBUSI WAKTU MAKAN (Actual vs Target)")
    print("=" * 100)

    print(f"\n{'Meal':<12} {'Actual kcal':>12} {'Actual %':>10} {'Target %':>10} {'Diff':>10}")
    print("-" * 60)

    total_energy = portion_df['final_energy_kcal'].sum()

    for meal_name, indices in MEAL_INDICES.items():
        meal_energy = sum(portion_df.iloc[i]['final_energy_kcal'] for i in indices if i < len(portion_df))
        actual_pct = meal_energy / total_energy * 100 if total_energy > 0 else 0
        target_pct = TARGET_MEAL_RATIO.get(meal_name, 0) * 100
        diff = actual_pct - target_pct

        print(f"{meal_name.upper():<12} {meal_energy:>12.1f} {actual_pct:>9.2f}% {target_pct:>9.2f}% {diff:>+9.2f}%")

    print(f"\n{'TOTAL':<12} {total_energy:>12.1f} {'100.00%':>10} {'100.00%':>10}")
    print(f"TDEE target: {tdee:.1f} kcal | Actual/TDEE: {total_energy/tdee*100:.1f}%")
    print(f"Disease: {PROFILE['disease']}")
    # ════════════════════════════════════════════════════════════════════════
    # STEP 5: Cek Drink vs Main Course/Side Dish per meal
    # ════════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 100)
    print("STEP 5: CEK DRINK <= MAIN COURSE & SIDE DISH (per meal, by gram)")
    print("=" * 100)

    print(f"\n{'Meal':<12} {'Main (g)':>10} {'Side (g)':>10} {'Drink (g)':>10} {'Drink<=Main':>14} {'Drink<=Side':>14}")
    print("-" * 75)

    for meal_name, indices in MEAL_INDICES.items():
        if len(indices) < 3:
            # snack tidak punya main/side/drink
            continue

        main_idx, side_idx, drink_idx = indices[0], indices[1], indices[2]
        main_g = portion_df.iloc[main_idx]['gram']
        side_g = portion_df.iloc[side_idx]['gram']
        drink_g = portion_df.iloc[drink_idx]['gram']

        drink_le_main = "OK" if drink_g <= main_g else "VIOLATED"
        drink_le_side = "OK" if drink_g <= side_g else "VIOLATED"

        print(f"{meal_name.upper():<12} {main_g:>9.0f}g {side_g:>9.0f}g {drink_g:>9.0f}g {drink_le_main:>14} {drink_le_side:>14}")

    print("\n" + "=" * 100)
    print("DONE")
    print("=" * 100)


if __name__ == "__main__":
    main()
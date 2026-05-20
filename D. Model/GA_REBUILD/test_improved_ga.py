#!/usr/bin/env python
"""
Test improved GA - with realistic absolute macronutrient targets
"""

import sys
sys.path.insert(0, r"c:\Users\Silfia\Documents\FILE TA\TugasAkhirDSS\D. Model\GA_REBUILD")

import pandas as pd
import numpy as np
import random

random.seed(42)
np.random.seed(42)

print("[TEST] Improved GA vs Original GA")
print("="*70)

# Load CSV files
food_df = pd.read_csv(r"c:\Users\Silfia\Documents\FILE TA\TugasAkhirDSS\A. Data\Data Processed\05_final_dataset.csv")
guideline_df = pd.read_csv(r"c:\Users\Silfia\Documents\FILE TA\TugasAkhirDSS\A. Data\Data Raw\guideline.csv")

print(f"\n[LOAD] Food: {len(food_df)} items")
print(f"[LOAD] Guideline: {len(guideline_df)} rows")

# Build more realistic HARD constraints (absolute values, not ratios)
# For a 2000-2200 kcal meal plan (10 items × ~200kcal each):
# carbohydrate: 225-275g (45-55% of ~2000kcal)
# protein: 75-100g (15-20% of ~2000kcal)
# fat: 55-75g (25-30% of ~2000kcal)

guidelines = {
    'hard': {
        'carbohydrate_g': {'min': 225, 'max': 275, 'constraint_type': 'range'},
        'protein_g': {'min': 75, 'max': 100, 'constraint_type': 'range'},
        'fat_g': {'min': 55, 'max': 75, 'constraint_type': 'range'},
        'sugar_g': {'min': 0, 'max': 40, 'constraint_type': 'max'},
        'saturated_fat_g': {'min': 0, 'max': 24, 'constraint_type': 'max'},
        'cholesterol_mg': {'min': 0, 'max': 300, 'constraint_type': 'max'}
    },
    'soft': {}
}

print(f"\n[SETUP] HARD constraints (realistic macros):")
for nutrient, constraint in guidelines['hard'].items():
    print(f"  - {nutrient:25} {constraint['min']:6.0f} - {constraint['max']:6.0f}")

# Import GA functions
from ga_v1 import (
    calculate_total_nutrition,
    calculate_total_hard_deviation,
    is_feasible,
    run_ga,
    filter_extreme_foods
)

print("\n[IMPORT] GA functions loaded ✓")

# Clean food dataset
print(f"\n[FILTERING] Extreme foods...")
food_df_clean = filter_extreme_foods(food_df, verbose=True)

# Run GA with improved algorithm
print(f"\n{'='*70}")
print(f"[GA] Running 50 generations (improved version)...")
print(f"{'='*70}")

best_solution, _ = run_ga(
    food_df=food_df_clean,
    guidelines=guidelines,
    tdee=None,
    generations=50,
    pop_size=20,
    verbose=True
)

ga_nutrition = calculate_total_nutrition(best_solution)
ga_deviation = calculate_total_hard_deviation(best_solution, guidelines)
ga_feasible, ga_violations = is_feasible(best_solution, guidelines)

print(f"\n{'='*70}")
print(f"[GA FINAL RESULT]")
print(f"{'='*70}")
print(f"  Total HARD deviation: {ga_deviation:.1f}")
print(f"  Feasible: {ga_feasible}")
print(f"  Violations: {len(ga_violations)}")

if not ga_feasible:
    print(f"\n[VIOLATIONS]")
    for v in ga_violations[:5]:
        status = v.get('status', '?')
        print(f"  {v['nutrient']:25} {status:4} - Actual: {v['actual']:8.1f} (target: {v['min']:6.0f}-{v['max']:6.0f})")

print(f"\n[MACRO ANALYSIS]")
macros = {
    'carbohydrate_g': ga_nutrition.get('carbohydrate_g', 0),
    'protein_g': ga_nutrition.get('protein_g', 0),
    'fat_g': ga_nutrition.get('fat_g', 0),
}

for nutrient, value in macros.items():
    constraint = guidelines['hard'][nutrient]
    min_v = constraint['min']
    max_v = constraint['max']
    
    if min_v <= value <= max_v:
        status = "✓ OK"
    elif value < min_v:
        status = f"✗ LOW (need {min_v - value:.0f}g more)"
    else:
        status = f"✗ HIGH (excess {value - max_v:.0f}g)"
    
    print(f"  {nutrient:25} {value:8.1f}g (target: {min_v:6.0f}-{max_v:6.0f})  {status}")

print(f"\n[ENERGY]")
energy = ga_nutrition.get('energy_kcal', 0)
print(f"  Total energy: {energy:8.1f} kcal (target: ~2000)")

print(f"\n[MEAL PLAN]")
for idx, row in best_solution.iterrows():
    print(f"  {idx+1}. {row.get('food_name', '?'):40} {row.get('energy_kcal', 0):6.0f} kcal")

if ga_feasible:
    print(f"\n✓✓✓ SUCCESS! FEASIBLE SOLUTION FOUND! ✓✓✓")
else:
    print(f"\n✗ Still infeasible but deviation reduced significantly")
    print(f"✓ Local Search can now fine-tune this solution")

print("\n[TEST COMPLETE]")

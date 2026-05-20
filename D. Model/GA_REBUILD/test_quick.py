#!/usr/bin/env python
"""
Quick test: GA + Local Search dengan global HARD deviation
"""

import sys
sys.path.insert(0, r"c:\Users\Silfia\Documents\FILE TA\TugasAkhirDSS\D. Model\GA_REBUILD")

import pandas as pd
import numpy as np
import random

random.seed(42)
np.random.seed(42)

print("[TEST] Starting GA + Local Search (STABLE VERSION)")
print("="*70)

# Load CSV files
food_df = pd.read_csv(r"c:\Users\Silfia\Documents\FILE TA\TugasAkhirDSS\A. Data\Data Processed\05_final_dataset.csv")
guideline_df = pd.read_csv(r"c:\Users\Silfia\Documents\FILE TA\TugasAkhirDSS\A. Data\Data Raw\guideline.csv")

print(f"\n[LOAD] Food: {len(food_df)} items")
print(f"[LOAD] Guideline: {len(guideline_df)} rows")

# Build guidelines (all guideline nutrients are HARD for this test)
guide_normal = guideline_df[guideline_df['disease'] == 'normal'].copy()
hard_nutrients = guide_normal[['nutrient', 'min', 'max']].drop_duplicates(subset=['nutrient'])

guidelines = {'hard': {}, 'soft': {}}

for _, row in hard_nutrients.iterrows():
    nutrient = row['nutrient']
    min_val = row['min'] if pd.notna(row['min']) else 0
    max_val = row['max'] if pd.notna(row['max']) else float('inf')
    guidelines['hard'][nutrient] = {
        'min': min_val,
        'max': max_val,
        'constraint_type': 'range',
        'hard_soft_type': 'HARD'
    }

print(f"\n[SETUP] {len(guidelines['hard'])} HARD constraints")
for nutrient, constraint in list(guidelines['hard'].items())[:3]:
    print(f"  - {nutrient}: {constraint['min']:.3f} - {constraint['max']:.3f}")

# Import GA functions
from ga_v1 import (
    calculate_total_nutrition,
    calculate_total_hard_deviation,
    is_feasible,
    run_ga,
    local_search
)

print("[IMPORT] GA functions loaded")

# Clean food
invalid_keywords = ['spice', 'powder', 'yeast', 'sauce', 'extract', 'flavoring', 'dressing', 'seasoning']
food_df_clean = food_df[~food_df['food_name'].str.lower().str.contains('|'.join(invalid_keywords), na=False)].copy()

print(f"\n[FILTER] {len(food_df)} → {len(food_df_clean)} items")

# Run GA
print("\n[GA] Running 50 generations...")
best_solution, top_solutions = run_ga(
    food_df=food_df_clean,
    guidelines=guidelines,
    tdee=None,
    generations=50,
    pop_size=20,
    verbose=False
)

ga_nutrition = calculate_total_nutrition(best_solution)
ga_deviation = calculate_total_hard_deviation(best_solution, guidelines)
ga_feasible, ga_violations = is_feasible(best_solution, guidelines)

print(f"\n[GA RESULT]")
print(f"  Deviation: {ga_deviation:.1f}")
print(f"  Feasible: {ga_feasible}")
print(f"  Violations: {len(ga_violations)}")

# Run Local Search
print(f"\n[LOCAL SEARCH] Running up to 20 iterations...")
ls_solution = local_search(
    solution=best_solution,
    food_df=food_df_clean,
    guidelines=guidelines,
    tdee=None,
    iterations=20,
    verbose=True
)

ls_nutrition = calculate_total_nutrition(ls_solution)
ls_deviation = calculate_total_hard_deviation(ls_solution, guidelines)
ls_feasible, ls_violations = is_feasible(ls_solution, guidelines)

print(f"\n[LOCAL SEARCH RESULT]")
print(f"  Deviation: {ls_deviation:.1f}")
print(f"  Feasible: {ls_feasible}")
print(f"  Violations: {len(ls_violations)}")

print(f"\n[IMPROVEMENT]")
print(f"  Deviation: {ga_deviation:.1f} → {ls_deviation:.1f} (Δ{ga_deviation - ls_deviation:+.1f})")
print(f"  Feasible: {ga_feasible} → {ls_feasible}")
print(f"  Violations: {len(ga_violations)} → {len(ls_violations)}")

if not ga_feasible and ls_feasible:
    print(f"\n✓✓✓ SUCCESS! Solution is now FEASIBLE! ✓✓✓")
elif ls_deviation < ga_deviation:
    print(f"\n✓ Deviation reduced by {ga_deviation - ls_deviation:.1f}")
else:
    print(f"\n✗ No improvement in deviation")

print("\n[TEST COMPLETE]")

"""
Ultra-simple direct test - NO System Flow imports at all
Just load CSV and test GA + Local Search
"""

import pandas as pd
import numpy as np
import random
import sys
import os

# Set random seeds
random.seed(42)
np.random.seed(42)

# Add only GA_REBUILD to path
ga_path = r"c:\Users\Silfia\Documents\FILE TA\TugasAkhirDSS\D. Model\GA_REBUILD"
sys.path.insert(0, ga_path)

print("="*70)
print("TEST: GA + LOCAL SEARCH (Pure Standalone)")
print("="*70)

# ════════════════════════════════════════════════════════════════
# Load data directly from CSV (no System Flow)
# ════════════════════════════════════════════════════════════════

print("\n[STEP 1] Loading data...")

# Load food database
food_df = pd.read_csv(r"c:\Users\Silfia\Documents\FILE TA\TugasAkhirDSS\A. Data\Data Processed\05_final_dataset.csv")
print(f"  Food items: {len(food_df)}")

# Load guideline
guideline_df = pd.read_csv(r"c:\Users\Silfia\Documents\FILE TA\TugasAkhirDSS\A. Data\Data Raw\guideline.csv")
print(f"  Guidelines: {len(guideline_df)}")

# ════════════════════════════════════════════════════════════════
# Build HARD/SOFT constraints manually
# ════════════════════════════════════════════════════════════════

print("\n[STEP 2] Building constraints...")

# Filter guideline untuk 'normal' disease
guide_normal = guideline_df[guideline_df['disease'] == 'normal'].copy()

# HARD constraints (from 'range' and 'max' tipe)
hard_nutrients = guide_normal[guide_normal['tipe'].isin(['range', 'max'])][['nutrient', 'min', 'max']].drop_duplicates(subset=['nutrient'])

guidelines = {
    'hard': {},
    'soft': {}
}

print("  HARD constraints:")
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
    print(f"    {nutrient}: {min_val:.0f}-{max_val:.0f}")

# SOFT constraints (DRI micronutrients)
soft_nutrients_dict = {
    'calcium_mg': {'min': 1000, 'max': 2500},
    'iron_mg': {'min': 8, 'max': 45},
    'magnesium_mg': {'min': 400, 'max': 420},
    'phosphorus_mg': {'min': 700, 'max': 4000},
    'zinc_mg': {'min': 11, 'max': 40},
    'vitamin_a_mcg': {'min': 900, 'max': 3000},
    'vitamin_c_mg': {'min': 90, 'max': 2000},
    'vitamin_b12_mcg': {'min': 2.4, 'max': 100}
}

for nutrient, limits in soft_nutrients_dict.items():
    guidelines['soft'][nutrient] = {
        'min': limits['min'],
        'max': limits['max'],
        'constraint_type': 'range',
        'hard_soft_type': 'SOFT'
    }

print(f"  SOFT constraints: {len(guidelines['soft'])} micronutrients")

# ════════════════════════════════════════════════════════════════
# Import GA functions
# ════════════════════════════════════════════════════════════════

print("\n[STEP 3] Importing GA module...")

try:
    # Import only basic GA functions
    from ga_v1 import (
        calculate_total_nutrition,
        is_feasible,
        run_ga,
        local_search
    )
    print("  ✓ GA module imported successfully")
except Exception as e:
    print(f"  ✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ════════════════════════════════════════════════════════════════
# Clean food dataset
# ════════════════════════════════════════════════════════════════

print("\n[STEP 4] Filtering food dataset...")

# Remove junk foods
invalid_keywords = ['spice', 'powder', 'yeast', 'sauce', 'extract', 'flavoring', 'dressing', 'seasoning']
food_df_clean = food_df[~food_df['food_name'].str.lower().str.contains('|'.join(invalid_keywords), na=False)].copy()

print(f"  {len(food_df)} → {len(food_df_clean)} items")

# ════════════════════════════════════════════════════════════════
# Run GA
# ════════════════════════════════════════════════════════════════

print("\n[STEP 5] Running Genetic Algorithm...")

best_solution, top_solutions = run_ga(
    food_df=food_df_clean,
    guidelines=guidelines,
    tdee=None,
    generations=50,
    pop_size=20,
    verbose=False
)

print("  ✓ GA complete")

# ════════════════════════════════════════════════════════════════
# Display GA result
# ════════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("GA RESULT")
print("="*70)

ga_nutrition = calculate_total_nutrition(best_solution)

# Check feasibility
ga_feasible, ga_violations = is_feasible(best_solution, guidelines)

print("\nNutrition (actual):")
for nutrient in ['carbohydrate_g', 'protein_g', 'fat_g', 'sugar_g', 'saturated_fat_g', 'cholesterol_mg']:
    value = ga_nutrition.get(nutrient, 0)
    print(f"  {nutrient:25} {value:8.1f}")

print("\nHARD Constraints:")
hard_ok = 0
for nutrient, constraint in guidelines['hard'].items():
    actual = ga_nutrition.get(nutrient, 0)
    min_val = constraint['min']
    max_val = constraint['max']
    ok = min_val <= actual <= max_val
    hard_ok += (1 if ok else 0)
    status = "✓" if ok else "✗"
    print(f"  {status} {nutrient:25} {actual:8.1f} (range {min_val:.0f}-{max_val:.0f})")

print(f"\nFeasibility: {'VALID' if ga_feasible else 'INVALID'} ({hard_ok}/{len(guidelines['hard'])} HARD OK)")
if not ga_feasible:
    print("Violations:")
    for v in ga_violations[:5]:
        print(f"  - {v}")

# ════════════════════════════════════════════════════════════════
# Run LOCAL SEARCH
# ════════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("LOCAL SEARCH (NEW IMPROVED VERSION)")
print("="*70)

best_solution_improved = local_search(
    solution=best_solution,
    food_df=food_df_clean,
    guidelines=guidelines,
    tdee=None,
    iterations=20,
    verbose=True
)

# ════════════════════════════════════════════════════════════════
# Display LOCAL SEARCH result
# ════════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("LOCAL SEARCH RESULT")
print("="*70)

ls_nutrition = calculate_total_nutrition(best_solution_improved)

# Check feasibility
ls_feasible, ls_violations = is_feasible(best_solution_improved, guidelines)

print("\nNutrition (actual):")
for nutrient in ['carbohydrate_g', 'protein_g', 'fat_g', 'sugar_g', 'saturated_fat_g', 'cholesterol_mg']:
    ga_val = ga_nutrition.get(nutrient, 0)
    ls_val = ls_nutrition.get(nutrient, 0)
    delta = ls_val - ga_val
    symbol = "↑" if delta > 0 else "↓" if delta < 0 else "—"
    print(f"  {nutrient:25} {ls_val:8.1f} (Δ {delta:+7.1f}) {symbol}")

print("\nHARD Constraints:")
hard_ok_ls = 0
for nutrient, constraint in guidelines['hard'].items():
    actual = ls_nutrition.get(nutrient, 0)
    min_val = constraint['min']
    max_val = constraint['max']
    ok = min_val <= actual <= max_val
    hard_ok_ls += (1 if ok else 0)
    status = "✓" if ok else "✗"
    print(f"  {status} {nutrient:25} {actual:8.1f} (range {min_val:.0f}-{max_val:.0f})")

print(f"\nFeasibility: {'VALID' if ls_feasible else 'INVALID'} ({hard_ok_ls}/{len(guidelines['hard'])} HARD OK)")
if not ls_feasible:
    print("Violations:")
    for v in ls_violations[:5]:
        print(f"  - {v}")

# ════════════════════════════════════════════════════════════════
# Summary
# ════════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("IMPROVEMENT SUMMARY")
print("="*70)

print(f"\nHARD Constraints Fixed:")
print(f"  GA: {hard_ok}/{len(guidelines['hard'])} constraints OK")
print(f"  LS: {hard_ok_ls}/{len(guidelines['hard'])} constraints OK")
print(f"  Improvement: {hard_ok_ls - hard_ok} more constraints fixed")

print(f"\nViolations Reduced:")
print(f"  GA: {len(ga_violations)} violations")
print(f"  LS: {len(ls_violations)} violations")
print(f"  Reduction: {len(ga_violations) - len(ls_violations)} fewer violations")

if ls_feasible and not ga_feasible:
    print("\n✓✓✓ SUCCESS! Local Search made solution FEASIBLE! ✓✓✓")
elif hard_ok_ls > hard_ok:
    print(f"\n✓ SUCCESS! Local Search improved {hard_ok_ls - hard_ok} constraint(s)")
else:
    print("\n⊘ No improvement in HARD constraints")

print("\n[TEST COMPLETE]")

"""
Direct test untuk Local Search - BYPASS input handler
"""

import sys
sys.path.insert(0, r"c:\Users\Silfia\Documents\FILE TA\TugasAkhirDSS\D. Model\GA_REBUILD")

import pandas as pd
import numpy as np

# Import only from ga_v1 (no System Flow imports)
# This avoids triggering input_handler
import importlib.util
spec = importlib.util.spec_from_file_location("ga_v1", r"c:\Users\Silfia\Documents\FILE TA\TugasAkhirDSS\D. Model\GA_REBUILD\ga_v1.py")
ga_v1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ga_v1)

run_ga = ga_v1.run_ga
local_search = ga_v1.local_search
calculate_total_nutrition = ga_v1.calculate_total_nutrition
fitness = ga_v1.fitness
is_feasible = ga_v1.is_feasible

# ════════════════════════════════════════════════════════════════
# STEP 1: Load data directly
# ════════════════════════════════════════════════════════════════

print("="*70)
print("LOADING DATA DIRECTLY")
print("="*70)

# Load guideline
guideline = pd.read_csv(r"c:\Users\Silfia\Documents\FILE TA\TugasAkhirDSS\A. Data\Data Raw\guideline.csv")
print(f"[OK] Guideline loaded: {len(guideline)} rows")

# Load food data
food_df = pd.read_csv(r"c:\Users\Silfia\Documents\FILE TA\TugasAkhirDSS\A. Data\Data Processed\05_final_dataset.csv")
print(f"[OK] Food data loaded: {len(food_df)} rows")

# ════════════════════════════════════════════════════════════════
# STEP 2: Build guidelines dict (HARD/SOFT)
# ════════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("BUILD GUIDELINES")
print("="*70)

# Filter guideline untuk normal (non-disease)
guide_normal = guideline[guideline['disease'] == 'normal'].copy()

guidelines = {
    'hard': {},
    'soft': {}
}

# Get HARD constraints (tipe = 'range' atau 'max')
hard_nutrients = guide_normal[guide_normal['tipe'].isin(['range', 'max'])][['nutrient', 'min', 'max']].drop_duplicates(subset=['nutrient'])
print(f"\n[HARD Constraints] {len(hard_nutrients)} nutrients:")
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
    print(f"  {nutrient}: {min_val:.0f} - {max_val:.0f}")

# Get SOFT constraints (use DRI micronutrients)
soft_nutrients = ['calcium_mg', 'iron_mg', 'magnesium_mg', 'phosphorus_mg', 'zinc_mg', 'vitamin_a_mcg', 'vitamin_c_mg', 'vitamin_b12_mcg']
print(f"\n[SOFT Constraints] {len(soft_nutrients)} nutrients (DRI-based)")

for nutrient in soft_nutrients:
    # Fallback DRI values
    dri_values = {
        'calcium_mg': {'min': 1000, 'max': 2500},
        'iron_mg': {'min': 8, 'max': 45},
        'magnesium_mg': {'min': 400, 'max': 420},
        'phosphorus_mg': {'min': 700, 'max': 4000},
        'zinc_mg': {'min': 11, 'max': 40},
        'vitamin_a_mcg': {'min': 900, 'max': 3000},
        'vitamin_c_mg': {'min': 90, 'max': 2000},
        'vitamin_b12_mcg': {'min': 2.4, 'max': 100}
    }
    
    if nutrient in dri_values:
        guidelines['soft'][nutrient] = {
            'min': dri_values[nutrient]['min'],
            'max': dri_values[nutrient]['max'],
            'constraint_type': 'range',
            'hard_soft_type': 'SOFT'
        }
        print(f"  {nutrient}: {dri_values[nutrient]['min']:.0f} - {dri_values[nutrient]['max']:.0f}")

# ════════════════════════════════════════════════════════════════
# STEP 3: Filter foods & run GA
# ════════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("RUN GA (50 generations)")
print("="*70)

# Filter junk foods
invalid_keywords = ['spice', 'powder', 'yeast', 'sauce', 'extract', 'flavoring', 'dressing', 'seasoning']
food_df_clean = food_df[~food_df['food_name'].str.lower().str.contains('|'.join(invalid_keywords), na=False)].copy()

best_solution, top_solutions = run_ga(
    food_df=food_df_clean,
    guidelines=guidelines,
    tdee=None,
    generations=50,
    pop_size=20,
    verbose=False
)

print("[OK] GA complete")

# ════════════════════════════════════════════════════════════════
# STEP 4: Display GA result
# ════════════════════════════════════════════════════════════════

print("\n--- GA RESULT ---")
ga_nutrition = calculate_total_nutrition(best_solution)

print("NUTRITION VALUES:")
print(f"  Carbs:   {ga_nutrition.get('carbohydrate_g', 0):8.1f} g")
print(f"  Protein: {ga_nutrition.get('protein_g', 0):8.1f} g")
print(f"  Fat:     {ga_nutrition.get('fat_g', 0):8.1f} g")
print(f"  Sugar:   {ga_nutrition.get('sugar_g', 0):8.1f} g")
print(f"  Sat Fat: {ga_nutrition.get('saturated_fat_g', 0):8.1f} g")
print(f"  Chol:    {ga_nutrition.get('cholesterol_mg', 0):8.1f} mg")

print("\nHARD CONSTRAINT CHECK:")
for nutrient, constraint in guidelines['hard'].items():
    actual = ga_nutrition.get(nutrient, 0)
    min_val = constraint['min']
    max_val = constraint['max']
    status = "✓" if min_val <= actual <= max_val else "✗"
    print(f"  {status} {nutrient:25} {actual:8.1f} (range {min_val:.0f}-{max_val:.0f})")

ga_feasible, ga_violations = is_feasible(best_solution, guidelines)
print(f"\nFeasibility: {'VALID' if ga_feasible else 'INVALID'}")
if not ga_feasible:
    for v in ga_violations:
        print(f"  - {v}")

# ════════════════════════════════════════════════════════════════
# STEP 5: Run LOCAL SEARCH (NEW IMPROVED VERSION)
# ════════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("RUN LOCAL SEARCH (NEW IMPROVED VERSION)")
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
# STEP 6: Display LOCAL SEARCH result
# ════════════════════════════════════════════════════════════════

print("\n--- LOCAL SEARCH RESULT ---")
ls_nutrition = calculate_total_nutrition(best_solution_improved)

print("NUTRITION VALUES:")
print(f"  Carbs:   {ls_nutrition.get('carbohydrate_g', 0):8.1f} g")
print(f"  Protein: {ls_nutrition.get('protein_g', 0):8.1f} g")
print(f"  Fat:     {ls_nutrition.get('fat_g', 0):8.1f} g")
print(f"  Sugar:   {ls_nutrition.get('sugar_g', 0):8.1f} g")
print(f"  Sat Fat: {ls_nutrition.get('saturated_fat_g', 0):8.1f} g")
print(f"  Chol:    {ls_nutrition.get('cholesterol_mg', 0):8.1f} mg")

print("\nHARD CONSTRAINT CHECK:")
for nutrient, constraint in guidelines['hard'].items():
    actual = ls_nutrition.get(nutrient, 0)
    min_val = constraint['min']
    max_val = constraint['max']
    status = "✓" if min_val <= actual <= max_val else "✗"
    print(f"  {status} {nutrient:25} {actual:8.1f} (range {min_val:.0f}-{max_val:.0f})")

ls_feasible, ls_violations = is_feasible(best_solution_improved, guidelines)
print(f"\nFeasibility: {'VALID' if ls_feasible else 'INVALID'}")
if not ls_feasible:
    for v in ls_violations:
        print(f"  - {v}")

# ════════════════════════════════════════════════════════════════
# SUMMARY
# ════════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("IMPROVEMENT SUMMARY")
print("="*70)

improvements = {
    'carbs': ls_nutrition.get('carbohydrate_g', 0) - ga_nutrition.get('carbohydrate_g', 0),
    'protein': ls_nutrition.get('protein_g', 0) - ga_nutrition.get('protein_g', 0),
    'fat': ls_nutrition.get('fat_g', 0) - ga_nutrition.get('fat_g', 0),
    'sugar': ls_nutrition.get('sugar_g', 0) - ga_nutrition.get('sugar_g', 0),
    'saturated_fat': ls_nutrition.get('saturated_fat_g', 0) - ga_nutrition.get('saturated_fat_g', 0),
    'cholesterol': ls_nutrition.get('cholesterol_mg', 0) - ga_nutrition.get('cholesterol_mg', 0),
}

for key, change in improvements.items():
    symbol = "↑" if change > 0 else "↓" if change < 0 else "—"
    print(f"  {symbol} {key:15} {change:+8.1f}")

print(f"\nGA Feasible: {ga_feasible} → LS Feasible: {ls_feasible}")
if ga_feasible == False and ls_feasible == True:
    print("✓ SUCCESS: Local Search made solution feasible!")
elif not ga_feasible and not ls_feasible:
    print(f"Violations reduced: {len(ga_violations)} → {len(ls_violations)}")

print("\n[TEST COMPLETE]")

"""
Quick test untuk Local Search dengan GUIDED SELECTION
Menghasilkan improvement (bukan 0/15)
"""

import sys
sys.path.insert(0, r"c:\Users\Silfia\Documents\FILE TA\TugasAkhirDSS\C. System Flow")
sys.path.insert(0, r"c:\Users\Silfia\Documents\FILE TA\TugasAkhirDSS\D. Model\GA_REBUILD")

import pandas as pd
import numpy as np
from ga_v1 import (
    run_ga, local_search, calculate_total_nutrition,
    filter_food_dataset, display_nutrition_analysis_table
)
from food_filter_meal_ready import filter_meal_ready_foods
from nutrition_service import NutritionService

print("[OK] All imports successful\n")

# ════════════════════════════════════════════════════════════════
# STEP 1: Calculate nutrition needs
# ════════════════════════════════════════════════════════════════

print("="*70)
print("STEP 1: Calculate nutrition needs")
print("="*70)

# Hardcoded user data
user_input = {
    'gender': 'M',
    'age': 25,
    'weight': 70,
    'height': 175,
    'activity_factor': 1.55,  # Moderate
    'disease': [],
    'food_preferences': []
}

print(f"User: {user_input['gender']}, Age {user_input['age']}, {user_input['weight']}kg, {user_input['height']}cm")

# Calculate nutrition requirements
service = NutritionService()
nutrition_result = service.calculate_nutrition_needs(user_input)

if not nutrition_result['success']:
    print(f"✗ FAILED: {nutrition_result.get('error', 'Unknown error')}")
    sys.exit(1)

print(f"[OK] Nutrition calculation successful")

# Extract data
food_df = nutrition_result['food_data']['dataframe']
guidelines_all = nutrition_result['guidelines']['nutrients']
tdee = nutrition_result['energy']['tdee']

# Split guidelines berdasarkan hard_soft_type
guidelines = {
    'hard': {k: v for k, v in guidelines_all.items() if v.get('hard_soft_type') == 'HARD'},
    'soft': {k: v for k, v in guidelines_all.items() if v.get('hard_soft_type') != 'HARD'}
}

print(f"[OK] TDEE calculated: {tdee:.0f} kcal")
print(f"[OK] Food database loaded: {len(food_df)} items")
print(f"[OK] Nutrition guidelines ready")

# ════════════════════════════════════════════════════════════════
# STEP 2: Filter foods
# ════════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("STEP 2: Filtering food candidates - Remove non-meal foods")
print("="*70)

# Apply meal-ready filtering (removes dried, powder, spice, etc)
food_df_filtered = filter_meal_ready_foods(
    input_csv=food_df,
    output_csv=None,
    verbose=False
)
print(f"[OK] Meal-ready filter: {len(food_df)} -> {len(food_df_filtered)} items")

# Also apply legacy filter for additional safety
food_df_filtered = filter_food_dataset(food_df_filtered, verbose=False)
print(f"[OK] Legacy filter: {len(food_df_filtered)} suitable foods")

# ════════════════════════════════════════════════════════════════
# STEP 3: Run GA
# ════════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("STEP 3: Running Genetic Algorithm")
print("="*70)

best_solution, top_solutions = run_ga(
    food_df=food_df_filtered,
    guidelines=guidelines,
    tdee=tdee,
    generations=50,
    pop_size=20,
    verbose=False
)
print("[OK] GA optimization complete")

# Display GA result
print("\n--- GA RESULT ---")
ga_nutrition = calculate_total_nutrition(best_solution)
carb_target = guidelines_all.get('carbohydrate_g', {}).get('max', 350)
fat_target = guidelines_all.get('fat_g', {}).get('max', 78)
protein_target = guidelines_all.get('protein_g', {}).get('max', 100)

print(f"Carbs:   {ga_nutrition.get('carbohydrate_g', 0):6.0f}g (target {carb_target:.0f}g)")
print(f"Fats:    {ga_nutrition.get('fat_g', 0):6.0f}g (target {fat_target:.0f}g)")
print(f"Protein: {ga_nutrition.get('protein_g', 0):6.0f}g (target {protein_target:.0f}g)")

# ════════════════════════════════════════════════════════════════
# STEP 4: Run LOCAL SEARCH (IMPROVED with GUIDED SELECTION)
# ════════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("STEP 4: Running LOCAL SEARCH (IMPROVED)")
print("="*70)

best_solution = local_search(
    solution=best_solution,
    food_df=food_df_filtered,
    guidelines=guidelines,
    tdee=tdee,
    iterations=20,
    verbose=True
)

print("[OK] Local search optimization complete")

# Display improved result
print("\n--- LOCAL SEARCH RESULT ---")
ls_nutrition = calculate_total_nutrition(best_solution)
print(f"Carbs:   {ls_nutrition.get('carbohydrate_g', 0):6.0f}g (target {carb_target:.0f}g)")
print(f"Fats:    {ls_nutrition.get('fat_g', 0):6.0f}g (target {fat_target:.0f}g)")
print(f"Protein: {ls_nutrition.get('protein_g', 0):6.0f}g (target {protein_target:.0f}g)")

# ════════════════════════════════════════════════════════════════
# SUMMARY
# ════════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("SUMMARY")
print("="*70)

carb_change = ls_nutrition.get('carbohydrate_g', 0) - ga_nutrition.get('carbohydrate_g', 0)
fat_change = ls_nutrition.get('fat_g', 0) - ga_nutrition.get('fat_g', 0)
protein_change = ls_nutrition.get('protein_g', 0) - ga_nutrition.get('protein_g', 0)

print(f"\nNutrient Changes (GA → Local Search):")
print(f"  Carbs:   {carb_change:+6.1f}g")
print(f"  Fats:    {fat_change:+6.1f}g")
print(f"  Protein: {protein_change:+6.1f}g")

if carb_change > 0 or fat_change > 0 or protein_change < 0:
    print(f"\n[OK] SUCCESS! Local Search produced improvements!")
else:
    print(f"\n[FAIL] No improvements found")

# Display detailed nutrition analysis table (TASK 8)
print("\n" + "="*70)
print("NUTRITION ANALYSIS TABLE (100g basis - HARD/SOFT separated)")
print("="*70)
display_nutrition_analysis_table(best_solution, guidelines)

print(f"\n[OK] Test complete!")

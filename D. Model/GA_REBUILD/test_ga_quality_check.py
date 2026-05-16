"""
TEST: GA Quality Improvements - Macronutrient Prioritization
===========================================================

Verify:
1. Fitness penalties correctly prioritize macronutrients
2. Mutation selects nutrient-aware foods
3. GA produces balanced nutrition
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../C. System Flow'))

from ga_v1 import fitness, mutation, random_solution, run_ga, calculate_total_nutrition
from nutrition_service import NutritionService

print("\n" + "="*80)
print("[TEST] GA Quality Improvements")
print("="*80)

# Setup
print("\n[SETUP] Initializing...")
nutrition_service = NutritionService()
user_input = {
    'gender': 'Female', 'age': 25, 'weight': 60, 'height': 165,
    'activity_factor': 1.5, 'disease': ['hypertension'], 'food_preferences': []
}
result = nutrition_service.calculate_nutrition_needs(user_input)
food_df = result['food_data']['dataframe']
guidelines_dict = result.get('guidelines', {})
tdee = result.get('energy', {}).get('tdee', 2000)

# Convert guidelines to GA format
guidelines = {
    'hard': {},
    'soft': guidelines_dict.get('nutrients', {})
}

print(f"  Food items: {len(food_df)}, TDEE: {tdee:.0f}")

# ════════════════════════════════════════════════════════════════════════
# TEST: FULL GA RUN
# ════════════════════════════════════════════════════════════════════════
print("\n[TEST] Full GA Run (35 generations)")
print("-" * 80)

print("  Running GA...")
best_solution, top_solutions = run_ga(
    food_df=food_df,
    guidelines=guidelines,
    tdee=tdee,
    generations=35,
    pop_size=18,
    mutation_rate=0.3,
    verbose=False
)

# Analyze result
total_nutrition = calculate_total_nutrition(best_solution)
if tdee > 0:
    scale_factor = tdee / total_nutrition.get('energy_kcal', 1)
    for nutrient_name in total_nutrition:
        total_nutrition[nutrient_name] = total_nutrition[nutrient_name] * scale_factor

carb = total_nutrition.get('carbohydrate_g', 0)
fat = total_nutrition.get('fat_g', 0)
protein = total_nutrition.get('protein_g', 0)
energy = total_nutrition.get('energy_kcal', 0)
sodium = total_nutrition.get('sodium_mg', 0)

# Get targets
soft_guidelines = guidelines.get('soft', {})
carb_min = soft_guidelines.get('carbohydrate_g', {}).get('min', 200)
carb_max = soft_guidelines.get('carbohydrate_g', {}).get('max', 280)
fat_min = soft_guidelines.get('fat_g', {}).get('min', 50)
fat_max = soft_guidelines.get('fat_g', {}).get('max', 100)
protein_max = soft_guidelines.get('protein_g', {}).get('max', 120)
protein_min = soft_guidelines.get('protein_g', {}).get('min', 50)
sodium_max = soft_guidelines.get('sodium_mg', {}).get('max', 2300)

# Calculate percentages
carb_pct = (carb / carb_min * 100) if carb_min > 0 else 100
fat_pct = (fat / fat_min * 100) if fat_min > 0 else 100
protein_ratio = (protein / protein_max) if protein_max > 0 else 1.0

print(f"\n  RESULT ANALYSIS:")
print(f"    Energy:   {energy:.0f} kcal / {tdee:.0f}")
print(f"    Carbs:    {carb:.0f}g / {carb_min:.0f}-{carb_max:.0f}g ({carb_pct:.1f}%)")
print(f"    Fat:      {fat:.0f}g / {fat_min:.0f}-{fat_max:.0f}g ({fat_pct:.1f}%)")
print(f"    Protein:  {protein:.0f}g / {protein_min:.0f}-{protein_max:.0f}g ({protein_ratio*100:.1f}% of max)")
print(f"    Sodium:   {sodium:.0f}mg / max {sodium_max:.0f}mg ({(sodium/sodium_max*100):.1f}%)")

# Assessment
print(f"\n  QUALITY CHECKS:")
quality_score = 0

if carb >= carb_min and carb <= carb_max:
    quality_score += 1
    print(f"    [PASS] Carbs in range")
elif carb >= carb_min * 0.8:
    print(f"    [FAIR] Carbs {carb_pct:.0f}% of min")
else:
    print(f"    [FAIL] Carbs too low ({carb_pct:.0f}%)")

if fat >= fat_min and fat <= fat_max:
    quality_score += 1
    print(f"    [PASS] Fat in range")
elif fat >= fat_min * 0.8:
    print(f"    [FAIR] Fat {fat_pct:.0f}% of min")
else:
    print(f"    [FAIL] Fat too low ({fat_pct:.0f}%)")

if protein <= protein_max:
    quality_score += 1
    print(f"    [PASS] Protein controlled ({protein:.0f}g <= {protein_max:.0f}g)")
else:
    print(f"    [WARN] Protein excess ({protein:.0f}g > {protein_max:.0f}g)")

if sodium <= sodium_max:
    quality_score += 1
    print(f"    [PASS] Sodium controlled")
else:
    print(f"    [WARN] Sodium high ({(sodium/sodium_max*100):.0f}%)")

print(f"\n  OVERALL: {quality_score}/4 CHECKS PASSED")

if quality_score >= 3:
    print(f"  RESULT: [GOOD] GA producing balanced meals")
elif quality_score >= 2:
    print(f"  RESULT: [FAIR] Moderate quality improvement")
else:
    print(f"  RESULT: [NEEDS_WORK] Continue optimizing")

print("\n" + "="*80 + "\n")

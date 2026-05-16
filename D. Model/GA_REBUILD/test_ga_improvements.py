"""
TEST: GA Quality Improvements - Macronutrient Prioritization
===========================================================

Verify:
1. Fitness penalties correctly prioritize macronutrients
2. Mutation selects nutrient-aware foods
3. GA produces balanced nutrition (not POOR status)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../C. System Flow'))

from ga_v1 import fitness, mutation, random_solution, run_ga, calculate_total_nutrition
from nutrition_service import NutritionService

print("\n" + "="*80)
print("[TEST] GA Quality Improvements - Macronutrient Prioritization")
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

print(f"  [OK] Setup complete: TDEE={tdee:.0f}kcal, {len(food_df)} foods")

# ════════════════════════════════════════════════════════════════════════
# TEST 1: MACRONUTRIENT PENALTY VERIFICATION
# ════════════════════════════════════════════════════════════════════════
print("\n[TEST 1] Fitness Penalties - Macronutrient Priority")
print("-" * 80)

# Create two solutions: one with low carbs, one with good carbs
sol_low_carb = random_solution(food_df)
sol_good_balance = random_solution(food_df)

# Try to find/create solution with better carbs by sampling
for _ in range(10):
    candidate = random_solution(food_df)
    if candidate['carbohydrate_g'].sum() > sol_good_balance['carbohydrate_g'].sum():
        sol_good_balance = candidate

carb_low = sol_low_carb['carbohydrate_g'].sum()
carb_good = sol_good_balance['carbohydrate_g'].sum()

fitness_low = fitness(sol_low_carb, guidelines, tdee=tdee)
fitness_good = fitness(sol_good_balance, guidelines, tdee=tdee)

print(f"  Solution 1 (Low Carbs):  {carb_low:.0f}g → Fitness = {fitness_low:.2f}")
print(f"  Solution 2 (Good Carbs): {carb_good:.0f}g → Fitness = {fitness_good:.2f}")

if carb_good > carb_low:
    if fitness_good < fitness_low:
print(f"  [PASS] TEST 1 PASSED: Better carbs = Lower fitness (better score)")
        else:
            print(f"  [WARN] TEST 1 WARNING: Fitness not strongly favoring carbs")
        else:
            print(f"  [INFO] TEST 1 INFO: Random solutions didn't show carb difference")

# ════════════════════════════════════════════════════════════════════════
# TEST 2: MUTATION INTELLIGENT SELECTION
# ════════════════════════════════════════════════════════════════════════
print("\n[TEST 2] Mutation - Nutrient-Aware Food Selection")
print("-" * 80)

solution = random_solution(food_df)
carb_before = solution['carbohydrate_g'].sum()
fat_before = solution['fat_g'].sum()
protein_before = solution['protein_g'].sum()

# Apply guided mutations with 100% rate
for _ in range(5):
    solution = mutation(solution, food_df, mutation_rate=1.0, 
                       guidelines=guidelines, tdee=tdee)

carb_after = solution['carbohydrate_g'].sum()
fat_after = solution['fat_g'].sum()
protein_after = solution['protein_g'].sum()

print(f"  BEFORE: Carbs={carb_before:.0f}g, Fat={fat_before:.0f}g, Protein={protein_before:.0f}g")
print(f"  AFTER:  Carbs={carb_after:.0f}g, Fat={fat_after:.0f}g, Protein={protein_after:.0f}g")

# Check if mutation is working to improve deficiencies
guidance_score = 0
if carb_before < 200 and carb_after >= carb_before:
    guidance_score += 1
    print(f"  [OK] Carb guidance working (increased or stable)")
if fat_before < 50 and fat_after >= fat_before:
    guidance_score += 1
    print(f"  [OK] Fat guidance working (increased or stable)")
if protein_before > 120 and protein_after <= protein_before:
    guidance_score += 1
    print(f"  [OK] Protein control working (decreased or stable)")

print(f"  Guidance Score: {guidance_score}/3")

# ════════════════════════════════════════════════════════════════════════
# TEST 3: FULL GA RUN - QUALITY CHECK
# ════════════════════════════════════════════════════════════════════════
print("\n[TEST 3] Full GA Run - Quality & Balance Check")
print("-" * 80)

print("  Running GA (30 gen, 15 pop)...")
best_solution, top_solutions = run_ga(
    food_df=food_df,
    guidelines=guidelines,
    tdee=tdee,
    generations=30,
    pop_size=15,
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
fat_min = soft_guidelines.get('fat_g', {}).get('min', 50)
protein_max = soft_guidelines.get('protein_g', {}).get('max', 120)
sodium_max = soft_guidelines.get('sodium_mg', {}).get('max', 2300)

# Calculate percentages
carb_pct = (carb / carb_min * 100) if carb_min > 0 else 100
fat_pct = (fat / fat_min * 100) if fat_min > 0 else 100
protein_pct = (protein_max / protein * 100) if protein > 0 else 100

print(f"\n  MEAL PLAN ANALYSIS:")
print(f"    Energy:   {energy:.0f} kcal")
print(f"    Carbs:    {carb:.0f}g (target {carb_min:.0f}g) → {carb_pct:.0f}%")
print(f"    Fat:      {fat:.0f}g (target {fat_min:.0f}g) → {fat_pct:.0f}%")
print(f"    Protein:  {protein:.0f}g (max {protein_max:.0f}g) → {protein_pct:.0f}% of max")
print(f"    Sodium:   {sodium:.0f}mg (max {sodium_max:.0f}mg) → {(sodium/sodium_max*100):.0f}% of max")

# Quality assessment
quality_score = 0
issues = []

if carb_pct >= 80:
    quality_score += 1
    print(f"  [OK] Carbs: {carb_pct:.0f}% - GOOD")
else:
    issues.append(f"Carbs only {carb_pct:.0f}%")
    print(f"  [WARN] Carbs: {carb_pct:.0f}% - NEEDS IMPROVEMENT")

if fat_pct >= 80:
    quality_score += 1
    print(f"  [OK] Fat: {fat_pct:.0f}% - GOOD")
else:
    issues.append(f"Fat only {fat_pct:.0f}%")
    print(f"  [WARN] Fat: {fat_pct:.0f}% - NEEDS IMPROVEMENT")

if protein_pct >= 80:
    quality_score += 1
    print(f"  [OK] Protein: {protein_pct:.0f}% of max - GOOD")
else:
    issues.append(f"Protein {protein_pct:.0f}% of max")
    print(f"  [WARN] Protein: {protein_pct:.0f}% of max - TOO MUCH")

if sodium < sodium_max:
    quality_score += 1
    print(f"  [OK] Sodium: {sodium:.0f}mg - CONTROLLED")
else:
    issues.append(f"Sodium {(sodium/sodium_max*100):.0f}% of max")
    print(f"  [WARN] Sodium: {(sodium/sodium_max*100):.0f}% of max - HIGH")

# Overall assessment
print(f"\n  OVERALL QUALITY: {quality_score}/4")
if quality_score >= 3:
    print(f"  Status: [GOOD] Improved GA quality detected")
elif quality_score >= 2:
    print(f"  Status: [FAIR] Moderate improvement")
else:
    print(f"  Status: [NEEDS_WORK] {issues}")

print("\n" + "="*80)
print("[TEST COMPLETE]")
print("="*80 + "\n")

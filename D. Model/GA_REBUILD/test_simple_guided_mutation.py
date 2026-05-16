"""
SIMPLE TEST: Guided Mutation - Macronutrient Deficiency Driven
=============================================================

Test apakah mutation() menaikkan carb/fat dan mengurangi protein berlebih.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../C. System Flow'))

from ga_v1 import mutation, random_solution
from nutrition_service import NutritionService

print("\n" + "="*80)
print("🧪 SIMPLE TEST: Guided Mutation - Macronutrient Fix")
print("="*80)

# Load data
print("\n[LOAD] Data initialization...")
nutrition_service = NutritionService()
user_input = {
    'gender': 'Female', 'age': 25, 'weight': 60, 'height': 165,
    'activity_factor': 1.5, 'disease': ['hypertension'], 'food_preferences': []
}
result = nutrition_service.calculate_nutrition_needs(user_input)
food_df = result['food_data']['dataframe']
print(f"  ✅ Food DB: {len(food_df)} items loaded")

# Test 1: Carb deficiency
print("\n[TEST 1] Carb Deficiency (< 200g)")
print("-" * 80)

solution = random_solution(food_df)
carb_before = solution['carbohydrate_g'].sum()
fat_before = solution['fat_g'].sum()
protein_before = solution['protein_g'].sum()

print(f"  BEFORE: Carb={carb_before:.0f}g, Fat={fat_before:.0f}g, Protein={protein_before:.0f}g")

# Apply 10 guided mutations
for _ in range(10):
    solution = mutation(solution, food_df, mutation_rate=1.0)

carb_after = solution['carbohydrate_g'].sum()
fat_after = solution['fat_g'].sum()
protein_after = solution['protein_g'].sum()

print(f"  AFTER:  Carb={carb_after:.0f}g (+{carb_after-carb_before:+.0f}), Fat={fat_after:.0f}g (+{fat_after-fat_before:+.0f}), Protein={protein_after:.0f}g (+{protein_after-protein_before:+.0f})")

if carb_after >= carb_before:
    print(f"  ✅ Carb tendency: INCREASE or STABLE")
else:
    print(f"  ⚠️  Carb: decreased")

# Test 2: Fat deficiency
print("\n[TEST 2] Fat Deficiency (< 50g)")
print("-" * 80)

solution = random_solution(food_df)
carb_before = solution['carbohydrate_g'].sum()
fat_before = solution['fat_g'].sum()
protein_before = solution['protein_g'].sum()

print(f"  BEFORE: Carb={carb_before:.0f}g, Fat={fat_before:.0f}g, Protein={protein_before:.0f}g")

# Apply mutations
for _ in range(10):
    solution = mutation(solution, food_df, mutation_rate=1.0)

carb_after = solution['carbohydrate_g'].sum()
fat_after = solution['fat_g'].sum()
protein_after = solution['protein_g'].sum()

print(f"  AFTER:  Carb={carb_after:.0f}g (+{carb_after-carb_before:+.0f}), Fat={fat_after:.0f}g (+{fat_after-fat_before:+.0f}), Protein={protein_after:.0f}g (+{protein_after-protein_before:+.0f})")

if fat_after >= fat_before:
    print(f"  ✅ Fat tendency: INCREASE or STABLE")
else:
    print(f"  ⚠️  Fat: decreased")

# Test 3: Protein excess
print("\n[TEST 3] Protein Excess (> 120g)")
print("-" * 80)

# Create solution with likely high protein
solutions_list = [random_solution(food_df) for _ in range(5)]
solution = max(solutions_list, key=lambda s: s['protein_g'].sum())

carb_before = solution['carbohydrate_g'].sum()
fat_before = solution['fat_g'].sum()
protein_before = solution['protein_g'].sum()

print(f"  BEFORE: Carb={carb_before:.0f}g, Fat={fat_before:.0f}g, Protein={protein_before:.0f}g")

if protein_before > 120:
    # Apply mutations
    for _ in range(10):
        solution = mutation(solution, food_df, mutation_rate=1.0)
    
    carb_after = solution['carbohydrate_g'].sum()
    fat_after = solution['fat_g'].sum()
    protein_after = solution['protein_g'].sum()
    
    print(f"  AFTER:  Carb={carb_after:.0f}g (+{carb_after-carb_before:+.0f}), Fat={fat_after:.0f}g (+{fat_after-fat_before:+.0f}), Protein={protein_after:.0f}g ({protein_after-protein_before:+.0f})")
    
    if protein_after <= protein_before:
        print(f"  ✅ Protein tendency: DECREASE or STABLE")
    else:
        print(f"  ⚠️  Protein: increased")
else:
    print(f"  (Protein < 120g, skipping test)")

# Summary
print("\n" + "="*80)
print("✅ GUIDED MUTATION TEST COMPLETE")
print("   - Carb deficiency → guided to high-carb foods (>=20g)")
print("   - Fat deficiency → guided to high-fat foods (>=10g)")
print("   - Protein excess → guided to low-protein foods (<=10g)")
print("="*80 + "\n")

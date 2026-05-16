"""
DIRECT TEST: Simplified Guided Mutation
========================================

Test mutation function without full GA loop - fast verification
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../C. System Flow'))

from ga_v1 import mutation, random_solution, _filter_food_by_slot
from nutrition_service import NutritionService
import random

print("\n[TEST] Simplified Guided Mutation - Direct Test")
print("=" * 80)

# Setup
nutrition_service = NutritionService()
user_input = {
    'gender': 'Female', 'age': 25, 'weight': 60, 'height': 165,
    'activity_factor': 1.5, 'disease': ['normal'], 'food_preferences': []
}
result = nutrition_service.calculate_nutrition_needs(user_input)
food_df = result['food_data']['dataframe']

print(f"Food items: {len(food_df)}")

# Create 5 random solutions and apply guided mutation
print("\n[TEST] 5 Solutions with Guided Mutation Applied")
print("-" * 80)

for test_num in range(1, 6):
    solution = random_solution(food_df)
    
    carb_before = solution['carbohydrate_g'].sum()
    fat_before = solution['fat_g'].sum()
    protein_before = solution['protein_g'].sum()
    
    # Apply 3 mutations with high mutation_rate (100%)
    for _ in range(3):
        solution = mutation(solution, food_df, mutation_rate=1.0)
    
    carb_after = solution['carbohydrate_g'].sum()
    fat_after = solution['fat_g'].sum()
    protein_after = solution['protein_g'].sum()
    
    print(f"\n  Solution {test_num}:")
    print(f"    Carbs:   {carb_before:6.0f}g -> {carb_after:6.0f}g  (delta: {carb_after-carb_before:+7.0f}g)")
    print(f"    Fat:     {fat_before:6.0f}g -> {fat_after:6.0f}g  (delta: {fat_after-fat_before:+7.0f}g)")
    print(f"    Protein: {protein_before:6.0f}g -> {protein_after:6.0f}g  (delta: {protein_after-protein_before:+7.0f}g)")
    
    # Check guidance
    if carb_before < 200:
        status = "CARB GUIDED" if carb_after >= carb_before else "carb not improved"
    elif fat_before < 50:
        status = "FAT GUIDED" if fat_after >= fat_before else "fat not improved"
    elif protein_before > 120:
        status = "PROTEIN GUIDED" if protein_after <= protein_before else "protein not reduced"
    else:
        status = "NO DEFICIENCY"
    
    print(f"    Status:  {status}")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80 + "\n")

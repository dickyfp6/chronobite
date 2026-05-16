"""
TEST: GA with Simplified Guided Mutation
==========================================

Verifikasi bahwa GA produce nutrient-balanced meal plans
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../C. System Flow'))

from ga_v1 import run_ga
from nutrition_service import NutritionService

print("\n" + "="*80)
print("[TEST] GA with Simplified Guided Mutation")
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

print(f"  Food items: {len(food_df)}")
print(f"  TDEE: {tdee:.0f} kcal")
print(f"  Guidelines: {len(guidelines_dict.get('nutrients', {}))} constraints")

# Convert guidelines to GA format (hard/soft)
guidelines = {
    'hard': {},
    'soft': guidelines_dict.get('nutrients', {})
}

# Run GA
print("\n[RUN] GA 50 generations, 20 population...")
result_tuple = run_ga(
    food_df=food_df,
    guidelines=guidelines,
    tdee=tdee,
    generations=50,
    pop_size=20,
    mutation_rate=0.3,
    verbose=False
)

# Extract best solution (could be tuple or direct values)
if isinstance(result_tuple, tuple) and len(result_tuple) >= 2:
    best_solution = result_tuple[0]
else:
    best_solution = result_tuple

# Analyze results
print("\n[RESULT] Best Solution Analysis")
print("-" * 80)

energy = best_solution['energy_kcal'].sum()
carb = best_solution['carbohydrate_g'].sum()
fat = best_solution['fat_g'].sum()
protein = best_solution['protein_g'].sum()
fiber = best_solution['fiber_g'].sum() if 'fiber_g' in best_solution.columns else 0
sodium = best_solution['sodium_mg'].sum()

print(f"  Energy:    {energy:.0f} kcal (target {tdee:.0f})")
print(f"  Carbs:     {carb:.0f}g")
print(f"  Fat:       {fat:.0f}g")
print(f"  Protein:   {protein:.0f}g")
print(f"  Fiber:     {fiber:.0f}g")
print(f"  Sodium:    {sodium:.0f}mg")

# Check targets
soft_guidelines = guidelines.get('soft', {})
targets = {
    'carbohydrate_g': soft_guidelines.get('carbohydrate_g', {}).get('min', 200),
    'fat_g': soft_guidelines.get('fat_g', {}).get('min', 50),
    'protein_g': soft_guidelines.get('protein_g', {}).get('max', 120),
    'fiber_g': soft_guidelines.get('fiber_g', {}).get('min', 25),
}

print("\n[TARGETS]")
print(f"  Carbs:     {carb:.0f}g (target >= {targets['carbohydrate_g']:.0f}g): {'OK' if carb >= targets['carbohydrate_g'] else 'LOW'}")
print(f"  Fat:       {fat:.0f}g (target >= {targets['fat_g']:.0f}g): {'OK' if fat >= targets['fat_g'] else 'LOW'}")
print(f"  Protein:   {protein:.0f}g (target <= {targets['protein_g']:.0f}g): {'OK' if protein <= targets['protein_g'] else 'HIGH'}")
print(f"  Fiber:     {fiber:.0f}g (target >= {targets['fiber_g']:.0f}g): {'OK' if fiber >= targets['fiber_g'] else 'LOW'}")

print("\n[MEAL PLAN]")
meals = ['Breakfast Main', 'Breakfast Side', 'Breakfast Drink', 
         'Lunch Main', 'Lunch Side', 'Lunch Drink',
         'Dinner Main', 'Dinner Side', 'Dinner Drink', 'Snack']
for i, meal in enumerate(meals):
    food_name = best_solution.iloc[i]['food_name']
    food_kcal = best_solution.iloc[i]['energy_kcal']
    print(f"  {meal:20s}: {food_name:40s} ({food_kcal:.0f} kcal)")

print("\n" + "="*80)
print("TEST COMPLETE")
print("="*80 + "\n")

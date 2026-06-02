"""
Test Two-Phase Greedy Algorithm (Drink First)
"""

import sys
import os
import pandas as pd
from typing import Dict

# Add paths
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, root_dir)
sys.path.insert(0, os.path.join(root_dir, 'C. System Flow'))
sys.path.insert(0, os.path.join(root_dir, 'D. Model'))
sys.path.insert(0, os.path.join(root_dir, 'D. Model', 'Greedy Algorithm'))

# Import local modules
try:
    from nutrition_service import NutritionService
except ImportError:
    # Try alternate path
    sys.path.insert(0, os.path.join(root_dir, 'C. System_Flow'))
    from nutrition_service import NutritionService
from greedy_interface import GreedyAlgorithmInterface

def test_two_phase():
    print("🚀 Starting Two-Phase Implementation Test...")
    
    # 1. Setup Service & Data
    ns = NutritionService()
    user_data = {
        'gender': 'M',
        'age': 25,
        'weight': 70,
        'height': 175,
        'activity_factor': 1.545,
        'diseases': ['normal']
    }
    
    result = ns.calculate_nutrition_needs(user_data)
    tdee = result['energy']['tdee']
    food_db = result['food_data']['dataframe']
    guidelines = result['guidelines']
    
    meal_dist = {
        'breakfast': 0.2375,
        'lunch': 0.3375,
        'snack': 0.1375,
        'dinner': 0.2875
    }
    
    # 2. Greedy Algorithm Phase 1: Drinks
    greedy = GreedyAlgorithmInterface()
    greedy.initialize(food_db, guidelines)
    
    print("\n--- PHASE 1: Drink Options ---")
    drink_options = greedy.generate_drink_options(meal_dist, tdee)
    
    selected_drinks = {}
    for meal, options in drink_options.items():
        if options:
            selected = options[0] # Pick the first one
            selected_drinks[meal] = selected
            print(f"Selected for {meal}: {selected.food_name} ({selected.energy_kcal:.1f} kcal, {selected.portion_gram}g)")
    
    # 3. Greedy Algorithm Phase 2: Complete Menu
    print("\n--- PHASE 2: Final Menu Generation ---")
    menu_plan = greedy.generate_menu_with_drinks(user_data, meal_dist, tdee, selected_drinks)
    
    if menu_plan:
        print(f"✅ Menu Generated Successfully!")
        print(f"Daily Calories: {menu_plan.total_daily_calories:.1f} kcal (Target: {tdee:.1f})")
        print(f"Feasible: {menu_plan.feasible}")
        
        meals = {
            'Breakfast': menu_plan.breakfast,
            'Lunch': menu_plan.lunch,
            'Dinner': menu_plan.dinner,
            'Snack': menu_plan.snack
        }
        
        for meal_name, meal in meals.items():
            if meal_name == 'Snack':
                print(f"\n{meal_name}: {meal.actual_calories:.1f} kcal")
                for item in meal.candidates:
                     print(f"  - [Snack Candidate] {item.food_name}: {item.energy_kcal:.1f} kcal ({item.portion_gram}g)")
                continue

            print(f"\n{meal_name}: {meal.actual_calories:.1f} kcal")
            for course_type, course in meal.courses.items():
                item = course.candidates[0]
                print(f"  - [{course_type}] {item.food_name}: {item.energy_kcal:.1f} kcal ({item.portion_gram}g)")
    else:
        print("❌ Menu Generation Failed")

if __name__ == "__main__":
    test_two_phase()

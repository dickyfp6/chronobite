import sys
import os
import json
import pandas as pd

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(base_dir, 'C. System Flow'))
sys.path.insert(0, os.path.join(base_dir, 'D. Model', 'Greedy Algorithm'))

from nutrition_service import NutritionService
from greedy_interface import GreedyAlgorithmInterface

def main():
    print("Initializing Nutrition Service...")
    ns = NutritionService()
    
    user_input = {
        'gender': 'M',
        'age': 30,
        'weight': 70,
        'height': 170,
        'activity_factor': 1.845,
        'disease': ['normal'],
        'food_preferences': ['Western']
    }
    
    print("Calculating Needs...")
    analysis = ns.calculate_nutrition_needs(user_input)
    tdee = analysis.get('energy', {}).get('tdee', 2200)
    guidelines = analysis.get('guidelines', {})
    
    print(f"TDEE: {tdee}")
    
    food_db = ns.guideline_loader.food_df.copy()
    
    # Filter like app_integrated
    food_preferences = user_input.get('food_preferences', [])
    allowed = [p.title() for p in food_preferences] + ['Generic']
    cuisine_col = 'cuisine' if 'cuisine' in food_db.columns else 'cuisine_label'
    if cuisine_col in food_db.columns:
        filtered = food_db[food_db[cuisine_col].isin(allowed)].copy()
        if len(filtered) >= 50:
            food_db = filtered
            
    print(f"Database size after filtering: {len(food_db)}")
    
    print("Initializing Greedy...")
    greedy = GreedyAlgorithmInterface(food_db, guidelines)
    
    print("Generating Menu Plan...")
    menu = greedy.generate_menu_plan(user_input, tdee)
    
    print("\n--- RESULTS ---")
    print(f"Total Calories: {menu.total_daily_calories}")
    
    for meal in [menu.breakfast, menu.lunch, menu.dinner, menu.snack]:
        print(f"\n{meal.meal_type.upper()}: {meal.actual_calories:.1f} kcal")
        if hasattr(meal, 'courses'):
            for c_name, course in meal.courses.items():
                cand = course.candidates[0]
                print(f"  {c_name}: {cand.food_name} ({cand.portion_gram}g) - {cand.energy_kcal:.1f} kcal")
                if len(course.candidates) > 1:
                    print(f"    Alt 1: {course.candidates[1].food_name} ({course.candidates[1].portion_gram}g)")
                    print(f"    Alt 2: {course.candidates[2].food_name} ({course.candidates[2].portion_gram}g)")
        else:
            cand = meal.candidates[0]
            print(f"  Snack: {cand.food_name} ({cand.portion_gram}g) - {cand.energy_kcal:.1f} kcal")

if __name__ == '__main__':
    main()

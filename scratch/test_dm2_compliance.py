import sys
import os
import pandas as pd

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, "C. System Flow"))
sys.path.insert(0, os.path.join(ROOT_DIR, "D. Model"))
sys.path.insert(0, os.path.join(ROOT_DIR, "D. Model", "greedy"))

from nutrition_service import NutritionService
from greedy_interface import GreedyAlgorithmInterface

def main():
    profile = {
        'gender': 'M',
        'age': 45,
        'weight': 70,
        'height': 175,
        'activity_factor': 1.4,
        'disease': ['dm2'],  # Test under DM2
        'food_preferences': [],
    }
    
    service = NutritionService()
    result = service.calculate_nutrition_needs(profile)
    tdee = result['energy']['tdee']
    food_df = result['food_data']['dataframe']
    
    greedy_api = GreedyAlgorithmInterface(food_df, result['guidelines'])
    menu = greedy_api.generate_menu_plan(profile, tdee)
    
    print("\n" + "="*80)
    print("GREEDY HARD CONSTRAINTS AUDIT FOR DM2")
    print("="*80)
    print(f"Total Daily Calories: {menu.total_daily_calories:.1f} kcal (Target TDEE: {tdee:.1f})")
    
    nutrients = result['guidelines']['nutrients']
    
    print(f"\n{'Nutrient':<25} {'Hard/Soft':<10} {'Min Target':>12} {'Max Target':>12} {'Actual Value':>12} {'Status':<10}")
    print("-" * 85)
    
    for nutrient, constraint in nutrients.items():
        if constraint.get('hard_soft_type') != 'HARD':
            continue
            
        actual = menu.daily_micronutrients.get(nutrient, 0.0)
        # Handle macro keys format
        if nutrient == 'energy_kcal':
            actual = menu.total_daily_calories
        elif nutrient == 'protein_g':
            actual = menu.total_daily_protein_g
        elif nutrient == 'carbohydrate_g':
            actual = menu.total_daily_carb_g
        elif nutrient == 'fat_g':
            actual = menu.total_daily_fat_g
            
        min_val = constraint.get('min')
        max_val = constraint.get('max')
        
        status = "OK"
        if min_val is not None and actual < min_val:
            status = "BELOW"
        elif max_val is not None and actual > max_val:
            status = "ABOVE"
            
        min_str = f"{min_val:.2f}" if min_val is not None else "None"
        max_str = f"{max_val:.2f}" if max_val is not None and max_val != float('inf') else "None"
        
        print(f"{nutrient:<25} {constraint.get('hard_soft_type'):<10} {min_str:>12} {max_str:>12} {actual:>12.2f} {status:<10}")

if __name__ == '__main__':
    main()

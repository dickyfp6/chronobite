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
        'disease': ['normal'],
        'food_preferences': [],
    }
    
    service = NutritionService()
    result = service.calculate_nutrition_needs(profile)
    tdee = result['energy']['tdee']
    food_df = result['food_data']['dataframe']
    
    greedy_api = GreedyAlgorithmInterface(food_df, result['guidelines'])
    
    orig_update = greedy_api.optimizer._update_cumulative
    
    def debug_update(item):
        print(f"Adding item: {item.food_name:<35} | portion={item.portion_gram}g | Cal: {item.energy_kcal:.1f} | P: {item.protein_g:.2f} | C: {item.carbohydrate_g:.2f} | F: {item.fat_g:.2f}")
        orig_update(item)
        print(f"Cumulative: Cal={greedy_api.optimizer.cumulative_nutrients['energy_kcal']:.1f} | P={greedy_api.optimizer.cumulative_nutrients['protein_g']:.2f} | C={greedy_api.optimizer.cumulative_nutrients['carbohydrate_g']:.2f} | F={greedy_api.optimizer.cumulative_nutrients['fat_g']:.2f}")
        
    greedy_api.optimizer._update_cumulative = debug_update
    menu = greedy_api.generate_menu_plan(profile, tdee)
    
    print("\nFinal menu plan returned to interface:")
    print(f"Total Daily Calories: {menu.total_daily_calories:.1f} kcal")
    print(f"Total Daily Protein: {menu.total_daily_protein_g:.1f} g")
    print(f"Total Daily Carbs: {menu.total_daily_carb_g:.1f} g")
    print(f"Total Daily Fat: {menu.total_daily_fat_g:.1f} g")

if __name__ == '__main__':
    main()

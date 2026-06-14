import sys
import os
import pandas as pd

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, "C. System Flow"))
sys.path.insert(0, os.path.join(ROOT_DIR, "D. Model"))
sys.path.insert(0, os.path.join(ROOT_DIR, "D. Model", "greedy"))
sys.path.insert(0, os.path.join(ROOT_DIR, "D. Model", "Genetic Algorithm"))

from nutrition_service import NutritionService
from greedy_interface import GreedyAlgorithmInterface
from ga_interface import GeneticAlgorithmInterface

def print_menu_details(menu, name):
    print("=" * 80)
    print(f"ALGORITHM: {name}")
    print("=" * 80)
    if not menu:
        print("Menu generation failed.")
        return
    
    print(f"Total Daily Calories: {menu.total_daily_calories:.1f} kcal")
    print(f"Total Daily Protein: {menu.total_daily_protein_g:.1f} g")
    print(f"Total Daily Carbs: {menu.total_daily_carb_g:.1f} g")
    print(f"Total Daily Fat: {menu.total_daily_fat_g:.1f} g")
    
    water_from_micros = menu.daily_micronutrients.get('water_g', 0.0)
    print(f"Daily Water (from daily_micronutrients): {water_from_micros:.1f} g ({water_from_micros/1000:.3f} Liters)")
    
    calculated_water = 0.0
    meals = [('Breakfast', menu.breakfast), ('Lunch', menu.lunch), ('Dinner', menu.dinner)]
    
    print(f"\n{'Meal/Course':<20} {'Food Name':<45} {'Gram':>6} {'Cal':>6} {'Water (g)':>10}")
    print("-" * 90)
    
    for m_name, meal in meals:
        if not meal:
            continue
        print(f"--- {m_name} ---")
        for course_name, course in meal.courses.items():
            if not course or not course.candidates:
                continue
            item = course.candidates[0]
            water = item.micronutrients.get('water_g', 0.0)
            calculated_water += water
            print(f"  {course_type_name(course_name):<18} {item.food_name[:35]:<35} (ID:{item.fdc_id}) {item.portion_gram:>5.0f}g {item.energy_kcal:>5.1f} {water:>9.1f}g")
            
    # Snack
    if menu.snack and menu.snack.candidates:
        print("--- Snack ---")
        item = menu.snack.candidates[0]
        water = item.micronutrients.get('water_g', 0.0)
        calculated_water += water
        print(f"  {'Snack':<18} {item.food_name[:35]:<35} (ID:{item.fdc_id}) {item.portion_gram:>5.0f}g {item.energy_kcal:>5.1f} {water:>9.1f}g")
        
    print("-" * 90)
    print(f"Calculated Water (sum of selected candidates): {calculated_water:.1f} g ({calculated_water/1000:.3f} Liters)")
    print("\n")

def course_type_name(c):
    return c

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
    if not result['success']:
        print("Error calculating nutrition needs:", result['error'])
        return
        
    tdee = result['energy']['tdee']
    food_df = result['food_data']['dataframe']
    guidelines = result['guidelines']['nutrients']
    
    # Run Greedy
    greedy_api = GreedyAlgorithmInterface(food_df, result['guidelines'])
    menu_greedy = greedy_api.generate_menu_plan(profile, tdee)
    print_menu_details(menu_greedy, "Greedy")
    
    # Run Genetic
    ga_api = GeneticAlgorithmInterface(food_df, result['guidelines'])
    menu_ga = ga_api.generate_menu_plan(profile, tdee)
    print_menu_details(menu_ga, "Genetic")

if __name__ == '__main__':
    main()

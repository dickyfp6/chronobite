import sys
import os
import pandas as pd

# Add paths
sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "C. System Flow")))
sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "D. Model")))
sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "D. Model", "Greedy Algorithm")))

from nutrition_service import NutritionService
from greedy_02_optimizer import GreedyOptimizer

def main():
    service = NutritionService()
    
    # Try to reproduce TDEE ~ 2429
    # M, age 22, weight 65, height 170, activity 1.845 gives:
    # BMR: 88.362 + 13.397*65 + 4.799*170 - 5.677*22 = 88.362 + 870.805 + 815.83 - 124.894 = 1650.1
    # TDEE: 1650.1 * 1.845 = 3044.
    # What about: M, age 25, weight 70, height 170, sedentary (1.545)?
    # Bmr: 88.362 + 13.397*70 + 4.799*170 - 5.677*25 = 88.362 + 937.79 + 815.83 - 141.925 = 1700
    # Tdee: 1700 * 1.545 = 2626
    # Let's check different combinations or just run with user_input where we override or check guidelines.
    
    user_input = {
        'gender': 'M',
        'age': 30,
        'weight': 62.5,
        'height': 168,
        'activity_factor': 1.545,  # sedentary
        'disease': ['normal'],
        'food_preferences': []
    }
    
    # We will compute guidelines and then force TDEE to 2429
    res = service.calculate_nutrition_needs(user_input)
    if not res['success']:
        print(f"Error calculating needs: {res['error']}")
        return
        
    tdee = 2429.0
    print(f"TDEE: {tdee}")
    guidelines = res['guidelines']
    food_db = service.guideline_loader.food_df.copy()
    
    # Filter database by Western and Generic cuisine
    food_db = food_db[food_db['cuisine'].isin(['Western', 'Generic'])].copy()
    print(f"Number of Western + Generic foods: {len(food_db)}")
    
    # Run optimizer
    optimizer = GreedyOptimizer(food_db, guidelines)
    
    # Let's inspect the food candidates for Breakfast
    breakfast_target = tdee * 0.2375
    print(f"Breakfast Target: {breakfast_target} kcal")
    
    # Run portion optimizer directly on the top candidates
    # Main: Breaded Chicken Tenders, Side: Reduced-Calorie White Bread, Drink: maybe some drink
    main_df = food_db[food_db['food_name'].str.contains("Breaded Chicken Tenders|Chicken Tenders", case=False)]
    side_df = food_db[food_db['food_name'].str.contains("Reduced-Calorie White Bread|White Bread|Bread", case=False)]
    drink_df = food_db[food_db['food_name'].str.contains("Tea|Water|Coffee|Cola|Juice", case=False)]
    
    print("\nMain matches:")
    print(main_df[['fdc_id', 'food_name', 'energy_kcal', 'cuisine']])
    print("\nSide matches:")
    print(side_df[['fdc_id', 'food_name', 'energy_kcal', 'cuisine']])
    
    if len(main_df) > 0 and len(side_df) > 0:
        main_item = main_df.iloc[0].to_dict()
        side_item = side_df.iloc[0].to_dict()
        drink_item = drink_df.iloc[0].to_dict() if len(drink_df) > 0 else None
        
        # Calculate targets for optimizer
        tdee_est = breakfast_target / 0.2375
        min_target = tdee_est * 0.20
        max_target = tdee_est * 0.25
        print(f"Optimizer meal target range: [{min_target}, {max_target}]")
        
        # Call optimize_meal_portions
        portions = optimizer.optimize_meal_portions(
            main_item, side_item, drink_item,
            min_target, max_target
        )
        print(f"\nOptimized portions: Main={portions[0]}g, Side={portions[1]}g, Drink={portions[2]}g")
        
        # Print calories for these portions
        cal_m = (portions[0] * main_item['energy_kcal']) / 100.0
        cal_s = (portions[1] * side_item['energy_kcal']) / 100.0
        cal_d = (portions[2] * drink_item['energy_kcal']) / 100.0 if drink_item else 0.0
        print(f"Main calories: {cal_m:.2f} kcal")
        print(f"Side calories: {cal_s:.2f} kcal")
        print(f"Drink calories: {cal_d:.2f} kcal")
        print(f"Total: {cal_m + cal_s + cal_d:.2f} kcal")
        
        # Let's inspect the micro penalties
        nutrients = guidelines.get('nutrients', {})
        hard_micros = {}
        for nutrient, constraint in nutrients.items():
            if nutrient in ['energy_kcal', 'protein_g', 'carbohydrate_g', 'fat_g']:
                continue
            if constraint.get('hard_soft_type') == 'HARD' and constraint.get('constraint_type') != 'unlimited':
                hard_micros[nutrient] = {
                    'min': float(constraint.get('min') or 0.0),
                    'max': float(constraint.get('max') or float('inf')),
                    'val_m': float(main_item.get(nutrient, 0) or 0),
                    'val_s': float(side_item.get(nutrient, 0) or 0),
                    'val_d': float(drink_item.get(nutrient, 0) or 0) if drink_item else 0.0,
                    'cumulative': 0.0
                }
        
        print("\nHard Micronutrient Constraints:")
        for nutrient, info in hard_micros.items():
            print(f"  {nutrient}: min={info['min']}, max={info['max']}")
            
        # Run menu generation fully
        menu_plan = optimizer.generate_menu(user_input, tdee)
        print("\n=== GENERATED MENU PLAN ===")
        print(f"Total Daily Calories: {menu_plan.total_daily_calories:.1f} kcal")
        for meal in [menu_plan.breakfast, menu_plan.lunch, menu_plan.dinner, menu_plan.snack]:
            print(f"\n{meal.meal_type.upper()} actual calories: {meal.actual_calories:.1f}")
            for course in meal.courses.values():
                if course.candidates:
                    cand = course.candidates[0]
                    print(f"  {course.course_type}: {cand.food_name} ({cand.portion_gram}g) - {cand.energy_kcal:.1f} kcal")

if __name__ == "__main__":
    main()

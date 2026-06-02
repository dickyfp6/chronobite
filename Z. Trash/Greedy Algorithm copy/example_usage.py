#!/usr/bin/env python3
"""
CLEAN EXAMPLE: How to use Greedy Algorithm
==============================================

Data Flow:
1. User input (gender, age, weight, height, activity, disease)
2. NutritionService.calculate_nutrition_needs() → returns constraint_bag
3. GreedyAlgorithmInterface.initialize(food_db, constraint_bag)
4. GreedyAlgorithmInterface.generate_menu_plan() → returns MenuPlan

This example shows the complete workflow.
"""

import sys
import os

# Add directories
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(parent_dir)
system_flow_dir = os.path.join(root_dir, 'C. System Flow')

sys.path.insert(0, current_dir)
sys.path.insert(0, parent_dir)
sys.path.insert(0, root_dir)
sys.path.insert(0, system_flow_dir)


def main():
    """
    Complete example: From user input to menu generation
    """
    
    print("\n" + "="*80)
    print("GREEDY ALGORITHM - USAGE EXAMPLE")
    print("="*80 + "\n")
    
    # ========== STEP 1: USER INPUT ==========
    print("STEP 1: Prepare User Input")
    print("-" * 80)
    
    user_input = {
        'gender': 'M',
        'age': 35,
        'weight': 75.0,
        'height': 175.0,
        'activity_factor': 1.55,  # Lightly active
        'disease': 'normal',
        'food_preferences': ['Indonesian', 'Asian']
    }
    
    print(f"User: {user_input['gender']}, {user_input['age']}y, {user_input['weight']}kg")
    print(f"Height: {user_input['height']}cm, Activity: {user_input['activity_factor']}")
    print(f"Disease: {user_input['disease']}\n")
    
    
    # ========== STEP 2: CALCULATE NUTRITION NEEDS ==========
    print("\nSTEP 2: Get Nutrition Guidelines from NutritionService")
    print("-" * 80)
    
    from nutrition_service import NutritionService
    
    service = NutritionService()
    result = service.calculate_nutrition_needs(user_input)
    
    if not result.get('success'):
        print(f"Error: {result.get('error')}")
        return
    
    tdee = result['energy']['tdee']
    constraint_bag = result['guidelines']  # ← This is what we pass to algorithm
    food_database = result['food_data']['dataframe']
    
    print(f"✓ TDEE: {tdee:.0f} kcal/day")
    print(f"✓ BMR: {result['energy'].get('bmr', 'N/A'):.0f} kcal")
    print(f"✓ BMI: {result['anthropometrics'].get('bmi', 'N/A')}")
    print(f"✓ Constraint bag: {len(constraint_bag.get('nutrients', {}))} nutrient constraints")
    print(f"✓ Food database: {len(food_database)} items\n")
    
    
    # ========== STEP 3: INITIALIZE GREEDY ALGORITHM ==========
    print("\nSTEP 3: Initialize Greedy Algorithm")
    print("-" * 80)
    
    from greedy_interface import get_greedy_algorithm
    
    greedy = get_greedy_algorithm()
    
    if not greedy.initialize(food_database, constraint_bag):
        print("Failed to initialize Greedy Algorithm")
        return
    
    print("✓ Greedy Algorithm initialized\n")
    
    
    # ========== STEP 4: GENERATE MENU PLAN ==========
    print("\nSTEP 4: Generate Menu Plan")
    print("-" * 80)
    
    # Get meal distribution from NutritionService
    meal_distribution = result['user_params'].get('meal_distribution', {
        'breakfast': 0.2375,
        'lunch': 0.3375,
        'snack': 0.1375,
        'dinner': 0.2875
    })
    
    print(f"Meal distribution: {meal_distribution}\n")
    
    menu_plan = greedy.generate_menu_plan(
        user_profile=user_input,
        meal_distribution=meal_distribution,
        user_tdee=tdee
    )
    
    if not menu_plan:
        print("Failed to generate menu plan")
        return
    
    
    # ========== STEP 5: DISPLAY RESULTS ==========
    print("\nSTEP 5: Display Generated Menu Plan")
    print("-" * 80)
    
    print("\n📋 DAILY NUTRITIONAL SUMMARY:")
    print(f"  Calories: {menu_plan.total_daily_calories:.0f} kcal / {tdee:.0f} kcal target")
    print(f"  Protein: {menu_plan.total_daily_protein_g:.1f}g")
    print(f"  Carbs: {menu_plan.total_daily_carb_g:.1f}g")
    print(f"  Fat: {menu_plan.total_daily_fat_g:.1f}g")
    
    print(f"\n🍽️ MEALS:")
    
    # Breakfast
    if hasattr(menu_plan, 'breakfast') and menu_plan.breakfast:
        breakfast = menu_plan.breakfast
        print(f"  Breakfast ({breakfast.actual_calories:.0f}kcal):")
        if hasattr(breakfast, 'courses'):
            for course_name, course in breakfast.courses.items():
                if course and hasattr(course, 'candidates'):
                    for item in course.candidates:
                        print(f"    • {item.food_name}")
    
    # Lunch
    if hasattr(menu_plan, 'lunch') and menu_plan.lunch:
        lunch = menu_plan.lunch
        print(f"  Lunch ({lunch.actual_calories:.0f}kcal):")
        if hasattr(lunch, 'courses'):
            for course_name, course in lunch.courses.items():
                if course and hasattr(course, 'candidates'):
                    for item in course.candidates:
                        print(f"    • {item.food_name}")
    
    # Snack
    if hasattr(menu_plan, 'snack') and menu_plan.snack:
        snack = menu_plan.snack
        print(f"  Snack ({snack.actual_calories:.0f}kcal):")
        if hasattr(snack, 'candidates'):
            for item in snack.candidates:
                print(f"    • {item.food_name}")
    
    # Dinner
    if hasattr(menu_plan, 'dinner') and menu_plan.dinner:
        dinner = menu_plan.dinner
        print(f"  Dinner ({dinner.actual_calories:.0f}kcal):")
        if hasattr(dinner, 'courses'):
            for course_name, course in dinner.courses.items():
                if course and hasattr(course, 'candidates'):
                    for item in course.candidates:
                        print(f"    • {item.food_name}")
    
    # Constraint feasibility
    print(f"\n✅ CONSTRAINT FEASIBILITY:")
    if hasattr(menu_plan, 'feasible'):
        status = "FEASIBLE ✅" if menu_plan.feasible else "INFEASIBLE ⚠️"
        print(f"  Status: {status}")
        
        if hasattr(menu_plan, 'violations') and menu_plan.violations:
            print(f"  Violations: {len(menu_plan.violations)}")
            for violation in menu_plan.violations[:3]:
                print(f"    - {violation}")
    
    print("\n" + "="*80)
    print("✅ EXAMPLE COMPLETE")
    print("="*80 + "\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    print("  - comparison_algorithms()")
    
    # Print comparison untuk reference
    comparison_algorithms()

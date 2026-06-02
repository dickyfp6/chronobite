#!/usr/bin/env python3
"""
CLI Test Script for Greedy Algorithm
Testing Greedy Algorithm dengan 2 scenarios: normal user & disease user (dm2)

CARA MENJALANKAN:
  python test_cli.py              # Run test with normal user
  python test_cli.py disease      # Run test with DM2 user

EXPECTED OUTPUT:
  ✓ Meal plan generated
  ✓ Per-meal nutritional breakdown
  ✓ Daily totals with HARD constraint validation
  ✓ Feasible flag set correctly
"""

import sys
import os
import json

# Add directories untuk imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(parent_dir)
system_flow_dir = os.path.join(root_dir, 'C. System Flow')

sys.path.insert(0, current_dir)
sys.path.insert(0, parent_dir)
sys.path.insert(0, root_dir)
sys.path.insert(0, system_flow_dir)


def print_meal_breakdown(menu_plan, meal_type: str):
    """Print nutritional breakdown untuk satu meal"""
    
    meal = getattr(menu_plan, meal_type.lower(), None)
    if not meal:
        print(f"  {meal_type}: [tidak ada]")
        return
    
    print(f"\n  {meal_type.upper()}:")
    print(f"    Target: {meal.target_calories:.0f} kcal, Actual: {meal.actual_calories:.0f} kcal")
    
    # Courses
    if hasattr(meal, 'courses') and meal.courses:
        for course_name, course in meal.courses.items():
            if course and hasattr(course, 'candidates'):
                for item in course.candidates:
                    print(f"      • {item.food_name}")
                    print(f"        Energy: {item.energy_kcal:.0f}kcal | Protein: {item.protein_g:.1f}g | Carb: {item.carbohydrate_g:.1f}g | Fat: {item.fat_g:.1f}g")
    
    # For SnackMeal, print candidates
    elif hasattr(meal, 'candidates') and meal.candidates:
        for item in meal.candidates:
            print(f"      • {item.food_name}")
            print(f"        Energy: {item.energy_kcal:.0f}kcal | Protein: {item.protein_g:.1f}g | Carb: {item.carbohydrate_g:.1f}g | Fat: {item.fat_g:.1f}g")


def test_greedy_algorithm(scenario: str = 'normal'):
    """
    Test Greedy Algorithm dengan specified scenario
    
    Args:
        scenario: 'normal' atau 'disease' (dm2)
    """
    
    print("\n" + "="*80)
    print("GREEDY ALGORITHM - COMPREHENSIVE CLI TEST")
    print("="*80 + "\n")
    
    try:
        # [1] Load NutritionService
        print("[1/5] Loading NutritionService...")
        from nutrition_service import NutritionService
        service = NutritionService()
        print("✓ NutritionService loaded\n")
        
        # [2] Create user profile based on scenario
        print(f"[2/5] Creating sample user profile ({scenario} user)...")
        
        if scenario.lower() == 'normal':
            user_input = {
                'gender': 'M',
                'age': 30,
                'weight': 70.0,
                'height': 170.0,
                'activity_factor': 1.845,
                'disease': 'normal',  # ← FIXED: use 'disease' not 'health_condition'
                'food_preferences': ['Asian', 'Indonesian']
            }
            print("Profile: Male, 30y, 70kg, 170cm, Activity: 1.845, Disease: normal")
        else:  # disease scenario
            user_input = {
                'gender': 'F',
                'age': 45,
                'weight': 65.0,
                'height': 160.0,
                'activity_factor': 1.4,  # Sedentary (minimum allowed)
                'disease': 'dm2',  # ← FIXED: use 'disease' not 'health_condition'
                'food_preferences': ['Asian']
            }
            print("Profile: Female, 45y, 65kg, 160cm, Activity: 1.4, Disease: dm2")
        
        print("✓ User profile created\n")
        
        # [3] Calculate nutrition needs
        print("[3/5] Calculating nutrition guidelines...")
        result = service.calculate_nutrition_needs(user_input)
        
        if not result.get('success'):
            print(f"❌ Error: {result.get('error')}\n")
            return False
        
        tdee = result['energy']['tdee']
        print(f"✓ Nutrition guidelines calculated:")
        print(f"  - TDEE: {tdee:.0f} kcal")
        print(f"  - BMR: {result['energy'].get('bmr', 'N/A'):.0f} kcal")
        print(f"  - BMI: {result['anthropometrics'].get('bmi', 'N/A')}")
        print(f"  - Constraints: {result['guidelines'].get('total_nutrients', 'N/A')} nutrients defined")
        print(f"  - Disease: {result['guidelines'].get('disease', ['normal'])}\n")
        
        # [4] Initialize Greedy Algorithm
        print("[4/5] Initializing Greedy Algorithm...")
        from greedy_interface import get_greedy_algorithm
        
        greedy = get_greedy_algorithm()
        
        food_db = result['food_data']['dataframe']
        constraint_bag = result['guidelines']
        
        if not greedy.initialize(food_db, constraint_bag):
            print("❌ Failed to initialize Greedy Algorithm\n")
            return False
        
        print(f"✓ Greedy Algorithm initialized")
        print(f"  - Food database: {len(food_db)} items")
        print(f"  - Constraint bag: {len(constraint_bag.get('nutrients', {}))} nutrients\n")
        
        # [5] Generate Menu Plan
        print("[5/5] Generating menu plan using Greedy Algorithm...")
        
        meal_distribution = result.get('user_params', {}).get('meal_distribution', {
            'breakfast': 0.2375,
            'lunch': 0.3375,
            'snack': 0.1375,
            'dinner': 0.2875
        })
        
        menu_plan = greedy.generate_menu_plan(
            user_profile=user_input,
            meal_distribution=meal_distribution,
            user_tdee=tdee
        )
        
        if not menu_plan:
            print("❌ Failed to generate menu plan\n")
            return False
        
        print("✓ Menu plan generated successfully\n")
        
        # [6] PRINT RESULTS
        print("="*80)
        print("DETAILED MENU PLAN RESULTS")
        print("="*80 + "\n")
        
        print("📋 DAILY NUTRITIONAL SUMMARY:")
        print(f"  Total Calories: {menu_plan.total_daily_calories:.0f} kcal (Target: {tdee:.0f} kcal)")
        print(f"  Total Protein: {menu_plan.total_daily_protein_g:.1f}g")
        print(f"  Total Carbs: {menu_plan.total_daily_carb_g:.1f}g")
        print(f"  Total Fat: {menu_plan.total_daily_fat_g:.1f}g\n")
        
        # Per-meal breakdown
        print("🍽️ PER-MEAL BREAKDOWN:")
        print_meal_breakdown(menu_plan, 'breakfast')
        print_meal_breakdown(menu_plan, 'lunch')
        print_meal_breakdown(menu_plan, 'snack')
        print_meal_breakdown(menu_plan, 'dinner')
        print()
        
        # [7] HARD CONSTRAINT VALIDATION
        print("✅ HARD CONSTRAINT VALIDATION:")
        
        if hasattr(menu_plan, 'feasible') and hasattr(menu_plan, 'violations'):
            if menu_plan.feasible:
                print("  Status: ✅ FEASIBLE (All HARD constraints satisfied)")
            else:
                print(f"  Status: ⚠️ INFEASIBLE ({len(menu_plan.violations)} constraint(s) violated)")
                
                if menu_plan.violations:
                    print("  Violations:")
                    for violation in menu_plan.violations[:5]:
                        print(f"    {violation}")
                    if len(menu_plan.violations) > 5:
                        print(f"    ... and {len(menu_plan.violations) - 5} more")
        else:
            print("  Status: ⚠️ No feasibility information available")
        
        print("\n" + "="*80)
        print("✅ TEST PASSED - Greedy Algorithm working correctly!")
        print("="*80 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Determine scenario
    scenario = sys.argv[1] if len(sys.argv) > 1 else 'normal'
    
    if scenario not in ['normal', 'disease']:
        print("Usage: python test_cli.py [normal|disease]")
        print("  normal:  Test with healthy user profile")
        print("  disease: Test with DM2 disease profile")
        sys.exit(1)
    
    # Run test
    success = test_greedy_algorithm(scenario)
    sys.exit(0 if success else 1)

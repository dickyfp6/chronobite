#!/usr/bin/env python3
"""
CLI Test Script for Greedy Algorithm
Simple testing tool menggunakan command line
"""

import sys
import os
import json

# Add parent directories untuk imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(parent_dir)
system_flow_dir = os.path.join(root_dir, 'C. System Flow')

sys.path.insert(0, current_dir)
sys.path.insert(0, parent_dir)
sys.path.insert(0, root_dir)
sys.path.insert(0, system_flow_dir)

def test_greedy_basic():
    """Test basic Greedy Algorithm functionality"""
    print("\n" + "="*70)
    print("GREEDY ALGORITHM - CLI TEST")
    print("="*70 + "\n")
    
    try:
        # Import services
        print("[1/4] Loading NutritionService...")
        from nutrition_service import NutritionService
        service = NutritionService()
        print("✓ NutritionService loaded\n")
        
        # Sample user input
        print("[2/4] Creating sample user profile...")
        user_input = {
            'gender': 'M',
            'age': 30,
            'weight': 70.0,
            'height': 170.0,
            'activity_factor': 1.845,
            'health_condition': 'normal',
            'food_preferences': ['Asian', 'Indonesian']
        }
        print(f"✓ User Profile: {json.dumps(user_input, indent=2)}\n")
        
        # Calculate nutrition needs
        print("[3/4] Calculating nutrition needs...")
        result = service.calculate_nutrition_needs(user_input)
        
        if not result['success']:
            print(f"❌ Error: {result.get('error')}\n")
            return False
        
        print("✓ Nutrition needs calculated:")
        print(f"  - TDEE: {result.get('energy', {}).get('tdee', 'N/A')} kcal")
        print(f"  - Protein: {result.get('macros', {}).get('protein', 'N/A')}g")
        print(f"  - Carbs: {result.get('macros', {}).get('carbs', 'N/A')}g")
        print(f"  - Fat: {result.get('macros', {}).get('fat', 'N/A')}g\n")
        
        # Generate menu using Greedy Algorithm
        print("[4/4] Generating menu with Greedy Algorithm...")
        from greedy_interface import get_greedy_algorithm
        
        greedy = get_greedy_algorithm()
        
        # Initialize optimizer with data from result
        if not greedy.initialize(result['food_data']['dataframe'], result['guidelines']):
            print("❌ Failed to initialize Greedy Algorithm\n")
            return False
        
        # Define meal distribution
        meal_distribution = {
            'breakfast': 0.25,
            'lunch': 0.35,
            'snack': 0.05,
            'dinner': 0.35
        }
        
        # Generate menu
        menu = greedy.generate_menu_plan(
            user_profile=user_input,
            meal_distribution=meal_distribution,
            user_tdee=result.get('energy', {}).get('tdee', 2000)
        )
        
        if menu:
            print("✓ Menu generated successfully!\n")
            
            print("GENERATED MENU PLAN:")
            print("-" * 70)
            if hasattr(menu, '__dict__'):
                for meal, items in menu.__dict__.items():
                    print(f"\n{meal.upper()}: {items}")
            print("\n" + "="*70)
            print("✓ TEST PASSED")
            print("="*70 + "\n")
            return True
        else:
            print(f"❌ Menu generation failed\n")
            return False
            
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("   Make sure to run this from the project root directory:\n")
        print("   cd 'C:\\Users\\USERR\\Documents\\0. Mata Kuliah\\8 -TA\\Code\\TugasAkhirDSS'")
        print("   python 'D. Model/Greedy Algorithm/test_cli.py'\n")
        return False
    except Exception as e:
        print(f"❌ Test Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_greedy_with_disease():
    """Test Greedy Algorithm with specific health condition"""
    print("\n" + "="*70)
    print("GREEDY ALGORITHM - TEST WITH DISEASE")
    print("="*70 + "\n")
    
    try:
        from nutrition_service import NutritionService
        service = NutritionService()
        
        user_input = {
            'gender': 'F',
            'age': 45,
            'weight': 65.0,
            'height': 160.0,
            'activity_factor': 1.55,
            'health_condition': 'dm2',  # Diabetes Type 2
            'food_preferences': ['Asian']
        }
        
        print(f"User Profile (Diabetes Type 2):")
        print(f"  Age: {user_input['age']}, Gender: {user_input['gender']}")
        print(f"  Weight: {user_input['weight']}kg, Height: {user_input['height']}cm\n")
        
        result = service.calculate_nutrition_needs(user_input)
        
        if result['success']:
            print(f"✓ TDEE: {result.get('energy', {}).get('tdee', 'N/A')} kcal\n")
            
            from greedy_interface import get_greedy_algorithm
            
            greedy = get_greedy_algorithm()
            if not greedy.initialize(result['food_data']['dataframe'], result['guidelines']):
                print("❌ Failed to initialize\n")
                return False
            
            meal_distribution = {
                'breakfast': 0.25,
                'lunch': 0.35,
                'snack': 0.05,
                'dinner': 0.35
            }
            
            menu = greedy.generate_menu_plan(
                user_profile=user_input,
                meal_distribution=meal_distribution,
                user_tdee=result.get('energy', {}).get('tdee', 1800)
            )
            
            if menu:
                print("✓ Menu generated for DM2 patient!")
                print("="*70 + "\n")
                return True
        
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "disease":
        test_greedy_with_disease()
    else:
        test_greedy_basic()

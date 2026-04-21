"""
TEST GENETIC ALGORITHM - Integration with NutritionService
==========================================================

Test file untuk GA dengan NutritionService
- Input user data
- Calculate nutrition needs via NutritionService
- Run GA
- Display hasil
"""

import sys
import os

# Add paths untuk import
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
system_flow_path = os.path.join(project_root, 'C. System Flow')
ga_rebuild_path = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, system_flow_path)
sys.path.insert(0, ga_rebuild_path)

# Import GA engine
from ga_v1 import run_ga, display_solution, display_fitness_details

# Import NutritionService
try:
    from nutrition_service import NutritionService
    print("✓ NutritionService imported successfully")
except ImportError as e:
    print(f"✗ Cannot import NutritionService: {e}")
    sys.exit(1)


def get_simple_user_input(interactive=False):
    """
    Get user input either interactively or use defaults
    
    Args:
        interactive: If True, prompt for input. If False, use defaults.
    
    Returns:
        dict: user_input untuk NutritionService
    """
    print("\n" + "="*70)
    print("MEAL PLANNING SYSTEM - USER INPUT")
    print("="*70)
    
    if interactive:
        print("\n(Press Enter untuk gunakan default values)")
        
        gender = input("Gender (M/F) [M]: ").strip() or "M"
        age = int(input("Age (18-100) [25]: ").strip() or "25")
        weight = float(input("Weight (kg) [70]: ").strip() or "70")
        height = float(input("Height (cm) [170]: ").strip() or "170")
        activity = input("Activity Factor (1.4-2.2) [1.55]: ").strip() or "1.55"
        activity_factor = float(activity)
        
        print("\nHealth Conditions (comma-separated):")
        print("  Valid: normal, dm2, hypertension, cvd, cholesterol, ckd")
        disease_input = input("Diseases [normal]: ").strip() or "normal"
        disease = [d.strip() for d in disease_input.split(",")]
        
        print("\nFood Preferences (comma-separated):")
        print("  Valid: Asian, Western, Mediterranean, Generic")
        preferences_input = input("Preferences [Asian, Western]: ").strip() or "Asian, Western"
        food_preferences = [p.strip() for p in preferences_input.split(",")]
    else:
        # Use defaults (non-interactive)
        print("\n(Using default values)")
        gender = "M"
        age = 25
        weight = 70.0
        height = 170.0
        activity_factor = 1.55
        disease = ["normal"]
        food_preferences = ["Asian", "Western"]
    
    user_input = {
        'gender': gender,
        'age': age,
        'weight': weight,
        'height': height,
        'activity_factor': activity_factor,
        'disease': disease,
        'food_preferences': food_preferences
    }
    
    return user_input


def test_ga_with_nutrition_service():
    """
    Main flow: User input → NutritionService → GA → Output
    
    Steps:
        1. Get user input
        2. Call NutritionService.calculate_nutrition_needs()
        3. Extract food_df dan guidelines
        4. Run GA
        5. Display hasil
    """
    
    try:
        # STEP 1: Get user input
        print("\nSTEP 1: Get user input...")
        user_input = get_simple_user_input(interactive=False)  # Non-interactive (use defaults)
        
        print("\n✓ User input received")
        print(f"  Gender: {user_input['gender']}")
        print(f"  Age: {user_input['age']}, Weight: {user_input['weight']}kg, Height: {user_input['height']}cm")
        print(f"  Activity Factor: {user_input['activity_factor']}")
        print(f"  Diseases: {user_input['disease']}")
        print(f"  Food Preferences: {user_input['food_preferences']}")
        
        # STEP 2: Calculate nutrition require ments using NutritionService
        print("\n" + "="*70)
        print("STEP 2: Calculate nutrition requirements...")
        print("="*70)
        
        service = NutritionService()
        nutrition_result = service.calculate_nutrition_needs(user_input)
        
        # Check success
        if not nutrition_result['success']:
            print(f"✗ FAILED: {nutrition_result.get('error', 'Unknown error')}")
            return
        
        print("✓ Nutrition calculation successful")
        
        # STEP 3: Extract data dari nutrition_result
        print("\nSTEP 3: Extract data from NutritionService...")
        
        food_df = nutrition_result['food_data']['dataframe']
        guidelines = nutrition_result['guidelines']['nutrients']
        tdee = nutrition_result['energy']['tdee']
        
        print(f"✓ Data extracted:")
        print(f"  - Food items available: {len(food_df)}")
        print(f"  - Nutrition constraints: {len(guidelines)}")
        print(f"  - User TDEE: {tdee:.0f} kcal/day")
        
        # Display some info dari NutritionService
        print(f"\n📊 User Profile:")
        anthro = nutrition_result['anthropometrics']
        print(f"  - BMI: {anthro['bmi']:.1f} ({anthro['bmi_category']})")
        print(f"  - BBI: {anthro['bbi']:.1f} kg")
        energy = nutrition_result['energy']
        print(f"  - BMR: {energy['bmr']:.0f} kcal/day")
        print(f"  - TDEE: {energy['tdee']:.0f} kcal/day")
        
        # Display nutrition constraints
        print(f"\n🎯 Nutrition Guidelines (Top 10 constraints):")
        constraint_items = list(guidelines.items())[:10]
        for nutrient, constraint in constraint_items:
            min_val = constraint.get('min', 0)
            max_val = constraint.get('max', float('inf'))
            unit = constraint.get('unit', 'unit')
            print(f"  - {nutrient}: {min_val:.1f} - {max_val:.1f} {unit}")
        
        # STEP 4: Run GA
        print("\n" + "="*70)
        print("STEP 4: Run Genetic Algorithm...")
        print("="*70)
        
        best_solution, best_fitness = run_ga(
            food_df=food_df,
            guidelines=guidelines,
            generations=50,
            pop_size=20,
            elite_ratio=0.25,
            mutation_rate=0.3,
            verbose=True
        )
        
        # STEP 5: Display hasil
        print("\n" + "="*70)
        print("STEP 5: OPTIMAL MEAL PLAN - GA RESULT")
        print("="*70)
        
        display_solution(best_solution, guidelines)
        display_fitness_details(best_solution, guidelines)
        
        # STEP 6: Display food details
        print("\n" + "="*70)
        print("DETAILED FOOD INFORMATION:")
        print("="*70)
        
        meals = ['Breakfast', 'Lunch', 'Dinner', 'Snack']
        for i, meal_name in enumerate(meals):
            food_row = best_solution.iloc[i]
            print(f"\n{i+1}. {meal_name}:")
            
            # Display available columns
            important_cols = ['food_name', 'energy_kcal', 'protein_g', 'carbohydrate_g', 
                            'fat_g', 'fiber_g', 'cuisine']
            
            for col in important_cols:
                if col in food_row.index:
                    value = food_row[col]
                    if isinstance(value, (int, float)):
                        print(f"   {col}: {value:.1f}")
                    else:
                        print(f"   {col}: {value}")
        
        print("\n" + "="*70)
        print("✓ GA RUN COMPLETE")
        print("="*70 + "\n")
    
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_ga_with_nutrition_service()

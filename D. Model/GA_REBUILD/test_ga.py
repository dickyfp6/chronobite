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
import random
import numpy as np
import pandas as pd

# Set random seeds untuk reproducibility
random.seed(42)
np.random.seed(42)

# Add paths untuk import
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
system_flow_path = os.path.join(project_root, 'C. System Flow')
ga_rebuild_path = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, system_flow_path)
sys.path.insert(0, ga_rebuild_path)

# ============ MODE SWITCH ============
# Set to True to use interactive input via CLI
# Set to False to use hardcoded default values
USE_INTERACTIVE_INPUT = True
# ====================================

# Import GA engine
from ga_v1 import (
    run_ga, display_solution, generate_meal_options, display_meal_options, 
    display_fitness_details, MEAL_INDICES, calculate_total_nutrition, 
    SLOT_NAMES, CHROMOSOME_SIZE
)

# Import NutritionService
try:
    from nutrition_service import NutritionService
    print("✓ NutritionService imported successfully")
except ImportError as e:
    print(f"✗ Cannot import NutritionService: {e}")
    sys.exit(1)

# Import input handler
try:
    from modules.input_handler import get_user_input
    print("✓ Input handler imported successfully")
except ImportError as e:
    print(f"✗ Cannot import input handler: {e}")
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
        # print("\n(Using default values)")  # Commented out - using real input
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
        
        if USE_INTERACTIVE_INPUT:
            # Use interactive input handler from modules
            user_input = get_user_input()
        else:
            # Use default values (fallback)
            user_input = get_simple_user_input(interactive=False)
        
        print("\n✓ User input received")
        print(f"  Gender: {user_input['gender']}")
        print(f"  Age: {user_input['age']}, Weight: {user_input['weight']}kg, Height: {user_input['height']}cm")
        print(f"  Activity Factor: {user_input['activity_factor']}")
        print(f"  Diseases: {user_input['disease']}")
        print(f"  Food Preferences: {user_input['food_preferences']}")
        
        # STEP 2: Calculate nutrition requirements using NutritionService
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
        
        best_solution, top_solutions = run_ga(
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
        
        # STEP 6: Generate meal options dari top solutions
        print("\n" + "="*70)
        print("STEP 6: Generate 3 pilihan menu per slot...")
        print("="*70)
        
        slot_options = generate_meal_options(top_solutions, max_options_per_slot=3)
        display_meal_options(slot_options)
        
        # ============================================================================
        # STEP 7: USER SELECTION - Interactive menu selection
        # ============================================================================
        print("\n" + "="*70)
        print("STEP 7: USER SELECTION - Choose your menu")
        print("="*70)
        
        selected_meal = []
        
        # Mapping slot name ke meal type untuk better display
        meal_display_map = {
            'breakfast_main': ('BREAKFAST', 'MAIN'),
            'breakfast_side': ('BREAKFAST', 'SIDE'),
            'breakfast_drink': ('BREAKFAST', 'DRINK'),
            'lunch_main': ('LUNCH', 'MAIN'),
            'lunch_side': ('LUNCH', 'SIDE'),
            'lunch_drink': ('LUNCH', 'DRINK'),
            'dinner_main': ('DINNER', 'MAIN'),
            'dinner_side': ('DINNER', 'SIDE'),
            'dinner_drink': ('DINNER', 'DRINK'),
            'snack': ('SNACK', 'ITEM')
        }
        
        # Loop setiap slot dan minta user untuk memilih
        for slot_idx, slot_name in enumerate(SLOT_NAMES):
            options = slot_options.get(slot_name, [])
            
            if not options:
                print(f"\n⚠️  {slot_name}: Tidak ada opsi tersedia")
                continue
            
            meal_type, item_type = meal_display_map.get(slot_name, (slot_name, 'Item'))
            
            print(f"\n{'─' * 70}")
            print(f"{meal_type} - {item_type} (Slot {slot_idx})")
            print(f"{'─' * 70}")
            
            # Display 3 options
            for i, option in enumerate(options, 1):
                food_name = option.get('food_name', 'Unknown')
                energy = option.get('energy_kcal', 0)
                protein = option.get('protein_g', 0)
                print(f"{i}. {food_name:30} | Energy: {energy:6.1f} kcal | Protein: {protein:5.1f}g")
            
            # Get user choice
            while True:
                try:
                    choice_str = input(f"\nPilih opsi (1-{len(options)}) [default=1]: ").strip()
                    
                    # Default to 1 jika user tekan Enter
                    if choice_str == "":
                        choice = 0
                    else:
                        choice = int(choice_str) - 1
                    
                    if 0 <= choice < len(options):
                        selected_item = options[choice].copy()
                        selected_meal.append(selected_item)
                        print(f"✓ {options[choice].get('food_name', 'Unknown')} dipilih")
                        break
                    else:
                        print(f"✗ Pilih antara 1-{len(options)}")
                except ValueError:
                    print("✗ Input harus berupa angka")
        
        # Convert selected meals ke DataFrame
        print("\n" + "="*70)
        print("Memproses pilihan user...")
        print("="*70)
        
        if len(selected_meal) == CHROMOSOME_SIZE:
            selected_df = pd.DataFrame(selected_meal).reset_index(drop=True)
            print(f"✓ {len(selected_df)} items dipilih dari {CHROMOSOME_SIZE} slots")
            
            # Calculate total nutrition dari selected meals
            selected_nutrition = calculate_total_nutrition(selected_df)
            
            # STEP 8: Display final nutrition comparison
            print("\n" + "="*70)
            print("STEP 8: FINAL NUTRITION ANALYSIS - Selected Menu Plan")
            print("="*70)
            
            print("\n📊 SELECTED MEAL COMPOSITION:")
            print("─" * 70)
            
            # Display all selected meals
            for idx, meal in enumerate(selected_df.itertuples()):
                print(f"[{idx:2d}] {meal.food_name:30} | {meal.energy_kcal:6.1f} kcal")
            
            print("\n" + "─" * 70)
            print("📈 TOTAL NUTRITION - SELECTED MENU:")
            print("─" * 70)
            
            # Key nutrients for display
            key_nutrients = [
                ('energy_kcal', 'kcal', 'Energy'),
                ('protein_g', 'g', 'Protein'),
                ('carbohydrate_g', 'g', 'Carbohydrates'),
                ('fat_g', 'g', 'Fat'),
                ('fiber_g', 'g', 'Fiber'),
                ('sodium_mg', 'mg', 'Sodium'),
                ('calcium_mg', 'mg', 'Calcium'),
                ('iron_mg', 'mg', 'Iron')
            ]
            
            nutrition_status = []
            
            for nutrient_col, unit, label in key_nutrients:
                if nutrient_col in selected_nutrition:
                    value = selected_nutrition[nutrient_col]
                    constraint = guidelines.get(nutrient_col, {})
                    min_val = constraint.get('min', 0)
                    max_val = constraint.get('max', float('inf'))
                    
                    # Determine status
                    if value < min_val:
                        status = "🔴 LOW"
                        nutrition_status.append('❌')
                    elif value > max_val:
                        status = "🟡 HIGH"
                        nutrition_status.append('⚠️')
                    else:
                        status = "🟢 OK"
                        nutrition_status.append('✅')
                    
                    print(f"\n{label:20} : {value:8.1f} {unit:5} {status}")
                    print(f"  Target           : {min_val:8.1f} - {max_val:8.1f} {unit}")
            
            # Summary status
            print("\n" + "="*70)
            compliance_rate = (nutrition_status.count('✅') / len(nutrition_status)) * 100
            print(f"📋 GUIDELINE COMPLIANCE: {compliance_rate:.0f}% ({nutrition_status.count('✅')}/{len(nutrition_status)} nutrients OK)")
            
            if compliance_rate == 100:
                print("✅ ALL nutrients within guidelines!")
            elif compliance_rate >= 75:
                print("⚠️  Most nutrients are within guidelines")
            else:
                print("❌ Several nutrients outside guidelines - consider adjusting selection")
            
            print("="*70)
        else:
            print(f"✗ Error: Hanya {len(selected_meal)} dari {CHROMOSOME_SIZE} items yang dipilih")
        
        # STEP 9: Display detailed food information
        print("\n" + "="*70)
        print("STEP 9: DETAILED FOOD INFORMATION (Selected Menu - 10 Items)")
        print("="*70)
        
        meals = ['breakfast', 'lunch', 'dinner', 'snack']
        slot_types = {'breakfast': ['main', 'side', 'drink'], 
                      'lunch': ['main', 'side', 'drink'],
                      'dinner': ['main', 'side', 'drink'],
                      'snack': ['item']}
        
        # Use selected_df jika tersedia, otherwise use best_solution
        display_df = selected_df if len(selected_meal) == CHROMOSOME_SIZE else best_solution
        
        for meal in meals:
            # Use MEAL_INDICES from ga_v1 untuk consistency
            indices = MEAL_INDICES[meal]
            
            print(f"\n{meal.upper()}:")
            for i, idx in enumerate(indices):
                if idx < len(display_df):
                    food_row = display_df.iloc[idx]
                    slot_type = slot_types[meal][i] if i < len(slot_types[meal]) else 'item'
                    
                    print(f"\n  {slot_type.upper()}:")
                    
                    # Display available columns
                    important_cols = ['food_name', 'energy_kcal', 'protein_g', 'carbohydrate_g', 
                                    'fat_g', 'fiber_g', 'cuisine']
                    
                    for col in important_cols:
                        if col in food_row.index:
                            value = food_row[col]
                            if isinstance(value, (int, float)):
                                print(f"    {col}: {value:.1f}")
                            else:
                                print(f"    {col}: {value}")
        
        print("\n" + "="*70)
        print("✓ GA COMPLETE - ALL STEPS FINISHED")
        print("="*70 + "\n")
    
    except ValueError as e:
        print(f"\n✗ VALUE ERROR: {e}")
        import traceback
        traceback.print_exc()
    except KeyError as e:
        print(f"\n✗ KEY ERROR: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_ga_with_nutrition_service()

"""
Genetic Algorithm Menu Generator - Input Handler Integration
Aligned dengan input_handler.py specifications
User input → NutritionService → GA Optimization → Formatted Menu
"""

import sys
import os
import pandas as pd

# Add paths
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../C. System Flow')))

from ga_interface import GeneticAlgorithmInterface
from nutrition_service import NutritionService


def get_user_input():
    """
    Standardized input sesuai input_handler.py spec
    Returns dict dengan: gender, age, weight, height, activity_factor, disease, food_preferences
    """
    print("\n" + "="*80)
    print("GENETIC ALGORITHM PERSONAL NUTRITION MENU GENERATOR")
    print("="*80 + "\n")
    
    # === GENDER ===
    print("[STEP 1] Personal Information")
    print("-" * 80)
    
    gender = None
    while gender not in ['M', 'F']:
        gender = input("Gender (M/F): ").upper().strip()
        if gender not in ['M', 'F']:
            print("[ERROR] Input invalid. Choose M or F.")
    
    # === AGE ===
    age = None
    while age is None:
        try:
            age = int(input("Age (years, 18-100): "))
            if not (18 <= age <= 100):
                print("[ERROR] Age must be between 18-100 years.")
                age = None
        except ValueError:
            print("[ERROR] Input must be a number.")
    
    # === WEIGHT ===
    weight = None
    while weight is None:
        try:
            weight = float(input("Weight (kg): "))
            if weight <= 0:
                print("[ERROR] Weight must be positive.")
                weight = None
        except ValueError:
            print("[ERROR] Input must be a number.")
    
    # === HEIGHT ===
    height = None
    while height is None:
        try:
            height = float(input("Height (cm, 100-300): "))
            if not (100 <= height <= 300):
                print("[ERROR] Height must be between 100-300 cm.")
                height = None
        except ValueError:
            print("[ERROR] Input must be a number.")
    
    # === ACTIVITY FACTOR ===
    print("\n[STEP 2] Activity Level")
    print("-" * 80)
    print("1. Sedentary/Light Activity (Office worker, rarely exercise) [PAL: 1.545]")
    print("2. Active/Moderately Active (Construction, teacher, regular jogging) [PAL: 1.845]")
    print("3. Vigorous/Vigorously Active (Athlete, porter, intense sports) [PAL: 2.2]")
    
    activity_map = {
        '1': 1.545,
        '2': 1.845,
        '3': 2.2
    }
    
    activity_choice = None
    while activity_choice not in activity_map:
        activity_choice = input("Choose (1-3): ").strip()
        if activity_choice not in activity_map:
            print("[ERROR] Invalid choice. Enter 1, 2, or 3.")
    
    activity_factor = activity_map[activity_choice]
    print(f"[OK] Selected: {activity_choice} (PAL: {activity_factor})")
    
    # === HEALTH CONDITIONS (Multi-select with validation) ===
    print("\n[STEP 3] Health Conditions")
    print("-" * 80)
    print("1. Normal")
    print("2. Diabetes Type 2 (DM2)")
    print("3. Hypertension")
    print("4. Cardiovascular Disease (CVD)")
    print("5. High Cholesterol")
    print("6. Chronic Kidney Disease (CKD)")
    print("\nYou can select multiple (e.g., '2,3' for DM2+Hypertension)")
    print("If selecting 'Normal' (1), cannot combine with other conditions")
    
    disease_map = {
        '1': 'normal',
        '2': 'dm2',
        '3': 'hypertension',
        '4': 'cvd',
        '5': 'cholesterol',
        '6': 'ckd'
    }
    
    disease = None
    while disease is None:
        choice_input = input("Select conditions (e.g., '2,3' or '1'): ").strip()
        
        # Parse input
        choice_list = [c.strip() for c in choice_input.split(',') if c.strip()]
        
        if not choice_list:
            print("[ERROR] Cannot be empty.")
            continue
        
        # Validate all choices exist
        if not all(c in disease_map for c in choice_list):
            print("[ERROR] Invalid input. Enter 1-6 only.")
            continue
        
        # Get labels
        selected_labels = [disease_map[c] for c in choice_list]
        
        # Check for "Normal" conflict
        if 'normal' in selected_labels:
            if len(selected_labels) > 1:
                print("[WARN] 'Normal' cannot be combined with other conditions. Please re-select.")
                continue
            disease = 'normal'
        # Check max 3 diseases
        elif len(selected_labels) > 3:
            print("[WARN] Maximum 3 conditions allowed.")
            continue
        else:
            disease = selected_labels
        
        print(f"[OK] Selected: {disease}")
        break
    
    # === FOOD PREFERENCES (Multi-select) ===
    print("\n[STEP 4] Food Preferences (Optional)")
    print("-" * 80)
    print("1. Asian")
    print("2. Western")
    print("3. Mediterranean")
    print("\nLeave blank to include all cuisines, or select multiple (e.g., '1,2')")
    
    cuisine_map = {
        '1': 'Asian',
        '2': 'Western',
        '3': 'Mediterranean'
    }
    
    food_preferences = None
    while food_preferences is None:
        cuisine_input = input("Select preferences (leave blank for all): ").strip()
        
        if not cuisine_input:
            food_preferences = []
            print("[OK] All cuisines included")
            break
        
        # Parse input
        choice_list = [c.strip() for c in cuisine_input.split(',') if c.strip()]
        
        # Validate
        if all(c in cuisine_map for c in choice_list):
            food_preferences = [cuisine_map[c] for c in choice_list]
            print(f"[OK] Selected: {', '.join(food_preferences)}")
            break
        else:
            print("[ERROR] Invalid input. Enter 1-3 only.")
    
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


def display_nutrition_summary(nutrition_result, user_input):
    """
    Display nutrition calculation summary (Phase 1)
    Before GA optimization
    """
    print("\n" + "="*80)
    print("NUTRITION PROFILE SUMMARY")
    print("="*80 + "\n")
    
    if not nutrition_result['success']:
        print(f"[ERROR] {nutrition_result['error']}")
        return False
    
    anthro = nutrition_result['anthropometrics']
    energy = nutrition_result['energy']
    guidelines = nutrition_result['guidelines']
    
    # === BMI INFO ===
    print("[ANTHROPOMETRIC MEASUREMENTS]")
    print("-" * 80)
    print(f"Body Mass Index (BMI): {anthro['bmi']:.1f} kg/m²")
    
    bmi_category = anthro['bmi_category']
    if bmi_category == 'underweight':
        print("  Classification: Underweight (<18.5)")
    elif bmi_category == 'normal':
        print("  Classification: Normal weight (18.5–24.9)")
    elif bmi_category == 'overweight':
        print("  Classification: Overweight (25–29.9)")
    elif bmi_category == 'obesity_class_1':
        print("  Classification: Obesity Class I (30–34.9)")
    elif bmi_category == 'obesity_class_2':
        print("  Classification: Obesity Class II (35–39.9)")
    else:
        print("  Classification: Obesity Class III (≥40)")
    
    print(f"Ideal Body Weight (IBW): {anthro['bbi']:.1f} kg")
    
    # === ENERGY REQUIREMENTS ===
    print("\n[ENERGY REQUIREMENTS]")
    print("-" * 80)
    print(f"Basal Metabolic Rate (BMR): {energy['bmr']:.0f} kcal/day")
    print(f"Total Daily Energy Expenditure (TDEE): {energy['tdee']:.0f} kcal/day")
    print(f"  (Based on activity level: {user_input['activity_factor']:.3f} PAL)")
    
    # === DEMOGRAPHIC & HEALTH ===
    print("\n[DEMOGRAPHIC & HEALTH PROFILE]")
    print("-" * 80)
    print(f"Age Group: {anthro['age_range']}")
    
    disease_display = user_input['disease']
    if isinstance(disease_display, list):
        disease_display = ', '.join([d.upper() for d in disease_display])
    else:
        disease_display = disease_display.upper()
    
    print(f"Health Condition(s): {disease_display}")
    
    if user_input['food_preferences']:
        print(f"Cuisine Preference(s): {', '.join(user_input['food_preferences'])}")
    else:
        print(f"Cuisine Preference(s): All cuisines included")
    
    # === NUTRITION GUIDELINES ===
    print("\n[NUTRITION GUIDELINES]")
    print("-" * 80)
    print(f"Total Nutrients Evaluated: {guidelines['total_nutrients']}")
    print("  Includes macronutrients and micronutrients based on health conditions")
    
    print("\n" + "="*80 + "\n")
    return True


def display_ga_results(menu_plan, user_tdee):
    """
    Display GA optimization results (Phase 2)
    Shows menu with alternatives
    """
    print("\n" + "="*80)
    print("PERSONALIZED MENU RECOMMENDATIONS - GENETIC ALGORITHM")
    print("="*80 + "\n")
    
    if menu_plan is None:
        print("[ERROR] Failed to generate menu plan")
        return
    
    try:
        # === MEAL PLANS ===
        print("[MEAL COMPOSITION]")
        print("-" * 80)
        
        def display_meal(meal_obj, meal_name):
            if not meal_obj:
                return
            
            print(f"\n{meal_name.upper()}")
            print(f"Total Energy: {meal_obj.total_energy:.0f} kcal")
            print(f"Macros: Protein {meal_obj.total_protein:.1f}g | Carbs {meal_obj.total_carbs:.1f}g | Fat {meal_obj.total_fat:.1f}g")
            
            if not meal_obj.slots:
                return
            
            # Organize by category
            mains = []
            sides = []
            drinks = []
            
            for slot_type, slot in meal_obj.slots.items():
                if 'side' in slot_type:
                    sides.append(slot.primary)
                elif 'drink' in slot_type:
                    drinks.append(slot.primary)
                else:
                    mains.append(slot.primary)
            
            # Display main courses
            if mains:
                print("\n  MAIN COURSE OPTIONS:")
                for i, food in enumerate(mains, 1):
                    print(f"    [{i}] {food.name} ({food.portion_gram:.0f}g, {food.energy_kcal:.0f} kcal)")
            
            # Display sides
            if sides:
                print("\n  SIDE DISH OPTIONS:")
                for i, food in enumerate(sides, 1):
                    print(f"    [{i}] {food.name} ({food.portion_gram:.0f}g, {food.energy_kcal:.0f} kcal)")
            
            # Display drinks
            if drinks:
                print("\n  DRINK OPTIONS (Optional):")
                for i, food in enumerate(drinks, 1):
                    print(f"    [{i}] {food.name} ({food.portion_gram:.0f}g, {food.energy_kcal:.0f} kcal)")
        
        # Display each meal
        display_meal(menu_plan.breakfast, 'breakfast')
        display_meal(menu_plan.lunch, 'lunch')
        display_meal(menu_plan.dinner, 'dinner')
        
        # === EVALUATION ===
        print("\n\n[EVALUATION METRICS]")
        print("-" * 80)
        
        total_energy = menu_plan.total_energy_kcal
        energy_diff = total_energy - user_tdee
        energy_diff_pct = (energy_diff / user_tdee * 100) if user_tdee > 0 else 0
        
        print(f"\nDaily Energy Balance:")
        print(f"  Recommended TDEE: {user_tdee:.0f} kcal")
        print(f"  Menu Total:       {total_energy:.0f} kcal")
        print(f"  Difference:       {energy_diff:+.0f} kcal ({energy_diff_pct:+.1f}%)")
        
        print(f"\nGenetic Algorithm Fitness Score: {menu_plan.ga_fitness_score:.2f} / 100")
        
        if menu_plan.ga_fitness_score > 75:
            quality = "EXCELLENT"
        elif menu_plan.ga_fitness_score > 60:
            quality = "GOOD"
        elif menu_plan.ga_fitness_score > 45:
            quality = "FAIR"
        else:
            quality = "NEEDS IMPROVEMENT"
        
        print(f"Quality Rating: {quality}")
        
        # === NOTES ===
        print("\n\n[IMPORTANT NOTES]")
        print("-" * 80)
        print("""
[OK] EVALUATED:
  • Menu composition from food database
  • Nutritional compliance to 31 guidelines
  • Energy coverage vs TDEE target
  • Macronutrient balance

[FUTURE] NOT YET IMPLEMENTED:
  • Cost analysis & budget feasibility
  • Preparation time & difficulty
  • Detailed micronutrient analysis

[DISCLAIMER]
  • This is a RECOMMENDATION from optimization algorithm
  • NOT a medical prescription or diagnosis
  • Consult a nutritionist for medical needs
  • Use as guidance for meal planning
        """)
        
        print("\n" + "="*80 + "\n")
        
    except Exception as e:
        print(f"[WARN] Display error: {e}")
        print("Menu generated but display encountered an issue.")


def main():
    """Main flow with 2-phase display"""
    
    try:
        # === PHASE 1: INPUT & NUTRITION ===
        user_input = get_user_input()
        
        print("\n[STEP 5] Calculating Nutrition Requirements...")
        print("-" * 80)
        service = NutritionService()
        nutrition_result = service.calculate_nutrition_needs(user_input)
        
        if not nutrition_result['success']:
            print(f"[ERROR] {nutrition_result['error']}")
            return
        
        print("[OK] Nutrition profile calculated")
        
        # Display nutrition summary (Phase 1)
        if not display_nutrition_summary(nutrition_result, user_input):
            return
        
        # === PHASE 2: GA OPTIMIZATION ===
        print("[STEP 6] Running Genetic Algorithm Optimization...")
        print("-" * 80)
        
        food_df = nutrition_result['food_data']['dataframe']
        print(f"[OK] Using {len(food_df)} food items")
        
        ga = GeneticAlgorithmInterface()
        ga_init = ga.initialize(
            food_database=food_df,
            nutrition_guidelines=nutrition_result['guidelines'],
            verbose=False
        )
        
        if not ga_init:
            print("[ERROR] Failed to initialize GA")
            return
        
        meal_distribution = nutrition_result['meal_plan']['distribution']
        
        menu_plan = ga.generate_menu_plan(
            user_tdee=nutrition_result['energy']['tdee'],
            meal_distribution=meal_distribution,
            cuisine_preferences=user_input['food_preferences'] if user_input['food_preferences'] else None,
            max_generations=100,
            population_size=50,
            verbose=True
        )
        
        # Display GA results (Phase 2)
        display_ga_results(menu_plan, nutrition_result['energy']['tdee'])
        
    except KeyboardInterrupt:
        print("\n\n[WARN] Process interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] An error occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

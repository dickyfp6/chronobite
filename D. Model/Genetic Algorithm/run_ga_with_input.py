"""
Genetic Algorithm Menu Generator - Standalone Entry Point
User input → NutritionService → GA Optimization → Personalized Menu
"""

import sys
import os
import pandas as pd

# Add paths
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../C. System Flow')))

from ga_interface import GeneticAlgorithmInterface
from nutrition_service import NutritionService


def get_simple_input():
    """Simple user input (alternative to input_handler)"""
    print("\n" + "="*80)
    print("GENETIC ALGORITHM PERSONAL NUTRITION MENU GENERATOR")
    print("="*80 + "\n")
    
    print("[STEP 1] Enter Your Profile")
    print("-" * 40)
    
    gender = input("Gender (M/F): ").upper()
    while gender not in ['M', 'F']:
        gender = input("Invalid! Enter M or F: ").upper()
    
    age = int(input("Age (years): "))
    weight = float(input("Weight (kg): "))
    height = float(input("Height (cm): "))
    
    print("\nActivity Level:")
    print("  1 = Sedentary (little or no exercise)")
    print("  2 = Lightly active (exercise 1-3 days/week)")
    print("  3 = Moderately active (exercise 3-5 days/week)")
    print("  4 = Very active (exercise 6-7 days/week)")
    activity_choice = input("Choose (1-4): ")
    
    activity_map = {
        '1': 1.2,
        '2': 1.375,
        '3': 1.55,
        '4': 1.725
    }
    activity_factor = activity_map.get(activity_choice, 1.55)
    
    print("\nHealth Conditions:")
    print("  0 = Normal")
    print("  1 = Diabetes Type 2 (dm2)")
    print("  2 = Hypertension")
    print("  3 = Both dm2 and hypertension")
    disease_choice = input("Choose (0-3): ")
    
    disease_map = {
        '0': [],
        '1': ['dm2'],
        '2': ['hypertension'],
        '3': ['dm2', 'hypertension']
    }
    diseases = disease_map.get(disease_choice, [])
    
    print("\nFood Preferences (optional):")
    print("  Available: Asian, Mediterranean, Western, Generic")
    print("  (leave blank for no preference, separate with comma)")
    prefs_input = input("Preferences: ").strip()
    
    food_preferences = []
    if prefs_input:
        food_preferences = [p.strip() for p in prefs_input.split(',')]
    
    user_input = {
        'gender': gender,
        'age': age,
        'weight': weight,
        'height': height,
        'activity_factor': activity_factor,
        'disease': diseases,
        'food_preferences': food_preferences
    }
    
    return user_input


def display_results(menu_plan, user_tdee):
    """Display menu plan results"""
    print("\n" + "="*80)
    print("YOUR PERSONALIZED MENU PLAN")
    print("="*80 + "\n")
    
    if menu_plan is None:
        print("[ERROR] Failed to generate menu plan")
        return
    
    print(f"Algorithm: {menu_plan.algorithm}")
    print(f"Fitness Score: {menu_plan.ga_fitness_score:.2f} / 100")
    print(f"Total Energy: {menu_plan.total_energy_kcal:.0f} kcal (Target: {user_tdee:.0f})")
    
    # Breakfast
    if menu_plan.breakfast:
        print(f"\n[BREAKFAST]")
        print(f"  Total Energy: {menu_plan.breakfast.total_energy:.0f} kcal")
        print(f"  Protein: {menu_plan.breakfast.total_protein:.1f}g | Carbs: {menu_plan.breakfast.total_carbs:.1f}g | Fat: {menu_plan.breakfast.total_fat:.1f}g")
        if menu_plan.breakfast.slots:
            for slot_type, slot in menu_plan.breakfast.slots.items():
                print(f"    [{slot_type.upper()}] {slot.primary.name} ({slot.primary.energy_kcal:.0f} kcal, {slot.primary.portion_gram:.0f}g)")
    
    # Lunch
    if menu_plan.lunch:
        print(f"\n[LUNCH]")
        print(f"  Total Energy: {menu_plan.lunch.total_energy:.0f} kcal")
        print(f"  Protein: {menu_plan.lunch.total_protein:.1f}g | Carbs: {menu_plan.lunch.total_carbs:.1f}g | Fat: {menu_plan.lunch.total_fat:.1f}g")
        if menu_plan.lunch.slots:
            for slot_type, slot in menu_plan.lunch.slots.items():
                print(f"    [{slot_type.upper()}] {slot.primary.name} ({slot.primary.energy_kcal:.0f} kcal, {slot.primary.portion_gram:.0f}g)")
    
    # Dinner
    if menu_plan.dinner:
        print(f"\n[DINNER]")
        print(f"  Total Energy: {menu_plan.dinner.total_energy:.0f} kcal")
        print(f"  Protein: {menu_plan.dinner.total_protein:.1f}g | Carbs: {menu_plan.dinner.total_carbs:.1f}g | Fat: {menu_plan.dinner.total_fat:.1f}g")
        if menu_plan.dinner.slots:
            for slot_type, slot in menu_plan.dinner.slots.items():
                print(f"    [{slot_type.upper()}] {slot.primary.name} ({slot.primary.energy_kcal:.0f} kcal, {slot.primary.portion_gram:.0f}g)")
    
    # Snack
    if menu_plan.snack:
        print(f"\n[SNACK]")
        print(f"  {menu_plan.snack.get('food_name', 'N/A')} ({menu_plan.snack.get('energy_kcal', 0):.0f} kcal)")
    
    print("\n" + "="*80)
    print("[OK] Menu generated successfully!")
    print("="*80 + "\n")


def main():
    """Main flow: Input → Nutrition → GA → Output"""
    
    try:
        # Step 1: Get user input
        user_input = get_simple_input()
        
        # Step 2: Calculate nutrition needs using NutritionService
        print("\n[STEP 2] Calculating Nutrition Requirements...")
        print("-" * 40)
        service = NutritionService()
        nutrition_result = service.calculate_nutrition_needs(user_input)
        
        if not nutrition_result['success']:
            print(f"[ERROR] Nutrition calculation failed: {nutrition_result['error']}")
            return
        
        print("[OK] Nutrition requirements calculated")
        print(f"  TDEE: {nutrition_result['energy']['TDEE']:.0f} kcal/day")
        print(f"  Health Conditions: {user_input['disease'] if user_input['disease'] else 'None'}")
        print(f"  Total Nutrients Tracked: {nutrition_result['guidelines']['total_nutrients']}")
        
        # Step 3: Load food database
        print("\n[STEP 3] Loading Food Database...")
        print("-" * 40)
        food_path = os.path.join(
            os.path.dirname(__file__),
            '../../A. Data/Data Processed/05_final_dataset.csv'
        )
        food_df = pd.read_csv(food_path)
        print(f"[OK] Loaded {len(food_df)} food items")
        
        # Filter by cuisine if preferences specified
        if user_input['food_preferences']:
            original_count = len(food_df)
            food_df = food_df[food_df['cuisine'].isin(user_input['food_preferences'])]
            print(f"  Filtered to {len(food_df)} items matching preferences: {', '.join(user_input['food_preferences'])}")
        
        # Step 4: Initialize and run GA
        print("\n[STEP 4] Running Genetic Algorithm Optimization...")
        print("-" * 40)
        
        ga = GeneticAlgorithmInterface()
        ga_init = ga.initialize(
            food_database=food_df,
            nutrition_guidelines=nutrition_result['guidelines'],
            verbose=True
        )
        
        if not ga_init:
            print("[ERROR] Failed to initialize GA")
            return
        
        # Generate menu plan
        menu_plan = ga.generate_menu_plan(
            user_tdee=nutrition_result['energy']['TDEE'],
            meal_distribution=nutrition_result['meal_plan'],
            cuisine_preferences=user_input['food_preferences'] if user_input['food_preferences'] else None,
            max_generations=100,
            population_size=50,
            verbose=True
        )
        
        # Step 5: Display results
        display_results(menu_plan, nutrition_result['energy']['TDEE'])
        
    except KeyboardInterrupt:
        print("\n[WARN] Process interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] An error occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

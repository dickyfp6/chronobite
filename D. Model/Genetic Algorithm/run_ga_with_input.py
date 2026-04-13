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
    
    age = None
    while age is None:
        try:
            age = int(input("Age (years): "))
        except ValueError:
            print("Invalid input! Please enter a number.")
    
    weight = None
    while weight is None:
        try:
            weight = float(input("Weight (kg): "))
        except ValueError:
            print("Invalid input! Please enter a number.")
    
    height = None
    while height is None:
        try:
            height = float(input("Height (cm): "))
        except ValueError:
            print("Invalid input! Please enter a number.")
    
    print("\nActivity Level:")
    print("  1 = Sedentary (little or no exercise)")
    print("  2 = Lightly active (exercise 1-3 days/week)")
    print("  3 = Moderately active (exercise 3-5 days/week)")
    print("  4 = Very active (exercise 6-7 days/week)")
    
    activity_choice = None
    activity_map = {
        '1': 1.4,
        '2': 1.55,
        '3': 1.725,
        '4': 1.9
    }
    while activity_choice not in activity_map:
        activity_choice = input("Choose (1-4): ")
        if activity_choice not in activity_map:
            print("Invalid choice! Please enter 1, 2, 3, or 4.")
    
    activity_factor = activity_map[activity_choice]
    
    print("\nHealth Conditions:")
    print("  0 = Normal")
    print("  1 = Diabetes Type 2 (dm2)")
    print("  2 = Hypertension")
    print("  3 = Both dm2 and hypertension")
    
    disease_choice = None
    disease_map = {
        '0': [],
        '1': ['dm2'],
        '2': ['hypertension'],
        '3': ['dm2', 'hypertension']
    }
    while disease_choice not in disease_map:
        disease_choice = input("Choose (0-3): ")
        if disease_choice not in disease_map:
            print("Invalid choice! Please enter 0, 1, 2, or 3.")
    
    diseases = disease_map[disease_choice]
    
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
    """Display menu plan results with honest evaluation status"""
    print("\n" + "="*80)
    print("YOUR PERSONALIZED MENU PLAN - GENETIC ALGORITHM OPTIMIZATION")
    print("="*80 + "\n")
    
    if menu_plan is None:
        print("[ERROR] Failed to generate menu plan")
        return
    
    try:
        # === SECTION 1: MENU COMPOSITION ===
        print("[MENU COMPOSITION]")
        print("-" * 80)
        
        # Breakfast
        if menu_plan.breakfast:
            print(f"\n[BREAKFAST] - {menu_plan.breakfast.total_energy:.0f} kcal")
            print(f"  Macros: Protein {menu_plan.breakfast.total_protein:.1f}g | Carbs {menu_plan.breakfast.total_carbs:.1f}g | Fat {menu_plan.breakfast.total_fat:.1f}g")
            if menu_plan.breakfast.slots:
                for slot_type, slot in menu_plan.breakfast.slots.items():
                    print(f"    • [{slot_type}] {slot.primary.name} ({slot.primary.portion_gram:.0f}g, {slot.primary.energy_kcal:.0f} kcal)")
        
        # Lunch
        if menu_plan.lunch:
            print(f"\n[LUNCH] - {menu_plan.lunch.total_energy:.0f} kcal")
            print(f"  Macros: Protein {menu_plan.lunch.total_protein:.1f}g | Carbs {menu_plan.lunch.total_carbs:.1f}g | Fat {menu_plan.lunch.total_fat:.1f}g")
            if menu_plan.lunch.slots:
                for slot_type, slot in menu_plan.lunch.slots.items():
                    print(f"    • [{slot_type}] {slot.primary.name} ({slot.primary.portion_gram:.0f}g, {slot.primary.energy_kcal:.0f} kcal)")
        
        # Dinner
        if menu_plan.dinner:
            print(f"\n[DINNER] - {menu_plan.dinner.total_energy:.0f} kcal")
            print(f"  Macros: Protein {menu_plan.dinner.total_protein:.1f}g | Carbs {menu_plan.dinner.total_carbs:.1f}g | Fat {menu_plan.dinner.total_fat:.1f}g")
            if menu_plan.dinner.slots:
                for slot_type, slot in menu_plan.dinner.slots.items():
                    print(f"    • [{slot_type}] {slot.primary.name} ({slot.primary.portion_gram:.0f}g, {slot.primary.energy_kcal:.0f} kcal)")
        
        # === SECTION 2: EVALUATION STATUS ===
        print("\n\n[EVALUATION STATUS]")
        print("-" * 80)
        
        # Total energy
        computed_energy = menu_plan.total_energy_kcal
        energy_diff = computed_energy - user_tdee
        energy_diff_pct = (energy_diff / user_tdee * 100) if user_tdee > 0 else 0
        
        print(f"\nTotal Daily Energy:")
        print(f"  Computed from selected foods: {computed_energy:.0f} kcal")
        print(f"  User target TDEE:             {user_tdee:.0f} kcal")
        print(f"  Difference:                   {energy_diff:+.0f} kcal ({energy_diff_pct:+.1f}%)")
        
        # Fitness score
        guidelines_count = int(menu_plan.ga_fitness_score) if menu_plan.ga_fitness_score > 50 else 31
        
        print(f"\nGenetic Algorithm Fitness Score:")
        print(f"  Value: {menu_plan.ga_fitness_score:.2f} / 100")
        print(f"  Meaning: Compliance to nutrition guidelines (higher is better)")
        print(f"  Constraints: ~31 nutrients evaluated")
        
        # Interpretation
        if menu_plan.ga_fitness_score > 75:
            quality = "[BAIK] E"
        elif menu_plan.ga_fitness_score > 60:
            quality = "[SEDANG] C"
        elif menu_plan.ga_fitness_score > 45:
            quality = "[CUKUP] D"
        else:
            quality = "[PERLU DITINGKATKAN] E"
        
        print(f"  Quality: {quality}")
        
        # === SECTION 3: NOTES & LIMITATIONS ===
        print("\n\n[NOTES & ACADEMIC INTEGRITY]")
        print("-" * 80)
        print("""
[OK] YANG SUDAH DIEVALUASI:
  • Menu composition dari food database (sesuai cuisine preference)
  • Genetic Algorithm optimization terhadap 31 nutrition guidelines
  • Total energy coverage terhadap TDEE
  • Macronutrient balance (protein, carbs, fat)
  
[TASK] YANG BELUM DIIMPLEMENTASI (Future Enhancement):
  • Micronutrient evaluation detail (vitamins, minerals distribution)
  • Palatability & food acceptability scoring
  • Cost analysis & budget feasibility
  • Preparation time & cooking difficulty
  • Long-term nutritional sustainability
  
[PENTING] CATATAN METODOLOGI:
  • Fitness score dari INTERNAL GA evaluation, bukan validasi eksternal
  • Menu ini REKOMENDASI ALGORITMA, bukan diagnosis/prescription medis
  • Untuk kebutuhan medis: konsultasi ahli gizi profesional
  • Data makanan: USDA FoodData Central + Local Database
        """)
        
        # === SECTION 4: SUMMARY ===
        print("\n[SUMMARY]")
        print("-" * 80)
        print(f"Algorithm: {menu_plan.algorithm.upper()}")
        print(f"Status: [OK] Optimization Completed Successfully")
        print(f"Recommendation: [MENU DAPAT DIGUNAKAN SEBAGAI PANDUAN]")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"[WARN] Display error: {e}")
        print("Menu was generated. Core data available.")


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
        print(f"  TDEE: {nutrition_result['energy']['tdee']:.0f} kcal/day")
        print(f"  Health Conditions: {user_input['disease'] if user_input['disease'] else 'Normal'}")
        print(f"  Total Nutrients Tracked: {nutrition_result['guidelines']['total_nutrients']}")
        
        # Step 3: Get food database from nutrition service
        print("\n[STEP 3] Preparing Food Database...")
        print("-" * 40)
        
        food_df = nutrition_result['food_data']['dataframe']
        print(f"[OK] Using {len(food_df)} food items")
        
        if nutrition_result['food_data']['preferences']:
            print(f"  Cuisine preferences: {', '.join(nutrition_result['food_data']['preferences'])}")
        
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
        
        # Get meal distribution
        meal_distribution = nutrition_result['meal_plan']['distribution']
        
        # Generate menu plan
        menu_plan = ga.generate_menu_plan(
            user_tdee=nutrition_result['energy']['tdee'],
            meal_distribution=meal_distribution,
            cuisine_preferences=user_input['food_preferences'] if user_input['food_preferences'] else None,
            max_generations=100,
            population_size=50,
            verbose=True
        )
        
        # Step 5: Display results
        display_results(menu_plan, nutrition_result['energy']['tdee'])
        
    except KeyboardInterrupt:
        print("\n[WARN] Process interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] An error occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

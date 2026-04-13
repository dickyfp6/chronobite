"""
Example Usage: Genetic Algorithm Integration with NutritionService
Menunjukkan cara integrate GA dengan nutrition_service untuk generate menu recommendations
"""

import sys
import os

# Add paths
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../C. System Flow')))

from nutrition_service import NutritionService
from ga_interface import GeneticAlgorithmInterface


def example_complete_flow():
    """
    Complete flow: User input -> NutritionService -> GA Optimization -> Menu Output
    """
    
    print("\n" + "="*80)
    print("GENETIC ALGORITHM MEAL PLANNING SYSTEM - COMPLETE EXAMPLE")
    print("="*80 + "\n")
    
    # ===== STEP 1: Get user input =====
    print("STEP 1: Simulating user input...")
    user_input = {
        'gender': 'M',
        'age': 32,
        'weight': 75,          # kg
        'height': 175,         # cm
        'activity_factor': 1.55,  # Sedentary (office worker)
        'disease': ['dm2', 'hypertension'],  # Multiple diseases
        'food_preferences': ['Asian', 'Mediterranean']
    }
    
    print(f"  Gender: {user_input['gender']}")
    print(f"  Age: {user_input['age']} years")
    print(f"  Weight: {user_input['weight']} kg, Height: {user_input['height']} cm")
    print(f"  Activity: {user_input['activity_factor']} (Sedentary)")
    print(f"  Health Conditions: {', '.join(user_input['disease'])}")
    print(f"  Cuisine Preferences: {', '.join(user_input['food_preferences'])}")
    
    # ===== STEP 2: Use NutritionService =====
    print("\n\nSTEP 2: Calculating nutrition needs...")
    
    service = NutritionService()
    nutrition_result = service.calculate_nutrition_needs(user_input)
    
    if not nutrition_result['success']:
        print(f"[ERROR] Nutrition calculation failed: {nutrition_result['error']}")
        return
    
    print("[OK] Nutrition calculation completed")
    
    # Display key info
    anthropometrics = nutrition_result['anthropometrics']
    energy = nutrition_result['energy']
    
    print(f"\n  User Profile:")
    print(f"    BMI: {anthropometrics['bmi']} ({anthropometrics['bmi_category']})")
    print(f"    IBW: {anthropometrics['bbi']:.1f} kg")
    print(f"    Age Group: {anthropometrics['age_label']}")
    print(f"    BMR: {energy['bmr']:.0f} kcal (basal metabolic rate)")
    print(f"    TDEE: {energy['tdee']:.0f} kcal (daily energy expenditure)")
    
    print(f"\n  Nutrition Guidelines:")
    guidelines = nutrition_result['guidelines']
    print(f"    Health Conditions: {guidelines['disease']}")
    print(f"    Total Nutrients: {guidelines['total_nutrients']}")
    
    print(f"\n  Food Database:")
    food_data = nutrition_result['food_data']
    print(f"    Total Items: {food_data['total_items']}")
    if food_data['by_cuisine']:
        for cuisine, count in food_data['by_cuisine'].items():
            print(f"    - {cuisine}: {count} items")
    
    # ===== STEP 3: Use Genetic Algorithm =====
    print("\n\nSTEP 3: Running Genetic Algorithm Optimization...")
    
    # Initialize GA interface
    ga_interface = GeneticAlgorithmInterface()
    
    # Initialize dengan data dari NutritionService
    init_success = ga_interface.initialize(
        food_database=nutrition_result['food_data']['dataframe'],
        nutrition_guidelines=nutrition_result['guidelines'],
        verbose=True
    )
    
    if not init_success:
        print("[ERROR] GA initialization failed")
        return
    
    # Get meal distribution dari NutritionService
    meal_distribution = nutrition_result['meal_plan']
    
    # Generate menu plan menggunakan GA
    menu_plan = ga_interface.generate_menu_plan(
        user_tdee=energy['tdee'],
        meal_distribution=meal_distribution,
        cuisine_preferences=user_input['food_preferences'],
        max_generations=100,
        population_size=50,
        verbose=True
    )
    
    if menu_plan is None:
        print("[ERROR] Menu generation failed")
        return
    
    # ===== STEP 4: Display Results =====
    print("\n\nSTEP 4: Generated Menu Plan")
    print("="*80)
    
    print(f"\nAlgorithm: {menu_plan.algorithm}")
    print(f"GA Fitness Score: {menu_plan.ga_fitness_score:.2f} / 100")
    print(f"Total Energy: {menu_plan.total_energy_kcal:.0f} kcal (Target: {energy['tdee']:.0f})")
    
    # Display per meal
    meals = [
        ('BREAKFAST', menu_plan.breakfast),
        ('LUNCH', menu_plan.lunch),
        ('DINNER', menu_plan.dinner)
    ]
    
    for meal_name, meal in meals:
        if meal is None:
            continue
        print(f"\n{meal_name}:")
        print(f"  Total Calories: {meal.total_energy:.0f} kcal")
        print(f"  Protein: {meal.total_protein:.1f}g | Carbs: {meal.total_carbs:.1f}g | Fat: {meal.total_fat:.1f}g")
        
        for slot_type, slot in meal.slots.items():
            print(f"    - {slot.primary.name} ({slot.primary.energy_kcal:.0f} kcal)")
    
    # Snack
    if menu_plan.snack:
        print(f"\nSNACK:")
        print(f"  {menu_plan.snack['food_name']} ({menu_plan.snack['energy_kcal']:.0f} kcal)")
    
    # ===== STEP 5: Convergence Statistics =====
    print("\n\nSTEP 5: GA Convergence Statistics")
    print("="*80)
    
    stats = ga_interface.convergence_stats
    if stats:
        print(f"Generations Run: {stats['generations_run']}")
        print(f"Best Fitness: {stats['best_fitness']:.2f}")
        print(f"Initial Fitness: {stats['best_fitness_history'][0]:.2f}")
        print(f"Total Improvement: {stats['improvement']:.2f} points")
        
        improvement_percent = (
            (stats['best_fitness_history'][-1] - stats['best_fitness_history'][0]) /
            stats['best_fitness_history'][0] * 100
        ) if stats['best_fitness_history'][0] > 0 else 0
        
        print(f"Improvement Rate: {improvement_percent:.1f}%")
    
    print("\n" + "="*80)
    print("[OK] COMPLETE FLOW SUCCESSFUL")
    print("="*80 + "\n")


def example_ga_only():
    """
    Example: Standalone GA with minimal setup
    Shows how to use GA optimizer directly with DataFrame
    """
    
    print("\n" + "="*80)
    print("GA STANDALONE EXAMPLE (WITH NEW DICT-CHROMOSOME DESIGN)")
    print("="*80 + "\n")
    
    import pandas as pd
    from ga_optimizer import GeneticAlgorithmOptimizer
    from ga_chromosome import ChromosomeOperations
    
    # Create sample food database (DataFrame format - REQUIRED for new design)
    foods_data = [
        # Breakfast main options
        {'fdc_id': 'F1', 'food_name': 'Nasi Kuning', 'energy_kcal': 150, 'protein_g': 2.5, 'carbohydrate_g': 30, 'fat_g': 1.5},
        {'fdc_id': 'F2', 'food_name': 'Roti Bakar', 'energy_kcal': 140, 'protein_g': 4, 'carbohydrate_g': 25, 'fat_g': 1},
        {'fdc_id': 'F3', 'food_name': 'Nasi Goreng', 'energy_kcal': 180, 'protein_g': 6, 'carbohydrate_g': 30, 'fat_g': 3},
        
        # Sides
        {'fdc_id': 'S1', 'food_name': 'Telur Rebus', 'energy_kcal': 155, 'protein_g': 13, 'carbohydrate_g': 1, 'fat_g': 11},
        {'fdc_id': 'S2', 'food_name': 'Tempe Goreng', 'energy_kcal': 190, 'protein_g': 19, 'carbohydrate_g': 5, 'fat_g': 11},
        {'fdc_id': 'S3', 'food_name': 'Tahu Goreng', 'energy_kcal': 180, 'protein_g': 18, 'carbohydrate_g': 2, 'fat_g': 11},
        
        # Drinks
        {'fdc_id': 'D1', 'food_name': 'Air Putih', 'energy_kcal': 0, 'protein_g': 0, 'carbohydrate_g': 0, 'fat_g': 0},
        {'fdc_id': 'D2', 'food_name': 'Teh Tawar', 'energy_kcal': 2, 'protein_g': 0, 'carbohydrate_g': 1, 'fat_g': 0},
        
        # Snacks
        {'fdc_id': 'SNK1', 'food_name': 'Pisang', 'energy_kcal': 89, 'protein_g': 1, 'carbohydrate_g': 23, 'fat_g': 0},
        {'fdc_id': 'SNK2', 'food_name': 'Apel', 'energy_kcal': 52, 'protein_g': 0.3, 'carbohydrate_g': 14, 'fat_g': 0.2},
    ]
    
    # Convert to DataFrame (required format for new GA)
    food_database = pd.DataFrame(foods_data)
    
    # Add required columns if missing
    for col in ['carbohydrate_g', 'fiber_g', 'sodium_mg']:
        if col not in food_database.columns:
            food_database[col] = 0.0
    
    # Simple guidelines
    guidelines = {
        'nutrients': {
            'energy_kcal': {'min': 1800, 'max': 2200},
            'protein_g': {'min': 50, 'max': 150},
            'carbohydrate_g': {'min': 200, 'max': 300},
            'fat_g': {'min': 40, 'max': 100}
        }
    }
    
    user_tdee = 2000
    
    print("Running GA with new dict-chromosome design...")
    print(f"  Food Database: {len(food_database)} items")
    print(f"  Target TDEE: {user_tdee} kcal")
    print(f"  Guidelines: energy {guidelines['nutrients']['energy_kcal']['min']}-{guidelines['nutrients']['energy_kcal']['max']}")
    
    # Run GA (WITHOUT pre-made candidates - uses entire food database)
    optimizer = GeneticAlgorithmOptimizer(
        food_database=food_database,
        guidelines=guidelines,
        user_tdee=user_tdee,
        population_size=30,
        generations=20,
        verbose=True
    )
    
    best_chromosome, best_fitness = optimizer.optimize()
    
    if best_chromosome:
        print(f"\n[OK] Best Solution Found!")
        print(f"  Fitness Score: {best_fitness:.2f} / 100")
        print(f"  Chromosome Structure:")
        print(f"    {ChromosomeOperations.to_string(best_chromosome)}")
    else:
        print("[ERROR] Optimization failed")

    print(f"Best Chromosome: {best_chromosome}")


if __name__ == "__main__":
    # Run complete flow example
    example_complete_flow()
    
    # Uncomment untuk test GA standalone
    # example_ga_only()


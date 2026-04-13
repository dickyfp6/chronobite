"""
PHASE 3 CONCRETE EXAMPLE: End-to-End Interactive Menu Workflow

Demonstrasi lengkap Phase 3:
1. Load GA output (simulated)
2. Process dengan MenuPostProcessor
3. Display dengan InteractiveMenuFormatter
4. Get user selection
5. Show final menu
"""

import pandas as pd
from typing import Dict, List
import numpy as np

# Assume these modules exist in same directory
from menu_post_processor import MenuPostProcessor
from interactive_menu_formatter import InteractiveMenuFormatter


# =============================================================================
# EXAMPLE 1: Minimal CONCRETE Example
# =============================================================================

def example_1_minimal():
    """
    Minimal example showing core workflow
    """
    
    print("\n" + "="*80)
    print("EXAMPLE 1: MINIMAL WORKFLOW")
    print("="*80 + "\n")
    
    # Simulate GA output
    # GA usually returns population of shape: (pop_size, num_meals*num_categories)
    # Each element is food_id (0-3920 from USDA dataset)
    
    simulated_population = [
        [100, 200, 300, 101, 201, 301, 102, 202, 302],  # Solution 1
        [103, 203, 303, 104, 204, 304, 105, 205, 305],  # Solution 2
        [106, 206, 306, 107, 207, 307, 108, 208, 308],  # Solution 3
        [109, 209, 309, 110, 210, 310, 111, 211, 311],  # Solution 4
        [112, 212, 312, 113, 213, 313, 114, 214, 314],  # Solution 5
        # ... more solutions (typically 50)
    ]
    
    simulated_fitness = [75.3, 72.1, 70.5, 68.9, 67.2]  # Fitness scores
    
    # Load food database
    # In real scenario: pd.read_csv('path/to/05_final_dataset.csv')
    # For this example, we'll use placeholder structure
    
    print("✓ Simulated GA population: 5 chromosomes")
    print("✓ Simulated fitness scores: [75.3, 72.1, 70.5, 68.9, 67.2]")
    print("\nNote: In production, use real GA output from GeneticAlgorithmOptimizer")
    
    # Load real food database (if available)
    try:
        food_database = pd.read_csv(
            'C:/Users/Silfia/Documents/FILE TA/TugasAkhirDSS/A. Data/Data Processed/05_final_dataset.csv'
        )
        print(f"✓ Loaded food database: {len(food_database)} foods")
    except:
        print("⚠ Food database not found - using mock data for demo")
        # Create mock food database
        food_database = create_mock_food_database(300)
    
    # STEP 1: Process GA output
    print("\n[STEP 1] Processing GA output with MenuPostProcessor...")
    processor = MenuPostProcessor()
    meal_options, snack_options = processor.process(
        population=simulated_population,
        fitness_scores=simulated_fitness,
        food_database=food_database,
        top_k=5,
        top_n=3
    )
    print("✓ Post-processing complete")
    print(f"  - Meal options: {list(meal_options.keys())}")
    print(f"  - Snack options: {len(snack_options)} snacks")
    
    # STEP 2: Display interactive menu
    print("\n[STEP 2] Displaying interactive menu...")
    InteractiveMenuFormatter.display_interactive_menu(
        meal_options=meal_options,
        snack_options=snack_options,
        user_tdee=2500,
        ga_fitness_score=75.3
    )
    
    # STEP 3: Show alternate display formats
    print("\n[STEP 3] ALTERNATIVE DISPLAY FORMATS")
    print("-" * 80)
    
    print("\nCompact format:")
    InteractiveMenuFormatter.display_compact_menu(meal_options, snack_options)
    
    return meal_options, snack_options


# =============================================================================
# EXAMPLE 2: Dengan Real User Input Integration
# =============================================================================

def example_2_with_user_integration():
    """
    Contoh dengan actual user profile dari NutritionService
    """
    
    print("\n" + "="*80)
    print("EXAMPLE 2: WITH USER PROFILE INTEGRATION")
    print("="*80 + "\n")
    
    # Simulated user profile dari NutritionService
    user_profile = {
        'age': 30,
        'weight': 75,
        'height': 175,
        'gender': 'male',
        'activity_level': 'moderate',
        'bmr': 1800,
        'tdee': 2500,
        'daily_protein_target': 100,
        'daily_carbs_target': 300,
        'daily_fat_target': 80,
        'dietary_restrictions': [],
        'food_preferences': []
    }
    
    # Load food database
    try:
        food_database = pd.read_csv(
            'C:/Users/Silfia/Documents/FILE TA/TugasAkhirDSS/A. Data/Data Processed/05_final_dataset.csv'
        )
    except:
        food_database = create_mock_food_database(300)
    
    # PHASE 1: Display user profile
    print("PHASE 1: USER PROFILE")
    print("-" * 80)
    print(f"Age: {user_profile['age']} | Weight: {user_profile['weight']}kg | Height: {user_profile['height']}cm")
    print(f"Activity: {user_profile['activity_level']}")
    print(f"Daily Targets:")
    print(f"  - Energy: {user_profile['tdee']:.0f} kcal")
    print(f"  - Protein: {user_profile['daily_protein_target']:.0f}g")
    print(f"  - Carbs: {user_profile['daily_carbs_target']:.0f}g")
    print(f"  - Fat: {user_profile['daily_fat_target']:.0f}g")
    
    # PHASE 2: GA Optimization (simulated)
    print("\n\nPHASE 2: GENETIC ALGORITHM OPTIMIZATION")
    print("-" * 80)
    print("GA running with 50 population, 100 generations...")
    simulated_population = [
        np.random.randint(0, len(food_database), 9) for _ in range(50)
    ]
    simulated_fitness = 75.3 + np.random.randn(50) * 5
    
    best_idx = np.argmax(simulated_fitness)
    best_fitness = simulated_fitness[best_idx]
    
    print(f"✓ GA Complete")
    print(f"  - Best fitness: {best_fitness:.1f}/100")
    print(f"  - Generations run: 100")
    print(f"  - Population size: 50")
    
    # PHASE 3: Interactive Menu
    print("\n\nPHASE 3: INTERACTIVE MENU SELECTION")
    print("-" * 80)
    
    processor = MenuPostProcessor()
    meal_options, snack_options = processor.process(
        population=simulated_population,
        fitness_scores=simulated_fitness,
        food_database=food_database,
        top_k=5,
        top_n=3
    )
    
    InteractiveMenuFormatter.display_interactive_menu(
        meal_options=meal_options,
        snack_options=snack_options,
        user_tdee=user_profile['tdee'],
        ga_fitness_score=best_fitness
    )
    
    return meal_options, snack_options, user_profile


# =============================================================================
# EXAMPLE 3: Full Workflow dengan User Selection
# =============================================================================

def example_3_with_selection():
    """
    Fully interactive: mulai dari data sampai user membuat pilihan
    """
    
    print("\n" + "="*80)
    print("EXAMPLE 3: FULL INTERACTIVE WORKFLOW")
    print("="*80 + "\n")
    
    # Load data
    try:
        food_database = pd.read_csv(
            'C:/Users/Silfia/Documents/FILE TA/TugasAkhirDSS/A. Data/Data Processed/05_final_dataset.csv'
        )
    except:
        food_database = create_mock_food_database(300)
    
    # Simulate GA (in reality, from GeneticAlgorithmOptimizer)
    population = [
        np.random.randint(0, len(food_database), 9) for _ in range(50)
    ]
    fitness_scores = 75.3 + np.random.randn(50) * 5
    
    # Process
    processor = MenuPostProcessor()
    meal_options, snack_options = processor.process(
        population=population,
        fitness_scores=fitness_scores,
        food_database=food_database,
        top_k=5,
        top_n=3
    )
    
    # Display
    user_tdee = 2500
    ga_best_fitness = 75.3
    
    InteractiveMenuFormatter.display_interactive_menu(
        meal_options=meal_options,
        snack_options=snack_options,
        user_tdee=user_tdee,
        ga_fitness_score=ga_best_fitness
    )
    
    # Simulate user selection (auto-select for demo)
    # In production: use interactive input from get_user_selections()
    print("\n[AUTO-SELECTING MENU FOR DEMO]")
    print("(In real use, user would input selections interactively)\n")
    
    selection = {
        'breakfast': {
            'main_course': 0,
            'side_dish': 0,
            'drink': 0
        },
        'lunch': {
            'main_course': 1,
            'side_dish': 1,
            'drink': 1
        },
        'dinner': {
            'main_course': 2,
            'side_dish': 2,
            'drink': 0
        },
        'snacks': [0, 2]
    }
    
    # Display selected menu with totals
    print("\n" + "="*80)
    print("YOUR SELECTED MENU")
    print("="*80 + "\n")
    
    total_energy = 0
    total_protein = 0
    total_carbs = 0
    total_fat = 0
    
    for meal in ['breakfast', 'lunch', 'dinner']:
        
        print(f"\n{meal.upper()}")
        print("-" * 60)
        
        if meal in selection:
            for category, idx in selection[meal].items():
                
                if category in meal_options[meal]:
                    option = meal_options[meal][category][idx]
                    
                    name = option.get('food_name', 'Unknown')
                    portion = option.get('portion', 0)
                    kcal = option.get('energy_kcal', 0)
                    protein = option.get('protein_g', 0)
                    carbs = option.get('carbs_g', 0)
                    fat = option.get('fat_g', 0)
                    
                    print(f"  {category.replace('_', ' ').title()}: {name} ({portion:.0f}g)")
                    print(f"    {kcal:.0f} kcal | P:{protein:.1f}g C:{carbs:.1f}g F:{fat:.1f}g")
                    
                    total_energy += kcal
                    total_protein += protein
                    total_carbs += carbs
                    total_fat += fat
    
    # Snacks
    if 'snacks' in selection and selection['snacks']:
        print(f"\nSNACK")
        print("-" * 60)
        
        for idx in selection['snacks']:
            snack = snack_options[idx]
            name = snack.get('food_name', 'Unknown')
            portion = snack.get('portion', 0)
            kcal = snack.get('energy_kcal', 0)
            
            print(f"  {name} ({portion:.0f}g | {kcal:.0f} kcal)")
            total_energy += kcal
    
    # Summary
    print("\n" + "="*80)
    print("DAILY NUTRITION SUMMARY")
    print("="*80)
    print(f"\nEnergy:  {total_energy:>6.0f} kcal / {user_tdee:>5.0f} kcal ({total_energy/user_tdee*100:>5.1f}%)")
    print(f"Protein: {total_protein:>6.1f}g / {100:>5.1f}g ({total_protein/100*100:>5.1f}%)")
    print(f"Carbs:   {total_carbs:>6.1f}g / {300:>5.1f}g ({total_carbs/300*100:>5.1f}%)")
    print(f"Fat:     {total_fat:>6.1f}g / {80:>5.1f}g ({total_fat/80*100:>5.1f}%)")
    print()


# =============================================================================
# HELPER: Create Mock Food Database
# =============================================================================

def create_mock_food_database(num_foods: int = 100) -> pd.DataFrame:
    """
    Create mock food database untuk testing tanpa real data
    """
    
    food_names = [
        'Nasi Putih', 'Nasi Kuning', 'Nasi Goreng', 'Nasi Merah',
        'Roti Tawar', 'Roti Gandum', 'Roti Bakar',
        'Ayam Goreng', 'Ayam Rebus', 'Ayam Bakar', 'Daging Sapi', 'Daging Sapi Rebus',
        'Ikan Bakar', 'Ikan Goreng', 'Ikan Kukus', 'Tahu Goreng', 'Tahu Kuning',
        'Tempe Goreng', 'Tempe Rebus', 'Telur Rebus', 'Telur Goreng',
        'Sayur Bayam', 'Sayur Brokoli', 'Sayur Wortel', 'Sayur Kangkung',
        'Sambal Matah', 'Sambal Terasi', 'Sambal Ulek',
        'Sup Ayam', 'Sup Iga', 'Sop Buntut', 'Soto Ayam',
        'Teh Tawar', 'Teh Manis', 'Kopi Hitam', 'Kopi Susu',
        'Air Putih', 'Jus Jeruk', 'Jus Apel', 'Jus Tomat',
        'Susu Putih', 'Susu Cokelat', 'Yogurt Plain', 'Yogurt Buah',
        'Pisang', 'Apel', 'Jeruk', 'Mangga', 'Papaya',
        'Kue Lapis', 'Kue Bolu', 'Kue Tart', 'Donat', 'Bingka'
    ]
    
    np.random.seed(42)
    
    data = {
        'food_name': [food_names[i % len(food_names)] + f' {i//len(food_names)+1}' 
                      for i in range(num_foods)],
        'energy_kcal': np.random.uniform(50, 400, num_foods),
        'protein_g': np.random.uniform(1, 30, num_foods),
        'carbs_g': np.random.uniform(5, 60, num_foods),
        'fat_g': np.random.uniform(0, 20, num_foods),
        'portion_g': np.random.uniform(50, 300, num_foods),
        'fdc_id': range(num_foods),
    }
    
    return pd.DataFrame(data)


# =============================================================================
# RUN EXAMPLES
# =============================================================================

if __name__ == "__main__":
    
    print("\n" + "="*80)
    print("PHASE 3 CONCRETE EXAMPLES")
    print("="*80)
    
    print("\n[1] Running Example 1: Minimal Workflow...")
    try:
        meal_opts_1, snack_opts_1 = example_1_minimal()
        print("\n✓ Example 1 complete\n")
    except Exception as e:
        print(f"\n✗ Example 1 failed: {e}\n")
    
    input("\nPress Enter to continue to Example 2...")
    
    print("\n[2] Running Example 2: With User Integration...")
    try:
        meal_opts_2, snack_opts_2, profile_2 = example_2_with_user_integration()
        print("\n✓ Example 2 complete\n")
    except Exception as e:
        print(f"\n✗ Example 2 failed: {e}\n")
    
    input("\nPress Enter to continue to Example 3...")
    
    print("\n[3] Running Example 3: Full Interactive Workflow...")
    try:
        example_3_with_selection()
        print("\n✓ Example 3 complete\n")
    except Exception as e:
        print(f"\n✗ Example 3 failed: {e}\n")
    
    print("\n" + "="*80)
    print("ALL EXAMPLES COMPLETE")
    print("="*80)
    print("\nNext steps:")
    print("  1. Modify your GA optimizer to save population/fitness")
    print("  2. Integrate into main workflow (run_ga_with_input_v2.py)")
    print("  3. Test with real GA output")
    print("  4. Deploy with user interface")

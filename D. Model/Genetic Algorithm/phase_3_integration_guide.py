"""
PHASE 3 INTEGRATION GUIDE: MenuPostProcessor + Interactive Formatter

Menghubungkan GA Output → MenuPostProcessor → InteractiveMenuFormatter
untuk menghasilkan INTERACTIVE MULTI-OPTION MENU dengan Checklist
"""

# =============================================================================
# STEP 1: IMPORT MODULES
# =============================================================================

from menu_post_processor import MenuPostProcessor
from interactive_menu_formatter import InteractiveMenuFormatter
from ga_optimizer import GeneticAlgorithmOptimizer  # or your GA interface
import pandas as pd


# =============================================================================
# STEP 2: BASIC WORKFLOW - GA → MenuPostProcessor → Display
# =============================================================================

def create_interactive_menu(
    population,
    fitness_scores,
    food_database,
    user_tdee=None,
    ga_fitness_score=None,
    top_k=5,
    top_n=3
):
    """
    Complete workflow: GA output → interactive menu
    
    Args:
        population: GA population (list of chromosomes)
        fitness_scores: Fitness scores (list of floats)
        food_database: Pandas DataFrame dengan food data
        user_tdee: User's TDEE (optional)
        ga_fitness_score: GA best fitness (optional)
        top_k: Extract top K chromosomes (default 5)
        top_n: Select top N options per category (default 3)
    
    Returns:
        meal_options, snack_options dicts
    """
    
    # STEP 1: Post-process GA output
    processor = MenuPostProcessor()
    meal_options, snack_options = processor.process(
        population=population,
        fitness_scores=fitness_scores,
        food_database=food_database,
        top_k=top_k,
        top_n=top_n
    )
    
    # STEP 2: Display interactive menu
    InteractiveMenuFormatter.display_interactive_menu(
        meal_options=meal_options,
        snack_options=snack_options,
        user_tdee=user_tdee,
        ga_fitness_score=ga_fitness_score
    )
    
    return meal_options, snack_options


# =============================================================================
# STEP 3: INTEGRATION INTO GA WORKFLOW
# =============================================================================

def run_ga_with_interactive_menu(user_input_dict, food_database, top_k=5, top_n=3):
    """
    Complete GA workflow dengan interactive menu di akhir
    
    Args:
        user_input_dict: User profile (age, weight, activity, etc.)
        food_database: Pandas DataFrame dari USDA data
        top_k: Extract top K chromosomes
        top_n: Select top N per category
    
    Returns:
        Tuple: (meal_options, snack_options, user_profile)
    """
    
    from nutrition_service import NutritionService
    from output_formatter_ga import OutputFormatterGA
    
    # STEP 1: Calculate user nutrition needs
    nutrition_service = NutritionService()
    user_profile = nutrition_service.calculate_nutrition_profile(user_input_dict)
    
    # Display user profile (PHASE 1 OUTPUT)
    formatter = OutputFormatterGA()
    formatter.display_user_profile(user_profile)
    
    # STEP 2: Run GA optimization
    optimizer = GeneticAlgorithmOptimizer(
        food_database=food_database,
        nutrition_targets=user_profile,
        population_size=50,
        generations=100
    )
    
    best_solution, best_fitness = optimizer.optimize()
    
    # Display GA result (PHASE 2 OUTPUT)
    formatter.display_ga_optimization(best_solution, best_fitness)
    
    # STEP 3: Extract top K and create interactive menu (PHASE 3 OUTPUT)
    population = optimizer.population  # or get from internal state
    fitness_scores = optimizer.fitness_scores
    
    meal_options, snack_options = create_interactive_menu(
        population=population,
        fitness_scores=fitness_scores,
        food_database=food_database,
        user_tdee=user_profile.get('tdee'),
        ga_fitness_score=best_fitness,
        top_k=top_k,
        top_n=top_n
    )
    
    return meal_options, snack_options, user_profile


# =============================================================================
# STEP 4: USER SELECTION LOGIC
# =============================================================================

def get_user_selections(meal_options, snack_options):
    """
    Interactive user selection dari menu options
    
    User memilih:
    - 1 main_course per meal (breakfast, lunch, dinner)
    - 1 side_dish per meal
    - 1 drink per meal (optional)
    - Snacks (1 atau lebih, optional)
    
    Returns:
        selection_dict: {meal: {category: selected_index}, ...}
    """
    
    selection = {}
    
    meals_order = ['breakfast', 'lunch', 'dinner']
    categories_order = ['main_course', 'side_dish', 'drink']
    
    for meal in meals_order:
        
        if meal not in meal_options:
            continue
        
        selection[meal] = {}
        meal_data = meal_options[meal]
        
        print(f"\n{'='*60}")
        print(f"{meal.upper()} SELECTIONS")
        print(f"{'='*60}")
        
        for category in categories_order:
            
            if category not in meal_data:
                continue
            
            options = meal_data[category]
            is_optional = (category == 'drink')
            
            while True:
                
                # List options
                print(f"\n{category.upper().replace('_', ' ')} (Choose one):")
                for idx, option in enumerate(options, 1):
                    food_name = option.get('food_name', 'Unknown')
                    energy = option.get('energy_kcal', 0)
                    print(f"  [{idx}] {food_name} ({energy:.0f} kcal)")
                
                if is_optional:
                    print(f"  [0] Skip (optional)")
                
                # Get user input
                choice = input(f"Enter your choice (1-{len(options)}{'/ 0 to skip' if is_optional else ''}): ").strip()
                
                try:
                    choice_idx = int(choice)
                    
                    if is_optional and choice_idx == 0:
                        # Skip this category
                        break
                    elif 1 <= choice_idx <= len(options):
                        selection[meal][category] = choice_idx - 1  # Convert to 0-indexed
                        break
                    else:
                        print(f"Invalid choice. Please enter 1-{len(options)}")
                except ValueError:
                    print("Please enter a valid number")
    
    # Snacks
    if snack_options:
        print(f"\n{'='*60}")
        print(f"SNACK SELECTIONS (Optional)")
        print(f"{'='*60}")
        
        selected_snacks = []
        
        print("\nAvailable snacks:")
        for idx, snack in enumerate(snack_options, 1):
            food_name = snack.get('food_name', 'Unknown')
            energy = snack.get('energy_kcal', 0)
            print(f"  [{idx}] {food_name} ({energy:.0f} kcal)")
        
        print("\nEnter snack choices (comma-separated, e.g., '1,3') or press Enter to skip:")
        choice = input("Your snack choices: ").strip()
        
        if choice:
            try:
                choices = [int(c.strip()) for c in choice.split(',')]
                selected_snacks = [int(c) - 1 for c in choices if 1 <= int(c) <= len(snack_options)]
            except ValueError:
                pass
        
        selection['snacks'] = selected_snacks
    
    return selection


def display_selected_menu(selection, meal_options, snack_options, user_profile):
    """
    Display menu yang user telah pilih
    """
    
    print(f"\n\n{'='*80}")
    print("YOUR SELECTED MENU")
    print(f"{'='*80}\n")
    
    total_energy = 0
    total_protein = 0
    total_carbs = 0
    total_fat = 0
    
    meals_order = ['breakfast', 'lunch', 'dinner']
    categories_order = ['main_course', 'side_dish', 'drink']
    
    for meal in meals_order:
        
        if meal not in selection:
            continue
        
        print(f"\n{meal.upper()}")
        print("-" * 60)
        
        meal_energy = 0
        meal_protein = 0
        meal_carbs = 0
        meal_fat = 0
        
        for category in categories_order:
            
            if category not in selection[meal] or category not in meal_options[meal]:
                continue
            
            idx = selection[meal][category]
            food = meal_options[meal][category][idx]
            
            food_name = food.get('food_name', 'Unknown')
            portion = food.get('portion', 0)
            energy = food.get('energy_kcal', 0)
            protein = food.get('protein_g', 0)
            carbs = food.get('carbs_g', 0)
            fat = food.get('fat_g', 0)
            
            print(f"  • {category.replace('_', ' ').title()}: {food_name}")
            print(f"    {portion:.0f}g | {energy:.0f} kcal | P:{protein:.1f}g C:{carbs:.1f}g F:{fat:.1f}g")
            
            meal_energy += energy
            meal_protein += protein
            meal_carbs += carbs
            meal_fat += fat
        
        print(f"\n  {meal.upper()} TOTAL: {meal_energy:.0f} kcal | P:{meal_protein:.1f}g C:{meal_carbs:.1f}g F:{meal_fat:.1f}g")
        
        total_energy += meal_energy
        total_protein += meal_protein
        total_carbs += meal_carbs
        total_fat += meal_fat
    
    # Snacks
    if 'snacks' in selection and selection['snacks']:
        print(f"\nSNACKS")
        print("-" * 60)
        
        snack_energy = 0
        snack_protein = 0
        snack_carbs = 0
        snack_fat = 0
        
        for idx in selection['snacks']:
            snack = snack_options[idx]
            
            food_name = snack.get('food_name', 'Unknown')
            portion = snack.get('portion', 0)
            energy = snack.get('energy_kcal', 0)
            protein = snack.get('protein_g', 0)
            carbs = snack.get('carbs_g', 0)
            fat = snack.get('fat_g', 0)
            
            print(f"  • {food_name}: {portion:.0f}g | {energy:.0f} kcal | P:{protein:.1f}g C:{carbs:.1f}g F:{fat:.1f}g")
            
            snack_energy += energy
            snack_protein += protein
            snack_carbs += carbs
            snack_fat += fat
        
        print(f"\n  SNACKS TOTAL: {snack_energy:.0f} kcal | P:{snack_protein:.1f}g C:{snack_carbs:.1f}g F:{snack_fat:.1f}g")
        
        total_energy += snack_energy
        total_protein += snack_protein
        total_carbs += snack_carbs
        total_fat += snack_fat
    
    # Daily totals
    print(f"\n\n{'='*80}")
    print("DAILY NUTRITION SUMMARY")
    print(f"{'='*80}")
    
    tdee = user_profile.get('tdee', 0)
    target_protein = user_profile.get('daily_protein_target', 0)
    target_carbs = user_profile.get('daily_carbs_target', 0)
    target_fat = user_profile.get('daily_fat_target', 0)
    
    print(f"\nEnergy:  {total_energy:.0f} kcal / {tdee:.0f} kcal (Target) | {(total_energy/tdee*100):.1f}%")
    print(f"Protein: {total_protein:.1f}g / {target_protein:.1f}g (Target) | {(total_protein/target_protein*100):.1f}%")
    print(f"Carbs:   {total_carbs:.1f}g / {target_carbs:.1f}g (Target) | {(total_carbs/target_carbs*100):.1f}%")
    print(f"Fat:     {total_fat:.1f}g / {target_fat:.1f}g (Target) | {(total_fat/target_fat*100):.1f}%")
    
    print(f"\n{'='*80}\n")


# =============================================================================
# STEP 5: COMPLETE EXAMPLE WORKFLOW
# =============================================================================

def complete_workflow_example(user_input_dict, food_database):
    """
    Full example: User Input → GA → Interactive Menu → Selection → Display
    """
    
    print("\n" + "="*80)
    print("PERSONALIZED NUTRITION MENU SYSTEM - PHASE 3 INTERACTIVE")
    print("="*80)
    
    # Step 1: Run GA with interactive menu
    meal_options, snack_options, user_profile = run_ga_with_interactive_menu(
        user_input_dict=user_input_dict,
        food_database=food_database,
        top_k=5,
        top_n=3
    )
    
    # Step 2: Get user selections
    selection = get_user_selections(meal_options, snack_options)
    
    # Step 3: Display selected menu
    display_selected_menu(selection, meal_options, snack_options, user_profile)
    
    return selection, user_profile


# =============================================================================
# USAGE EXAMPLE
# =============================================================================

if __name__ == "__main__":
    """
    Example usage:
    
    1. Load data:
        food_database = pd.read_csv('path/to/05_final_dataset.csv')
    
    2. Create user input:
        user_input = {
            'age': 30,
            'weight': 70,
            'height': 170,
            'gender': 'male',
            'activity_level': 'moderate',
            'dietary_restrictions': [],
            'food_preferences': []
        }
    
    3. Run workflow:
        selection, profile = complete_workflow_example(user_input, food_database)
    
    Or individual steps:
        
        # Step A: GA optimization
        meal_opts, snack_opts, profile = run_ga_with_interactive_menu(
            user_input, food_database
        )
        
        # Step B: Display options (already done above)
        
        # Step C: Get selections
        selection = get_user_selections(meal_opts, snack_opts)
        
        # Step D: Display final menu
        display_selected_menu(selection, meal_opts, snack_opts, profile)
    """
    
    print("Phase 3 Integration Guide loaded")
    print("\nUse this guide to integrate:")
    print("  1. MenuPostProcessor (extract top K chromosomes)")
    print("  2. InteractiveMenuFormatter (display checklist)")
    print("  3. User selection logic (get user picks)")
    print("  4. Final summary (show selected menu)")

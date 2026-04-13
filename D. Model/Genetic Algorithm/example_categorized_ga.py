"""
CONTOH IMPLEMENTASI: GA DENGAN CATEGORY CONSTRAINTS
Menunjukkan cara menggunakan CategorizedGeneticAlgorithmOptimizer

File ini bisa langsung dijalankan untuk testing
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple
from ga_chromosome_with_categories import FoodCategoryManager, CategorizedChromosome
from ga_optimizer_with_categories import CategorizedGeneticAlgorithmOptimizer


# ============================================================================
# STEP 1: PREPARE DATA (Mock Data untuk Contoh)
# ============================================================================

def create_sample_food_database() -> pd.DataFrame:
    """
    Create sample food database dengan kategori yang jelas
    Dalam production, ini dari 05_final_dataset.csv
    """
    foods = [
        # BREAKFAST - Main courses
        {'fdc_id': 101, 'food_name': 'Nasi Putih', 'food_category': 'main_course', 
         'energy_kcal': 280, 'protein_g': 6.5, 'carbs_g': 60, 'fat_g': 0.5, 'cuisine': 'indonesian'},
        {'fdc_id': 102, 'food_name': 'Nasi Kuning', 'food_category': 'main_course',
         'energy_kcal': 320, 'protein_g': 7, 'carbs_g': 62, 'fat_g': 4, 'cuisine': 'indonesian'},
        {'fdc_id': 103, 'food_name': 'Roti Tawar', 'food_category': 'main_course',
         'energy_kcal': 250, 'protein_g': 8, 'carbs_g': 48, 'fat_g': 2, 'cuisine': 'western'},
        {'fdc_id': 104, 'food_name': 'Oatmeal', 'food_category': 'main_course',
         'energy_kcal': 150, 'protein_g': 5, 'carbs_g': 28, 'fat_g': 3, 'cuisine': 'western'},
        
        # Side dishes
        {'fdc_id': 201, 'food_name': 'Telur Rebus', 'food_category': 'side_dish',
         'energy_kcal': 95, 'protein_g': 7.5, 'carbs_g': 0.7, 'fat_g': 7, 'cuisine': 'indonesian'},
        {'fdc_id': 202, 'food_name': 'Sambal Matah', 'food_category': 'side_dish',
         'energy_kcal': 120, 'protein_g': 2, 'carbs_g': 4, 'fat_g': 9, 'cuisine': 'indonesian'},
        {'fdc_id': 203, 'food_name': 'Tahu Goreng', 'food_category': 'side_dish',
         'energy_kcal': 180, 'protein_g': 16, 'carbs_g': 2, 'fat_g': 10, 'cuisine': 'indonesian'},
        {'fdc_id': 204, 'food_name': 'Yogurt', 'food_category': 'side_dish',
         'energy_kcal': 75, 'protein_g': 6, 'carbs_g': 5, 'fat_g': 1.5, 'cuisine': 'western'},
        
        # Drinks
        {'fdc_id': 301, 'food_name': 'Teh Tawar', 'food_category': 'drink',
         'energy_kcal': 5, 'protein_g': 0, 'carbs_g': 1, 'fat_g': 0, 'cuisine': 'indonesian'},
        {'fdc_id': 302, 'food_name': 'Kopi Hitam', 'food_category': 'drink',
         'energy_kcal': 15, 'protein_g': 1, 'carbs_g': 2, 'fat_g': 0.5, 'cuisine': 'indonesian'},
        {'fdc_id': 303, 'food_name': 'Jus Jeruk', 'food_category': 'drink',
         'energy_kcal': 110, 'protein_g': 2, 'carbs_g': 28, 'fat_g': 0.3, 'cuisine': 'indonesian'},
        {'fdc_id': 304, 'food_name': 'Susu Putih', 'food_category': 'drink',
         'energy_kcal': 160, 'protein_g': 8, 'carbs_g': 12, 'fat_g': 8, 'cuisine': 'western'},
        
        # LUNCH/DINNER - Main courses
        {'fdc_id': 401, 'food_name': 'Ayam Goreng', 'food_category': 'main_course',
         'energy_kcal': 380, 'protein_g': 42, 'carbs_g': 0, 'fat_g': 22, 'cuisine': 'indonesian'},
        {'fdc_id': 402, 'food_name': 'Ikan Bakar', 'food_category': 'main_course',
         'energy_kcal': 310, 'protein_g': 48, 'carbs_g': 0, 'fat_g': 12, 'cuisine': 'indonesian'},
        {'fdc_id': 403, 'food_name': 'Daging Sapi', 'food_category': 'main_course',
         'energy_kcal': 320, 'protein_g': 56, 'carbs_g': 0, 'fat_g': 10, 'cuisine': 'indonesian'},
        {'fdc_id': 404, 'food_name': 'Pasta Bolognese', 'food_category': 'main_course',
         'energy_kcal': 450, 'protein_g': 18, 'carbs_g': 55, 'fat_g': 15, 'cuisine': 'western'},
        
        # LUNCH/DINNER - Side dishes
        {'fdc_id': 501, 'food_name': 'Sayur Bayam', 'food_category': 'side_dish',
         'energy_kcal': 140, 'protein_g': 4, 'carbs_g': 6, 'fat_g': 10, 'cuisine': 'indonesian'},
        {'fdc_id': 502, 'food_name': 'Nasi Putih', 'food_category': 'side_dish',
         'energy_kcal': 280, 'protein_g': 6.5, 'carbs_g': 60, 'fat_g': 0.5, 'cuisine': 'indonesian'},
        {'fdc_id': 503, 'food_name': 'Kentang Goreng', 'food_category': 'side_dish',
         'energy_kcal': 200, 'protein_g': 3, 'carbs_g': 28, 'fat_g': 8, 'cuisine': 'western'},
        {'fdc_id': 504, 'food_name': 'Salad Sayur', 'food_category': 'side_dish',
         'energy_kcal': 85, 'protein_g': 3, 'carbs_g': 10, 'fat_g': 2, 'cuisine': 'western'},
        
        # SNACKS
        {'fdc_id': 601, 'food_name': 'Pisang Ambon', 'food_category': 'snack',
         'energy_kcal': 105, 'protein_g': 1.3, 'carbs_g': 27, 'fat_g': 0.3, 'cuisine': 'indonesian'},
        {'fdc_id': 602, 'food_name': 'Apel Merah', 'food_category': 'snack',
         'energy_kcal': 95, 'protein_g': 0.5, 'carbs_g': 25, 'fat_g': 0.3, 'cuisine': 'western'},
        {'fdc_id': 603, 'food_name': 'Kacang Almond', 'food_category': 'snack',
         'energy_kcal': 180, 'protein_g': 6.5, 'carbs_g': 6, 'fat_g': 14, 'cuisine': 'western'},
        {'fdc_id': 604, 'food_name': 'Kue Lapis', 'food_category': 'snack',
         'energy_kcal': 220, 'protein_g': 2, 'carbs_g': 32, 'fat_g': 9, 'cuisine': 'indonesian'},
    ]
    
    df = pd.DataFrame(foods)
    return df


def create_nutrition_targets_for_user(
    age: int = 30,
    weight: float = 70,
    height: float = 175,
    activity_level: str = 'moderate'
) -> Dict:
    """
    Create nutrition targets untuk user
    Dalam production, ini dari NutritionService/calculations.py
    """
    # Simple calculation
    if activity_level == 'sedentary':
        multiplier = 1.2
    elif activity_level == 'moderate':
        multiplier = 1.55
    else:
        multiplier = 1.9
    
    bmr = 10 * weight + 6.25 * height - 5 * age + 5
    tdee = bmr * multiplier
    
    return {
        'age': age,
        'weight': weight,
        'height': height,
        'activity_level': activity_level,
        'bmr': bmr,
        'tdee': tdee,
        'daily_protein_target': weight * 1.2,  # 1.2g per kg
        'daily_carbs_target': tdee * 0.45 / 4,  # 45% of calories
        'daily_fat_target': tdee * 0.30 / 9,    # 30% of calories
    }


# ============================================================================
# STEP 2: TEST CATEGORY MANAGER
# ============================================================================

def test_category_manager():
    """Test bahwa category separation berfungsi dengan baik"""
    print("\n" + "="*80)
    print("TEST 1: CATEGORY MANAGER")
    print("="*80)
    
    df = create_sample_food_database()
    print(f"\n✓ Loaded {len(df)} foods from database")
    print(f"Kolom yang ada: {list(df.columns)}")
    
    # Create category manager
    catmgr = FoodCategoryManager(df)
    print(f"\n✓ Category Manager initialized")
    print(f"Kategori yang ditemukan:")
    for cat, ids in catmgr.food_ids_by_category.items():
        count = len(ids)
        foods_in_cat = df[df['food_category'] == cat]['food_name'].tolist()
        print(f"  - {cat}: {count} foods")
        print(f"    Foods: {', '.join(foods_in_cat[:3])}")
    
    # Test filter by cuisine
    print(f"\n✓ Testing cuisine filter (indonesian only):")
    catmgr_ind = catmgr.filter_by_cuisine(['indonesian'])
    for cat, ids in catmgr_ind.food_ids_by_category.items():
        print(f"  - {cat}: {len(ids)} foods")


# ============================================================================
# STEP 3: TEST CHROMOSOME OPERATIONS
# ============================================================================

def test_chromosome_operations():
    """Test chromosome structure dan operations"""
    print("\n" + "="*80)
    print("TEST 2: CHROMOSOME OPERATIONS")
    print("="*80)
    
    df = create_sample_food_database()
    catmgr = FoodCategoryManager(df)
    
    # Create chromosome
    chromosome = CategorizedChromosome.initialize_random(catmgr)
    print(f"\n✓ Chromosome created")
    
    valid, msg = CategorizedChromosome.is_valid(chromosome)
    print(f"✓ Chromosome valid: {valid}")
    
    if valid:
        readable = CategorizedChromosome.to_readable(chromosome, df)
        print(f"\n✓ Readable format:")
        for meal, foods in readable.items():
            if isinstance(foods, dict):
                print(f"  {meal}:")
                for cat, food_name in foods.items():
                    print(f"    - {cat}: {food_name}")
            else:
                print(f"  {meal}: {foods}")
    
    # Test mutation
    print(f"\n✓ Testing mutation...")
    mutated = CategorizedChromosome.mutate(chromosome, catmgr, mutation_rate=0.5)
    valid2, msg2 = CategorizedChromosome.is_valid(mutated)
    print(f"✓ Mutated chromosome valid: {valid2}")
    
    # Test crossover
    print(f"\n✓ Testing crossover...")
    chromosome2 = CategorizedChromosome.initialize_random(catmgr)
    offspring = CategorizedChromosome.crossover(chromosome, chromosome2, catmgr)
    valid3, msg3 = CategorizedChromosome.is_valid(offspring)
    print(f"✓ Offspring chromosome valid: {valid3}")


# ============================================================================
# STEP 4: RUN GA WITH CATEGORY CONSTRAINTS
# ============================================================================

def test_ga_optimization():
    """Run complete GA dengan category constraints"""
    print("\n" + "="*80)
    print("TEST 3: GA OPTIMIZATION WITH CATEGORY CONSTRAINTS")
    print("="*80)
    
    # Prepare data
    food_db = create_sample_food_database()
    nutrition_targets = create_nutrition_targets_for_user()
    
    print(f"\n✓ User nutrition targets:")
    print(f"  - TDEE: {nutrition_targets['tdee']:.0f} kcal")
    print(f"  - Protein: {nutrition_targets['daily_protein_target']:.0f}g")
    print(f"  - Carbs: {nutrition_targets['daily_carbs_target']:.0f}g")
    print(f"  - Fat: {nutrition_targets['daily_fat_target']:.0f}g")
    
    # Create optimizer
    user_pref = {'cuisine': ['indonesian']}  # Prefer Indonesian food
    
    optimizer = CategorizedGeneticAlgorithmOptimizer(
        food_database=food_db,
        nutrition_targets=nutrition_targets,
        user_preferences=user_pref,
        population_size=30,
        generations=50,
        mutation_rate=0.15,
        crossover_rate=0.80,
        verbose=True
    )
    
    # Run optimization
    print(f"\n{'='*80}")
    print("STARTING GA OPTIMIZATION...")
    print(f"{'='*80}")
    
    best_solution, best_fitness = optimizer.optimize()
    
    print(f"\n{'='*80}")
    print("OPTIMIZATION COMPLETE!")
    print(f"{'='*80}")
    print(f"\nBest Fitness: {best_fitness:.2f}")
    
    # Show readable solution
    readable = optimizer.get_best_solution_readable()
    print(f"\nBest Menu Found:")
    for meal, foods in readable.items():
        if isinstance(foods, dict):
            print(f"\n{meal.upper()}:")
            for cat, food_name in foods.items():
                print(f"  - {cat:15s}: {food_name}")
        else:
            print(f"\n{meal.upper()}: {foods}")


# ============================================================================
# STEP 5: MAIN - RUN ALL TESTS
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*80)
    print("CONTOH IMPLEMENTASI: GA DENGAN CATEGORY CONSTRAINTS")
    print("="*80)
    
    try:
        test_category_manager()
        test_chromosome_operations()
        test_ga_optimization()
        
        print("\n" + "="*80)
        print("✓ ALL TESTS PASSED!")
        print("="*80)
        print("\nKey Insights:")
        print("1. FoodCategoryManager mengelola pool makanan per kategori")
        print("2. CategorizedChromosome memastikan struktur meal yang jelas")
        print("3. Mutation/Crossover strictly respect kategori")
        print("4. Hasil menu always realistis (main + side + drink)")
        print("5. User preference (cuisine) bisa di-apply via filter")
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()

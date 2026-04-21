"""
GENETIC ALGORITHM - Simple Implementation v1
============================================

Core GA engine untuk meal planning optimization.
Mencari kombinasi 10 makanan (10 gene chromosome) yang memenuhi
constraint nutrisi dengan penalty minimal.

Struktur Chromosome (10 items):
- 0: breakfast_main
- 1: breakfast_side
- 2: breakfast_drink
- 3: lunch_main
- 4: lunch_side
- 5: lunch_drink
- 6: dinner_main
- 7: dinner_side
- 8: dinner_drink
- 9: snack

Fitness = Total penalty terhadap nutrient constraints
GA Loop = Initialize → Evaluate → Select → Crossover → Mutate → Repeat

Tanpa class, hanya functions murni.
"""

import pandas as pd
import numpy as np
import random
from typing import List, Dict, Tuple, Optional, cast

# ═════════════════════════════════════════════════════════════════════════════
# CHROMOSOME STRUCTURE
# ═════════════════════════════════════════════════════════════════════════════

CHROMOSOME_SIZE = 10
SLOT_NAMES = [
    'breakfast_main',    # 0
    'breakfast_side',    # 1
    'breakfast_drink',   # 2
    'lunch_main',        # 3
    'lunch_side',        # 4
    'lunch_drink',       # 5
    'dinner_main',       # 6
    'dinner_side',       # 7
    'dinner_drink',      # 8
    'snack'              # 9
]

MEAL_INDICES = {
    'breakfast': [0, 1, 2],  # main, side, drink
    'lunch': [3, 4, 5],      # main, side, drink
    'dinner': [6, 7, 8],     # main, side, drink
    'snack': [9]             # just 1 item
}

# Mapping slot index ke expected food group
# Digunakan untuk filter agar breakfast_drink tidak jadi main course, dll
SLOT_FOOD_GROUP_MAPPING = {
    0: ['main_course', 'staple', 'rice', 'bread'],           # breakfast_main
    1: ['side_dish', 'vegetable', 'protein', 'legume'],      # breakfast_side
    2: ['beverage', 'drink', 'juice', 'milk', 'tea'],        # breakfast_drink
    3: ['main_course', 'staple', 'rice', 'noodle'],          # lunch_main
    4: ['side_dish', 'vegetable', 'protein', 'legume'],      # lunch_side
    5: ['beverage', 'drink', 'juice', 'milk', 'tea'],        # lunch_drink
    6: ['main_course', 'staple', 'rice', 'noodle'],          # dinner_main
    7: ['side_dish', 'vegetable', 'protein', 'legume'],      # dinner_side
    8: ['beverage', 'drink', 'juice', 'milk', 'tea'],        # dinner_drink
    9: ['snack', 'dessert', 'fruit', 'nut']                  # snack
}

# Nutrient weights - semakin tinggi weight semakin strict constraint-nya
NUTRIENT_WEIGHTS = {
    'energy_kcal': 2.0,      # Energy is critical
    'protein_g': 1.5,        # Protein important
    'fat_g': 1.2,            # Fat moderation
    'carbohydrate_g': 1.2,   # Carbs moderation
    'fiber_g': 1.0,          # Standard weight
    'sodium_mg': 1.3,        # Important for health
    'calcium_mg': 1.0,       # Standard
    'iron_mg': 1.0,          # Standard
    'phosphorus_mg': 1.0,    # Standard
    'zinc_mg': 1.0,          # Standard
    'potassium_mg': 1.2,     # Important for hypertension
    'magnesium_mg': 1.0,     # Standard
    'vitamin_a_iu': 0.8,     # Lower weight (optional)
    'vitamin_c_mg': 0.8,     # Lower weight
    'vitamin_b1_mg': 0.8,    # Lower weight
    'vitamin_b2_mg': 0.8,    # Lower weight
    'vitamin_b3_mg': 0.8,    # Lower weight
    'cholesterol_mg': 1.2    # Important for CVD
}

# Duplicate penalty weight
DUPLICATE_PENALTY_WEIGHT = 50.0  # Penalty for each duplicate food item


# ═════════════════════════════════════════════════════════════════════════════
# 1. RANDOM SOLUTION - Generate meal plan random
# ═════════════════════════════════════════════════════════════════════════════

def _filter_food_by_slot(food_df: pd.DataFrame, slot_idx: int) -> pd.DataFrame:
    """
    Filter food items sesuai dengan expected food group untuk slot tertentu
    
    Args:
        food_df: DataFrame berisi semua food items
        slot_idx: Index slot (0-9)
    
    Returns:
        Filtered DataFrame atau original jika tidak ada food_group column
    """
    # Jika tidak ada food_group column, return semua items
    if 'food_group' not in food_df.columns:
        return food_df
    
    # Ambil expected groups untuk slot ini
    expected_groups = SLOT_FOOD_GROUP_MAPPING.get(slot_idx, [])
    if not expected_groups:
        return food_df
    
    # Filter items yang memiliki salah satu expected group
    filtered = cast(pd.DataFrame, food_df[food_df['food_group'].isin(expected_groups)])
    
    # Jika tidak ada match, return original (fallback)
    if len(filtered) == 0:
        return food_df
    
    return filtered


def random_solution(food_df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate 1 solusi random = 10 makanan random dari food_df dengan food group filter
    
    Chromosome structure:
    - Index 0-2: breakfast (main, side, drink)
    - Index 3-5: lunch (main, side, drink)
    - Index 6-8: dinner (main, side, drink)
    - Index 9: snack
    
    Args:
        food_df: DataFrame berisi semua food items (optional: dengan kolom 'food_group')
    
    Returns:
        DataFrame dengan 10 baris (1 item per slot)
    
    Logic:
        - Untuk setiap slot (0-9), filter foods by expected group
        - Jika food_df >= 10 items → sample tanpa replacement (unique)
        - Jika food_df < 10 items → sample dengan replacement (boleh duplikat)
    
    Example:
        solution = random_solution(food_df)
        # output: DataFrame dengan 10 rows
        #   food_name           food_group      energy_kcal  ...
        # 0  Nasi Putih          rice            180          ...
        # 1  Telur Goreng        protein         150          ...
        # 2  Teh Panas           beverage        50           ...
        # 3  Nasi Goreng         main_course     450          ...
        # ...
        # 9  Kue                 snack           100          ...
    """
    if len(food_df) < 1:
        raise ValueError(f"Food database harus memiliki minimal 1 item, got {len(food_df)}")
    
    solution_items = []
    
    # Generate 1 item per slot dengan food group filter jika tersedia
    for slot_idx in range(CHROMOSOME_SIZE):
        filtered_df = _filter_food_by_slot(food_df, slot_idx)
        
        # Smart replacement: jika ada cukup items, ambil unik; jika tidak, boleh duplikat
        replace_flag = len(filtered_df) < 1  # Only replace if 0 items left
        
        # Sample 1 item untuk slot ini
        if len(filtered_df) > 0:
            item = filtered_df.sample(n=1, replace=replace_flag)
            solution_items.append(item)
    
    # Concat semua items dan reset index
    if solution_items:
        solution = pd.concat(solution_items, ignore_index=True)
    else:
        # Fallback: jika semua filter gagal, random sample saja
        replace_flag = len(food_df) < CHROMOSOME_SIZE
        solution = food_df.sample(n=CHROMOSOME_SIZE, replace=replace_flag).reset_index(drop=True)
    
    return solution


# ═════════════════════════════════════════════════════════════════════════════
# 2. CALCULATE TOTAL NUTRITION - Sum nutrisi dari 4 makanan
# ═════════════════════════════════════════════════════════════════════════════

def calculate_total_nutrition(solution: pd.DataFrame) -> Dict[str, float]:
    """
    Hitung total nutrisi dari 10 item dalam solution (chromosome)
    
    Args:
        solution: DataFrame dengan 10 baris (10 items dari chromosome)
    
    Returns:
        Dict: {nutrient_name: total_value, ...}
        Contoh: {'energy_kcal': 1850, 'protein_g': 65, 'fat_g': 45, ...}
    
    Method:
        - Sum semua numeric columns di solution
        - Ignore non-numeric columns
    """
    # Sum semua numeric columns (otomatis)
    total_nutrition = solution.select_dtypes(include=[np.number]).sum().to_dict()
    return total_nutrition


# ═════════════════════════════════════════════════════════════════════════════
# 3. FITNESS - Hitung penalty score dari nutrient violations
# ═════════════════════════════════════════════════════════════════════════════

def fitness(solution: pd.DataFrame, guidelines: Dict) -> float:
    """
    Hitung fitness score (penalty total) untuk 1 solusi (10-item chromosome)
    Dengan weighted nutrients, duplicate penalty, dan normalization
    
    Args:
        solution: DataFrame dengan 10 items (chromosome)
        guidelines: Dict dari NutritionService
                   {nutrient: {'min': float, 'max': float, ...}, ...}
    
    Returns:
        float: Total penalty (semakin kecil = semakin baik)
               0 = perfectly match guidelines
    
    Logic:
        1. Hitung total nutrisi dari 10 items
        2. Untuk setiap nutrient dalam guidelines:
           - Jika value < min → penalty += (min - value) * weight
           - Jika value > max → penalty += (value - max) * weight
           - Jika min ≤ value ≤ max → no penalty
        3. Add duplicate penalty jika ada duplikat food_name
        4. Normalize total penalty dengan jumlah constraints
        5. Return total penalty
    
    Example:
        guidelines = {
            'energy_kcal': {'min': 1800, 'max': 2200, ...},
            'protein_g': {'min': 60, 'max': 100, ...}
        }
        
        solution_nutrition = {'energy_kcal': 1900, 'protein_g': 50, ...}
        solution = [food1, food1, food3, ...]  # food1 appears twice = duplicate
        
        Penalties:
        - energy_kcal: 1800 ≤ 1900 ≤ 2200 → 0
        - protein_g: 50 < 60 → penalty = (60-50) * weight(1.5) = 15
        - duplicate: 1 duplicate * 50 = 50
        - normalized: (15 + 50) / 2 constraints = 32.5
        
        Total penalty = 32.5
    """
    # Hitung total nutrisi dari solution
    total_nutrition = calculate_total_nutrition(solution)
    
    total_penalty = 0.0
    constraint_count = 0
    
    # Iterate setiap nutrient constraint
    for nutrient_name, constraint in guidelines.items():
        # Skip jika constraint type unlimited
        if constraint.get('constraint_type') == 'unlimited':
            continue
        
        # Skip jika nutrient tidak ada di food database
        if nutrient_name not in total_nutrition:
            continue
        
        constraint_count += 1
        
        # Ambil nilai min dan max
        min_val = constraint.get('min', 0)
        max_val = constraint.get('max', float('inf'))
        value = total_nutrition[nutrient_name]
        
        # Get nutrient weight (default 1.0 jika tidak ada)
        weight = NUTRIENT_WEIGHTS.get(nutrient_name, 1.0)
        
        # Hitung penalty dengan weight
        if value < min_val:
            # Kurang dari minimum
            penalty = (min_val - value) * weight
            total_penalty += penalty
        elif value > max_val:
            # Lebih dari maximum
            penalty = (value - max_val) * weight
            total_penalty += penalty
        # else: dalam range, no penalty
    
    # ════════════════════════════════════════════════════════════════
    # PERBAIKAN 2: ADD DUPLICATE PENALTY
    # ════════════════════════════════════════════════════════════════
    if 'food_name' in solution.columns:
        unique_foods = solution['food_name'].nunique()
        duplicate_count = len(solution) - unique_foods
        duplicate_penalty = duplicate_count * DUPLICATE_PENALTY_WEIGHT
        total_penalty += duplicate_penalty
    
    # ════════════════════════════════════════════════════════════════
    # PERBAIKAN 4: NORMALIZE PENALTY
    # ════════════════════════════════════════════════════════════════
    if constraint_count > 0:
        total_penalty = total_penalty / constraint_count
    
    return total_penalty


# ═════════════════════════════════════════════════════════════════════════════
# 4. CROSSOVER - Single-point crossover antara 2 parent
# ═════════════════════════════════════════════════════════════════════════════

def crossover(parent1: pd.DataFrame, parent2: pd.DataFrame) -> pd.DataFrame:
    """
    Single-point crossover: ambil N genes dari parent1, sisa dari parent2
    
    Args:
        parent1: Solution (DataFrame 10 rows)
        parent2: Solution (DataFrame 10 rows)
    
    Returns:
        Child: DataFrame hasil kombinasi parent1 + parent2
    
    Method:
        1. Random pilih crossover point (1-9)
           point = 3 → child = [P1[0:3] + P2[3:10]]
           point = 6 → child = [P1[0:6] + P2[6:10]]
        2. Konkatenasi dan reset index
    
    Example:
        P1 = [A,B,C,D,E,F,G,H,I,J]
        P2 = [1,2,3,4,5,6,7,8,9,10]
        
        Point = 3:
        Child = [A,B,C] + [4,5,6,7,8,9,10] = [A,B,C,4,5,6,7,8,9,10]
    """
    # Ensure size = 10
    assert len(parent1) == CHROMOSOME_SIZE, f"Parent1 harus {CHROMOSOME_SIZE} rows"
    assert len(parent2) == CHROMOSOME_SIZE, f"Parent2 harus {CHROMOSOME_SIZE} rows"
    
    # Random crossover point (1-9, tidak 0 atau 10)
    point = random.randint(1, CHROMOSOME_SIZE - 1)
    
    # Ambil N genes dari parent1, sisa dari parent2
    child_p1 = parent1.iloc[:point].copy()
    child_p2 = parent2.iloc[point:].copy()
    
    # Gabung - explicit cast to DataFrame untuk type checker
    concatenated = pd.concat([child_p1, child_p2], ignore_index=True)
    result = cast(pd.DataFrame, concatenated)
    
    return result


# ═════════════════════════════════════════════════════════════════════════════
# 5. MUTATION - Ganti 1 item random dengan makanan baru
# ═════════════════════════════════════════════════════════════════════════════

def mutation(solution: pd.DataFrame, food_df: pd.DataFrame, 
             mutation_rate: float = 0.3) -> pd.DataFrame:
    """
    Mutation: Replace 1 random gene (item) dalam solution dengan food baru
    Dengan food group filter untuk memastikan konsistensi
    
    Args:
        solution: DataFrame (10 rows)
        food_df: Semua available food items
        mutation_rate: Probability untuk apply mutation (default 0.3 = 30%)
    
    Returns:
        Mutated solution (atau original jika no mutation)
    
    Method:
        1. Jika random() > mutation_rate → return original (no mutation)
        2. Else:
           - Random select 1 gene index (0-9)
           - Filter food_df sesuai food group untuk index tersebut
           - Random select 1 food dari filtered foods
           - Replace gene tersebut
           - Return mutated copy
    """
    # Check jika ada mutation
    if random.random() > mutation_rate:
        return solution.copy()
    
    # Ada mutation
    result = solution.copy()
    
    # Random select 1 gene index to mutate (0-9)
    gene_idx = random.randint(0, CHROMOSOME_SIZE - 1)
    
    # Filter food_df berdasarkan slot food group
    filtered_food_df = _filter_food_by_slot(food_df, gene_idx)
    
    # Random select 1 food dari filtered foods
    if len(filtered_food_df) > 0:
        new_food = filtered_food_df.sample(n=1).reset_index(drop=True)
    else:
        # Fallback jika no filtered foods
        new_food = food_df.sample(n=1).reset_index(drop=True)
    
    # Replace gene
    result.iloc[gene_idx] = new_food.iloc[0]
    
    return result


# ═════════════════════════════════════════════════════════════════════════════
# 6. RUN_GA - Main GA loop
# ═════════════════════════════════════════════════════════════════════════════

def run_ga(
    food_df: pd.DataFrame,
    guidelines: Dict,
    generations: int = 50,
    pop_size: int = 20,
    elite_ratio: float = 0.25,
    mutation_rate: float = 0.3,
    verbose: bool = True
) -> Tuple[pd.DataFrame, List[pd.DataFrame]]:
    """
    Jalankan Genetic Algorithm untuk mencari optimal meal plan
    
    Args:
        food_df: DataFrame semua food items
        guidelines: Dict constraints dari NutritionService
        generations: Jumlah generasi (default 50)
        pop_size: Ukuran populasi (default 20)
        elite_ratio: Fraksi elite untuk breeding (default 0.25 = top 25%)
        mutation_rate: Probability mutasi (default 0.3 = 30%)
        verbose: Print progress? (default True)
    
    Returns:
        Tuple: (best_solution, top_solutions)
               best_solution: DataFrame optimal meal plan terbaik
               top_solutions: List[DataFrame] 10 solusi terbaik untuk generate options
    
    Algorithm:
        For gen in generations:
            1. Evaluate: hitung fitness semua population
            2. Sort ascending (kecil = baik)
            3. Elite: ambil top elite_ratio
            4. Breeding: loop sampai pop_size
               - Random select 2 parent dari elite
               - Crossover → child
               - Mutation(prob=mutation_rate)
            5. Update population
        
        Return: best individual + top 10 solutions dari semua generasi
    """
    
    if verbose:
        print(f"\n{'='*70}")
        print(f"GENETIC ALGORITHM - MEAL PLANNING OPTIMIZATION")
        print(f"{'='*70}")
        print(f"Pop Size: {pop_size} | Generations: {generations}")
        print(f"Elite Ratio: {elite_ratio} | Mutation Rate: {mutation_rate}")
        print(f"Food Items: {len(food_df)} | Constraints: {len(guidelines)}")
        print(f"{'='*70}\n")
    
    # STEP 1: Initialize populasi random
    if verbose:
        print("[STEP 1] Initializing population...")
    
    population = []
    for _ in range(pop_size):
        solution = random_solution(food_df)
        population.append(solution)
    
    # Track best solution ever found
    best_solution = population[0].copy()
    best_fitness = fitness(best_solution, guidelines)
    
    # STEP 2: Main GA loop
    if verbose:
        print(f"[STEP 2] Running {generations} generations...")
        print(f"{'Gen':<5} | {'Best Fitness':<15} | {'Avg Fitness':<15}")
        print(f"{'-'*50}")
    
    for gen in range(generations):
        # 2a. Evaluate fitness semua population
        fitness_scores = []
        for solution in population:
            score = fitness(solution, guidelines)
            fitness_scores.append(score)
        
        # 2b. Sort population by fitness (ascending = semakin kecil semakin baik)
        sorted_indices = np.argsort(fitness_scores)
        population = [population[i] for i in sorted_indices]
        fitness_scores = [fitness_scores[i] for i in sorted_indices]
        
        # 2c. Track best solution
        if fitness_scores[0] < best_fitness:
            best_fitness = fitness_scores[0]
            best_solution = population[0].copy()
        
        # 2d. Show progress
        if verbose and (gen % max(1, generations // 10) == 0 or gen == generations - 1):
            avg_fitness = np.mean(fitness_scores)
            print(f"{gen:<5} | {fitness_scores[0]:<15.2f} | {avg_fitness:<15.2f}")
        
        # 2e. Selection: ambil elite
        elite_size = max(1, int(pop_size * elite_ratio))
        elite = population[:elite_size]
        
        # 2f. Breeding: buat populasi baru sampai pop_size
        new_population = elite.copy()  # Keep elite
        
        while len(new_population) < pop_size:
            # Select 2 parent dari elite (random with replacement)
            parent1 = random.choice(elite)
            parent2 = random.choice(elite)
            
            # Crossover
            child = crossover(parent1, parent2)
            
            # Mutation (probabilitas mutation_rate)
            child = mutation(child, food_df, mutation_rate=mutation_rate)
            
            # Add to new population
            new_population.append(child)
        
        # Update population
        population = new_population[:pop_size]
    
    # STEP 3: Final evaluation dan get top solutions
    if verbose:
        print(f"{'='*50}")
        print(f"[STEP 3] GA Complete!")
        print(f"Best Fitness Score: {best_fitness:.2f}")
    
    # Evaluate final population
    final_fitness_scores = []
    for solution in population:
        score = fitness(solution, guidelines)
        final_fitness_scores.append(score)
    
    # Sort population by fitness
    sorted_indices = np.argsort(final_fitness_scores)
    sorted_population = [population[i] for i in sorted_indices]
    sorted_scores = [final_fitness_scores[i] for i in sorted_indices]
    
    # Get top 10 solutions (atau kurang jika pop_size < 10)
    num_top_solutions = min(10, len(sorted_population))
    top_solutions = sorted_population[:num_top_solutions]
    
    if verbose:
        print(f"Top {num_top_solutions} solutions selected for options")
        print(f"{'='*50}\n")
    
    return best_solution, top_solutions


# ═════════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═════════════════════════════════════════════════════════════════════════════

def display_solution(solution: pd.DataFrame, guidelines: Optional[Dict] = None):
    """
    Display 10-item meal plan secara readable dengan slot labels
    
    Args:
        solution: DataFrame 10 items (chromosome)
        guidelines: Optional, untuk display constraint values
    """
    print("\n📋 MEAL PLAN (10-ITEM CHROMOSOME):")
    print("─" * 70)
    
    meal_order = ['breakfast', 'lunch', 'dinner', 'snack']
    
    for meal_name in meal_order:
        indices = MEAL_INDICES[meal_name]
        print(f"\n{meal_name.upper()}:")
        
        slot_types = ['main', 'side', 'drink'] if meal_name != 'snack' else ['item']
        
        for i, idx in enumerate(indices):
            if idx < len(solution):
                food_row = solution.iloc[idx]
                slot_type = slot_types[i] if i < len(slot_types) else 'item'
                food_name = food_row.get('food_name', 'Unknown')
                energy = food_row.get('energy_kcal', 0)
                
                print(f"  • {slot_type.capitalize()}: {food_name} ({energy:.0f} kcal)")
    
    # Display total nutrition
    print("\n" + "─" * 70)
    total_nutrition = calculate_total_nutrition(solution)
    print(f"📊 TOTAL NUTRITION:")
    
    # Show key nutrients
    key_nutrients = ['energy_kcal', 'protein_g', 'carbohydrate_g', 'fat_g', 'fiber_g']
    for nutrient in key_nutrients:
        if nutrient in total_nutrition:
            value = total_nutrition[nutrient]
            unit = 'kcal' if 'energy' in nutrient else 'g'
            print(f"   {nutrient.replace('_', ' ').title()}: {value:.1f} {unit}")


def generate_meal_options(top_solutions: List[pd.DataFrame], max_options_per_slot: int = 3) -> Dict[str, List[pd.Series]]:
    """
    Generate 3 pilihan makanan untuk SETIAP SLOT (breakfast_main, breakfast_side, dst)
    dari top solutions
    
    Output structure (10 slots):
    {
        'breakfast_main': [item1, item2, item3],
        'breakfast_side': [item1, item2, item3],
        'breakfast_drink': [item1, item2, item3],
        'lunch_main': [...],
        'lunch_side': [...],
        'lunch_drink': [...],
        'dinner_main': [...],
        'dinner_side': [...],
        'dinner_drink': [...],
        'snack': [item1, item2, item3]
    }
    
    Args:
        top_solutions: List of top DataFrame solutions dari GA (10 items each)
        max_options_per_slot: Jumlah pilihan per slot (default 3)
    
    Returns:
        Dict dengan 10 keys (per slot), masing-masing berisi list items
    
    Logic:
        1. Loop setiap slot index (0-9)
        2. Untuk setiap slot, loop setiap solution
        3. Ambil item dari solution.iloc[slot_idx]
        4. Deduplicate by food_name
        5. Simpan max 3 unik items per slot
    
    Example:
        top_solutions = [sol1, sol2, ..., sol10]  # each with 10 items
        options = generate_meal_options(top_solutions)
        
        options['breakfast_main'] = [
            pd.Series{food_name: 'Nasi Putih', energy_kcal: 180, ...},
            pd.Series{food_name: 'Roti Tawar', energy_kcal: 250, ...},
            pd.Series{food_name: 'Bubur Ayam', energy_kcal: 200, ...}
        ]
        
        options['breakfast_side'] = [
            pd.Series{food_name: 'Tempe Goreng', energy_kcal: 95, ...},
            ...
        ]
    """
    # Initialize dictionary untuk semua 10 slots
    slot_options = {slot: [] for slot in SLOT_NAMES}
    tracked_foods = {slot: set() for slot in SLOT_NAMES}  # Track food_name untuk dedup
    
    # Loop setiap slot index (0-9)
    for slot_idx in range(CHROMOSOME_SIZE):
        slot_name = SLOT_NAMES[slot_idx]
        
        # Loop setiap solution
        for solution in top_solutions:
            # Skip jika sudah punya max options untuk slot ini
            if len(slot_options[slot_name]) >= max_options_per_slot:
                break
            
            # Check index valid
            if slot_idx < len(solution):
                food_item = solution.iloc[slot_idx]
                food_name = food_item.get('food_name', 'Unknown')
                
                # Deduplicate: skip jika sudah ada
                if food_name in tracked_foods[slot_name]:
                    continue
                
                # Add to options
                slot_options[slot_name].append(food_item)
                tracked_foods[slot_name].add(food_name)
    
    return slot_options


def display_meal_options(slot_options: Dict[str, List[pd.Series]]):
    """
    Display 3 pilihan menu per slot dengan format readable
    
    Args:
        slot_options: Dict dari generate_meal_options()
                     {slot_name: [item1, item2, item3], ...}
                     Example: 'breakfast_main', 'breakfast_side', 'breakfast_drink',
                              'lunch_main', 'lunch_side', 'lunch_drink',
                              'dinner_main', 'dinner_side', 'dinner_drink', 'snack'
    
    Example output:
        🌅 BREAKFAST
        ├─ Main Course (3 options - click one):
        │  1. Nasi Putih (180 kcal | 3.6g protein)
        │  2. Roti Tawar (250 kcal | 8.0g protein)
        │  3. Bubur Ayam (200 kcal | 5.0g protein)
        ├─ Side Dish (3 options - click one):
        │  1. Telur Rebus...
        ...
    """
    print("\n" + "="*70)
    print("✨ 3 PILIHAN MENU PER SLOT ✨")
    print("="*70)
    
    # Meal groupings for display organization
    meal_structure = {
        'breakfast': {
            'emoji': '🌅',
            'slots': ['breakfast_main', 'breakfast_side', 'breakfast_drink'],
            'slot_labels': {
                'breakfast_main': 'Main Course',
                'breakfast_side': 'Side Dish',
                'breakfast_drink': 'Beverage'
            }
        },
        'lunch': {
            'emoji': '☀️',
            'slots': ['lunch_main', 'lunch_side', 'lunch_drink'],
            'slot_labels': {
                'lunch_main': 'Main Course',
                'lunch_side': 'Side Dish',
                'lunch_drink': 'Beverage'
            }
        },
        'dinner': {
            'emoji': '🌙',
            'slots': ['dinner_main', 'dinner_side', 'dinner_drink'],
            'slot_labels': {
                'dinner_main': 'Main Course',
                'dinner_side': 'Side Dish',
                'dinner_drink': 'Beverage'
            }
        },
        'snack': {
            'emoji': '🍪',
            'slots': ['snack'],
            'slot_labels': {
                'snack': 'Snack Option'
            }
        }
    }
    
    for meal_name, meal_info in meal_structure.items():
        meal_emoji = meal_info['emoji']
        print(f"\n{meal_emoji} {meal_name.upper()}")
        print("─" * 70)
        
        for slot_idx, slot_name in enumerate(meal_info['slots']):
            slot_label = meal_info['slot_labels'].get(slot_name, slot_name)
            items = slot_options.get(slot_name, [])
            
            # Prefix for tree-like display
            is_last_slot = (slot_idx == len(meal_info['slots']) - 1)
            prefix = "└─" if is_last_slot else "├─"
            item_prefix_start = "   " if is_last_slot else "│  "
            
            print(f"{prefix} {slot_label} ({len(items)} options):")
            
            if not items:
                print(f"{item_prefix_start}   (No options available)")
                continue
            
            for opt_idx, item in enumerate(items, 1):
                food_name = item.get('food_name', 'Unknown')
                energy = item.get('energy_kcal', 0)
                protein = item.get('protein_g', 0)
                
                print(f"{item_prefix_start}   {opt_idx}. {food_name}")
                print(f"{item_prefix_start}      Energy: {energy:.0f} kcal | Protein: {protein:.1f}g")
                
                # Optional: show more nutrients
                carbs = item.get('carbohydrate_g', 0)
                fat = item.get('fat_g', 0)
                if carbs > 0 or fat > 0:
                    print(f"{item_prefix_start}      Carbs: {carbs:.1f}g | Fat: {fat:.1f}g")
    
    print("\n" + "="*70 + "\n")



def display_fitness_details(solution: pd.DataFrame, guidelines: Dict):
    """
    Display fitness score breakdown (penalty per nutrient)
    
    Args:
        solution: DataFrame meal plan
        guidelines: Dict constraints
    """
    total_nutrition = calculate_total_nutrition(solution)
    total_penalty = fitness(solution, guidelines)
    
    print("\n⚖️  FITNESS BREAKDOWN:")
    print("─" * 70)
    
    nutrient_penalties = {}
    
    for nutrient_name, constraint in guidelines.items():
        if constraint.get('constraint_type') == 'unlimited':
            continue
        if nutrient_name not in total_nutrition:
            continue
        
        min_val = constraint.get('min', 0)
        max_val = constraint.get('max', float('inf'))
        value = total_nutrition[nutrient_name]
        
        penalty = 0
        status = "✓ OK"
        
        if value < min_val:
            penalty = min_val - value
            status = f"✗ LOW (need {min_val - value:.1f} more)"
        elif value > max_val:
            penalty = value - max_val
            status = f"✗ HIGH (excess {value - max_val:.1f})"
        
        nutrient_penalties[nutrient_name] = penalty
    
    # Show top violations
    violations = [(n, p) for n, p in nutrient_penalties.items() if p > 0]
    violations.sort(key=lambda x: x[1], reverse=True)
    
    if violations:
        print(f"Top violations:\n")
        for nutrient, penalty in violations[:5]:
            print(f"   {nutrient}: penalty = {penalty:.2f}")
    else:
        print(f"   No violations! All constraints satisfied ✓")
    
    print(f"\n   Total Penalty Score: {total_penalty:.2f}")

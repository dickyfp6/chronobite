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

# Mapping slot ke expected consumption_label
# Digunakan untuk filter makanan sesuai kategori konsumsi yang realistis
# HARUS MATCH dengan actual dataset labels: "Main Course", "Side Dish", "Drink", "Snack"
SLOT_LABEL_MAP = {
    0: 'Main Course',    # breakfast_main
    1: 'Side Dish',      # breakfast_side
    2: 'Drink',          # breakfast_drink
    3: 'Main Course',    # lunch_main
    4: 'Side Dish',      # lunch_side
    5: 'Drink',          # lunch_drink
    6: 'Main Course',    # dinner_main
    7: 'Side Dish',      # dinner_side
    8: 'Drink',          # dinner_drink
    9: 'Snack'           # snack
}

# Legacy: kept for reference (tidak digunakan lagi, gunakan consumption_label)
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

def _filter_food_by_slot(food_df: pd.DataFrame, slot_idx: int, debug: bool = False) -> pd.DataFrame:
    """
    Filter food items sesuai dengan expected consumption_label untuk slot tertentu
    Menggunakan case-insensitive comparison untuk robustness
    
    Args:
        food_df: DataFrame berisi semua food items dengan kolom 'consumption_label'
        slot_idx: Index slot (0-9)
        debug: Jika True, print info tentang filtering
    
    Returns:
        Filtered DataFrame atau fallback jika tidak ada match
        
    Logic:
        - Cek apakah ada kolom 'consumption_label' di dalam food_df
        - Ambil expected_label dari SLOT_LABEL_MAP[slot_idx]
        - Filter dengan case-insensitive comparison + strip
        - Fallback: return sample max 20 items jika tidak ada match
    """
    # Jika tidak ada consumption_label column, return semua items
    if 'consumption_label' not in food_df.columns:
        if debug:
            print(f"DEBUG: Slot {slot_idx} - No consumption_label column")
        return food_df
    
    # Ambil expected label untuk slot ini
    expected_label = SLOT_LABEL_MAP.get(slot_idx, None)
    if not expected_label:
        if debug:
            print(f"DEBUG: Slot {slot_idx} - No label mapping")
        return food_df
    
    # Filter items yang match expected label (case-insensitive with strip)
    filtered = cast(pd.DataFrame, food_df[
        food_df['consumption_label'].str.strip().str.lower() == expected_label.lower()
    ])
    
    if debug:
        print(f"DEBUG: Slot {slot_idx} ({SLOT_NAMES[slot_idx]}) -> label='{expected_label}' -> {len(filtered)} items")
        if len(filtered) == 0:
            print(f"       Available labels: {food_df['consumption_label'].unique().tolist()}")
    
    # Jika tidak ada match, sample dari original sebagai fallback
    if len(filtered) == 0:
        if debug:
            print(f"DEBUG: Slot {slot_idx} - No items found, using fallback (sampling max 20)")
        return food_df.sample(n=min(20, len(food_df)))
    
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
        - Untuk setiap slot (0-9), filter foods by consumption_label
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
    used_foods = set()  # Track used food_name untuk menghindari duplikasi jika mungkin
    
    # Generate 1 item per slot dengan food group filter jika tersedia
    for slot_idx in range(CHROMOSOME_SIZE):
        filtered_df = _filter_food_by_slot(food_df, slot_idx)
        
        # Sample 1 item untuk slot ini
        # Karena n=1, parameter replace tidak relevan
        if len(filtered_df) > 0:
            # Coba hindari duplikasi jika ada pilihan lain
            available_df = filtered_df
            if 'food_name' in filtered_df.columns and len(used_foods) > 0:
                # Filter out foods yang sudah digunakan jika masih ada pilihan
                not_used = filtered_df[~filtered_df['food_name'].isin(used_foods)]
                if len(not_used) > 0:
                    available_df = not_used
            
            item = available_df.sample(n=1)
            solution_items.append(item)
            
            # Track food yang digunakan
            if 'food_name' in item.columns:
                food_name = item.iloc[0].get('food_name', '')
                if food_name:
                    used_foods.add(food_name)
    
    # Concat semua items dan reset index
    if solution_items:
        solution = pd.concat(solution_items, ignore_index=True)
    else:
        # Fallback: jika semua filter gagal, random sample saja
        # Jika food_df < 10 items, allow replacement untuk mencapai 10 items
        allow_replacement = len(food_df) < CHROMOSOME_SIZE
        solution = food_df.sample(n=CHROMOSOME_SIZE, replace=allow_replacement).reset_index(drop=True)
    
    return solution


# ═════════════════════════════════════════════════════════════════════════════
# 2. CALCULATE TOTAL NUTRITION - Sum nutrisi dari 10 item (chromosome)
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

def fitness(solution: pd.DataFrame, guidelines: Dict, tdee: Optional[float] = None) -> float:
    """
    Hitung fitness score (penalty total) untuk 1 solusi (10-item chromosome)
    Dengan HARD dan SOFT constraints, weighted nutrients, duplicate penalty, dan normalization
    
    ⚠️  HARD vs SOFT:
        HARD (PRIMARY - disease-based + energy):
            - ENERGY: ±20% tolerance (0.8-1.2 × TDEE)
            - SODIUM, CHOLESTEROL, dll: 10x untuk under / 15x untuk over
            - Jika ada HARD violation ekstrem: +10000 hard stop penalty
        
        SOFT (SECONDARY - DRI-based):
            - Violation penalty: 1x normal weight
            - Contoh: Protein, Fiber dari DRI umum
            - Lebih fleksibel, tidak kritis
    
    Args:
        solution: DataFrame dengan 10 items (chromosome)
        guidelines: Dict struktur:
                   {
                       'hard': {nutrient: {'min': float, 'max': float, ...}, ...},
                       'soft': {nutrient: {'min': float, 'max': float, ...}, ...}
                   }
        tdee: Target daily energy expenditure (kcal) - untuk energy constraint
    
    Returns:
        float: Total penalty (semakin kecil = semakin baik)
    """
    # Hitung total nutrisi dari solution
    total_nutrition = calculate_total_nutrition(solution)
    
    total_penalty = 0.0
    constraint_count = 0
    
    # ════════════════════════════════════════════════════════════════════════
    # DETECT GUIDELINE STRUCTURE (HARD/SOFT atau LAMA)
    # ════════════════════════════════════════════════════════════════════════
    has_hard_soft = isinstance(guidelines.get(list(guidelines.keys())[0] if guidelines else None, None), dict) \
                    and 'hard' in guidelines and 'soft' in guidelines
    
    if has_hard_soft:
        hard_constraints = guidelines['hard']
        soft_constraints = guidelines['soft']
    else:
        # Backward compatibility: semua jadi SOFT
        hard_constraints = {}
        soft_constraints = guidelines
    
    # ════════════════════════════════════════════════════════════════════════
    # STEP 1: ENERGY CONSTRAINT - UTAMA SEKALI (HARD)
    # ════════════════════════════════════════════════════════════════════════
    if tdee and tdee > 0:
        current_energy = total_nutrition.get('energy_kcal', 0)
        
        # Tolerance: 80% - 120% dari TDEE
        min_energy = 0.8 * tdee
        max_energy = 1.2 * tdee
        
        if current_energy < min_energy:
            # Energi terlalu rendah - BESAR penalty (20x multiplier)
            energy_penalty = (min_energy - current_energy) * 20
            total_penalty += energy_penalty
        elif current_energy > max_energy:
            # Energi terlalu tinggi - penalty besar (15x multiplier)
            energy_penalty = (current_energy - max_energy) * 15
            total_penalty += energy_penalty
        
        constraint_count += 1
    
    # ════════════════════════════════════════════════════════════════════════
    # STEP 2: HARD CONSTRAINTS - PRIORITAS UTAMA (10x/15x penalty)
    # ════════════════════════════════════════════════════════════════════════
    for nutrient_name, constraint in hard_constraints.items():
        # Skip unlimited
        if constraint.get('constraint_type') == 'unlimited':
            continue
        
        # Skip jika nutrient tidak ada
        if nutrient_name not in total_nutrition:
            continue
        
        # Skip energy (sudah di-handle di STEP 1)
        if nutrient_name == 'energy_kcal':
            continue
        
        constraint_count += 1
        
        # Ambil nilai min dan max
        min_val = constraint.get('min', 0)
        max_val = constraint.get('max', float('inf'))
        value = total_nutrition[nutrient_name]
        
        # Get nutrient weight (default 1.0)
        weight = NUTRIENT_WEIGHTS.get(nutrient_name, 1.0)
        
        # HARD constraint penalty: lebih besar (10x untuk under, 15x untuk over)
        if value < min_val:
            penalty = (min_val - value) * weight * 10
            total_penalty += penalty
        elif value > max_val:
            penalty = (value - max_val) * weight * 15
            total_penalty += penalty
    
    # ════════════════════════════════════════════════════════════════════════
    # STEP 3: SOFT CONSTRAINTS - FLEXIBLE (1x normal penalty)
    # ════════════════════════════════════════════════════════════════════════
    for nutrient_name, constraint in soft_constraints.items():
        # Skip unlimited
        if constraint.get('constraint_type') == 'unlimited':
            continue
        
        # Skip jika nutrient tidak ada
        if nutrient_name not in total_nutrition:
            continue
        
        # Skip energy (sudah di-handle di STEP 1)
        if nutrient_name == 'energy_kcal':
            continue
        
        constraint_count += 1
        
        # Ambil nilai min dan max
        min_val = constraint.get('min', 0)
        max_val = constraint.get('max', float('inf'))
        value = total_nutrition[nutrient_name]
        
        # Get nutrient weight (default 1.0)
        weight = NUTRIENT_WEIGHTS.get(nutrient_name, 1.0)
        
        # SOFT constraint penalty: normal weight (tidak di-multiply)
        if value < min_val:
            penalty = (min_val - value) * weight
            total_penalty += penalty
        elif value > max_val:
            penalty = (value - max_val) * weight
            total_penalty += penalty
    
    # ════════════════════════════════════════════════════════════════════════
    # STEP 4: HARD STOP - Jika ada violation ekstrem di HARD constraint
    # ════════════════════════════════════════════════════════════════════════
    for nutrient_name, constraint in hard_constraints.items():
        max_val = constraint.get('max', float('inf'))
        value = total_nutrition.get(nutrient_name, 0)
        
        # Jika violation sangat ekstrem (>= 2x limit), add HARD STOP penalty
        if max_val != float('inf') and value > max_val * 2:
            total_penalty += 10000  # HARD STOP - ini buruk!
    
    # ════════════════════════════════════════════════════════════════════════
    # STEP 5: DUPLICATE PENALTY
    # ════════════════════════════════════════════════════════════════════════
    if 'food_name' in solution.columns:
        unique_foods = solution['food_name'].nunique()
        duplicate_count = len(solution) - unique_foods
        duplicate_penalty = duplicate_count * DUPLICATE_PENALTY_WEIGHT
        total_penalty += duplicate_penalty
    
    # ════════════════════════════════════════════════════════════════════════
    # STEP 6: NORMALIZE PENALTY
    # ════════════════════════════════════════════════════════════════════════
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
    tdee: Optional[float] = None,
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
        tdee: Target daily energy expenditure (kcal) - CRITICAL HARD constraint
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
        if tdee:
            print(f"Target TDEE: {tdee:.0f} kcal/day (HARD constraint)")
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
    best_fitness = fitness(best_solution, guidelines, tdee=tdee)
    
    # STEP 2: Main GA loop
    if verbose:
        print(f"[STEP 2] Running {generations} generations...")
        print(f"{'Gen':<5} | {'Best Fitness':<15} | {'Avg Fitness':<15}")
        print(f"{'-'*50}")
    
    for gen in range(generations):
        # 2a. Evaluate fitness semua population
        fitness_scores = []
        for solution in population:
            score = fitness(solution, guidelines, tdee=tdee)
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


def _calculate_nutrition_score(food_item: pd.Series) -> float:
    """
    Hitung nutrition score untuk food item
    
    Score = (0.6 * protein) + (0.3 * energy/100) - (0.1 * fat)
    
    Tujuan: Prioritas protein, energy, minimal fat
    
    Args:
        food_item: pd.Series dengan kolom energy_kcal, protein_g, fat_g
    
    Returns:
        float: Score (higher is better)
    """
    protein = food_item.get('protein_g', 0) or 0
    energy = food_item.get('energy_kcal', 0) or 0
    fat = food_item.get('fat_g', 0) or 0
    
    # Score: prioritas protein > energy > minimize fat
    score = (0.6 * protein) + (0.3 * energy / 100) - (0.1 * fat)
    
    return float(score)


def _apply_quality_filter(filtered: pd.DataFrame, expected_label: str) -> pd.DataFrame:
    """
    Apply quality filter untuk setiap food category
    
    Main Course: strict (energy >= 150, protein >= 5)
    Side Dish: moderate
    Drink: lenient
    Snack: lenient
    
    Args:
        filtered: DataFrame yang sudah filter by label
        expected_label: Label untuk slot (e.g., 'Main Course')
    
    Returns:
        Filtered DataFrame dengan quality constraints
    """
    if len(filtered) == 0:
        return filtered
    
    expected_lower = expected_label.strip().lower()
    
    # MAIN COURSE: STRICT quality filter untuk realistic main dishes
    if expected_lower == 'main course':
        # Main harus energy >= 200 kcal (sufficient) dan protein >= 8g (adequate protein)
        # Ini menghilangkan snack-like items seperti chestnut, pretzel
        filtered = cast(pd.DataFrame, filtered[
            (filtered['energy_kcal'] >= 200) &
            (filtered['protein_g'] >= 8)
        ])
    
    # SIDE DISH: Moderate filter (minimum nutrisi)
    elif expected_lower == 'side dish':
        # Side minimal protein >= 2g (biar ada nutrisi)
        filtered = cast(pd.DataFrame, filtered[filtered['protein_g'] >= 2])
    
    # DRINK & SNACK: Lenient, terima saja
    
    return filtered


def generate_meal_options(
    food_df: pd.DataFrame,
    top_solutions: List[pd.DataFrame],
    max_options_per_slot: int = 3,
    food_preferences: Optional[List[str]] = None
) -> Dict[str, List[pd.Series]]:
    """
    Generate 2-3 opsi menu per slot yang beragam dan tidak duplikat.
    
    Strategy SEDERHANA:
    1. Kumpulkan items dari top_solutions untuk setiap slot → basis utama
    2. Tambah variasi dari dataset dengan filtering konsumsi label
    3. Hilangkan duplikat per slot (by food_name)
    4. Hindari duplikasi global (across slots) dengan tracking used_foods
    5. Shuffle ringan untuk variasi
    6. Ambil 3 opsi pertama
    
    Args:
        food_df: DataFrame semua food items
        top_solutions: List of top 10 meal plans dari GA
        max_options_per_slot: Jumlah pilihan per slot (default 3)
        food_preferences: List of preferred cuisines (e.g., ['Asian', 'Western'])
    
    Returns:
        Dict[slot_name: [option1, option2, option3], ...]
    
    Example:
        best_sol, top_sols = run_ga(food_df, guidelines)
        options = generate_meal_options(food_df, top_sols, max_options_per_slot=3)
    """
    
    slot_options = {slot: [] for slot in SLOT_NAMES}
    used_foods = set()  # Track makanan yang sudah dipakai (hindari duplikasi global)
    
    # Prepare cuisine preferences
    if food_preferences and len(food_preferences) > 0:
        allowed_cuisine = food_preferences + ['Generic']
        allowed_cuisine = list(set(allowed_cuisine))
    else:
        allowed_cuisine = None
    
    # ════════════════════════════════════════════════════════════════════════
    # LOOP SETIAP SLOT
    # ════════════════════════════════════════════════════════════════════════
    for slot_idx in range(CHROMOSOME_SIZE):
        slot_name = SLOT_NAMES[slot_idx]
        expected_label = SLOT_LABEL_MAP[slot_idx]
        
        # ────────────────────────────────────────────────────────────────────
        # STEP 1: Kumpulkan items dari top_solutions
        # ────────────────────────────────────────────────────────────────────
        candidates = []
        
        for solution in top_solutions:
            if slot_idx < len(solution):
                item = solution.iloc[slot_idx]
                candidates.append(item)
        
        # ────────────────────────────────────────────────────────────────────
        # STEP 2: Tambah variasi dari dataset
        # ────────────────────────────────────────────────────────────────────
        dataset_items = food_df[
            food_df['consumption_label'].str.strip().str.lower() == expected_label.lower()
        ]
        
        # Filter by cuisine jika ada preference
        if allowed_cuisine and 'cuisine' in dataset_items.columns:
            dataset_items = dataset_items[dataset_items['cuisine'].isin(allowed_cuisine)]
        
        # Sample max 20 items dari dataset untuk variasi
        if len(dataset_items) > 20:
            dataset_items = dataset_items.sample(n=20, random_state=None)
        
        # Gabungkan candidates + dataset items (convert to Series list)
        for idx, row in dataset_items.iterrows():
            candidates.append(row)  # row is already a pd.Series
        
        # ────────────────────────────────────────────────────────────────────
        # STEP 3: Hilangkan duplikat per slot (by food_name)
        # ────────────────────────────────────────────────────────────────────
        unique_dict = {}
        for item in candidates:
            # Safe extraction dari Series
            item_name = item.get('food_name', '') if isinstance(item, pd.Series) else getattr(item, 'food_name', '')
            if item_name and item_name not in unique_dict:
                unique_dict[item_name] = item
        
        candidates = list(unique_dict.values())
        
        # ────────────────────────────────────────────────────────────────────
        # STEP 4: Hindari duplikasi global (dengan exception untuk Drinks)
        # ────────────────────────────────────────────────────────────────────
        # LOGIC: Strict untuk Main Course/Side Dish, tapi RELAX untuk Drink/Snack
        # Alasan: Realistis bahwa user bisa minum hal yang sama di berbagai waktu,
        #         tapi unlikely makan exact same main course di multiple slots
        # ────────────────────────────────────────────────────────────────────
        filtered_candidates = []
        is_drink_or_snack = expected_label.lower() in ['drink', 'snack']
        
        for item in candidates:
            # Safe extraction dari Series
            item_name = item.get('food_name', '') if isinstance(item, pd.Series) else getattr(item, 'food_name', '')
            
            # Untuk Drink/Snack: RELAX global dedup (allow reuse)
            # Untuk Main Course/Side Dish: STRICT global dedup (no reuse)
            if item_name:
                if is_drink_or_snack or item_name not in used_foods:
                    filtered_candidates.append(item)
        
        candidates = filtered_candidates
        
        # ────────────────────────────────────────────────────────────────────
        # STEP 5: Shuffle ringan untuk variasi
        # ────────────────────────────────────────────────────────────────────
        random.shuffle(candidates)
        
        # ────────────────────────────────────────────────────────────────────
        # STEP 6: Ambil 3 opsi pertama
        # ────────────────────────────────────────────────────────────────────
        final_options = candidates[:max_options_per_slot]
        
        # Ensure semua adalah pd.Series untuk konsistensi
        final_options_series = []
        for opt in final_options:
            if isinstance(opt, pd.Series):
                opt_series = opt
            else:
                opt_series = pd.Series(opt)
            
            final_options_series.append(opt_series)
            
            # Track makanan yang dipakai HANYA untuk Main Course/Side Dish
            # Drink/Snack: DON'T track (allow reuse untuk realism)
            if not is_drink_or_snack:
                item_name = opt_series.get('food_name', '')
                if item_name:
                    used_foods.add(item_name)
        
        slot_options[slot_name] = final_options_series
    
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
    Display fitness score breakdown (penalty per nutrient dengan weights)
    Gunakan weighted calculation sama seperti di fitness() function
    
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
        
        # Get nutrient weight (sama seperti di fitness())
        weight = NUTRIENT_WEIGHTS.get(nutrient_name, 1.0)
        
        penalty = 0
        status = "✓ OK"
        
        if value < min_val:
            # Kurang dari minimum dengan weight
            penalty = (min_val - value) * weight
            status = f"✗ LOW (need {min_val - value:.1f} more)"
        elif value > max_val:
            # Lebih dari maximum dengan weight
            penalty = (value - max_val) * weight
            status = f"✗ HIGH (excess {value - max_val:.1f})"
        
        nutrient_penalties[nutrient_name] = penalty
    
    # Show top violations
    violations = [(n, p) for n, p in nutrient_penalties.items() if p > 0]
    violations.sort(key=lambda x: x[1], reverse=True)
    
    if violations:
        print(f"Top violations (with weights):\n")
        for nutrient, penalty in violations[:5]:
            weight = NUTRIENT_WEIGHTS.get(nutrient, 1.0)
            print(f"   {nutrient} (weight={weight}): penalty = {penalty:.2f}")
    else:
        print(f"   No violations! All constraints satisfied ✓")
    
    print(f"\n   Total Penalty Score: {total_penalty:.2f}")


# ═════════════════════════════════════════════════════════════════════════════
# 7. CALCULATE PORTION SIZES - Hitung gram dinamis berdasarkan target energi
# ═════════════════════════════════════════════════════════════════════════════

def calculate_portion_sizes_dynamic(
    selected_df: pd.DataFrame,
    TDEE: float,
    guidelines: Optional[Dict] = None
) -> pd.DataFrame:
    """
    Calculate portion sizes (grams) dengan MEAL-BASED DISTRIBUTION & DEFICIT-AWARE WEIGHTING.
    
    Algoritma v3 - SOPHISTICATED:
        1. Meal distribution: Breakfast 25%, Lunch 35%, Dinner 30%, Snack 10%
        2. Calculate totals @ 100g
        3. Calculate deficit (kekurangan vs target minimum)
        4. Deficit-aware weight: prioritize nutrients yang kurang
        5. Label adjustment: Snack 0.3x, Drink 0.5x, Side 0.8x, Main 1.0x
        6. Normalize weights per meal
        7. Distribute energy per meal
        8. Calculate gram
        9. Clamp realistic
        10. Renormalize setelah clamp untuk match target
    
    Tujuan:
        - Snack tidak dominan
        - Protein tidak over
        - Carb tidak drop
        - Distribusi meal realistis
        - Compliance meningkat
    
    Args:
        selected_df: DataFrame 10 selected meal items (index 0-9)
        TDEE: Total daily energy expenditure (kcal)
        guidelines: Optional dict dari NutritionService (untuk target nutrient)
    
    Returns:
        DataFrame dengan kolom: gram, final_energy_kcal, final_protein_g, dll
    """
    
    # Meal distribution ratios
    meal_ratio = {
        'breakfast': 0.25,
        'lunch': 0.35,
        'dinner': 0.30,
        'snack': 0.10
    }
    
    # Mapping slot index ke meal type
    slot_to_meal = {
        0: 'breakfast', 1: 'breakfast', 2: 'breakfast',
        3: 'lunch', 4: 'lunch', 5: 'lunch',
        6: 'dinner', 7: 'dinner', 8: 'dinner',
        9: 'snack'
    }
    
    # Gram constraints realistic
    gram_constraints = {
        'Main Course': (100, 300),
        'Side Dish': (50, 150),
        'Drink': (150, 300),
        'Snack': (30, 100)
    }
    
    # Label adjustment factors
    label_adjustments = {
        'Main Course': 1.0,
        'Side Dish': 0.8,
        'Drink': 0.5,
        'Snack': 0.3
    }
    
    # Extract guideline targets if provided
    if guidelines:
        target_protein_min = guidelines.get('protein_g', {}).get('min', 60)
        target_fat_min = guidelines.get('fat_g', {}).get('min', 50)
        target_carb_min = guidelines.get('carbohydrate_g', {}).get('min', 250)
    else:
        target_protein_min = 60
        target_fat_min = 50
        target_carb_min = 250
    
    # Copy dataframe
    result_df = selected_df.copy()
    result_df['gram'] = 0.0
    
    # Nutrients to scale
    nutrients_to_scale = [
        'energy_kcal', 'protein_g', 'carbohydrate_g', 'fat_g', 'fiber_g',
        'sodium_mg', 'calcium_mg', 'iron_mg', 'phosphorus_mg', 'zinc_mg',
        'potassium_mg', 'magnesium_mg', 'vitamin_a_iu', 'vitamin_c_mg',
        'vitamin_b1_mg', 'vitamin_b2_mg', 'vitamin_b3_mg', 'cholesterol_mg'
    ]
    
    for nutrient in nutrients_to_scale:
        result_df[f'final_{nutrient}'] = 0.0
    
    # ════════════════════════════════════════════════════════════════════════
    # STEP 1-2: Calculate totals @ 100g
    # ════════════════════════════════════════════════════════════════════════
    total_energy = 0.0
    total_protein = 0.0
    total_fat = 0.0
    total_carb = 0.0
    
    for idx in range(len(result_df)):
        item = result_df.iloc[idx]
        total_energy += item.get('energy_kcal', 0) or 0
        total_protein += item.get('protein_g', 0) or 0
        total_fat += item.get('fat_g', 0) or 0
        total_carb += item.get('carbohydrate_g', 0) or 0
    
    if total_energy <= 0: total_energy = 1
    if total_protein <= 0: total_protein = 1
    if total_fat <= 0: total_fat = 1
    if total_carb <= 0: total_carb = 1
    
    # ════════════════════════════════════════════════════════════════════════
    # STEP 3: Calculate deficit (kekurangan vs target)
    # ════════════════════════════════════════════════════════════════════════
    protein_need = max(0, target_protein_min - total_protein)
    fat_need = max(0, target_fat_min - total_fat)
    carb_need = max(0, target_carb_min - total_carb)
    
    # Boost factors untuk nutrients yang kurang
    protein_boost = 1.0 if protein_need > 0 else 0.3
    fat_boost = 1.0 if fat_need > 0 else 0.3
    carb_boost = 1.0 if carb_need > 0 else 1.2
    
    # ════════════════════════════════════════════════════════════════════════
    # STEP 4-6: Calculate weights (deficit-aware) + label adjustment + normalize per meal
    # ════════════════════════════════════════════════════════════════════════
    
    weights_per_meal = {meal: [] for meal in meal_ratio.keys()}
    
    for idx in range(len(result_df)):
        item = result_df.iloc[idx]
        
        energy = item.get('energy_kcal', 0) or 0
        protein = item.get('protein_g', 0) or 0
        fat = item.get('fat_g', 0) or 0
        carb = item.get('carbohydrate_g', 0) or 0
        
        # STEP 4: Deficit-aware weight
        weight_raw = (
            0.4 * (energy / total_energy) +
            0.3 * (protein / total_protein) * protein_boost +
            0.2 * (fat / total_fat) * fat_boost +
            0.1 * (carb / total_carb) * carb_boost
        )
        
        # STEP 5: Label adjustment
        label = item.get('consumption_label', 'Main Course')
        if isinstance(label, str):
            label = label.strip()
        
        adjustment = label_adjustments.get(label, 1.0)
        weight_adjusted = weight_raw * adjustment
        
        # STEP 6: Store untuk normalisasi per meal
        meal_type = slot_to_meal.get(idx, 'snack')
        weights_per_meal[meal_type].append((idx, weight_adjusted, label, energy))
    
    # ════════════════════════════════════════════════════════════════════════
    # STEP 7-10: Normalize per meal, distribute energy, calc gram, clamp, renormalize
    # ════════════════════════════════════════════════════════════════════════
    
    for meal_type, ratio in meal_ratio.items():
        # Target energy untuk meal ini
        target_meal_energy = TDEE * ratio
        
        # Get items untuk meal ini
        meal_items = weights_per_meal[meal_type]
        if not meal_items:
            continue
        
        # Normalize weights per meal
        total_weight_meal = sum(w for _, w, _, _ in meal_items)
        if total_weight_meal <= 0:
            total_weight_meal = 1
        
        normalized_weights = [(w / total_weight_meal) for _, w, _, _ in meal_items]
        
        # First pass: calculate grams
        grams_first_pass = []
        meal_energy_first = 0
        
        for (idx, weight_adj, label, energy), norm_weight in zip(meal_items, normalized_weights):
            # STEP 7: Distribute energy per meal
            target_energy_item = norm_weight * target_meal_energy
            
            # STEP 8: Calculate gram
            energy_per_100g = energy or 1
            gram = (target_energy_item / energy_per_100g) * 100
            
            # STEP 9: Clamp realistic
            min_g, max_g = gram_constraints.get(label, (50, 150))
            gram_clamped = np.clip(gram, min_g, max_g)
            
            grams_first_pass.append((idx, gram_clamped, energy_per_100g))
            meal_energy_first += energy_per_100g * gram_clamped / 100
        
        # STEP 10: Renormalize setelah clamp untuk match target meal energy
        if meal_energy_first > 0:
            scale = target_meal_energy / meal_energy_first
        else:
            scale = 1.0
        
        for idx, gram_clamped, energy_per_100g in grams_first_pass:
            gram_final = gram_clamped * scale
            result_df.at[idx, 'gram'] = round(gram_final, 1)
            
            # Calculate final nutrients
            item = result_df.iloc[idx]
            for nutrient in nutrients_to_scale:
                if nutrient in item.index:
                    value_per_100g = item.get(nutrient, 0) or 0
                    final_value = value_per_100g * gram_final / 100
                    result_df.at[idx, f'final_{nutrient}'] = round(final_value, 2)
    
    # ════════════════════════════════════════════════════════════════════════
    # NEW: HARD STOP CONTROL - SODIUM & CHOLESTEROL
    # ════════════════════════════════════════════════════════════════════════
    # Jika ada HARD constraint violation, scale down semua portions
    
    # Check HARD constraints from guidelines
    if guidelines and isinstance(guidelines, dict) and 'hard' in guidelines:
        hard_constraints = guidelines['hard']
        
        # ────────────────────────────────────────────────────────────────────
        # SODIUM CONTROL
        # ────────────────────────────────────────────────────────────────────
        if 'sodium_mg' in hard_constraints:
            sodium_limit = hard_constraints['sodium_mg'].get('max', float('inf'))
            total_sodium = result_df['final_sodium_mg'].sum()
            
            if total_sodium > sodium_limit and sodium_limit != float('inf'):
                # Scale down grams untuk match sodium limit
                scale_sodium = sodium_limit / total_sodium
                result_df['gram'] *= scale_sodium
                
                # Recalculate final nutrients dengan scaled gram
                for idx in range(len(result_df)):
                    item = result_df.iloc[idx]
                    gram = result_df.at[idx, 'gram']
                    
                    for nutrient in nutrients_to_scale:
                        if nutrient in item.index:
                            value_per_100g = item.get(nutrient, 0) or 0
                            final_value = value_per_100g * gram / 100
                            result_df.at[idx, f'final_{nutrient}'] = round(final_value, 2)
        
        # ────────────────────────────────────────────────────────────────────
        # CHOLESTEROL CONTROL
        # ────────────────────────────────────────────────────────────────────
        if 'cholesterol_mg' in hard_constraints:
            chol_limit = hard_constraints['cholesterol_mg'].get('max', float('inf'))
            total_chol = result_df['final_cholesterol_mg'].sum()
            
            if total_chol > chol_limit and chol_limit != float('inf'):
                # Scale down grams untuk match cholesterol limit
                scale_chol = chol_limit / total_chol
                result_df['gram'] *= scale_chol
                
                # Recalculate final nutrients dengan scaled gram
                for idx in range(len(result_df)):
                    item = result_df.iloc[idx]
                    gram = result_df.at[idx, 'gram']
                    
                    for nutrient in nutrients_to_scale:
                        if nutrient in item.index:
                            value_per_100g = item.get(nutrient, 0) or 0
                            final_value = value_per_100g * gram / 100
                            result_df.at[idx, f'final_{nutrient}'] = round(final_value, 2)
    
    return result_df


def display_portion_summary_dynamic(portion_df: pd.DataFrame, guidelines: Dict, TDEE: float):
    """
    Display portion sizing hasil dengan detail per meal (v3 - SOPHISTICATED)
    
    Algorithm yang ditampilkan:
    1. Meal distribution: Breakfast 25%, Lunch 35%, Dinner 30%, Snack 10%
    2. Calculate totals @ 100g
    3. Calculate deficit (kekurangan vs target)
    4. Deficit-aware weight: boost nutrients yang kurang
    5. Label adjustment: Snack 0.3x, Drink 0.5x, Side 0.8x, Main 1.0x
    6. Normalize per meal
    7. Distribute energy per meal
    8. Clamp realistic
    9. Renormalize setelah clamp untuk match target
    10. Final nutrition summary
    
    Args:
        portion_df: DataFrame hasil calculate_portion_sizes_dynamic()
        guidelines: Dict dengan constraint min/max per nutrient
        TDEE: Total daily energy expenditure (untuk reference)
    """
    print("\n" + "="*70)
    print("STEP 9: PORTION SIZING - MEAL-BASED + DEFICIT-AWARE (v3)")
    print("="*70)
    
    print(f"\n📐 SOPHISTICATED ALGORITHM:")
    print(f"  1. Meal distribution: Breakfast 25% | Lunch 35% | Dinner 30% | Snack 10% of TDEE")
    print(f"  2. Totals @ 100g: Energy {portion_df['energy_kcal'].sum():.0f}kcal | Protein {portion_df['protein_g'].sum():.1f}g | Fat {portion_df['fat_g'].sum():.1f}g | Carb {portion_df['carbohydrate_g'].sum():.1f}g")
    print(f"  3. Calculate deficit vs targets (Protein>{guidelines.get('protein_g', {}).get('min', 60)}, Fat>{guidelines.get('fat_g', {}).get('min', 50)}, Carb>{guidelines.get('carbohydrate_g', {}).get('min', 250)})")
    print(f"  4. Weight = 40% energy + 30% protein(×boost) + 20% fat(×boost) + 10% carb(×boost)")
    print(f"  5. Label adjustment: Main 1.0x | Side 0.8x | Drink 0.5x | Snack 0.3x")
    print(f"  6. Normalize weights per meal")
    print(f"  7. Distribute energy: Target_meal = TDEE × meal_ratio")
    print(f"  8. Clamp: Main 100-300g | Side 50-150g | Drink 150-300g | Snack 30-100g")
    print(f"  9. Renormalize setelah clamp untuk match target_meal_energy")
    
    print(f"\n📊 YOUR PERSONALIZED MEAL PORTIONS:")
    print(f"─" * 70)
    
    # Display by meal type
    meal_display_order = [
        ('breakfast', '🌅 BREAKFAST', [0, 1, 2]),
        ('lunch', '☀️ LUNCH', [3, 4, 5]),
        ('dinner', '🌙 DINNER', [6, 7, 8]),
        ('snack', '🍪 SNACK', [9])
    ]
    
    meal_totals = {}
    
    for meal_name, meal_emoji, indices in meal_display_order:
        print(f"\n{meal_emoji}")
        print(f"─" * 70)
        
        meal_energy = 0
        meal_protein = 0
        meal_items = []
        
        for idx in indices:
            if idx >= len(portion_df):
                continue
            
            item = portion_df.iloc[idx]
            
            food_name = item.get('food_name', f'Item {idx}')
            gram = item.get('gram', 0)
            final_energy = item.get('final_energy_kcal', 0)
            final_protein = item.get('final_protein_g', 0)
            final_carbs = item.get('final_carbohydrate_g', 0)
            final_fat = item.get('final_fat_g', 0)
            label = item.get('consumption_label', 'Unknown')
            
            meal_items.append({
                'name': food_name,
                'gram': gram,
                'label': label,
                'energy': final_energy,
                'protein': final_protein,
                'carbs': final_carbs,
                'fat': final_fat
            })
            
            meal_energy += final_energy
            meal_protein += final_protein
            
            # Display item
            print(f"  • {food_name[:40]}")
            print(f"    Label: {label} | Portion: {gram:.0f}g")
            print(f"    Energy: {final_energy:.0f} kcal | Protein: {final_protein:.1f}g | Carbs: {final_carbs:.1f}g | Fat: {final_fat:.1f}g")
        
        meal_totals[meal_name] = {
            'energy': meal_energy,
            'protein': meal_protein,
            'items': meal_items
        }
    
    # Display daily totals
    print(f"\n" + "="*70)
    print(f"📈 DAILY NUTRITION SUMMARY:")
    print(f"─" * 70)
    
    total_energy = portion_df['final_energy_kcal'].sum()
    total_protein = portion_df['final_protein_g'].sum()
    total_carbs = portion_df['final_carbohydrate_g'].sum()
    total_fat = portion_df['final_fat_g'].sum()
    total_fiber = portion_df['final_fiber_g'].sum()
    total_sodium = portion_df['final_sodium_mg'].sum()
    
    for meal_name, meal_emoji, _ in meal_display_order:
        if meal_name in meal_totals:
            energy = meal_totals[meal_name]['energy']
            protein = meal_totals[meal_name]['protein']
            print(f"  {meal_emoji} {meal_name.upper():10}: {energy:6.0f} kcal | {protein:5.1f}g protein")
    
    print(f"\n  {'─'*66}")
    print(f"  {'TOTAL':10}: {total_energy:6.0f} kcal | {total_protein:5.1f}g protein")
    print(f"              {total_carbs:6.1f}g carbs | {total_fat:6.1f}g fat | {total_sodium:6.0f}mg sodium")
    
    # Show compliance vs target
    print(f"\n📋 COMPLIANCE vs GUIDELINES:")
    print(f"─" * 70)
    
    # Key nutrients for compliance check
    key_checks = [
        ('energy_kcal', total_energy, 'kcal'),
        ('protein_g', total_protein, 'g'),
        ('carbohydrate_g', total_carbs, 'g'),
        ('fat_g', total_fat, 'g'),
        ('sodium_mg', total_sodium, 'mg'),
    ]
    
    compliant_count = 0
    total_checks = 0
    
    for nutrient, actual_val, unit in key_checks:
        constraint = guidelines.get(nutrient, {})
        min_val = constraint.get('min', 0)
        max_val = constraint.get('max', float('inf'))
        
        total_checks += 1
        is_compliant = min_val <= actual_val <= max_val
        
        if is_compliant:
            compliant_count += 1
            status = "✓"
        else:
            status = "✗"
        
        print(f"  {status} {nutrient:20}: {actual_val:8.1f} {unit:3} (Target: {min_val:7.0f} - {max_val:7.0f} {unit})")
    
    compliance_pct = (compliant_count / total_checks * 100) if total_checks > 0 else 0
    print(f"\n  💯 Compliance Rate: {compliance_pct:.0f}% ({compliant_count}/{total_checks})")
    print(f"  🎯 Target TDEE: {TDEE:.0f} kcal | Actual: {total_energy:.0f} kcal | Δ: {abs(total_energy - TDEE):.0f} kcal")
    
    print(f"\n" + "="*70 + "\n")

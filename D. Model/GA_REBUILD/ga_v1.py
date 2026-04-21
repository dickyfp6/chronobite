"""
GENETIC ALGORITHM - Simple Implementation v1
============================================

Core GA engine untuk meal planning optimization.
Mencari kombinasi 4 makanan (breakfast, lunch, dinner, snack) yang memenuhi
constraint nutrisi dengan penalty minimal.

Struktur Sederhana:
- Solution = 1 baris DataFrame (1 makanan) × 4 baris = 4 makanan sehari
- Fitness = Total penalty terhadap nutrient constraints
- GA Loop = Initialize → Evaluate → Select → Crossover → Mutate → Repeat

Tanpa class, hanya functions murni.
"""

import pandas as pd
import numpy as np
import random
from typing import List, Dict, Tuple, Optional, cast


# ═════════════════════════════════════════════════════════════════════════════
# 1. RANDOM SOLUTION - Generate meal plan random
# ═════════════════════════════════════════════════════════════════════════════

def random_solution(food_df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate 1 solusi random = 4 makanan random dari food_df
    
    Args:
        food_df: DataFrame berisi semua food items
    
    Returns:
        DataFrame dengan 4 baris (1 meal per baris)
    
    Example:
        solution = random_solution(food_df)
        # output: DataFrame dengan 4 rows
        #   food_name     energy_kcal  protein_g  ...
        # 0  Nasi Putih     180          3.6       ...
        # 1  Tahu Goreng    150          15        ...
        # 2  Rendang...     250          20        ...
        # 3  Teh Manis      50           0         ...
    """
    if len(food_df) < 4:
        raise ValueError(f"Food database harus memiliki ≥4 items, got {len(food_df)}")
    
    # Random select 4 makanan (dengan replacement = boleh duplikat)
    solution = food_df.sample(n=4, replace=True).reset_index(drop=True)
    return solution


# ═════════════════════════════════════════════════════════════════════════════
# 2. CALCULATE TOTAL NUTRITION - Sum nutrisi dari 4 makanan
# ═════════════════════════════════════════════════════════════════════════════

def calculate_total_nutrition(solution: pd.DataFrame) -> Dict[str, float]:
    """
    Hitung total nutrisi dari 4 makanan dalam solution
    
    Args:
        solution: DataFrame dengan 4 baris food items
    
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
    Hitung fitness score (penalty total) untuk 1 solusi
    
    Args:
        solution: DataFrame dengan 4 food items
        guidelines: Dict dari NutritionService
                   {nutrient: {'min': float, 'max': float, ...}, ...}
    
    Returns:
        float: Total penalty (semakin kecil = semakin baik)
               0 = perfectly match guidelines
    
    Logic:
        1. Hitung total nutrisi dari 4 makanan
        2. Untuk setiap nutrient dalam guidelines:
           - Jika value < min → penalty += (min - value)
           - Jika value > max → penalty += (value - max)
           - Jika min ≤ value ≤ max → no penalty
        3. Return total penalty
    
    Example:
        guidelines = {
            'energy_kcal': {'min': 1800, 'max': 2200, ...},
            'protein_g': {'min': 60, 'max': 100, ...}
        }
        
        solution_nutrition = {'energy_kcal': 1900, 'protein_g': 50, ...}
        
        Penalties:
        - energy_kcal: 1800 ≤ 1900 ≤ 2200 → 0
        - protein_g: 50 < 60 → penalty = 60 - 50 = 10
        
        Total penalty = 10
    """
    # Hitung total nutrisi dari solution
    total_nutrition = calculate_total_nutrition(solution)
    
    total_penalty = 0.0
    
    # Iterate setiap nutrient constraint
    for nutrient_name, constraint in guidelines.items():
        # Skip jika constraint type unlimited
        if constraint.get('constraint_type') == 'unlimited':
            continue
        
        # Skip jika nutrient tidak ada di food database
        if nutrient_name not in total_nutrition:
            continue
        
        # Ambil nilai min dan max
        min_val = constraint.get('min', 0)
        max_val = constraint.get('max', float('inf'))
        value = total_nutrition[nutrient_name]
        
        # Hitung penalty
        if value < min_val:
            # Kurang dari minimum
            penalty = min_val - value
            total_penalty += penalty
        elif value > max_val:
            # Lebih dari maximum
            penalty = value - max_val
            total_penalty += penalty
        # else: dalam range, no penalty
    
    return total_penalty


# ═════════════════════════════════════════════════════════════════════════════
# 4. CROSSOVER - Single-point crossover antara 2 parent
# ═════════════════════════════════════════════════════════════════════════════

def crossover(parent1: pd.DataFrame, parent2: pd.DataFrame) -> pd.DataFrame:
    """
    Single-point crossover: ambil N baris dari parent1, M dari parent2
    
    Args:
        parent1: Solution (DataFrame 4 rows)
        parent2: Solution (DataFrame 4 rows)
    
    Returns:
        Child: DataFrame hasil kombinasi parent1 + parent2
    
    Method:
        1. Random pilih crossover point (1-3)
           point = 1 → child = [P1[0] + P2[1,2,3]]
           point = 2 → child = [P1[0,1] + P2[2,3]]
           point = 3 → child = [P1[0,1,2] + P2[3]]
        2. Konkatenasi dan reset index
    
    Example:
        P1 = [Nasi, Tahu, Rendang, Teh]
        P2 = [Roti, Telur, Ayam, Kopi]
        
        Point = 2:
        Child = [Nasi, Tahu] + [Ayam, Kopi] = [Nasi, Tahu, Ayam, Kopi]
    """
    # Ensure diameter = 4
    assert len(parent1) == 4, "Parent1 harus 4 rows"
    assert len(parent2) == 4, "Parent2 harus 4 rows"
    
    # Random crossover point (1-3)
    point = random.randint(1, 3)
    
    # Ambil N baris dari parent1, sisa dari parent2
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
    Mutation: Replace 1 random item dalam solution dengan food baru dari food_df
    
    Args:
        solution: DataFrame (4 rows)
        food_df: Semua available food items
        mutation_rate: Probability untuk apply mutation (default 0.3 = 30%)
    
    Returns:
        Mutated solution (atau original jika no mutation)
    
    Method:
        1. Jika random() > mutation_rate → return original (no mutation)
        2. Else:
           - Random select 1 index (0-3)
           - Random select 1 food dari food_df
           - Replace row tersebut
           - Return mutated copy
    """
    # Check jika ada mutation
    if random.random() > mutation_rate:
        return solution.copy()
    
    # Ada mutation
    result = solution.copy()
    
    # Random select 1 index to mutate (0-3)
    idx = random.randint(0, 3)
    
    # Random select 1 food dari food_df
    new_food = food_df.sample(n=1).reset_index(drop=True)
    
    # Replace
    result.iloc[idx] = new_food.iloc[0]
    
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
) -> Tuple[pd.DataFrame, float]:
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
        Tuple: (best_solution, best_fitness)
               best_solution: DataFrame optimal meal plan
               best_fitness: float penalty score terbaik
    
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
        
        Return: best individual dari semua generasi
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
    
    # STEP 3: Return best solution found
    if verbose:
        print(f"{'='*50}")
        print(f"[STEP 3] GA Complete!")
        print(f"Best Fitness Score: {best_fitness:.2f}")
        print(f"{'='*50}\n")
    
    return best_solution, best_fitness


# ═════════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═════════════════════════════════════════════════════════════════════════════

def display_solution(solution: pd.DataFrame, guidelines: Optional[Dict] = None):
    """
    Display meal plan secara readable
    
    Args:
        solution: DataFrame 4 food items
        guidelines: Optional, untuk display constraint values
    """
    meals = ['Breakfast', 'Lunch', 'Dinner', 'Snack']
    
    print("\n📋 MEAL PLAN:")
    print("─" * 70)
    
    for i, meal_name in enumerate(meals):
        food_row = solution.iloc[i]
        print(f"\n{i+1}. {meal_name}:")
        print(f"   Food: {food_row.get('food_name', 'Unknown')}")
        print(f"   Energy: {food_row.get('energy_kcal', 0):.0f} kcal")
    
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

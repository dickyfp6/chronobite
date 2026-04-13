"""
GENETIC ALGORITHM OPTIMIZER WITH CATEGORY CONSTRAINTS
GA yang respect kategori makanan untuk menu yang realistis

Fitur:
- Chromosome dengan kategori yang ketat
- Population initialization yang respect kategori
- Mutation yang maintain kategori
- Crossover yang intelligent
- Fitness calculation yang fair

Key differences dari GA biasa:
- Tidak bisa memilih food arbitrary dari database
- Setiap kategori punya pool sendiri
- Hasil menu selalu realistis (main + side + drink per meal)
"""

import random
import numpy as np
from typing import Dict, List, Tuple, Optional
import pandas as pd

from ga_chromosome_with_categories import (
    FoodCategoryManager,
    CategorizedChromosome
)
from ga_fitness_improved import ImprovedFitnessCalculator


class CategorizedGeneticAlgorithmOptimizer:
    """
    GA Optimizer dengan kategori constraint
    
    Memastikan menu yang dihasilkan realistis dan following food category rules
    """
    
    def __init__(
        self,
        food_database: pd.DataFrame,
        nutrition_targets: Dict,
        user_preferences: Optional[Dict] = None,
        population_size: int = 50,
        generations: int = 100,
        mutation_rate: float = 0.1,
        crossover_rate: float = 0.8,
        elite_fraction: float = 0.1,
        verbose: bool = True
    ):
        """
        Initialize GA dengan category constraints
        
        Args:
            food_database: DataFrame dengan kolom food_category
            nutrition_targets: Target nutrisi (tdee, protein_target, dsb)
            user_preferences: {'cuisine': ['indonesian', 'western'], ...}
            population_size: Jumlah solusi per generasi
            generations: Jumlah generasi
            mutation_rate: Probability mutation per food (0.0-1.0)
            crossover_rate: Probability crossover (0.0-1.0)
            elite_fraction: Fraction untuk elitism (0.0-1.0)
            verbose: Print progress
        """
        self.food_database = food_database
        self.nutrition_targets = nutrition_targets
        self.user_preferences = user_preferences or {}
        
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elite_fraction = elite_fraction
        self.verbose = verbose
        
        # Initialize category manager
        self.category_manager = FoodCategoryManager(food_database)
        
        # Apply cuisine filter jika ada preference
        if 'cuisine' in self.user_preferences:
            cuisine_list = self.user_preferences.get('cuisine', [])
            if cuisine_list:
                self.category_manager = self.category_manager.filter_by_cuisine(cuisine_list)
        
        # GA state
        self.best_solution = None
        self.best_fitness = -float('inf')
        self.population = []
        self.fitness_scores = []
        self.fitness_history = []
    
    def optimize(self) -> Tuple[Dict, float]:
        """
        Run GA optimization dengan category constraints
        
        Returns:
            (best_chromosome, best_fitness)
        """
        
        if self.verbose:
            print(f"[GA] Starting optimization dengan {self.population_size} population, {self.generations} generations")
            print(f"[GA] Kategori tersedia: {list(self.category_manager.food_ids_by_category.keys())}")
        
        # Step 1: Initialize population
        self.population = []
        for i in range(self.population_size):
            chromosome = CategorizedChromosome.initialize_random(self.category_manager)
            if chromosome:
                self.population.append(chromosome)
        
        if not self.population:
            raise RuntimeError("Failed to initialize population")
        
        if self.verbose:
            print(f"[GA] Population initialized: {len(self.population)} valid chromosomes")
        
        # Step 2: Evolution loop
        for generation in range(self.generations):
            # Evaluate fitness
            self.fitness_scores = [
                self._evaluate_fitness(chromosome)
                for chromosome in self.population
            ]
            
            # Track best
            best_idx = np.argmax(self.fitness_scores)
            gen_best_fitness = self.fitness_scores[best_idx]
            
            if gen_best_fitness > self.best_fitness:
                self.best_fitness = gen_best_fitness
                self.best_solution = self.population[best_idx].copy()
            
            self.fitness_history.append({
                'generation': generation,
                'best': gen_best_fitness,
                'avg': np.mean(self.fitness_scores),
                'min': np.min(self.fitness_scores)
            })
            
            if self.verbose and (generation % 10 == 0 or generation == self.generations - 1):
                avg_fit = np.mean(self.fitness_scores)
                print(f"[Gen {generation:3d}] Best: {gen_best_fitness:6.2f} | "
                      f"Avg: {avg_fit:6.2f} | Global: {self.best_fitness:6.2f}")
            
            # Step 3: Elitism - preserve best
            elite_size = max(1, int(self.population_size * self.elite_fraction))
            elite_indices = sorted(
                range(len(self.population)),
                key=lambda i: self.fitness_scores[i],
                reverse=True
            )[:elite_size]
            
            elite_population = [
                self.population[i] for i in elite_indices
            ]
            
            # Step 4: Create offspring via crossover + mutation
            offspring = []
            offspring_size = self.population_size - elite_size
            
            for _ in range(offspring_size):
                # Selection via tournament
                parent1_idx = self._tournament_selection()
                parent2_idx = self._tournament_selection()
                
                parent1 = self.population[parent1_idx]
                parent2 = self.population[parent2_idx]
                
                # Crossover
                if random.random() < self.crossover_rate:
                    child = CategorizedChromosome.crossover(
                        parent1, parent2, self.category_manager
                    )
                else:
                    # No crossover, just pick random parent
                    child = parent1 if random.random() < 0.5 else parent2
                
                # Mutation
                child = CategorizedChromosome.mutate(
                    child, self.category_manager, self.mutation_rate
                )
                
                # Validate sebelum add
                valid, msg = CategorizedChromosome.is_valid(child)
                if valid:
                    offspring.append(child)
                else:
                    # Fallback: duplicate parent
                    offspring.append(parent1 if random.random() < 0.5 else parent2)
            
            # Step 5: Create new population = elite + offspring
            self.population = elite_population + offspring[:self.population_size - elite_size]
        
        if self.verbose:
            print(f"\n[GA] Optimization complete!")
            print(f"[GA] Best fitness: {self.best_fitness:.2f}")
            print(f"[GA] Best solution:")
            self._print_solution(self.best_solution)
        
        return self.best_solution, self.best_fitness
    
    def _evaluate_fitness(self, chromosome: Dict) -> float:
        """
        Evaluate fitness untuk chromosome dengan kategori
        Menggunakan ImprovedFitnessCalculator dari Phase 1
        """
        try:
            # Extract food_ids dari chromosome
            food_ids = CategorizedChromosome.get_food_ids(chromosome)
            
            # Create fake chromosome format untuk fitness calculator
            # (jika fitness calculator expect format lama)
            chromosome_for_fitness = {
                'breakfast': {food_ids[0]: 100, food_ids[1]: 50, food_ids[2]: 200},
                'lunch': {food_ids[3]: 150, food_ids[4]: 80, food_ids[5]: 250},
                'dinner': {food_ids[6]: 120, food_ids[7]: 100, food_ids[8]: 200},
                'snack': {food_ids[9]: 50}
            }
            
            fitness = ImprovedFitnessCalculator.calculate_fitness(
                chromosome_for_fitness,
                self.food_database,
                self.nutrition_targets,
                user_tdee=self.nutrition_targets.get('tdee', 2000)
            )
            
            return fitness
        
        except Exception as e:
            # Fallback: return low fitness
            if self.verbose:
                print(f"[WARN] Fitness calculation error: {e}")
            return 0.0
    
    def _tournament_selection(self, tournament_size: int = 3) -> int:
        """
        Tournament selection untuk parent picking
        """
        candidates = random.sample(range(len(self.population)), tournament_size)
        best_candidate = max(candidates, key=lambda i: self.fitness_scores[i])
        return best_candidate
    
    def _print_solution(self, chromosome: Dict):
        """
        Print solution dalam format readable
        """
        readable = CategorizedChromosome.to_readable(chromosome, self.food_database)
        
        print("\n" + "="*80)
        for meal in ['breakfast', 'lunch', 'dinner']:
            print(f"\n{meal.upper()}:")
            for category, food_name in readable[meal].items():
                print(f"  {category}: {food_name}")
        print(f"\nSNACK: {readable['snack']}")
        print("="*80)
    
    def get_best_solution_readable(self) -> Dict:
        """Get best solution dalam format readable"""
        if not self.best_solution:
            return None
        return CategorizedChromosome.to_readable(self.best_solution, self.food_database)
    
    def get_fitness_history(self) -> List[Dict]:
        """Get fitness improvement history"""
        return self.fitness_history


if __name__ == "__main__":
    print("CategorizedGeneticAlgorithmOptimizer module loaded")
    print("\nExample usage:")
    print("1. optimizer = CategorizedGeneticAlgorithmOptimizer(food_db, targets)")
    print("2. best_solution, best_fitness = optimizer.optimize()")
    print("3. readable = optimizer.get_best_solution_readable()")

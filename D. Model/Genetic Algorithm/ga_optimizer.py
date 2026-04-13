"""
Core Genetic Algorithm + Local Search Implementation - REDESIGNED
Chromosome = {meal: {food_id: portion, ...}, ...}
"""

import random
from typing import Dict, List, Tuple, Optional
import pandas as pd

from ga_chromosome import ChromosomeOperations
from ga_operators import GeneticOperators
from ga_fitness import FitnessCalculator
from ga_local_search import LocalSearchOptimizer


class GeneticAlgorithmOptimizer:
    """
    Hybrid GA + Local Search untuk meal planning
    - Chromosome: flexible dict {meal: {food_id: portion, ...}, ...}
    - Population-based search + local refinement
    - Adaptive food selection across entire food database
    """
    
    def __init__(
        self,
        food_database: pd.DataFrame,
        guidelines: Dict,
        user_tdee: float,
        population_size: int = 50,
        generations: int = 100,
        verbose: bool = True
    ):
        """
        Initialize GA optimizer
        
        Args:
            food_database: DataFrame with all foods (fdc_id, food_name, nutrients)
            guidelines: Dict dari NutritionService dengan constraints per nutrient
            user_tdee: User's TDEE (energy target)
            population_size: GA population size
            generations: Max generations
            verbose: Print progress
        """
        self.food_database = food_database
        self.guidelines = guidelines
        self.user_tdee = user_tdee
        self.population_size = population_size
        self.generations = generations
        self.verbose = verbose
        
        # GA parameters
        self.crossover_rate = 0.8
        self.mutation_rate = 0.3  # More mutations untuk variable length
        self.elite_fraction = 0.2  # Top 20% gets local search
        self.ls_max_iterations = 50
        
        # Tracking
        self.best_fitness_history = []
        self.avg_fitness_history = []
        self.best_solution = None
        self.best_fitness = 0.0
    
    def optimize(self) -> Tuple[Optional[Dict], float]:
        """
        Run GA + LS optimization
        
        Returns:
            (best_chromosome, best_fitness)
        """
        
        if self.verbose:
            print("\n" + "="*70)
            print("GENETIC ALGORITHM OPTIMIZATION")
            print("="*70)
            print(f"Population Size: {self.population_size}")
            print(f"Generations: {self.generations}")
            print(f"Mutation Rate: {self.mutation_rate}")
            print(f"Crossover Rate: {self.crossover_rate}")
            print("="*70 + "\n")
        
        # Step 1: Initialize population
        population = self._initialize_population()
        
        if not population:
            print("[ERROR] Failed to initialize population - no valid chromosomes created")
            return None, 0.0
        
        if self.verbose:
            print(f"[OK] Population initialized with {len(population)} chromosomes\n")
        
        # Step 2: Main GA loop
        for generation in range(self.generations):
            
            # Evaluate fitness
            fitness_scores = [
                self._evaluate_fitness(ind) for ind in population
            ]
            
            # Track statistics
            best_fit = max(fitness_scores)
            avg_fit = sum(fitness_scores) / len(fitness_scores)
            self.best_fitness_history.append(best_fit)
            self.avg_fitness_history.append(avg_fit)
            
            # Update global best
            best_idx = fitness_scores.index(best_fit)
            if best_fit > self.best_fitness:
                self.best_fitness = best_fit
                self.best_solution = self._deep_copy_chromosome(population[best_idx])
            
            if self.verbose and (generation % 10 == 0 or generation == 0):
                print(f"[Gen {generation:3d}] Best: {best_fit:6.2f} | "
                      f"Avg: {avg_fit:6.2f} | Global Best: {self.best_fitness:6.2f}")
            
            # Step 3: Local Search on elite
            if self.elite_fraction > 0:
                elite_size = max(1, int(self.population_size * self.elite_fraction))
                elite_indices = sorted(
                    range(len(population)),
                    key=lambda i: fitness_scores[i],
                    reverse=True
                )[:elite_size]
                
                for elite_idx in elite_indices:
                    fitness_args = {
                        'food_database': self.food_database,
                        'guidelines': self.guidelines,
                        'user_tdee': self.user_tdee
                    }
                    
                    improved = LocalSearchOptimizer.optimize(
                        population[elite_idx],
                        self.food_database,
                        FitnessCalculator.calculate_fitness,
                        fitness_args,
                        max_iterations=self.ls_max_iterations
                    )
                    
                    # Update if better
                    improved_fit = self._evaluate_fitness(improved)
                    if improved_fit > fitness_scores[elite_idx]:
                        population[elite_idx] = improved
                        fitness_scores[elite_idx] = improved_fit
            
            # Step 4: Elitism - preserve best
            elite_size = max(1, int(self.population_size * 0.1))
            sorted_indices = sorted(
                range(len(population)),
                key=lambda i: fitness_scores[i],
                reverse=True
            )
            elite_pop = [
                self._deep_copy_chromosome(population[i])
                for i in sorted_indices[:elite_size]
            ]
            elite_fitness = [fitness_scores[i] for i in sorted_indices[:elite_size]]
            
            # Step 5: Create offspring (crossover + mutation)
            offspring_size = self.population_size - elite_size
            offspring = []
            
            for _ in range(offspring_size):
                # Selection + Crossover
                if random.random() < self.crossover_rate:
                    parent1 = GeneticOperators.tournament_selection(
                        population, fitness_scores, tournament_size=3
                    )
                    parent2 = GeneticOperators.tournament_selection(
                        population, fitness_scores, tournament_size=3
                    )
                    child = GeneticOperators.crossover_meal_based(parent1, parent2)
                else:
                    child = GeneticOperators.tournament_selection(
                        population, fitness_scores, tournament_size=3
                    )
                    child = self._deep_copy_chromosome(child)
                
                # Mutation - prepare food_database_by_meal
                food_ids = self.food_database['fdc_id'].unique().tolist()
                food_database_by_meal = {
                    meal: food_ids for meal in ChromosomeOperations.MEALS
                }
                
                if random.random() < self.mutation_rate:
                    child = GeneticOperators.mutate_add_food(child, food_database_by_meal, self.mutation_rate)
                elif random.random() < self.mutation_rate:
                    child = GeneticOperators.mutate_remove_food(child)
                elif random.random() < self.mutation_rate:
                    child = GeneticOperators.mutate_adjust_portion(child)
                else:
                    child = GeneticOperators.mutate_swap_food(child, food_database_by_meal, self.mutation_rate)
                
                # Validate
                if ChromosomeOperations.is_valid(child):
                    offspring.append(child)
                else:
                    # Keep parent if offspring invalid
                    offspring.append(GeneticOperators.tournament_selection(
                        population, fitness_scores, tournament_size=3
                    ))
            
            # Step 6: Combine elite + offspring
            population = elite_pop + offspring
        
        if self.verbose:
            print("\n" + "="*70)
            print("OPTIMIZATION COMPLETE")
            print(f"Best Fitness Found: {self.best_fitness:.2f}")
            print("="*70 + "\n")
        
        return self.best_solution, self.best_fitness
    
    def _initialize_population(self) -> List[Dict]:
        """Initialize random population"""
        food_ids = self.food_database['fdc_id'].unique().tolist()
        food_database_by_meal = {
            meal: food_ids for meal in ChromosomeOperations.MEALS
        }
        
        if self.verbose:
            print(f"[DEBUG] food_database_by_meal has {len(food_database_by_meal)} meals")
            for meal, foods in food_database_by_meal.items():
                print(f"  {meal}: {len(foods)} foods available")
        
        population = []
        failures = 0
        for _ in range(self.population_size):
            chromosome = ChromosomeOperations.initialize_random(food_database_by_meal)
            if chromosome:
                population.append(chromosome)
            else:
                failures += 1
        
        if self.verbose and failures > 0:
            print(f"[WARN] Population init: {len(population)}/{self.population_size} valid, {failures} failed")
        
        return population
    
    def _evaluate_fitness(self, chromosome: Dict) -> float:
        """Evaluate fitness"""
        return FitnessCalculator.calculate_fitness(
            chromosome,
            self.food_database,
            self.guidelines,
            self.user_tdee
        )
    
    def _deep_copy_chromosome(self, chromosome: Dict) -> Dict:
        """Deep copy chromosome"""
        return {
            meal: foods_dict.copy()
            for meal, foods_dict in chromosome.items()
        }
    
    def get_statistics(self) -> Dict:
        """Get optimization statistics"""
        return {
            'best_fitness': self.best_fitness,
            'best_fitness_history': self.best_fitness_history,
            'avg_fitness_history': self.avg_fitness_history,
            'final_generation': len(self.best_fitness_history),
            'improvement': (
                self.best_fitness_history[-1] - self.best_fitness_history[0]
                if self.best_fitness_history else 0
            )
        }


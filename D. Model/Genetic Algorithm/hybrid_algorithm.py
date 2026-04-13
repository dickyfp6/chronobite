"""
Hybrid Genetic Algorithm + Local Search

Integrated optimization: GA + LS improvement per generation (Option 2)
Main entry point untuk meal planning optimization
"""

import pandas as pd
from typing import Dict, List, Any, Tuple
import time
import copy

from ga_core import GeneticAlgorithm, Individual, Population
from ls_core import LocalSearcher
from food_slot_mapping import group_food_candidates
from output_contract import build_final_output_template
from validator import validate_complete_solution


def _build_solution_from_individual(individual, food_df, meal_budgets) -> Dict[str, Any]:
    """Convert individual to solution format dari output_contract"""
    solution = {}
    
    for meal_name in ['breakfast', 'lunch', 'dinner', 'snack']:
        meal_data = individual.meal_plan.get(meal_name, {})
        
        if meal_name == 'snack':
            solution[meal_name] = {
                'budget_kcal': meal_budgets.get('snack', 0),
                'selected': meal_data.get('selected'),
                'candidates': [],
                'refresh_state': 0
            }
        else:
            solution[meal_name] = {
                'budget_kcal': meal_budgets.get(meal_name, 0),
                'selected': meal_data.get('selected', {}),
                'candidates': {
                    'main_course': [],
                    'side_dish': [],
                    'drink': []
                },
                'refresh_state': {
                    'main_course': 0,
                    'side_dish': 0,
                    'drink': 0
                }
            }
    
    return solution


class HybridGA_LS:
    """
    Genetic Algorithm dengan Local Search improvement per generation
    
    Flow:
    1. Initialize population (GA)
    2. For each generation:
       a. Selection:tournament
       b. Crossover & Mutation
       c. Evaluate fitness
       d. LS improvement pada best individual
       e. Update population dengan improved best
       f. Elitism preserve
    3. Return best solution overall
    """
    
    def __init__(
        self,
        food_df: pd.DataFrame,
        meal_budgets: Dict[str, float],
        food_groups: Dict[str, List[Dict]],
        ga_params: Dict[str, Any],
        ls_strategy: str = 'hill_climbing',
        ls_iterations: int = 10,
        verbose: bool = True
    ):
        self.food_df = food_df
        self.meal_budgets = meal_budgets
        self.food_groups = food_groups
        self.ga_params = ga_params
        self.ls_strategy = ls_strategy
        self.ls_iterations = ls_iterations
        self.verbose = verbose
        
        # GA setup
        self.ga = GeneticAlgorithm(
            food_df=food_df,
            meal_budgets=meal_budgets,
            food_groups=food_groups,
            params=ga_params,
            verbose=False  # LS nanti handle verbose
        )
        
        # LS setup
        self.ls = LocalSearcher(
            food_df=food_df,
            meal_budgets=meal_budgets,
            food_groups=food_groups,
            energy_tolerance_pct=ga_params.get('energy_tolerance_pct', 10.0),
            similarity_threshold=ga_params.get('similarity_threshold', 0.60),
            verbose=False
        )
        
        self.best_individual = None
        self.best_fitness = float('-inf')
        self.history = []
    
    def run(self) -> Individual:
        """Run hybrid GA+LS"""
        # Initialize population
        self.ga.initialize_population()
        self.ga.evaluate_population()
        population = self.ga.population
        
        if self.verbose:
            print(f"\nInitial population: avg_fitness={population.get_average_fitness():.1f}")
        
        # Main loop per generation
        for generation in range(self.ga.params['generations']):
            # GA operators: selection, crossover, mutation
            new_individuals = []
            
            for _ in range(self.ga.params['population_size'] // 2):
                parent1 = self.ga.selection_tournament(population)
                parent2 = self.ga.selection_tournament(population)
                
                child = self.ga.crossover(parent1, parent2)
                self.ga.mutation(child)
                
                new_individuals.append(child)
            
            # Evaluate new individuals
            self.ga.evaluate_individuals(new_individuals)
            
            # Get best dari current generation
            best_in_gen = max(new_individuals, key=lambda x: x.fitness)
            
            # **LS IMPROVEMENT pada best individual ini**
            if self.verbose and generation % 5 == 0:
                print(f"  Gen {generation}: best_before_ls={best_in_gen.fitness:.1f}", end="")
            
            improved_copy = copy.deepcopy(best_in_gen)
            
            if self.ls_strategy == 'greedy':
                improved_copy, improved_fitness = self.ls.greedy_improvement(
                    improved_copy,
                    max_iterations=self.ls_iterations
                )
            elif self.ls_strategy == 'hill_climbing':
                improved_copy, improved_fitness = self.ls.hill_climbing(
                    improved_copy,
                    max_iterations=self.ls_iterations
                )
            elif self.ls_strategy == 'simulated_annealing':
                improved_copy, improved_fitness = self.ls.simulated_annealing(
                    improved_copy,
                    max_iterations=self.ls_iterations
                )
            
            if self.verbose and generation % 5 == 0:
                print(f" -> after_ls={improved_fitness:.1f}")
            
            # Use improved version jika better
            if improved_fitness > best_in_gen.fitness:
                best_in_gen = improved_copy
                best_in_gen.fitness = improved_fitness
            
            # Merge populations untuk selection
            all_individuals = population.individuals + new_individuals
            all_individuals = sorted(all_individuals, key=lambda x: x.fitness, reverse=True)
            
            # Keep best + tournament untuk next gen (elitism)
            elite_count = self.ga.params.get('elite_size', 2)
            elite = all_individuals[:elite_count]
            remaining = all_individuals[elite_count:elite_count + (self.ga.params['population_size'] - elite_count)]
            
            population.individuals = elite + remaining[:self.ga.params['population_size'] - elite_count]
            
            # Track best ever
            if best_in_gen.fitness > self.best_fitness:
                self.best_fitness = best_in_gen.fitness
                self.best_individual = copy.deepcopy(best_in_gen)
            
            self.history.append({
                'generation': generation,
                'best_fitness': self.best_fitness,
                'pop_avg': sum(ind.fitness for ind in population.individuals) / len(population.individuals)
            })
        
        return self.best_individual


def run_hybrid_algorithm(
    food_df: pd.DataFrame,
    user_constraints: Dict[str, Any],
    meal_budgets: Dict[str, float],
    tdee: float,
    pop_size: int = 100,
    ga_generations: int = 50,
    ls_iterations: int = 10,
    ls_strategy: str = 'hill_climbing',
    mutation_rate: float = 0.15,
    crossover_rate: float = 0.8,
    energy_tolerance_pct: float = 10.0,
    similarity_threshold: float = 0.60,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Run Hybrid GA+LS (MAIN ENTRY POINT)
    
    Args:
        food_df: Food dataframe
        user_constraints: User constraints
        meal_budgets: Budget per meal
        tdee: Total daily energy expenditure
        pop_size: GA population size
        ga_generations: Number of GA generations
        ls_iterations: LS iterations per generation
        ls_strategy: 'greedy', 'hill_climbing', 'simulated_annealing'
        mutation_rate: GA mutation rate
        crossover_rate: GA crossover rate
        energy_tolerance_pct: Energy tolerance threshold
        similarity_threshold: Similarity threshold
        verbose: Print progress
    
    Returns:
        Dict sesuai output_contract
    """
    if verbose:
        print("\n" + "="*70)
        print("HYBRID GENETIC ALGORITHM + LOCAL SEARCH")
        print("="*70)
        print(f"Configuration:")
        print(f"  GA Population: {pop_size}")
        print(f"  GA Generations: {ga_generations}")
        print(f"  LS Strategy: {ls_strategy}")
        print(f"  LS Iterations/Gen: {ls_iterations}")
    
    start_time = time.time()
    
    # Group food candidates
    food_groups = group_food_candidates(food_df.to_dict('records'))
    
    # GA params
    params = {
        'population_size': pop_size,
        'generations': ga_generations,
        'mutation_rate': mutation_rate,
        'crossover_rate': crossover_rate,
        'energy_tolerance_pct': energy_tolerance_pct,
        'similarity_threshold': similarity_threshold
    }
    
    # Run hybrid
    hybrid = HybridGA_LS(
        food_df=food_df,
        meal_budgets=meal_budgets,
        food_groups=food_groups,
        ga_params=params,
        ls_strategy=ls_strategy,
        ls_iterations=ls_iterations,
        verbose=verbose
    )
    
    best_individual = hybrid.run()
    
    execution_time = time.time() - start_time
    
    # Build output
    output = build_final_output_template()
    output['algorithm'] = f'Hybrid GA+LS'
    output['success'] = True
    output['user_profile'] = user_constraints
    output['meal_plan'] = _build_solution_from_individual(best_individual, food_df, meal_budgets)
    output['debug']['selected_algorithm_mode'] = 'ga_with_ls'
    output['debug']['ga_generations'] = ga_generations
    output['debug']['ls_iterations_per_gen'] = ls_iterations
    output['debug']['ls_strategy'] = ls_strategy
    
    # Validate
    validation = validate_complete_solution(
        output['meal_plan'],
        food_df,
        meal_budgets,
        energy_tolerance_pct,
        similarity_threshold
    )
    
    # Summary
    output['summary'] = {
        'fitness_score': best_individual.fitness,
        'feasible': validation['feasible'],
        'execution_time': execution_time,
        'violations': validation['total_violations'],
        'notes': [
            f"Hybrid GA+LS converged to fitness {best_individual.fitness:.1f}",
            f"Integrated {ga_generations} GA generations with {ls_iterations} LS iterations each"
        ]
    }
    
    if verbose:
        print(f"\nHybrid Execution Time: {execution_time:.2f} seconds")
        print(f"Final Fitness: {best_individual.fitness:.1f}")
        print(f"Solution Feasible: {validation['feasible']}")
        print("="*70 + "\n")
    
    return output

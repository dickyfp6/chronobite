"""
Genetic Algorithm Main Runner

Standalone GA wrapper yang return output sesuai output_contract.py
"""

import pandas as pd
from typing import Dict, List, Any
import time

from ga_core import GeneticAlgorithm
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
                'candidates': [],  # LS phase nanti isi ini
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


def run_genetic_algorithm(
    food_df: pd.DataFrame,
    user_constraints: Dict[str, Any],
    meal_budgets: Dict[str, float],
    tdee: float,
    pop_size: int = 100,
    generations: int = 50,
    mutation_rate: float = 0.15,
    crossover_rate: float = 0.8,
    energy_tolerance_pct: float = 10.0,
    similarity_threshold: float = 0.60,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Run Genetic Algorithm standalone
    
    Args:
        food_df: Food dataframe
        user_constraints: User constraints (disease, preferences, etc)
        meal_budgets: Budget per meal
        tdee: Total daily energy expenditure
        pop_size: Population size
        generations: Number of generations
        mutation_rate: Mutation probability
        crossover_rate: Crossover probability
        energy_tolerance_pct: Energy tolerance
        similarity_threshold: Similarity threshold
        verbose: Print progress
    
    Returns:
        Dict sesuai output_contract (dengan meal_plan)
    """
    if verbose:
        print("\n" + "="*70)
        print("GENETIC ALGORITHM")
        print("="*70)
    
    start_time = time.time()
    
    # Group food candidates
    food_groups = group_food_candidates(food_df.to_dict('records'))
    
    # Create GA instance
    params = {
        'population_size': pop_size,
        'generations': generations,
        'mutation_rate': mutation_rate,
        'crossover_rate': crossover_rate,
        'energy_tolerance_pct': energy_tolerance_pct,
        'similarity_threshold': similarity_threshold
    }
    
    ga = GeneticAlgorithm(
        food_df=food_df,
        meal_budgets=meal_budgets,
        food_groups=food_groups,
        params=params,
        verbose=verbose
    )
    
    # Run GA
    best_individual = ga.run()
    
    execution_time = time.time() - start_time
    
    # Build output
    output = build_final_output_template()
    output['algorithm'] = 'Genetic Algorithm'
    output['success'] = True
    output['user_profile'] = user_constraints
    output['meal_plan'] = _build_solution_from_individual(best_individual, food_df, meal_budgets)
    output['debug']['selected_algorithm_mode'] = 'ga_only'
    
    # Validate solution
    validation = validate_complete_solution(
        output['meal_plan'],
        food_df,
        meal_budgets,
        energy_tolerance_pct,
        similarity_threshold
    )
    
    # Fill summary
    output['summary'] = {
        'fitness_score': best_individual.fitness,
        'feasible': validation['feasible'],
        'execution_time': execution_time,
        'violations': validation['total_violations'],
        'notes': [f"GA converged to {best_individual.fitness:.1f}"]
    }
    
    if verbose:
        print(f"\nGA Execution Time: {execution_time:.2f} seconds")
        print(f"Final Fitness: {best_individual.fitness:.1f}")
        print(f"Solution Feasible: {validation['feasible']}")
        print("="*70 + "\n")
    
    return output

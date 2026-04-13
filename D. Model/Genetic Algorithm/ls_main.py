"""
Local Search Main Runner

Standalone LS wrapper yang return output sesuai output_contract.py
"""

import pandas as pd
from typing import Dict, List, Any, Optional
import time

from ga_core import Individual
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


def run_local_search(
    food_df: pd.DataFrame,
    user_constraints: Dict[str, Any],
    meal_budgets: Dict[str, float],
    tdee: float,
    initial_solution: Optional[Individual] = None,
    strategy: str = 'hill_climbing',
    max_iterations: int = 50,
    energy_tolerance_pct: float = 10.0,
    similarity_threshold: float = 0.60,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Run Local Search standalone (bisa dari random init atau dari existing solution)
    
    Args:
        food_df: Food dataframe
        user_constraints: User constraints
        meal_budgets: Budget per meal
        tdee: Total daily energy expenditure
        initial_solution: Starting solution (jika None, random)
        strategy: 'greedy', 'hill_climbing', atau 'simulated_annealing'
        max_iterations: Max iterations
        energy_tolerance_pct: Energy tolerance
        similarity_threshold: Similarity threshold
        verbose: Print progress
    
    Returns:
        Dict sesuai output_contract
    """
    if verbose:
        print("\n" + "="*70)
        print(f"LOCAL SEARCH ({strategy.upper()})")
        print("="*70)
    
    start_time = time.time()
    
    # Group food candidates
    food_groups = group_food_candidates(food_df.to_dict('records'))
    
    # Init solution jika ga ada
    if initial_solution is None:
        # Create random meal plan
        from ga_core import GeneticAlgorithm
        
        ga_params = {
            'population_size': 1,
            'generations': 1,
            'mutation_rate': 0.15,
            'crossover_rate': 0.8,
            'energy_tolerance_pct': energy_tolerance_pct,
            'similarity_threshold': similarity_threshold
        }
        ga = GeneticAlgorithm(
            food_df=food_df,
            meal_budgets=meal_budgets,
            food_groups=food_groups,
            params=ga_params,
            verbose=False
        )
        initial_solution = ga._create_random_individual()
    
    # Create LS instance
    ls = LocalSearcher(
        food_df=food_df,
        meal_budgets=meal_budgets,
        food_groups=food_groups,
        energy_tolerance_pct=energy_tolerance_pct,
        similarity_threshold=similarity_threshold,
        verbose=False
    )
    
    # Run LS sesuai strategy
    if strategy == 'greedy':
        best_solution, best_fitness = ls.greedy_improvement(
            initial_solution,
            max_iterations=max_iterations
        )
    elif strategy == 'hill_climbing':
        best_solution, best_fitness = ls.hill_climbing(
            initial_solution,
            max_iterations=max_iterations
        )
    elif strategy == 'simulated_annealing':
        best_solution, best_fitness = ls.simulated_annealing(
            initial_solution,
            max_iterations=max_iterations
        )
    else:
        raise ValueError(f"Unknown strategy: {strategy}")
    
    execution_time = time.time() - start_time
    
    # Build output
    output = build_final_output_template()
    output['algorithm'] = f'Local Search ({strategy})'
    output['success'] = True
    output['user_profile'] = user_constraints
    output['meal_plan'] = _build_solution_from_individual(best_solution, food_df, meal_budgets)
    output['debug']['selected_algorithm_mode'] = 'ls_only'
    
    # Validate
    validation = validate_complete_solution(
        output['meal_plan'],
        food_df,
        meal_budgets,
        energy_tolerance_pct,
        similarity_threshold
    )
    
    output['summary'] = {
        'fitness_score': best_fitness,
        'feasible': validation['feasible'],
        'execution_time': execution_time,
        'violations': validation['total_violations'],
        'notes': [f"LS ({strategy}) improved to {best_fitness:.1f}"]
    }
    
    if verbose:
        print(f"\nLS Execution Time: {execution_time:.2f} seconds")
        print(f"Final Fitness: {best_fitness:.1f}")
        print(f"Solution Feasible: {validation['feasible']}")
        print("="*70 + "\n")
    
    return output

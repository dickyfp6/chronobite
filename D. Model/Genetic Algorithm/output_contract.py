"""
Adapter: output_contract.py

Bridge untuk mengakses meal schema dan output contract dari parent/../meal_schema.py

Provides: build_final_output_template()
"""

import sys
import os
from typing import Dict, Any

# Add parent directory to path (D. Model/)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from meal_schema import MenuPlan, Meal, SnackMeal, FoodItem


def build_final_output_template() -> Dict[str, Any]:
    """
    Build template untuk final output hasil GA/LS
    
    Returns:
        Dict template dengan struktur lengkap:
        {
            'algorithm': 'Genetic Algorithm' atau 'Local Search' atau 'Hybrid GA+LS',
            'success': True/False,
            'user_profile': {...},
            'meal_plan': {
                'breakfast': {...},
                'lunch': {...},
                'dinner': {...},
                'snack': {...}
            },
            'summary': {
                'fitness_score': float,
                'feasible': True/False,
                'execution_time': float,
                'violations': int,
                'notes': [...]
            },
            'debug': {
                'selected_algorithm_mode': 'ga_only' / 'ls_only' / 'ga_with_ls',
                'ga_generations': int,
                'ls_iterations_per_gen': int,
                'ls_strategy': str
            }
        }
    """
    return {
        'algorithm': '',
        'success': False,
        'timestamp': None,
        'user_profile': {},
        'meal_plan': {
            'breakfast': {
                'budget_kcal': 0,
                'selected': {},
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
            },
            'lunch': {
                'budget_kcal': 0,
                'selected': {},
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
            },
            'dinner': {
                'budget_kcal': 0,
                'selected': {},
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
            },
            'snack': {
                'budget_kcal': 0,
                'selected': None,
                'candidates': [],
                'refresh_state': 0
            }
        },
        'summary': {
            'fitness_score': 0.0,
            'feasible': False,
            'execution_time': 0.0,
            'violations': 0,
            'warnings': 0,
            'notes': []
        },
        'debug': {
            'selected_algorithm_mode': '',  # 'ga_only' / 'ls_only' / 'ga_with_ls'
            'ga_generations': 0,
            'ga_population_size': 0,
            'ls_iterations_per_gen': 0,
            'ls_strategy': '',  # 'greedy' / 'hill_climbing' / 'simulated_annealing'
            'energy_tolerance_pct': 10.0,
            'similarity_threshold': 0.60
        },
        'validation': {
            'valid': False,
            'meal_validations': [],
            'total_violations': 0,
            'total_warnings': 0,
            'daily_energy': 0.0
        }
    }

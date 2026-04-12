"""
Adapter: meal_distribution.py

Bridge untuk mengakses meal distribution logic dari 
../../C. System Flow/modules/calculations.py

Provides: get_meal_scheme(), calculate_slot_budget(), get_default_meal_ratios()
"""

import sys
import os
from typing import Dict, Optional

# Add C. System Flow/modules to path
calculations_path = os.path.join(
    os.path.dirname(__file__), 
    '../../C. System Flow'
)
sys.path.insert(0, calculations_path)

from modules.calculations import NutritionCalculator


def get_default_meal_ratios() -> Dict[str, float]:
    """
    Get default meal distribution ratios
    
    Returns:
        Dict dengan meal names dan percentage:
        {
            'breakfast': 0.2375,
            'lunch': 0.3375,
            'dinner': 0.2875,
            'snack': 0.1375
        }
    """
    return {
        'breakfast': 0.2375,   # 23.75%
        'lunch': 0.3375,       # 33.75%
        'dinner': 0.2875,      # 28.75%
        'snack': 0.1375        # 13.75%
    }


def calculate_slot_budget(tdee: float, meal_name: str) -> float:
    """
    Calculate calorie budget untuk satu meal slot
    
    Args:
        tdee: Total Daily Energy Expenditure (kcal/hari)
        meal_name: 'breakfast', 'lunch', 'dinner', atau 'snack'
    
    Returns:
        Calorie budget untuk meal tersebut
    """
    ratios = get_default_meal_ratios()
    ratio = ratios.get(meal_name, 0.0)
    return round(tdee * ratio, 2)


def get_meal_scheme(meal_name: str) -> Dict[str, any]:
    """
    Get meal scheme/structure untuk satu meal
    
    Args:
        meal_name: 'breakfast', 'lunch', 'dinner', atau 'snack'
    
    Returns:
        Dict dengan meal scheme:
        {
            'meal_name': 'breakfast',
            'required_slots': ['main_course', 'side_dish', 'drink'],  # untuk regular meals
            'is_regular': True,  # atau False untuk snack
            'snack_only': False
        }
    """
    if meal_name == 'snack':
        return {
            'meal_name': 'snack',
            'required_slots': [],  # snack tidak punya slots
            'is_regular': False,
            'snack_only': True,
            'num_items': 3  # 3 snack candidates max
        }
    else:
        return {
            'meal_name': meal_name,
            'required_slots': ['main_course', 'side_dish', 'drink'],
            'is_regular': True,
            'snack_only': False,
            'slots_spec': {
                'main_course': {'required': True, 'max_items': 1},
                'side_dish': {'required': True, 'max_items': 1},
                'drink': {'required': True, 'max_items': 1}
            }
        }


def calculate_meal_distribution(tdee: float) -> Dict[str, float]:
    """
    Calculate meal distribution untuk seluruh hari
    
    Args:
        tdee: Total Daily Energy Expenditure (kcal/hari)
    
    Returns:
        Dict dengan calorie budget per meal:
        {
            'breakfast': 570.0,
            'lunch': 810.0,
            'dinner': 690.0,
            'snack': 330.0
        }
    """
    return NutritionCalculator.calculate_meal_distribution(tdee)

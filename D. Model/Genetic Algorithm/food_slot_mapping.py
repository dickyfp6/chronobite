"""
Adapter: food_slot_mapping.py

Bridge untuk mengakses food categorization dan candidate generation logic
dari parent/../food_categorizer.py dan parent/../candidate_generator.py

Provides: group_food_candidates(), infer_food_role()
"""

import sys
import os
import pandas as pd
from typing import Dict, List, Optional

# Add parent directory to path (D. Model/)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from food_categorizer import FoodCategorizer
from candidate_generator import CandidateGenerator


def infer_food_role(food_dict: Dict) -> Optional[str]:
    """
    Infer food role/category dari food_dict
    
    Args:
        food_dict: Dictionary dengan keys: 'food_name', 'consumption_label', 'food_group'
    
    Returns:
        Category: 'main_course', 'side_dish', 'drink', 'snack'
    """
    category = FoodCategorizer.categorize_item(food_dict)
    
    # Normalize ke format yang diresources (lowercase dengan underscore)
    if category:
        return category.lower().replace(' ', '_')
    
    return None


def group_food_candidates(food_records: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Group food records berdasarkan category/role
    
    Args:
        food_records: List of dictionaries hasil food dataset (dengan food_name, consumption_label, food_group, fdc_id, energy_kcal, dll)
    
    Returns:
        Dict dengan structure:
        {
            'main_course': [food1_dict, food2_dict, ...],
            'side_dish': [food3_dict, food4_dict, ...],
            'drink': [food5_dict, ...],
            'snack': [food6_dict, ...]
        }
    """
    grouped = {
        'main_course': [],
        'side_dish': [],
        'drink': [],
        'snack': []
    }
    
    for food_dict in food_records:
        role = infer_food_role(food_dict)
        
        # Map role ke grouped keys
        if role == 'main':
            grouped['main_course'].append(food_dict)
        elif role == 'side':
            grouped['side_dish'].append(food_dict)
        elif role == 'drink':
            grouped['drink'].append(food_dict)
        elif role == 'snack':
            grouped['snack'].append(food_dict)
        else:
            # Fallback: try to guess based on protein source
            protein = CandidateGenerator.extract_protein_source(food_dict.get('food_name', ''))
            if protein:
                grouped['main_course'].append(food_dict)
            else:
                grouped['side_dish'].append(food_dict)
    
    return grouped

"""
Adapter: meal_similarity.py

Bridge untuk mengakses similarity checking logic dari parent/../similarity_checker.py
Provides: is_too_similar(), diversity_penalty()
"""

import sys
import os
from typing import List, Dict, Optional

# Add parent directory to path (D. Model/)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from similarity_checker import SimilarityChecker


def is_too_similar(food_dict_1: Dict, food_dict_list: List[Dict], threshold: float = 0.60) -> bool:
    """
    Check apakah food_dict_1 mirip dengan salah satu dari food_dict_list
    
    Args:
        food_dict_1: Dictionary dengan 'food_name' key
        food_dict_list: List of dictionaries dengan 'food_name' key
        threshold: Similarity threshold (0-1). Jika >= threshold = too similar
    
    Returns:
        True jika ada yang mirip, False jika semua berbeda
    """
    if not food_dict_list:
        return False
    
    food_name_1 = food_dict_1.get('food_name', '')
    
    for food_dict_2 in food_dict_list:
        food_name_2 = food_dict_2.get('food_name', '')
        similarity_score = SimilarityChecker.calculate_similarity_score(food_name_1, food_name_2)
        
        if similarity_score >= threshold:
            return True
    
    return False


def diversity_penalty(food_dict_1: Dict, food_dict_list: List[Dict]) -> float:
    """
    Calculate penalty score jika food_dict_1 similar dengan items dalam food_dict_list
    
    Args:
        food_dict_1: Dictionary dengan 'food_name' key
        food_dict_list: List of dictionaries dengan 'food_name' key
    
    Returns:
        Max similarity score dengan items dalam list (0-1)
        0 = tidak ada yang mirip (good diversity)
        1 = ada yang identical (bad diversity)
    """
    if not food_dict_list:
        return 0.0
    
    food_name_1 = food_dict_1.get('food_name', '')
    
    max_similarity = 0.0
    for food_dict_2 in food_dict_list:
        food_name_2 = food_dict_2.get('food_name', '')
        similarity_score = SimilarityChecker.calculate_similarity_score(food_name_1, food_name_2)
        max_similarity = max(max_similarity, similarity_score)
    
    return max_similarity

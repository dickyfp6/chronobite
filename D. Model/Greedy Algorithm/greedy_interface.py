"""
Greedy Algorithm Interface
Wrapper untuk integrate Greedy Algorithm dengan NutritionService dan main system
"""

import sys
import os
import pandas as pd
from typing import Dict, Optional

# Add current and parent directories untuk imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from greedy_optimizer import GreedyOptimizer
from meal_schema import MenuPlan


class GreedyAlgorithmInterface:
    """
    Interface untuk Greedy Algorithm
    Digunakan oleh main sistem atau webapp untuk generate menu recommendations
    """
    
    def __init__(self):
        """Initialize interface"""
        self.optimizer = None
        self.last_result = None
    
    def initialize(self, food_database: pd.DataFrame, nutrition_guidelines: Dict) -> bool:
        """
        Initialize optimizer dengan database dan guidelines
        
        Args:
            food_database: DataFrame dari NutritionService.food_data['dataframe']
            nutrition_guidelines: Dict dari NutritionService.guidelines
        
        Returns:
            True jika success, False otherwise
        """
        try:
            self.optimizer = GreedyOptimizer(food_database, nutrition_guidelines)
            return True
        except Exception as e:
            print(f"❌ Greedy Algorithm initialization failed: {e}")
            return False
    
    def generate_menu_plan(
        self,
        user_profile: Dict,
        meal_distribution: Dict,
        user_tdee: float
    ) -> Optional[MenuPlan]:
        """
        Generate complete menu plan untuk user
        
        Args:
            user_profile: User demographic & health info dari NutritionService
            meal_distribution: Dict dengan meal distribution dari main system
                e.g., {'breakfast': 0.25, 'lunch': 0.35, 'snack': 0.10, 'dinner': 0.30}
            user_tdee: Total Daily Energy Expenditure
        
        Returns:
            MenuPlan object atau None jika gagal
        """
        
        if self.optimizer is None:
            print("❌ Optimizer not initialized. Call initialize() first.")
            return None
        
        try:
            # Calculate meal targets berdasarkan TDEE dan distribution
            meal_targets = {
                'breakfast': int(user_tdee * meal_distribution.get('breakfast', 0.25)),
                'lunch': int(user_tdee * meal_distribution.get('lunch', 0.35)),
                'snack': int(user_tdee * meal_distribution.get('snack', 0.10)),
                'dinner': int(user_tdee * meal_distribution.get('dinner', 0.30)),
            }
            
            print(f"\n🎯 Greedy Algorithm: Generating menu with targets:")
            print(f"   Breakfast: {meal_targets['breakfast']} kcal")
            print(f"   Lunch: {meal_targets['lunch']} kcal")
            print(f"   Snack: {meal_targets['snack']} kcal")
            print(f"   Dinner: {meal_targets['dinner']} kcal")
            print(f"   Total: {sum(meal_targets.values())} kcal / {user_tdee} kcal target")
            
            # Generate menu menggunakan greedy algorithm
            menu_plan = self.optimizer.optimize_full_menu(user_profile, meal_targets)
            
            if menu_plan:
                self.last_result = menu_plan
                print(f"✅ Greedy Algorithm: Menu generated successfully!")
                print(f"   Total calories: {menu_plan.total_calories:.0f} kcal")
                return menu_plan
            else:
                print("❌ Greedy Algorithm: Failed to generate menu (not enough food candidates)")
                return None
        
        except Exception as e:
            print(f"❌ Greedy Algorithm error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_last_result(self) -> Optional[MenuPlan]:
        """Return last generated menu plan"""
        return self.last_result


# Singleton instance untuk convenience
_instance = None

def get_greedy_algorithm() -> GreedyAlgorithmInterface:
    """Get singleton instance of Greedy Algorithm interface"""
    global _instance
    if _instance is None:
        _instance = GreedyAlgorithmInterface()
    return _instance


# Export untuk easy import
__all__ = ['GreedyAlgorithmInterface', 'get_greedy_algorithm', 'GreedyOptimizer']

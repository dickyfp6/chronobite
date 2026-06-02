"""
Greedy Algorithm Interface
Wrapper untuk integrate Greedy Algorithm dengan NutritionService dan main system
Maintains API compatibility: initialize(food_db, constraint_bag) → generate_menu_plan()
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
    Digunakan oleh app_integrated.py untuk generate menu recommendations
    
    API Contract:
    1. initialize(food_database, constraint_bag) - setup dengan data dari NutritionService
    2. generate_menu_plan(user_profile, meal_distribution, user_tdee) - generate menu
    """
    
    def __init__(self):
        """Initialize interface"""
        self.optimizer = None
        self.last_result = None
    
    def initialize(self, food_database: pd.DataFrame, constraint_bag: Dict) -> bool:
        """
        Initialize optimizer dengan food database dan constraint bag dari NutritionService
        
        Args:
            food_database: DataFrame dari result['food_data']['dataframe']
            constraint_bag: Dict dari result['guidelines'] (already contains disease, nutrients)
                {
                    'disease': ['dm2'],
                    'nutrients': {
                        'energy_kcal': {'min': 1800, 'max': 2200, 'hard_soft_type': 'HARD', ...},
                        ...
                    }
                }
        
        Returns:
            True jika success, False jika error
        """
        try:
            if food_database is None or food_database.empty:
                raise ValueError("Food database is empty")
            if constraint_bag is None:
                raise ValueError("Constraint bag is None")
            
            self.optimizer = GreedyOptimizer(food_database, constraint_bag)
            print("✅ Greedy Algorithm Interface initialized")
            return True
        except Exception as e:
            print(f"❌ Greedy Algorithm initialization failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def generate_menu_plan(
        self,
        user_profile: Dict,
        meal_distribution: Dict,
        user_tdee: float
    ) -> Optional[MenuPlan]:
        """
        Generate complete menu plan untuk user dengan constraint satisfaction
        
        Args:
            user_profile: User demographics & health dari NutritionService
            meal_distribution: Dict dengan meal time distribution
                e.g., {'breakfast': 0.2375, 'lunch': 0.3375, 'snack': 0.1375, 'dinner': 0.2875}
            user_tdee: Total Daily Energy Expenditure (kcal)
        
        Returns:
            MenuPlan object (dengan feasible flag dan violations list) atau None jika gagal
        """
        
        if self.optimizer is None:
            print("❌ Optimizer not initialized. Call initialize() first.")
            return None
        
        try:
            # Calculate meal targets berdasarkan TDEE dan meal distribution
            # meal_distribution dapat berupa:
            # - Percentages: {'breakfast': 0.2375, ...} → multiply by TDEE
            # - Absolute values: {'breakfast': 734.84, ...} → use as-is
            
            breakfast_dist = meal_distribution.get('breakfast', 0.2375)
            if breakfast_dist < 1.0:  # Percentage
                meal_targets = {
                    'breakfast': int(user_tdee * meal_distribution.get('breakfast', 0.2375)),
                    'lunch': int(user_tdee * meal_distribution.get('lunch', 0.3375)),
                    'snack': int(user_tdee * meal_distribution.get('snack', 0.1375)),
                    'dinner': int(user_tdee * meal_distribution.get('dinner', 0.2875)),
                }
            else:  # Absolute calorie values
                meal_targets = {
                    'breakfast': int(meal_distribution.get('breakfast', 600)),
                    'lunch': int(meal_distribution.get('lunch', 800)),
                    'snack': int(meal_distribution.get('snack', 400)),
                    'dinner': int(meal_distribution.get('dinner', 800)),
                }
            
            print(f"\n🎯 Greedy Algorithm: Generating menu plan")
            print(f"   TDEE: {user_tdee:.0f} kcal")
            print(f"   Breakfast: {meal_targets['breakfast']} kcal")
            print(f"   Lunch: {meal_targets['lunch']} kcal")
            print(f"   Snack: {meal_targets['snack']} kcal")
            print(f"   Dinner: {meal_targets['dinner']} kcal")
            print(f"   Total target: {sum(meal_targets.values())} kcal")
            
            # Generate menu menggunakan greedy algorithm
            menu_plan = self.optimizer.optimize_full_menu(user_profile, meal_targets)
            
            if menu_plan:
                self.last_result = menu_plan
                
                # Print results
                print(f"\n✅ Greedy Algorithm: Menu generated successfully!")
                print(f"   Total daily calories: {menu_plan.total_daily_calories:.0f} kcal")
                print(f"   Total daily protein: {menu_plan.total_daily_protein_g:.1f}g")
                print(f"   Total daily carbs: {menu_plan.total_daily_carb_g:.1f}g")
                print(f"   Total daily fat: {menu_plan.total_daily_fat_g:.1f}g")
                print(f"   Feasible: {'✅ YES' if menu_plan.feasible else '⚠️  NO'}")
                
                if menu_plan.violations:
                    print(f"   Violations: {len(menu_plan.violations)}")
                    for violation in menu_plan.violations[:3]:
                        print(f"     - {violation}")
                    if len(menu_plan.violations) > 3:
                        print(f"     ... and {len(menu_plan.violations) - 3} more")
                
                return menu_plan
            else:
                print("❌ Greedy Algorithm: Failed to generate menu (insufficient candidates)")
                return None
        
        except Exception as e:
            print(f"❌ Greedy Algorithm error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_last_result(self) -> Optional[MenuPlan]:
        """Return last generated MenuPlan"""
        return self.last_result


# Singleton untuk convenience
_instance = None

def get_greedy_algorithm() -> GreedyAlgorithmInterface:
    """Get or create singleton instance"""
    global _instance
    if _instance is None:
        _instance = GreedyAlgorithmInterface()
    return _instance


__all__ = ['GreedyAlgorithmInterface', 'get_greedy_algorithm']


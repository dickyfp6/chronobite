"""
Interface for Greedy Algorithm to connect with NutritionService.
Standardizes input from system space to algorithm space.

REDESIGNED ARCHITECTURE:
- Phase 1: Food Selection (generate diverse candidates)
- Phase 2: Portion Optimization (calculate realistic portions + scale nutrients)
- Phase 3: Post-Selection Portion Rebalancing (optional, after user substitutions)
"""

import sys
import os
import pandas as pd
from typing import Dict, List, Any, Optional

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from meal_schema import MenuPlan
from greedy_optimizer import GreedyOptimizer
from portion_rebalancer import PortionRebalancer

class GreedyAlgorithmInterface:
    def __init__(self, food_database: pd.DataFrame, constraint_bag: Dict):
        """
        Initialize the interface with data from NutritionService
        
        Args:
            food_database: Complete food database (per-100g basis)
            constraint_bag: Nutrition constraints and guidelines
        """
        self.food_db = food_database
        self.constraint_bag = constraint_bag
        self.optimizer = GreedyOptimizer(food_database, constraint_bag)
        print("[OK] Greedy Algorithm Interface initialized (DSS Architecture)")
    
    def initialize(self, food_database: pd.DataFrame, constraint_bag: Dict):
        """Reinitialize with new data"""
        self.food_db = food_database
        self.constraint_bag = constraint_bag
        self.optimizer.initialize(food_database, constraint_bag)
    
    def generate_menu_plan(self, user_profile: Dict, tdee: float) -> Optional[MenuPlan]:
        """
        PHASE 1 + 2: Generate complete menu plan using TDEE.
        
        The optimizer will:
        1. Calculate meal targets from TDEE using validated percentages
        2. Generate diverse food candidates for each course
        3. Optimize portions and scale all nutrients
        
        Args:
            user_profile: User demographic and health info
            tdee: Total Daily Energy Expenditure in kcal
        
        Returns:
            MenuPlan with all courses and scaled nutrients, or None if failed
        """
        print("\n[GENERAT] Greedy Algorithm (DSS): Generating menu plan")
        print(f"   User: {user_profile.get('age', '?')}y {user_profile.get('gender', '?')}")
        print(f"   TDEE: {tdee:.0f} kcal")
        
        try:
            menu_plan = self.optimizer.generate_menu(user_profile, tdee)
            
            if menu_plan:
                print(f"\n[OK] Menu generated successfully")
                print(f"   Daily Total: {menu_plan.total_daily_calories:.0f} kcal")
                print(f"   Protein: {menu_plan.total_daily_protein_g:.1f}g")
            
            return menu_plan
            
        except Exception as e:
            print(f"[ERROR] Greedy Algorithm error: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def rebalance_portions(
        self,
        breakfast,
        lunch,
        dinner,
        snack,
        target_nutrition: Dict[str, float],
        current_nutrition: Dict[str, float]
    ):
        """
        PHASE 3: Post-selection portion rebalancing.
        
        After user makes substitutions (e.g., selects Water instead of drink),
        adjust portions of remaining foods to recover nutritional deficits.
        
        IMPORTANT: Does NOT change which foods are selected, only portions.
        
        Args:
            breakfast, lunch, dinner, snack: Current meals after substitutions
            target_nutrition: Target daily nutrition
            current_nutrition: Current nutrition after substitutions
        
        Returns:
            PortionRebalanceResult with before/after comparison
        """
        print("\n[REBALANCE] Portion Rebalancing: Recovering nutritional deficits...")
        
        result = PortionRebalancer.rebalance_menu(
            breakfast, lunch, dinner, snack,
            target_nutrition, current_nutrition
        )
        
        print(f"   Before: Energy {result.nutrition_coverage_before.get('energy', 0):.0f}%")
        print(f"   After: Energy {result.nutrition_coverage_after.get('energy', 0):.0f}%")
        print(f"   Changes: {len(result.rebalanced_items)} portions adjusted")
        
        return result


def get_greedy_algorithm(food_database: pd.DataFrame, constraint_bag: Dict) -> GreedyAlgorithmInterface:
    """Factory function for integration"""
    return GreedyAlgorithmInterface(food_database, constraint_bag)

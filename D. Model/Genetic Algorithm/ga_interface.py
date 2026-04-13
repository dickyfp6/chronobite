"""
Genetic Algorithm Interface - REDESIGNED
Integrate GA dengan NutritionService dan output formatting
"""

import pandas as pd
from typing import Dict, Optional, List

from ga_optimizer import GeneticAlgorithmOptimizer
from ga_output_formatter import GeneticAlgorithmOutputFormatter, MenuPlan


class GeneticAlgorithmInterface:
    """
    High-level interface untuk GA optimization
    Orchestrates optimization + output formatting
    """
    
    def __init__(self):
        """Initialize interface"""
        self.food_database = None
        self.guidelines = None
        self.last_result = None
        self.convergence_stats = None
    
    def initialize(
        self,
        food_database: pd.DataFrame,
        nutrition_guidelines: Dict,
        verbose: bool = False
    ) -> bool:
        """
        Initialize dengan data dari NutritionService
        
        Args:
            food_database: DataFrame dengan foods (fdc_id, food_name, nutrients)
            nutrition_guidelines: Guidelines dict dari NutritionService
            verbose: Print messages
        
        Returns:
            True jika success
        """
        try:
            if verbose:
                print("[GA] Initializing Genetic Algorithm...")
            
            # Validate database
            required_cols = ['fdc_id', 'food_name', 'energy_kcal']
            if not all(col in food_database.columns for col in required_cols):
                print("[ERROR] Food database missing required columns")
                return False
            
            self.food_database = food_database
            self.guidelines = nutrition_guidelines
            
            if verbose:
                print(f"[OK] GA initialized with {len(food_database)} foods")
            
            return True
        
        except Exception as e:
            print(f"[ERROR] GA initialization failed: {e}")
            return False
    
    def generate_menu_plan(
        self,
        user_tdee: float,
        meal_distribution: Dict,
        cuisine_preferences: Optional[List[str]] = None,
        max_generations: int = 100,
        population_size: int = 50,
        verbose: bool = True
    ) -> Optional[MenuPlan]:
        """
        Generate complete menu plan dengan GA
        
        Process:
        1. Initialize GA optimizer
        2. Run optimization untuk find best chromosome
        3. Format output ke MenuPlan
        4. Return dengan alternatives per slot
        
        Args:
            user_tdee: User's TDEE
            meal_distribution: {meal: fraction, ...}
            cuisine_preferences: Filter to these cuisines
            max_generations: GA generations
            population_size: GA population size
            verbose: Print progress
        
        Returns:
            MenuPlan dengan recommendations
        """
        
        try:
            if verbose:
                print("\n" + "="*70)
                print("[GA] GENETIC ALGORITHM OPTIMIZATION")
                print("="*70)
                print(f"Target TDEE: {user_tdee:.0f} kcal")
                print(f"Population: {population_size} | Generations: {max_generations}")
            
            # Filter database by cuisine if needed
            if self.food_database is None:
                print("[ERROR] Food database not initialized")
                return None
                
            db_filtered = self.food_database.copy()
            if cuisine_preferences:
                if 'cuisine_label' in db_filtered.columns:
                    db_filtered = db_filtered[
                        db_filtered['cuisine_label'].isin(cuisine_preferences)
                    ]
                    if db_filtered.empty:
                        print("[WARN] No foods matching cuisine preferences, using all foods")
                        db_filtered = self.food_database.copy()
            
            # Initialize optimizer
            if self.guidelines is None:
                print("[ERROR] Guidelines not initialized. Call initialize() first.")
                return None
                
            optimizer = GeneticAlgorithmOptimizer(
                food_database=db_filtered,
                guidelines=self.guidelines,
                user_tdee=user_tdee,
                population_size=population_size,
                generations=max_generations,
                verbose=verbose
            )
            
            # Run optimization
            best_chromosome, best_fitness = optimizer.optimize()
            
            if best_chromosome is None:
                print("[ERROR] GA optimization failed")
                return None
            
            if verbose:
                print(f"\n[OK] Optimization complete | Best fitness: {best_fitness:.2f}")
                print("  Converting to menu plan...")
            
            # Step 2: Format output (chromosome → MenuPlan)
            menu_plan = GeneticAlgorithmOutputFormatter.format_output(
                chromosome=best_chromosome,
                food_database=db_filtered,
                meal_distribution=meal_distribution,
                user_tdee=user_tdee
            )
            
            # Store results
            self.last_result = menu_plan
            self.convergence_stats = optimizer.get_statistics()
            
            if verbose:
                print(f"[OK] Menu plan generated")
                print(f"  Total Energy: {menu_plan.total_energy:.0f} kcal")
                print(f"  Meals: {', '.join(menu_plan.meals.keys())}")
                print("="*70 + "\n")
            
            return menu_plan
        
        except Exception as e:
            print(f"[ERROR] Menu generation failed: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_convergence_stats(self) -> Optional[Dict]:
        """Get GA convergence statistics"""
        return self.convergence_stats
    
    def get_last_result(self) -> Optional[MenuPlan]:
        """Get last generated menu plan"""
        return self.last_result
        
        if menu['snack']:
            total += menu['snack'].get('energy_kcal', 0)
        
        return total


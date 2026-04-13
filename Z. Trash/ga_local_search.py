"""
Local Search - First Improvement Hill Climbing
Neighborhood = food-level modifications (swap, adjust portion)
"""

import random
from typing import Dict, List, Tuple, Callable, Optional


class LocalSearchOptimizer:
    """First Improvement Hill Climbing untuk chromosome"""
    
    @staticmethod
    def optimize(
        chromosome: Dict,
        food_database,
        calculate_fitness: Callable,
        fitness_args: Dict,
        max_iterations: int = 50,
        max_no_improve: int = 5
    ) -> Dict:
        """
        Apply local search (first improvement) ke chromosome
        
        Algorithm:
        1. For each food dalam chromosome
        2. Generate neighbors (swap to different food, adjust portion)
        3. Evaluate neighbor
        4. If better fitness: accept (first improvement)
        5. Move to next food
        6. Repeat until no improvement atau max iterations
        
        Args:
            chromosome: {meal: {food_id: portion, ...}, ...}
            food_database: DataFrame with all foods
            calculate_fitness: fitness_func(chromosome, ..., **fitness_args) -> float
            fitness_args: Dict dengan kunci: food_database, guidelines, user_tdee, weights
            max_iterations: Max evaluation calls
            max_no_improve: Stop if N consecutive no improvement
        
        Returns:
            Improved chromosome
        """
        
        current_chromosome = chromosome.copy()
        current_fitness = calculate_fitness(current_chromosome, **fitness_args)
        
        evaluation_count = 0
        no_improve_count = 0
        
        # Get all foods dalam chromosome
        while evaluation_count < max_iterations and no_improve_count < max_no_improve:
            
            # Iterate meals
            for meal in current_chromosome.keys():
                food_ids = list(current_chromosome[meal].keys())
                
                # Try modify each food
                for food_id in food_ids:
                    
                    # Neighbor 1: Adjust portion (±15%)
                    current_portion = current_chromosome[meal][food_id]
                    
                    for adjustment in [0.85, 1.15]:  # ±15%
                        neighbor = LocalSearchOptimizer._deep_copy_chromosome(current_chromosome)
                        neighbor[meal][food_id] = current_portion * adjustment
                        
                        # Ensure valid portion
                        if neighbor[meal][food_id] < 50:
                            neighbor[meal][food_id] = 50
                        elif neighbor[meal][food_id] > 300:
                            neighbor[meal][food_id] = 300
                        
                        neighbor_fitness = calculate_fitness(neighbor, **fitness_args)
                        evaluation_count += 1
                        
                        if neighbor_fitness > current_fitness:
                            # First improvement: accept + continue
                            current_chromosome = neighbor
                            current_fitness = neighbor_fitness
                            no_improve_count = 0
                            break  # Move to next food
                        
                        if evaluation_count >= max_iterations:
                            break
                    
                    if evaluation_count >= max_iterations:
                        break
                    
                    # Neighbor 2: Swap to different food (same meal)
                    if evaluation_count < max_iterations - 1:
                        similar_foods = LocalSearchOptimizer._get_similar_foods(
                            food_id, food_database, current_chromosome[meal][food_id], count=3
                        )
                        
                        for alt_food_id in similar_foods:
                            neighbor = LocalSearchOptimizer._deep_copy_chromosome(current_chromosome)
                            neighbor[meal][alt_food_id] = neighbor[meal].pop(food_id)
                            
                            neighbor_fitness = calculate_fitness(neighbor, **fitness_args)
                            evaluation_count += 1
                            
                            if neighbor_fitness > current_fitness:
                                current_chromosome = neighbor
                                current_fitness = neighbor_fitness
                                no_improve_count = 0
                                break
                            
                            if evaluation_count >= max_iterations:
                                break
                    
                    if evaluation_count >= max_iterations:
                        break
                
                if evaluation_count >= max_iterations:
                    break
            
            no_improve_count += 1
        
        return current_chromosome
    
    @staticmethod
    def _deep_copy_chromosome(chromosome: Dict) -> Dict:
        """Create deep copy dari chromosome"""
        return {
            meal: foods_dict.copy()
            for meal, foods_dict in chromosome.items()
        }
    
    @staticmethod
    def _get_similar_foods(
        food_id: str,
        food_database,
        target_portion: float,
        count: int = 5
    ) -> List[str]:
        """
        Get similar foods (similar kcal, macros)
        dalam database untuk potential swaps
        
        Returns:
            List of food_ids (max count items)
        """
        try:
            # Find original food
            if hasattr(food_database, 'loc'):
                # Pandas DataFrame
                original = food_database[food_database['fdc_id'] == food_id]
                if original.empty:
                    return []
                
                original_row = original.iloc[0]
                target_kcal = float(original_row.get('energy_kcal', 0))
                
                # Find similar
                tolerance = target_kcal * 0.15  # ±15%
                similar = food_database[
                    (food_database['energy_kcal'] >= target_kcal - tolerance) &
                    (food_database['energy_kcal'] <= target_kcal + tolerance) &
                    (food_database['fdc_id'] != food_id)
                ]
                
                return similar['fdc_id'].head(count).tolist()
        
        except Exception:
            pass
        
        return []


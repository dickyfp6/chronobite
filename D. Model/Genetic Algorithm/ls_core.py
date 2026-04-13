"""
Local Search Core Implementation

Strategies:
- Greedy: Replace worst item dengan best neighbor
- Hill Climbing: Accept only better solutions
- Simulated Annealing: Sometimes accept worse (escape local optima)
"""

import random
import pandas as pd
from typing import Dict, List, Any, Tuple
from copy import deepcopy
import math
import time

from ga_core import Individual
from meal_similarity import diversity_penalty
from food_slot_mapping import group_food_candidates


class LocalSearcher:
    """Local Search implementation dengan multiple strategies"""
    
    def __init__(
        self,
        food_df: pd.DataFrame,
        meal_budgets: Dict[str, float],
        food_groups: Dict[str, List[Dict]] = None,
        energy_tolerance_pct: float = 10.0,
        similarity_threshold: float = 0.60,
        verbose: bool = True
    ):
        """
        Initialize LocalSearcher
        
        Args:
            food_df: Food dataframe
            meal_budgets: Budget per meal
            food_groups: Grouped food items
            energy_tolerance_pct: Energy tolerance %
            similarity_threshold: Similarity threshold
            verbose: Print progress
        """
        self.food_df = food_df
        self.meal_budgets = meal_budgets
        self.verbose = verbose
        self.energy_tolerance_pct = energy_tolerance_pct
        self.similarity_threshold = similarity_threshold
        
        if food_groups is None:
            self.food_groups = group_food_candidates(food_df.to_dict('records'))
        else:
            self.food_groups = food_groups
        
        self.iterations = 0
        self.improvements = 0
    
    def _evaluate(self, individual: Individual) -> float:
        """Evaluate fitness of individual (same as GA)"""
        fitness = 0
        
        for meal_name in ['breakfast', 'lunch', 'dinner', 'snack']:
            actual_energy = individual.get_meal_energy(meal_name)
            target_energy = self.meal_budgets.get(meal_name, 0)
            
            tolerance = target_energy * (self.energy_tolerance_pct / 100)
            energy_diff = abs(actual_energy - target_energy)
            
            if energy_diff <= tolerance:
                fitness += 100
            else:
                fitness -= (energy_diff ** 1.5) / 10
        
        # Diversity check
        try:
            all_items = individual.get_all_items()
            food_dicts = [
                self.food_df[self.food_df['fdc_id'] == fid].iloc[0].to_dict()
                for fid in all_items if fid in self.food_df['fdc_id'].values
            ]
            
            for i, food_i in enumerate(food_dicts):
                for food_j in food_dicts[i+1:]:
                    penalty = diversity_penalty(food_i, [food_j])
                    if penalty >= self.similarity_threshold:
                        fitness -= 200
        except:
            pass
        
        return fitness
    
    def _get_neighbors(self, individual: Individual, num_neighbors: int = 10) -> List[Individual]:
        """
        Generate neighbor solutions (1-move neighborhood)
        Strategy: Replace 1 item per neighbor
        """
        neighbors = []
        all_items = individual.get_all_items()
        
        if not all_items:
            return neighbors
        
        # Generate neighbors by replacing each item
        for _ in range(min(num_neighbors, len(all_items) * 3)):
            neighbor = individual.copy()
            
            # Pick random item to replace
            meal_names = ['breakfast', 'lunch', 'dinner', 'snack']
            random.shuffle(meal_names)
            
            for meal_name in meal_names:
                if meal_name == 'snack':
                    snack_pool = self.food_groups.get('snack', [])
                    if snack_pool and neighbor.meal_plan['snack'].get('selected'):
                        neighbor.meal_plan['snack']['selected'] = random.choice(snack_pool).get('fdc_id')
                        neighbors.append(neighbor)
                        break
                else:
                    selected = neighbor.meal_plan[meal_name].get('selected', {})
                    categories = ['main_course', 'side_dish', 'drink']
                    random.shuffle(categories)
                    
                    for cat in categories:
                        if cat in selected and selected[cat]:
                            pool = self.food_groups.get(cat, [])
                            if pool:
                                selected[cat] = random.choice(pool).get('fdc_id')
                                neighbors.append(neighbor)
                                break
                    
                    if len(neighbors) > 0:
                        break
        
        return neighbors
    
    def greedy_improvement(
        self,
        initial_solution: Individual,
        max_iterations: int = 50
    ) -> Tuple[Individual, float]:
        """
        Greedy local search: always accept better neighbor
        
        Args:
            initial_solution: Starting point
            max_iterations: Max iterations
        
        Returns:
            (best_solution, best_fitness)
        """
        if self.verbose:
            print(f"\n[LS] Greedy Improvement (max_iter={max_iterations})")
        
        best_solution = initial_solution.copy()
        best_fitness = self._evaluate(best_solution)
        best_solution.fitness = best_fitness
        
        self.iterations = 0
        self.improvements = 0
        
        for iteration in range(max_iterations):
            self.iterations += 1
            neighbors = self._get_neighbors(best_solution, num_neighbors=15)
            
            if not neighbors:
                break
            
            # Evaluate neighbors
            neighbor_fitness = [self._evaluate(n) for n in neighbors]
            best_neighbor_idx = neighbor_fitness.index(max(neighbor_fitness))
            best_neighbor = neighbors[best_neighbor_idx]
            best_neighbor_fitness = neighbor_fitness[best_neighbor_idx]
            
            # Accept if better
            if best_neighbor_fitness > best_fitness:
                best_solution = best_neighbor
                best_fitness = best_neighbor_fitness
                best_solution.fitness = best_fitness
                self.improvements += 1
                
                if self.verbose and (iteration % 10 == 0 or iteration < 5):
                    print(f"  Iter {iteration}: Fitness = {best_fitness:.1f} ✓ (improved)")
            else:
                if self.verbose and iteration < 5:
                    print(f"  Iter {iteration}: Fitness = {best_fitness:.1f} (no improvement)")
                # No improvement - could terminate early
                if iteration % 5 == 0 and iteration > 10:
                    break
        
        if self.verbose:
            print(f"  Greedy Done: {self.improvements} improvements in {self.iterations} iterations")
        
        return best_solution, best_fitness
    
    def hill_climbing(
        self,
        initial_solution: Individual,
        max_iterations: int = 50
    ) -> Tuple[Individual, float]:
        """
        Hill climbing: accept only strictly better moves
        Same as greedy in this implementation
        """
        return self.greedy_improvement(initial_solution, max_iterations)
    
    def simulated_annealing(
        self,
        initial_solution: Individual,
        max_iterations: int = 50,
        initial_temperature: float = 100.0,
        cooling_rate: float = 0.95
    ) -> Tuple[Individual, float]:
        """
        Simulated Annealing: sometimes accept worse solutions
        Helps escape local optima
        
        Args:
            initial_solution: Starting point
            max_iterations: Max iterations
            initial_temperature: Starting temperature
            cooling_rate: How fast to cool (0-1)
        
        Returns:
            (best_solution, best_fitness)
        """
        if self.verbose:
            print(f"\n[LS] Simulated Annealing (max_iter={max_iterations}, T_init={initial_temperature})")
        
        current_solution = initial_solution.copy()
        current_fitness = self._evaluate(current_solution)
        current_solution.fitness = current_fitness
        
        best_solution = current_solution.copy()
        best_fitness = current_fitness
        
        temperature = initial_temperature
        self.iterations = 0
        self.improvements = 0
        
        for iteration in range(max_iterations):
            self.iterations += 1
            neighbors = self._get_neighbors(current_solution, num_neighbors=10)
            
            if not neighbors:
                break
            
            # Pick random neighbor
            neighbor = random.choice(neighbors)
            neighbor_fitness = self._evaluate(neighbor)
            
            # Acceptance probability
            delta = neighbor_fitness - current_fitness
            
            if delta > 0:
                # Accept if better
                current_solution = neighbor
                current_fitness = neighbor_fitness
                
                if current_fitness > best_fitness:
                    best_solution = current_solution.copy()
                    best_fitness = current_fitness
                    self.improvements += 1
                    
                    if self.verbose and iteration < 10:
                        print(f"  Iter {iteration}: Fitness = {best_fitness:.1f} ✓ (improved)")
            else:
                # Accept worse with probability
                probability = math.exp(delta / temperature)
                if random.random() < probability:
                    current_solution = neighbor
                    current_fitness = neighbor_fitness
                    
                    if self.verbose and iteration < 10:
                        print(f"  Iter {iteration}: Fitness = {current_fitness:.1f} ~ (accepted worse)")
            
            # Cool down
            temperature *= cooling_rate
        
        if self.verbose:
            print(f"  SA Done: {self.improvements} improvements in {self.iterations} iterations")
        
        return best_solution, best_fitness

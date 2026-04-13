"""
Genetic Algorithm Core Implementation

Classes:
- Individual: Satu chromosome (meal plan untuk 1 hari)
- Population: Set of individuals
- GeneticAlgorithm: Main GA orchestrator dengan operators
"""

import random
import pandas as pd
from typing import Dict, List, Tuple, Any
from copy import deepcopy
import time

from meal_distribution import get_meal_scheme, calculate_slot_budget, get_default_meal_ratios
from food_slot_mapping import infer_food_role, group_food_candidates
from meal_similarity import diversity_penalty


# ============================================================================
# INDIVIDUAL - Satu Chromosome
# ============================================================================

class Individual:
    """
    Satu solusi (meal plan untuk 1 hari)
    
    Chromosome structure:
    {
        'breakfast': {'main_course': item_id, 'side_dish': item_id, 'drink': item_id},
        'lunch': {...},
        'dinner': {...},
        'snack': item_id
    }
    """
    
    def __init__(self, meal_plan: Dict[str, Any], food_df: pd.DataFrame, food_groups: Dict[str, List[Dict]]):
        self.meal_plan = deepcopy(meal_plan)
        self.food_df = food_df
        self.food_groups = food_groups
        self.fitness = None
        self.created_at = time.time()
    
    def get_all_items(self) -> List[int]:
        """Get flattened list semua food items dalam meal plan"""
        items = []
        for meal_name in ['breakfast', 'lunch', 'dinner', 'snack']:
            meal = self.meal_plan.get(meal_name, {})
            if meal_name == 'snack':
                if meal.get('selected'):
                    items.append(meal['selected'])
            else:
                if meal.get('selected'):
                    items.extend([
                        meal['selected'].get(cat)
                        for cat in ['main_course', 'side_dish', 'drink']
                        if meal['selected'].get(cat)
                    ])
        return [item for item in items if item is not None]
    
    def calculate_total_nutrition(self, nutrient_col: str) -> float:
        """Sum nutrient untuk semua items"""
        items = self.get_all_items()
        total = sum([
            self.food_df[self.food_df['fdc_id'] == fid][nutrient_col].values[0]
            for fid in items if fid in self.food_df['fdc_id'].values
        ])
        return total
    
    def get_meal_energy(self, meal_name: str) -> float:
        """Calculate energy untuk 1 meal"""
        meal = self.meal_plan.get(meal_name, {})
        items = []
        
        if meal_name == 'snack':
            if meal.get('selected'):
                items.append(meal['selected'])
        else:
            if meal.get('selected'):
                items.extend([
                    meal['selected'].get(cat)
                    for cat in ['main_course', 'side_dish', 'drink']
                    if meal['selected'].get(cat)
                ])
        
        items = [item for item in items if item is not None]
        energy = sum([
            self.food_df[self.food_df['fdc_id'] == fid]['energy_kcal'].values[0]
            for fid in items if fid in self.food_df['fdc_id'].values
        ])
        return energy
    
    def evaluate(self):
        """Placeholder evaluate method - actual evaluation done by GeneticAlgorithm"""
        pass  # GeneticAlgorithm handles evaluation via _evaluate_fitness()
    
    def copy(self):
        """Create deep copy of individual"""
        return Individual(self.meal_plan, self.food_df, self.food_groups)
    
    def __str__(self):
        return f"Individual(fitness={self.fitness:.2f})" if self.fitness else "Individual(unevaluated)"


# ============================================================================
# POPULATION - Set of Individuals
# ============================================================================

class Population:
    """Populasi dari N individuals"""
    
    def __init__(self, size: int = 50):
        self.size = size
        self.individuals: List[Individual] = []
    
    def add_individual(self, individual: Individual) -> None:
        """Add individual ke population"""
        self.individuals.append(individual)
    
    def sort_by_fitness(self, ascending: bool = False) -> None:
        """Sort population by fitness"""
        self.individuals.sort(key=lambda x: x.fitness, reverse=not ascending)
    
    def get_best(self) -> Individual:
        """Get best individual"""
        if not self.individuals:
            return None
        return max(self.individuals, key=lambda x: x.fitness)
    
    def get_worst(self) -> Individual:
        """Get worst individual"""
        if not self.individuals:
            return None
        return min(self.individuals, key=lambda x: x.fitness)
    
    def get_average_fitness(self) -> float:
        """Get average fitness"""
        if not self.individuals:
            return 0
        return sum([ind.fitness for ind in self.individuals]) / len(self.individuals)
    
    def __len__(self):
        return len(self.individuals)


# ============================================================================
# GENETIC ALGORITHM - Main Orchestrator
# ============================================================================

class GeneticAlgorithm:
    """
    GA Implementation dengan operators: selection, crossover, mutation
    """
    
    # Default Parameters
    DEFAULT_PARAMS = {
        'population_size': 100,
        'generations': 50,
        'mutation_rate': 0.15,
        'crossover_rate': 0.8,
        'tournament_size': 3,
        'elite_size': 2,
        'energy_tolerance_pct': 10.0,
        'similarity_threshold': 0.60
    }
    
    def __init__(
        self,
        food_df: pd.DataFrame,
        meal_budgets: Dict[str, float],
        food_groups: Dict[str, List[Dict]] = None,
        params: Dict[str, Any] = None,
        verbose: bool = True
    ):
        """
        Initialize GA
        
        Args:
            food_df: Food dataframe
            meal_budgets: {'breakfast': 400, 'lunch': 700, ...}
            food_groups: Grouped food items by role
            params: Override default parameters
            verbose: Print progress
        """
        self.food_df = food_df
        self.meal_budgets = meal_budgets
        self.verbose = verbose
        
        # Initialize food groups if not provided
        if food_groups is None:
            self.food_groups = group_food_candidates(food_df.to_dict('records'))
        else:
            self.food_groups = food_groups
        
        # Set parameters
        self.params = {**self.DEFAULT_PARAMS}
        if params:
            self.params.update(params)
        
        self.population = None
        self.generation = 0
        self.best_fitness_history = []
        self.avg_fitness_history = []
    
    def _create_random_individual(self) -> Individual:
        """Create random individual (random menu selection)"""
        meal_plan = {}
        
        for meal_name in ['breakfast', 'lunch', 'dinner', 'snack']:
            scheme = get_meal_scheme(meal_name)
            
            if meal_name == 'snack':
                # Snack: hanya 1 item dari snack pool
                snack_pool = self.food_groups.get('snack', [])
                if snack_pool:
                    item = random.choice(snack_pool)
                    meal_plan['snack'] = {
                        'budget_kcal': self.meal_budgets.get('snack', 0),
                        'selected': item.get('fdc_id')
                    }
            else:
                # Breakfast/Lunch/Dinner: main + side + drink
                selected = {}
                
                # Main course
                main_pool = self.food_groups.get('main_course', [])
                if main_pool:
                    selected['main_course'] = random.choice(main_pool).get('fdc_id')
                
                # Side dish
                side_pool = self.food_groups.get('side_dish', [])
                if side_pool:
                    selected['side_dish'] = random.choice(side_pool).get('fdc_id')
                
                # Drink (optional)
                drink_pool = self.food_groups.get('drink', [])
                if drink_pool and random.random() < 0.7:  # 70% chance drink
                    selected['drink'] = random.choice(drink_pool).get('fdc_id')
                
                meal_plan[meal_name] = {
                    'budget_kcal': self.meal_budgets.get(meal_name, 0),
                    'selected': selected
                }
        
        return Individual(meal_plan, self.food_df, self.food_groups)
    
    def initialize_population(self) -> None:
        """Generate initial random population"""
        if self.verbose:
            print(f"[GA] Initializing population (size={self.params['population_size']})...")
        
        self.population = Population(self.params['population_size'])
        for _ in range(self.params['population_size']):
            individual = self._create_random_individual()
            self.population.add_individual(individual)
    
    def _evaluate_fitness(self, individual: Individual) -> float:
        """
        Calculate fitness score untuk individual
        
        Fitness components:
        - Energy compliance per meal (±tolerance)
        - Similarity constraint adherence
        - Nutrient balance
        """
        fitness = 0
        
        meal_names = ['breakfast', 'lunch', 'dinner', 'snack']
        energy_tolerance = self.params['energy_tolerance_pct']
        
        for meal_name in meal_names:
            actual_energy = individual.get_meal_energy(meal_name)
            target_energy = self.meal_budgets.get(meal_name, 0)
            
            # Energy compliance score
            tolerance = target_energy * (energy_tolerance / 100)
            energy_diff = abs(actual_energy - target_energy)
            
            if energy_diff <= tolerance:
                fitness += 100  # Perfect energy match
            else:
                # Penalize energy mismatch
                fitness -= (energy_diff ** 1.5) / 10
        
        # Diversity bonus (items not too similar)
        try:
            all_items = individual.get_all_items()
            food_dicts = [
                self.food_df[self.food_df['fdc_id'] == fid].iloc[0].to_dict()
                for fid in all_items if fid in self.food_df['fdc_id'].values
            ]
            
            # Check diversity
            diversity_score = 0
            for i, food_i in enumerate(food_dicts):
                for food_j in food_dicts[i+1:]:
                    penalty = diversity_penalty(food_i, [food_j])
                    if penalty < self.params['similarity_threshold']:
                        diversity_score += 20  # Good diversity
                    else:
                        fitness -= 200  # Penalize similarity violation
        except:
            pass  # Skip if error in diversity check
        
        return fitness
    
    def evaluate_population(self) -> None:
        """Evaluate fitness untuk semua individual dalam self.population"""
        for individual in self.population.individuals:
            if individual.fitness is None:
                individual.fitness = self._evaluate_fitness(individual)
    
    def evaluate_individuals(self, individuals: List[Individual]) -> None:
        """Evaluate fitness untuk list of individuals (without assigning to population)"""
        for individual in individuals:
            if individual.fitness is None:
                individual.fitness = self._evaluate_fitness(individual)
    
    def selection_tournament(self, population=None, tournament_size: int = 3) -> Individual:
        """
        Tournament selection: pick best dari random tournament
        
        Args:
            population: Optional Population object (if None, uses self.population)
            tournament_size: Size of tournament
        
        Returns:
            Best individual from tournament
        """
        if population is None:
            population = self.population
        
        tournament = random.sample(population.individuals, tournament_size)
        return max(tournament, key=lambda x: x.fitness)
    
    def crossover(self, parent1: Individual, parent2: Individual) -> Individual:
        """
        Crossover: combine 2 parents
        Strategy: untuk setiap meal, pick random parent
        """
        child_meal_plan = {}
        
        for meal_name in ['breakfast', 'lunch', 'dinner', 'snack']:
            parent = random.choice([parent1, parent2])
            child_meal_plan[meal_name] = deepcopy(parent.meal_plan[meal_name])
        
        return Individual(child_meal_plan, self.food_df, self.food_groups)
    
    def mutation(self, individual: Individual, mutation_rate: float = None) -> None:
        """
        Mutation: random change di meal plan
        Strategy: replace random item dengan random item dari pool
        """
        if mutation_rate is None:
            mutation_rate = self.params['mutation_rate']
        
        meal_names = ['breakfast', 'lunch', 'dinner', 'snack']
        
        for meal_name in meal_names:
            if random.random() < mutation_rate:
                if meal_name == 'snack':
                    # Mutate snack item
                    snack_pool = self.food_groups.get('snack', [])
                    if snack_pool:
                        individual.meal_plan['snack']['selected'] = random.choice(snack_pool).get('fdc_id')
                else:
                    # Mutate meal items (main, side, or drink)
                    selected = individual.meal_plan[meal_name].get('selected', {})
                    
                    if random.random() < 0.5 and 'main_course' in selected:
                        main_pool = self.food_groups.get('main_course', [])
                        if main_pool:
                            selected['main_course'] = random.choice(main_pool).get('fdc_id')
                    
                    if random.random() < 0.5 and 'side_dish' in selected:
                        side_pool = self.food_groups.get('side_dish', [])
                        if side_pool:
                            selected['side_dish'] = random.choice(side_pool).get('fdc_id')
                    
                    if random.random() < 0.5 and 'drink' in selected:
                        drink_pool = self.food_groups.get('drink', [])
                        if drink_pool:
                            selected['drink'] = random.choice(drink_pool).get('fdc_id')
    
    def run(self) -> Individual:
        """
        Run GA untuk N generations
        Return: best individual found
        """
        if self.verbose:
            print(f"\n{'='*70}")
            print(f"GENETIC ALGORITHM - INITIALIZATION PHASE")
            print(f"{'='*70}")
            print(f"Population: {self.params['population_size']}")
            print(f"Generations: {self.params['generations']}")
            print(f"Mutation Rate: {self.params['mutation_rate']}")
            print(f"Crossover Rate: {self.params['crossover_rate']}")
        
        self.initialize_population()
        self.evaluate_population()
        
        if self.verbose:
            print(f"\n{'='*70}")
            print(f"GENETIC ALGORITHM - EVOLUTION PHASE")
            print(f"{'='*70}")
        
        for gen in range(self.params['generations']):
            self.generation = gen
            
            # Evaluate population
            self.evaluate_population()
            
            # Record history
            self.population.sort_by_fitness(ascending=False)
            best = self.population.get_best()
            avg = self.population.get_average_fitness()
            
            self.best_fitness_history.append(best.fitness)
            self.avg_fitness_history.append(avg)
            
            if self.verbose and (gen % 10 == 0 or gen == self.params['generations'] - 1):
                print(f"Gen {gen:3d}: Best={best.fitness:8.1f}, Avg={avg:8.1f}")
            
            # Create next generation
            new_population = Population(self.params['population_size'])
            
            # Elitism: keep top individuals
            elite_size = self.params['elite_size']
            for i in range(elite_size):
                if i < len(self.population):
                    new_population.add_individual(self.population.individuals[i].copy())
            
            # Generate offspring
            while len(new_population) < self.params['population_size']:
                # Selection
                parent1 = self.selection_tournament(self.population, self.params['tournament_size'])
                parent2 = self.selection_tournament(self.population, self.params['tournament_size'])
                
                # Crossover
                if random.random() < self.params['crossover_rate']:
                    child = self.crossover(parent1, parent2)
                else:
                    child = random.choice([parent1, parent2]).copy()
                
                # Mutation
                self.mutation(child)
                
                new_population.add_individual(child)
            
            self.population = new_population
        
        # Final evaluation
        self.evaluate_population()
        best = self.population.get_best()
        
        if self.verbose:
            print(f"\n{'='*70}")
            print(f"GA BEST SOLUTION: Fitness = {best.fitness:.1f}")
            print(f"{'='*70}\n")
        
        return best

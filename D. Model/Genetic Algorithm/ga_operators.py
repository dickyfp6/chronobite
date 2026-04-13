"""
Genetic Operators: Mutation, Crossover, Selection
Designed untuk chromosome format: {meal: {food_id: portion, ...}, ...}
"""

import random
from typing import Dict, List, Tuple, Optional
from ga_chromosome import ChromosomeOperations


class GeneticOperators:
    """Genetic operators untuk new chromosome format"""
    
    # ===== MUTATION OPERATORS =====
    
    @staticmethod
    def mutate_add_food(
        chromosome: Dict,
        food_database_by_meal: Dict[str, List[str]],
        mutation_rate: float = 0.5
    ) -> Dict:
        """
        Mutasi: Add satu food baru ke random meal
        
        Args:
            chromosome: Current chromosome
            food_database_by_meal: Available foods per meal
            mutation_rate: Probability untuk apply mutation
        
        Returns:
            Mutated chromosome copy
        """
        if random.random() > mutation_rate:
            return ChromosomeOperations.copy(chromosome)
        
        result = ChromosomeOperations.copy(chromosome)
        
        try:
            # Random pilih meal
            meal = random.choice(ChromosomeOperations.MEALS)
            
            if meal not in food_database_by_meal:
                return result
            
            available_foods = food_database_by_meal[meal]
            if not available_foods:
                return result
            
            # Random pilih food (avoid duplicate)
            current_foods = set(result[meal].keys())
            available = [f for f in available_foods if f not in current_foods]
            
            if not available:
                available = available_foods  # Use any if all current
            
            food_id = random.choice(available)
            portion = random.uniform(80, 250)
            
            result[meal][food_id] = portion
        
        except Exception:
            pass
        
        return result
    
    @staticmethod
    def mutate_remove_food(
        chromosome: Dict,
        mutation_rate: float = 0.3
    ) -> Dict:
        """
        Mutasi: Remove satu food dari random meal
        
        Constraint: Each meal keeps ≥ 1 food
        
        Returns:
            Mutated chromosome copy (jika valid, else original)
        """
        if random.random() > mutation_rate:
            return ChromosomeOperations.copy(chromosome)
        
        result = ChromosomeOperations.copy(chromosome)
        
        try:
            # Get meals yang punya > 1 food (removable)
            removable_meals = [
                meal for meal in ChromosomeOperations.MEALS
                if len(result[meal]) > 1
            ]
            
            if not removable_meals:
                return result
            
            meal = random.choice(removable_meals)
            food_id = random.choice(list(result[meal].keys()))
            
            del result[meal][food_id]
        
        except Exception:
            pass
        
        return result
    
    @staticmethod
    def mutate_adjust_portion(
        chromosome: Dict,
        mutation_rate: float = 0.6
    ) -> Dict:
        """
        Mutasi: Adjust portion dari existing food ±10-30%
        
        Returns:
            Mutated chromosome copy
        """
        if random.random() > mutation_rate:
            return ChromosomeOperations.copy(chromosome)
        
        result = ChromosomeOperations.copy(chromosome)
        
        try:
            # Get all foods
            all_foods = ChromosomeOperations.get_all_foods(result)
            if not all_foods:
                return result
            
            meal, food_id, current_portion = random.choice(all_foods)
            
            # Adjust ±10-30%
            adjustment = random.uniform(0.7, 1.3)
            new_portion = current_portion * adjustment
            new_portion = max(50, min(300, new_portion))
            
            result[meal][food_id] = new_portion
        
        except Exception:
            pass
        
        return result
    
    @staticmethod
    def mutate_swap_food(
        chromosome: Dict,
        food_database_by_meal: Dict[str, List[str]],
        mutation_rate: float = 0.4
    ) -> Dict:
        """
        Mutasi: Swap satu food dengan food lain (similarish)
        
        Keep portion, replace food_id
        
        Returns:
            Mutated chromosome copy
        """
        if random.random() > mutation_rate:
            return ChromosomeOperations.copy(chromosome)
        
        result = ChromosomeOperations.copy(chromosome)
        
        try:
            all_foods = ChromosomeOperations.get_all_foods(result)
            if not all_foods:
                return result
            
            meal, old_food_id, portion = random.choice(all_foods)
            
            if meal not in food_database_by_meal:
                return result
            
            available_foods = food_database_by_meal[meal]
            # Prefer foods not in current meal
            current_foods = set(result[meal].keys())
            alternatives = [f for f in available_foods if f != old_food_id and f not in current_foods]
            
            if not alternatives:
                alternatives = [f for f in available_foods if f != old_food_id]
            
            if not alternatives:
                return result
            
            new_food_id = random.choice(alternatives)
            
            del result[meal][old_food_id]
            result[meal][new_food_id] = portion
        
        except Exception:
            pass
        
        return result
    
    @staticmethod
    def apply_mutations(
        chromosome: Dict,
        food_database_by_meal: Dict[str, List[str]],
        num_mutations: int = 2
    ) -> Dict:
        """
        Apply random mutations sequentially
        
        Args:
            num_mutations: Number of mutation operations (1-3 typically)
        
        Returns:
            Mutated chromosome
        """
        result = ChromosomeOperations.copy(chromosome)
        num_mutations = random.randint(1, num_mutations)
        
        mutation_ops = [
            lambda c: GeneticOperators.mutate_add_food(c, food_database_by_meal, 0.7),
            lambda c: GeneticOperators.mutate_remove_food(c, 0.4),
            lambda c: GeneticOperators.mutate_adjust_portion(c, 0.7),
            lambda c: GeneticOperators.mutate_swap_food(c, food_database_by_meal, 0.5)
        ]
        
        for _ in range(num_mutations):
            mutation_op = random.choice(mutation_ops)
            result = mutation_op(result)
        
        return result
    
    # ===== CROSSOVER OPERATORS =====
    
    @staticmethod
    def crossover_meal_based(
        parent1: Dict,
        parent2: Dict,
        crossover_rate: float = 0.8
    ) -> Dict:
        """
        Crossover: Inherit meals dari parents
        
        For each meal: random choose dari parent1 OR parent2
        
        Example:
        Parent1: breakfast={food1, food2}, lunch={food3}
        Parent2: breakfast={food4}, lunch={food5, food6}
        
        Random: breakfast from P1, lunch from P2
        Child: breakfast={food1, food2}, lunch={food5, food6}
        
        Returns:
            child (single child)
        """
        if random.random() > crossover_rate:
            return ChromosomeOperations.copy(parent1)
        
        child = ChromosomeOperations.get_empty()
        
        for meal in ChromosomeOperations.MEALS:
            if random.random() < 0.5:
                # Child dari P1
                child[meal] = ChromosomeOperations.copy(parent1.get(meal, {}))
            else:
                # Child dari P2
                child[meal] = ChromosomeOperations.copy(parent2.get(meal, {}))
        
        return child
    
    @staticmethod
    def crossover_uniform(
        parent1: Dict,
        parent2: Dict,
        crossover_rate: float = 0.8
    ) -> Tuple[Dict, Dict]:
        """
        Uniform crossover: For each food, random choose dari parent1 or parent2
        
        More mixing than meal-based
        
        Returns:
            (child1, child2)
        """
        if random.random() > crossover_rate:
            return ChromosomeOperations.copy(parent1), ChromosomeOperations.copy(parent2)
        
        child1 = ChromosomeOperations.get_empty()
        child2 = ChromosomeOperations.get_empty()
        
        all_meals = set()
        for parent in [parent1, parent2]:
            all_meals.update(parent.keys())
        
        for meal in all_meals:
            foods_p1 = parent1.get(meal, {})
            foods_p2 = parent2.get(meal, {})
            
            all_foods = set(foods_p1.keys()) | set(foods_p2.keys())
            
            for food_id in all_foods:
                if random.random() < 0.5:
                    if food_id in foods_p1:
                        child1[meal][food_id] = foods_p1[food_id]
                    if food_id in foods_p2:
                        child2[meal][food_id] = foods_p2[food_id]
                else:
                    if food_id in foods_p2:
                        child1[meal][food_id] = foods_p2[food_id]
                    if food_id in foods_p1:
                        child2[meal][food_id] = foods_p1[food_id]
        
        # Ensure each meal has min 1 food
        for meal in ChromosomeOperations.MEALS:
            if not child1.get(meal):
                child1[meal] = ChromosomeOperations.copy(parent1.get(meal, {}))
            if not child2.get(meal):
                child2[meal] = ChromosomeOperations.copy(parent2.get(meal, {}))
        
        return child1, child2
    
    # ===== SELECTION OPERATORS =====
    
    @staticmethod
    def tournament_selection(
        population: List[Dict],
        fitness_scores: List[float],
        tournament_size: int = 3
    ) -> Dict:
        """
        Tournament selection: Pick tournament_size random individuals,
        return yang fitness-nya best
        
        Returns:
            Selected chromosome copy
        """
        candidates = random.sample(
            range(len(population)),
            min(tournament_size, len(population))
        )
        
        best_idx = max(candidates, key=lambda i: fitness_scores[i])
        return ChromosomeOperations.copy(population[best_idx])
    
    @staticmethod
    def get_elite(
        population: List[Dict],
        fitness_scores: List[float],
        elite_size: int
    ) -> Tuple[List[Dict], List[float]]:
        """
        Elitism: Get top elite_size individuals
        
        Returns:
            (elite_population, elite_fitness_scores)
        """
        sorted_indices = sorted(
            range(len(population)),
            key=lambda i: fitness_scores[i],
            reverse=True
        )
        
        elite_indices = sorted_indices[:elite_size]
        elite_pop = [ChromosomeOperations.copy(population[i]) for i in elite_indices]
        elite_fit = [fitness_scores[i] for i in elite_indices]
        
        return elite_pop, elite_fit
    
    @staticmethod
    def create_offspring(
        population: List[Dict],
        fitness_scores: List[float],
        food_database_by_meal: Dict[str, List[str]],
        offspring_size: int,
        crossover_type: str = 'meal_based'
    ) -> List[Dict]:
        """
        Create offspring melalui selection, crossover, mutation
        
        Args:
            crossover_type: 'meal_based' or 'uniform'
        
        Returns:
            List of new offspring
        """
        offspring = []
        
        crossover_fn = (
            GeneticOperators.crossover_meal_based
            if crossover_type == 'meal_based'
            else GeneticOperators.crossover_uniform
        )
        
        while len(offspring) < offspring_size:
            # Selection
            parent1 = GeneticOperators.tournament_selection(population, fitness_scores)
            parent2 = GeneticOperators.tournament_selection(population, fitness_scores)
            
            # Crossover
            child1, child2 = crossover_fn(parent1, parent2)
            
            # Mutation
            child1 = GeneticOperators.apply_mutations(child1, food_database_by_meal, num_mutations=2)
            if len(offspring) < offspring_size:
                child2 = GeneticOperators.apply_mutations(child2, food_database_by_meal, num_mutations=2)
            
            offspring.append(child1)
            if len(offspring) < offspring_size:
                offspring.append(child2)
        
        return offspring[:offspring_size]


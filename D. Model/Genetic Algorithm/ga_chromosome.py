"""
Chromosome Representation and Operations
Chromosome = {meal: {food_id: portion_gram, ...}, ...}
Represents complete daily meal plan as internal optimization format
"""

import random
from typing import Dict, List, Tuple, Optional
from copy import deepcopy


class ChromosomeOperations:
    """
    Chromosome representation untuk GA optimization
    Format: {
        'breakfast': {food_id: portion, ...},
        'lunch': {food_id: portion, ...},
        'dinner': {food_id: portion, ...},
        'snack': {food_id: portion, ...}
    }
    """
    
    MEALS = ['breakfast', 'lunch', 'dinner', 'snack']
    DEFAULT_PORTION_RANGE = (80, 250)  # grams
    
    @staticmethod
    def get_empty() -> Dict:
        """Create empty chromosome"""
        return {
            'breakfast': {},
            'lunch': {},
            'dinner': {},
            'snack': {}
        }
    
    @staticmethod
    def is_valid(chromosome: Dict) -> Tuple[bool, str]:
        """
        Validate chromosome
        
        Rules:
        - Must have 4 meals (breakfast, lunch, dinner, snack)
        - Each meal must have ≥ 1 food
        - Each food_id must be string or number
        - Each portion must be number > 0
        
        Returns:
            (is_valid: bool, error_message: str)
        """
        if not isinstance(chromosome, dict):
            return False, "Chromosome must be dict"
        
        for meal in ChromosomeOperations.MEALS:
            if meal not in chromosome:
                return False, f"Missing meal: {meal}"
            
            if not isinstance(chromosome[meal], dict):
                return False, f"{meal} must be dict"
            
            if len(chromosome[meal]) == 0:
                return False, f"{meal} must have ≥ 1 food"
            
            for food_id, portion in chromosome[meal].items():
                if not isinstance(food_id, (str, int)):
                    return False, f"Food ID must be string or int, got {type(food_id)}"
                
                if not isinstance(portion, (int, float)):
                    return False, f"Portion must be number, got {type(portion)}"
                
                if portion <= 0:
                    return False, f"Portion must be > 0, got {portion}"
        
        return True, ""
    
    @staticmethod
    def initialize_random(
        food_database_by_meal: Dict[str, List[str]],
        target_calories_per_meal: Optional[Dict[str, float]] = None,
        max_attempts: int = 10
    ) -> Optional[Dict]:
        """
        Initialize random valid chromosome
        
        Args:
            food_database_by_meal: {
                'breakfast': ['FOOD_001', 'FOOD_089', ...],
                'lunch': [...],
                ...
            }
            target_calories_per_meal: {
                'breakfast': 500,
                'lunch': 700,
                'dinner': 600,
                'snack': 200
            } (optional, for smarter initialization)
            max_attempts: Max attempts to generate valid
        
        Returns:
            Valid chromosome atau None jika gagal
        """
        
        for attempt in range(max_attempts):
            chromosome = ChromosomeOperations.get_empty()
            
            try:
                for meal in ChromosomeOperations.MEALS:
                    if meal not in food_database_by_meal:
                        continue
                    
                    available_foods = food_database_by_meal[meal]
                    if not available_foods:
                        continue
                    
                    # Random select 1-3 foods per meal
                    num_foods = random.randint(1, min(3, len(available_foods)))
                    selected_foods = random.sample(available_foods, num_foods)
                    
                    for food_id in selected_foods:
                        # Random portion
                        portion = random.uniform(80, 250)
                        chromosome[meal][food_id] = portion
                
                # Validate
                is_valid, error_msg = ChromosomeOperations.is_valid(chromosome)
                if is_valid:
                    return chromosome
            
            except Exception as e:
                continue
        
        # Fallback: Create minimal valid chromosome
        chromosome = ChromosomeOperations.get_empty()
        for meal in ChromosomeOperations.MEALS:
            if meal in food_database_by_meal and food_database_by_meal[meal]:
                food_id = random.choice(food_database_by_meal[meal])
                portion = random.uniform(100, 200)
                chromosome[meal][food_id] = portion
        
        # Return if valid, otherwise None
        is_valid, _ = ChromosomeOperations.is_valid(chromosome)
        return chromosome if is_valid else None
    
    @staticmethod
    def copy(chromosome: Dict) -> Dict:
        """Deep copy chromosome"""
        return deepcopy(chromosome)
    
    @staticmethod
    def get_all_foods(chromosome: Dict) -> List[Tuple[str, str, float]]:
        """
        Get all foods dalam chromosome
        
        Returns:
            List of (meal, food_id, portion) tuples
        """
        foods = []
        for meal, foods_dict in chromosome.items():
            for food_id, portion in foods_dict.items():
                foods.append((meal, food_id, portion))
        return foods
    
    @staticmethod
    def count_foods(chromosome: Dict) -> int:
        """Get total number of foods dalam chromosome"""
        count = 0
        for meal_val in chromosome.values():
            if isinstance(meal_val, dict):
                count += len(meal_val)
        return count
    
    @staticmethod
    def get_meals_by_size(meal_name: str, chromosome: Dict) -> Dict[str, float]:
        """
        Get foods dalam specific meal, sorted by portion (descending)
        
        Useful untuk identify main, side, drink
        
        Returns:
            {food_id: portion, ...} sorted by portion DESC
        """
        if meal_name not in chromosome:
            return {}
        
        meal_dict = chromosome[meal_name]
        if not isinstance(meal_dict, dict):
            return {}
        
        sorted_foods = sorted(meal_dict.items(), key=lambda x: x[1], reverse=True)
        return {food_id: portion for food_id, portion in sorted_foods}
    
    @staticmethod
    def add_food(
        chromosome: Dict,
        meal: str,
        food_id: str,
        portion: Optional[float] = None
    ) -> Dict:
        """
        Add food ke chromosome
        
        Args:
            chromosome: Source chromosome
            meal: Meal name (breakfast/lunch/dinner/snack)
            food_id: Food to add
            portion: Portion in grams (random if None)
        
        Returns:
            Modified chromosome copy
        """
        if meal not in ChromosomeOperations.MEALS:
            raise ValueError(f"Invalid meal: {meal}")
        
        result = deepcopy(chromosome)
        
        if portion is None:
            portion = random.uniform(80, 250)
        
        if portion is None:
            portion = random.uniform(80, 250)
        
        result[meal][food_id] = portion
        return result
    
    @staticmethod
    def remove_food(
        chromosome: Dict,
        meal: str,
        food_id: str
    ) -> Optional[Dict]:
        """
        Remove food dari chromosome
        
        Constraint: Each meal must keep ≥ 1 food
        
        Returns:
            Modified chromosome jika valid, None jika would violate constraint
        """
        if meal not in ChromosomeOperations.MEALS:
            return None
        
        if meal not in chromosome or food_id not in chromosome[meal]:
            return None
        
        # Check constraint
        if len(chromosome[meal]) <= 1:
            return None  # Would leave meal empty
        
        result = deepcopy(chromosome)
        del result[meal][food_id]
        
        return result
    
    @staticmethod
    def adjust_portion(
        chromosome: Dict,
        meal: str,
        food_id: str,
        new_portion: float
    ) -> Optional[Dict]:
        """
        Adjust portion dari existing food
        
        Args:
            new_portion: New portion in grams (clipped to 50-300)
        
        Returns:
            Modified chromosome jika valid, None jika invalid
        """
        if meal not in ChromosomeOperations.MEALS:
            return None
        
        if meal not in chromosome or food_id not in chromosome[meal]:
            return None
        
        # Clamp to valid range
        new_portion = max(50, min(300, new_portion))
        
        result = deepcopy(chromosome)
        result[meal][food_id] = new_portion
        
        return result
    
    @staticmethod
    def swap_food(
        chromosome: Dict,
        meal: str,
        old_food_id: str,
        new_food_id: str,
        new_portion: Optional[float] = None
    ) -> Optional[Dict]:
        """
        Replace satu food dengan food lain
        
        Keep portion sama kecuali new_portion specified
        
        Returns:
            Modified chromosome jika valid
        """
        if meal not in ChromosomeOperations.MEALS:
            return None
        
        if meal not in chromosome or old_food_id not in chromosome[meal]:
            return None
        
        result = deepcopy(chromosome)
        old_portion = result[meal][old_food_id]
        
        del result[meal][old_food_id]
        
        if new_portion is None:
            new_portion = old_portion
        
        result[meal][new_food_id] = new_portion
        
        return result
    
    @staticmethod
    def get_total_portion(chromosome: Dict) -> float:
        """Calculate total portion dalam chromosome (grams)"""
        total = 0
        for foods_dict in chromosome.values():
            if isinstance(foods_dict, dict):
                total += sum(foods_dict.values())
        return total
    
    @staticmethod
    def get_meals_food_count(chromosome: Dict) -> Dict[str, int]:
        """Get jumlah foods per meal"""
        return {
            meal: len(chromosome.get(meal, {}))
            for meal in ChromosomeOperations.MEALS
        }
    
    @staticmethod
    def to_string(chromosome: Dict) -> str:
        """Convert chromosome ke string representation"""
        lines = []
        for meal in ChromosomeOperations.MEALS:
            count = len(chromosome[meal])
            lines.append(f"{meal}: {count} foods")
            for food_id, portion in sorted(chromosome[meal].items()):
                lines.append(f"  - {food_id}: {portion:.0f}g")
        return "\n".join(lines)


"""
IMPROVED CHROMOSOME WITH CATEGORY CONSTRAINTS
Chromosome structure yang strict dengan kategori yang jelas

Format:
{
    'breakfast': {
        'main_course': food_id,      ← Only from main_foods
        'side_dish': food_id,        ← Only from side_foods
        'drink': food_id             ← Only from drink_foods
    },
    'lunch': {...},
    'dinner': {...},
    'snack': food_id                 ← Only from snack_foods
}

Constraints yang dijaga:
- Setiap kategori hanya memilih dari food_ids dengan kategori yang sesuai
- No cross-category selection (tidak boleh ambil drink untuk main_course)
- Respects user cuisine preferences
- Deterministic dan realistis
"""

import random
from typing import Dict, List, Tuple, Optional
from copy import deepcopy
import pandas as pd


class FoodCategoryManager:
    """
    Manager untuk filter makanan berdasarkan kategori
    Memisahkan food database menjadi sub-lists per kategori dan per meal
    """
    
    MEAL_TYPES = ['breakfast', 'lunch', 'dinner']
    SNACK_TYPE = 'snack'
    
    MEAL_CATEGORIES = ['main_course', 'side_dish', 'drink']
    SNACK_CATEGORIES = ['food']  # Snack hanya punya 1 kategori
    
    def __init__(self, food_database: pd.DataFrame):
        """
        Initialize category manager
        
        Args:
            food_database: DataFrame dengan kolom food_category
                Kolom required: food_name, food_category, energy_kcal, dsb
        """
        self.food_database = food_database
        self.food_by_category = {}
        self.food_ids_by_category = {}
        
        # Build category lookups
        self._build_category_maps()
    
    def _build_category_maps(self):
        """
        Buat mapping: category → food_ids
        Juga bisa filter by cuisine preference
        """
        # Kolom yang expected
        if 'food_category' not in self.food_database.columns:
            raise ValueError("Dataset harus punya kolom 'food_category'")
        
        # Group by food_category
        for category in self.food_database['food_category'].unique():
            category_foods = self.food_database[
                self.food_database['food_category'] == category
            ]
            
            # Simpan sebagai list of dicts (untuk feature clarity)
            self.food_by_category[category] = category_foods.to_dict('records')
            
            # Simpan juga sebagai list of food_ids (untuk fast random pick)
            if 'fdc_id' in self.food_database.columns:
                food_ids = category_foods['fdc_id'].tolist()
            else:
                food_ids = category_foods.index.tolist()
            
            self.food_ids_by_category[category] = food_ids
    
    def get_foods_for_category(self, category: str, limit: int = None) -> List:
        """Get foods untuk kategori tertentu"""
        foods = self.food_by_category.get(category, [])
        if limit:
            return foods[:limit]
        return foods
    
    def get_random_food_id(self, category: str) -> any:
        """Pilih random food_id dari kategori dengan filter user preference"""
        food_ids = self.food_ids_by_category.get(category, [])
        if not food_ids:
            raise ValueError(f"Tidak ada food untuk kategori: {category}")
        return random.choice(food_ids)
    
    def filter_by_cuisine(self, cuisine_list: List[str]) -> 'FoodCategoryManager':
        """
        Filter database berdasarkan cuisine preference
        Jika user prefer 'indonesian', prioritas makanan Indonesia
        
        Args:
            cuisine_list: ['indonesian', 'western', ...]
        
        Returns:
            New FoodCategoryManager dengan filtered database
        """
        if 'cuisine' not in self.food_database.columns:
            # Jika tidak ada kolom cuisine, return as-is
            return self
        
        # Filter database
        filtered_db = self.food_database[
            self.food_database['cuisine'].isin(cuisine_list)
        ].copy()
        
        if len(filtered_db) == 0:
            # Fallback ke original jika filter hasil 0
            return self
        
        return FoodCategoryManager(filtered_db)
    
    def validate_category(self, food_id: any, expected_category: str) -> bool:
        """Validate bahwa food_id sesuai dengan kategori yang diharapkan"""
        # Cek di semua foods dengan id ini
        for category, food_ids in self.food_ids_by_category.items():
            if food_id in food_ids:
                return category == expected_category
        return False


class CategorizedChromosome:
    """
    Chromosome operations dengan category constraints
    
    Struktur:
    {
        'breakfast': {
            'main_course': food_id,
            'side_dish': food_id,
            'drink': food_id
        },
        'lunch': {similar},
        'dinner': {similar},
        'snack': food_id  ← Direct food_id, bukan dict
    }
    """
    
    MEAL_TYPES = ['breakfast', 'lunch', 'dinner']
    MEAL_CATEGORIES = ['main_course', 'side_dish', 'drink']
    SNACK_TYPE = 'snack'
    
    @staticmethod
    def get_empty() -> Dict:
        """Create empty chromosome dengan structure"""
        chromosome = {}
        
        # Initialize meals
        for meal in CategorizedChromosome.MEAL_TYPES:
            chromosome[meal] = {
                'main_course': None,
                'side_dish': None,
                'drink': None
            }
        
        # Initialize snack
        chromosome[CategorizedChromosome.SNACK_TYPE] = None
        
        return chromosome
    
    @staticmethod
    def is_valid(chromosome: Dict) -> Tuple[bool, str]:
        """
        Validate chromosome structure
        - Harus punya 4 meals
        - Setiap meal harus punya 3 kategori (main, side, drink)
        - Semua values harus ada (not None)
        - Snack harus ada
        """
        if not isinstance(chromosome, dict):
            return False, "Chromosome harus dict"
        
        # Check meals
        for meal in CategorizedChromosome.MEAL_TYPES:
            if meal not in chromosome:
                return False, f"Missing meal: {meal}"
            
            meal_data = chromosome[meal]
            if not isinstance(meal_data, dict):
                return False, f"{meal} must be dict"
            
            # Check categories
            for category in CategorizedChromosome.MEAL_CATEGORIES:
                if category not in meal_data:
                    return False, f"{meal} missing category: {category}"
                
                if meal_data[category] is None:
                    return False, f"{meal}.{category} cannot be None"
        
        # Check snack
        if CategorizedChromosome.SNACK_TYPE not in chromosome:
            return False, "Missing snack"
        
        if chromosome[CategorizedChromosome.SNACK_TYPE] is None:
            return False, "Snack cannot be None"
        
        return True, ""
    
    @staticmethod
    def initialize_random(
        category_manager: FoodCategoryManager,
        max_attempts: int = 10
    ) -> Optional[Dict]:
        """
        Initialize chromosome dengan constraint kategori
        
        Args:
            category_manager: FoodCategoryManager untuk get foods by category
            max_attempts: Jumlah retry jika failed
        
        Returns:
            Valid chromosome atau None jika semua attempt failed
        """
        for attempt in range(max_attempts):
            try:
                chromosome = CategorizedChromosome.get_empty()
                
                # Initialize breakfast, lunch, dinner
                for meal in CategorizedChromosome.MEAL_TYPES:
                    chromosome[meal]['main_course'] = category_manager.get_random_food_id('main_course')
                    chromosome[meal]['side_dish'] = category_manager.get_random_food_id('side_dish')
                    chromosome[meal]['drink'] = category_manager.get_random_food_id('drink')
                
                # Initialize snack
                chromosome[CategorizedChromosome.SNACK_TYPE] = category_manager.get_random_food_id('snack')
                
                # Validate
                valid, msg = CategorizedChromosome.is_valid(chromosome)
                if valid:
                    return chromosome
            
            except Exception as e:
                continue
        
        return None
    
    @staticmethod
    def mutate(
        chromosome: Dict,
        category_manager: FoodCategoryManager,
        mutation_rate: float = 0.1
    ) -> Dict:
        """
        Mutate chromosome sambil maintain category constraints
        
        Args:
            chromosome: Chromosome to mutate
            category_manager: Untuk pick random food per kategori
            mutation_rate: Probability per food (0.1 = 10% per food)
        
        Returns:
            Mutated chromosome (original unchanged)
        """
        mutated = deepcopy(chromosome)
        
        # Mutate breakfast, lunch, dinner
        for meal in CategorizedChromosome.MEAL_TYPES:
            for category in CategorizedChromosome.MEAL_CATEGORIES:
                if random.random() < mutation_rate:
                    # IMPORTANT: Hanya pick dari kategori yang sama!
                    mutated[meal][category] = category_manager.get_random_food_id(category)
        
        # Mutate snack
        if random.random() < mutation_rate:
            mutated[CategorizedChromosome.SNACK_TYPE] = category_manager.get_random_food_id('snack')
        
        return mutated
    
    @staticmethod
    def crossover(
        parent1: Dict,
        parent2: Dict,
        category_manager: FoodCategoryManager
    ) -> Dict:
        """
        Crossover dua chromosome dengan constraint kategori
        
        Strategy: Swap per kategori (tidak sembarangan mix)
        
        Args:
            parent1, parent2: Parent chromosomes
            category_manager: Untuk fallback jika crossover error
        
        Returns:
            Offspring chromosome
        """
        offspring = CategorizedChromosome.get_empty()
        
        for meal in CategorizedChromosome.MEAL_TYPES:
            for category in CategorizedChromosome.MEAL_CATEGORIES:
                # 50% dari parent1, 50% dari parent2
                if random.random() < 0.5:
                    offspring[meal][category] = parent1[meal][category]
                else:
                    offspring[meal][category] = parent2[meal][category]
        
        # Snack: random pick
        offspring[CategorizedChromosome.SNACK_TYPE] = (
            parent1[CategorizedChromosome.SNACK_TYPE] if random.random() < 0.5
            else parent2[CategorizedChromosome.SNACK_TYPE]
        )
        
        return offspring
    
    @staticmethod
    def to_readable(chromosome: Dict, food_database: pd.DataFrame) -> Dict:
        """
        Convert chromosome ke format readable (dengan food names)
        
        Args:
            chromosome: Chromosome to convert
            food_database: DataFrame untuk lookup food names
        
        Returns:
            Readable format dengan food names
        """
        readable = {}
        
        # Helper untuk find food name
        def get_food_name(food_id):
            if 'fdc_id' in food_database.columns:
                match = food_database[food_database['fdc_id'] == food_id]
            else:
                match = food_database[food_database.index == food_id]
            
            if len(match) > 0:
                return match.iloc[0]['food_name']
            return str(food_id)
        
        # Convert meals
        for meal in CategorizedChromosome.MEAL_TYPES:
            readable[meal] = {}
            for category in CategorizedChromosome.MEAL_CATEGORIES:
                food_id = chromosome[meal][category]
                readable[meal][category] = get_food_name(food_id)
        
        # Convert snack
        readable[CategorizedChromosome.SNACK_TYPE] = get_food_name(
            chromosome[CategorizedChromosome.SNACK_TYPE]
        )
        
        return readable
    
    @staticmethod
    def get_food_ids(chromosome: Dict) -> List:
        """Extract semua food_ids dari chromosome (untuk nutrition calculation)"""
        food_ids = []
        
        for meal in CategorizedChromosome.MEAL_TYPES:
            for category in CategorizedChromosome.MEAL_CATEGORIES:
                food_ids.append(chromosome[meal][category])
        
        food_ids.append(chromosome[CategorizedChromosome.SNACK_TYPE])
        
        return food_ids


if __name__ == "__main__":
    print("CategorizedChromosome module loaded")
    print("\nExample usage:")
    print("1. category_manager = FoodCategoryManager(food_database)")
    print("2. chromosome = CategorizedChromosome.initialize_random(category_manager)")
    print("3. mutated = CategorizedChromosome.mutate(chromosome, category_manager)")

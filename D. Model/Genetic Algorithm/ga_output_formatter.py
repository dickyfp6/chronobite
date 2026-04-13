"""
Output Formatter - Convert Chromosome to UI Format
Chromosome (internal) → MenuPlan (external display)
"""

import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class FoodOption:
    """Single food option dalam meal slot"""
    fdc_id: str
    name: str
    portion_gram: float
    energy_kcal: float
    protein_g: float
    carbohydrate_g: float
    fat_g: float
    fiber_g: float
    sodium_mg: float = 0
    
    def __str__(self):
        return f"{self.name} ({self.portion_gram}g)"


@dataclass
class MealSlot:
    """Single meal slot (main, side, drink)"""
    slot_type: str  # 'main', 'side', 'drink'
    primary: FoodOption  # Selected option
    alternatives: List[FoodOption] = field(default_factory=list)  # Up to 2 alternatives
    
    def to_dict(self):
        return {
            'type': self.slot_type,
            'primary': {
                'id': self.primary.fdc_id,
                'name': self.primary.name,
                'portion': self.primary.portion_gram,
                'energy_kcal': self.primary.energy_kcal
            },
            'alternatives': [
                {
                    'id': alt.fdc_id,
                    'name': alt.name,
                    'portion': alt.portion_gram,
                    'energy_kcal': alt.energy_kcal
                }
                for alt in self.alternatives
            ]
        }


@dataclass
class Meal:
    """Single meal (breakfast, lunch, etc)"""
    meal_name: str
    slots: Dict[str, MealSlot] = field(default_factory=dict)  # slot_type -> MealSlot
    total_energy: float = 0.0
    total_protein: float = 0.0
    total_carbs: float = 0.0
    total_fat: float = 0.0
    total_fiber: float = 0.0
    
    def to_dict(self):
        return {
            'name': self.meal_name,
            'slots': {stype: slot.to_dict() for stype, slot in self.slots.items()},
            'nutritionInfo': {
                'energy_kcal': round(self.total_energy, 1),
                'protein_g': round(self.total_protein, 1),
                'carbohydrate_g': round(self.total_carbs, 1),
                'fat_g': round(self.total_fat, 1),
                'fiber_g': round(self.total_fiber, 1)
            }
        }


@dataclass
class MenuPlan:
    """Complete menu plan untuk sehari"""
    algorithm: str = "GA"  # Algorithm name for output
    ga_fitness_score: float = 0.0  # Fitness score (0-100)
    total_energy_kcal: float = 0.0  # Total energy in kcal
    breakfast: Optional['Meal'] = None  # Breakfast meal
    lunch: Optional['Meal'] = None  # Lunch meal
    dinner: Optional['Meal'] = None  # Dinner meal
    snack: Optional[Dict] = None  # Snack as dict {'food_name': ..., 'energy_kcal': ...}
    meals: Dict[str, Meal] = field(default_factory=dict)  # meal_name -> Meal (legacy)
    total_energy: float = 0.0  # Legacy name for compatibility
    total_nutrients: Dict[str, float] = field(default_factory=dict)  # Legacy for compatibility
    
    def to_dict(self):
        return {
            'meals': {name: meal.to_dict() for name, meal in self.meals.items()},
            'dailyTotal': {
                'energy_kcal': round(self.total_energy, 1),
                'nutrients': {k: round(v, 1) for k, v in self.total_nutrients.items()}
            }
        }


class GeneticAlgorithmOutputFormatter:
    """Convert optimized chromosome to user-friendly MenuPlan"""
    
    @staticmethod
    def format_output(
        chromosome: Dict,
        food_database: pd.DataFrame,
        meal_distribution: Dict,  # from NutritionService
        user_tdee: float
    ) -> MenuPlan:
        """
        Convert chromosome solution ke MenuPlan dengan alternatives
        
        Args:
            chromosome: {meal: {food_id: portion, ...}, ...}
            food_database: DataFrame semua foods
            meal_distribution: {meal: kcal_target, ...} dari NutritionService
            user_tdee: User TDEE untuk sanity check
        
        Returns:
            MenuPlan object dengan:
            - 1 primary food option per slot
            - 2 alternative options per slot
            - Nutritional info untuk setiap meal & overall
        """
        
        menu_plan = MenuPlan()
        
        # Map chromosome meals ke standard meal names
        meal_order = ['breakfast', 'lunch', 'dinner', 'snack']
        
        for meal_name in meal_order:
            if meal_name not in chromosome:
                continue
            
            foods_dict = chromosome[meal_name]
            
            # Step 1: Extract & categorize foods
            main_food = None
            side_foods = []
            drink_food = None
            
            # Sort by portion (largest first)
            sorted_foods = sorted(
                foods_dict.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            for food_id, portion in sorted_foods:
                food_row = GeneticAlgorithmOutputFormatter._find_food(
                    food_id, food_database
                )
                
                if food_row is None:
                    continue
                
                # Heuristic: categorize berdasarkan portion & food type
                if food_name := food_row.get('food_name', ''):
                    # Very simple categorization (could be improved)
                    if 'drink' in food_name.lower() or 'juice' in food_name.lower():
                        if drink_food is None:
                            drink_food = FoodOption(
                                fdc_id=food_id,
                                name=food_name,
                                portion_gram=portion,
                                energy_kcal=float(food_row.get('energy_kcal', 0)),
                                protein_g=float(food_row.get('protein_g', 0)),
                                carbohydrate_g=float(food_row.get('carbohydrate_g', 0)),
                                fat_g=float(food_row.get('fat_g', 0)),
                                fiber_g=float(food_row.get('fiber_g', 0)),
                                sodium_mg=float(food_row.get('sodium_mg', 0))
                            )
                    else:
                        if main_food is None:
                            main_food = FoodOption(
                                fdc_id=food_id,
                                name=food_name,
                                portion_gram=portion,
                                energy_kcal=float(food_row.get('energy_kcal', 0)),
                                protein_g=float(food_row.get('protein_g', 0)),
                                carbohydrate_g=float(food_row.get('carbohydrate_g', 0)),
                                fat_g=float(food_row.get('fat_g', 0)),
                                fiber_g=float(food_row.get('fiber_g', 0)),
                                sodium_mg=float(food_row.get('sodium_mg', 0))
                            )
                        else:
                            side_foods.append(FoodOption(
                                fdc_id=food_id,
                                name=food_name,
                                portion_gram=portion,
                                energy_kcal=float(food_row.get('energy_kcal', 0)),
                                protein_g=float(food_row.get('protein_g', 0)),
                                carbohydrate_g=float(food_row.get('carbohydrate_g', 0)),
                                fat_g=float(food_row.get('fat_g', 0)),
                                fiber_g=float(food_row.get('fiber_g', 0)),
                                sodium_mg=float(food_row.get('sodium_mg', 0))
                            ))
            
            # Step 2: Create meal dengan main food
            meal = Meal(meal_name=meal_name.capitalize())
            
            if main_food:
                slot_main = MealSlot(slot_type='main', primary=main_food)
                
                # Find alternatives untuk main
                alts = GeneticAlgorithmOutputFormatter._find_alternatives(
                    main_food, food_database, count=2
                )
                slot_main.alternatives = alts
                
                meal.slots['main'] = slot_main
                meal.total_energy += main_food.energy_kcal
                meal.total_protein += main_food.protein_g
                meal.total_carbs += main_food.carbohydrate_g
                meal.total_fat += main_food.fat_g
                meal.total_fiber += main_food.fiber_g
            
            # Step 3: Add side foods
            for idx, side_food in enumerate(side_foods):
                slot_type = f'side_{idx + 1}' if len(side_foods) > 1 else 'side'
                slot_side = MealSlot(slot_type=slot_type, primary=side_food)
                
                # Find alternatives
                alts = GeneticAlgorithmOutputFormatter._find_alternatives(
                    side_food, food_database, count=2
                )
                slot_side.alternatives = alts
                
                meal.slots[slot_type] = slot_side
                meal.total_energy += side_food.energy_kcal
                meal.total_protein += side_food.protein_g
                meal.total_carbs += side_food.carbohydrate_g
                meal.total_fat += side_food.fat_g
                meal.total_fiber += side_food.fiber_g
            
            # Step 4: Add drink
            if drink_food:
                slot_drink = MealSlot(slot_type='drink', primary=drink_food)
                
                # Find alternatives
                alts = GeneticAlgorithmOutputFormatter._find_alternatives(
                    drink_food, food_database, count=2, is_drink=True
                )
                slot_drink.alternatives = alts
                
                meal.slots['drink'] = slot_drink
                meal.total_energy += drink_food.energy_kcal
                meal.total_protein += drink_food.protein_g
                meal.total_carbs += drink_food.carbohydrate_g
                meal.total_fat += drink_food.fat_g
                meal.total_fiber += drink_food.fiber_g
            
            menu_plan.meals[meal_name] = meal
            menu_plan.total_energy += meal.total_energy
        
        # Calculate overall nutrients
        for meal in menu_plan.meals.values():
            menu_plan.total_nutrients['protein_g'] = menu_plan.total_nutrients.get('protein_g', 0) + meal.total_protein
            menu_plan.total_nutrients['carbohydrate_g'] = menu_plan.total_nutrients.get('carbohydrate_g', 0) + meal.total_carbs
            menu_plan.total_nutrients['fat_g'] = menu_plan.total_nutrients.get('fat_g', 0) + meal.total_fat
            menu_plan.total_nutrients['fiber_g'] = menu_plan.total_nutrients.get('fiber_g', 0) + meal.total_fiber
        
        return menu_plan
    
    @staticmethod
    def _find_food(food_id: str, food_database: pd.DataFrame) -> Optional[Dict]:
        """Find food dalam database by ID"""
        try:
            if 'fdc_id' in food_database.columns:
                match = food_database[food_database['fdc_id'] == food_id]
            else:
                match = food_database[food_database.index == food_id]
            
            if match.empty:
                return None
            
            return match.iloc[0].to_dict()
        except:
            return None
    
    @staticmethod
    def _find_alternatives(
        target_food: FoodOption,
        food_database: pd.DataFrame,
        count: int = 2,
        is_drink: bool = False
    ) -> List[FoodOption]:
        """
        Find similar foods sebagai alternatives
        Similarity kriteria:
        - ±10% kcal
        - Similar macronutrient profile
        - Different food (exclude original)
        """
        
        alternatives = []
        kcal_tolerance = target_food.energy_kcal * 0.10
        kcal_min = target_food.energy_kcal - kcal_tolerance
        kcal_max = target_food.energy_kcal + kcal_tolerance
        
        try:
            # Filter candidates
            candidates = food_database[
                (food_database['energy_kcal'] >= kcal_min) &
                (food_database['energy_kcal'] <= kcal_max) &
                (food_database['fdc_id'] != target_food.fdc_id)  # Exclude original
            ]
            
            if candidates.empty:
                return alternatives
            
            # Score similarity (simple version - could be enhanced)
            candidates['similarity_score'] = candidates.apply(
                lambda row: GeneticAlgorithmOutputFormatter._calculate_similarity(
                    target_food, row
                ),
                axis=1
            )
            
            # Get top matches
            top_candidates = candidates.nlargest(count, 'similarity_score')
            
            for _, row in top_candidates.iterrows():
                alt = FoodOption(
                    fdc_id=row['fdc_id'],
                    name=row['food_name'],
                    portion_gram=target_food.portion_gram,  # Same portion as original
                    energy_kcal=float(row['energy_kcal']),
                    protein_g=float(row['protein_g']),
                    carbohydrate_g=float(row['carbohydrate_g']),
                    fat_g=float(row['fat_g']),
                    fiber_g=float(row['fiber_g']),
                    sodium_mg=float(row.get('sodium_mg', 0))
                )
                alternatives.append(alt)
        
        except Exception as e:
            print(f"Error finding alternatives: {e}")
        
        return alternatives
    
    @staticmethod
    def _calculate_similarity(food1: FoodOption, food2) -> float:
        """
        Calculate similarity score (0-100)
        Based on nutrient profile match
        """
        try:
            # Extract values
            kcal1, kcal2 = food1.energy_kcal, float(food2.get('energy_kcal', 0))
            protein1, protein2 = food1.protein_g, float(food2.get('protein_g', 0))
            carb1, carb2 = food1.carbohydrate_g, float(food2.get('carbohydrate_g', 0))
            fat1, fat2 = food1.fat_g, float(food2.get('fat_g', 0))
            
            # Calculate differences
            kcal_diff = abs(kcal1 - kcal2) / max(1, kcal1, kcal2)
            protein_diff = abs(protein1 - protein2) / max(1, protein1, protein2)
            carb_diff = abs(carb1 - carb2) / max(1, carb1, carb2)
            fat_diff = abs(fat1 - fat2) / max(1, fat1, fat2)
            
            # Average difference
            avg_diff = (kcal_diff + protein_diff + carb_diff + fat_diff) / 4.0
            
            # Convert to similarity (0-100)
            similarity = max(0, 100 - (avg_diff * 100))
            
            return similarity
        
        except:
            return 0.0


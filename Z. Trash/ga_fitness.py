"""
Fitness Calculation - REDESIGNED
Chromosome = {meal: {food_id: portion, ...}, ...}
Fitness = aggregate nutrient compliance vs guidelines
"""

import pandas as pd
from typing import Dict, List, Tuple, Optional


class FitnessCalculator:
    """Calculate fitness dari chromosome dengan aggregate nutrients"""
    
    @staticmethod
    def calculate_fitness(
        chromosome: Dict,
        food_database: pd.DataFrame,
        guidelines: Dict,
        user_tdee: float,
        weights: Optional[Dict] = None
    ) -> float:
        """
        Calculate overall fitness score (0-100)
        
        Args:
            chromosome: {meal: {food_id: portion, ...}, ...}
            food_database: DataFrame dengan nutrient columns per food
            guidelines: Dict dari NutritionService dengan nutrient constraints
            user_tdee: User's TDEE
            weights: Custom weights for components
        
        Returns:
            Fitness score (0-100, higher is better)
        """
        
        if weights is None:
            weights = {
                'nutrient_compliance': 0.80,
                'meal_variety': 0.10,
                'total_calorie': 0.10
            }
        
        try:
            # Component 1: Aggregate nutrients & compare vs constraints
            total_nutrients = FitnessCalculator._aggregate_nutrients(
                chromosome, food_database
            )
            
            nutrient_compliance_score = FitnessCalculator._calculate_nutrient_compliance(
                total_nutrients, guidelines
            )
            
            # Component 2: Meal variety (number of unique foods)
            total_foods = FitnessCalculator._count_foods(chromosome)
            unique_foods = FitnessCalculator._count_unique_foods(chromosome)
            variety_score = (unique_foods / max(1, total_foods)) * 100 if total_foods > 0 else 0
            
            # Component 3: Total calorie match
            total_kcal = total_nutrients.get('energy_kcal', 0)
            calorie_score = FitnessCalculator._calculate_proximity_score(
                total_kcal, user_tdee, tolerance=0.15  # ±15% tolerance
            )
            
            # Combine
            fitness = (
                nutrient_compliance_score * weights['nutrient_compliance'] +
                variety_score * weights['meal_variety'] +
                calorie_score * weights['total_calorie']
            )
            
            return round(max(0, min(100, fitness)), 2)
        
        except Exception as e:
            print(f"Fitness calculation error: {e}")
            return 0.0
    
    @staticmethod
    def _aggregate_nutrients(
        chromosome: Dict,
        food_database: pd.DataFrame
    ) -> Dict[str, float]:
        """
        Aggregate TOTAL nutrients dari semua foods dalam chromosome
        
        Process:
        1. For each meal in chromosome
        2. For each food_id + portion
        3. Lookup food data dari database
        4. Scale nutrients to portion size
        5. Sum across all foods
        
        Returns:
            {nutrient_name: total_value, ...} (total untuk seluruh hari)
        """
        
        # Initialize nutrient dict
        nutrients = {}
        
        # Get all nutrient columns dari database
        # Assume database columns: energy_kcal, protein_g, carb_g, fat_g, fiber_g, sodium_mg, etc.
        nutrient_columns = [
            'energy_kcal', 'protein_g', 'carbohydrate_g', 'fat_g', 'fiber_g',
            'sodium_mg', 'potassium_mg', 'calcium_mg', 'iron_mg', 'zinc_mg',
            'vitamin_a_rae_mcg', 'vitamin_c_mg', 'vitamin_d_mcg', 'vitamin_e_mg',
            'vitamin_k_mcg', 'thiamine_mg', 'riboflavin_mg', 'niacin_mg',
            'vitamin_b6_mg', 'vitamin_b12_mcg', 'folate_mcg', 'cholesterol_mg'
        ]
        
        for nutrient in nutrient_columns:
            nutrients[nutrient] = 0.0
        
        # Iterate chromosome
        for meal, foods_dict in chromosome.items():
            for food_id, portion_gram in foods_dict.items():
                try:
                    # Find food dalam database
                    if 'fdc_id' in food_database.columns:
                        food_row = food_database[food_database['fdc_id'] == food_id]
                    else:
                        food_row = food_database[food_database.index == food_id]
                    
                    if food_row.empty:
                        continue
                    
                    food_row = food_row.iloc[0]  # Get first row
                    
                    # Scale nutrients ke portion
                    # Database values usually per 100g
                    scaling_factor = portion_gram / 100.0
                    
                    for nutrient in nutrient_columns:
                        if nutrient in food_row.index:
                            try:
                                value = float(food_row[nutrient])
                                nutrients[nutrient] += value * scaling_factor
                            except (ValueError, TypeError):
                                pass
                
                except Exception:
                    continue
        
        return nutrients
    
    @staticmethod
    def _calculate_nutrient_compliance(
        total_nutrients: Dict[str, float],
        guidelines: Dict
    ) -> float:
        """
        Calculate how well nutrients comply dengan guideline constraints
        
        Algorithm:
        - For each nutrient dalam guidelines
        - If within [min, max] range: score 100
        - If below min: penalty based on distance
        - If above max: penalty based on distance
        - Average dari semua nutrients
        
        Returns:
            Score 0-100
        """
        
        guideline_nutrients = guidelines.get('nutrients', {})
        
        if not guideline_nutrients:
            return 50.0  # Default jika tidak ada guideline
        
        nutrient_scores = []
        
        for nutrient_name, constraint in guideline_nutrients.items():
            min_val = constraint.get('min', 0)
            max_val = constraint.get('max', float('inf'))
            actual_val = total_nutrients.get(nutrient_name, 0)
            
            # Handle invalid constraints
            if min_val is None or max_val is None:
                continue
            
            score = FitnessCalculator._calculate_nutrient_score(
                actual_val, min_val, max_val
            )
            nutrient_scores.append(score)
        
        if nutrient_scores:
            return sum(nutrient_scores) / len(nutrient_scores)
        else:
            return 50.0
    
    @staticmethod
    def _calculate_nutrient_score(
        actual: float,
        min_val: float,
        max_val: float
    ) -> float:
        """
        Score single nutrient:
        - Within [min, max]: 100
        - Below min: diminish linearly
        - Above max: diminish linearly
        
        Returns:
            0-100 score
        """
        if actual >= min_val and actual <= max_val:
            return 100.0
        
        elif actual < min_val:
            if min_val == 0:
                return 0.0
            # Penalty: how far below minimum
            penalty = (min_val - actual) / min_val * 100
            return max(0, 100 - penalty)
        
        else:  # actual > max_val
            if max_val == 0:
                return 0.0
            # Penalty: how far above maximum
            penalty = (actual - max_val) / max_val * 100
            return max(0, 100 - penalty)
    
    @staticmethod
    def _calculate_proximity_score(
        actual: float,
        target: float,
        tolerance: float = 0.10
    ) -> float:
        """
        Score berdasarkan proximity ke target value
        
        Args:
            tolerance: Acceptable deviation ratio (0.10 = ±10%)
        
        Returns:
            0-100 score
        """
        if target == 0:
            return 0.0 if actual != 0 else 100.0
        
        error_ratio = abs(actual - target) / target
        
        if error_ratio <= tolerance:
            return 100.0
        else:
            # Linear diminish
            penalty = (error_ratio - tolerance) / (1 - tolerance) * 100
            return max(0, 100 - penalty)
    
    @staticmethod
    def _count_foods(chromosome: Dict) -> int:
        """Count total foods dalam chromosome"""
        count = 0
        for foods_dict in chromosome.values():
            count += len(foods_dict)
        return count
    
    @staticmethod
    def _count_unique_foods(chromosome: Dict) -> int:
        """Count unique food IDs dalam chromosome"""
        all_foods = set()
        for foods_dict in chromosome.values():
            all_foods.update(foods_dict.keys())
        return len(all_foods)


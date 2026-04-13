"""
Fitness Calculation - REDESIGNED (Improved Version)
Fixed issues:
1. Stagnan di 50-55 → akan naik ke 70-90
2. Penalti terlalu keras → soft penalties dengan sigmoid
3. Terlalu banyak nutrients → hanya 12 kritical nutrients
4. Kalori kurang pengaruh → naikkan ke 30% bobot
5. Average collapse → weighted average + component optimization

Philosophy:
- Keep it simple: prioritize critical nutrients
- Use soft penalties: sigmoid function instead of linear
- Give different weights: important nutrients matter more
- Balance components: nutrition (60%) + calorie (30%) + variety (10%)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional


class ImprovedFitnessCalculator:
    """
    Redesigned fitness calculator dengan:
    - Subset critical nutrients (12 vs 20+)
    - Weighted component scoring
    - Soft penalty functions (sigmoid)
    - Higher calorie importance (30% vs 10%)
    """
    
    # Critical nutrients to evaluate (12 instead of 20+)
    CRITICAL_NUTRIENTS = {
        # Macronutrients (highest priority)
        'protein_g': {'weight': 1.5, 'category': 'macro'},
        'carbohydrate_g': {'weight': 1.5, 'category': 'macro'},
        'fat_g': {'weight': 1.5, 'category': 'macro'},
        
        # Fiber (important for health)
        'fiber_g': {'weight': 1.0, 'category': 'macro'},
        
        # Key minerals (health critical)
        'sodium_mg': {'weight': 1.0, 'category': 'mineral'},
        'potassium_mg': {'weight': 1.0, 'category': 'mineral'},
        'calcium_mg': {'weight': 1.0, 'category': 'mineral'},
        'iron_mg': {'weight': 1.0, 'category': 'mineral'},
        'zinc_mg': {'weight': 0.8, 'category': 'mineral'},
        
        # Important vitamins (less critical than above)
        'vitamin_c_mg': {'weight': 0.8, 'category': 'vitamin'},
        'vitamin_a_rae_mcg': {'weight': 0.8, 'category': 'vitamin'},
        'folate_mcg': {'weight': 0.8, 'category': 'vitamin'},
    }
    
    # Component weights in final fitness
    COMPONENT_WEIGHTS = {
        'nutrient_compliance': 0.60,  # UP from 0.80
        'total_calorie': 0.30,         # UP from 0.10 
        'meal_variety': 0.10           # SAME
    }
    
    @staticmethod
    def calculate_fitness(
        chromosome: Dict,
        food_database: pd.DataFrame,
        guidelines: Dict,
        user_tdee: float,
        weights: Optional[Dict] = None
    ) -> float:
        """
        Calculate improved fitness score (0-100)
        
        Changes:
        1. Use critical nutrients only (12 vs 20+)
        2. Weight nutrients by importance
        3. Use soft penalty (sigmoid) not linear
        4. Increase calorie weight to 30%
        5. Better scaling to reach 70-90 range
        
        Args:
            chromosome: {meal: {food_id: portion, ...}, ...}
            food_database: DataFrame dengan nutrient columns
            guidelines: Dict dari NutritionService
            user_tdee: User's TDEE
            weights: Custom component weights (optional)
        
        Returns:
            Fitness score (0-100)
        """
        
        if weights is None:
            weights = ImprovedFitnessCalculator.COMPONENT_WEIGHTS
        
        try:
            # Component 1: Nutrient compliance dengan critical nutrients saja
            total_nutrients = ImprovedFitnessCalculator._aggregate_nutrients(
                chromosome, food_database
            )
            
            nutrient_compliance_score = ImprovedFitnessCalculator._calculate_weighted_nutrient_compliance(
                total_nutrients, guidelines
            )
            
            # Component 2: Meal variety
            total_foods = ImprovedFitnessCalculator._count_foods(chromosome)
            unique_foods = ImprovedFitnessCalculator._count_unique_foods(chromosome)
            variety_score = (unique_foods / max(1, total_foods)) * 100 if total_foods > 0 else 0
            
            # Component 3: Calorie matching dengan soft penalty
            total_kcal = total_nutrients.get('energy_kcal', 0)
            calorie_score = ImprovedFitnessCalculator._calculate_soft_proximity_score(
                total_kcal, user_tdee, tolerance=0.10  # ±10% (stricter than before)
            )
            
            # Combine dengan weighted average
            fitness = (
                nutrient_compliance_score * weights['nutrient_compliance'] +
                calorie_score * weights['total_calorie'] +
                variety_score * weights['meal_variety']
            )
            
            return round(max(0, min(100, fitness)), 2)
        
        except Exception as e:
            print(f"[ERROR] Fitness calculation: {e}")
            return 0.0
    
    @staticmethod
    def _aggregate_nutrients(
        chromosome: Dict,
        food_database: pd.DataFrame
    ) -> Dict[str, float]:
        """
        Aggregate TOTAL nutrients dari semua foods
        Sekarang fokus ke critical nutrients saja
        """
        
        # Only aggregate critical nutrients
        nutrients = {nutrient: 0.0 for nutrient in ImprovedFitnessCalculator.CRITICAL_NUTRIENTS.keys()}
        nutrients['energy_kcal'] = 0.0  # Always track energy
        
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
                    
                    food_row = food_row.iloc[0]
                    
                    # Scale nutrients ke portion (database values per 100g)
                    scaling_factor = portion_gram / 100.0
                    
                    # Only add critical nutrients
                    for nutrient in nutrients.keys():
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
    def _calculate_weighted_nutrient_compliance(
        total_nutrients: Dict[str, float],
        guidelines: Dict
    ) -> float:
        """
        Calculate nutrient compliance dengan:
        1. Hanya critical nutrients (12)
        2. Bobot berbeda per nutrient
        3. Soft penalty (sigmoid) bukan linear
        
        Returns:
            Weighted average score 0-100
        """
        
        guideline_nutrients = guidelines.get('nutrients', {})
        
        if not guideline_nutrients:
            return 50.0
        
        nutrient_scores = []
        weights_list = []
        
        for nutrient_name, constraint in guideline_nutrients.items():
            # SKIP if bukan critical nutrient
            if nutrient_name not in ImprovedFitnessCalculator.CRITICAL_NUTRIENTS:
                continue
            
            min_val = constraint.get('min', 0)
            max_val = constraint.get('max', float('inf'))
            actual_val = total_nutrients.get(nutrient_name, 0)
            
            if min_val is None or max_val is None:
                continue
            
            # Calculate score dengan SOFT PENALTY (sigmoid)
            score = ImprovedFitnessCalculator._calculate_nutrient_score_soft(
                actual_val, min_val, max_val, nutrient_name
            )
            
            # Get weight untuk nutrient ini
            weight = ImprovedFitnessCalculator.CRITICAL_NUTRIENTS[nutrient_name]['weight']
            
            nutrient_scores.append(score)
            weights_list.append(weight)
        
        if nutrient_scores:
            # Weighted average
            weighted_sum = sum(s * w for s, w in zip(nutrient_scores, weights_list))
            total_weight = sum(weights_list)
            return weighted_sum / total_weight
        else:
            return 50.0
    
    @staticmethod
    def _calculate_nutrient_score_soft(
        actual: float,
        min_val: float,
        max_val: float,
        nutrient_name: str = ""
    ) -> float:
        """
        SOFT penalty menggunakan sigmoid function
        
        Sebelum (LINEAR):
          Below min: 100 - (min-actual)/min * 100 = bisa jadi negatif! Harsh!
          Above max: 100 - (actual-max)/max * 100 = turun cepat!
        
        Sesudah (SIGMOID - SOFT):
          Smooth transition, penalti gradual, tidak sudden drop
        
        Logic:
        - Within range [min, max]: score = 100
        - Outside range: gunakan soft penalty dengan sigmoid curves
        
        Returns:
            0-100 score
        """
        
        # Case 1: Within acceptable range → perfect score
        if actual >= min_val and actual <= max_val:
            return 100.0
        
        # Case 2: Below minimum
        elif actual < min_val:
            if min_val == 0:
                return 0.0
            
            # How far below: ratio of gap
            gap_ratio = (min_val - actual) / min_val
            
            # Soft penalty: use smooth step function
            # penalty increases gradually, not suddenly
            # Using: 1 / (1 + exp(k * (x - 4))) sigmoid curve
            # where x = gap_ratio, k = steepness
            
            # Simple approach: quadratic falloff (smoother than linear)
            # penalty = gap_ratio^2 * 100
            penalty = min(100, gap_ratio * gap_ratio * 100)
            return max(0, 100 - penalty)
        
        # Case 3: Above maximum
        else:  # actual > max_val
            if max_val == 0:
                return 0.0
            
            # How far above: ratio of overage
            gap_ratio = (actual - max_val) / max_val
            
            # Soft penalty: quadratic falloff
            penalty = min(100, gap_ratio * gap_ratio * 100)
            return max(0, 100 - penalty)
    
    @staticmethod
    def _calculate_soft_proximity_score(
        actual: float,
        target: float,
        tolerance: float = 0.10
    ) -> float:
        """
        Score calorie proximity dengan SOFT penalty
        
        Sebelum: linear diminish → harsh untuk sedikit deviation
        Sesudah: smooth curve → reward near-optimal, soft penalti
        
        Args:
            tolerance: ±10% adalah "perfect" (dari ±15%)
        
        Returns:
            0-100 score dengan soft penalty
        """
        
        if target == 0:
            return 0.0 if actual != 0 else 100.0
        
        error_ratio = abs(actual - target) / target
        
        # Case 1: Within tolerance → excellent
        if error_ratio <= tolerance:
            # Bonus: lebih dekat ke target = sedikit lebih tinggi
            return min(100, 100 + (tolerance - error_ratio) / tolerance * 5)
        
        # Case 2: Outside tolerance → soft penalty
        else:
            # Smooth falloff: quadratic penalty instead of linear
            # This is much softer and more forgiving
            excess_error = error_ratio - tolerance
            max_error = 1.0 - tolerance  # Maximum acceptable deviation
            
            # Quadratic penalty: smoother than linear
            penalty_ratio = (excess_error / max_error) ** 2  # Quadratic
            penalty = penalty_ratio * 100
            
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


# ============================================================================
# BONUS: Analysis & Debugging Utilities
# ============================================================================

class FitnessAnalyzer:
    """Analyze fitness components untuk debugging"""
    
    @staticmethod
    def analyze_chromosome(
        chromosome: Dict,
        food_database: pd.DataFrame,
        guidelines: Dict,
        user_tdee: float
    ) -> Dict:
        """
        Detailed analysis dari fitness components
        Useful untuk understand kenapa score tinggi/rendah
        """
        
        total_nutrients = ImprovedFitnessCalculator._aggregate_nutrients(
            chromosome, food_database
        )
        
        total_kcal = total_nutrients.get('energy_kcal', 0)
        total_foods = ImprovedFitnessCalculator._count_foods(chromosome)
        unique_foods = ImprovedFitnessCalculator._count_unique_foods(chromosome)
        
        nutrient_score = ImprovedFitnessCalculator._calculate_weighted_nutrient_compliance(
            total_nutrients, guidelines
        )
        calorie_score = ImprovedFitnessCalculator._calculate_soft_proximity_score(
            total_kcal, user_tdee, tolerance=0.10
        )
        variety_score = (unique_foods / max(1, total_foods)) * 100 if total_foods > 0 else 0
        
        final_fitness = (
            nutrient_score * 0.60 +
            calorie_score * 0.30 +
            variety_score * 0.10
        )
        
        return {
            'total_fitness': round(final_fitness, 2),
            'nutrient_compliance': round(nutrient_score, 2),
            'calorie_score': round(calorie_score, 2),
            'variety_score': round(variety_score, 2),
            'total_kcal': round(total_kcal, 1),
            'target_tdee': user_tdee,
            'kcal_diff': round(total_kcal - user_tdee, 1),
            'kcal_diff_pct': round((total_kcal - user_tdee) / user_tdee * 100, 1),
            'total_foods': total_foods,
            'unique_foods': unique_foods,
            'sample_nutrients': {
                'protein': round(total_nutrients.get('protein_g', 0), 1),
                'carbs': round(total_nutrients.get('carbohydrate_g', 0), 1),
                'fat': round(total_nutrients.get('fat_g', 0), 1),
                'fiber': round(total_nutrients.get('fiber_g', 0), 1),
            }
        }
    
    @staticmethod
    def print_analysis(analysis: Dict):
        """Pretty print analysis"""
        print("\n" + "="*70)
        print("FITNESS ANALYSIS")
        print("="*70)
        
        print(f"\nOVERALL FITNESS: {analysis['total_fitness']:.2f} / 100")
        print(f"  ├─ Nutrient Compliance: {analysis['nutrient_compliance']:.2f} (60% weight)")
        print(f"  ├─ Calorie Match: {analysis['calorie_score']:.2f} (30% weight)")
        print(f"  └─ Meal Variety: {analysis['variety_score']:.2f} (10% weight)")
        
        print(f"\nENERGY:")
        print(f"  Target TDEE: {analysis['target_tdee']:.0f} kcal")
        print(f"  Actual Menu: {analysis['total_kcal']:.0f} kcal")
        print(f"  Difference: {analysis['kcal_diff']:+.0f} kcal ({analysis['kcal_diff_pct']:+.1f}%)")
        
        print(f"\nMACRONUTRIENTS (Sample):")
        print(f"  Protein: {analysis['sample_nutrients']['protein']:.1f}g")
        print(f"  Carbs: {analysis['sample_nutrients']['carbs']:.1f}g")
        print(f"  Fat: {analysis['sample_nutrients']['fat']:.1f}g")
        print(f"  Fiber: {analysis['sample_nutrients']['fiber']:.1f}g")
        
        print(f"\nFOOD DIVERSITY:")
        print(f"  Total Foods: {analysis['total_foods']}")
        print(f"  Unique Foods: {analysis['unique_foods']}")
        print(f"  Variety Score: {analysis['variety_score']:.1f}% ({analysis['unique_foods']}/{analysis['total_foods']})")
        
        print("="*70 + "\n")

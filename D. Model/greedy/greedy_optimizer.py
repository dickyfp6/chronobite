"""
REDESIGNED Greedy Algorithm - Proper DSS Architecture
================================================

Three-Phase Flow:
1. FOOD SELECTION: Generate diverse candidates without portion scaling
2. PORTION OPTIMIZATION: Calculate realistic portions + scale nutrients
3. POST-SELECTION REBALANCING: Adjust portions after user substitutions (optional)

All dataset values are PER 100g. Scaling happens AFTER food selection.
"""

import pandas as pd
import math
from typing import List, Dict, Tuple, Optional, Set
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from meal_schema import FoodItem, MealCourse, Meal, SnackMeal, MenuPlan
from candidate_generator import CandidateGenerator
from similarity_checker import SimilarityChecker

# Validated meal distribution (DO NOT CHANGE)
MEAL_DISTRIBUTION = {
    'breakfast': 0.2375,   # 23.75% of TDEE
    'lunch': 0.3375,       # 33.75% of TDEE
    'dinner': 0.2875,      # 28.75% of TDEE
    'snack': 0.1375,       # 13.75% of TDEE
}

# Within each meal: Main 50%, Side 30%, Drink 20%
COURSE_DISTRIBUTION = {
    'Main': 0.50,
    'Side': 0.30,
    'Drink': 0.20,
}

# Realistic portion ranges (must be applied during optimization)
PORTION_RANGE = {
    'Main Course': (100, 300),
    'Side Dish':   (50,  150),
    'Drink':       (100, 250),
    'Snack':       (30,   80),
}

MICRONUTRIENT_COLS = [
    'fiber_g', 'sugar_g', 'saturated_fat_g', 'trans_fat_g',
    'cholesterol_mg', 'sodium_mg', 'potassium_mg', 'calcium_mg',
    'iron_mg', 'magnesium_mg', 'phosphorus_mg', 'zinc_mg',
    'copper_mg', 'manganese_mg', 'selenium_mg', 'fluoride_mg',
    'vitamin_a_rae_mg', 'vitamin_b1_thiamin_mg', 'vitamin_b2_riboflavin_mg',
    'vitamin_b3_niacin_mg', 'vitamin_b5_pantothenic_acid_mg',
    'vitamin_b6_mg', 'vitamin_b12_mg', 'vitamin_c_mg', 'vitamin_d_mg',
    'vitamin_e_mg', 'vitamin_k_mg', 'choline_mg', 'folate_mg',
    'water_g'
]


class GreedyOptimizer:
    """
    DSS-compliant Greedy Algorithm with proper three-phase flow:
    1. Food Selection (generate candidates)
    2. Portion Optimization (scale portions + nutrients)
    3. Portion Rebalancing (optional, post-substitution adjustment)
    """
    
    def __init__(self, food_database: pd.DataFrame, constraint_bag: Dict):
        self.food_db = food_database.copy()
        self.constraint_bag = constraint_bag
        self.similarity_checker = SimilarityChecker()
        self.selected_items = []
        self.cumulative_nutrients = {}
        self._init_cumulative_tracking()
    
    def _init_cumulative_tracking(self):
        """Initialize cumulative nutrient tracking"""
        self.cumulative_nutrients = {
            'energy_kcal': 0.0,
            'protein_g': 0.0,
            'carbohydrate_g': 0.0,
            'fat_g': 0.0,
        }
        if 'nutrients' in self.constraint_bag:
            for nutrient_name in self.constraint_bag['nutrients'].keys():
                self.cumulative_nutrients[nutrient_name] = 0.0
    
    def initialize(self, food_database: pd.DataFrame, constraint_bag: Dict):
        """Reinitialize with new database and constraints"""
        self.food_db = food_database.copy()
        self.constraint_bag = constraint_bag
        self.selected_items = []
        self._init_cumulative_tracking()
        
    def optimize_meal_portions(
        self,
        main_item: Optional[Dict],
        side_item: Optional[Dict],
        drink_item: Optional[Dict],
        min_target: float, max_target: float,
        min_m=100.0, max_m=300.0,
        min_s=50.0, max_s=150.0,
        min_d=100.0, max_d=250.0
    ) -> Tuple[float, float, float]:
        """
        Find portion sizes (main_g, side_g, drink_g) that:
        1. Satisfy min/max limits for each course
        2. Satisfy portion hierarchy: main_g >= side_g + 1 and main_g >= drink_g + 1
        3. Keep total meal calories within [min_target, max_target], or as close as possible.
        4. Minimize violations of HARD micronutrient constraints.
        """
        best_error = float('inf')
        best_portions = (min_m, min_s, min_d)
        
        target_mid = (min_target + max_target) / 2.0
        
        energy_m = float(main_item.get('energy_kcal', 0) or 0) if main_item else 0.0
        energy_s = float(side_item.get('energy_kcal', 0) or 0) if side_item else 0.0
        energy_d = float(drink_item.get('energy_kcal', 0) or 0) if drink_item else 0.0
        
        # Load guidelines and cumulative nutrients
        nutrients = self.constraint_bag.get('nutrients', {})
        
        # Pre-extract hard micronutrient constraints for performance inside search loops
        hard_micros = {}
        for nutrient, constraint in nutrients.items():
            if nutrient in ['energy_kcal', 'protein_g', 'carbohydrate_g', 'fat_g']:
                continue
            if constraint.get('hard_soft_type') == 'HARD' and constraint.get('constraint_type') != 'unlimited':
                hard_micros[nutrient] = {
                    'min': float(constraint.get('min') or 0.0),
                    'max': float(constraint.get('max') or float('inf')),
                    'val_m': float(main_item.get(nutrient, 0) or 0) if main_item else 0.0,
                    'val_s': float(side_item.get(nutrient, 0) or 0) if side_item else 0.0,
                    'val_d': float(drink_item.get(nutrient, 0) or 0) if drink_item else 0.0,
                    'cumulative': float(self.cumulative_nutrients.get(nutrient, 0.0)),
                }

        # Grid search over possible Main Course portions (since step is 1g, it is very fast)
        for m in range(int(min_m), int(max_m) + 1):
            s_upper = min(max_s, m - 1.0)
            if s_upper < min_s:
                continue
                
            d_upper = min(max_d, m - 1.0)
            if d_upper < min_d:
                continue
                
            # Search over Side Dish portions
            for s in range(int(min_s), int(s_upper) + 1):
                # Target remaining calories for drink
                cal_ms = (m * energy_m + s * energy_s) / 100.0
                needed_cal_d = target_mid - cal_ms
                
                if energy_d > 0:
                    ideal_d = (needed_cal_d * 100.0) / energy_d
                else:
                    ideal_d = min_d
                    
                # Clamp drink portion
                d = max(min_d, min(d_upper, ideal_d))
                d = float(round(d))
                
                # Calculate total calories and error
                total_cal = cal_ms + (d * energy_d) / 100.0
                
                if total_cal < min_target:
                    error = min_target - total_cal
                elif total_cal > max_target:
                    error = total_cal - max_target
                else:
                    # Inside target range! Prioritize getting closer to midpoint
                    error = abs(total_cal - target_mid) * 0.1
                
                # Calculate hard micronutrient penalties
                micro_penalty = 0.0
                for nutrient, data in hard_micros.items():
                    added_val = (m * data['val_m'] + s * data['val_s'] + d * data['val_d']) / 100.0
                    total_daily_val = data['cumulative'] + added_val
                    
                    if total_daily_val < data['min']:
                        deviation = (data['min'] - total_daily_val) / max(data['min'], 1.0)
                        micro_penalty += deviation * 500.0
                    elif total_daily_val > data['max']:
                        deviation = (total_daily_val - data['max']) / max(data['max'], 1.0)
                        micro_penalty += deviation * 500.0
                        
                error += micro_penalty
                    
                if error < best_error:
                    best_error = error
                    best_portions = (float(m), float(s), float(d))
                    
        return best_portions
    
    # ================================================================
    # PHASE 1: FOOD SELECTION - Generate diverse candidates
    # ================================================================
    
    def score_candidate(
        self,
        candidate: Dict,
        target_calories: float,
        selected_items_names: List[str],
        cumulative_nutrients: Optional[Dict] = None
    ) -> float:
        """
        Score a candidate based on calorie accuracy, constraint satisfaction, and diversity
        (Per-100g basis - no portion scaling yet)
        """
        # 1. CALORIE SCORE (40%)
        target_calories = max(target_calories, 1)
        energy_100g = float(candidate.get('energy_kcal', 0) or 0)
        
        # Estimate portion size for scoring
        consumption_label = str(candidate.get('consumption_label', 'Main Course'))
        min_p, max_p = PORTION_RANGE.get(consumption_label, (50, 400))
        if energy_100g > 0:
            est_portion = (target_calories / energy_100g) * 100.0
        else:
            est_portion = (min_p + max_p) / 2.0
        est_portion = max(min_p, min(max_p, est_portion))
        est_scale = est_portion / 100.0
        
        energy_est = energy_100g * est_scale
        calorie_error = abs(energy_est - target_calories) / target_calories
        calorie_score = max(0, 100 - (calorie_error * 100))

        # 2. CONSTRAINT SATISFACTION SCORE (40%)
        constraint_score = 100
        if cumulative_nutrients is not None:
            nutrients = self.constraint_bag.get('nutrients', {})
            
            for nutrient, constraint in nutrients.items():
                if constraint.get('hard_soft_type') != 'HARD':
                    continue
                if constraint.get('constraint_type') == 'unlimited':
                    continue
                
                cumulative = cumulative_nutrients.get(nutrient, 0.0)
                food_val_per_100g = float(candidate.get(nutrient, 0) or 0)
                food_val_est = food_val_per_100g * est_scale
                max_val = constraint.get('max')
                min_val = float(constraint.get('min') or 0)
                
                # PENALTY: food would push cumulative over max
                if max_val is not None and max_val > 0:
                    if (cumulative + food_val_est) > max_val:
                        over_ratio = ((cumulative + food_val_est) - max_val) / max_val
                        constraint_score -= min(50, over_ratio * 60)
                
                # BONUS: food helps reach unfulfilled minimum
                remaining = min_val - cumulative
                if remaining > 0 and food_val_est > 0:
                    help_ratio = min(food_val_est, remaining) / max(min_val, 1)
                    constraint_score += min(20, help_ratio * 25)
            
            constraint_score = max(0, min(100, constraint_score))

        # 3. DIVERSITY SCORE (20%)
        diversity_score = 100
        for selected_name in selected_items_names:
            sim = SimilarityChecker.calculate_similarity_score(
                str(candidate.get('food_name', '')),
                selected_name
            )
            if sim > 0.7:
                diversity_score = 0
                break

        return (calorie_score * 0.4 +
                constraint_score * 0.4 +
                diversity_score * 0.2)
    
    def generate_candidates_for_course(
        self,
        course_type: str,
        target_calories_per_100g: float,
        current_meal_excluded: List[str],
        use_global_exclusion: bool = True
    ) -> List[Dict]:
        """
        PHASE 1: Generate 3 diverse candidates for a course.
        Operates on per-100g basis. No portion scaling yet.
        
        Args:
            course_type: 'Main', 'Side', 'Drink', or 'Snack' (SHORT FORM)
            target_calories_per_100g: Target per-100g energy value
            current_meal_excluded: Foods to exclude from this meal
            use_global_exclusion: Whether to use items from previous meals (default True, False for drinks)
        
        Returns:
            List of 3 candidate dicts (per-100g basis, not scaled)
        """
        # Combine exclusion lists (only use global if requested)
        if use_global_exclusion:
            global_excluded = [item.food_name for item in self.selected_items] + current_meal_excluded
        else:
            global_excluded = current_meal_excluded
        
        # Generate 30 raw candidates from database using SHORT form ('Main', 'Side', 'Drink', 'Snack')
        raw_candidates = CandidateGenerator.generate_candidates_for_slot(
            food_database=self.food_db,
            slot_category=course_type,  # Pass short form directly: 'Main', 'Side', 'Drink', 'Snack'
            target_calories=target_calories_per_100g,
            num_candidates=30,  # Increased from 10 to 30 to provide enough pool for diversity filtering
            exclusion_names=global_excluded,
        )
        
        if not raw_candidates:
            return []
        
        # Score all candidates
        scored = []
        for cand in raw_candidates:
            score = self.score_candidate(
                cand,
                target_calories_per_100g,
                global_excluded,
                cumulative_nutrients=self.cumulative_nutrients
            )
            scored.append((score, cand))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        
        # Select top 3 diverse candidates
        final_candidates = []
        added_names = []
        
        for score, cand in scored:
            # Check if similar to already added candidates
            is_duplicate = False
            for ans in added_names:
                if SimilarityChecker.calculate_similarity_score(
                    str(cand.get('food_name', '')), 
                    ans
                ) > 0.5:
                    is_duplicate = True
                    break
            
            if is_duplicate:
                continue
            
            final_candidates.append(cand)
            added_names.append(cand.get('food_name', ''))
            
            if len(final_candidates) >= 3:
                break
        
        return final_candidates
    
    # ================================================================
    # PHASE 2: PORTION OPTIMIZATION - Calculate realistic portions
    # ================================================================
    
    def optimize_portion(
        self,
        candidate_per_100g: Dict,
        target_calories: float,
        consumption_label: str
    ) -> float:
        """
        PHASE 2: Calculate realistic portion size.
        
        Formula:
            portion_g = (target_calories / energy_kcal_per_100g) * 100
        
        Then clamp to realistic range based on course type.
        
        Args:
            candidate_per_100g: Candidate dict (per-100g basis)
            target_calories: Target energy for this course
            consumption_label: 'Main Course', 'Side Dish', 'Drink', 'Snack'
        
        Returns:
            Optimized portion in grams (clamped to realistic range)
        """
        energy_100g = float(candidate_per_100g.get('energy_kcal', 0))
        
        # Calculate portion
        if energy_100g > 0:
            portion_g = (target_calories / energy_100g) * 100.0
        else:
            # Fallback if no energy data
            min_p, max_p = PORTION_RANGE.get(consumption_label, (50, 400))
            portion_g = (min_p + max_p) / 2.0
        
        # Clamp to realistic range
        min_portion, max_portion = PORTION_RANGE.get(consumption_label, (50, 400))
        portion_g = max(min_portion, min(max_portion, portion_g))
        
        # Round to the nearest whole integer gram for practical usability
        portion_g = float(round(portion_g))
        
        return portion_g
    
    def scale_nutrients(
        self,
        candidate_per_100g: Dict,
        portion_gram: float
    ) -> FoodItem:
        """
        PHASE 2: Scale all nutrients from per-100g to actual portion.
        
        scale = portion_g / 100
        actual_value = value_per_100g * scale
        
        Apply to all nutrients.
        """
        if portion_gram <= 0:
            portion_gram = 100.0
        
        scale = portion_gram / 100.0
        
        # Get all available nutrient columns from the database row
        # For now, we scale the main macronutrients
        food_item = FoodItem(
            fdc_id=str(candidate_per_100g.get('fdc_id', 'unknown')),
            food_name=str(candidate_per_100g.get('food_name', 'Unknown')),
            food_group=str(candidate_per_100g.get('food_group', 'Unknown')),
            consumption_label=str(candidate_per_100g.get('consumption_label', 'Unknown')),
            cuisine_label=str(candidate_per_100g.get('cuisine_label', 'Unknown')),
            portion_gram=round(portion_gram, 1),
            energy_kcal=round(float(candidate_per_100g.get('energy_kcal', 0)) * scale, 1),
            protein_g=round(float(candidate_per_100g.get('protein_g', 0)) * scale, 2),
            carbohydrate_g=round(float(candidate_per_100g.get('carbohydrate_g', 0)) * scale, 2),
            fat_g=round(float(candidate_per_100g.get('fat_g', 0)) * scale, 2),
        )
        
        scaled_micros = {}
        for col in MICRONUTRIENT_COLS:
            val = candidate_per_100g.get(col, 0.0)
            if val is not None:
                scaled_micros[col] = round(float(val) * scale, 4)
        
        food_item.micronutrients = scaled_micros
        
        return food_item
    
    def _update_cumulative(self, item: FoodItem):
        """Track selected items and cumulative nutrients"""
        self.cumulative_nutrients['energy_kcal'] += item.energy_kcal
        self.cumulative_nutrients['protein_g'] += item.protein_g
        self.cumulative_nutrients['carbohydrate_g'] += item.carbohydrate_g
        self.cumulative_nutrients['fat_g'] += item.fat_g
        
        for nutrient, value in item.micronutrients.items():
            if nutrient not in self.cumulative_nutrients:
                self.cumulative_nutrients[nutrient] = 0.0
            self.cumulative_nutrients[nutrient] += value
            
        self.selected_items.append(item)
    
    def generate_meal(
        self,
        meal_type: str,
        target_calories: float
    ) -> Meal:
        """
        Generate a complete meal (Breakfast/Lunch/Dinner) with all courses.
        
        PHASE 1 + 2 combined:
        1. Select diverse food candidates (Phase 1)
        2. Optimize portions and scale nutrients (Phase 2)
        """
        main_target = target_calories * COURSE_DISTRIBUTION['Main']
        side_target = target_calories * COURSE_DISTRIBUTION['Side']
        drink_target = target_calories * COURSE_DISTRIBUTION['Drink']
        
        courses = {}
        actual_calories = 0.0
        current_meal_excluded = []
        
        # 1. Main Course Candidate Selection & initial portion calculation
        main_candidates_per_100g = self.generate_candidates_for_course(
            'Main', main_target, current_meal_excluded
        )
        main_per_100g = main_candidates_per_100g[0] if main_candidates_per_100g else None
        main_portion = self.optimize_portion(main_per_100g, main_target, 'Main Course') if main_per_100g else 0.0
        if main_per_100g:
            current_meal_excluded.append(str(main_per_100g.get('food_name', '')))
        
        # 2. Side Dish Candidate Selection & initial portion calculation
        side_candidates_per_100g = self.generate_candidates_for_course(
            'Side', side_target, current_meal_excluded
        )
        side_per_100g = side_candidates_per_100g[0] if side_candidates_per_100g else None
        side_portion = self.optimize_portion(side_per_100g, side_target, 'Side Dish') if side_per_100g else 0.0
        if side_per_100g:
            current_meal_excluded.append(str(side_per_100g.get('food_name', '')))
        
        # 3. Drink Candidate Selection & initial portion calculation
        drink_candidates_per_100g = self.generate_candidates_for_course(
            'Drink', drink_target, [], use_global_exclusion=False
        )
        drink_per_100g = drink_candidates_per_100g[0] if drink_candidates_per_100g else None
        drink_portion = self.optimize_portion(drink_per_100g, drink_target, 'Drink') if drink_per_100g else 0.0

        # Calculate initial meal energy using clamped portion sizes
        main_energy_initial = (float(main_per_100g.get('energy_kcal', 0)) * main_portion / 100.0) if main_per_100g else 0.0
        side_energy_initial = (float(side_per_100g.get('energy_kcal', 0)) * side_portion / 100.0) if side_per_100g else 0.0
        drink_energy_initial = (float(drink_per_100g.get('energy_kcal', 0)) * drink_portion / 100.0) if drink_per_100g else 0.0
        total_energy_initial = main_energy_initial + side_energy_initial + drink_energy_initial

        # 4. RANGE-BASED SCALING
        # Estimate TDEE: target_calories = TDEE * MEAL_DISTRIBUTION[meal_type.lower()]
        meal_key = meal_type.lower()
        tdee_est = target_calories / MEAL_DISTRIBUTION.get(meal_key, 0.25)
        
        if meal_key == 'breakfast':
            min_target = tdee_est * 0.20
            max_target = tdee_est * 0.25
        elif meal_key == 'lunch':
            min_target = tdee_est * 0.30
            max_target = tdee_est * 0.35
        elif meal_key == 'dinner':
            min_target = tdee_est * 0.25
            max_target = tdee_est * 0.30
        else:
            min_target = target_calories
            max_target = target_calories
            
        # Calculate scale factor to bring energy within [min_target, max_target] range
        scale = 1.0
        if total_energy_initial > 0:
            if total_energy_initial < min_target:
                scale = min_target / total_energy_initial
            elif total_energy_initial > max_target:
                scale = max_target / total_energy_initial
            else:
                scale = 1.0  # Already inside range!
                
        # Clamp scale factor to [0.5, 2.0] for portion realism
        scale = max(0.5, min(2.0, scale))

        # 5. Optimize portions for the selected candidates to hit target calories while obeying hierarchy
        energy_m = float(main_per_100g.get('energy_kcal', 0)) if main_per_100g else 0.0
        energy_s = float(side_per_100g.get('energy_kcal', 0)) if side_per_100g else 0.0
        energy_d = float(drink_per_100g.get('energy_kcal', 0)) if drink_per_100g else 0.0

        min_m, max_m = PORTION_RANGE['Main Course']
        min_s, max_s = PORTION_RANGE['Side Dish']
        min_d, max_d = PORTION_RANGE['Drink']

        main_port_opt, side_port_opt, drink_port_opt = self.optimize_meal_portions(
            main_per_100g, side_per_100g, drink_per_100g,
            min_target, max_target,
            min_m, max_m,
            min_s, max_s,
            min_d, max_d
        )

        # Scale alternative Side and Drink candidates, clamping them below main_port_opt
        epsilon = 1.0  # strict inequality
        
        side_candidates_scaled = []
        if side_candidates_per_100g:
            for idx, cand_per_100g in enumerate(side_candidates_per_100g):
                if idx == 0:
                    portion_scaled = side_port_opt
                else:
                    portion = self.optimize_portion(cand_per_100g, side_target, 'Side Dish')
                    portion_scaled = float(round(portion * scale))
                    if portion_scaled >= main_port_opt:
                        portion_scaled = max(50.0, main_port_opt - epsilon)
                portion_scaled = float(round(portion_scaled))
                scaled = self.scale_nutrients(cand_per_100g, portion_scaled)
                side_candidates_scaled.append(scaled)

        drink_candidates_scaled = []
        if drink_candidates_per_100g:
            for idx, cand_per_100g in enumerate(drink_candidates_per_100g):
                if idx == 0:
                    portion_scaled = drink_port_opt
                else:
                    portion = self.optimize_portion(cand_per_100g, drink_target, 'Drink')
                    portion_scaled = float(round(portion * scale))
                    if portion_scaled >= main_port_opt:
                        portion_scaled = max(150.0, main_port_opt - epsilon)
                portion_scaled = float(round(portion_scaled))
                scaled = self.scale_nutrients(cand_per_100g, portion_scaled)
                drink_candidates_scaled.append(scaled)

        # Find the maximum portion size among all Side Dish and Drink candidates
        max_non_main = 0.0
        if side_candidates_scaled:
            max_non_main = max(max_non_main, max([c.portion_gram for c in side_candidates_scaled]))
        if drink_candidates_scaled:
            max_non_main = max(max_non_main, max([c.portion_gram for c in drink_candidates_scaled]))

        # Now scale all Main Course candidates and enforce: Main Course > max_non_main
        main_candidates_scaled = []
        if main_candidates_per_100g:
            for idx, cand_per_100g in enumerate(main_candidates_per_100g):
                if idx == 0:
                    portion_scaled = main_port_opt
                else:
                    portion = self.optimize_portion(cand_per_100g, main_target, 'Main Course')
                    portion_scaled = float(round(portion * scale))
                    if portion_scaled <= max_non_main:
                        portion_scaled = min(300.0, max_non_main + epsilon)
                portion_scaled = float(round(portion_scaled))
                scaled = self.scale_nutrients(cand_per_100g, portion_scaled)
                main_candidates_scaled.append(scaled)

        # Now construct the MealCourse objects using these static candidate lists
        # Main Course
        if main_candidates_scaled:
            main_scaled = main_candidates_scaled[0]
            courses['Main'] = MealCourse(
                course_type='Main',
                candidates=main_candidates_scaled,
                total_calories=main_scaled.energy_kcal,
                total_protein_g=main_scaled.protein_g,
                total_carb_g=main_scaled.carbohydrate_g,
                total_fat_g=main_scaled.fat_g
            )
            actual_calories += main_scaled.energy_kcal
            self._update_cumulative(main_scaled)
        
        # Side Dish
        if side_candidates_scaled:
            side_scaled = side_candidates_scaled[0]
            courses['Side'] = MealCourse(
                course_type='Side',
                candidates=side_candidates_scaled,
                total_calories=side_scaled.energy_kcal,
                total_protein_g=side_scaled.protein_g,
                total_carb_g=side_scaled.carbohydrate_g,
                total_fat_g=side_scaled.fat_g
            )
            actual_calories += side_scaled.energy_kcal
            self._update_cumulative(side_scaled)
        
        # Drink
        if drink_candidates_scaled:
            drink_scaled = drink_candidates_scaled[0]
            courses['Drink'] = MealCourse(
                course_type='Drink',
                candidates=drink_candidates_scaled,
                total_calories=drink_scaled.energy_kcal,
                total_protein_g=drink_scaled.protein_g,
                total_carb_g=drink_scaled.carbohydrate_g,
                total_fat_g=drink_scaled.fat_g
            )
            actual_calories += drink_scaled.energy_kcal
            self._update_cumulative(drink_scaled)
        
        return Meal(
            meal_type=meal_type,
            courses=courses,
            target_calories=target_calories,
            actual_calories=actual_calories,
            include_drink=True
        )
    
    def generate_snack(self, target_calories: float) -> SnackMeal:
        """Generate snack candidates with portion optimization"""
        snack_candidates_per_100g = self.generate_candidates_for_course(
            'Snack', target_calories, []
        )
        
        snack_candidates_scaled = []
        selected_calories = 0.0
        
        if snack_candidates_per_100g:
            # Estimate TDEE to compute the [10%, 15%] range
            tdee_est = target_calories / MEAL_DISTRIBUTION.get('snack', 0.1375)
            min_target = tdee_est * 0.10
            max_target = tdee_est * 0.15
            
            for cand_per_100g in snack_candidates_per_100g:
                portion = self.optimize_portion(cand_per_100g, target_calories, 'Snack')
                initial_energy = float(cand_per_100g.get('energy_kcal', 0)) * portion / 100.0
                
                scale = 1.0
                if initial_energy > 0:
                    if initial_energy < min_target:
                        scale = min_target / initial_energy
                    elif initial_energy > max_target:
                        scale = max_target / initial_energy
                    else:
                        scale = 1.0
                
                # Clamp scale to keep snack portions realistic
                scale = max(0.8, min(1.25, scale))
                
                final_portion = float(round(portion * scale))
                scaled = self.scale_nutrients(cand_per_100g, final_portion)
                snack_candidates_scaled.append(scaled)
            
            # Track the first (selected) snack
            self._update_cumulative(snack_candidates_scaled[0])
            selected_calories = snack_candidates_scaled[0].energy_kcal
        
        return SnackMeal(
            meal_type='Snack',
            candidates=snack_candidates_scaled,
            target_calories=target_calories,
            actual_calories=selected_calories
        )
    
    # ================================================================
    # MAIN ENTRY POINT - Generate complete menu plan
    # ================================================================
    
    def generate_menu(
        self,
        user_profile: Dict,
        tdee: float
    ) -> MenuPlan:
        """
        Generate complete menu plan using TDEE.
        
        Calculates meal targets using validated distribution percentages:
        - Breakfast: 23.75%
        - Lunch: 33.75%
        - Dinner: 28.75%
        - Snack: 13.75%
        """
        self._init_cumulative_tracking()
        self.selected_items = []
        
        # Calculate meal targets in kcal
        breakfast_target = tdee * MEAL_DISTRIBUTION['breakfast']
        lunch_target = tdee * MEAL_DISTRIBUTION['lunch']
        dinner_target = tdee * MEAL_DISTRIBUTION['dinner']
        snack_target = tdee * MEAL_DISTRIBUTION['snack']
        
        print(f"\n[TARGETS] Meal Targets (TDEE {tdee:.0f} kcal):")
        print(f"  Breakfast: {breakfast_target:.0f} kcal")
        print(f"  Lunch: {lunch_target:.0f} kcal")
        print(f"  Dinner: {dinner_target:.0f} kcal")
        print(f"  Snack: {snack_target:.0f} kcal")
        
        # Generate meals
        breakfast = self.generate_meal('Breakfast', breakfast_target)
        lunch = self.generate_meal('Lunch', lunch_target)
        dinner = self.generate_meal('Dinner', dinner_target)
        snack = self.generate_snack(snack_target)
        
        
        # Create MenuPlan
        feasible = True
        violations = []
        
        # TODO: Evaluate compliance using validate_final_solution
        # Currently portioned_df is not exposed by greedy optimizer
        # Need to reconstruct or modify optimizer to track it
        
        menu_plan = MenuPlan(
            algorithm_used='Greedy',
            user_profile=user_profile,
            breakfast=breakfast,
            lunch=lunch,
            dinner=dinner,
            snack=snack,
            total_daily_calories=self.cumulative_nutrients['energy_kcal'],
            total_daily_protein_g=self.cumulative_nutrients['protein_g'],
            total_daily_carb_g=self.cumulative_nutrients['carbohydrate_g'],
            total_daily_fat_g=self.cumulative_nutrients['fat_g'],
            daily_micronutrients=self.cumulative_nutrients,
            feasible=feasible,
            violations=violations,
            compliance_rate=0.0,        # Placeholder: evaluate in future
            n_constraints_passed=0,     # Placeholder: evaluate in future
            n_constraints_total=0       # Placeholder: evaluate in future
        )
        
        return menu_plan

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
    'Main Course': (150, 400),
    'Side Dish': (50, 250),
    'Drink': (150, 300),
    'Snack': (30, 100)
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
        energy_100g = candidate.get('energy_kcal', 0)
        calorie_error = abs(energy_100g - target_calories) / target_calories
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
                
                current_total = cumulative_nutrients.get(nutrient, 0.0)
                food_val = float(candidate.get(nutrient, 0) or 0)
                max_val = constraint.get('max')
                min_val = float(constraint.get('min') or 0)
                
                # Penalty: if adding this food would exceed max
                if max_val is not None and max_val > 0:
                    if (current_total + food_val) > (max_val * 1.1):
                        constraint_score -= 20
                
                # Bonus: if this food helps reach unfulfilled minimum
                if current_total < min_val and food_val > 0:
                    constraint_score += 10
            
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
            
            max_candidates = 2 if course_type == 'Drink' else 3
            if len(final_candidates) >= max_candidates:
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
        
        # Main Course
        main_candidates_per_100g = self.generate_candidates_for_course(
            'Main', main_target, current_meal_excluded
        )
        if main_candidates_per_100g:
            main_per_100g = main_candidates_per_100g[0]
            main_portion = self.optimize_portion(main_per_100g, main_target, 'Main Course')
            main_scaled = self.scale_nutrients(main_per_100g, main_portion)
            
            # Create MealCourse with all 3 candidates (scaled for display)
            main_candidates_scaled = []
            for cand_per_100g in main_candidates_per_100g:
                portion = self.optimize_portion(cand_per_100g, main_target, 'Main Course')
                scaled = self.scale_nutrients(cand_per_100g, portion)
                main_candidates_scaled.append(scaled)
            
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
            current_meal_excluded.append(main_scaled.food_name)
        
        # Side Dish
        side_candidates_per_100g = self.generate_candidates_for_course(
            'Side', side_target, current_meal_excluded
        )
        if side_candidates_per_100g:
            side_per_100g = side_candidates_per_100g[0]
            side_portion = self.optimize_portion(side_per_100g, side_target, 'Side Dish')
            side_scaled = self.scale_nutrients(side_per_100g, side_portion)
            
            side_candidates_scaled = []
            for cand_per_100g in side_candidates_per_100g:
                portion = self.optimize_portion(cand_per_100g, side_target, 'Side Dish')
                scaled = self.scale_nutrients(cand_per_100g, portion)
                side_candidates_scaled.append(scaled)
            
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
            current_meal_excluded.append(side_scaled.food_name)
        
        # Drink (no global exclusion - drinks can repeat across meals)
        drink_candidates_per_100g = self.generate_candidates_for_course(
            'Drink', drink_target, [], use_global_exclusion=False
        )
        
        if drink_candidates_per_100g:
            drink_per_100g = drink_candidates_per_100g[0]
            drink_portion = self.optimize_portion(drink_per_100g, drink_target, 'Drink')
            drink_scaled = self.scale_nutrients(drink_per_100g, drink_portion)
            
            drink_candidates_scaled = []
            for cand_per_100g in drink_candidates_per_100g:
                portion = self.optimize_portion(cand_per_100g, drink_target, 'Drink')
                scaled = self.scale_nutrients(cand_per_100g, portion)
                drink_candidates_scaled.append(scaled)
            
            # Append Mineral Water as the mandatory 3rd candidate
            water = FoodItem(
                fdc_id='water_000',
                food_name='Mineral Water',
                food_group='Beverages',
                consumption_label='Drink',
                cuisine_label='Generic',
                portion_gram=250.0,
                energy_kcal=0.0,
                protein_g=0.0,
                carbohydrate_g=0.0,
                fat_g=0.0,
                micronutrients={}
            )
            drink_candidates_scaled.append(water)
            
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
            # current_meal_excluded.append(drink_scaled.food_name)
        
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
            for cand_per_100g in snack_candidates_per_100g:
                portion = self.optimize_portion(cand_per_100g, target_calories, 'Snack')
                scaled = self.scale_nutrients(cand_per_100g, portion)
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
            violations=violations
        )
        
        return menu_plan

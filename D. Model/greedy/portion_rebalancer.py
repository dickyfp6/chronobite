"""
PHASE 3: POST-SELECTION PORTION REBALANCING
==============================================

After user makes substitutions (e.g., choosing Water instead of selected drink),
attempt to recover nutritional deficits by adjusting portions of already-selected foods.

IMPORTANT RULES:
- DO NOT change which foods are selected
- DO NOT replace foods
- DO NOT generate new foods
- Only adjust portion_g for foods already selected
- Respect realistic portion limits
- Maximize nutritional coverage
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from meal_schema import FoodItem, Meal, SnackMeal, MealCourse

# Portion limits (same as in optimizer)
PORTION_RANGE = {
    'Main Course': (100, 400),
    'Side Dish': (50, 250),
    'Drink': (100, 300),
    'Snack': (30, 100)
}


@dataclass
class NutritionGap:
    """Represents a nutritional deficit"""
    energy_gap_kcal: float = 0.0
    protein_gap_g: float = 0.0
    fat_gap_g: float = 0.0
    carb_gap_g: float = 0.0
    magnitude: float = 0.0  # Total gap magnitude for prioritization


@dataclass
class PortionRebalanceResult:
    """Result of portion rebalancing operation"""
    success: bool
    nutrition_gap_before: NutritionGap
    nutrition_gap_after: NutritionGap
    rebalanced_items: List[Tuple[str, float, float]] = field(default_factory=list)  # (name, original_portion, new_portion)
    nutrition_coverage_before: Dict[str, float] = field(default_factory=dict)
    nutrition_coverage_after: Dict[str, float] = field(default_factory=dict)
    message: str = ""


class PortionRebalancer:
    """
    Post-selection portion rebalancing utility.
    
    Workflow:
    1. Calculate nutritional deficits after user substitutions
    2. Identify which foods can absorb portion increases
    3. Increase portions of high-impact foods (calorie/nutrient dense)
    4. Respect realistic serving size limits
    5. Return rebalanced portions and updated nutrition summary
    """
    
    @staticmethod
    def calculate_nutrition_gap(
        target_nutrition: Dict[str, float],
        current_nutrition: Dict[str, float]
    ) -> NutritionGap:
        """
        Calculate nutritional deficit between target and current.
        
        Args:
            target_nutrition: Target daily nutrition (e.g., from DRI guidelines)
            current_nutrition: Current nutrition after user substitutions
        
        Returns:
            NutritionGap with all deficits
        """
        gap = NutritionGap(
            energy_gap_kcal=max(0, target_nutrition.get('energy_kcal', 0) - current_nutrition.get('energy_kcal', 0)),
            protein_gap_g=max(0, target_nutrition.get('protein_g', 0) - current_nutrition.get('protein_g', 0)),
            fat_gap_g=max(0, target_nutrition.get('fat_g', 0) - current_nutrition.get('fat_g', 0)),
            carb_gap_g=max(0, target_nutrition.get('carbohydrate_g', 0) - current_nutrition.get('carbohydrate_g', 0)),
        )
        
        # Calculate gap magnitude (normalized)
        gap.magnitude = (
            gap.energy_gap_kcal / max(target_nutrition.get('energy_kcal', 1), 1) * 0.4 +
            gap.protein_gap_g / max(target_nutrition.get('protein_g', 1), 1) * 0.3 +
            gap.fat_gap_g / max(target_nutrition.get('fat_g', 1), 1) * 0.15 +
            gap.carb_gap_g / max(target_nutrition.get('carbohydrate_g', 1), 1) * 0.15
        )
        
        return gap
    
    @staticmethod
    def calculate_nutrient_density(food_item: FoodItem) -> Dict[str, float]:
        """
        Calculate nutrient density per gram for a food.
        
        Returns:
            Dict with 'energy', 'protein', 'fat', 'carb' per gram
        """
        if food_item.portion_gram <= 0:
            return {'energy': 0, 'protein': 0, 'fat': 0, 'carb': 0}
        
        per_gram = food_item.portion_gram
        
        return {
            'energy': food_item.energy_kcal / per_gram,
            'protein': food_item.protein_g / per_gram,
            'fat': food_item.fat_g / per_gram,
            'carb': food_item.carbohydrate_g / per_gram,
        }
    
    @staticmethod
    def scale_food_to_portion(
        food_item: FoodItem,
        new_portion_gram: float
    ) -> FoodItem:
        """
        Create a new FoodItem with scaled nutrients for a new portion.
        
        Args:
            food_item: Original food item with current portion
            new_portion_gram: New portion size in grams
        
        Returns:
            New FoodItem with scaled nutrients
        """
        # Round to the nearest whole integer gram for practical usability
        rounded_portion_gram = float(round(new_portion_gram))
        
        if food_item.portion_gram <= 0:
            scale = 1.0
        else:
            scale = rounded_portion_gram / food_item.portion_gram
        
        # Create new item with scaled values
        return FoodItem(
            fdc_id=food_item.fdc_id,
            food_name=food_item.food_name,
            food_group=food_item.food_group,
            consumption_label=food_item.consumption_label,
            cuisine_label=food_item.cuisine_label,
            portion_gram=rounded_portion_gram,
            energy_kcal=round(food_item.energy_kcal * scale, 1),
            protein_g=round(food_item.protein_g * scale, 2),
            carbohydrate_g=round(food_item.carbohydrate_g * scale, 2),
            fat_g=round(food_item.fat_g * scale, 2),
        )
    
    @staticmethod
    def rebalance_meal(
        meal: Meal,
        nutrition_gap: NutritionGap,
        target_nutrition: Dict[str, float]
    ) -> Tuple[Meal, List[Tuple[str, float, float]]]:
        """
        Rebalance portions within a meal to close nutritional gaps.
        
        Strategy:
        1. Identify which foods can increase (still under max portion)
        2. Prioritize by nutrient density (energy, protein, etc.)
        3. Increase portions iteratively until gap closes or max portions reached
        
        Args:
            meal: The meal to rebalance
            nutrition_gap: Current nutritional gap
            target_nutrition: Target daily nutrition
        
        Returns:
            Tuple of (rebalanced_meal, list of changes)
        """
        if not meal or not meal.courses:
            return meal, []
        
        changes = []  # (food_name, original_portion, new_portion)
        
        # Build list of food items in meal with their max portions
        foods_to_rebalance = []
        
        for course_type, course in meal.courses.items():
            if not course or not course.candidates:
                continue
            
            # Use the first candidate (the selected one)
            food_item = course.candidates[0]
            
            # Determine max portion for this food
            consumption_label = food_item.consumption_label
            # Map consumption_label to portion range category
            # e.g., 'Main Course' -> 'Main Course', or handle any variations
            min_p, max_p = PORTION_RANGE.get(consumption_label, (50, 400))
            
            foods_to_rebalance.append({
                'item': food_item,
                'course_type': course_type,
                'current_portion': food_item.portion_gram,
                'min_portion': min_p,
                'max_portion': max_p,
                'density': PortionRebalancer.calculate_nutrient_density(food_item)
            })
        
        # If nutrition gap is minimal, don't rebalance
        if nutrition_gap.magnitude < 0.05:  # Less than 5% gap
            return meal, changes
        
        # Try to increase portions
        total_gap_magnitude = nutrition_gap.magnitude
        
        for attempt in range(3):  # Make up to 3 passes
            if total_gap_magnitude < 0.05:
                break
            # Find current main course portion
            main_port = None
            for f in foods_to_rebalance:
                if f['course_type'] == 'Main':
                    main_port = f['current_portion']
                    break

            # Find best food to increase (highest energy density for energy gaps)
            best_food = None
            best_score = 0
            best_idx = -1
            
            for idx, food_dict in enumerate(foods_to_rebalance):
                # Enforce portion hierarchy constraints: Main > Side and Main > Drink
                max_allowed_portion = food_dict['max_portion']
                if food_dict['course_type'] in ['Side', 'Drink'] and main_port is not None:
                    max_allowed_portion = min(max_allowed_portion, main_port - 1.0)

                if food_dict['current_portion'] >= max_allowed_portion:
                    continue  # Already at max or constrained by Main Course
                
                # Score based on nutrient gap priorities
                score = 0
                if nutrition_gap.energy_gap_kcal > 0:
                    score += food_dict['density']['energy'] * nutrition_gap.energy_gap_kcal
                if nutrition_gap.protein_gap_g > 0:
                    score += food_dict['density']['protein'] * nutrition_gap.protein_gap_g * 2
                
                if score > best_score:
                    best_score = score
                    best_food = food_dict
                    best_idx = idx
            
            if best_food is None:
                break  # All foods at max portions or constrained
            
            # Increase portion by increments
            old_portion = best_food['current_portion']
            # Recheck max allowed portion for best_food
            max_allowed_portion = best_food['max_portion']
            if best_food['course_type'] in ['Side', 'Drink'] and main_port is not None:
                max_allowed_portion = min(max_allowed_portion, main_port - 1.0)

            max_increase = max_allowed_portion - old_portion
            increment = max(1.0, max_increase * 0.2)
            new_portion = min(old_portion + increment, max_allowed_portion)
            # Ensure final portion is rounded to nearest whole integer gram
            new_portion = float(round(new_portion))
            
            best_food['current_portion'] = new_portion

        # Final safety enforcement of portion hierarchy constraints
        main_port = None
        for f in foods_to_rebalance:
            if f['course_type'] == 'Main':
                main_port = f['current_portion']
                break
                
        if main_port is not None:
            for f in foods_to_rebalance:
                if f['course_type'] in ['Side', 'Drink']:
                    if f['current_portion'] >= main_port:
                        f['current_portion'] = max(f['min_portion'], main_port - 1.0)
                        f['current_portion'] = float(round(f['current_portion']))
            
            # Recalculate gap with new portions
            new_totals = {
                'energy_kcal': 0.0,
                'protein_g': 0.0,
                'fat_g': 0.0,
                'carbohydrate_g': 0.0,
            }
            
            for food_dict in foods_to_rebalance:
                scale = food_dict['current_portion'] / food_dict['item'].portion_gram
                new_totals['energy_kcal'] += food_dict['item'].energy_kcal * scale
                new_totals['protein_g'] += food_dict['item'].protein_g * scale
                new_totals['fat_g'] += food_dict['item'].fat_g * scale
                new_totals['carbohydrate_g'] += food_dict['item'].carbohydrate_g * scale
            
            # Update nutrition gap
            nutrition_gap = PortionRebalancer.calculate_nutrition_gap(target_nutrition, new_totals)
            total_gap_magnitude = nutrition_gap.magnitude
        
        # Build new meal with rebalanced portions
        new_meal = Meal(
            meal_type=meal.meal_type,
            courses={},
            target_calories=meal.target_calories,
            actual_calories=0,
            include_drink=meal.include_drink
        )
        
        actual_calories = 0
        
        for food_dict in foods_to_rebalance:
            original_item = food_dict['item']
            new_portion = food_dict['current_portion']
            
            # Record change if portion changed
            if new_portion != food_dict['item'].portion_gram:
                changes.append((
                    original_item.food_name,
                    round(food_dict['item'].portion_gram, 1),
                    round(new_portion, 1)
                ))
            
            # Create scaled food item
            scaled_item = PortionRebalancer.scale_food_to_portion(original_item, new_portion)
            
            # Find which course this belongs to
            for food_check in foods_to_rebalance:
                if food_check['item'] == original_item:
                    course_type = food_check['course_type']
                    break
            
            # Create course with rebalanced item as first candidate
            candidates = [scaled_item]  # Only show the selected (rebalanced) item
            
            new_meal.courses[course_type] = MealCourse(
                course_type=course_type,
                candidates=candidates,
                total_calories=scaled_item.energy_kcal,
                total_protein_g=scaled_item.protein_g,
                total_carb_g=scaled_item.carbohydrate_g,
                total_fat_g=scaled_item.fat_g
            )
            
            actual_calories += scaled_item.energy_kcal
        
        new_meal.actual_calories = actual_calories
        
        return new_meal, changes
    
    @staticmethod
    def rebalance_menu(
        breakfast: Meal,
        lunch: Meal,
        dinner: Meal,
        snack: Optional[SnackMeal],
        target_nutrition: Dict[str, float],
        current_nutrition: Dict[str, float]
    ) -> PortionRebalanceResult:
        """
        Rebalance entire day's menu to close nutritional gaps.
        
        Args:
            breakfast, lunch, dinner, snack: Current meals after user substitutions
            target_nutrition: Target daily nutrition
            current_nutrition: Current nutrition after substitutions
        
        Returns:
            PortionRebalanceResult with before/after comparison
        """
        gap_before = PortionRebalancer.calculate_nutrition_gap(target_nutrition, current_nutrition)
        
        all_changes = []
        
        # Rebalance each meal
        breakfast, changes_b = PortionRebalancer.rebalance_meal(breakfast, gap_before, target_nutrition)
        all_changes.extend(changes_b)
        
        lunch, changes_l = PortionRebalancer.rebalance_meal(lunch, gap_before, target_nutrition)
        all_changes.extend(changes_l)
        
        dinner, changes_d = PortionRebalancer.rebalance_meal(dinner, gap_before, target_nutrition)
        all_changes.extend(changes_d)
        
        # Recalculate nutrition after rebalancing
        new_nutrition = {
            'energy_kcal': 0.0,
            'protein_g': 0.0,
            'fat_g': 0.0,
            'carbohydrate_g': 0.0,
        }
        
        # Aggregate from meals (simplified - would need to iterate through courses)
        if breakfast:
            new_nutrition['energy_kcal'] += breakfast.actual_calories
        if lunch:
            new_nutrition['energy_kcal'] += lunch.actual_calories
        if dinner:
            new_nutrition['energy_kcal'] += dinner.actual_calories
        if snack:
            new_nutrition['energy_kcal'] += snack.actual_calories
        
        gap_after = PortionRebalancer.calculate_nutrition_gap(target_nutrition, new_nutrition)
        
        # Calculate coverage percentages
        coverage_before = {
            'energy': min(100, (current_nutrition.get('energy_kcal', 0) / target_nutrition.get('energy_kcal', 1)) * 100),
            'protein': min(100, (current_nutrition.get('protein_g', 0) / target_nutrition.get('protein_g', 1)) * 100),
        }
        
        coverage_after = {
            'energy': min(100, (new_nutrition['energy_kcal'] / target_nutrition.get('energy_kcal', 1)) * 100),
            'protein': min(100, (new_nutrition['protein_g'] / target_nutrition.get('protein_g', 1)) * 100),
        }
        
        return PortionRebalanceResult(
            success=True,
            nutrition_gap_before=gap_before,
            nutrition_gap_after=gap_after,
            rebalanced_items=all_changes,
            nutrition_coverage_before=coverage_before,
            nutrition_coverage_after=coverage_after,
            message=f"Rebalanced {len(all_changes)} food portions to recover nutritional deficits"
        )

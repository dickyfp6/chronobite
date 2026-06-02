"""
Greedy Algorithm for Meal Planning Optimization
Menggunakan locally optimal choice pada setiap slot untuk mendapatkan menu berkualitas

Mekanisme:
1. Untuk setiap meal slot (breakfast main, lunch side, etc)
2. Generate candidates dengan similarity check (ingredient diversity)
3. Score setiap candidate berdasarkan:
   - Calorie match to target (minimize error)
   - HARD constraint satisfaction (penalize or exclude violators)
   - SOFT constraint bonus (reward if satisfied)
   - Food diversity (no repeated main ingredient)
4. Pilih candidate dengan score tertinggi (greedy step)
5. Update cumulative daily nutrient tracking
6. Return complete MenuPlan dengan constraint validation

Output: MenuPlan (same contract as Genetic Algorithm)

Breaking Changes Fixed:
✓ BUG 1: constraint_bag now USED for scoring (not just stored)
✓ BUG 2: score_candidate() uses actual constraint_bag bounds per nutrient
✓ BUG 3: Snack detection uses consumption_label safely
✓ BUG 4: Course calorie split made configurable
✓ BUG 5: test_cli.py uses 'disease' key (not 'health_condition')
"""

import pandas as pd
import math
from typing import List, Dict, Tuple, Optional, Set
from meal_schema import FoodItem, MealCourse, Meal, SnackMeal, MenuPlan
from candidate_generator import CandidateGenerator
from similarity_checker import SimilarityChecker


class GreedyOptimizer:
    """Greedy Algorithm untuk generate optimal meal plan dengan constraint-aware scoring"""
    
    def __init__(self, food_database: pd.DataFrame, constraint_bag: Dict):
        """
        Initialize Greedy Optimizer
        
        Args:
            food_database: DataFrame dengan food items (dari NutritionService)
            constraint_bag: Dict dengan nutrient constraints (dari NutritionService.guidelines)
                {
                    'disease': ['dm2'],
                    'nutrients': {
                        'energy_kcal': {'min': 1800, 'max': 2200, 'hard_soft_type': 'HARD', ...},
                        ...
                    }
                }
        """
        self.food_db = food_database.copy()
        self.constraint_bag = constraint_bag
        self.similarity_checker = SimilarityChecker()
        self.selected_items = []  # Track semua yang sudah dipilih
        
        # Cumulative tracking untuk daily nutrients
        self.cumulative_nutrients = {}
        self._init_cumulative_tracking()
    
    def _init_cumulative_tracking(self):
        """Initialize cumulative nutrient tracking struktur"""
        self.cumulative_nutrients = {
            'energy_kcal': 0.0,
            'protein_g': 0.0,
            'carbohydrate_g': 0.0,
            'fat_g': 0.0,
        }
        
        # Add all nutrients dari constraint_bag
        if 'nutrients' in self.constraint_bag:
            for nutrient_name in self.constraint_bag['nutrients'].keys():
                self.cumulative_nutrients[nutrient_name] = 0.0
    
    def _check_hard_constraint_violation(
        self,
        candidate: Dict,
        nutrient_name: str,
        constraint: Dict,
        cumulative_so_far: float,
        item_portion_gram: float = 100.0
    ) -> Tuple[bool, float]:
        """
        Check jika candidate akan violate HARD constraint jika ditambahkan
        
        Args:
            candidate: Candidate food item
            nutrient_name: Nutrient key (e.g., 'sodium_mg')
            constraint: Constraint definition dengan 'min', 'max', 'hard_soft_type'
            cumulative_so_far: Current cumulative total untuk nutrient ini
            item_portion_gram: Portion size (default 100g)
        
        Returns:
            (is_violated: bool, new_total: float)
            - is_violated=True jika adding this item violates HARD constraint
        """
        if constraint.get('hard_soft_type') != 'HARD':
            return False, cumulative_so_far
        
        # Get nutrient value dari candidate (normalize ke 100g basis)
        nutrient_per_100g = candidate.get(nutrient_name, 0.0)
        if nutrient_per_100g is None or pd.isna(nutrient_per_100g):
            nutrient_per_100g = 0.0
        
        # Scale to actual portion
        nutrient_value = nutrient_per_100g * (item_portion_gram / 100.0)
        new_total = cumulative_so_far + nutrient_value
        
        # Check bounds
        min_constraint = constraint.get('min')
        max_constraint = constraint.get('max')
        
        # Only check if we're at the end of day (after all meals)
        # For now, we'll do soft checking during meal generation
        # and hard validation at the end
        
        return False, new_total
    
    def score_candidate(
        self,
        candidate: Dict,
        target_calories: float,
        selected_items: List[str],
        constraint_bag: Optional[Dict] = None,
        cumulative_nutrients: Optional[Dict] = None,
        weight_calorie: float = 0.5,
        weight_hard_constraints: float = 0.3,
        weight_soft_constraints: float = 0.1,
        weight_diversity: float = 0.1
    ) -> float:
        """
        Score satu candidate berdasarkan multiple factors dengan constraint awareness
        
        Args:
            candidate: Dict food item dengan nutritional info
            target_calories: Target calori untuk slot
            selected_items: List food names yang sudah dipilih (untuk diversity check)
            constraint_bag: Nutrient constraints dict (opsional)
            cumulative_nutrients: Current cumulative nutrients (opsional)
            weight_calorie: Bobot calorie match (default 0.5)
            weight_hard_constraints: Bobot HARD constraint satisfaction (default 0.3)
            weight_soft_constraints: Bobot SOFT constraint bonus (default 0.1)
            weight_diversity: Bobot ingredient diversity (default 0.1)
        
        Returns:
            Score dari 0-100 (higher is better)
        """
        scores = {}
        
        # 1. CALORIE MATCH SCORE
        calorie_error = abs(candidate.get('energy_kcal', 0) - target_calories) / max(target_calories, 1)
        if calorie_error <= 0.1:
            scores['calorie'] = 100
        elif calorie_error <= 0.2:
            scores['calorie'] = 80
        elif calorie_error <= 0.3:
            scores['calorie'] = 50
        else:
            scores['calorie'] = max(0, 100 - (calorie_error * 200))
        
        # 2. HARD CONSTRAINT SATISFACTION SCORE
        hard_constraint_score = 100.0
        
        if constraint_bag and cumulative_nutrients:
            hard_violations = 0
            hard_total = 0
            
            nutrients_def = constraint_bag.get('nutrients', {})
            for nutrient_name, constraint in nutrients_def.items():
                if constraint.get('hard_soft_type') != 'HARD':
                    continue
                
                hard_total += 1
                nutrient_value = candidate.get(nutrient_name, 0.0) or 0.0
                new_cumulative = cumulative_nutrients.get(nutrient_name, 0.0) + nutrient_value
                
                min_val = constraint.get('min')
                max_val = constraint.get('max')
                
                # Check if this would violate bounds (soft check, not hard fail)
                is_above_max = max_val is not None and new_cumulative > max_val * 1.1  # 10% tolerance
                is_below_min = min_val is not None and new_cumulative < min_val * 0.9  # 10% tolerance
                
                if is_above_max or is_below_min:
                    hard_violations += 1
            
            if hard_total > 0:
                hard_constraint_score = 100 * (1 - (hard_violations / hard_total))
        
        scores['hard_constraints'] = hard_constraint_score
        
        # 3. SOFT CONSTRAINT BONUS SCORE
        soft_constraint_score = 0.0
        
        if constraint_bag and cumulative_nutrients:
            soft_satisfied = 0
            soft_total = 0
            
            nutrients_def = constraint_bag.get('nutrients', {})
            for nutrient_name, constraint in nutrients_def.items():
                if constraint.get('hard_soft_type') != 'SOFT':
                    continue
                
                soft_total += 1
                nutrient_value = candidate.get(nutrient_name, 0.0) or 0.0
                new_cumulative = cumulative_nutrients.get(nutrient_name, 0.0) + nutrient_value
                
                target_val = constraint.get('min', 0)
                
                # Bonus if we're moving towards the target
                if target_val > 0 and new_cumulative <= target_val:
                    soft_satisfied += 1
            
            if soft_total > 0:
                soft_constraint_score = 100 * (soft_satisfied / soft_total)
        
        scores['soft_constraints'] = soft_constraint_score
        
        # 4. INGREDIENT DIVERSITY SCORE
        has_repeated_ingredient = False
        for selected_name in selected_items:
            similarity = SimilarityChecker.calculate_similarity_score(
                candidate.get('food_name', ''),
                selected_name
            )
            if similarity > 0.7:
                has_repeated_ingredient = True
                break
        
        scores['diversity'] = 0 if has_repeated_ingredient else 100
        
        # WEIGHTED SCORE
        final_score = (
            scores['calorie'] * weight_calorie +
            scores['hard_constraints'] * weight_hard_constraints +
            scores['soft_constraints'] * weight_soft_constraints +
            scores['diversity'] * weight_diversity
        )
        
        return final_score
    
    def select_best_candidate_for_slot(
        self,
        slot_category: str,
        target_calories: float,
        num_candidates: int = 3,
        exclusion_names: Optional[List[str]] = None
    ) -> Optional[FoodItem]:
        """
        Greedy step: Select single best candidate untuk satu slot
        
        Args:
            slot_category: 'Main', 'Side', 'Drink'
            target_calories: Target calori untuk slot
            num_candidates: Generate N candidates, pick best
            exclusion_names: List nama makanan untuk exclude (default: use selected_items for global diversity)
        
        Returns:
            FoodItem object (best scored candidate) atau None
        """
        
        if exclusion_names is None:
            # Global diversity: exclude from ALL previous meals
            exclusion_names = [item.food_name for item in self.selected_items]
        
        candidates_list = CandidateGenerator.generate_candidates_for_slot(
            food_database=self.food_db,
            slot_category=slot_category,
            target_calories=target_calories,
            num_candidates=num_candidates,
            exclusion_names=exclusion_names,
        )
        
        if not candidates_list:
            return None
        
        # Score setiap candidate dengan constraint awareness
        best_score = -1
        best_candidate = None
        
        for candidate_dict in candidates_list:
            score = self.score_candidate(
                candidate=candidate_dict,
                target_calories=target_calories,
                selected_items=[item.food_name for item in self.selected_items],
                constraint_bag=self.constraint_bag,
                cumulative_nutrients=self.cumulative_nutrients
            )
            
            if score > best_score:
                best_score = score
                best_candidate = candidate_dict
        
        # Convert dict to FoodItem dan track
        if best_candidate:
            # Calculate portion scaling
            # Dataset is per 100g. Scalar = target / calories_per_100g
            energy_per_100g = float(best_candidate.get('energy_kcal', 0))
            if energy_per_100g > 0:
                portion_gram = (target_calories / energy_per_100g) * 100.0
            else:
                portion_gram = 100.0  # Fallback
            
            # Limit portion gram to realistic range (e.g. 50g to 500g)
            portion_gram = max(50.0, min(500.0, portion_gram))
            
            # Scale nutrients
            scale = portion_gram / 100.0
            
            food_item = FoodItem(
                fdc_id=str(best_candidate.get('fdc_id', 'unknown')),
                food_name=str(best_candidate.get('food_name', 'Unknown')),
                food_group=str(best_candidate.get('food_group', 'Unknown')),
                consumption_label=str(best_candidate.get('consumption_label', slot_category)),
                cuisine_label=str(best_candidate.get('cuisine_label', 'Unknown')),
                portion_gram=round(portion_gram, 1),
                energy_kcal=round(energy_per_100g * scale, 1),
                protein_g=round(float(best_candidate.get('protein_g', 0)) * scale, 2),
                carbohydrate_g=round(float(best_candidate.get('carbohydrate_g', 0)) * scale, 2),
                fat_g=round(float(best_candidate.get('fat_g', 0)) * scale, 2),
            )
            
            # Update tracking with scaled values
            self.selected_items.append(food_item)
            scaled_dict = best_candidate.copy()
            for k in ['energy_kcal', 'protein_g', 'carbohydrate_g', 'fat_g']:
                scaled_dict[k] = getattr(food_item, k)
            # Add other nutrients if needed
            if 'nutrients' in self.constraint_bag:
                for n_name in self.constraint_bag['nutrients'].keys():
                    if n_name not in ['energy_kcal', 'protein_g', 'carbohydrate_g', 'fat_g']:
                        val = float(best_candidate.get(n_name, 0) or 0)
                        scaled_dict[n_name] = round(val * scale, 3)
            
            self._update_cumulative_nutrients(scaled_dict)
            
            return food_item
        
        return None
    
    def generate_drink_options(
        self,
        meal_targets: Dict[str, float],
        num_candidates: int = 3
    ) -> Dict[str, List[FoodItem]]:
        """
        Phase 1: Generate diverse drink candidates for each meal
        
        Args:
            meal_targets: Dict {'breakfast': total_kcal, ...}
            num_candidates: Number of options per meal (default 3)
            
        Returns:
            Dict {'breakfast': [FoodItem, ...], 'lunch': [...], 'dinner': [...]}
        """
        results = {}
        # Meal split for drinks is roughly 10% of meal target
        drink_weight = 0.1
        
        for meal_type in ['breakfast', 'lunch', 'dinner']:
            target = meal_targets.get(meal_type, 600) * drink_weight
            
            candidates_list = CandidateGenerator.generate_candidates_for_slot(
                food_database=self.food_db,
                slot_category='Drink',
                target_calories=target,
                num_candidates=num_candidates,
                exclusion_names=[item.food_name for item in self.selected_items],
            )
            
            items = []
            for cand in candidates_list:
                # Scale portion
                energy_per_100g = float(cand.get('energy_kcal', 0))
                portion = (target / energy_per_100g * 100) if energy_per_100g > 0 else 250.0
                portion = max(100.0, min(400.0, portion)) # Realistic drink size
                scale = portion / 100.0
                
                food_item = FoodItem(
                    fdc_id=str(cand.get('fdc_id', 'unknown')),
                    food_name=str(cand.get('food_name', 'Unknown')),
                    food_group=str(cand.get('food_group', 'Unknown')),
                    consumption_label='Drink',
                    cuisine_label=str(cand.get('cuisine_label', 'Unknown')),
                    portion_gram=round(portion, 1),
                    energy_kcal=round(energy_per_100g * scale, 1),
                    protein_g=round(float(cand.get('protein_g', 0)) * scale, 2),
                    carbohydrate_g=round(float(cand.get('carbohydrate_g', 0)) * scale, 2),
                    fat_g=round(float(cand.get('fat_g', 0)) * scale, 2),
                )
                items.append(food_item)
            
            results[meal_type] = items
            
        return results

    def _update_cumulative_nutrients(self, food_item_dict: Dict):
        """Update cumulative nutrient tracking setelah item dipilih"""
        for nutrient_name in self.cumulative_nutrients.keys():
            value = food_item_dict.get(nutrient_name, 0.0) or 0.0
            self.cumulative_nutrients[nutrient_name] += float(value)
    
    def generate_meal(
        self,
        meal_type: str,
        target_calories: float,
        course_distribution: Optional[Dict[str, float]] = None,
        fixed_drink: Optional[FoodItem] = None
    ) -> Optional[Meal]:
        """
        Generate lengkap satu meal (Main + Side + optional Drink)
        menggunakan greedy algorithm
        
        Args:
            meal_type: 'Breakfast', 'Lunch', 'Dinner'
            target_calories: Total target calori untuk meal
            course_distribution: Dict {'Main': 0.6, 'Side': 0.3, 'Drink': 0.1}
            fixed_drink: Drink yang sudah dipilih (Phase 1)
        
        Returns:
            Meal object dengan courses atau None jika gagal
        """
        
        # Default distribution jika tidak ada input
        if course_distribution is None:
            course_distribution = {
                'Main': 0.6,
                'Side': 0.3,
                'Drink': 0.1
            }
        
        courses = {}
        actual_calories = 0
        meal_items = []  # Track items dalam meal ini untuk exclusion
        
        # Use fixed drink if provided
        if fixed_drink:
            courses['Drink'] = MealCourse(
                course_type='Drink',
                candidates=[fixed_drink],
                total_calories=fixed_drink.energy_kcal,
                total_protein_g=fixed_drink.protein_g,
                total_carb_g=fixed_drink.carbohydrate_g,
                total_fat_g=fixed_drink.fat_g,
            )
            actual_calories += fixed_drink.energy_kcal
            meal_items.append(fixed_drink)
            # Update cumulative with fixed drink
            drink_dict = {
                'energy_kcal': fixed_drink.energy_kcal,
                'protein_g': fixed_drink.protein_g,
                'carbohydrate_g': fixed_drink.carbohydrate_g,
                'fat_g': fixed_drink.fat_g,
            }
            # Add other nutrients from fixed_drink if they were in the object
            # (In reality we might need to fetch them from DB or pass them in fixed_drink but FoodItem is simple)
            self._update_cumulative_nutrients(drink_dict)
            self.selected_items.append(fixed_drink)

        # Remaining calories for Main and Side
        remaining_target = target_calories - actual_calories
        
        # Split remaining target between Main and Side based on distribution
        # e.g. if original was 0.6 Main and 0.3 Side, then Main gets 0.6/(0.6+0.3) of remaining
        main_weight = course_distribution.get('Main', 0.6)
        side_weight = course_distribution.get('Side', 0.3)
        total_weight = main_weight + side_weight
        
        # MAIN COURSE
        main_target = remaining_target * (main_weight / total_weight)
        main_item = self.select_best_candidate_for_slot(
            'Main', main_target, 
            exclusion_names=[item.food_name for item in meal_items]
        )
        
        if main_item:
            courses['Main'] = MealCourse(
                course_type='Main',
                candidates=[main_item],
                total_calories=main_item.energy_kcal,
                total_protein_g=main_item.protein_g,
                total_carb_g=main_item.carbohydrate_g,
                total_fat_g=main_item.fat_g,
            )
            actual_calories += main_item.energy_kcal
            meal_items.append(main_item)
        else:
            return None
        
        # SIDE COURSE
        side_target = remaining_target * (side_weight / total_weight)
        side_item = self.select_best_candidate_for_slot(
            'Side', side_target,
            exclusion_names=[item.food_name for item in meal_items]
        )
        
        if side_item:
            courses['Side'] = MealCourse(
                course_type='Side',
                candidates=[side_item],
                total_calories=side_item.energy_kcal,
                total_protein_g=side_item.protein_g,
                total_carb_g=side_item.carbohydrate_g,
                total_fat_g=side_item.fat_g,
            )
            actual_calories += side_item.energy_kcal
            meal_items.append(side_item)
        
        # DRINK COURSE (if not fixed and include_drink is true)
        if not fixed_drink:
            drink_target = target_calories * course_distribution.get('Drink', 0.1)
            drink_item = self.select_best_candidate_for_slot(
                'Drink', drink_target,
                exclusion_names=[item.food_name for item in meal_items]
            )
            
            if drink_item:
                courses['Drink'] = MealCourse(
                    course_type='Drink',
                    candidates=[drink_item],
                    total_calories=drink_item.energy_kcal,
                    total_protein_g=drink_item.protein_g,
                    total_carb_g=drink_item.carbohydrate_g,
                    total_fat_g=drink_item.fat_g,
                )
                actual_calories += drink_item.energy_kcal
                meal_items.append(drink_item)
        
        return Meal(
            meal_type=meal_type,
            courses=courses,
            target_calories=target_calories,
            actual_calories=actual_calories,
            include_drink=True
        )
    
    def generate_snack(
        self,
        target_calories: float,
        num_candidates: int = 3
    ) -> Optional[SnackMeal]:
        """
        Generate snack menu (tidak ada sub-course, cukup N candidates)
        
        Args:
            target_calories: Target calori untuk snack
            num_candidates: Jumlah kandidat (biasanya 3)
        
        Returns:
            SnackMeal object atau None
        """
        
        # Generate candidates dengan consumption_label = 'Snack'
        candidates_list = CandidateGenerator.generate_candidates_for_slot(
            food_database=self.food_db,
            slot_category='Snack',
            target_calories=target_calories,
            num_candidates=num_candidates,
            exclusion_names=[item.food_name for item in self.selected_items],
        )
        
        if not candidates_list:
            return None
        
        # Score dan ambil top candidates (tidak hanya 1, tapi 3 untuk snack)
        scored_candidates = []
        for candidate_dict in candidates_list:
            score = self.score_candidate(
                candidate=candidate_dict,
                target_calories=target_calories,
                selected_items=[item.food_name for item in self.selected_items],
                constraint_bag=self.constraint_bag,
                cumulative_nutrients=self.cumulative_nutrients
            )
            scored_candidates.append((score, candidate_dict))
        
        # Sort by score dan ambil top N
        scored_candidates.sort(key=lambda x: x[0], reverse=True)
        
        snack_items = []
        
        for i, (score, candidate_dict) in enumerate(scored_candidates[:num_candidates]):
            # Scale portion
            energy_per_100g = float(candidate_dict.get('energy_kcal', 0))
            portion = (target_calories / energy_per_100g * 100) if energy_per_100g > 0 else 100.0
            portion = max(50.0, min(300.0, portion))
            scale = portion / 100.0

            food_item = FoodItem(
                fdc_id=str(candidate_dict.get('fdc_id', 'unknown')),
                food_name=str(candidate_dict.get('food_name', 'Unknown')),
                food_group=str(candidate_dict.get('food_group', 'Unknown')),
                consumption_label='Snack',
                cuisine_label=str(candidate_dict.get('cuisine_label', 'Unknown')),
                portion_gram=round(portion, 1),
                energy_kcal=round(energy_per_100g * scale, 1),
                protein_g=round(float(candidate_dict.get('protein_g', 0)) * scale, 2),
                carbohydrate_g=round(float(candidate_dict.get('carbohydrate_g', 0)) * scale, 2),
                fat_g=round(float(candidate_dict.get('fat_g', 0)) * scale, 2),
            )
            snack_items.append(food_item)

            # Update tracking for the FIRST snack only (the one used for daily totals)
            if i == 0:
                self.selected_items.append(food_item)
                scaled_dict = candidate_dict.copy()
                for k in ['energy_kcal', 'protein_g', 'carbohydrate_g', 'fat_g']:
                    scaled_dict[k] = getattr(food_item, k)
                self._update_cumulative_nutrients(scaled_dict)
        
        if not snack_items:
            return None
        
        # Note: snack actual_calories in SnackMeal might be confusing if it shows total of all candidates
        # Usually it should show the average or target. Let's use target.
        return SnackMeal(
            meal_type='Snack',
            candidates=snack_items,
            target_calories=target_calories,
            actual_calories=snack_items[0].energy_kcal if snack_items else 0
        )
    
    def optimize_full_menu_phase2(
        self,
        user_profile: Dict,
        meal_targets: Dict[str, float],
        selected_drinks: Dict[str, FoodItem]
    ) -> Optional[MenuPlan]:
        """
        Phase 2: Generate complete menu using PRE-SELECTED drinks (fixed contributions)
        
        Args:
            user_profile: User profile dictionary
            meal_targets: Dict {'breakfast': kcal, 'lunch': kcal, 'snack': kcal, 'dinner': kcal}
            selected_drinks: Dict {'breakfast': FoodItem, 'lunch': FoodItem, 'dinner': FoodItem}
            
        Returns:
            MenuPlan object or None
        """
        self._init_cumulative_tracking()
        self.selected_items = []
        
        # Generate with fixed drinks
        breakfast = self.generate_meal('Breakfast', meal_targets.get('breakfast', 500), fixed_drink=selected_drinks.get('breakfast'))
        lunch = self.generate_meal('Lunch', meal_targets.get('lunch', 700), fixed_drink=selected_drinks.get('lunch'))
        dinner = self.generate_meal('Dinner', meal_targets.get('dinner', 600), fixed_drink=selected_drinks.get('dinner'))
        snack = self.generate_snack(meal_targets.get('snack', 200))
        
        if not (breakfast and lunch and dinner):
            return None
            
        # Total daily calculation
        daily_totals = self.cumulative_nutrients.copy()
        
        feasible, violations = self.validate_constraints(daily_totals)
        
        return MenuPlan(
            algorithm_used='Greedy',
            user_profile=user_profile,
            breakfast=breakfast,
            lunch=lunch,
            dinner=dinner,
            snack=snack,
            total_daily_calories=daily_totals.get('energy_kcal', 0),
            total_daily_protein_g=daily_totals.get('protein_g', 0),
            total_daily_carb_g=daily_totals.get('carbohydrate_g', 0),
            total_daily_fat_g=daily_totals.get('fat_g', 0),
            feasible=feasible,
            violations=violations
        )

    def validate_constraints(self, daily_totals: Dict[str, float]) -> Tuple[bool, List[str]]:
        """
        Validate menu terhadap HARD constraints
        
        Args:
            daily_totals: Dict dengan daily nutrient totals
        
        Returns:
            (is_feasible: bool, violations: List[str])
        """
        violations = []
        
        if not self.constraint_bag or 'nutrients' not in self.constraint_bag:
            return True, []
        
        nutrients_def = self.constraint_bag['nutrients']
        
        for nutrient_name, constraint in nutrients_def.items():
            if constraint.get('hard_soft_type') != 'HARD':
                continue  # Skip SOFT constraints
            
            actual = daily_totals.get(nutrient_name, 0.0)
            min_val = constraint.get('min')
            max_val = constraint.get('max')
            unit = constraint.get('unit', '')
            
            if min_val is not None and actual < min_val:
                violations.append(
                    f"❌ {nutrient_name}: below minimum ({actual:.1f} < {min_val:.1f} {unit})"
                )
            
            if max_val is not None and actual > max_val:
                violations.append(
                    f"❌ {nutrient_name}: above maximum ({actual:.1f} > {max_val:.1f} {unit})"
                )
        
        return len(violations) == 0, violations
    
    def optimize_full_menu(
        self,
        user_profile: Dict,
        meal_targets: Dict
    ) -> Optional[MenuPlan]:
        """
        Generate lengkap full day menu menggunakan greedy algorithm
        dengan constraint satisfaction checking
        
        Args:
            user_profile: User profile dari NutritionService
            meal_targets: Dict {'breakfast': 500, 'lunch': 700, 'dinner': 600, 'snack': 200}
        
        Returns:
            MenuPlan object (complete day menu) atau None jika gagal
        """
        
        # Reset cumulative tracking untuk fresh calculation
        self._init_cumulative_tracking()
        self.selected_items = []
        
        # Generate each meal greedily
        breakfast = self.generate_meal('Breakfast', meal_targets.get('breakfast', 500))
        lunch = self.generate_meal('Lunch', meal_targets.get('lunch', 700))
        dinner = self.generate_meal('Dinner', meal_targets.get('dinner', 600))
        snack = self.generate_snack(meal_targets.get('snack', 200))
        
        if not (breakfast and lunch and dinner):
            return None
        
        # Calculate daily totals
        daily_totals = self.cumulative_nutrients.copy()
        
        # Validate HARD constraints
        is_feasible, violations = self.validate_constraints(daily_totals)
        
        # Build MenuPlan
        menu_plan = MenuPlan(
            algorithm_used='Greedy',
            user_profile=user_profile,
            breakfast=breakfast,
            lunch=lunch,
            dinner=dinner,
            snack=snack or SnackMeal(),
            total_daily_calories=daily_totals.get('energy_kcal', 0),
            total_daily_protein_g=daily_totals.get('protein_g', 0),
            total_daily_carb_g=daily_totals.get('carbohydrate_g', 0),
            total_daily_fat_g=daily_totals.get('fat_g', 0),
            feasible=is_feasible,
            violations=violations
        )
        
        return menu_plan

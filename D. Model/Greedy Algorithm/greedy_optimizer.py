"""
Greedy Algorithm untuk Meal Planning Optimization
Menggunakan locally optimal choice pada setiap slot untuk mendapatkan menu yang berkualitas

Mekanisme:
1. Untuk setiap meal slot (breakfast main, lunch side, etc)
2. Generate candidates dengan similarity check (ingredient diversity)
3. Score setiap candidate berdasarkan:
   - Calorie match to target (minimize error)
   - Nutrient satisfaction (constraint fulfillment)
   - Food diversity (no repeated main ingredient in same meal time)
4. Pilih candidate dengan score tertinggi (greedy step)
5. Update exclusion list untuk slot berikutnya
6. Return complete MenuPlan

Output: MenuPlan (same contract as Genetic Algorithm)
"""

import pandas as pd
import math
from typing import List, Dict, Tuple, Optional
from meal_schema import FoodItem, MealCourse, Meal, SnackMeal, MenuPlan
from candidate_generator import CandidateGenerator
from similarity_checker import SimilarityChecker


class GreedyOptimizer:
    """Greedy Algorithm untuk generate optimal meal plan"""
    
    def __init__(self, food_database: pd.DataFrame, nutrition_guidelines: Dict):
        """
        Initialize Greedy Optimizer
        
        Args:
            food_database: DataFrame dengan food items (dari NutritionService)
            nutrition_guidelines: Dict dengan nutrient constraints (dari NutritionService)
        """
        self.food_db = food_database.copy()
        self.guidelines = nutrition_guidelines
        self.similarity_checker = SimilarityChecker()
        self.selected_items = []  # Track semua yang sudah dipilih
    
    @staticmethod
    def score_candidate(
        candidate: Dict,
        target_calories: float,
        selected_items: List[str],
        weight_calorie: float = 0.6,
        weight_nutrient: float = 0.3,
        weight_diversity: float = 0.1
    ) -> float:
        """
        Score satu candidate berdasarkan multiple factors
        
        Args:
            candidate: Dict food item dengan nutritional info
            target_calories: Target calori untuk slot
            selected_items: List food names yang sudah dipilih (untuk diversity check)
            weight_calorie: Bobot calorie match (default 0.6)
            weight_nutrient: Bobot nutrient satisfaction (default 0.3)
            weight_diversity: Bobot ingredient diversity (default 0.1)
        
        Returns:
            Score dari 0-100 (higher is better)
        """
        
        scores = {}
        
        # 1. CALORIE MATCH SCORE (best when close to target)
        # Ideal: 0% error, Acceptable: ±20%, Bad: >30% error
        calorie_error = abs(candidate['energy_kcal'] - target_calories) / target_calories
        if calorie_error <= 0.1:
            scores['calorie'] = 100
        elif calorie_error <= 0.2:
            scores['calorie'] = 80
        elif calorie_error <= 0.3:
            scores['calorie'] = 50
        else:
            scores['calorie'] = max(0, 100 - (calorie_error * 200))  # Gradual penalty
        
        # 2. INGREDIENT DIVERSITY SCORE
        # 100 if completely new, 0 if similar main ingredient already used
        has_repeated_ingredient = False
        for selected_name in selected_items:
            # Check similarity menggunakan SimilarityChecker
            similarity = SimilarityChecker.calculate_similarity_score(candidate['food_name'], selected_name)
            # Threshold: jika similarity > 0.7, anggap sama ingredient
            if similarity > 0.7:
                has_repeated_ingredient = True
                break
        
        scores['diversity'] = 0 if has_repeated_ingredient else 100
        
        # 3. NUTRIENT SATISFACTION SCORE (simplified)
        # Check if macros (protein, carb, fat) reasonable for a single item
        protein_ok = 0 < candidate.get('protein_g', 0) <= 50  # reasonable portion
        carb_ok = 0 <= candidate.get('carbohydrate_g', 0) <= 100
        fat_ok = 0 <= candidate.get('fat_g', 0) <= 35
        
        macro_score = sum([protein_ok, carb_ok, fat_ok]) / 3 * 100
        scores['nutrient'] = macro_score
        
        # WEIGHTED SCORE
        final_score = (
            scores['calorie'] * weight_calorie +
            scores['nutrient'] * weight_nutrient +
            scores['diversity'] * weight_diversity
        )
        
        return final_score
    
    def select_best_candidate_for_slot(
        self,
        slot_category: str,  # 'Main', 'Side', 'Drink'
        target_calories: float,
        num_candidates: int = 3
    ) -> Optional[FoodItem]:
        """
        Greedy step: Select single best candidate untuk satu slot
        
        Args:
            slot_category: 'Main', 'Side', 'Drink'
            target_calories: Target calori untuk slot
            num_candidates: Generate N candidates, pick best
        
        Returns:
            FoodItem object (best scored candidate)
        """
        
        # Generate candidates dengan diversity check
        candidates_list = CandidateGenerator.generate_candidates_for_slot(
            food_database=self.food_db,
            slot_category=slot_category,
            target_calories=target_calories,
            num_candidates=num_candidates,
            exclusion_names=[item.food_name for item in self.selected_items],
        )
        
        if not candidates_list:
            return None
        
        # Score setiap candidate
        best_score = -1
        best_candidate = None
        
        for candidate_dict in candidates_list:
            score = self.score_candidate(
                candidate=candidate_dict,
                target_calories=target_calories,
                selected_items=[item.food_name for item in self.selected_items]
            )
            
            if score > best_score:
                best_score = score
                best_candidate = candidate_dict
        
        # Convert dict to FoodItem
        if best_candidate:
            food_item = FoodItem(
                fdc_id=best_candidate['fdc_id'],
                food_name=best_candidate['food_name'],
                food_group=best_candidate['food_group'],
                consumption_label=best_candidate['consumption_label'],
                cuisine_label=best_candidate['cuisine_label'],
                portion_gram=100,  # Default 100g (bisa di-adjust)
                energy_kcal=float(best_candidate['energy_kcal']),
                protein_g=float(best_candidate.get('protein_g', 0)),
                carbohydrate_g=float(best_candidate.get('carbohydrate_g', 0)),
                fat_g=float(best_candidate.get('fat_g', 0)),
            )
            
            # Track untuk diversity check nanti
            self.selected_items.append(food_item)
            
            return food_item
        
        return None
    
    def generate_meal(
        self,
        meal_type: str,  # 'Breakfast', 'Lunch', 'Dinner'
        target_calories: float,
        num_courses: int = 3,
        include_drink: bool = True
    ) -> Optional[Meal]:
        """
        Generate lengkap satu meal (Main + Side + optional Drink)
        menggunakan greedy algorithm
        
        Args:
            meal_type: 'Breakfast', 'Lunch', 'Dinner'
            target_calories: Total target calori untuk meal
            num_courses: Jumlah course (biasanya 3: Main, Side, Drink)
            include_drink: Include drink course?
        
        Returns:
            Meal object dengan courses
        """
        
        courses = {}
        actual_calories = 0
        
        # MAIN COURSE (40% dari target calori)
        main_target = target_calories * 0.4
        main_item = self.select_best_candidate_for_slot('Main', main_target)
        
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
        else:
            # Fallback jika ga ada main
            return None
        
        # SIDE COURSE (30% dari target)
        side_target = target_calories * 0.3
        side_item = self.select_best_candidate_for_slot('Side', side_target)
        
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
        
        # DRINK COURSE (optional, 20% dari target)
        if include_drink:
            drink_target = target_calories * 0.2
            drink_item = self.select_best_candidate_for_slot('Drink', drink_target)
            
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
        
        return Meal(
            meal_type=meal_type,
            courses=courses,
            target_calories=target_calories,
            actual_calories=actual_calories,
            include_drink=include_drink and 'Drink' in courses
        )
    
    def optimize_full_menu(
        self,
        user_profile: Dict,
        meal_targets: Dict  # {'breakfast': 500, 'lunch': 700, 'dinner': 600, 'snack': 200}
    ) -> Optional[MenuPlan]:
        """
        Generate lengkap full day menu menggunakan greedy algorithm
        
        Args:
            user_profile: User profile dari NutritionService
            meal_targets: Target calori untuk setiap meal
        
        Returns:
            MenuPlan object (complete day menu)
        """
        
        # Reset selected items untuk fresh calculation
        self.selected_items = []
        
        # Generate each meal greedily
        breakfast = self.generate_meal('Breakfast', meal_targets.get('breakfast', 500))
        lunch = self.generate_meal('Lunch', meal_targets.get('lunch', 700))
        dinner = self.generate_meal('Dinner', meal_targets.get('dinner', 600))
        snack = self.generate_snack(meal_targets.get('snack', 200))
        
        if not (breakfast and lunch and dinner):
            return None  # Fail jika tidak bisa generate major meals
        
        # Build MenuPlan
        menu_plan = MenuPlan(
            algorithm_used='Greedy',
            user_profile=user_profile,
            breakfast=breakfast,
            lunch=lunch,
            dinner=dinner,
            snack=snack,
            total_calories=sum([
                breakfast.actual_calories if breakfast else 0,
                lunch.actual_calories if lunch else 0,
                dinner.actual_calories if dinner else 0,
                snack.actual_calories if snack else 0,
            ])
        )
        
        return menu_plan
    
    def generate_snack(self, target_calories: float) -> Optional[SnackMeal]:
        """
        Generate snack meal (only 3 candidates, no sub-courses)
        
        Args:
            target_calories: Target calori untuk snack
        
        Returns:
            SnackMeal object
        """
        
        candidates_list = CandidateGenerator.generate_candidates_for_slot(
            food_database=self.food_db,
            slot_category='Snack' if 'Snack' in self.food_db.get('menu_category', pd.Series()).values else 'Side',
            target_calories=target_calories,
            num_candidates=3,
            exclusion_names=[item.food_name for item in self.selected_items],
        )
        
        if not candidates_list:
            return None
        
        # Score dan select best
        best_score = -1
        best_candidate = None
        
        for candidate_dict in candidates_list:
            score = self.score_candidate(
                candidate=candidate_dict,
                target_calories=target_calories,
                selected_items=[item.food_name for item in self.selected_items]
            )
            
            if score > best_score:
                best_score = score
                best_candidate = candidate_dict
        
        if best_candidate:
            snack_item = FoodItem(
                fdc_id=best_candidate['fdc_id'],
                food_name=best_candidate['food_name'],
                food_group=best_candidate['food_group'],
                consumption_label='Snack',
                cuisine_label=best_candidate['cuisine_label'],
                portion_gram=100,
                energy_kcal=float(best_candidate['energy_kcal']),
                protein_g=float(best_candidate.get('protein_g', 0)),
                carbohydrate_g=float(best_candidate.get('carbohydrate_g', 0)),
                fat_g=float(best_candidate.get('fat_g', 0)),
            )
            
            self.selected_items.append(snack_item)
            
            return SnackMeal(
                candidates=[snack_item],
                target_calories=target_calories,
                actual_calories=snack_item.energy_kcal,
            )
        
        return None


# TEST & EXAMPLE
if __name__ == "__main__":
    print("✓ Greedy Algorithm module loaded successfully")
    print("✓ Ready to be imported by main system")

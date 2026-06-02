import pandas as pd
import math
from typing import List, Dict, Tuple, Optional, Set
import sys
import os

# Adds D. Model to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from meal_schema import FoodItem, MealCourse, Meal, SnackMeal, MenuPlan
from candidate_generator import CandidateGenerator
from similarity_checker import SimilarityChecker

PORTION_RANGE = {
    'Main Course': (150, 400),
    'Side Dish': (50, 250),
    'Drink': (150, 300),
    'Snack': (30, 100)
}

class GreedyOptimizer:
    """Greedy Algorithm untuk generate optimal meal plan dengan constraint-aware scoring"""
    
    def __init__(self, food_database: pd.DataFrame, constraint_bag: Dict):
        self.food_db = food_database.copy()
        self.constraint_bag = constraint_bag
        self.similarity_checker = SimilarityChecker()
        self.selected_items = []  
        self.cumulative_nutrients = {}
        self._init_cumulative_tracking()
    
    def _init_cumulative_tracking(self):
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
        self.food_db = food_database.copy()
        self.constraint_bag = constraint_bag
        self.similarity_checker = SimilarityChecker()
        self.selected_items = []
        self._init_cumulative_tracking()
        
    def score_candidate(
        self,
        candidate: Dict,
        target_calories: float,
        selected_items_names: List[str]
    ) -> float:
        # Score calculation
        target_calories = max(target_calories, 1)
        energy = candidate.get('energy_kcal', 0)
        calorie_error = abs(energy - target_calories) / target_calories
        
        calorie_score = 100
        if calorie_error > 0.1:
            calorie_score = max(0, 100 - (calorie_error * 100))
            
        # Diversity score
        diversity_score = 100
        for selected_name in selected_items_names:
            sim = SimilarityChecker.calculate_similarity_score(str(candidate.get('food_name', '')), selected_name)
            if sim > 0.7:
                diversity_score = 0
                break
                
        return (calorie_score * 0.7) + (diversity_score * 0.3)

    def _scale_nutrients(self, candidate_dict: Dict, portion_gram: float) -> FoodItem:
        if portion_gram <= 0:
            portion_gram = 100.0
        
        scale = portion_gram / 100.0
        
        food_item = FoodItem(
            fdc_id=str(candidate_dict.get('fdc_id', 'unknown')),
            food_name=str(candidate_dict.get('food_name', 'Unknown')),
            food_group=str(candidate_dict.get('food_group', 'Unknown')),
            consumption_label=str(candidate_dict.get('consumption_label', 'Unknown')),
            cuisine_label=str(candidate_dict.get('cuisine_label', 'Unknown')),
            portion_gram=round(portion_gram, 1),
            energy_kcal=round(float(candidate_dict.get('energy_kcal', 0)) * scale, 1),
            protein_g=round(float(candidate_dict.get('protein_g', 0)) * scale, 2),
            carbohydrate_g=round(float(candidate_dict.get('carbohydrate_g', 0)) * scale, 2),
            fat_g=round(float(candidate_dict.get('fat_g', 0)) * scale, 2),
        )
        return food_item

    def generate_candidates_for_course(
        self,
        course_type: str, 
        target_calories: float,
        current_meal_excluded: List[str]
    ) -> List[FoodItem]:
        label_map = {
            'Main': 'Main Course',
            'Side': 'Side Dish',
            'Drink': 'Drink',
            'Snack': 'Snack'
        }
        actual_label = label_map.get(course_type, 'Main Course')
        
        global_excluded = [item.food_name for item in self.selected_items] + current_meal_excluded
        
        raw_candidates = CandidateGenerator.generate_candidates_for_slot(
            food_database=self.food_db,
            slot_category=actual_label,
            target_calories=target_calories,  
            num_candidates=10, 
            exclusion_names=global_excluded,
        )
        
        if not raw_candidates:
            return []
            
        scored = []
        for cand in raw_candidates:
            score = self.score_candidate(cand, target_calories, global_excluded)
            scored.append((score, cand))
            
        scored.sort(key=lambda x: x[0], reverse=True)
        
        final_items = []
        added_names = []
        
        min_p, max_p = PORTION_RANGE.get(actual_label, (50, 400))
        
        for score, cand in scored:
            is_dup = False
            for ans in added_names:
                if SimilarityChecker.calculate_similarity_score(str(cand.get('food_name','')), ans) > 0.5:
                    is_dup = True
                    break
            if is_dup:
                continue
                
            energy_100g = float(cand.get('energy_kcal', 0))
            if energy_100g > 0:
                portion = (target_calories / energy_100g) * 100.0
            else:
                portion = max_p
                
            portion = max(min_p, min(max_p, portion))
            
            food_item = self._scale_nutrients(cand, portion)
            final_items.append(food_item)
            added_names.append(food_item.food_name)
            
            if len(final_items) >= 3:
                break
                
        return final_items

    def _update_cumulative(self, item: FoodItem):
        self.cumulative_nutrients['energy_kcal'] += item.energy_kcal
        self.cumulative_nutrients['protein_g'] += item.protein_g
        self.cumulative_nutrients['carbohydrate_g'] += item.carbohydrate_g
        self.cumulative_nutrients['fat_g'] += item.fat_g
        self.selected_items.append(item)

    def generate_meal(self, meal_type: str, target_calories: float) -> Meal:
        main_target = target_calories * 0.50
        side_target = target_calories * 0.30
        drink_target = target_calories * 0.20
        
        courses = {}
        actual = 0
        current_excluded = []
        
        mains = self.generate_candidates_for_course('Main', main_target, current_excluded)
        if mains:
            courses['Main'] = MealCourse(
                course_type='Main', candidates=mains,
                total_calories=mains[0].energy_kcal, total_protein_g=mains[0].protein_g,
                total_carb_g=mains[0].carbohydrate_g, total_fat_g=mains[0].fat_g
            )
            actual += mains[0].energy_kcal
            self._update_cumulative(mains[0])
            current_excluded.append(mains[0].food_name)
            
        sides = self.generate_candidates_for_course('Side', side_target, current_excluded)
        if sides:
            courses['Side'] = MealCourse(
                course_type='Side', candidates=sides,
                total_calories=sides[0].energy_kcal, total_protein_g=sides[0].protein_g,
                total_carb_g=sides[0].carbohydrate_g, total_fat_g=sides[0].fat_g
            )
            actual += sides[0].energy_kcal
            self._update_cumulative(sides[0])
            current_excluded.append(sides[0].food_name)

        drinks = self.generate_candidates_for_course('Drink', drink_target, current_excluded)
        if drinks:
            courses['Drink'] = MealCourse(
                course_type='Drink', candidates=drinks,
                total_calories=drinks[0].energy_kcal, total_protein_g=drinks[0].protein_g,
                total_carb_g=drinks[0].carbohydrate_g, total_fat_g=drinks[0].fat_g
            )
            actual += drinks[0].energy_kcal
            self._update_cumulative(drinks[0])
            current_excluded.append(drinks[0].food_name)
            
        return Meal(
            meal_type=meal_type, courses=courses,
            target_calories=target_calories, actual_calories=actual, include_drink=True
        )

    def generate_menu(self, user_profile: Dict, meal_targets: Dict[str, float]) -> MenuPlan:
        self._init_cumulative_tracking()
        self.selected_items = []
        
        b = self.generate_meal('Breakfast', meal_targets.get('breakfast', 500))
        l = self.generate_meal('Lunch', meal_targets.get('lunch', 700))
        d = self.generate_meal('Dinner', meal_targets.get('dinner', 500))
        
        snacks = self.generate_candidates_for_course('Snack', meal_targets.get('snack', 200), [])
        s = SnackMeal(meal_type='Snack', candidates=snacks, target_calories=meal_targets.get('snack', 200), actual_calories=snacks[0].energy_kcal if snacks else 0)
        if snacks:
            self._update_cumulative(snacks[0])
            
        feasible = True
        return MenuPlan(
            algorithm_used='Greedy', user_profile=user_profile,
            breakfast=b, lunch=l, dinner=d, snack=s,
            total_daily_calories=self.cumulative_nutrients['energy_kcal'],
            total_daily_protein_g=self.cumulative_nutrients['protein_g'],
            total_daily_carb_g=self.cumulative_nutrients['carbohydrate_g'],
            total_daily_fat_g=self.cumulative_nutrients['fat_g'],
            feasible=feasible, violations=[]
        )
import sys
import os
import pandas as pd
from typing import Dict, List, Any, Optional

current_dir = os.path.dirname(__file__)
if current_dir not in sys.path:
    sys.path.append(current_dir)
    
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from meal_schema import MenuPlan, Meal, MealCourse, SnackMeal, FoodItem
from ga_v1 import run_ga, calculate_portion_sizes_dynamic, validate_final_solution, generate_meal_options # type: ignore

class GeneticAlgorithmInterface:
    def __init__(self, food_database: pd.DataFrame, constraint_bag: Dict):
        """
        Initialize the GA interface with data from NutritionService
        """
        self.food_db = food_database
        self.constraint_bag = self._convert_to_ga_format(constraint_bag)
        print("[OK] Genetic Algorithm Interface initialized")
    
    def initialize(self, food_database: pd.DataFrame, constraint_bag: Dict):
        """Reinitialize with new data"""
        self.food_db = food_database
        self.constraint_bag = self._convert_to_ga_format(constraint_bag)
        print("[OK] Genetic Algorithm Interface reinitialized")
        
    def _convert_to_ga_format(self, constraint_bag: Dict) -> Dict:
        """Convert NutritionService flat format to GA hard/soft format"""
        nutrients = constraint_bag.get('nutrients', constraint_bag)
        
        hard = {}
        soft = {}
        
        for nutrient, constraint in nutrients.items():
            if not isinstance(constraint, dict):
                continue
            if constraint.get('constraint_type') == 'unlimited':
                continue
            
            # Skip nutrients not in food database
            if nutrient == 'fruits_and_vegies_g':
                continue
            
            min_val = constraint.get('min')
            min_val = min_val if min_val is not None else 0
            max_val = constraint.get('max')
            max_val = max_val if max_val is not None else float('inf')
            
            nutrient_data = {
                'min': min_val,
                'max': max_val,
                'unit': constraint.get('unit', ''),
            }
            
            if constraint.get('hard_soft_type') == 'HARD':
                hard[nutrient] = nutrient_data
            else:
                soft[nutrient] = nutrient_data
        
        return {'hard': hard, 'soft': soft}
        
    def _create_food_item_from_row(self, row: pd.Series) -> FoodItem:
        """Helper to convert a GA output row into a FoodItem object"""
        micronutrients = {}
        for col in row.index:
            if col.startswith('final_') and col not in ['final_energy_kcal', 'final_protein_g', 'final_carbohydrate_g', 'final_fat_g']:
                micro_name = col.replace('final_', '')
                micronutrients[micro_name] = row[col]
                
        return FoodItem(
            fdc_id=str(row.get('fdc_id', '0')),
            food_name=row.get('food_name', 'Unknown'),
            food_group=row.get('food_group', 'Unknown'),
            consumption_label=row.get('consumption_label', 'Main Course'),
            cuisine_label=row.get('cuisine_label', 'Unknown'),
            portion_gram=row.get('gram', 100.0),
            energy_kcal=row.get('final_energy_kcal', 0.0),
            protein_g=row.get('final_protein_g', 0.0),
            carbohydrate_g=row.get('final_carbohydrate_g', 0.0),
            fat_g=row.get('final_fat_g', 0.0),
            micronutrients=micronutrients
        )

    def _get_3_candidates(
        self,
        primary_item: FoodItem,
        slot_key: str,
        slot_options: Optional[Dict]
    ) -> List[FoodItem]:
        candidates = [primary_item]
        
        if slot_options is None:
            return candidates
        
        options = slot_options.get(slot_key, [])
        
        for opt in options:
            if len(candidates) >= 3:
                break
            
            if not isinstance(opt, pd.Series):
                continue
            
            try:
                cand = self._create_food_item_from_row(opt)
                if cand.food_name != primary_item.food_name:
                    existing_names = [c.food_name for c in candidates]
                    if cand.food_name not in existing_names:
                        candidates.append(cand)
            except Exception:
                continue
        
        return candidates

    def _create_meal_from_rows(
        self,
        meal_type: str,
        main_row: pd.Series,
        side_row: pd.Series,
        drink_row: pd.Series,
        tdee: float = 0.0,
        slot_options: Optional[Dict] = None,
        meal_prefix: str = 'breakfast'
    ) -> Meal:
        main_item = self._create_food_item_from_row(main_row)
        side_item = self._create_food_item_from_row(side_row)
        drink_item = self._create_food_item_from_row(drink_row)
        
        main_candidates = self._get_3_candidates(main_item, f'{meal_prefix}_main', slot_options)
        side_candidates = self._get_3_candidates(side_item, f'{meal_prefix}_side', slot_options)
        drink_candidates = self._get_3_candidates(drink_item, f'{meal_prefix}_drink', slot_options)
        
        main_course = MealCourse(
            course_type='Main',
            candidates=main_candidates,
            total_calories=main_item.energy_kcal,
            total_protein_g=main_item.protein_g,
            total_carb_g=main_item.carbohydrate_g,
            total_fat_g=main_item.fat_g
        )
        
        side_course = MealCourse(
            course_type='Side',
            candidates=side_candidates,
            total_calories=side_item.energy_kcal,
            total_protein_g=side_item.protein_g,
            total_carb_g=side_item.carbohydrate_g,
            total_fat_g=side_item.fat_g
        )
        
        drink_course = MealCourse(
            course_type='Drink',
            candidates=drink_candidates,
            total_calories=drink_item.energy_kcal,
            total_protein_g=drink_item.protein_g,
            total_carb_g=drink_item.carbohydrate_g,
            total_fat_g=drink_item.fat_g
        )
        
        total_cal = main_item.energy_kcal + side_item.energy_kcal + drink_item.energy_kcal
        
        MEAL_DISTRIBUTION = {
            'Breakfast': 0.2375,
            'Lunch': 0.3375,
            'Dinner': 0.2875,
            'Snack': 0.1375,
        }
        target_calories = tdee * MEAL_DISTRIBUTION.get(meal_type, 0.25)
        
        return Meal(
            meal_type=meal_type,
            courses={'Main': main_course, 'Side': side_course, 'Drink': drink_course},
            target_calories=target_calories,
            actual_calories=total_cal,
            include_drink=True
        )

    def generate_menu_plan(self, user_profile: Dict, tdee: float) -> Optional[MenuPlan]:
        """
        Generate complete menu plan using Genetic Algorithm.
        """
        print("\n[GENERAT] Genetic Algorithm: Generating menu plan")
        print(f"   TDEE Target: {tdee:.0f} kcal")
        
        try:
            # 1. Run GA to find best 10 items
            best_solution, top_solutions = run_ga(
                food_df=self.food_db,
                guidelines=self.constraint_bag,
                tdee=tdee,
                generations=100,    # naik dari 20 → 100 untuk konvergensi lebih baik
                pop_size=50,        # naik dari 30 → 50 untuk diversity lebih baik
                elite_ratio=0.25,
                mutation_rate=0.3,
                verbose=False
            )
            
            if best_solution is None or len(best_solution) < 10:
                print("[ERROR] Genetic Algorithm failed to find a valid 10-item solution.")
                return None
                
            # Generate 3 options per slot
            slot_options = generate_meal_options(
                food_df=self.food_db,
                top_solutions=top_solutions,
                max_options_per_slot=3
            )
                
            # 2. Calculate dynamic portion sizes to match TDEE and limits
            portioned_df = calculate_portion_sizes_dynamic(
                selected_df=best_solution,
                TDEE=tdee,
                guidelines=self.constraint_bag
            )
            
            # 3. Construct the MenuPlan
            breakfast = self._create_meal_from_rows(
                'Breakfast',
                portioned_df.iloc[0],
                portioned_df.iloc[1],
                portioned_df.iloc[2],
                tdee=tdee,
                slot_options=slot_options,
                meal_prefix='breakfast'
            )
            lunch = self._create_meal_from_rows(
                'Lunch',
                portioned_df.iloc[3],
                portioned_df.iloc[4],
                portioned_df.iloc[5],
                tdee=tdee,
                slot_options=slot_options,
                meal_prefix='lunch'
            )
            dinner = self._create_meal_from_rows(
                'Dinner',
                portioned_df.iloc[6],
                portioned_df.iloc[7],
                portioned_df.iloc[8],
                tdee=tdee,
                slot_options=slot_options,
                meal_prefix='dinner'
            )
            
            snack_item = self._create_food_item_from_row(portioned_df.iloc[9])
            snack_candidates = self._get_3_candidates(
                snack_item,
                'snack',
                slot_options
            )
            
            snack = SnackMeal(
                meal_type='Snack',
                candidates=snack_candidates,
                target_calories=tdee * 0.1375,
                actual_calories=snack_item.energy_kcal
            )
            
            # Calculate daily totals
            total_cal = breakfast.actual_calories + lunch.actual_calories + dinner.actual_calories + snack.actual_calories
            
            total_protein = (sum([c.total_protein_g for c in breakfast.courses.values()]) + 
                            sum([c.total_protein_g for c in lunch.courses.values()]) + 
                            sum([c.total_protein_g for c in dinner.courses.values()]) + 
                            snack_item.protein_g)
                            
            total_carb = (sum([c.total_carb_g for c in breakfast.courses.values()]) + 
                         sum([c.total_carb_g for c in lunch.courses.values()]) + 
                         sum([c.total_carb_g for c in dinner.courses.values()]) + 
                         snack_item.carbohydrate_g)
                         
            total_fat = (sum([c.total_fat_g for c in breakfast.courses.values()]) + 
                        sum([c.total_fat_g for c in lunch.courses.values()]) + 
                        sum([c.total_fat_g for c in dinner.courses.values()]) + 
                        snack_item.fat_g)
                        
            daily_micronutrients = {}
            for col in portioned_df.columns:
                if col.startswith('final_') and col not in ['final_energy_kcal', 'final_protein_g', 'final_carbohydrate_g', 'final_fat_g']:
                    micro_name = col.replace('final_', '')
                    daily_micronutrients[micro_name] = round(float(portioned_df[col].sum()), 2)
            
            # 4. Check validation
            validation = validate_final_solution(portioned_df, self.constraint_bag, tdee=tdee)
            
            # Parse n_passed dan n_total dari summary string "Compliance: 58% (18/31)"
            import re
            _match = re.search(r'\((\d+)/(\d+)\)', validation.get('summary', ''))
            _n_passed = int(_match.group(1)) if _match else 0
            _n_total = int(_match.group(2)) if _match else 0
            
            menu_plan = MenuPlan(
                algorithm_used='Genetic',
                user_profile=user_profile,
                breakfast=breakfast,
                lunch=lunch,
                dinner=dinner,
                snack=snack,
                total_daily_calories=total_cal,
                total_daily_protein_g=total_protein,
                total_daily_carb_g=total_carb,
                total_daily_fat_g=total_fat,
                feasible=validation['is_valid'],
                violations=[f"{v[0]}: {v[4]}" for v in validation['violations']],
                compliance_rate=validation['compliance_rate'],
                n_constraints_passed=_n_passed,
                n_constraints_total=_n_total,
                daily_micronutrients=daily_micronutrients
            )
            
            print(f"[OK] Genetic Algorithm generated menu successfully")
            print(f"   Daily Total: {total_cal:.0f} kcal")
            print(f"   Validation: {validation['summary']}")
            return menu_plan
            
        except Exception as e:
            print(f"[ERROR] Genetic Algorithm error: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
            
    # Mocking Phase 1 for two-phase integration if needed
    def generate_drink_options(self, meal_distribution: Dict, user_tdee: float) -> Dict[str, List[Any]]:
        """
        Generate drink options. Since GA normally does everything at once, 
        we will use random selection from food_db for drinks here to satisfy the API shape.
        Or better, we just use a small random selection from drinks.
        """
        drinks_df = self.food_db[self.food_db['consumption_label'].str.contains('Drink', case=False, na=False)]
        if len(drinks_df) == 0:
            drinks_df = self.food_db.sample(min(15, len(self.food_db)))
            
        results = {}
        for meal in ['breakfast', 'lunch', 'dinner']:
            sample = drinks_df.sample(min(3, len(drinks_df)))
            # Convert to something with energy_kcal, protein_g, etc that API expects
            results[meal] = [pd.Series(row) for _, row in sample.iterrows()]
            
        return results
        
    def generate_menu_with_drinks(self, user_profile: Dict, meal_distribution: Dict, user_tdee: float, selected_drinks: Dict) -> Optional[MenuPlan]:
        """
        Ideally GA would fix the drink genes and optimize the rest.
        For V1, we just run the full generation ignoring the pre-selected drinks,
        or we generate the menu and replace the drinks.
        For simplicity, we'll just run generate_menu_plan and it will ignore the selected drinks.
        A better implementation would fix the chromosomes for drinks.
        """
        print("[INFO] GA currently ignores pre-selected drinks and generates full optimal plan.")
        return self.generate_menu_plan(user_profile, user_tdee)

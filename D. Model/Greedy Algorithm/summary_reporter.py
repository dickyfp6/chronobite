"""
SUMMARY REPORTER - Backend Testing Tool
Generate menu dan tampilkan Target vs Actual Achievement
"""

import sys
import os

# Setup paths
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '../..'))
os.chdir(project_root)

sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'C. System Flow'))
sys.path.insert(0, os.path.join(project_root, 'B. Preprocessing'))

# Import using importlib to handle folder names with spaces/dots
import importlib.util

# Load nutrition_service
spec = importlib.util.spec_from_file_location("nutrition_service",
    os.path.join(project_root, 'C. System Flow/nutrition_service.py'))
assert spec is not None, "Failed to load nutrition_service spec"
assert spec.loader is not None, "Failed to load nutrition_service loader"
nutrition_service_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nutrition_service_module)
NutritionService = nutrition_service_module.NutritionService

# Load greedy_interface
spec = importlib.util.spec_from_file_location("greedy_interface",
    os.path.join(project_root, 'D. Model/Greedy Algorithm/greedy_interface.py'))
assert spec is not None, "Failed to load greedy_interface spec"
assert spec.loader is not None, "Failed to load greedy_interface loader"
greedy_interface_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(greedy_interface_module)
GreedyAlgorithmInterface = greedy_interface_module.GreedyAlgorithmInterface


class SummaryReporter:
    """Generate menu dan tampilkan summary achievement"""
    
    def __init__(self):
        self.nutrition_service = None
        
    def generate_and_report(self, user_profile, disease_mode='normal'):
        """
        Generate menu dan return detailed summary
        """
        
        print("\n" + "="*80)
        print("MENU GENERATION & ACHIEVEMENT ANALYSIS")
        print("="*80)
        
        # Initialize
        print("\n[1/3] Loading NutritionService...")
        try:
            self.nutrition_service = NutritionService()
            print("[OK] Service loaded")
        except Exception as e:
            print(f"[ERROR] {e}")
            return None
        
        # Calculate nutrition needs
        print(f"\n[2/3] Calculating nutrition profile...")
        try:
            user_input = {
                'age': user_profile.get('age', 25),
                'gender': user_profile.get('gender', 'M'),
                'weight': user_profile.get('weight_kg', 70),
                'height': user_profile.get('height_cm', 175),
                'activity_factor': user_profile.get('activity_level', 1.6),
                'disease': disease_mode,
            }
            
            nutrition_result = self.nutrition_service.calculate_nutrition_needs(user_input)
            
            if not nutrition_result or not nutrition_result.get('success'):
                print(f"[ERROR] Calculation failed")
                return None
            
            nutrition_profile = nutrition_result
            print(f"[OK] TDEE: {nutrition_profile['energy']['tdee']:.0f} kcal | BMI: {nutrition_profile['anthropometrics']['bmi']:.2f}")
        except Exception as e:
            print(f"[ERROR] {e}")
            import traceback
            traceback.print_exc()
            return None
        
        # Generate menu
        print(f"\n[3/3] Generating menu with Greedy Algorithm...")
        try:
            greedy = GreedyAlgorithmInterface(
                self.nutrition_service.guideline_loader.food_df,
                nutrition_profile['guidelines']['nutrients']
            )
            
            menu_plan = greedy.generate_menu_plan(
                user_profile,
                nutrition_profile['energy']['tdee']
            )
            
            if not menu_plan:
                print("[ERROR] Menu generation failed")
                return None
            
            print("[OK] Menu generated")
        except Exception as e:
            print(f"[ERROR] {e}")
            import traceback
            traceback.print_exc()
            return None
        
        # Print report
        self._print_report(user_profile, nutrition_profile, menu_plan, disease_mode)
        
        return True
    
    def _print_report(self, user_profile, nutrition_profile, menu_plan, disease_mode):
        """Print detailed achievement report"""
        
        print("\n" + "="*80)
        print("USER PROFILE")
        print("="*80)
        print(f"Age: {user_profile['age']} | Gender: {user_profile['gender']} | " +
              f"Weight: {user_profile['weight_kg']}kg | Height: {user_profile['height_cm']}cm | " +
              f"Activity: {user_profile['activity_level']} | Disease: {disease_mode}")
        
        # Get targets from nutrition profile
        targets = nutrition_profile['guidelines']['nutrients']
        tdee = nutrition_profile['energy']['tdee']
        
        print("\n" + "="*80)
        print("NUTRITION ACHIEVEMENT - TARGET vs ACTUAL")
        print("="*80)
        print(f"{'Nutrient':<28} {'Target':>12} {'Actual':>12} {'Diff':>11} {'%':>8}")
        print("-" * 80)
        
        # Calculate actuals
        actuals = {
            'energy': menu_plan.total_daily_calories,
            'protein_g': menu_plan.total_daily_protein_g,
            'carbohydrate_g': menu_plan.total_daily_carb_g,
            'fat_g': menu_plan.total_daily_fat_g,
        }
        
        # Create achievement list - use underscore naming from targets
        nutrient_order = ['energy', 'protein_g', 'carbohydrate_g', 'fat_g']
        nutrient_display_names = {
            'energy': 'Energy (kcal)',
            'protein_g': 'Protein (g)',
            'carbohydrate_g': 'Carbohydrate (g)',
            'fat_g': 'Fat (g)',
        }
        
        achievements = []
        
        # Add energy manually (not in targets dict, TDEE is the target)
        energy_actual = actuals.get('energy', 0)
        energy_target = nutrition_profile['energy']['tdee']
        
        if energy_target > 0:
            energy_pct = (energy_actual / energy_target) * 100
        else:
            energy_pct = 100 if energy_actual == 0 else 0
        
        achievements.append({
            'nutrient': 'Energy (kcal)',
            'target': energy_target,
            'actual': energy_actual,
            'diff': energy_actual - energy_target,
            'pct': energy_pct
        })
        
        # Add macronutrients from targets
        for nutrient_key in ['protein_g', 'carbohydrate_g', 'fat_g']:
            if nutrient_key not in targets:
                continue
            
            target_info = targets[nutrient_key]
            # Use midpoint between min and max as target
            if isinstance(target_info, dict):
                target_val = (target_info.get('min', 0) + target_info.get('max', 0)) / 2
            else:
                target_val = target_info
            
            actual_val = actuals.get(nutrient_key, 0)
            
            if target_val > 0:
                achievement_pct = (actual_val / target_val) * 100
            else:
                achievement_pct = 100 if actual_val == 0 else 0
            
            achievements.append({
                'nutrient': nutrient_display_names.get(nutrient_key, nutrient_key),
                'target': target_val,
                'actual': actual_val,
                'diff': actual_val - target_val,
                'pct': achievement_pct
            })
        
        # Sort by achievement %
        achievements.sort(key=lambda x: x['pct'], reverse=True)
        
        # Print rows
        for item in achievements:
            nutrient_display = item['nutrient'][:27]
            target = item['target']
            actual = item['actual']
            diff = item['diff']
            pct = item['pct']
            
            # Status indicator
            if 95 <= pct <= 105:
                status = "OK"
            elif pct < 90:
                status = "LOW"
            elif pct > 110:
                status = "HIGH"
            else:
                status = "--"
            
            print(f"{nutrient_display:<28} {target:>12.1f} {actual:>12.1f} {diff:>+11.1f} {pct:>7.1f}% {status}")
        
        # Summary
        print("\n" + "="*80)
        print("MEAL BREAKDOWN")
        print("="*80)
        
        meals = [
            ('BREAKFAST', menu_plan.breakfast),
            ('LUNCH', menu_plan.lunch),
            ('DINNER', menu_plan.dinner),
            ('SNACK', menu_plan.snack),
        ]
        
        for meal_name, meal in meals:
            if not meal:
                continue
            
            # Collect ONLY selected items (first candidate per course) - BUG FIX
            all_items = []
            cal = 0
            protein = 0
            carbs = 0
            fat = 0
            
            # For regular meals (Breakfast, Lunch, Dinner) - access courses dict
            if hasattr(meal, 'courses') and isinstance(meal.courses, dict):
                for course_name, course in meal.courses.items():
                    if hasattr(course, 'candidates') and len(course.candidates) > 0:
                        # BUG FIX: Only take FIRST candidate (the selected one)
                        selected_item = course.candidates[0]
                        all_items.append(selected_item)
                        cal += selected_item.energy_kcal
                        protein += selected_item.protein_g
                        carbs += selected_item.carbohydrate_g
                        fat += selected_item.fat_g
            
            # For snack - access candidates directly
            elif hasattr(meal, 'candidates'):
                # BUG FIX: For snack, only the FIRST candidate is selected
                if meal.candidates and len(meal.candidates) > 0:
                    all_items = [meal.candidates[0]]
                    item = meal.candidates[0]
                    cal = item.energy_kcal
                    protein = item.protein_g
                    carbs = item.carbohydrate_g
                    fat = item.fat_g
            
            if not all_items:
                continue
            
            print(f"\n{meal_name}:")
            print(f"  Energy: {cal:>6.0f} kcal | Protein: {protein:>5.1f}g | Carbs: {carbs:>6.1f}g | Fat: {fat:>5.1f}g")
            print(f"  Items ({len(all_items)}):")
            
            for item in all_items:
                print(f"    - {item.food_name[:40]:<40} {item.portion_gram:>6.0f}g | {item.energy_kcal:>6.0f}kcal")
        
        # Overall assessment
        print("\n" + "="*80)
        print("OVERALL ACHIEVEMENT")
        print("="*80)
        
        avg_pct = sum([item['pct'] for item in achievements]) / len(achievements) if achievements else 0
        on_target = sum(1 for item in achievements if 95 <= item['pct'] <= 105)
        total = len(achievements)
        compliance = (on_target / total * 100) if total > 0 else 0
        
        print(f"Average Achievement: {avg_pct:.1f}%")
        print(f"Target Compliance: {on_target}/{total} nutrients in 95-105% range ({compliance:.1f}%)")
        
        # BUG FIX: Verdict based on TARGET COMPLIANCE, not average achievement
        if compliance >= 75:  # At least 3/4 nutrients within target
            verdict = "[SUCCESS] Menu achieves targets very well!"
        elif compliance >= 50:  # At least 2/4 nutrients within target
            verdict = "[WARNING] Menu partially achieves targets - some nutrients outside acceptable range"
        else:  # Less than 2/4 nutrients within target
            verdict = "[ERROR] Menu does not achieve targets adequately - major nutrient imbalances"
        
        print(f"\nVerdict: {verdict}")
        print("="*80 + "\n")


def main():
    reporter = SummaryReporter()
    
    # Test 1: Normal user
    print("\n\nTEST 1: 25y Male Normal Mode")
    user1 = {
        'age': 25,
        'gender': 'M',
        'weight_kg': 70,
        'height_cm': 175,
        'activity_level': 1.6,
    }
    reporter.generate_and_report(user1, 'normal')
    
    # Test 2: Female user
    print("\n\nTEST 2: 30y Female Normal Mode")
    user2 = {
        'age': 30,
        'gender': 'F',
        'weight_kg': 60,
        'height_cm': 165,
        'activity_level': 1.5,
    }
    reporter.generate_and_report(user2, 'normal')


if __name__ == '__main__':
    main()

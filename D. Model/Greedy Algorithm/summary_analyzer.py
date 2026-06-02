"""
SUMMARY ANALYZER - Menu Generation Results vs Target Analysis
Digunakan untuk backend testing: lihat berapa banyak targets tercapai
"""

import sys
import os
import pandas as pd
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Fix imports for correct folder names
import importlib.util

# Load nutrition_service
spec = importlib.util.spec_from_file_location("nutrition_service",
    os.path.abspath(os.path.join(os.path.dirname(__file__), '../../C. System Flow/nutrition_service.py')))
assert spec is not None, "Failed to load nutrition_service spec"
assert spec.loader is not None, "Failed to load nutrition_service loader"
nutrition_service_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nutrition_service_module)
NutritionService = nutrition_service_module.NutritionService

# Load greedy_interface
spec = importlib.util.spec_from_file_location("greedy_interface",
    os.path.abspath(os.path.join(os.path.dirname(__file__), './greedy_interface.py')))
assert spec is not None, "Failed to load greedy_interface spec"
assert spec.loader is not None, "Failed to load greedy_interface loader"
greedy_interface_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(greedy_interface_module)
GreedyAlgorithmInterface = greedy_interface_module.GreedyAlgorithmInterface


class SummaryAnalyzer:
    """Generate menu dan analyze achievement vs targets"""
    
    def __init__(self):
        self.nutrition_service = None
        
    def generate_and_analyze(self, user_profile, disease_mode='normal'):
        """
        Generate menu dan return detailed summary
        
        Args:
            user_profile: Dict dengan age, gender, weight (kg), height (cm), activity_level
            disease_mode: 'normal', 'ckd', 'diabetes', etc.
        
        Returns:
            Dict dengan semua target vs actual comparison
        """
        
        print("\n" + "="*80)
        print("MENU GENERATION & ACHIEVEMENT ANALYSIS")
        print("="*80)
        
        # Step 1: Initialize NutritionService
        print("\n[1/4] Loading data and constraints...")
        try:
            self.nutrition_service = NutritionService()
            print("[OK] NutritionService loaded")
        except Exception as e:
            print(f"[ERROR] Failed to load NutritionService: {e}")
            return None
        
        # Step 2: Set disease mode and calculate nutrition profile
        print(f"\n[2/4] Calculating nutrition profile (Disease: {disease_mode})...")
        try:
            user_input = {
                'age': user_profile.get('age', 25),
                'gender': user_profile.get('gender', 'M'),
                'weight': user_profile.get('weight_kg', 70),
                'height': user_profile.get('height_cm', 175),
                'activity_factor': user_profile.get('activity_level', 1.6),
                'disease': disease_mode,
            }
            nutrition_profile = self.nutrition_service.calculate_nutrition_needs(user_input)
            
            # Check if calculation succeeded
            if not nutrition_profile or not nutrition_profile.get('success'):
                print(f"[ERROR] Calculation failed - returned: {type(nutrition_profile)}")
                return None
                
            print(f"[OK] Profile calculated:")
            print(f"     TDEE: {nutrition_profile['energy']['tdee']:.0f} kcal")
            print(f"     BMI: {nutrition_profile['anthropometrics']['bmi']:.2f}")
        except Exception as e:
            print(f"[ERROR] Failed to calculate nutrition profile: {e}")
            import traceback
            traceback.print_exc()
            return None
        
        # Step 3: Generate menu using Greedy Algorithm
        print(f"\n[3/4] Generating menu with Greedy Algorithm...")
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
            
            print("[OK] Menu generated successfully")
        except Exception as e:
            print(f"[ERROR] Failed to generate menu: {e}")
            import traceback
            traceback.print_exc()
            return None
        
        # Step 4: Analyze results
        print(f"\n[4/4] Analyzing achievement vs targets...")
        
        analysis = self._analyze_achievement(
            nutrition_profile,
            menu_plan,
            user_profile,
            disease_mode
        )
        
        return analysis
    
    def _analyze_achievement(self, nutrition_profile, menu_plan, user_profile, disease_mode):
        """Detailed analysis of targets vs actual"""
        
        # Extract targets
        targets = nutrition_profile['guidelines']['nutrients']
        tdee = nutrition_profile['energy']['tdee']
        
        # Extract actuals from menu_plan
        actuals = {
            'energy': menu_plan.total_daily_calories,
            'protein_g': menu_plan.total_daily_protein_g,
            'carbohydrate_g': menu_plan.total_daily_carb_g,
            'fat_g': menu_plan.total_daily_fat_g,
        }
        
        # Build comprehensive analysis
        analysis = {
            'user_profile': user_profile,
            'disease_mode': disease_mode,
            'menu_plan': menu_plan,
            'nutrition_profile': nutrition_profile,
            'targets': targets,
            'actuals': actuals,
            'achievements': {},
            'meal_breakdown': {},
        }
        
        # Calculate achievement % for key macronutrients
        nutrient_mapping = {
            'Energy': ('energy', tdee),
            'Protein': ('protein_g', (targets.get('protein_g', {}).get('min', 0) + targets.get('protein_g', {}).get('max', 0)) / 2),
            'Carbohydrate': ('carbohydrate_g', (targets.get('carbohydrate_g', {}).get('min', 0) + targets.get('carbohydrate_g', {}).get('max', 0)) / 2),
            'Fat': ('fat_g', (targets.get('fat_g', {}).get('min', 0) + targets.get('fat_g', {}).get('max', 0)) / 2),
        }
        
        for display_name, (key, target_val) in nutrient_mapping.items():
            actual_val = actuals.get(key, 0)
            if target_val > 0:
                achievement_pct = (actual_val / target_val) * 100
            else:
                achievement_pct = 100 if actual_val == 0 else 0
            
            analysis['achievements'][display_name] = {
                'target': target_val,
                'actual': actual_val,
                'achievement_pct': achievement_pct,
                'difference': actual_val - target_val,
            }
        
        # Meal breakdown
        if menu_plan.breakfast:
            analysis['meal_breakdown']['breakfast'] = self._meal_summary(menu_plan.breakfast)
        if menu_plan.lunch:
            analysis['meal_breakdown']['lunch'] = self._meal_summary(menu_plan.lunch)
        if menu_plan.dinner:
            analysis['meal_breakdown']['dinner'] = self._meal_summary(menu_plan.dinner)
        if menu_plan.snack:
            analysis['meal_breakdown']['snack'] = self._meal_summary(menu_plan.snack)
        
        return analysis
    
    def _meal_summary(self, meal):
        """Extract meal summary info - ONLY count selected items (first candidate per course)"""
        summary = {
            'calories': 0,
            'protein_g': 0,
            'carbs_g': 0,
            'fat_g': 0,
            'items': [],
        }
        
        # Collect ONLY selected items (first candidate from each course)
        selected_items = []
        
        # For regular meals (Breakfast, Lunch, Dinner) - access courses dict
        if hasattr(meal, 'courses') and isinstance(meal.courses, dict):
            for course_name, course in meal.courses.items():
                if hasattr(course, 'candidates') and len(course.candidates) > 0:
                    # BUG FIX: Only take FIRST candidate (the selected one)
                    selected_items.append(course.candidates[0])
        
        # For snack - take first 3 candidates only (as displayed for choice)
        elif hasattr(meal, 'candidates'):
            # For snack, only the FIRST candidate is selected
            if meal.candidates and len(meal.candidates) > 0:
                selected_items = [meal.candidates[0]]
        
        # Calculate totals from SELECTED items only
        for item in selected_items:
            summary['calories'] += item.energy_kcal or 0
            summary['protein_g'] += item.protein_g or 0
            summary['carbs_g'] += item.carbohydrate_g or 0
            summary['fat_g'] += item.fat_g or 0
            summary['items'].append({
                'name': item.food_name[:40],
                'portion_g': item.portion_gram,
                'calories': item.energy_kcal,
            })
        
        return summary
    
    def print_summary(self, analysis):
        """Pretty print summary"""
        
        if not analysis:
            print("\n[ERROR] No analysis to display")
            return
        
        profile = analysis['user_profile']
        print("\n" + "="*80)
        print("USER PROFILE")
        print("="*80)
        print(f"Age: {profile.get('age')} | Gender: {profile.get('gender')} | " +
              f"Weight: {profile.get('weight_kg')}kg | Height: {profile.get('height_cm')}cm | " +
              f"Activity: {profile.get('activity_level')}")
        print(f"Disease Mode: {analysis['disease_mode']}")
        
        print("\n" + "="*80)
        print("NUTRITION ACHIEVEMENT SUMMARY")
        print("="*80)
        print(f"{'Nutrient':<25} {'Target':>12} {'Actual':>12} {'Diff':>10} {'%':>8}")
        print("-" * 80)
        
        # Sort by achievement %
        achievements = sorted(
            analysis['achievements'].items(),
            key=lambda x: x[1]['achievement_pct'],
            reverse=True
        )
        
        for nutrient, data in achievements:
            nutrient_display = str(nutrient)[:24]
            target = data['target']
            actual = data['actual']
            diff = data['difference']
            pct = data['achievement_pct']
            
            # Color coding
            if 95 <= pct <= 105:
                status = "OK"
            elif pct < 90:
                status = "LOW"
            elif pct > 110:
                status = "HIGH"
            else:
                status = "--"
            
            print(f"{nutrient_display:<25} {target:>12.1f} {actual:>12.1f} {diff:>+10.1f} {pct:>7.1f}% {status}")
        
        print("\n" + "="*80)
        print("MEAL BREAKDOWN")
        print("="*80)
        
        for meal_name, meal_data in analysis['meal_breakdown'].items():
            print(f"\n{meal_name.upper()}:")
            print(f"  Calories: {meal_data['calories']:.0f} kcal")
            print(f"  Protein: {meal_data['protein_g']:.1f}g | Carbs: {meal_data['carbs_g']:.1f}g | Fat: {meal_data['fat_g']:.1f}g")
            print(f"  Items ({len(meal_data['items'])}):")
            for item in meal_data['items']:
                print(f"    - {item['name']:<35} {item['portion_g']:>6.0f}g | {item['calories']:>6.0f}kcal")
        
        print("\n" + "="*80)
        print("ACHIEVEMENT SCORE")
        print("="*80)
        
        # Calculate overall achievement
        achievements_list = [data['achievement_pct'] for data in analysis['achievements'].values()]
        avg_achievement = sum(achievements_list) / len(achievements_list) if achievements_list else 0
        
        target_count = sum(1 for data in analysis['achievements'].values() if 95 <= data['achievement_pct'] <= 105)
        total_count = len(analysis['achievements'])
        target_compliance = (target_count / total_count * 100) if total_count > 0 else 0
        
        print(f"Average Achievement: {avg_achievement:.1f}%")
        print(f"Target Compliance: {target_count}/{total_count} nutrients within 95-105% ({target_compliance:.1f}%)")
        
        # Verdict based on TARGET COMPLIANCE, not average achievement
        # BUG FIX: Compliance 0% should NOT show SUCCESS
        if target_compliance >= 75:  # At least 3/4 nutrients within target
            print("\n[SUCCESS] Menu achieves targets well!")
        elif target_compliance >= 50:  # At least 2/4 nutrients within target
            print("\n[WARNING] Menu partially achieves targets - some nutrients outside acceptable range")
        else:  # Less than 2/4 nutrients within target
            print("\n[ERROR] Menu does not achieve target nutrition adequately - major nutrient imbalances")
        
        print("="*80 + "\n")


def main():
    """Test dengan berbagai user profiles"""
    
    analyzer = SummaryAnalyzer()
    
    # Test 1: Default user profile
    print("\n\nTEST 1: Default User (25y M 70kg 175cm Activity 1.6) - NORMAL mode")
    print("="*80)
    
    user1 = {
        'age': 25,
        'gender': 'M',
        'weight_kg': 70,
        'height_cm': 175,
        'activity_level': 1.6,
    }
    
    analysis1 = analyzer.generate_and_analyze(user1, disease_mode='normal')
    if analysis1:
        analyzer.print_summary(analysis1)
    
    # Test 2: Different profile - female
    print("\n\nTEST 2: Female User (30y F 60kg 165cm Activity 1.5) - NORMAL mode")
    print("="*80)
    
    user2 = {
        'age': 30,
        'gender': 'F',
        'weight_kg': 60,
        'height_cm': 165,
        'activity_level': 1.5,
    }
    
    analysis2 = analyzer.generate_and_analyze(user2, disease_mode='normal')
    if analysis2:
        analyzer.print_summary(analysis2)
    
    print("\n\nNote: CKD and other disease modes require further debugging in NutritionService")


if __name__ == '__main__':
    main()

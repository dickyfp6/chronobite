"""
GREEDY ALGORITHM - CLI TEST INTERFACE
======================================

Comprehensive CLI for testing the 7-Phase DSS Meal Optimization Pipeline:
1. User Profile → 2. Nutrition Constraints → 3. Greedy Optimization
4. Portion Optimization → 5. Nutrition Recalculation → 6. Final Recommendation
7. User Substitution (stub for future implementation)

USAGE MODES:
============

1. Normal User (Default):
   $ python test_cli.py
   or
   $ python test_cli.py normal

2. Interactive Mode (Custom Input):
   $ python test_cli.py interactive
   
   Then enter:
   - Gender (M/F)
   - Age
   - Weight (kg)
   - Height (cm)
   - Activity Factor
   - Disease (normal, dm2, hypertension, ckd, obesity)

3. Pre-configured Disease Tests:
   $ python test_cli.py disease       # Diabetes (dm2)
   $ python test_cli.py hypertension  # Hypertension
   $ python test_cli.py ckd           # Chronic Kidney Disease
   $ python test_cli.py obesity       # Obesity

OUTPUT:
=======

For each meal (Breakfast, Lunch, Dinner, Snack):
- Main Course (3 candidates with scaled portions & nutrients)
- Side Dish (3 candidates with scaled portions & nutrients)
- Drink (3 candidates with scaled portions & nutrients)
- Snack (3 candidates with scaled portions & nutrients)

Daily Totals:
- Total Calories, Protein, Carbs, Fat
- All scaled to actual portion sizes (NOT per 100g)

ARCHITECTURE:
=============

Phase 1: Generate 3 diverse food candidates per course (per-100g basis)
Phase 2: Optimize portions → portion_g = (target_kcal / kcal_per_100g) * 100
Phase 3: Scale all nutrients → nutrient_actual = nutrient_per_100g * (portion_g / 100)
Phase 4: Return MenuPlan with all courses having scaled values

All values in output are ACTUAL portions (grams/ml) with SCALED nutrients.
"""

import sys
import os

# Add model to path explicitly and ensure correct directory context
model_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(model_dir)

# Add System Flow explicitly to find nutrition_service
system_flow_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'C. System Flow'))
sys.path.append(system_flow_dir)

from nutrition_service import NutritionService

def print_menu_plan(menu_plan):
    """Utility to print the MenuPlan object clearly"""
    if not menu_plan:
        print("[ERROR] No menu plan generated")
        return
        
    print("\n" + "="*50)
    print(f"[MENU] GENERATED MENU PLAN (Algorithm: {menu_plan.algorithm_used})")
    print("="*50)
    
    # Print nutritional summary
    print("\n[NUTRITION] DAILY TOTALS:")
    print(f"  Calories: {menu_plan.total_daily_calories:.1f} kcal")
    print(f"  Protein:  {menu_plan.total_daily_protein_g:.1f} g")
    print(f"  Carbs:    {menu_plan.total_daily_carb_g:.1f} g")
    print(f"  Fat:      {menu_plan.total_daily_fat_g:.1f} g")
    
    meals = {
        'Breakfast': menu_plan.breakfast,
        'Lunch': menu_plan.lunch,
        'Dinner': menu_plan.dinner,
        'Snack': menu_plan.snack,
    }
    
    for meal_name, meal in meals.items():
        if not meal:
            continue
            
        print(f"\n[MEAL] {meal_name.upper()}")
        print(f"   Target: {meal.target_calories:.1f} kcal | Actual: {meal.actual_calories:.1f} kcal")
        
        if meal.meal_type == 'Snack':
            for idx, item in enumerate(meal.candidates):
                marker = "[SELECTED]" if idx == 0 else "[OPTION]  "
                print(f"   {marker}: {item.food_name} ({item.food_group})")
                print(f"              {item.portion_gram}g | {item.energy_kcal:.1f}kcal | P:{item.protein_g:.1f}g | C:{item.carbohydrate_g:.1f}g | F:{item.fat_g:.1f}g")
        else:
            options = {
                'Main': meal.courses.get('Main'),
                'Side': meal.courses.get('Side'),
                'Drink': meal.courses.get('Drink')
            }
            
            for course_type, course in options.items():
                print(f"\n   [{course_type} Course]")
                if not course or not course.candidates:
                    print("      No candidates generated")
                    continue
                    
                for idx, item in enumerate(course.candidates):
                    marker = "[SELECTED]" if idx == 0 else "[OPTION]"
                    print(f"      {marker}: {item.food_name} ({item.food_group})")
                    print(f"                 {item.portion_gram}g | {item.energy_kcal:.1f}kcal | P:{item.protein_g:.1f}g | C:{item.carbohydrate_g:.1f}g | F:{item.fat_g:.1f}g")

def test_greedy_algorithm():
    print("\n" + "="*80)
    print("GREEDY ALGORITHM - DSS ARCHITECTURE TEST")
    print("="*80)
    
    try:
        print("\n[1/4] Loading NutritionService...")
        ns = NutritionService()
        print("[OK] NutritionService loaded")
        
        print("\n[2/4] Creating user profile...")
        # Support multiple input modes
        test_mode = sys.argv[1] if len(sys.argv) > 1 else "normal"
        
        if test_mode == "interactive":
            # Interactive mode: ask user for input
            print("\nEnter user profile (or press Enter for defaults):")
            gender = input("Gender (M/F) [M]: ").strip().upper() or "M"
            age = int(input("Age [25]: ").strip() or "25")
            weight = float(input("Weight (kg) [70.0]: ").strip() or "70.0")
            height = float(input("Height (cm) [175.0]: ").strip() or "175.0")
            activity = float(input("Activity Factor [1.6]: ").strip() or "1.6")
            
            print("\nAvailable diseases: normal, dm2, hypertension, ckd, obesity")
            disease = input("Disease [normal]: ").strip().lower() or "normal"
            
            user = {
                'age': age, 'gender': gender, 'weight_kg': weight, 'height_cm': height,
                'activity_factor': activity, 'disease': disease
            }
            print(f"[OK] User profile created: {gender} {age}y {weight}kg {height}cm Activity:{activity} Disease:{disease}")
        
        elif test_mode == "disease":
            # Pre-configured diabetes test
            user = {
                'age': 45, 'gender': 'F', 'weight_kg': 65.0, 'height_cm': 160.0,
                'activity_factor': 1.4, 'disease': 'dm2'
            }
            print("Profile: Female, 45y, 65kg, 160cm, Activity: 1.4, Disease: dm2")
        
        elif test_mode == "hypertension":
            # Pre-configured hypertension test
            user = {
                'age': 50, 'gender': 'M', 'weight_kg': 85.0, 'height_cm': 180.0,
                'activity_factor': 1.5, 'disease': 'hypertension'
            }
            print("Profile: Male, 50y, 85kg, 180cm, Activity: 1.5, Disease: hypertension")
        
        elif test_mode == "ckd":
            # Pre-configured CKD test
            user = {
                'age': 55, 'gender': 'M', 'weight_kg': 75.0, 'height_cm': 172.0,
                'activity_factor': 1.4, 'disease': 'ckd'
            }
            print("Profile: Male, 55y, 75kg, 172cm, Activity: 1.4, Disease: ckd")
        
        elif test_mode == "obesity":
            # Pre-configured obesity test
            user = {
                'age': 40, 'gender': 'F', 'weight_kg': 95.0, 'height_cm': 162.0,
                'activity_factor': 1.3, 'disease': 'obesity'
            }
            print("Profile: Female, 40y, 95kg, 162cm, Activity: 1.3, Disease: obesity")
        
        else:
            # Default: normal user
            user = {
                'age': 25, 'gender': 'M', 'weight_kg': 70.0, 'height_cm': 175.0,
                'activity_factor': 1.6, 'disease': 'normal'
            }
            print("Profile: Male, 25y, 70kg, 175cm, Activity: 1.6, Normal")
            
        print("[OK] User profile created")
        
        print("\n[3/4] Calculating nutrition guidelines...")
        # Use NutritionService to calculate guidelines
        ns_result = dict(ns.calculate_nutrition_needs(user) or {})
        
        if not ns_result.get('success'):
            print(f"[ERROR] Failed to calculate nutrition needs: {ns_result.get('error')}")
            return
        
        guidelines = ns_result.get('guidelines', {})
        tdee = ns_result['energy']['tdee']
        # pyrefly: ignore [missing-attribute]
        food_db = ns_result.get('food_data', {}).get('dataframe')
        
        if food_db is None or len(food_db) == 0:
            print("[ERROR] No food database available")
            return
        
        print("[OK] Nutrition guidelines calculated:")
        print(f"  - TDEE: {tdee:.0f} kcal")
        print(f"  - BMI: {ns_result.get('anthropometrics', {}).get('bmi', 0):.2f}")
        print(f"  - Constraints: {len(guidelines.get('nutrients', {}))} nutrients defined")
        if guidelines.get('disease'):
            print(f"  - Disease: {guidelines['disease']}")
            
        print("\n[4/4] Initializing Greedy Algorithm and generating menu...")
        # Get interface
        from greedy_interface import get_greedy_algorithm  # type: ignore
        greedy = get_greedy_algorithm(food_db, guidelines)
        
        # Generate menu using TDEE (NEW ARCHITECTURE)
        menu_plan = greedy.generate_menu_plan(user, tdee)
        
        # Output the results
        print_menu_plan(menu_plan)
        
        print("\n" + "="*50)
        print("[CONSTRAINTS] HARD CONSTRAINT VALIDATION")
        print("="*50)
        
        guidelines = ns_result.get('guidelines', {}).get('nutrients', {})
        
        # Get daily totals from greedy optimizer
        daily = greedy.optimizer.cumulative_nutrients
        
        hard_violations = []
        hard_passed = []
        
        for nutrient, constraint in guidelines.items():
            if constraint.get('hard_soft_type') != 'HARD':
                continue
            if constraint.get('constraint_type') == 'unlimited':
                continue
            
            actual = daily.get(nutrient, None)
            if actual is None:
                continue  # skip constraints for missing nutrients
            min_v = constraint.get('min') or 0
            max_v = constraint.get('max')
            unit  = constraint.get('unit', '')
            
            min_ok = actual >= min_v
            max_ok = (max_v is None) or (actual <= max_v)
            
            if min_ok and max_ok:
                hard_passed.append(
                    f"  ✅ {nutrient}: {actual:.1f} {unit} "
                    f"(target: {min_v:.1f}-{max_v if max_v else '∞'} {unit})"
                )
            else:
                hard_violations.append(
                    f"  ❌ {nutrient}: {actual:.1f} {unit} "
                    f"(target: {min_v:.1f}-{max_v if max_v else '∞'} {unit})"
                )
        
        if hard_violations:
            print(f"Status: ⚠️  INFEASIBLE ({len(hard_violations)} violation(s))")
            print("\nViolations:")
            for v in hard_violations:
                print(v)
        else:
            print("Status: ✅ FEASIBLE - All HARD constraints satisfied!")
        
        if hard_passed:
            print(f"\nPassed ({len(hard_passed)}):")
            for p in hard_passed:
                print(p)
            
    except Exception as e:
        print(f"\n[ERROR] TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_greedy_algorithm()
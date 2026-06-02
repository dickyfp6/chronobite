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
        'Snack': menu_plan.snack,
        'Dinner': menu_plan.dinner
    }
    
    for meal_name, meal in meals.items():
        if not meal:
            continue
            
        print(f"\n[MEAL] {meal_name.upper()}")
        print(f"   Target: {meal.target_calories:.1f} kcal | Actual: {meal.actual_calories:.1f} kcal")
        
        if meal.meal_type == 'Snack':
            # Snack only uses candidates directly
            for idx, item in enumerate(meal.candidates):
                print(f"   {idx+1}. {item.food_name}")
                print(f"      {item.portion_gram}g | {item.energy_kcal}kcal")
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
        
        print("\n[2/4] Creating sample user profile...")
        test_type = sys.argv[1] if len(sys.argv) > 1 else "normal"
        
        if test_type == "disease":
            # Diabetes user
            user = {
                'age': 45, 'gender': 'F', 'weight_kg': 65.0, 'height_cm': 160.0,
                'activity_factor': 1.4, 'disease': 'dm2'
            }
            print("Profile: Female, 45y, 65kg, 160cm, Activity: 1.4, Disease: dm2")
        else:
            # Normal user
            user = {
                'age': 25, 'gender': 'M', 'weight_kg': 70.0, 'height_cm': 175.0,
                'activity_factor': 1.6, 'disease': 'normal'
            }
            print("Profile: Male, 25y, 70kg, 175cm, Activity: 1.6, Normal")
            
        print("[OK] User profile created")
        
        print("\n[3/4] Calculating nutrition guidelines...")
        # Use NutritionService to calculate guidelines
        ns_result = ns.calculate_nutrition_needs(user)
        
        if not ns_result.get('success'):
            print(f"[ERROR] Failed to calculate nutrition needs: {ns_result.get('error')}")
            return
        
        guidelines = ns_result.get('guidelines', {})
        tdee = ns_result['energy']['tdee']
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
        from greedy_interface import get_greedy_algorithm
        greedy = get_greedy_algorithm(food_db, guidelines)
        
        # Generate menu using TDEE (NEW ARCHITECTURE)
        menu_plan = greedy.generate_menu_plan(user, tdee)
        
        # Output the results
        print_menu_plan(menu_plan)
            
    except Exception as e:
        print(f"\n[ERROR] TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_greedy_algorithm()
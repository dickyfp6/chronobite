
import sys
import os
import importlib.util

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

spec = importlib.util.spec_from_file_location("nutrition_service",
    os.path.abspath(os.path.join(os.path.dirname(__file__), '../../C. System Flow/nutrition_service.py')))
assert spec is not None
assert spec.loader is not None
nutrition_service_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nutrition_service_module)
NutritionService = nutrition_service_module.NutritionService

spec = importlib.util.spec_from_file_location("greedy_interface",
    os.path.abspath(os.path.join(os.path.dirname(__file__), './greedy_interface.py')))
assert spec is not None
assert spec.loader is not None
greedy_interface_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(greedy_interface_module)
GreedyAlgorithmInterface = greedy_interface_module.GreedyAlgorithmInterface

# Generate a menu
nutrition_service = NutritionService()
user_input = {
    'age': 25,
    'gender': 'M',
    'weight': 70,
    'height': 175,
    'activity_factor': 1.6,
    'disease': 'normal',
}
nutrition_profile = nutrition_service.calculate_nutrition_needs(user_input)

greedy = GreedyAlgorithmInterface(
    nutrition_service.guideline_loader.food_df,
    nutrition_profile['guidelines']['nutrients']
)

menu_plan = greedy.generate_menu_plan(
    user_input,
    nutrition_profile['energy']['tdee']
)

# DEBUG: Count all items per course
print("\n" + "="*80)
print("DEBUG: CANDIDATE COUNT ANALYSIS")
print("="*80)

breakfast = menu_plan.breakfast
print(f"\nBREAKFAST courses: {list(breakfast.courses.keys())}")
for course_name, course in breakfast.courses.items():
    print(f"  {course_name}: {len(course.candidates)} candidates")
    for i, item in enumerate(course.candidates):
        print(f"    [{i}] {item.food_name[:40]:<40} {item.energy_kcal:>6.1f}kcal")

print(f"\nBreakfast meal.actual_calories: {breakfast.actual_calories:.1f}")

# Manual sum of first candidates
first_candidate_sum = sum(course.candidates[0].energy_kcal for course in breakfast.courses.values() if course.candidates)
print(f"Sum of FIRST candidates only: {first_candidate_sum:.1f}")

# Manual sum of ALL candidates
all_candidate_sum = sum(item.energy_kcal for course in breakfast.courses.values() for item in course.candidates)
print(f"Sum of ALL candidates: {all_candidate_sum:.1f}")

print(f"\nDaily total from MenuPlan: {menu_plan.total_daily_calories:.1f} kcal")
print(f"Daily total from cumulative (as should be): (should equal first candidates only per course)")


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

menu_plan = greedy.generate_menu_plan(user_input, nutrition_profile['energy']['tdee'])

print("="*80)
print("VERIFICATION: MEAL SUMS vs DAILY TOTALS")
print("="*80)

# Calculate meal totals
meals = {
    'breakfast': menu_plan.breakfast,
    'lunch': menu_plan.lunch,
    'dinner': menu_plan.dinner,
    'snack': menu_plan.snack,
}

meal_totals = {
    'energy': 0,
    'protein_g': 0,
    'carbohydrate_g': 0,
    'fat_g': 0,
}

for meal_name, meal in meals.items():
    if not meal:
        continue
    
    energy = 0
    protein = 0
    carbs = 0
    fat = 0
    
    if hasattr(meal, 'courses') and isinstance(meal.courses, dict):
        for course in meal.courses.values():
            if course.candidates and len(course.candidates) > 0:
                item = course.candidates[0]  # Only first candidate
                energy += item.energy_kcal
                protein += item.protein_g
                carbs += item.carbohydrate_g
                fat += item.fat_g
    elif hasattr(meal, 'candidates'):
        if meal.candidates and len(meal.candidates) > 0:
            item = meal.candidates[0]  # Only first candidate
            energy += item.energy_kcal
            protein += item.protein_g
            carbs += item.carbohydrate_g
            fat += item.fat_g
    
    meal_totals['energy'] += energy
    meal_totals['protein_g'] += protein
    meal_totals['carbohydrate_g'] += carbs
    meal_totals['fat_g'] += fat
    
    print(f"\n{meal_name.upper()}:")
    print(f"  Energy: {energy:.1f} kcal | Protein: {protein:.1f}g | Carbs: {carbs:.1f}g | Fat: {fat:.1f}g")

print("\n" + "-"*80)
print("\nMEAL TOTALS (sum):")
print(f"  Energy: {meal_totals['energy']:.1f} kcal")
print(f"  Protein: {meal_totals['protein_g']:.1f}g")
print(f"  Carbohydrate: {meal_totals['carbohydrate_g']:.1f}g")
print(f"  Fat: {meal_totals['fat_g']:.1f}g")

print("\nMENUPLAN DAILY TOTALS:")
print(f"  Energy: {menu_plan.total_daily_calories:.1f} kcal")
print(f"  Protein: {menu_plan.total_daily_protein_g:.1f}g")
print(f"  Carbohydrate: {menu_plan.total_daily_carb_g:.1f}g")
print(f"  Fat: {menu_plan.total_daily_fat_g:.1f}g")

print("\nMATCH VERIFICATION:")
energy_match = abs(meal_totals['energy'] - menu_plan.total_daily_calories) < 0.1
protein_match = abs(meal_totals['protein_g'] - menu_plan.total_daily_protein_g) < 0.1
carbs_match = abs(meal_totals['carbohydrate_g'] - menu_plan.total_daily_carb_g) < 0.1
fat_match = abs(meal_totals['fat_g'] - menu_plan.total_daily_fat_g) < 0.1

print(f"  Energy match: {'YES' if energy_match else 'NO'}")
print(f"  Protein match: {'YES' if protein_match else 'NO'}")
print(f"  Carbs match: {'YES' if carbs_match else 'NO'}")
print(f"  Fat match: {'YES' if fat_match else 'NO'}")

if all([energy_match, protein_match, carbs_match, fat_match]):
    print("\n=== ALL CALCULATIONS VERIFIED - NO DOUBLE COUNTING ===")
else:
    print("\n=== MISMATCH DETECTED ===")

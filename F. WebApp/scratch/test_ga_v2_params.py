import sys
import os
import pandas as pd
import time

# Get parent directories correctly
scratch_dir = os.path.dirname(os.path.abspath(__file__))
webapp_dir = os.path.dirname(scratch_dir)
root_dir = os.path.dirname(webapp_dir)

# Add correct paths to sys.path
sys.path.append(webapp_dir)
sys.path.append(os.path.join(root_dir, 'C. System Flow'))
sys.path.append(os.path.join(root_dir, 'D. Model'))
sys.path.append(os.path.join(root_dir, 'D. Model', 'Genetic Algorithm'))

from nutrition_service import NutritionService
from ga_interface import GeneticAlgorithmInterface # type: ignore
from ga_v2 import run_ga, local_search, fitness, validate_final_solution, calculate_portion_sizes_dynamic # type: ignore

print("Initializing NutritionService...")
service = NutritionService()
user_input = {
    'gender': 'M',
    'age': 45,
    'weight': 85,
    'height': 165,
    'activity_factor': 1.725,
    'disease': ['dm2'],
    'food_preferences': []
}
result = service.calculate_nutrition_needs(user_input)
if result is None or not isinstance(result, dict):
    print("Error calculating nutrition needs.")
    sys.exit(1)

guidelines = result.get('guidelines')
energy_info = result.get('energy')
food_data = result.get('food_data')

if guidelines is None or energy_info is None or food_data is None:
    print("Invalid result structure.")
    sys.exit(1)

# pyrefly: ignore [bad-index]
tdee = energy_info['tdee']
# pyrefly: ignore [bad-index]
food_db = food_data['dataframe']

print(f"User TDEE target: {tdee:.1f} kcal")
ga = GeneticAlgorithmInterface(food_db, guidelines)


print("\n--- Running GA v2 with pop_size=71, generations=91, iterations=37 ---")
t0 = time.time()

best_solution, top_solutions = run_ga(
    food_df=ga.food_db,
    guidelines=ga.constraint_bag,
    tdee=tdee,
    generations=91,
    pop_size=71,
    elite_ratio=0.15,
    mutation_rate=0.35,
    verbose=True
)

if best_solution is not None:
    best_solution = local_search(
        solution=best_solution,
        food_df=ga.food_db,
        guidelines=ga.constraint_bag,
        tdee=tdee,
        iterations=37,
        verbose=True
    )
    
    duration = time.time() - t0
    fit = fitness(best_solution, ga.constraint_bag, tdee=tdee)
    
    portioned_df = calculate_portion_sizes_dynamic(best_solution, tdee, ga.constraint_bag)
    val = validate_final_solution(portioned_df, ga.constraint_bag, tdee)
    
    print("\n================ TEST COMPLETED ================")
    print(f"Time Taken: {duration:.2f}s")
    print(f"Fitness Score (Lower is better): {fit:.4f}")
    print(f"Compliance Details: {val.get('summary', '')}")
    print("================================================")
else:
    print("GA failed to find a solution.")

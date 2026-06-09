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
# pyrefly: ignore [missing-import]
from ga_interface import GeneticAlgorithmInterface

service = NutritionService()
user_input = {
    'gender': 'M',
    'age': 45,
    'weight': 70,
    'height': 165,
    'activity_factor': 1.545,
    'disease': ['normal'],
    'food_preferences': []
}
result = service.calculate_nutrition_needs(user_input)
guidelines = result['guidelines']
# pyrefly: ignore [unsupported-operation]
tdee = result['energy']['tdee']
# pyrefly: ignore [unsupported-operation]
food_db = result['food_data']['dataframe']

ga = GeneticAlgorithmInterface(food_db, guidelines)

# Test combinations of pop_size and generations
combinations = [
    (25, 12, 3), # current
    (20, 10, 2),
    (15, 8, 2),
    (15, 6, 2)
]

# pyrefly: ignore [missing-import]
from ga_v1 import run_ga, local_search

for pop_size, generations, ls_iterations in combinations:
    print(f"\n--- Testing pop_size={pop_size}, generations={generations}, ls_iterations={ls_iterations} ---")
    t0 = time.time()
    
    best_solution, top_solutions = run_ga(
        food_df=ga.food_db,
        guidelines=ga.constraint_bag,
        tdee=tdee,
        generations=generations,
        pop_size=pop_size,
        elite_ratio=0.15,
        mutation_rate=0.35,
        verbose=False
    )
    
    best_solution = local_search(
        solution=best_solution,
        food_df=ga.food_db,
        guidelines=ga.constraint_bag,
        tdee=tdee,
        iterations=ls_iterations,
        verbose=False
    )
    
    duration = time.time() - t0
    # Evaluate fitness
    # pyrefly: ignore [missing-import]
    from ga_v1 import fitness, validate_final_solution
    fit = fitness(best_solution, ga.constraint_bag, tdee=tdee)
    
    # Portioned validation
    # pyrefly: ignore [missing-import]
    from ga_v1 import calculate_portion_sizes_dynamic
    portioned_df = calculate_portion_sizes_dynamic(best_solution, tdee, ga.constraint_bag)
    val = validate_final_solution(portioned_df, ga.constraint_bag, tdee)
    
    print(f"Time: {duration:.2f}s")
    print(f"Fitness: {fit:.2f}")
    print(f"Compliance: {val.get('compliance_rate', 0)*100:.1f}% ({val.get('summary', '')})")

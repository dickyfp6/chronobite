import sys
import os
import time
import pandas as pd
import numpy as np
import itertools

# Setup paths
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

sys.path.append(os.path.join(project_root, 'F. WebApp'))
sys.path.append(os.path.join(project_root, 'D. Model', 'Genetic Algorithm'))

try:
    # Need to add C. System Flow to path to import nutrition_service
    sys.path.append(os.path.join(project_root, 'C. System Flow'))
    from nutrition_service import NutritionService
    # pyrefly: ignore [missing-import]
    from ga_interface import GeneticAlgorithmInterface
    # pyrefly: ignore [missing-import]
    from ga_v1 import run_ga, fitness, calculate_portion_sizes_dynamic, local_search
except ImportError as e:
    print(f"Failed to import required modules: {e}")
    sys.exit(1)

def create_dummy_guidelines(ns: NutritionService):
    user_input = {
        'gender': 'M',
        'age': 22,
        'weight': 65,
        'height': 170,
        'activity_factor': 1.845,
        'disease': 'normal',
        'food_preferences': []
    }
    result = ns.calculate_nutrition_needs(user_input)
    if not result['success']:
        print(f"Nutrition Calculation Failed: {result['error']}")
        sys.exit(1)
        
    # pyrefly: ignore [unsupported-operation]
    food_df = result['food_data']['dataframe']
    # pyrefly: ignore [unsupported-operation]
    tdee = result['user_params']['tdee']
    
    ga_interface = GeneticAlgorithmInterface(food_df, result)
    return food_df, ga_interface.constraint_bag, tdee

def main():
    print("========================================")
    print("GA HYPERPARAMETER TUNING SCRIPT")
    print("========================================")
    
    # 1. Load Data
    print("\n[1] Loading Food Database and Guidelines...")
    ns = NutritionService()
    food_df, guidelines, tdee = create_dummy_guidelines(ns)
    
    print(f"Food Items loaded: {len(food_df)}")
    print(f"Target TDEE: {tdee:.2f} kcal")
    
    # Tuning Configuration
    # Options: 'grid' or 'random'
    # 'grid': tests specific combinations defined below
    # 'random': randomly samples parameters within specified ranges (step of 1)
    tuning_mode = 'random' 
    n_random_combinations = 50
    n_trials = 3
    
    # 2. Define Parameter Space
    if tuning_mode == 'random':
        pop_size_range = (30, 100)
        generations_range = (50, 150)
        ls_iterations_range = (20, 50)
        
        import random
        random.seed(42) # For reproducibility
        
        combinations_set = set()
        # Ensure we generate exactly n_random_combinations unique sets
        while len(combinations_set) < n_random_combinations:
            pop = random.randint(pop_size_range[0], pop_size_range[1])
            gen = random.randint(generations_range[0], generations_range[1])
            ls = random.randint(ls_iterations_range[0], ls_iterations_range[1])
            combinations_set.add((pop, gen, ls))
            
        combinations = list(combinations_set)
        keys = ['pop_size', 'generations', 'ls_iterations']
        total_combinations = len(combinations)
        print(f"\n[2] Starting Randomized Search (Step of 1)")
    else:
        grid = {
            'pop_size': [30, 50, 100],
            'generations': [50, 100, 150],
            'ls_iterations': [20, 35, 50]
        }
        keys = list(grid.keys())
        combinations = list(itertools.product(*(grid[k] for k in keys)))
        total_combinations = len(combinations)
        print(f"\n[2] Starting Grid Search")
        
    print(f"Total Combinations to test: {total_combinations}")
    print(f"Trials per combination: {n_trials}")
    print("========================================\n")
    
    results = []
    
    for idx, combo in enumerate(combinations):
        params = dict(zip(keys, combo))
        print(f"Testing [{idx+1}/{total_combinations}] - {params}")
        
        trial_fitness = []
        trial_times = []
        
        for trial in range(n_trials):
            start_time = time.time()
            
            # Run GA + Local Search
            try:
                # 1. Run GA with fixed elite_ratio and mutation_rate (from system defaults)
                best_solution, _ = run_ga(
                    food_df=food_df,
                    pop_size=params['pop_size'],
                    generations=params['generations'],
                    mutation_rate=0.35,
                    elite_ratio=0.15,
                    guidelines=guidelines,
                    tdee=tdee,
                    verbose=False
                )
                
                # 2. Run Local Search for fine-tuning
                best_solution = local_search(
                    solution=best_solution,
                    food_df=food_df,
                    guidelines=guidelines,
                    tdee=tdee,
                    iterations=params['ls_iterations'],
                    verbose=False
                )
                
                # Calculate final fitness after portion size dynamic sizing
                end_time = time.time()
                exec_time = end_time - start_time
                
                # Portioned fitness
                portioned = calculate_portion_sizes_dynamic(best_solution, tdee, guidelines)
                final_fitness = fitness(portioned, guidelines, tdee=tdee)
                
                trial_fitness.append(final_fitness)
                trial_times.append(exec_time)
                
            except Exception as e:
                print(f"  Error on trial {trial}: {e}")
                trial_fitness.append(float('inf'))
                trial_times.append(0)
        
        avg_fitness = np.mean([f for f in trial_fitness if f != float('inf')])
        avg_time = np.mean(trial_times)
        std_fitness = np.std([f for f in trial_fitness if f != float('inf')])
        
        print(f"  Result -> Avg Fitness: {avg_fitness:.2f} | Std: {std_fitness:.2f} | Avg Time: {avg_time:.2f}s")
        
        # Save to results
        result_row = {
            **params,
            'avg_fitness': avg_fitness,
            'std_fitness': std_fitness,
            'avg_time_sec': avg_time,
            'trials_run': n_trials
        }
        results.append(result_row)
        
        # Save incrementally
        results_df = pd.DataFrame(results)
        results_df.to_csv(os.path.join(current_dir, "tuning_results.csv"), index=False)
        
    # 3. Print Top Results
    print("\n========================================")
    print("TUNING COMPLETED!")
    print("========================================")
    results_df = pd.DataFrame(results)
    
    # Sort by best fitness (lowest)
    top_results = results_df.sort_values('avg_fitness').head(3)
    print("\nTop 3 Parameter Combinations:")
    for i, (_, row) in enumerate(top_results.iterrows()):
        print(f"Rank {i+1}: pop={int(row['pop_size'])}, gen={int(row['generations'])}, "
              f"ls_iter={int(row['ls_iterations'])} "
              f"-> Fitness: {row['avg_fitness']:.2f} (Time: {row['avg_time_sec']:.2f}s)")
              
    print(f"\nFull results saved to: {os.path.join(current_dir, 'tuning_results.csv')}")

if __name__ == '__main__':
    main()


import sys
import os
import time
import pandas as pd
import numpy as np
# pyrefly: ignore [missing-import]
import optuna

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

# Disable Optuna default verbose logs to keep terminal clean
optuna.logging.set_verbosity(optuna.logging.WARNING)

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

# Load global data once
ns = NutritionService()
food_df, guidelines, tdee = create_dummy_guidelines(ns)

# Target time threshold (in seconds) to avoid Vercel 60s timeout
TIME_LIMIT = 45.0  

def objective(trial):
    # Suggest values using Bayesian optimization (step of 1)
    pop_size = trial.suggest_int('pop_size', 25, 100)
    generations = trial.suggest_int('generations', 50, 150)
    ls_iterations = trial.suggest_int('ls_iterations', 20, 50)
    
    n_trials = 3
    trial_fitness = []
    trial_times = []
    
    for _ in range(n_trials):
        start_time = time.time()
        try:
            # 1. Run GA
            best_solution, _ = run_ga(
                food_df=food_df,
                pop_size=pop_size,
                generations=generations,
                mutation_rate=0.35, # default from interface
                elite_ratio=0.15,   # default from interface
                guidelines=guidelines,
                tdee=tdee,
                verbose=False
            )
            
            # 2. Run Local Search
            best_solution = local_search(
                solution=best_solution,
                food_df=food_df,
                guidelines=guidelines,
                tdee=tdee,
                iterations=ls_iterations,
                verbose=False
            )
            
            exec_time = time.time() - start_time
            
            # 3. Dynamic portion sizing and fitness evaluation
            portioned = calculate_portion_sizes_dynamic(best_solution, tdee, guidelines)
            final_fitness = fitness(portioned, guidelines, tdee=tdee)
            
            trial_fitness.append(final_fitness)
            trial_times.append(exec_time)
        except Exception as e:
            trial_fitness.append(float('inf'))
            trial_times.append(0)
            
    # Compute average metrics
    valid_fitness = [f for f in trial_fitness if f != float('inf')]
    avg_fitness = np.mean(valid_fitness) if valid_fitness else 99999999.0
    avg_time = np.mean(trial_times)
    
    if np.isnan(avg_fitness):
        avg_fitness = 99999999.0
        
    # Store detailed metrics for reporting
    trial.set_user_attr('avg_time_sec', avg_time)
    trial.set_user_attr('actual_fitness', avg_fitness)
    
    # Penalize if execution time exceeds TIME_LIMIT (45 seconds)
    score = avg_fitness
    if avg_time > TIME_LIMIT:
        # Penalty is proportional to the seconds exceeded
        time_exceeded = avg_time - TIME_LIMIT
        score += time_exceeded * 100000.0  # Apply heavy penalty
        
    print(f"Trial {trial.number:02d} | pop={pop_size:2d}, gen={generations:3d}, ls={ls_iterations:2d} | "
          f"Fitness: {avg_fitness:7.2f} | Time: {avg_time:5.2f}s | Penalized Score: {score:7.2f}")
          
    return score

def save_results_callback(study, trial):
    # Save incremental results to CSV
    df = study.trials_dataframe()
    df = df.rename(columns={
        'params_pop_size': 'pop_size',
        'params_generations': 'generations',
        'params_ls_iterations': 'ls_iterations',
        'user_attrs_avg_time_sec': 'avg_time_sec',
        'user_attrs_actual_fitness': 'actual_fitness',
        'value': 'penalized_score'
    })
    
    cols_to_keep = ['number', 'pop_size', 'generations', 'ls_iterations', 'actual_fitness', 'avg_time_sec', 'penalized_score', 'state']
    cols_to_keep = [c for c in cols_to_keep if c in df.columns]
    
    df_filtered = df[cols_to_keep]
    df_filtered.to_csv(os.path.join(current_dir, "optuna_tuning_results.csv"), index=False)

def main():
    print("========================================")
    print("GA OPTUNA HYPERPARAMETER TUNING SCRIPT")
    print("========================================")
    print(f"Food Items loaded: {len(food_df)}")
    print(f"Target TDEE: {tdee:.2f} kcal")
    print(f"Target execution time: < {TIME_LIMIT} seconds")
    print("Starting Bayesian Optimization...")
    print("========================================\n")
    
    # Create study
    study = optuna.create_study(direction="minimize")
    
    # We will run 100 trials, which takes ~15 minutes and covers the space intelligently
    study.optimize(objective, n_trials=100, callbacks=[save_results_callback])
    
    print("\n========================================")
    print("TUNING COMPLETED!")
    print("========================================")
    best_trial = study.best_trial
    
    print(f"Best Trial: #{best_trial.number}")
    print(f"  pop_size: {best_trial.params['pop_size']}")
    print(f"  generations: {best_trial.params['generations']}")
    print(f"  ls_iterations: {best_trial.params['ls_iterations']}")
    print(f"  Fitness: {best_trial.user_attrs['actual_fitness']:.2f}")
    print(f"  Execution Time: {best_trial.user_attrs['avg_time_sec']:.2f}s")
    print(f"\nAll results saved to: {os.path.join(current_dir, 'optuna_tuning_results.csv')}")

if __name__ == '__main__':
    main()

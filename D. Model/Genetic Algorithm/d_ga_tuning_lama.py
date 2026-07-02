"""
TUNE GA DICKY - Optuna Hyperparameter Tuning untuk ga_dicky + Local Search
========================================================================

Strategi:
  Mencari kombinasi hyperparameter GA terbaik (pop_size, generations, elite_ratio,
  mutation_rate, ls_iterations) melintasi 5 skenario profil penyakit sekaligus.

Cara pakai di Kaggle (setelah clone repo):
  python "D. Model/Genetic Algorithm/tune_ga_dicky.py"
"""

import sys
import os
import json
import time
import numpy as np
import pandas as pd
import optuna
from optuna.samplers import TPESampler

# ─────────────────────────────────────────────────────────────────────────────
# 1. PATH SETUP — menggunakan relative path dari file ini
# ─────────────────────────────────────────────────────────────────────────────
file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(file_dir))
system_flow_path = os.path.join(project_root, 'C. System Flow')
genetic_algorithm_path = file_dir

sys.path.insert(0, system_flow_path)
sys.path.insert(0, genetic_algorithm_path)

# Import dari system flow & GA dicky
from b_nutrition_service import NutritionService
from b_genetic_algorithm import run_ga_numpy, local_search, fitness

# ─────────────────────────────────────────────────────────────────────────────
# 2. KONFIGURASI PROFIL PENYAKIT (5 KASUS)
# ─────────────────────────────────────────────────────────────────────────────
_BASE = {
    'gender': 'M',
    'age': 45,
    'weight': 70.0,
    'height': 170.0,
    'activity_factor': 1.4,
    'food_preferences': ['Asian', 'Western']
}

PROFILES = [
    {**_BASE, 'disease': ['normal']},
    {**_BASE, 'disease': ['dm2']},
    {**_BASE, 'disease': ['hypertension']},
    {**_BASE, 'disease': ['cholesterol']},
    {**_BASE, 'disease': ['ckd']},
]

N_TRIALS = 1000

# ─────────────────────────────────────────────────────────────────────────────
# 3. SETUP DATA
# ─────────────────────────────────────────────────────────────────────────────
def setup_data(profile):
    service = NutritionService()
    result = service.calculate_nutrition_needs(profile)
    if not result['success']:
        raise RuntimeError(f"NutritionService error: {result.get('error')}")
    
    food_df = result['food_data']['dataframe']
    tdee = result['energy']['tdee']
    
    # Convert constraint format
    constraint_bag = result['guidelines']
    nutrients = constraint_bag.get('nutrients', constraint_bag)
    hard = {}
    soft = {}
    for nutrient, constraint in nutrients.items():
        if not isinstance(constraint, dict) or constraint.get('constraint_type') == 'unlimited' or nutrient == 'fruits_and_vegies_g':
            continue
        ndata = {
            'min': constraint.get('min', 0),
            'max': constraint.get('max', float('inf')),
            'unit': constraint.get('unit', '')
        }
        if constraint.get('hard_soft_type') == 'HARD':
            hard[nutrient] = ndata
        else:
            soft[nutrient] = ndata
    
    ga_guidelines = {'hard': hard, 'soft': soft}
    return food_df, ga_guidelines, tdee

# ─────────────────────────────────────────────────────────────────────────────
# 4. OPTUNA OBJECTIVE FUNCTION
# ─────────────────────────────────────────────────────────────────────────────
def make_objective(all_case_data):
    def objective(trial):
        # Hyperparameter search space
        pop_size = trial.suggest_int('pop_size', 50, 200, step=10)
        generations = trial.suggest_int('generations', 50, 300, step=10)
        elite_ratio = trial.suggest_float('elite_ratio', 0.05, 0.30, step=0.05)
        mutation_rate = trial.suggest_float('mutation_rate', 0.1, 0.6, step=0.05)
        ls_iterations = trial.suggest_int('ls_iterations', 10, 50, step=5)

        all_fitness = []
        
        for case_idx, (food_df, guidelines, tdee) in enumerate(all_case_data):
            try:
                # 1. Run GA Dicky
                best_solution, _ = run_ga_numpy(
                    food_df=food_df,
                    guidelines=guidelines,
                    tdee=tdee,
                    generations=generations,
                    pop_size=pop_size,
                    elite_ratio=elite_ratio,
                    mutation_rate=mutation_rate,
                    verbose=False
                )
                
                # Jika GA gagal
                if best_solution is None or len(best_solution) < 10:
                    all_fitness.append(999999)
                    continue
                    
                # 2. Local Search
                best_solution = local_search(
                    solution=best_solution,
                    food_df=food_df,
                    guidelines=guidelines,
                    tdee=tdee,
                    iterations=ls_iterations,
                    verbose=False
                )
                
                # 3. Hitung Final Fitness
                case_fitness = fitness(best_solution, guidelines, tdee=tdee)
                all_fitness.append(case_fitness)
                
            except Exception as e:
                print(f"[Error di kasus {case_idx}] {e}")
                all_fitness.append(999999)

        # Rata-rata fitness dari 5 penyakit
        mean_fitness = float(np.mean(all_fitness))
        return mean_fitness

    return objective

# ─────────────────────────────────────────────────────────────────────────────
# 5. MAIN EXECUTION
# ─────────────────────────────────────────────────────────────────────────────
def main():
    print("Loading data untuk 5 profil penyakit...")
    all_case_data = []
    for p in PROFILES:
        all_case_data.append(setup_data(p))
    print("Data loaded. Memulai Optuna Tuning...")

    study = optuna.create_study(direction='minimize', sampler=TPESampler(seed=42))

    # Tambahkan parameter existing sebagai baseline (Trial 0)
    study.enqueue_trial({
        'pop_size': 150,
        'generations': 270,
        'elite_ratio': 0.05,
        'mutation_rate': 0.55,
        'ls_iterations': 35
    })

    t_start = time.time()
    study.optimize(make_objective(all_case_data), n_trials=N_TRIALS)

    print(f"\nSelesai dalam {(time.time() - t_start)/60:.1f} menit.")
    print("\nBEST PARAMETERS:")
    print(study.best_params)
    print(f"BEST FITNESS SCORE: {study.best_value:.2f}")

    # Simpan ke CSV
    output_csv = os.path.join(genetic_algorithm_path, 'tuning_1000_trials_dicky.csv')
    df_results = study.trials_dataframe()
    df_results.to_csv(output_csv, index=False)
    print(f"Hasil disimpan ke {output_csv}")

    # Simpan best params ke JSON
    output_json = os.path.join(genetic_algorithm_path, 'best_params_dicky.json')
    with open(output_json, 'w') as f:
        json.dump(study.best_params, f, indent=2)
    print(f"Best parameters disimpan ke {output_json}")

if __name__ == '__main__':
    main()

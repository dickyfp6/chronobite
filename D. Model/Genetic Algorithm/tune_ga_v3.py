"""
TUNE GA V3 - Optuna Hyperparameter Tuning untuk ga_v3
========================================================================

Strategi:
  Mencari kombinasi hyperparameter GA terbaik (pop_size, generations, elite_ratio,
  mutation_rate, ls_iterations) melintasi 10 skenario profil penyakit sekaligus
  (campuran single, dual, dan triple disease) agar parameter yang ditemukan
  robust untuk semua kondisi, bukan hanya single disease.

Perubahan dari tune_ga_dicky.py:
  - Import dari ga_v3 (bukan ga_dicky)
  - Local search TIDAK dipanggil di objective (sudah di dalam run_ga_numpy ga_v3)
  - PROFILES diperluas dari 5 single disease → 10 profil (single + dual + triple)
  - N_TRIALS default 50 (cukup untuk Kaggle ~6-7 jam)
  - Baseline parameter diupdate ke Trial 5 (pop=110, gen=70, elite=0.10, mutation=0.25)

Cara pakai di Kaggle (setelah clone repo):
  python "D. Model/Genetic Algorithm/tune_ga_v3.py"

Output:
  - tuning_results_v3.csv  → semua trial results
  - best_params_v3.json    → best parameters untuk di-copy ke ga_config.py
"""

import sys
import os
import json
import time
import numpy as np
import pandas as pd
import optuna
from optuna.samplers import TPESampler
from optuna.pruners import MedianPruner

# ─────────────────────────────────────────────────────────────────────────────
# 1. PATH SETUP
# ─────────────────────────────────────────────────────────────────────────────
file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(file_dir))
system_flow_path = os.path.join(project_root, 'C. System Flow')
genetic_algorithm_path = file_dir

sys.path.insert(0, system_flow_path)
sys.path.insert(0, genetic_algorithm_path)

# Import dari ga_v3 (bukan ga_dicky)
from nutrition_service import NutritionService
from ga_v3 import run_ga_numpy, fitness
# Catatan: local_search TIDAK diimport karena sudah dipanggil
# di dalam run_ga_numpy di ga_v3

# ─────────────────────────────────────────────────────────────────────────────
# 2. KONFIGURASI PROFIL PENYAKIT (10 KASUS)
#    Campuran single (3) + dual (4) + triple (3)
#    Representatif untuk semua kondisi, bukan hanya single disease
# ─────────────────────────────────────────────────────────────────────────────

# Profil 1: Normal/Single disease — M/28th/68kg/178cm/Moderate
_BASE_1 = {
    'gender': 'M', 'age': 28, 'weight': 68.0, 'height': 178.0,
    'activity_factor': 1.845, 'food_preferences': []
}

# Profil 2: Dual disease — F/55th/83kg/162cm/Sedentary
_BASE_2 = {
    'gender': 'F', 'age': 55, 'weight': 83.0, 'height': 162.0,
    'activity_factor': 1.545, 'food_preferences': []
}

# Profil 3: Triple disease — M/34th/51kg/178cm/Vigorous
_BASE_3 = {
    'gender': 'M', 'age': 34, 'weight': 51.0, 'height': 178.0,
    'activity_factor': 2.2, 'food_preferences': []
}

PROFILES = [
    # Single disease (3 case) — profil 1
    {**_BASE_1, 'disease': ['normal']},
    {**_BASE_1, 'disease': ['dm2']},       # DM2 selalu jadi masalah di kombinasi
    {**_BASE_1, 'disease': ['ckd']},       # CKD constraint paling ketat

    # Dual disease (4 case) — profil 2
    {**_BASE_2, 'disease': ['dm2', 'hypertension']},      # CSR terrendah (72%)
    {**_BASE_2, 'disease': ['dm2', 'cholesterol']},       # CSR 77%
    {**_BASE_2, 'disease': ['hypertension', 'cvd']},      # CSR 92%
    {**_BASE_2, 'disease': ['ckd', 'hypertension']},      # CSR 78%

    # Triple disease (3 case) — profil 3
    {**_BASE_3, 'disease': ['dm2', 'hypertension', 'cholesterol']},   # CSR 68%
    {**_BASE_3, 'disease': ['ckd', 'dm2', 'hypertension']},           # CSR 89%
    {**_BASE_3, 'disease': ['hypertension', 'cholesterol', 'cvd']},   # CSR 100%
]

N_TRIALS = 50  # ~6-7 jam di Kaggle. Naikkan ke 100 kalau ada waktu lebih.


# ─────────────────────────────────────────────────────────────────────────────
# 3. SETUP DATA
# ─────────────────────────────────────────────────────────────────────────────
def setup_data(profile):
    """Load food_df, guidelines, dan tdee untuk satu profil."""
    service = NutritionService()
    result = service.calculate_nutrition_needs(profile)
    if not result['success']:
        raise RuntimeError(f"NutritionService error: {result.get('error')}")

    food_df = result['food_data']['dataframe']
    tdee = result['energy']['tdee']

    nutrients = result['guidelines'].get('nutrients', result['guidelines'])
    hard, soft = {}, {}
    for nutrient, constraint in nutrients.items():
        if not isinstance(constraint, dict):
            continue
        if constraint.get('constraint_type') == 'unlimited':
            continue
        if nutrient == 'fruits_and_vegies_g':
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
        # Search space hyperparameter
        pop_size     = trial.suggest_int  ('pop_size',     50,  200, step=10)
        generations  = trial.suggest_int  ('generations',  50,  200, step=10)
        elite_ratio  = trial.suggest_float('elite_ratio',  0.05, 0.25, step=0.05)
        mutation_rate= trial.suggest_float('mutation_rate',0.10, 0.50, step=0.05)
        ls_iterations= trial.suggest_int  ('ls_iterations',10,   50, step=5)

        all_fitness = []

        for case_idx, (food_df, guidelines, tdee) in enumerate(all_case_data):
            try:
                # Run GA — local_search sudah dipanggil di dalam run_ga_numpy (ga_v3)
                best_solution, _ = run_ga_numpy(
                    food_df=food_df,
                    guidelines=guidelines,
                    tdee=tdee,
                    generations=generations,
                    pop_size=pop_size,
                    elite_ratio=elite_ratio,
                    mutation_rate=mutation_rate,
                    ls_iterations=ls_iterations,  # dipass ke run_ga_numpy, diteruskan ke local_search
                    verbose=False,
                    deadline=None
                )

                if best_solution is None or len(best_solution) < 10:
                    all_fitness.append(999999)
                    continue

                # Hitung fitness akhir
                case_fitness = fitness(best_solution, guidelines, tdee=tdee)
                all_fitness.append(case_fitness)

            except Exception as e:
                print(f"  [Case {case_idx} error] {e}")
                all_fitness.append(999999)

        mean_fitness = float(np.mean(all_fitness))

        # Log progress tiap trial
        trial_num = trial.number + 1
        print(f"  Trial {trial_num:>3}/{N_TRIALS} | "
              f"pop={pop_size} gen={generations} elite={elite_ratio:.2f} "
              f"mut={mutation_rate:.2f} ls={ls_iterations} | "
              f"fitness={mean_fitness:.2f}")

        return mean_fitness

    return objective


# ─────────────────────────────────────────────────────────────────────────────
# 5. MAIN EXECUTION
# ─────────────────────────────────────────────────────────────────────────────
def main():
    print("=" * 70)
    print("TUNE GA V3 - Optuna Hyperparameter Tuning")
    print("=" * 70)
    print(f"Profil: {len(PROFILES)} cases (3 single + 4 dual + 3 triple disease)")
    print(f"Trials : {N_TRIALS}")
    print()

    print("Loading data untuk semua profil...")
    all_case_data = []
    for i, p in enumerate(PROFILES):
        disease_str = "_".join(p['disease'])
        print(f"  [{i+1}/{len(PROFILES)}] {disease_str}...")
        all_case_data.append(setup_data(p))
    print("Semua data berhasil diload.\n")

    # Buat study Optuna
    study = optuna.create_study(
        direction='minimize',
        sampler=TPESampler(seed=42),
        pruner=MedianPruner(n_startup_trials=5, n_warmup_steps=0)
    )

    # Enqueue baseline: Trial 5 (hasil tuning sebelumnya)
    study.enqueue_trial({
        'pop_size': 110,
        'generations': 70,
        'elite_ratio': 0.10,
        'mutation_rate': 0.25,
        'ls_iterations': 30
    })

    print("Memulai Optuna Tuning...")
    print("-" * 70)
    t_start = time.time()
    study.optimize(make_objective(all_case_data), n_trials=N_TRIALS)
    elapsed = time.time() - t_start

    # ── Hasil ──
    print("\n" + "=" * 70)
    print(f"Selesai dalam {elapsed/60:.1f} menit ({elapsed/3600:.2f} jam)")
    print("\nBEST PARAMETERS:")
    for k, v in study.best_params.items():
        print(f"  {k:<20} = {v}")
    print(f"\nBEST FITNESS SCORE: {study.best_value:.4f}")
    print(f"BEST TRIAL       : #{study.best_trial.number + 1}")

    # ── Simpan hasil ──
    output_csv = os.path.join(genetic_algorithm_path, 'tuning_results_v3.csv')
    study.trials_dataframe().to_csv(output_csv, index=False)
    print(f"\nSemua trial disimpan ke: {output_csv}")

    output_json = os.path.join(genetic_algorithm_path, 'best_params_v3.json')
    with open(output_json, 'w') as f:
        json.dump(study.best_params, f, indent=2)
    print(f"Best parameters disimpan ke: {output_json}")

    # ── Instruksi update ga_config.py ──
    print("\n" + "=" * 70)
    print("LANGKAH SELANJUTNYA:")
    print("Update GA_PARAMS dan LS_PARAMS di ga_config.py dengan nilai berikut:")
    print()
    print("GA_PARAMS = {")
    print(f"    'pop_size'    : {study.best_params['pop_size']},")
    print(f"    'generations' : {study.best_params['generations']},")
    print(f"    'elite_ratio' : {study.best_params['elite_ratio']},")
    print(f"    'mutation_rate': {study.best_params['mutation_rate']},")
    print("}")
    print()
    print("LS_PARAMS = {")
    print(f"    'ls_iterations': {study.best_params['ls_iterations']},")
    print("}")
    print("=" * 70)


if __name__ == '__main__':
    main()
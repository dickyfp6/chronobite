"""
TUNE KAGGLE DICKY - Optuna Hyperparameter Tuning untuk GA + Local Search (Versi Numpy)
====================================================================================

Tuning ini dikhususkan untuk kasus MULTI CONSTRAINT paling berat:
CKD + DM2 + Hypertension

Menargetkan parameter terbaik dengan constraint waktu eksekusi < 60 detik.
"""

import sys
import os
import json
import time
import numpy as np
import pandas as pd
import optuna
from optuna.samplers import NSGAIISampler

# PATH SETUP
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(project_root, 'C. System Flow'))
sys.path.insert(0, os.path.join(project_root, 'D. Model', 'Genetic Algorithm'))

from ga_dicky import run_ga_numpy as run_ga, local_search, calculate_total_nutrition_from_portions, fitness as ga_fitness
from b_nutrition_service import NutritionService

# KONFIGURASI TUNING
_BASE = {
    'gender': 'M',
    'age': 45,
    'weight': 70.0,
    'height': 175.0,
    'activity_factor': 1.4,
    'food_preferences': ['Asian', 'Western']
}

# 1 kasus PALING BERAT (Multi constraint)
TUNING_PROFILES = [
    {**_BASE, 'disease': ['ckd', 'dm2', 'hypertension']}, # CKD + DM2 + HT (Paling banyak hard constraint)
]

# Total Trial (bisa dinaikkan di Kaggle jadi 100-200)
N_TRIALS = 150
N_RUNS_PER_TRIAL = 1

def calculate_csr(solution: pd.DataFrame, guidelines: dict) -> float:
    hard_constraints = guidelines.get('hard', {})
    if not hard_constraints:
        return 0.0

    total_nutrition = calculate_total_nutrition_from_portions(solution)

    passed = 0
    total = 0

    for nutrient, constraint in hard_constraints.items():
        if constraint.get('constraint_type') == 'unlimited':
            continue
        
        # Mapping untuk keys di total_nutrition vs keys di guidelines
        HARD_NUTRIENT_KEY_MAP = {
            'energy':        ['energy_kcal', 'calories', 'energy'],
            'protein':       ['protein_g', 'protein'],
            'fat':           ['fat_g', 'total_fat_g', 'fat'],
            'carbohydrate':  ['carbohydrate_g', 'carbs_g', 'carbohydrate'],
            'sodium':        ['sodium_mg', 'sodium'],
            'sugar':         ['sugar_g', 'total_sugar_g', 'sugars_g'],
            'cholesterol':   ['cholesterol_mg', 'cholesterol'],
        }
        
        # Lookup 
        candidates = HARD_NUTRIENT_KEY_MAP.get(nutrient, [nutrient])
        actual = None
        for candidate in candidates:
            if candidate in total_nutrition:
                actual = total_nutrition[candidate]
                break
                
        if actual is None:
            continue

        total += 1
        min_val = constraint.get('min') or 0
        max_val = constraint.get('max') or float('inf')

        if min_val <= actual <= max_val:
            passed += 1

    if total == 0:
        return 0.0

    return (passed / total) * 100.0

def setup_data(profile: dict):
    service = NutritionService()
    result = service.calculate_nutrition_needs(profile)

    if not result['success']:
        raise RuntimeError(f"NutritionService failed: {result.get('error')}")

    food_df = result['food_data']['dataframe']
    guidelines_all = result['guidelines']['nutrients']
    tdee = result['energy']['tdee']

    guidelines = {
        'hard': {k: v for k, v in guidelines_all.items() if v.get('hard_soft_type') == 'HARD'},
        'soft': {k: v for k, v in guidelines_all.items() if v.get('hard_soft_type') != 'HARD'},
    }

    return food_df, guidelines, tdee


def make_objective(all_case_data: list):
    def objective(trial: optuna.Trial):
        pop_size      = trial.suggest_int('pop_size', 50, 300, step=10)
        generations   = trial.suggest_int('generations', 50, 400, step=10)
        elite_ratio   = trial.suggest_float('elite_ratio', 0.05, 0.30, step=0.05)
        mutation_rate = trial.suggest_float('mutation_rate', 0.1, 0.6, step=0.05)
        ls_iterations = trial.suggest_int('ls_iterations', 10, 80, step=5)

        all_fitness = []
        all_csr     = []
        all_time    = []

        for case_idx, (food_df, guidelines, tdee) in enumerate(all_case_data):
            for run_idx in range(N_RUNS_PER_TRIAL):
                try:
                    t_start = time.time()
                    best_solution, _ = run_ga(
                        food_df=food_df,
                        guidelines=guidelines,
                        tdee=tdee,
                        generations=generations,
                        pop_size=pop_size,
                        elite_ratio=elite_ratio,
                        mutation_rate=mutation_rate,
                        verbose=False
                    )

                    if best_solution is None or len(best_solution) < 10:
                        all_fitness.append(999_999)
                        all_csr.append(0.0)
                        all_time.append(time.time() - t_start)
                        continue

                    best_solution = local_search(
                        solution=best_solution,
                        food_df=food_df,
                        guidelines=guidelines,
                        tdee=tdee,
                        iterations=ls_iterations,
                        verbose=False
                    )
                    
                    elapsed = time.time() - t_start

                    fit = ga_fitness(best_solution, guidelines, tdee=tdee)
                    csr = calculate_csr(best_solution, guidelines)

                    all_fitness.append(fit)
                    all_csr.append(csr)
                    all_time.append(elapsed)

                except Exception as e:
                    print(f"  [Trial {trial.number} case {case_idx} run {run_idx}] ERROR: {e}")
                    all_fitness.append(999_999)
                    all_csr.append(0.0)
                    all_time.append(60.0)

        mean_fitness = float(np.mean(all_fitness))
        mean_csr     = float(np.mean(all_csr))
        mean_time    = float(np.mean(all_time))

        trial.set_user_attr('mean_fitness', mean_fitness)
        trial.set_user_attr('mean_csr',     mean_csr)
        trial.set_user_attr('mean_time',    mean_time)
        trial.set_user_attr('std_fitness',  float(np.std(all_fitness)))
        trial.set_user_attr('std_csr',      float(np.std(all_csr)))

        # Waktu penalti (jika > 60s, fitness makin buruk supaya optuna menghindarinya)
        penalty_fitness = mean_fitness
        if mean_time > 60.0:
            penalty_fitness += 100000 * (mean_time - 60.0) # Besar penalti

        print(
            f"  Trial {trial.number:3d} | "
            f"pop={pop_size:3d} gen={generations:3d} elite={elite_ratio:.2f} "
            f"mut={mutation_rate:.2f} ls={ls_iterations:2d} | "
            f"fitness={mean_fitness:10.1f} CSR={mean_csr:5.1f}% TIME={mean_time:5.1f}s"
        )

        return penalty_fitness, -mean_csr

    return objective

def save_results(study: optuna.Study, output_dir: str = "."):
    os.makedirs(output_dir, exist_ok=True)

    rows = []
    for t in study.trials:
        if t.state != optuna.trial.TrialState.COMPLETE:
            continue
        row = {
            'trial':         t.number,
            'pop_size':      t.params.get('pop_size'),
            'generations':   t.params.get('generations'),
            'elite_ratio':   t.params.get('elite_ratio'),
            'mutation_rate': t.params.get('mutation_rate'),
            'ls_iterations': t.params.get('ls_iterations'),
            'fitness':       t.user_attrs.get('mean_fitness'),
            'csr_pct':       t.user_attrs.get('mean_csr'),
            'time_s':        t.user_attrs.get('mean_time'),
            'is_pareto':     t in study.best_trials,
        }
        rows.append(row)

    df = pd.DataFrame(rows)
    csv_path = os.path.join(output_dir, 'tune_kaggle_results.csv')
    df.to_csv(csv_path, index=False)
    print(f"\n✓ Semua hasil disimpan: {csv_path}")

    # Pareto-optimal trials yang waktunya < 65s (kasih toleransi sedikit)
    valid_pareto = [t for t in study.best_trials if t.user_attrs.get('mean_time', 999) < 65.0]
    
    if not valid_pareto:
        print("\n[WARNING] Tidak ada Pareto optimal yang < 65 detik. Menggunakan semua Pareto.")
        valid_pareto = study.best_trials

    print(f"\n{'='*80}")
    print(f"PARETO-OPTIMAL TRIALS (Waktu < 65s) - {len(valid_pareto)} solusi:")
    print(f"{'='*80}")
    print(f"  {'Trial':>5}  {'pop':>4}  {'gen':>4}  {'elite':>5}  {'mut':>5}  {'ls':>3}  {'fitness':>12}  {'CSR':>7}  {'TIME':>6}")
    print(f"  {'-'*78}")

    best_params_list = []
    for t in sorted(valid_pareto, key=lambda x: x.user_attrs.get('mean_csr', 0), reverse=True):
        fit  = t.user_attrs.get('mean_fitness', 0)
        csr  = t.user_attrs.get('mean_csr', 0)
        time_s = t.user_attrs.get('mean_time', 0)
        print(
            f"  {t.number:5d}  "
            f"{t.params['pop_size']:4d}  "
            f"{t.params['generations']:4d}  "
            f"{t.params['elite_ratio']:5.2f}  "
            f"{t.params['mutation_rate']:5.2f}  "
            f"{t.params['ls_iterations']:3d}  "
            f"{fit:12.1f}  "
            f"{csr:6.1f}%  "
            f"{time_s:5.1f}s"
        )
        best_params_list.append({
            'trial': t.number,
            'params': t.params,
            'mean_fitness': fit,
            'mean_csr': csr,
            'mean_time': time_s
        })

    if valid_pareto:
        best = max(valid_pareto, key=lambda t: t.user_attrs.get('mean_csr', 0))
        best_params = {
            'pop_size':      best.params['pop_size'],
            'generations':   best.params['generations'],
            'elite_ratio':   best.params['elite_ratio'],
            'mutation_rate': best.params['mutation_rate'],
            'ls_iterations': best.params['ls_iterations'],
            '_trial_number': best.number,
            '_mean_fitness': best.user_attrs.get('mean_fitness'),
            '_mean_csr':     best.user_attrs.get('mean_csr'),
            '_mean_time':    best.user_attrs.get('mean_time'),
            '_note': 'Dipilih berdasarkan CSR tertinggi dengan waktu < 65s',
        }

        json_path = os.path.join(output_dir, 'best_kaggle_params.json')
        with open(json_path, 'w') as f:
            json.dump(best_params, f, indent=2)
        print(f"\n✓ Best params disimpan: {json_path}")

        print(f"\n{'='*80}")
        print("REKOMENDASI PARAMETER (CSR tertinggi, Waktu < 65s):")
        print(f"{'='*80}")
        print(f"  pop_size      = {best_params['pop_size']}")
        print(f"  generations   = {best_params['generations']}")
        print(f"  elite_ratio   = {best_params['elite_ratio']}")
        print(f"  mutation_rate = {best_params['mutation_rate']}")
        print(f"  ls_iterations = {best_params['ls_iterations']}")
        print(f"\n  → Fitness: {best_params['_mean_fitness']:.1f} | CSR: {best_params['_mean_csr']:.1f}% | Waktu: {best_params['_mean_time']:.1f}s")
        print(f"\n  Copy parameter di atas ke ga_config.py")
        print(f"{'='*80}")

def main():
    case_labels = [p['disease'] for p in TUNING_PROFILES]
    est_minutes = N_TRIALS * len(TUNING_PROFILES) * N_RUNS_PER_TRIAL

    print("=" * 80)
    print("KAGGLE TUNING GA DICKY — Maximize CSR, Time < 60s")
    print("=" * 80)
    for i, label in enumerate(case_labels):
        print(f"Kasus {i+1}      : {label}")
    print(f"Jumlah trial : {N_TRIALS}")
    print(f"Estimasi waktu: ~{est_minutes} menit")
    print("=" * 80)

    print("\n[SETUP] Loading kasus...")
    all_case_data = []
    for i, profile in enumerate(TUNING_PROFILES):
        print(f"  Kasus {i+1}: {profile['disease']}")
        food_df, guidelines, tdee = setup_data(profile)
        print(f"    ✓ {len(food_df)} foods | {len(guidelines['hard'])} HARD constraints | TDEE {tdee:.0f} kcal")
        all_case_data.append((food_df, guidelines, tdee))

    sampler = NSGAIISampler(seed=42)
    study = optuna.create_study(
        directions=['minimize', 'minimize'],   # (fitness↓, -CSR↓)
        sampler=sampler,
        study_name='kaggle_ga_tuning'
    )

    optuna.logging.set_verbosity(optuna.logging.WARNING)
    objective = make_objective(all_case_data)
    
    # Masukkan config yg dipakai sekarang sebagai start
    from ga_config import GA_PARAMS, LS_PARAMS
    EXISTING_PARAMS = {
        'pop_size': GA_PARAMS.get('pop_size', 110),
        'generations': GA_PARAMS.get('generations', 70),
        'elite_ratio': GA_PARAMS.get('elite_ratio', 0.10),
        'mutation_rate': GA_PARAMS.get('mutation_rate', 0.25),
        'ls_iterations': LS_PARAMS.get('iterations', 30),
    }
    study.enqueue_trial(EXISTING_PARAMS)
    print(f"[INFO] Warm start dengan parameter eksisting: {EXISTING_PARAMS}")

    print(f"\n[TUNING] Mulai {N_TRIALS} trials...\n")
    t_start = time.time()

    study.optimize(objective, n_trials=N_TRIALS + 1)

    elapsed = time.time() - t_start
    print(f"\n✓ Selesai dalam {elapsed/60:.1f} menit")

    output_dir = os.path.dirname(os.path.abspath(__file__))
    save_results(study, output_dir=output_dir)

if __name__ == '__main__':
    main()

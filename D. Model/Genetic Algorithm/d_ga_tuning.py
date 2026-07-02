"""
d_ga_tuning.py — Optuna Hyperparameter Tuning GA + LS
======================================================
Objective  : Memaksimalkan CSR (Constraint Satisfaction Rate) — bukan fitness score
Interface  : c_ga_interface (identik dengan evaluasi 26 profil)
Profil     : 13 kasus yang divalidasi ahli gizi
N Trials   : 100

Cara pakai di Kaggle:
  python "D. Model/Genetic Algorithm/d_ga_tuning.py"
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
file_dir     = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(file_dir))
sys.path.insert(0, os.path.join(project_root, 'C. System Flow'))
sys.path.insert(0, os.path.join(project_root, 'D. Model'))
sys.path.insert(0, file_dir)

import a_ga_parameter as ga_param                           # type: ignore
from b_nutrition_service import NutritionService            # type: ignore
from c_ga_interface import GeneticAlgorithmInterface        # type: ignore

# ─────────────────────────────────────────────────────────────────────────────
# 2. PROFIL — 13 kasus yang divalidasi ahli gizi
# ─────────────────────────────────────────────────────────────────────────────
_BASE = {
    'gender': 'M',
    'age': 45,
    'weight': 70.0,
    'height': 175.0,
    'activity_factor': 1.4,
}

PROFILES = [
    {**_BASE, 'name': 'Normal',                                   'disease': ['normal']},
    {**_BASE, 'name': 'Diabetes Melitus Tipe 2',                  'disease': ['dm2']},
    {**_BASE, 'name': 'Hipertensi',                               'disease': ['hypertension']},
    {**_BASE, 'name': 'Penyakit Kardiovaskular',                  'disease': ['cvd']},
    {**_BASE, 'name': 'Hiperkolesterolemia',                      'disease': ['cholesterol']},
    {**_BASE, 'name': 'Penyakit Ginjal Kronis',                   'disease': ['ckd']},
    {**_BASE, 'name': 'DM2 + Hipertensi',                        'disease': ['dm2', 'hypertension']},
    {**_BASE, 'name': 'DM2 + Hiperkolesterolemia',               'disease': ['dm2', 'cholesterol']},
    {**_BASE, 'name': 'Hipertensi + CVD',                        'disease': ['hypertension', 'cvd']},
    {**_BASE, 'name': 'CKD + Hipertensi',                        'disease': ['ckd', 'hypertension']},
    {**_BASE, 'name': 'DM2 + Hipertensi + Hiperkolesterolemia',  'disease': ['dm2', 'hypertension', 'cholesterol']},
    {**_BASE, 'name': 'CKD + DM2 + Hipertensi',                 'disease': ['ckd', 'dm2', 'hypertension']},
    {**_BASE, 'name': 'Hipertensi + Hiperkolesterolemia + CVD',  'disease': ['hypertension', 'cholesterol', 'cvd']},
]

N_TRIALS = 100

# ─────────────────────────────────────────────────────────────────────────────
# 3. SETUP DATA — preload semua profil sekali saja
# ─────────────────────────────────────────────────────────────────────────────
def preload_all(profiles):
    service = NutritionService()
    all_data = []
    for p in profiles:
        result = service.calculate_nutrition_needs(p)
        if not result['success']:
            raise RuntimeError(f"NutritionService error untuk {p['name']}: {result.get('error')}")
        all_data.append({
            'profile':    p,
            'tdee':       result['energy']['tdee'],           # type: ignore
            'guidelines': result['guidelines'],               # type: ignore
            'food_df':    result['food_data']['dataframe'],   # type: ignore
        })
    return all_data

# ─────────────────────────────────────────────────────────────────────────────
# 4. HITUNG CSR — identik dengan ga_evaluation_26.py
# ─────────────────────────────────────────────────────────────────────────────
def compute_csr(menu_plan, guideline_nutrients):
    """Hitung CSR HARD constraints only, identik dengan ga_evaluation_26.py"""
    if not menu_plan:
        return 0.0

    MACRO_MAP = {
        'energy_kcal':    menu_plan.total_daily_calories,
        'protein_g':      menu_plan.total_daily_protein_g,
        'carbohydrate_g': menu_plan.total_daily_carb_g,
        'fat_g':          menu_plan.total_daily_fat_g,
    }
    if hasattr(menu_plan, 'daily_micronutrients') and menu_plan.daily_micronutrients:
        MACRO_MAP.update(menu_plan.daily_micronutrients)

    passed = 0
    total  = 0
    for nutrient, limits in guideline_nutrients.items():
        if limits.get('hard_soft_type') != 'HARD':
            continue
        if nutrient not in MACRO_MAP:
            continue
        total += 1
        actual = MACRO_MAP[nutrient]
        if limits.get('min', 0) <= actual <= limits.get('max', float('inf')):
            passed += 1

    return (passed / total * 100) if total > 0 else 100.0

# ─────────────────────────────────────────────────────────────────────────────
# 5. OBJECTIVE FUNCTION
# ─────────────────────────────────────────────────────────────────────────────
def make_objective(all_data):
    def objective(trial):
        # Search space
        pop_size      = trial.suggest_int('pop_size',      50,  250, step=10)
        generations   = trial.suggest_int('generations',   50,  300, step=10)
        elite_ratio   = trial.suggest_float('elite_ratio', 0.05, 0.40, step=0.05)
        mutation_rate = trial.suggest_float('mutation_rate', 0.10, 0.70, step=0.05)
        ls_iterations = trial.suggest_int('ls_iterations', 10,  80,  step=5)

        # Override GA_PARAMS sementara untuk trial ini
        ga_param.GA_PARAMS['pop_size']      = pop_size
        ga_param.GA_PARAMS['generations']   = generations
        ga_param.GA_PARAMS['elite_ratio']   = elite_ratio
        ga_param.GA_PARAMS['mutation_rate'] = mutation_rate
        ga_param.LS_PARAMS['iterations']    = ls_iterations

        csr_list = []

        for case_idx, data in enumerate(all_data):
            try:
                profile    = data['profile']
                tdee       = data['tdee']
                guidelines = data['guidelines']
                food_df    = data['food_df']

                guideline_nutrients = guidelines.get('nutrients', {})

                # Jalankan GA via c_ga_interface (identik dengan evaluasi)
                ga_engine = GeneticAlgorithmInterface(food_df, guidelines)
                menu_plan = ga_engine.generate_menu_plan(profile, tdee)

                csr = compute_csr(menu_plan, guideline_nutrients)
                csr_list.append(csr)

            except Exception as e:
                print(f"  [Error {data['profile']['name']}] {e}")
                csr_list.append(0.0)

            # Pruning intermediate
            trial.report(100.0 - float(np.mean(csr_list)), step=case_idx)
            if trial.should_prune():
                raise optuna.exceptions.TrialPruned()

        mean_csr = float(np.mean(csr_list))
        print(f"  Trial {trial.number} selesai | mean CSR: {mean_csr:.2f}%")
        return 100.0 - mean_csr   # minimize (100 - CSR) = maximize CSR

    return objective

# ─────────────────────────────────────────────────────────────────────────────
# 6. MAIN
# ─────────────────────────────────────────────────────────────────────────────
def main():
    print("=" * 65)
    print("  OPTUNA TUNING — Objective: Maximize CSR via c_ga_interface")
    print("=" * 65)
    print(f"Profil : {len(PROFILES)} kasus")
    print(f"Trials : {N_TRIALS}")
    print("=" * 65)

    print("\nPreloading data semua profil...")
    all_data = preload_all(PROFILES)
    print(f"OK — {len(all_data)} profil siap.\n")

    study = optuna.create_study(
        direction='minimize',   # minimize (100 - CSR) = maximize CSR
        sampler=TPESampler(seed=42),
        pruner=MedianPruner(n_startup_trials=10, n_warmup_steps=3),
    )

    # Baseline — parameter aktif saat ini
    study.enqueue_trial({
        'pop_size':      200,
        'generations':   150,
        'elite_ratio':   0.30,
        'mutation_rate': 0.40,
        'ls_iterations': 60,
    })

    t_start = time.time()
    study.optimize(make_objective(all_data), n_trials=N_TRIALS)
    elapsed = (time.time() - t_start) / 60

    print(f"\nSelesai dalam {elapsed:.1f} menit.")

    best = study.best_params
    best_csr = 100.0 - study.best_value
    print(f"\nBEST PARAMETERS (Trial {study.best_trial.number}) — CSR: {best_csr:.2f}%:")
    for k, v in best.items():
        print(f"  {k}: {v}")

    # Simpan CSV semua trial
    output_csv = os.path.join(file_dir, 'tuning_results_v4.csv')
    study.trials_dataframe().to_csv(output_csv, index=False)
    print(f"\nHasil semua trial : {output_csv}")

    # Simpan best params ke JSON
    output_json = os.path.join(file_dir, 'best_params_v4.json')
    with open(output_json, 'w') as f:
        json.dump({**best, 'mean_csr': round(best_csr, 2)}, f, indent=2)
    print(f"Best params JSON  : {output_json}")

    # Print top 5
    print("\nTOP 5 TRIAL:")
    print(f"{'Trial':>6} | {'CSR':>8} | {'pop':>5} | {'gen':>5} | {'elite':>6} | {'mut':>5} | {'ls':>4}")
    print("-" * 55)
    top5 = sorted(
        [t for t in study.trials if t.value is not None],
        key=lambda t: t.value or 999999
    )[:5]
    for t in top5:
        p = t.params
        print(f"{t.number:>6} | {100-(t.value or 0):>7.2f}% | "              f"{p.get('pop_size','-'):>5} | {p.get('generations','-'):>5} | "
              f"{p.get('elite_ratio','-'):>6.2f} | {p.get('mutation_rate','-'):>5.2f} | "
              f"{p.get('ls_iterations','-'):>4}")

    # Print panduan update a_ga_parameter.py
    print("\n" + "=" * 65)
    print("  UPDATE a_ga_parameter.py dengan parameter berikut:")
    print("=" * 65)
    print(f"GA_PARAMS = {{")
    print(f"    \"generations\":   {best['generations']},")
    print(f"    \"pop_size\":      {best['pop_size']},")
    print(f"    \"elite_ratio\":   {best['elite_ratio']},")
    print(f"    \"mutation_rate\": {best['mutation_rate']},")
    print(f"}}")
    print(f"LS_PARAMS = {{\"iterations\": {best['ls_iterations']}}}")


if __name__ == '__main__':
    main()
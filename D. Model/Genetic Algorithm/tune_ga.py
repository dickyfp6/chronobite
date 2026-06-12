"""
TUNE GA - Optuna Hyperparameter Tuning untuk GA + Local Search
==============================================================

Strategi: 2-stage tuning
  Stage 1: Cari parameter terbaik di 1 kasus representatif (cepat ~30 menit)
  Stage 2: Validasi parameter terbaik di semua 13 kasus (jalankan test_ga.py)

Cara pakai:
  python tune_ga.py

Output:
  - tune_results.csv  : semua trial hasil tuning
  - best_params.json  : parameter terbaik yang bisa di-copy ke ga_interface.py
"""

import sys
import os
import json
import time
import random
import numpy as np
import pandas as pd
import optuna
from optuna.samplers import NSGAIISampler

# ─────────────────────────────────────────────────────────────────────────────
# PATH SETUP — sesuaikan dengan struktur folder kamu
# ─────────────────────────────────────────────────────────────────────────────
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
system_flow_path = os.path.join(project_root, 'C. System Flow')
genetic_algorithm_path = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, system_flow_path)
sys.path.insert(0, genetic_algorithm_path)

# ─────────────────────────────────────────────────────────────────────────────
# IMPORT
# ─────────────────────────────────────────────────────────────────────────────
from ga_v1 import run_ga, local_search, fitness, calculate_total_nutrition
from nutrition_service import NutritionService

# ─────────────────────────────────────────────────────────────────────────────
# KONFIGURASI TUNING
# Ubah di sini sesuai kebutuhan kamu
# ─────────────────────────────────────────────────────────────────────────────

# Base demographic — sama untuk semua kasus (isolasi variabel penyakit)
_BASE = {
    'gender': 'M',
    'age': 45,
    'weight': 70.0,
    'height': 175.0,
    'activity_factor': 1.4,
    'food_preferences': ['Asian', 'Western']
}

# 3 kasus representatif — cover semua 5 penyakit
TUNING_PROFILES = [
    {**_BASE, 'disease': ['normal']},                              # baseline
    {**_BASE, 'disease': ['dm2', 'hypertension', 'cholesterol']}, # DM2 + HT + Chol
    {**_BASE, 'disease': ['ckd', 'hypertension', 'cvd']},         # CKD + HT + CVD
]

# Jumlah trial Optuna
N_TRIALS = 15

# Jumlah run GA per trial per kasus (noise diredam oleh avg 3 kasus)
N_RUNS_PER_TRIAL = 1

def calculate_csr(solution: pd.DataFrame, guidelines: dict) -> float:
    """
    Hitung CS Rate (CSR) dari HARD constraints saja.
    Pakai calculate_total_nutrition() dari ga_v1 — konsisten dengan GA fitness.
    """
    hard_constraints = guidelines.get('hard', {})
    if not hard_constraints:
        return 0.0

    total_nutrition = calculate_total_nutrition(solution)

    passed = 0
    total = 0

    for nutrient, constraint in hard_constraints.items():
        if constraint.get('constraint_type') == 'unlimited':
            continue
        if nutrient not in total_nutrition:
            continue

        total += 1
        actual = total_nutrition[nutrient]
        min_val = constraint.get('min') or 0
        max_val = constraint.get('max') or float('inf')

        if min_val <= actual <= max_val:
            passed += 1

    if total == 0:
        return 0.0

    return (passed / total) * 100.0


def setup_data(profile: dict):
    """
    Inisialisasi NutritionService dan ambil food_df, guidelines, tdee.
    """
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


# ─────────────────────────────────────────────────────────────────────────────
# OBJECTIVE FUNCTION
# Dipanggil oleh Optuna setiap trial
# ─────────────────────────────────────────────────────────────────────────────

def make_objective(all_case_data: list):
    """
    Factory: buat objective function dengan semua kasus yang sudah di-load.
    Setiap trial dijalankan di semua kasus, hasilnya di-average.
    """
    def objective(trial: optuna.Trial):
        # ── Search space parameter ──────────────────────────────────────────
        pop_size      = trial.suggest_int  ('pop_size',      50,   150,  step=10)
        generations   = trial.suggest_int  ('generations',   50,   200,  step=10)
        elite_ratio   = trial.suggest_float('elite_ratio',   0.05, 0.25, step=0.05)
        mutation_rate = trial.suggest_float('mutation_rate', 0.1,  0.5,  step=0.05)
        ls_iterations = trial.suggest_int  ('ls_iterations', 10,   50,   step=5)

        all_fitness = []
        all_csr     = []

        # Loop semua kasus
        for case_idx, (food_df, guidelines, tdee) in enumerate(all_case_data):
            for run_idx in range(N_RUNS_PER_TRIAL):
                try:
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
                        continue

                    best_solution = local_search(
                        solution=best_solution,
                        food_df=food_df,
                        guidelines=guidelines,
                        tdee=tdee,
                        iterations=ls_iterations,
                        verbose=False
                    )

                    fit = fitness(best_solution, guidelines, tdee=tdee)
                    csr = calculate_csr(best_solution, guidelines)

                    all_fitness.append(fit)
                    all_csr.append(csr)

                except Exception as e:
                    print(f"  [Trial {trial.number} case {case_idx} run {run_idx}] ERROR: {e}")
                    all_fitness.append(999_999)
                    all_csr.append(0.0)

        mean_fitness = float(np.mean(all_fitness))
        mean_csr     = float(np.mean(all_csr))

        trial.set_user_attr('mean_fitness', mean_fitness)
        trial.set_user_attr('mean_csr',     mean_csr)
        trial.set_user_attr('std_fitness',  float(np.std(all_fitness)))
        trial.set_user_attr('std_csr',      float(np.std(all_csr)))

        print(
            f"  Trial {trial.number:3d} | "
            f"pop={pop_size:3d} gen={generations:3d} elite={elite_ratio:.2f} "
            f"mut={mutation_rate:.2f} ls={ls_iterations:2d} | "
            f"fitness={mean_fitness:10.1f}  CSR={mean_csr:5.1f}%"
        )

        return mean_fitness, -mean_csr

    return objective


# ─────────────────────────────────────────────────────────────────────────────
# SIMPAN HASIL
# ─────────────────────────────────────────────────────────────────────────────

def save_results(study: optuna.Study, output_dir: str = "."):
    """Simpan semua trial ke CSV dan best params ke JSON."""
    os.makedirs(output_dir, exist_ok=True)

    # ── Semua trial → CSV ───────────────────────────────────────────────────
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
            'std_fitness':   t.user_attrs.get('std_fitness'),
            'std_csr':       t.user_attrs.get('std_csr'),
            'is_pareto':     t in study.best_trials,
        }
        rows.append(row)

    df = pd.DataFrame(rows)
    csv_path = os.path.join(output_dir, 'tune_results.csv')
    df.to_csv(csv_path, index=False)
    print(f"\n✓ Semua hasil disimpan: {csv_path}")

    # ── Pareto-optimal trials ───────────────────────────────────────────────
    pareto_trials = study.best_trials
    print(f"\n{'='*70}")
    print(f"PARETO-OPTIMAL TRIALS ({len(pareto_trials)} solusi):")
    print(f"{'='*70}")
    print(f"  {'Trial':>5}  {'pop':>4}  {'gen':>4}  {'elite':>5}  {'mut':>5}  {'ls':>3}  {'fitness':>12}  {'CSR':>7}")
    print(f"  {'-'*65}")

    best_params_list = []
    for t in sorted(pareto_trials, key=lambda x: x.user_attrs.get('mean_csr', 0), reverse=True):
        fit = t.user_attrs.get('mean_fitness', 0)
        csr = t.user_attrs.get('mean_csr', 0)
        print(
            f"  {t.number:5d}  "
            f"{t.params['pop_size']:4d}  "
            f"{t.params['generations']:4d}  "
            f"{t.params['elite_ratio']:5.2f}  "
            f"{t.params['mutation_rate']:5.2f}  "
            f"{t.params['ls_iterations']:3d}  "
            f"{fit:12.1f}  "
            f"{csr:6.1f}%"
        )
        best_params_list.append({
            'trial': t.number,
            'params': t.params,
            'mean_fitness': fit,
            'mean_csr': csr,
        })

    # ── Rekomendasi: pilih pareto trial dengan CSR tertinggi ────────────────
    best = max(pareto_trials, key=lambda t: t.user_attrs.get('mean_csr', 0))
    best_params = {
        'pop_size':      best.params['pop_size'],
        'generations':   best.params['generations'],
        'elite_ratio':   best.params['elite_ratio'],
        'mutation_rate': best.params['mutation_rate'],
        'ls_iterations': best.params['ls_iterations'],
        '_trial_number': best.number,
        '_mean_fitness': best.user_attrs.get('mean_fitness'),
        '_mean_csr':     best.user_attrs.get('mean_csr'),
        '_note': 'Dipilih dari Pareto front berdasarkan CSR tertinggi',
    }

    json_path = os.path.join(output_dir, 'best_params.json')
    with open(json_path, 'w') as f:
        json.dump(best_params, f, indent=2)
    print(f"\n✓ Best params disimpan: {json_path}")

    print(f"\n{'='*70}")
    print("REKOMENDASI PARAMETER (CSR tertinggi dari Pareto front):")
    print(f"{'='*70}")
    print(f"  pop_size      = {best_params['pop_size']}")
    print(f"  generations   = {best_params['generations']}")
    print(f"  elite_ratio   = {best_params['elite_ratio']}")
    print(f"  mutation_rate = {best_params['mutation_rate']}")
    print(f"  ls_iterations = {best_params['ls_iterations']}")
    print(f"\n  → Fitness: {best_params['_mean_fitness']:.1f}  |  CSR: {best_params['_mean_csr']:.1f}%")
    print(f"\n  Copy parameter di atas ke ga_interface.py → generate_menu_plan()")
    print(f"{'='*70}")

    return best_params


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    case_labels = [p['disease'] for p in TUNING_PROFILES]
    est_minutes = N_TRIALS * len(TUNING_PROFILES) * N_RUNS_PER_TRIAL

    print("=" * 70)
    print("OPTUNA HYPERPARAMETER TUNING — GA + Local Search")
    print("=" * 70)
    for i, label in enumerate(case_labels):
        print(f"Kasus {i+1}      : {label}")
    print(f"Jumlah trial : {N_TRIALS}")
    print(f"Runs/trial   : {N_RUNS_PER_TRIAL} per kasus")
    print(f"Estimasi waktu: ~{est_minutes} menit (asumsi 1 mnt/run)")
    print("=" * 70)

    # Load semua kasus sekali saja di awal
    print("\n[SETUP] Loading semua kasus...")
    all_case_data = []
    for i, profile in enumerate(TUNING_PROFILES):
        print(f"  Kasus {i+1}: {profile['disease']}")
        food_df, guidelines, tdee = setup_data(profile)
        print(f"    ✓ {len(food_df)} foods | {len(guidelines['hard'])} HARD constraints | TDEE {tdee:.0f} kcal")
        all_case_data.append((food_df, guidelines, tdee))

    # Buat Optuna study (multi-objective, NSGA-II sampler)
    sampler = NSGAIISampler(seed=42)
    study = optuna.create_study(
        directions=['minimize', 'minimize'],   # (fitness↓, -CSR↓) = (fitness↓, CSR↑)
        sampler=sampler,
        study_name='ga_tuning'
    )

    # Kurangi verbosity Optuna supaya tidak berisik
    optuna.logging.set_verbosity(optuna.logging.WARNING)

    # Buat objective dengan semua kasus
    objective = make_objective(all_case_data)

    # ── Warm start: sisipkan parameter existing sebagai trial #0 ──────────
    # Ini parameter yang sudah dipakai di ga_interface.py sekarang
    # Hasilnya akan muncul di Pareto front untuk perbandingan langsung
    EXISTING_PARAMS = {
        'pop_size':      71,
        'generations':   91,
        'elite_ratio':   0.15,   # dari ga_interface.py
        'mutation_rate': 0.35,   # dari ga_interface.py
        'ls_iterations': 37,
    }
    study.enqueue_trial(EXISTING_PARAMS)
    print(f"[INFO] Warm start: parameter existing disisipkan sebagai Trial #0")
    print(f"       {EXISTING_PARAMS}")

    print(f"\n[TUNING] Mulai {N_TRIALS} trials...\n")
    t_start = time.time()

    study.optimize(objective, n_trials=N_TRIALS + 1)  # +1 untuk warm start trial

    elapsed = time.time() - t_start
    print(f"\n✓ Selesai dalam {elapsed/60:.1f} menit")

    # Simpan dan tampilkan hasil
    output_dir = os.path.dirname(os.path.abspath(__file__))
    save_results(study, output_dir=output_dir)


if __name__ == '__main__':
    main()
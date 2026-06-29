"""
convergence_ga.py
-----------------
Evaluasi konvergensi Genetic Algorithm + Local Search untuk 26 profil penyakit.

Pendekatan: GA dijalankan dengan parameter penuh (termasuk Local Search),
lalu fitness_history per generasi di-log dan diplot sebagai kurva konvergensi.
Ini merepresentasikan perilaku sistem yang sesungguhnya (GA + LS).

Output:
- output/convergence_ga/convergence_summary.csv  → fitness per generasi per profil
- output/convergence_ga/convergence_all.png      → semua 26 profil dalam 1 chart
- output/convergence_ga/convergence_grouped.png  → 3 subplot: single/dual/triple disease
"""

import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir  = os.path.abspath(os.path.join(current_dir, '..'))
root_dir    = os.path.abspath(os.path.join(current_dir, '..', '..'))
sys.path.insert(0, parent_dir)
sys.path.insert(0, root_dir)
sys.path.insert(0, os.path.join(root_dir, 'C. System Flow'))
sys.path.insert(0, os.path.join(root_dir, 'D. Model'))
sys.path.insert(0, os.path.join(root_dir, 'D. Model', 'Genetic Algorithm'))

from b_nutrition_service import NutritionService          # type: ignore
from b_genetic_algorithm import run_ga_numpy              # type: ignore
from c_ga_interface import GeneticAlgorithmInterface      # type: ignore
from a_ga_parameter import GA_PARAMS, LS_PARAMS           # type: ignore

# ─────────────────────────────────────────────────────────────
# 26 PROFIL (identik dengan ga_evaluation_26.py)
# ─────────────────────────────────────────────────────────────
BASE = {'gender': 'M', 'age': 45, 'weight': 70, 'height': 175, 'activity_factor': 1.4}

PROFILES = [
    # === NORMAL ===
    {**BASE, 'name': 'Normal',                                          'disease': ['normal'],                              'group': 'Normal'},

    # === SINGLE DISEASE ===
    {**BASE, 'name': 'Diabetes Melitus Tipe 2',                        'disease': ['dm2'],                                 'group': 'Single'},
    {**BASE, 'name': 'Hipertensi',                                     'disease': ['hypertension'],                        'group': 'Single'},
    {**BASE, 'name': 'Penyakit Kardiovaskular',                        'disease': ['cvd'],                                 'group': 'Single'},
    {**BASE, 'name': 'Hiperkolesterolemia',                            'disease': ['cholesterol'],                         'group': 'Single'},
    {**BASE, 'name': 'Penyakit Ginjal Kronis',                        'disease': ['ckd'],                                 'group': 'Single'},

    # === DUAL DISEASE ===
    {**BASE, 'name': 'DM2 + Hipertensi',                              'disease': ['dm2', 'hypertension'],                 'group': 'Dual'},
    {**BASE, 'name': 'DM2 + CVD',                                     'disease': ['dm2', 'cvd'],                          'group': 'Dual'},
    {**BASE, 'name': 'DM2 + Hiperkolesterolemia',                     'disease': ['dm2', 'cholesterol'],                  'group': 'Dual'},
    {**BASE, 'name': 'DM2 + CKD',                                     'disease': ['dm2', 'ckd'],                          'group': 'Dual'},
    {**BASE, 'name': 'Hipertensi + CVD',                              'disease': ['hypertension', 'cvd'],                 'group': 'Dual'},
    {**BASE, 'name': 'Hipertensi + Hiperkolesterolemia',              'disease': ['hypertension', 'cholesterol'],         'group': 'Dual'},
    {**BASE, 'name': 'Hipertensi + CKD',                             'disease': ['hypertension', 'ckd'],                 'group': 'Dual'},
    {**BASE, 'name': 'CVD + Hiperkolesterolemia',                     'disease': ['cvd', 'cholesterol'],                  'group': 'Dual'},
    {**BASE, 'name': 'CVD + CKD',                                     'disease': ['cvd', 'ckd'],                          'group': 'Dual'},
    {**BASE, 'name': 'Hiperkolesterolemia + CKD',                     'disease': ['cholesterol', 'ckd'],                  'group': 'Dual'},

    # === TRIPLE DISEASE ===
    {**BASE, 'name': 'DM2 + Hipertensi + CVD',                       'disease': ['dm2', 'hypertension', 'cvd'],          'group': 'Triple'},
    {**BASE, 'name': 'DM2 + Hipertensi + Hiperkolesterolemia',       'disease': ['dm2', 'hypertension', 'cholesterol'],  'group': 'Triple'},
    {**BASE, 'name': 'DM2 + Hipertensi + CKD',                       'disease': ['dm2', 'hypertension', 'ckd'],          'group': 'Triple'},
    {**BASE, 'name': 'DM2 + CVD + Hiperkolesterolemia',              'disease': ['dm2', 'cvd', 'cholesterol'],           'group': 'Triple'},
    {**BASE, 'name': 'DM2 + CVD + CKD',                              'disease': ['dm2', 'cvd', 'ckd'],                   'group': 'Triple'},
    {**BASE, 'name': 'DM2 + Hiperkolesterolemia + CKD',              'disease': ['dm2', 'cholesterol', 'ckd'],           'group': 'Triple'},
    {**BASE, 'name': 'Hipertensi + CVD + Hiperkolesterolemia',       'disease': ['hypertension', 'cvd', 'cholesterol'],  'group': 'Triple'},
    {**BASE, 'name': 'Hipertensi + CVD + CKD',                       'disease': ['hypertension', 'cvd', 'ckd'],          'group': 'Triple'},
    {**BASE, 'name': 'Hipertensi + Hiperkolesterolemia + CKD',       'disease': ['hypertension', 'cholesterol', 'ckd'],  'group': 'Triple'},
    {**BASE, 'name': 'CVD + Hiperkolesterolemia + CKD',              'disease': ['cvd', 'cholesterol', 'ckd'],           'group': 'Triple'},
]

# Pengulangan per profil untuk stabilitas rata-rata fitness_history
N_REPEATS = 3


def run_and_get_history(food_df, guidelines_ga, tdee):
    """
    Jalankan GA+LS satu kali dengan parameter penuh,
    kembalikan fitness_history (list panjang = jumlah generasi).
    """
    _, _, fitness_history = run_ga_numpy(
        food_df=food_df,
        guidelines=guidelines_ga,
        tdee=tdee,
        **GA_PARAMS,
        ls_iterations=LS_PARAMS['iterations'],
        verbose=False,
    )
    return fitness_history


def average_histories(histories):
    """
    Rata-ratakan beberapa fitness_history yang mungkin panjangnya berbeda
    (karena early stopping / deadline). Potong ke panjang terpendek.
    """
    min_len = min(len(h) for h in histories)
    arr = np.array([h[:min_len] for h in histories])
    return arr.mean(axis=0).tolist(), arr.std(axis=0).tolist(), min_len


def main():
    print("=" * 65)
    print("  EVALUASI KONVERGENSI GA+LS — 26 PROFIL PENYAKIT")
    print("=" * 65)
    print(f"Parameter GA : {GA_PARAMS}")
    print(f"Parameter LS : {LS_PARAMS}")
    print(f"Pengulangan  : {N_REPEATS}x per profil")
    print("=" * 65)

    output_dir = os.path.join(current_dir, 'output', 'convergence_ga')
    os.makedirs(output_dir, exist_ok=True)

    try:
        nutrition_service = NutritionService()
    except Exception as e:
        print(f"[ERROR] NutritionService gagal: {e}")
        return

    # Simpan hasil semua profil
    all_rows   = []   # untuk CSV panjang (per generasi per profil)
    plot_data  = {}   # {profile_name: {'mean': [...], 'std': [...], 'group': str}}

    for i, profile in enumerate(PROFILES):
        print(f"\n[{i+1:02d}/{len(PROFILES)}] {profile['name']} ({profile['group']})")
        print("-" * 55)

        try:
            analysis = nutrition_service.calculate_nutrition_needs(profile)
            if not analysis['success']:
                print(f"  [ERROR] {analysis.get('error')}")
                continue

            tdee          = analysis['energy']['tdee']          # type: ignore
            guidelines    = analysis['guidelines']              # type: ignore
            food_database = analysis['food_data']['dataframe']  # type: ignore

            # Convert ke format GA
            ga_iface      = GeneticAlgorithmInterface(food_database, guidelines)
            guidelines_ga = ga_iface.constraint_bag

        except Exception as e:
            print(f"  [ERROR] Persiapan data: {e}")
            continue

        print(f"  TDEE={tdee:.0f} kcal | Foods={len(food_database)}")

        # Kumpulkan fitness_history dari N_REPEATS run
        histories = []
        for r in range(N_REPEATS):
            print(f"  -> Run {r+1}/{N_REPEATS}...", end=' ', flush=True)
            try:
                hist = run_and_get_history(food_df=food_database,
                                           guidelines_ga=guidelines_ga,
                                           tdee=tdee)
                if hist:
                    histories.append(hist)
                    print(f"OK ({len(hist)} gen, final fitness={hist[-1]:.1f})")
                else:
                    print("FAILED (history kosong)")
            except Exception as e:
                print(f"ERROR → {e}")

        if not histories:
            print(f"  [SKIP] Semua run gagal untuk {profile['name']}")
            continue

        mean_hist, std_hist, n_gen = average_histories(histories)

        plot_data[profile['name']] = {
            'mean':  mean_hist,
            'std':   std_hist,
            'group': profile['group'],
        }

        # Simpan ke rows CSV
        for gen_idx, (m, s) in enumerate(zip(mean_hist, std_hist)):
            all_rows.append({
                'Profile':      profile['name'],
                'Group':        profile['group'],
                'Generation':   gen_idx + 1,
                'Mean Fitness': round(m, 2),
                'Std Fitness':  round(s, 2),
            })

        print(f"  Fitness awal : {mean_hist[0]:.1f}")
        print(f"  Fitness akhir: {mean_hist[-1]:.1f}")
        print(f"  Penurunan    : {(mean_hist[0]-mean_hist[-1])/mean_hist[0]*100:.1f}%")

    # ── Simpan CSV ──
    if not all_rows:
        print("\n[ERROR] Tidak ada data yang berhasil dikumpulkan.")
        return

    df_all = pd.DataFrame(all_rows)
    csv_path = os.path.join(output_dir, 'convergence_summary.csv')
    df_all.to_csv(csv_path, index=False)
    print(f"\n[OK] CSV disimpan: {csv_path}")

    # ════════════════════════════════════════════════════════
    # PLOT 1: Semua 26 profil dalam 1 chart (dengan warna per group)
    # ════════════════════════════════════════════════════════
    group_colors = {
        'Normal': '#2ca02c',
        'Single': '#1f77b4',
        'Dual':   '#ff7f0e',
        'Triple': '#d62728',
    }
    group_alpha = {'Normal': 0.9, 'Single': 0.7, 'Dual': 0.7, 'Triple': 0.7}

    fig, ax = plt.subplots(figsize=(14, 7))
    sns.set_style("whitegrid")

    legend_added = set()
    for profile_name, data in plot_data.items():
        group  = data['group']
        color  = group_colors.get(group, 'gray')
        alpha  = group_alpha.get(group, 0.6)
        mean_h = data['mean']
        gens   = list(range(1, len(mean_h) + 1))

        label = group if group not in legend_added else None
        ax.plot(gens, mean_h, color=color, alpha=alpha, linewidth=1.2, label=label)
        legend_added.add(group)

    ax.set_title('Kurva Konvergensi Genetic Algorithm + Local Search\n(26 Profil Penyakit, Rata-rata 3 Run)',
                 fontsize=13)
    ax.set_xlabel('Generasi', fontsize=11)
    ax.set_ylabel('Best Fitness Score (Lower is Better)', fontsize=11)
    ax.legend(title='Kelompok Penyakit', fontsize=10, title_fontsize=10)
    plt.tight_layout()

    chart1_path = os.path.join(output_dir, 'convergence_all.png')
    plt.savefig(chart1_path, dpi=300)
    plt.close()
    print(f"[OK] Chart 1 disimpan: {chart1_path}")

    # ════════════════════════════════════════════════════════
    # PLOT 2: 4 subplot per kelompok (Normal, Single, Dual, Triple)
    # ════════════════════════════════════════════════════════
    groups_order = ['Normal', 'Single', 'Dual', 'Triple']
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    axes = axes.flatten()

    for ax_idx, group_name in enumerate(groups_order):
        ax = axes[ax_idx]
        group_profiles = {k: v for k, v in plot_data.items() if v['group'] == group_name}

        for profile_name, data in group_profiles.items():
            mean_h = data['mean']
            std_h  = data['std']
            gens   = list(range(1, len(mean_h) + 1))

            ax.plot(gens, mean_h, linewidth=1.5, label=profile_name)
            ax.fill_between(gens,
                            [m - s for m, s in zip(mean_h, std_h)],
                            [m + s for m, s in zip(mean_h, std_h)],
                            alpha=0.1)

        count = len(group_profiles)
        ax.set_title(f'{group_name} ({count} profil)', fontsize=11, fontweight='bold')
        ax.set_xlabel('Generasi', fontsize=10)
        ax.set_ylabel('Best Fitness Score', fontsize=10)
        ax.grid(True, alpha=0.3)

        if count <= 6:
            ax.legend(fontsize=7, loc='upper right')

    plt.suptitle('Konvergensi GA+LS per Kelompok Penyakit (Mean ± Std, 3 Run)',
                 fontsize=13, y=1.01)
    plt.tight_layout()

    chart2_path = os.path.join(output_dir, 'convergence_grouped.png')
    plt.savefig(chart2_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Chart 2 disimpan: {chart2_path}")

    # ════════════════════════════════════════════════════════
    # PRINT SUMMARY AKHIR
    # ════════════════════════════════════════════════════════
    print("\n" + "=" * 65)
    print("  RINGKASAN KONVERGENSI")
    print("=" * 65)
    print(f"{'Profile':<45} | {'Awal':>8} | {'Akhir':>8} | {'Turun':>7}")
    print("-" * 75)
    for profile_name, data in plot_data.items():
        m   = data['mean']
        pct = (m[0] - m[-1]) / m[0] * 100 if m[0] > 0 else 0
        print(f"{profile_name:<45} | {m[0]:>8.1f} | {m[-1]:>8.1f} | {pct:>6.1f}%")

    print(f"\n[DONE] Semua output tersimpan di: {output_dir}")


if __name__ == "__main__":
    main()
import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ─── Path setup (auto-detect project root by locating 'D. Model' folder) ──────
current_dir = os.path.dirname(os.path.abspath(__file__))

def find_root(start_dir, marker='D. Model'):
    d = start_dir
    for _ in range(6):  # search up to 6 levels up
        if os.path.isdir(os.path.join(d, marker)):
            return d
        d = os.path.abspath(os.path.join(d, '..'))
    raise FileNotFoundError(
        f"Could not locate project root containing '{marker}' folder starting from {start_dir}. "
        f"Adjust the path setup manually if your folder structure is different."
    )

root_dir = find_root(current_dir)
sys.path.insert(0, root_dir)
sys.path.insert(0, os.path.join(root_dir, 'C. System Flow'))
sys.path.insert(0, os.path.join(root_dir, 'D. Model'))
sys.path.insert(0, os.path.join(root_dir, 'D. Model', 'Genetic Algorithm'))

# NOTE: adjust these imports if your module/class names differ from Dicky's repo copy
from b_nutrition_service import NutritionService
from c_ga_interface import GeneticAlgorithmInterface

BASE = {'gender': 'M', 'age': 45, 'weight': 70, 'height': 175, 'activity_factor': 1.4}

PROFILES = [
    {**BASE, 'name': 'Normal',                                          'disease': ['normal']},
    {**BASE, 'name': 'Diabetes Melitus Tipe 2',                        'disease': ['dm2']},
    {**BASE, 'name': 'Hipertensi',                                     'disease': ['hypertension']},
    {**BASE, 'name': 'Penyakit Kardiovaskular',                        'disease': ['cvd']},
    {**BASE, 'name': 'Hiperkolesterolemia',                            'disease': ['cholesterol']},
    {**BASE, 'name': 'Penyakit Ginjal Kronis',                        'disease': ['ckd']},
    {**BASE, 'name': 'DM2 + Hipertensi',                              'disease': ['dm2', 'hypertension']},
    {**BASE, 'name': 'DM2 + CVD',                                     'disease': ['dm2', 'cvd']},
    {**BASE, 'name': 'DM2 + Hiperkolesterolemia',                     'disease': ['dm2', 'cholesterol']},
    {**BASE, 'name': 'DM2 + CKD',                                     'disease': ['dm2', 'ckd']},
    {**BASE, 'name': 'Hipertensi + CVD',                              'disease': ['hypertension', 'cvd']},
    {**BASE, 'name': 'Hipertensi + Hiperkolesterolemia',              'disease': ['hypertension', 'cholesterol']},
    {**BASE, 'name': 'Hipertensi + CKD',                              'disease': ['hypertension', 'ckd']},
    {**BASE, 'name': 'CVD + Hiperkolesterolemia',                     'disease': ['cvd', 'cholesterol']},
    {**BASE, 'name': 'CVD + CKD',                                     'disease': ['cvd', 'ckd']},
    {**BASE, 'name': 'Hiperkolesterolemia + CKD',                     'disease': ['cholesterol', 'ckd']},
    {**BASE, 'name': 'DM2 + Hipertensi + CVD',                       'disease': ['dm2', 'hypertension', 'cvd']},
    {**BASE, 'name': 'DM2 + Hipertensi + Hiperkolesterolemia',       'disease': ['dm2', 'hypertension', 'cholesterol']},
    {**BASE, 'name': 'DM2 + Hipertensi + CKD',                       'disease': ['dm2', 'hypertension', 'ckd']},
    {**BASE, 'name': 'DM2 + CVD + Hiperkolesterolemia',              'disease': ['dm2', 'cvd', 'cholesterol']},
    {**BASE, 'name': 'DM2 + CVD + CKD',                              'disease': ['dm2', 'cvd', 'ckd']},
    {**BASE, 'name': 'DM2 + Hiperkolesterolemia + CKD',              'disease': ['dm2', 'cholesterol', 'ckd']},
    {**BASE, 'name': 'Hipertensi + CVD + Hiperkolesterolemia',       'disease': ['hypertension', 'cvd', 'cholesterol']},
    {**BASE, 'name': 'Hipertensi + CVD + CKD',                       'disease': ['hypertension', 'cvd', 'ckd']},
    {**BASE, 'name': 'Hipertensi + Hiperkolesterolemia + CKD',       'disease': ['hypertension', 'cholesterol', 'ckd']},
    {**BASE, 'name': 'CVD + Hiperkolesterolemia + CKD',              'disease': ['cvd', 'cholesterol', 'ckd']},
]

N_RUNS = 5  # GA is stochastic -> average over 5 runs per profile

def main():
    print("Calculating NCS for Genetic Algorithm (5 runs per profile)...")
    nutrition_service = NutritionService()
    results_summary = []

    for i, profile in enumerate(PROFILES):
        print(f"[{i+1}/{len(PROFILES)}] {profile['name']}")
        analysis = nutrition_service.calculate_nutrition_needs(profile)
        tdee = analysis['energy']['tdee']
        guidelines = analysis['guidelines']
        db = analysis['food_data']['dataframe']

        guideline_nutrients = guidelines.get('nutrients', {})
        ga_engine = GeneticAlgorithmInterface(db, guidelines)

        run_opt, run_def, run_exc = [], [], []

        for run_idx in range(N_RUNS):
            menu_plan = ga_engine.generate_menu_plan(profile, tdee)
            if not menu_plan:
                continue

            MACRO_MAP = {
                'energy_kcal':    menu_plan.total_daily_calories,
                'protein_g':      menu_plan.total_daily_protein_g,
                'carbohydrate_g': menu_plan.total_daily_carb_g,
                'fat_g':          menu_plan.total_daily_fat_g,
            }
            if hasattr(menu_plan, 'daily_micronutrients') and menu_plan.daily_micronutrients:
                MACRO_MAP.update(menu_plan.daily_micronutrients)

            optimal_count = 0
            deficient_count = 0
            excess_count = 0
            total_eval = 0

            for nutrient, limits in guideline_nutrients.items():
                if nutrient not in MACRO_MAP:
                    continue

                actual_val = MACRO_MAP[nutrient]
                min_v = limits.get('min', 0)
                max_v = limits.get('max', float('inf'))

                total_eval += 1
                if actual_val < min_v:
                    deficient_count += 1
                elif actual_val > max_v:
                    excess_count += 1
                else:
                    optimal_count += 1

            run_opt.append(optimal_count / total_eval * 100 if total_eval > 0 else 0)
            run_def.append(deficient_count / total_eval * 100 if total_eval > 0 else 0)
            run_exc.append(excess_count / total_eval * 100 if total_eval > 0 else 0)

        if run_opt:
            results_summary.append({
                'Profile': profile['name'],
                'Optimal (%)': np.mean(run_opt),
                'Deficient (%)': np.mean(run_def),
                'Excess (%)': np.mean(run_exc),
                'Optimal Std': np.std(run_opt),
            })
            print(f"    Optimal={np.mean(run_opt):.1f}%  Deficient={np.mean(run_def):.1f}%  Excess={np.mean(run_exc):.1f}%  (std={np.std(run_opt):.1f})")

    df = pd.DataFrame(results_summary)
    out_dir = os.path.join(current_dir, 'output', 'ga_26')
    os.makedirs(out_dir, exist_ok=True)
    df.to_csv(os.path.join(out_dir, 'ncs_summary_ga.csv'), index=False)

    # ─── Color Coding per Kelompok ────────────────────────────────────────────
    def get_group(profile):
        if profile == "Normal":
            return "normal"
        count = profile.count("+")
        if count == 0:
            return "single"
        elif count == 1:
            return "dual"
        else:
            return "triple"

    df["group"] = df["Profile"].apply(get_group)
    group_order = {"normal": 0, "single": 1, "dual": 2, "triple": 3}
    df["group_order"] = df["group"].map(group_order)
    df = df.sort_values(["group_order", "Optimal (%)"], ascending=[True, False]).reset_index(drop=True)

    # Plot
    fig, ax = plt.subplots(figsize=(12, 11))

    p1 = ax.barh(df["Profile"], df["Optimal (%)"], color="#2a9d8f", edgecolor="white", height=0.7)
    p2 = ax.barh(df["Profile"], df["Deficient (%)"], left=df["Optimal (%)"], color="#e9c46a", edgecolor="white", height=0.7)
    p3 = ax.barh(df["Profile"], df["Excess (%)"], left=df["Optimal (%)"] + df["Deficient (%)"], color="#e76f51", edgecolor="white", height=0.7)

    for i, (idx, row) in enumerate(df.iterrows()):
        ax.text(row["Optimal (%)"] / 2, i, f'{row["Optimal (%)"]:.0f}%', va='center', ha='center', color='white', fontweight='bold', fontsize=8)
        if row["Deficient (%)"] > 5:
            ax.text(row["Optimal (%)"] + row["Deficient (%)"] / 2, i, f'{row["Deficient (%)"]:.0f}%', va='center', ha='center', color='black', fontsize=8)
        if row["Excess (%)"] > 5:
            ax.text(row["Optimal (%)"] + row["Deficient (%)"] + row["Excess (%)"] / 2, i, f'{row["Excess (%)"]:.0f}%', va='center', ha='center', color='black', fontsize=8)

    group_sizes = df.groupby("group_order").size()
    cumulative = 0
    separators = []
    for g in sorted(group_sizes.index)[:-1]:
        cumulative += group_sizes[g]
        separators.append(cumulative - 0.5)

    for sep in separators:
        ax.axhline(sep, color="#aaaaaa", linewidth=0.9, linestyle="-")

    ax.set_xlabel("Persentase Nutrisi (%)", fontsize=11, labelpad=10)
    ax.set_title("Nutrition Compliance Score (NCS) per Skenario Profil\n(Genetic Algorithm, rata-rata 5 run)", fontsize=13, fontweight="bold", pad=15)
    ax.set_xlim(0, 100)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0f}%"))
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.invert_yaxis()

    ax.legend([p1, p2, p3], ["Optimal", "Deficient (Kurang)", "Excess (Berlebih)"], loc="upper center", bbox_to_anchor=(0.5, -0.05), ncol=3, frameon=False)

    plt.tight_layout()
    chart_path = os.path.join(out_dir, "overall_ncs_ga.png")
    plt.savefig(chart_path, dpi=180, bbox_inches="tight", facecolor="white")
    print(f"\nChart saved to {chart_path}")
    print(f"CSV saved to {os.path.join(out_dir, 'ncs_summary_ga.csv')}")

if __name__ == "__main__":
    main()
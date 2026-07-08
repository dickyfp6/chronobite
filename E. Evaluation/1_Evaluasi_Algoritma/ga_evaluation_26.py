import sys
import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt # type: ignore
import seaborn as sns # type: ignore
from datetime import datetime

# ============================================================
# KONFIGURASI RUN — ubah dua baris ini tiap kali mau run baru
# ============================================================
N_RUNS = 5                      # jumlah run per profile (dulu 3, sekarang 5)
# ============================================================

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))         # evaluation folder
root_dir = os.path.abspath(os.path.join(current_dir, '..', '..'))    # project root
sys.path.insert(0, parent_dir)
sys.path.insert(0, root_dir)
sys.path.insert(0, os.path.join(root_dir, 'C. System Flow'))
sys.path.insert(0, os.path.join(root_dir, 'D. Model'))
sys.path.insert(0, os.path.join(root_dir, 'D. Model', 'Genetic Algorithm'))

from b_nutrition_service import NutritionService # type: ignore
from c_ga_interface import GeneticAlgorithmInterface # type: ignore

BASE = {'gender': 'M', 'age': 45, 'weight': 70, 'height': 175, 'activity_factor': 1.4}

PROFILES = [
    # === NORMAL ===
    {**BASE, 'name': 'Normal',                                          'disease': ['normal']},
    
    # === SINGLE DISEASE (5) ===
    {**BASE, 'name': 'Diabetes Melitus Tipe 2',                        'disease': ['dm2']},
    {**BASE, 'name': 'Hipertensi',                                     'disease': ['hypertension']},
    {**BASE, 'name': 'Penyakit Kardiovaskular',                        'disease': ['cvd']},
    {**BASE, 'name': 'Hiperkolesterolemia',                            'disease': ['cholesterol']},
    {**BASE, 'name': 'Penyakit Ginjal Kronis',                        'disease': ['ckd']},
    
    # === DUAL DISEASE — C(5,2) = 10 ===
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
    
    # === TRIPLE DISEASE — C(5,3) = 10 ===
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

def main():
    print("==========================================")
    print(" GENETIC ALGORITHM EVALUATION - 26 CASES ")
    print("==========================================")
    
    try:
        nutrition_service = NutritionService()
    except Exception as e:
        print(f"[ERROR] Failed to initialize NutritionService: {e}")
        return

    # Setiap run baru masuk ke folder sendiri (bertanggal + label),
    # jadi hasil lama otomatis nggak ketimpa dan gampang dibandingin nanti.
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_dir = os.path.join(current_dir, 'output', 'ga_26')
    os.makedirs(output_dir, exist_ok=True)
    print(f"Hasil run ini akan disimpan di: {output_dir}")
    
    results_summary = []
    raw_results = []  # simpan semua data mentah per-run, per-profile, untuk analisis ulang tanpa run lagi
    
    for i, profile in enumerate(PROFILES):
        print(f"\n[{i+1}/{len(PROFILES)}] Running GA for {profile['name']} profile...")
        
        try:
            analysis_result = nutrition_service.calculate_nutrition_needs(profile)
            if not analysis_result['success']:
                print(f"  [ERROR] Nutrition analysis failed: {analysis_result['error']}")
                continue
                
            tdee = analysis_result['energy']['tdee'] # type: ignore
            guidelines = analysis_result['guidelines'] # type: ignore
            food_database = analysis_result['food_data']['dataframe'] # type: ignore
            guideline_nutrients = guidelines.get('nutrients', {}) # type: ignore
            
            ga_engine = GeneticAlgorithmInterface(food_database, guidelines)
            
            run_fitnesses = []
            run_cs_rates = []
            run_avg_deviations = []
            run_n_passed = []
            run_n_total = []
            deviations_all_runs = []
            
            for run_idx in range(N_RUNS):
                print(f"  -> Run {run_idx+1}/{N_RUNS}...")
                menu_plan = ga_engine.generate_menu_plan(profile, tdee)
                
                if not menu_plan:
                    print(f"    [WARN] Run {run_idx+1} failed to generate menu plan")
                    continue
                    
                # Build actual nutrients from menu_plan tracked macros.
                # Keys match guideline key names exactly.
                MACRO_MAP = {
                    'energy_kcal':    menu_plan.total_daily_calories,
                    'protein_g':      menu_plan.total_daily_protein_g,
                    'carbohydrate_g': menu_plan.total_daily_carb_g,
                    'fat_g':          menu_plan.total_daily_fat_g,
                }
                # Also include daily_micronutrients if the algorithm populated them
                if hasattr(menu_plan, 'daily_micronutrients') and menu_plan.daily_micronutrients:
                    MACRO_MAP.update(menu_plan.daily_micronutrients)
    
                # Calculate CS Rate manually - HARD constraints only (consistent with greedy_evaluation.py)
                hard_constraints_passed = 0
                total_hard_constraints = 0
                
                for nutrient, limits in guideline_nutrients.items():
                    tipe = limits.get('hard_soft_type', 'SOFT')
                    if nutrient not in MACRO_MAP:
                        continue
                    actual_val = MACRO_MAP[nutrient]
                    min_v = limits.get('min', 0)
                    max_v = limits.get('max', float('inf'))
                    if tipe == 'HARD':
                        total_hard_constraints += 1
                        if min_v <= actual_val <= max_v:
                            hard_constraints_passed += 1
                
                satisfaction_rate = (hard_constraints_passed / total_hard_constraints * 100) if total_hard_constraints > 0 else 100
                n_passed = hard_constraints_passed
                n_total = total_hard_constraints

                # Best fitness langsung dari GA (penalty score, lower = better)
                best_fitness = menu_plan.best_fitness_score
                run_fitnesses.append(best_fitness)

                # Deviation tetap dihitung untuk chart analisis
                deviations = []
                for nutrient, limits in guideline_nutrients.items():
                    if nutrient not in MACRO_MAP:
                        continue
                    actual_val = MACRO_MAP[nutrient]
                    min_v = limits.get('min', 0)
                    max_v = limits.get('max', float('inf'))
                    tipe = limits.get('hard_soft_type', 'SOFT')

                    if min_v > 0 and max_v < float('inf'):
                        target = (min_v + max_v) / 2
                    elif min_v > 0:
                        target = min_v
                    elif max_v < float('inf'):
                        target = max_v
                    else:
                        target = None

                    if target and target > 0:
                        deviation_pct = abs(actual_val - target) / target * 100
                        deviations.append({
                            'nutrient': nutrient,
                            'deviation_pct': min(deviation_pct, 100),
                            'type': tipe,
                            'actual': round(actual_val, 2),
                            'target': round(target, 2),
                        })
                avg_deviation = sum(d['deviation_pct'] for d in deviations) / len(deviations) if deviations else 0
                
                run_cs_rates.append(satisfaction_rate)
                run_n_passed.append(n_passed)
                run_n_total.append(n_total)
                run_avg_deviations.append(avg_deviation)
                if run_idx == 0:
                    deviations_all_runs = deviations # Save first run for charting
                    
            if not run_fitnesses:
                continue
                
            mean_fitness = np.mean(run_fitnesses)
            std_fitness = np.std(run_fitnesses)
            mean_cs = np.mean(run_cs_rates)
            mean_dev = np.mean(run_avg_deviations)
            
            # Simpan data mentah tiap run (bukan cuma rata-rata) — ini yang bikin
            # perbandingan versi lama vs baru bisa dilakukan kapan saja tanpa run ulang GA
            raw_results.append({
                'profile': profile['name'],
                'disease': profile['disease'],
                'n_runs': N_RUNS,
                'fitness_per_run': [float(x) for x in run_fitnesses],
                'cs_rate_per_run': [float(x) for x in run_cs_rates],
                'avg_deviation_per_run': [float(x) for x in run_avg_deviations],
                'n_passed_per_run': [int(x) for x in run_n_passed],
                'n_total_per_run': [int(x) for x in run_n_total],
            })
            
            results_summary.append({
                'Profile': profile['name'],
                'CS Rate': mean_cs,
                'N Constraints': f"{int(np.mean(run_n_passed))}/{int(np.mean(run_n_total))}",
                'Avg Deviation': mean_dev,
                'Best Fitness (Mean)': round(mean_fitness, 1),
                'Best Fitness (Std)': round(std_fitness, 1)
            })
            
            if deviations_all_runs:
                plt.figure(figsize=(12, 6))
                sns.set_style("whitegrid")
                dev_df = pd.DataFrame(deviations_all_runs)
                dev_df = dev_df.sort_values('deviation_pct', ascending=False)
                
                sns.barplot(data=dev_df, x='nutrient', y='deviation_pct', hue='type', palette={'SOFT': 'blue', 'HARD': 'orange'})
                plt.title(f"Deviation Analysis - GA (Run 1) - {profile['name']}")
                plt.ylabel("Deviation from Target (%)")
                plt.xlabel("Nutrient")
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                plt.savefig(os.path.join(output_dir, f"deviation_{i+1}_ga.png"), dpi=300)
                plt.close()
            
            # GRAFIK 1: Line chart fitness per run
            plt.figure(figsize=(12, 6))
            sns.set_style("whitegrid")
            runs = [f"Run {j+1}" for j in range(len(run_fitnesses))]
            plt.plot(runs, run_fitnesses, marker='o', linestyle='-', linewidth=2, markersize=8, color='#1f77b4', label='Fitness Score')
            plt.axhline(y=float(mean_fitness), color='gray', linestyle='--', linewidth=2, label=f'Mean: {mean_fitness:.1f}')
            plt.title(f"Fitness per Run - {profile['name']}")
            plt.ylabel("Fitness Score (lower = better)")
            plt.xlabel("Run Number")
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, f"fitness_per_run_{i+1}.png"), dpi=300)
            plt.close()
                
            print(f"  -> Best Fitness Score (GA Penalty): {mean_fitness:.1f} ± {std_fitness:.1f}")
            print(f"     (Lower = Better | Scale: macro×5000 + hard×10000 + soft×100)")
            print(f"  -> Mean CS Rate: {mean_cs:.1f}%")
            print(f"  -> Mean Avg Deviation: {mean_dev:.1f}%")
            
        except Exception as e:
            print(f"  [ERROR] {e}")
            import traceback
            traceback.print_exc()

    if results_summary:
        summary_df = pd.DataFrame(results_summary)
        summary_df.to_csv(os.path.join(output_dir, 'summary.csv'), index=False)
        
        # Simpan raw data lengkap + metadata run — ini yang dipakai kalau nanti
        # mau bandingin versi ini vs versi lain tanpa run ulang
        with open(os.path.join(output_dir, 'raw_results.json'), 'w') as f:
            json.dump({
                'n_runs': N_RUNS,
                'n_profiles': len(PROFILES),
                'results': raw_results
            }, f, indent=2)
        print(f"\nRaw data (per-run, bisa dianalisis ulang) disimpan di: raw_results.json")
        
        plt.figure(figsize=(10, 6))
        sns.barplot(data=summary_df, x='Profile', y='CS Rate', color='coral')
        plt.title('Constraint Satisfaction Rate by Profile (Genetic Algorithm)')
        plt.ylabel('Satisfaction Rate (%)')
        plt.ylim(0, 100)
        plt.xticks(rotation=15)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'overall_cs_ga.png'), dpi=300)
        plt.close()
        
        # GRAFIK 2: Bar chart mean fitness ± std semua profile
        plt.figure(figsize=(12, 6))
        sns.set_style("whitegrid")
        fitness_data = [
            {
                'Profile': r['Profile'],
                'Best Fitness (Mean)': r['Best Fitness (Mean)'],
                'Best Fitness (Std)': r['Best Fitness (Std)']
            }
            for r in results_summary
        ]
        fitness_df = pd.DataFrame(fitness_data)
        
        bars = plt.bar(fitness_df['Profile'], fitness_df['Best Fitness (Mean)'], 
                       yerr=fitness_df['Best Fitness (Std)'], 
                       color='steelblue', alpha=0.7, capsize=5, error_kw={'linewidth': 2})
        
        # Add value labels on top of bars
        for bar, val, std in zip(bars, fitness_df['Best Fitness (Mean)'], fitness_df['Best Fitness (Std)']):
            plt.text(bar.get_x() + bar.get_width()/2, val + std + 5, 
                     f'{val:.1f}', ha='center', va='bottom', fontweight='bold')
        
        plt.title("Best Fitness Score by Profile (Genetic Algorithm) — Lower is Better")
        plt.ylabel("Best Fitness Score (Mean)")
        plt.xlabel("Profile")
        plt.xticks(rotation=15, ha='right')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'overall_fitness_ga.png'), dpi=300)
        plt.close()

        print("\n==========================================")
        print(f"{'Profile':<50} | {'CS Rate':<10} | {'N Constraints':<15} | {'Avg Deviation':<15} | {'Best Fitness (GA Penalty)':<25}")
        print("-" * 150)
        for row in results_summary:
            print(f"{row['Profile']:<50} | {row['CS Rate']:<8.1f}% | {row['N Constraints']:<15} | {row['Avg Deviation']:<13.1f}% | {row['Best Fitness (Mean)']:<10.1f} ± {row['Best Fitness (Std)']:<5.1f}")
        print("==========================================")

if __name__ == "__main__":
    main()
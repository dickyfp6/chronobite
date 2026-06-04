import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt # type: ignore
import seaborn as sns # type: ignore

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
sys.path.insert(0, os.path.join(parent_dir, 'C. System Flow'))
sys.path.insert(0, os.path.join(parent_dir, 'D. Model'))
sys.path.insert(0, os.path.join(parent_dir, 'D. Model', 'Genetic Algorithm'))

from nutrition_service import NutritionService # type: ignore
from ga_interface import GeneticAlgorithmInterface # type: ignore
from ga_v1 import fitness as calculate_fitness # type: ignore # Needed for fitness if not exposed directly

PROFILES = [
    {
        'name': 'Normal',
        'gender': 'M', 'age': 30, 'weight': 70, 
        'height': 175, 'activity_factor': 1.845,
        'disease': ['normal']
    },
    {
        'name': 'Single Disease (DM2)',
        'gender': 'F', 'age': 45, 'weight': 65,
        'height': 160, 'activity_factor': 1.4,
        'disease': ['dm2']
    },
    {
        'name': 'Dual Disease (DM2 + Hypertension)',
        'gender': 'M', 'age': 55, 'weight': 80,
        'height': 170, 'activity_factor': 1.4,
        'disease': ['dm2', 'hypertension']
    },
    {
        'name': 'Triple Disease (DM2 + Hypertension + Cholesterol)',
        'gender': 'F', 'age': 60, 'weight': 75,
        'height': 158, 'activity_factor': 1.4,
        'disease': ['dm2', 'hypertension', 'cholesterol']
    }
]

def main():
    print("==========================================")
    print(" GENETIC ALGORITHM EVALUATION FRAMEWORK ")
    print("==========================================")
    
    try:
        nutrition_service = NutritionService()
    except Exception as e:
        print(f"[ERROR] Failed to initialize NutritionService: {e}")
        return

    output_dir = os.path.join(current_dir, 'output', 'ga')
    os.makedirs(output_dir, exist_ok=True)
    
    results_summary = []
    
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
            deviations_all_runs = []
            
            for run_idx in range(3):
                print(f"  -> Run {run_idx+1}/3...")
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
    
                deviations = []
                hard_constraints_passed = 0
                total_hard_constraints = 0
                total_penalty = 0
                
                for nutrient, limits in guideline_nutrients.items():
                    tipe = limits.get('hard_soft_type', 'SOFT')

                    # Skip micronutrients — MenuPlan doesn't track them
                    if nutrient not in MACRO_MAP:
                        continue

                    actual_val = MACRO_MAP[nutrient]
                    min_v = limits.get('min', 0)
                    max_v = limits.get('max', float('inf'))
                    
                    if tipe == 'HARD':
                        total_hard_constraints += 1
                        if min_v <= actual_val <= max_v:
                            hard_constraints_passed += 1
                            
                    # Deviation Analysis: use midpoint of [min, max] as target
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
                        total_penalty += min(deviation_pct, 100)

                
                run_fitnesses.append(total_penalty) # using total deviation as a proxy for penalty fitness
                
                satisfaction_rate = (hard_constraints_passed / total_hard_constraints * 100) if total_hard_constraints > 0 else 100
                avg_deviation = sum(d['deviation_pct'] for d in deviations) / len(deviations) if deviations else 0
                
                run_cs_rates.append(satisfaction_rate)
                run_avg_deviations.append(avg_deviation)
                if run_idx == 0:
                    deviations_all_runs = deviations # Save first run for charting
                    
            if not run_fitnesses:
                continue
                
            mean_fitness = np.mean(run_fitnesses)
            std_fitness = np.std(run_fitnesses)
            mean_cs = np.mean(run_cs_rates)
            mean_dev = np.mean(run_avg_deviations)
            
            results_summary.append({
                'Profile': profile['name'],
                'CS Rate': mean_cs,
                'Avg Deviation': mean_dev,
                'Fitness (Mean)': mean_fitness,
                'Fitness (Std)': std_fitness
            })
            
            if deviations_all_runs:
                plt.figure(figsize=(12, 6))
                sns.set_style("whitegrid")
                dev_df = pd.DataFrame(deviations_all_runs)
                dev_df = dev_df.sort_values('deviation_pct', ascending=False)
                
                sns.barplot(data=dev_df, x='nutrient', y='deviation_pct', hue='type')
                plt.title(f"Deviation Analysis - GA (Run 1) - {profile['name']}")
                plt.ylabel("Deviation from Target (%)")
                plt.xlabel("Nutrient")
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                plt.savefig(os.path.join(output_dir, f"deviation_{i+1}_ga.png"), dpi=300)
                plt.close()
                
            print(f"  -> Best Fitness (Penalty): {mean_fitness:.1f} ± {std_fitness:.1f}")
            print(f"  -> Mean CS Rate: {mean_cs:.1f}%")
            print(f"  -> Mean Avg Deviation: {mean_dev:.1f}%")
            
        except Exception as e:
            print(f"  [ERROR] {e}")
            import traceback
            traceback.print_exc()

    if results_summary:
        summary_df = pd.DataFrame(results_summary)
        summary_df.to_csv(os.path.join(output_dir, 'summary.csv'), index=False)
        
        plt.figure(figsize=(10, 6))
        sns.barplot(data=summary_df, x='Profile', y='CS Rate', color='coral')
        plt.title('Constraint Satisfaction Rate by Profile (Genetic Algorithm)')
        plt.ylabel('Satisfaction Rate (%)')
        plt.ylim(0, 100)
        plt.xticks(rotation=15)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'overall_cs_ga.png'), dpi=300)
        plt.close()

        print("\n==========================================")
        print(f"{'Profile':<50} | {'CS Rate':<10} | {'Avg Deviation':<15} | {'Fitness (Penalty)':<20}")
        print("-" * 105)
        for row in results_summary:
            print(f"{row['Profile']:<50} | {row['CS Rate']:<8.1f}% | {row['Avg Deviation']:<13.1f}% | {row['Fitness (Mean)']:<7.1f} ± {row['Fitness (Std)']:<5.1f}")
        print("==========================================")

if __name__ == "__main__":
    main()

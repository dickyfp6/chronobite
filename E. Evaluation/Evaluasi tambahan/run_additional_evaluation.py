import os
import sys
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt # type: ignore
import seaborn as sns # type: ignore

# Add paths to import the required models
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..', '..'))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
sys.path.insert(0, os.path.join(parent_dir, 'C. System Flow'))
sys.path.insert(0, os.path.join(parent_dir, 'D. Model'))
sys.path.insert(0, os.path.join(parent_dir, 'D. Model', 'Genetic Algorithm'))
sys.path.insert(0, os.path.join(parent_dir, 'D. Model', 'greedy'))

from nutrition_service import NutritionService # type: ignore
from ga_interface import GeneticAlgorithmInterface # type: ignore
from greedy_interface import GreedyAlgorithmInterface # type: ignore
from ga_v1 import run_ga, fitness as calculate_fitness, local_search # type: ignore

PROFILES = [
    {'name': 'Normal',
     'gender': 'M', 'age': 45, 'weight': 70, 'height': 175, 'activity_factor': 1.4,
     'disease': ['normal']},
    {'name': 'Diabetes Melitus Type 2',
     'gender': 'M', 'age': 45, 'weight': 70, 'height': 175, 'activity_factor': 1.4,
     'disease': ['dm2']},
    {'name': 'Hypertension',
     'gender': 'M', 'age': 45, 'weight': 70, 'height': 175, 'activity_factor': 1.4,
     'disease': ['hypertension']},
    {'name': 'Cardiovascular Disease',
     'gender': 'M', 'age': 45, 'weight': 70, 'height': 175, 'activity_factor': 1.4,
     'disease': ['cvd']},
    {'name': 'Hypercholesterolemia',
     'gender': 'M', 'age': 45, 'weight': 70, 'height': 175, 'activity_factor': 1.4,
     'disease': ['cholesterol']},
    {'name': 'Chronic Kidney Disease Stage 1',
     'gender': 'M', 'age': 45, 'weight': 70, 'height': 175, 'activity_factor': 1.4,
     'disease': ['ckd']},
    {'name': 'Diabetes + Hipertensi',
     'gender': 'M', 'age': 45, 'weight': 70, 'height': 175, 'activity_factor': 1.4,
     'disease': ['dm2', 'hypertension']},
    {'name': 'Diabetes + Hiperkolesterolemia',
     'gender': 'M', 'age': 45, 'weight': 70, 'height': 175, 'activity_factor': 1.4,
     'disease': ['dm2', 'cholesterol']},
    {'name': 'Hipertensi + Kardiovaskular',
     'gender': 'M', 'age': 45, 'weight': 70, 'height': 175, 'activity_factor': 1.4,
     'disease': ['hypertension', 'cvd']},
    {'name': 'CKD + Hipertensi',
     'gender': 'M', 'age': 45, 'weight': 70, 'height': 175, 'activity_factor': 1.4,
     'disease': ['ckd', 'hypertension']},
    {'name': 'Diabetes + Hipertensi + Hiperkolesterolemia',
     'gender': 'M', 'age': 45, 'weight': 70, 'height': 175, 'activity_factor': 1.4,
     'disease': ['dm2', 'hypertension', 'cholesterol']},
    {'name': 'CKD + Diabetes + Hipertensi',
     'gender': 'M', 'age': 45, 'weight': 70, 'height': 175, 'activity_factor': 1.4,
     'disease': ['ckd', 'dm2', 'hypertension']},
    {'name': 'Hipertensi + Hiperkolesterolemia + CVD',
     'gender': 'M', 'age': 45, 'weight': 70, 'height': 175, 'activity_factor': 1.4,
     'disease': ['hypertension', 'cholesterol', 'cvd']},
]

def check_hard_violations(menu_plan, guideline_nutrients):
    if not menu_plan:
        return 999  # Failed to generate = maximum violations
        
    MACRO_MAP = {
        'energy_kcal':    menu_plan.total_daily_calories,
        'protein_g':      menu_plan.total_daily_protein_g,
        'carbohydrate_g': menu_plan.total_daily_carb_g,
        'fat_g':          menu_plan.total_daily_fat_g,
    }
    if hasattr(menu_plan, 'daily_micronutrients') and menu_plan.daily_micronutrients:
        MACRO_MAP.update(menu_plan.daily_micronutrients)
        
    violations = 0
    for nutrient, limits in guideline_nutrients.items():
        tipe = limits.get('hard_soft_type', 'SOFT')
        if nutrient not in MACRO_MAP:
            continue
        if tipe == 'HARD':
            actual_val = MACRO_MAP[nutrient]
            min_v = limits.get('min', 0)
            max_v = limits.get('max', float('inf'))
            if not (min_v <= actual_val <= max_v):
                violations += 1
    return violations

def main():
    print("==========================================================")
    print("      ADDITIONAL EVALUATION: GREEDY VS GENETIC ALGORITHM  ")
    print("==========================================================")
    
    try:
        nutrition_service = NutritionService()
    except Exception as e:
        print(f"[ERROR] Failed to initialize NutritionService: {e}")
        return

    output_dir = os.path.join(current_dir, 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    results = []
    
    # Run evaluations for each profile
    for idx, profile in enumerate(PROFILES):
        print(f"\n[{idx+1}/{len(PROFILES)}] Evaluating {profile['name']}...")
        
        try:
            analysis_result = nutrition_service.calculate_nutrition_needs(profile)
            if not analysis_result['success']:
                print(f"  [ERROR] Nutrition analysis failed: {analysis_result['error']}")
                continue
                
            tdee = analysis_result['energy']['tdee'] # type: ignore
            guidelines = analysis_result['guidelines'] # type: ignore
            food_database = analysis_result['food_data']['dataframe'] # type: ignore
            guideline_nutrients = guidelines.get('nutrients', {}) # type: ignore
            
            greedy_engine = GreedyAlgorithmInterface(food_database, guidelines)
            ga_engine = GeneticAlgorithmInterface(food_database, guidelines)
            
            # --- EVALUATE GREEDY ---
            greedy_times = []
            greedy_violations = []
            
            for _ in range(3):
                t_start = time.time()
                menu_plan = greedy_engine.generate_menu_plan(profile, tdee)
                greedy_times.append(time.time() - t_start)
                greedy_violations.append(check_hard_violations(menu_plan, guideline_nutrients))
                
            # --- EVALUATE GENETIC ALGORITHM ---
            ga_times = []
            ga_violations = []
            
            for _ in range(3):
                t_start = time.time()
                menu_plan = ga_engine.generate_menu_plan(profile, tdee)
                ga_times.append(time.time() - t_start)
                ga_violations.append(check_hard_violations(menu_plan, guideline_nutrients))
                
            # Compute stats
            mean_greedy_time = np.mean(greedy_times)
            mean_ga_time = np.mean(ga_times)
            
            # Feasibility rate = % of runs with 0 hard violations
            greedy_feasibility = sum(1 for v in greedy_violations if v == 0) / len(greedy_violations) * 100
            ga_feasibility = sum(1 for v in ga_violations if v == 0) / len(ga_violations) * 100
            
            results.append({
                'Profile': profile['name'],
                'Greedy Time (s)': mean_greedy_time,
                'GA Time (s)': mean_ga_time,
                'Greedy Feasibility (%)': greedy_feasibility,
                'GA Feasibility (%)': ga_feasibility
            })
            
            print(f"  Greedy: Time = {mean_greedy_time:.4f}s, Feasibility = {greedy_feasibility:.1f}%")
            print(f"  GA:     Time = {mean_ga_time:.4f}s, Feasibility = {ga_feasibility:.1f}%")
            
        except Exception as e:
            print(f"  [ERROR] Evaluation failed for {profile['name']}: {e}")
            
    if not results:
        print("[ERROR] No evaluation results collected.")
        return
        
    df_results = pd.DataFrame(results)
    df_results.to_csv(os.path.join(output_dir, 'additional_evaluation_summary.csv'), index=False)
    
    # ════════════════════════════════════════════════════════════════════════
    # PLOT 1: COMPILATION/EXECUTION TIME COMPARISON (Waktu komputasi)
    # ════════════════════════════════════════════════════════════════════════
    plt.figure(figsize=(12, 6))
    sns.set_style("whitegrid")
    x = np.arange(len(df_results['Profile']))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(12, 6))
    rects1 = ax.bar(x - width/2, df_results['Greedy Time (s)'], width, label='Greedy', color='teal')
    rects2 = ax.bar(x + width/2, df_results['GA Time (s)'], width, label='Genetic Algorithm', color='coral')
    
    ax.set_ylabel('Execution Time (seconds) - Log Scale')
    ax.set_yscale('log') # Use log scale because Greedy is extremely fast (milliseconds) vs GA (seconds)
    ax.set_title('Execution Time Comparison (Greedy vs Genetic Algorithm) - Lower is Better')
    ax.set_xticks(x)
    ax.set_xticklabels(df_results['Profile'], rotation=15, ha='right')
    ax.legend()
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'waktu_komputasi_comparison.png'), dpi=300)
    plt.close()
    
    # ════════════════════════════════════════════════════════════════════════
    # PLOT 2: FEASIBILITY RATE COMPARISON (Seberapa sering berhasil tanpa warning)
    # ════════════════════════════════════════════════════════════════════════
    plt.figure(figsize=(12, 6))
    fig, ax = plt.subplots(figsize=(12, 6))
    rects1 = ax.bar(x - width/2, df_results['Greedy Feasibility (%)'], width, label='Greedy', color='teal')
    rects2 = ax.bar(x + width/2, df_results['GA Feasibility (%)'], width, label='Genetic Algorithm', color='coral')
    
    ax.set_ylabel('Feasibility Rate (%, 0 Hard Violations)')
    ax.set_title('Feasibility Rate Comparison (Greedy vs Genetic Algorithm) - Higher is Better')
    ax.set_xticks(x)
    ax.set_xticklabels(df_results['Profile'], rotation=15, ha='right')
    ax.set_ylim(0, 110)
    ax.legend()
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'feasibility_rate_comparison.png'), dpi=300)
    plt.close()
    
    # ════════════════════════════════════════════════════════════════════════
    # PLOT 3: GA CONVERGENCE RATE (Seberapa dekat hasil akhir ke target ideal)
    # ════════════════════════════════════════════════════════════════════════
    # We choose the most complex profile: "CKD + Diabetes + Hipertensi" to show convergence
    print("\nRunning GA Convergence evaluation for 'CKD + Diabetes + Hipertensi'...")
    try:
        ckd_profile = next(p for p in PROFILES if p['name'] == 'CKD + Diabetes + Hipertensi')
        analysis_result = nutrition_service.calculate_nutrition_needs(ckd_profile)
        tdee = analysis_result['energy']['tdee'] # type: ignore
        guidelines = analysis_result['guidelines'] # type: ignore
        food_database = analysis_result['food_data']['dataframe'] # type: ignore
        
        # Flattened guidelines to match ga format
        converted_bag = ga_engine = GeneticAlgorithmInterface(food_database, guidelines).constraint_bag
        
        generation_sizes = [10, 30, 50, 80, 110, 150]
        fitness_scores = []
        
        for gens in generation_sizes:
            print(f"  Evaluating GA with {gens} generations...")
            best_sol, _ = run_ga(
                food_df=food_database,
                guidelines=converted_bag,
                tdee=tdee,
                generations=gens,
                pop_size=100,
                elite_ratio=0.15,
                mutation_rate=0.35,
                verbose=True
            )
            score = calculate_fitness(best_sol, converted_bag, tdee=tdee)
            fitness_scores.append(score)
            
        plt.figure(figsize=(10, 5))
        plt.plot(generation_sizes, fitness_scores, marker='o', linestyle='-', linewidth=2.5, color='coral', label='Best Fitness')
        plt.title('Genetic Algorithm Convergence Rate (CKD + Diabetes + Hipertensi)')
        plt.ylabel('Penalty / Fitness Score (Lower is Better)')
        plt.xlabel('Generations')
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'fitness_convergence_rate.png'), dpi=300)
        plt.close()
        print("Convergence plot generated successfully.")
        
    except Exception as e:
        print(f"  [ERROR] Failed to run convergence evaluation: {e}")

    print("\n==========================================================================================")
    print("                                   ADDITIONAL EVALUATION SUMMARY                           ")
    print("==========================================================================================")
    print(f"{'Profile':<42} | {'Greedy Time':<12} | {'GA Time':<12} | {'Greedy Feas.':<12} | {'GA Feas.':<12}")
    print("-" * 102)
    for row in results:
        print(f"{row['Profile']:<42} | {row['Greedy Time (s)']:<11.4f}s | {row['GA Time (s)']:<10.4f}s | {row['Greedy Feasibility (%)']:<10.1f}% | {row['GA Feasibility (%)']:<9.1f}%")
    print("==========================================================================================")
    print(f"All reports and charts saved to: {output_dir}")

if __name__ == "__main__":
    main()

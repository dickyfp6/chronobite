import sys
import os
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt # type: ignore
import seaborn as sns # type: ignore

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
root_dir = os.path.abspath(os.path.join(current_dir, '..', '..'))
sys.path.insert(0, parent_dir)
sys.path.insert(0, root_dir)
sys.path.insert(0, os.path.join(root_dir, 'C. System Flow'))
sys.path.insert(0, os.path.join(root_dir, 'D. Model'))
sys.path.insert(0, os.path.join(root_dir, 'D. Model', 'Greedy Algorithm'))
sys.path.insert(0, os.path.join(root_dir, 'D. Model', 'Genetic Algorithm'))

from b_nutrition_service import NutritionService # type: ignore
from greedy_interface import GreedyAlgorithmInterface # type: ignore
from c_ga_interface import GeneticAlgorithmInterface # type: ignore
from greedy_evaluation_26 import PROFILES # type: ignore

def main():
    print("==========================================")
    print(" RUNTIME COMPARISON: GREEDY VS GA ")
    print("==========================================")
    
    output_dir = os.path.join(current_dir, 'output', 'comparison_26')
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        nutrition_service = NutritionService()
    except Exception as e:
        print(f"[ERROR] Failed to initialize NutritionService: {e}")
        return

    results = []
    
    for i, profile in enumerate(PROFILES):
        print(f"\n[{i+1}/{len(PROFILES)}] Measuring runtime for {profile['name']}...")
        
        analysis_result = nutrition_service.calculate_nutrition_needs(profile)
        if not analysis_result['success']:
            print(f"  [ERROR] Nutrition analysis failed: {analysis_result.get('error')}")
            continue
            
        tdee = analysis_result['energy']['tdee'] # type: ignore
        guidelines = analysis_result['guidelines'] # type: ignore
        food_database = analysis_result['food_data']['dataframe'] # type: ignore
        
        # --- Run Greedy ---
        greedy_engine = GreedyAlgorithmInterface(food_database, guidelines)
        start_time = time.time()
        greedy_engine.generate_menu_plan(profile, tdee)
        greedy_time = time.time() - start_time
        print(f"  -> Greedy: {greedy_time:.4f} seconds")
        
        # --- Run GA ---
        ga_engine = GeneticAlgorithmInterface(food_database, guidelines)
        start_time = time.time()
        ga_engine.generate_menu_plan(profile, tdee)
        ga_time = time.time() - start_time
        print(f"  -> GA: {ga_time:.4f} seconds")
        
        results.append({
            'Profile': profile['name'],
            'Greedy Runtime (s)': round(greedy_time, 4),
            'GA Runtime (s)': round(ga_time, 4)
        })
        
    df = pd.DataFrame(results)
    csv_path = os.path.join(output_dir, 'runtime_comparison.csv')
    df.to_csv(csv_path, index=False)
    print(f"\n==========================================")
    print(f"Results saved to {csv_path}")
    
    # --- Plotting ---
    plt.figure(figsize=(14, 7))
    x = np.arange(len(df['Profile']))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(14, 7))
    rects1 = ax.bar(x - width/2, df['Greedy Runtime (s)'], width, label='Greedy', color='gold')
    rects2 = ax.bar(x + width/2, df['GA Runtime (s)'], width, label='Genetic Algorithm', color='purple')
    
    ax.set_ylabel('Execution Time (seconds)')
    ax.set_title('Runtime Comparison: Greedy vs Genetic Algorithm')
    ax.set_xticks(x)
    ax.set_xticklabels(df['Profile'], rotation=45, ha='right')
    ax.legend()
    
    # Optional: Use log scale because GA is usually much slower than Greedy
    # ax.set_yscale('log')
    
    # Add labels on top of the bars
    def add_labels(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height:.2f}',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=8, rotation=90)
                        
    add_labels(rects1)
    add_labels(rects2)
    
    plt.tight_layout()
    chart_path = os.path.join(output_dir, 'runtime_comparison.png')
    plt.savefig(chart_path, dpi=300)
    plt.close()
    print(f"Chart saved to {chart_path}")

if __name__ == "__main__":
    main()

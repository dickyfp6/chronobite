import sys
import os
import pandas as pd
import matplotlib.pyplot as plt # type: ignore
import seaborn as sns # type: ignore

# Add paths to sys.path to access required modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
sys.path.insert(0, os.path.join(parent_dir, 'C. System Flow'))
sys.path.insert(0, os.path.join(parent_dir, 'D. Model'))
sys.path.insert(0, os.path.join(parent_dir, 'D. Model', 'greedy'))

from nutrition_service import NutritionService # type: ignore
from greedy_interface import GreedyAlgorithmInterface # type: ignore

# Test Profiles
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

def main():
    print("==========================================")
    print(" GREEDY ALGORITHM EVALUATION FRAMEWORK ")
    print("==========================================")
    
    # Initialize Nutrition Service
    try:
        nutrition_service = NutritionService()
    except Exception as e:
        print(f"[ERROR] Failed to initialize NutritionService: {e}")
        return

    output_dir = os.path.join(current_dir, 'output', 'greedy')
    os.makedirs(output_dir, exist_ok=True)
    
    results_summary = []
    
    for i, profile in enumerate(PROFILES):
        print(f"\n[{i+1}/{len(PROFILES)}] Running Greedy for {profile['name']} profile...")
        
        try:
            # 1. Analyze profile
            analysis_result = nutrition_service.calculate_nutrition_needs(profile)
            if not analysis_result['success']:
                print(f"  [ERROR] Nutrition analysis failed: {analysis_result['error']}")
                continue
                
            tdee = analysis_result['energy']['tdee'] # type: ignore
            guidelines = analysis_result['guidelines'] # type: ignore
            food_database = analysis_result['food_data']['dataframe'] # type: ignore
            
            # Extract constraint values for later calculation
            guideline_nutrients = guidelines.get('nutrients', {}) # type: ignore
            
            # 2. Run Greedy
            greedy_engine = GreedyAlgorithmInterface(food_database, guidelines)
            menu_plan = greedy_engine.generate_menu_plan(profile, tdee)
            
            if not menu_plan:
                print("  [ERROR] Failed to generate menu plan")
                continue

            # 3. Build actual nutrients from menu_plan tracked macros
            # MenuPlan stores 4 macros with keys matching guideline key names exactly
            MACRO_MAP = {
                'energy_kcal':    menu_plan.total_daily_calories,
                'protein_g':      menu_plan.total_daily_protein_g,
                'carbohydrate_g': menu_plan.total_daily_carb_g,
                'fat_g':          menu_plan.total_daily_fat_g,
            }
            # Also include daily_micronutrients if the algorithm populated them
            if hasattr(menu_plan, 'daily_micronutrients') and menu_plan.daily_micronutrients:
                MACRO_MAP.update(menu_plan.daily_micronutrients)
            # 4. Deviation & Constraint Analysis — HARD constraints only on tracked macros
            deviations = []
            hard_constraints_passed = 0
            total_hard_constraints = 0
            
            for nutrient, limits in guideline_nutrients.items():
                tipe = limits.get('hard_soft_type', 'SOFT')

                # Only evaluate if we have actual data for this nutrient
                if nutrient not in MACRO_MAP:
                    # Skip micronutrients — MenuPlan doesn't track them
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
                    
            satisfaction_rate = (hard_constraints_passed / total_hard_constraints * 100) if total_hard_constraints > 0 else 100
            avg_deviation = sum(d['deviation_pct'] for d in deviations) / len(deviations) if deviations else 0

            # Log results
            results_summary.append({
                'Profile': profile['name'],
                'CS Rate': satisfaction_rate,
                'Avg Deviation': avg_deviation
            })

            
            # Plot Deviation Chart for this profile
            if deviations:
                plt.figure(figsize=(12, 6))
                sns.set_style("whitegrid")
                dev_df = pd.DataFrame(deviations)
                dev_df = dev_df.sort_values('deviation_pct', ascending=False)
                
                sns.barplot(data=dev_df, x='nutrient', y='deviation_pct', hue='type')
                plt.title(f"Deviation Analysis - Greedy - {profile['name']}")
                plt.ylabel("Deviation from Target (%)")
                plt.xlabel("Nutrient")
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                plt.savefig(os.path.join(output_dir, f"deviation_{i+1}_greedy.png"), dpi=300)
                plt.close()
                
            print(f"  -> CS Rate: {satisfaction_rate:.1f}%")
            print(f"  -> Avg Deviation: {avg_deviation:.1f}%")
            
        except Exception as e:
            print(f"  [ERROR] {e}")
            import traceback
            traceback.print_exc()

    # Save summary
    if results_summary:
        summary_df = pd.DataFrame(results_summary)
        summary_df.to_csv(os.path.join(output_dir, 'summary.csv'), index=False)
        
        # Plot overall constraint satisfaction
        plt.figure(figsize=(10, 6))
        sns.barplot(data=summary_df, x='Profile', y='CS Rate', color='teal')
        plt.title('Constraint Satisfaction Rate by Profile (Greedy Algorithm)')
        plt.ylabel('Satisfaction Rate (%)')
        plt.ylim(0, 100)
        plt.xticks(rotation=15)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'overall_cs_greedy.png'), dpi=300)
        plt.close()

        print("\n==========================================")
        print(f"{'Profile':<50} | {'CS Rate':<10} | {'Avg Deviation':<15}")
        print("-" * 80)
        for row in results_summary:
            print(f"{row['Profile']:<50} | {row['CS Rate']:<8.1f}% | {row['Avg Deviation']:<13.1f}%")
        print("==========================================")

if __name__ == "__main__":
    main()

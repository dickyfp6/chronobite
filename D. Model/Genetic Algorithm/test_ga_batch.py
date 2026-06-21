"""
BATCH GENETIC ALGORITHM RUNNER - CSR-based filtering and selective export
==========================================================================

Batch runner yang menjalankan GA otomatis beberapa kali per case, 
filter by CSR (Constraint Satisfaction Rate), dan export Excel hanya 
yang memenuhi threshold.

Flow per case:
1. Jalankan GA + Local Search + auto-select opsi 1 semua slot (sama persis dengan test_ga_auto.py)
2. Hitung CSR menggunakan logic yang sama dengan export_to_excel() 
3. Jika CSR >= threshold → export Excel dan stop run untuk case itu
4. Jika setelah MAX_RUNS tidak ada yang >= threshold → export 1 run dengan CSR tertinggi 
   dengan suffix `_best_of_10`

Output naming:
- Kalau CSR >= threshold: batch_{disease}_{run_number}.xlsx
- Kalau fallback best: batch_{disease}_best_of_10.xlsx
"""

import sys
import os
import random
import numpy as np
import pandas as pd
import traceback

# Add paths untuk import
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
system_flow_path = os.path.join(project_root, 'C. System Flow')
genetic_algorithm_path = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, system_flow_path)
sys.path.insert(0, genetic_algorithm_path)

# Import GA engine
# pyrefly: ignore [missing-import]
from ga_v3 import (
    run_ga_numpy as run_ga, generate_meal_options, calculate_total_nutrition, 
    SLOT_NAMES, CHROMOSOME_SIZE, calculate_portion_sizes_dynamic,
    local_search, calculate_total_nutrition_from_portions
)
from ga_config import GA_PARAMS, LS_PARAMS

# Import dari test_ga.py - CSR calculation dan export
import importlib.util
test_ga_path = os.path.join(genetic_algorithm_path, 'test_ga.py')
spec = importlib.util.spec_from_file_location("test_ga", test_ga_path)
assert spec is not None, f"Cannot load module spec from {test_ga_path}"
test_ga = importlib.util.module_from_spec(spec)
sys.modules["test_ga"] = test_ga
spec.loader.exec_module(test_ga)

export_to_excel = test_ga.export_to_excel
HARD_NUTRIENT_KEY_MAP = test_ga.HARD_NUTRIENT_KEY_MAP
lookup_nutrition = test_ga.lookup_nutrition

# Import NutritionService
try:
    from b_nutrition_service import NutritionService
    print("✓ NutritionService imported successfully")
except ImportError as e:
    print(f"✗ Cannot import NutritionService: {e}")
    sys.exit(1)


# ════════════════════════════════════════════════════════════════════════
# BATCH CONFIGURATION
# ════════════════════════════════════════════════════════════════════════

BATCH_PROFILES = [
    # Normal & Single Disease — profil 1
   # {'gender': 'M', 'age': 28, 'weight': 68.0, 'height': 178.0, 'activity_factor': 1.845, 'disease': ['dm2'], 'food_preferences': []},
   # {'gender': 'M', 'age': 28, 'weight': 68.0, 'height': 178.0, 'activity_factor': 1.845, 'disease': ['hypertension'], 'food_preferences': []},
   # {'gender': 'M', 'age': 28, 'weight': 68.0, 'height': 178.0, 'activity_factor': 1.845, 'disease': ['cvd'], 'food_preferences': []},
   # {'gender': 'M', 'age': 28, 'weight': 68.0, 'height': 178.0, 'activity_factor': 1.845, 'disease': ['cholesterol'], 'food_preferences': []},
   # {'gender': 'M', 'age': 28, 'weight': 68.0, 'height': 178.0, 'activity_factor': 1.845, 'disease': ['ckd'], 'food_preferences': []},
    # Dual Disease — profil 2
    # {'gender': 'F', 'age': 55, 'weight': 83.0, 'height': 162.0, 'activity_factor': 1.545, 'disease': ['dm2', 'hypertension'], 'food_preferences': []},
    # {'gender': 'F', 'age': 55, 'weight': 83.0, 'height': 162.0, 'activity_factor': 1.545, 'disease': ['dm2', 'cholesterol'], 'food_preferences': []},
    # {'gender': 'F', 'age': 55, 'weight': 83.0, 'height': 162.0, 'activity_factor': 1.545, 'disease': ['hypertension', 'cvd'], 'food_preferences': []},
    # {'gender': 'F', 'age': 55, 'weight': 83.0, 'height': 162.0, 'activity_factor': 1.545, 'disease': ['ckd', 'hypertension'], 'food_preferences': []},
    # Triple Disease — profil 3
     {'gender': 'M', 'age': 34, 'weight': 51.0, 'height': 178.0, 'activity_factor': 2.2, 'disease': ['dm2', 'hypertension', 'cholesterol'], 'food_preferences': []},
    # {'gender': 'M', 'age': 34, 'weight': 51.0, 'height': 178.0, 'activity_factor': 2.2, 'disease': ['ckd', 'dm2', 'hypertension'], 'food_preferences': []},
    # {'gender': 'M', 'age': 34, 'weight': 51.0, 'height': 178.0, 'activity_factor': 2.2, 'disease': ['hypertension', 'cholesterol', 'cvd'], 'food_preferences': []},
]

MAX_RUNS = 10        # Jalankan maksimal 10x per case
CSR_THRESHOLD = 100.0 # Export kalau CSR >= 100%


# ════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ════════════════════════════════════════════════════════════════════════

def calculate_csr(total_nutrition, guidelines):
    """
    Calculate CSR (Constraint Satisfaction Rate) - HARD constraints only
    
    Logic konsisten dengan export_to_excel() di test_ga.py
    - Binary strict: min_val <= actual <= max_val → constraint passed
    - CSR = (hard_constraints_passed / total_hard_constraints * 100)
    
    Args:
        total_nutrition: Dict hasil calculate_total_nutrition() 
        guidelines: Dict dengan struktur {'hard': {...}, 'soft': {...}}
    
    Returns:
        float: CSR percentage (0-100)
    """
    hard_constraints_passed = 0
    total_hard_constraints = 0
    
    for nutrient_key, constraint in guidelines['hard'].items():
        min_val = constraint.get('min', 0)
        max_val = constraint.get('max', float('inf'))
        actual = lookup_nutrition(total_nutrition, nutrient_key, HARD_NUTRIENT_KEY_MAP)
        
        if actual is not None:
            total_hard_constraints += 1
            if min_val <= actual <= max_val:
                hard_constraints_passed += 1
    
    csr = (hard_constraints_passed / total_hard_constraints * 100) if total_hard_constraints > 0 else 0
    return csr


def run_single_ga(user_input, nutrition_service):
    """
    Run single GA iteration - same logic as test_ga_auto.py
    
    Returns:
        tuple: (best_solution, selected_df, portion_result_df, nutrition_result, guidelines, tdee, total_nutrition)
        or None if failed
    """
    try:
        # STEP 1: Calculate nutrition requirements
        nutrition_result = nutrition_service.calculate_nutrition_needs(user_input)
        
        if not nutrition_result['success']:
            return None
        
        # STEP 2: Extract data
        food_df = nutrition_result['food_data']['dataframe']
        guidelines_all = nutrition_result['guidelines']['nutrients']
        tdee = nutrition_result['energy']['tdee']
        
        # Split guidelines berdasarkan hard_soft_type
        guidelines = {
            'hard': {k: v for k, v in guidelines_all.items() if v.get('hard_soft_type') == 'HARD'},
            'soft': {k: v for k, v in guidelines_all.items() if v.get('hard_soft_type') != 'HARD'}
        }
        
        # STEP 3: Run GA
        best_solution, top_solutions = run_ga(
            food_df=food_df,
            guidelines=guidelines,
            tdee=tdee,
            **GA_PARAMS,
            verbose=False,
            deadline=None
        )
        
        # STEP 5: Generate meal options dan auto-select opsi 1 semua slot
        top_solutions_with_best = [best_solution] + top_solutions
        slot_options = generate_meal_options(
            food_df,
            top_solutions_with_best,
            max_options_per_slot=3,
            food_preferences=user_input['food_preferences']
        )
        
        # Auto-select opsi 1 untuk semua slot
        selected_meal = []
        for slot_name in SLOT_NAMES:
            options = slot_options.get(slot_name, [])
            if options:
                selected_item = options[0].copy()
                selected_meal.append(selected_item)
        
        if len(selected_meal) != CHROMOSOME_SIZE:
            return None
        
        # Convert to DataFrame
        selected_df = pd.DataFrame(selected_meal).reset_index(drop=True)
        
        # STEP 6: Calculate portion sizes
        portion_result_df = selected_df  # sudah diportioning oleh indices_to_dataframe di ga_v3
        # Calculate total nutrition
        total_nutrition = calculate_total_nutrition_from_portions(portion_result_df)

        return (best_solution, selected_df, portion_result_df, nutrition_result, guidelines, tdee, total_nutrition)
    
    except Exception as e:
        print(f"    ✗ GA run failed: {str(e)}")
        return None


def batch_runner(profile):
    """
    Run batch GA untuk satu profile dengan CSR filtering
    
    Args:
        profile: User input profile dict
    
    Returns:
        tuple: (best_run_data, best_csr, threshold_met)
    """
    disease_str = "_".join(profile['disease'])
    
    print(f"\n{'█'*70}")
    print(f"BATCH RUNNER: {disease_str.upper()}")
    print(f"{'█'*70}")
    print(f"Max runs: {MAX_RUNS}, CSR threshold: {CSR_THRESHOLD}%\n")
    
    # Initialize
    service = NutritionService()
    best_run_data = None
    best_csr = 0.0
    threshold_met = False
    run_results = []
    
    # Loop MAX_RUNS
    for run_num in range(1, MAX_RUNS + 1):
        print(f"[{disease_str.upper()}] Run {run_num}/{MAX_RUNS}...", end=" ", flush=True)
        
        # Run GA
        result = run_single_ga(profile, service)
        
        if result is None:
            print(f"FAILED")
            continue
        
        best_solution, selected_df, portion_result_df, nutrition_result, guidelines, tdee, total_nutrition = result
        
        # Calculate CSR
        csr = calculate_csr(total_nutrition, guidelines)
        
        print(f"CSR: {csr:.1f}%", end="")
        
        # Store result
        run_results.append({
            'run_num': run_num,
            'csr': csr,
            'data': result
        })
        
        # Check threshold
        if csr >= CSR_THRESHOLD:
            print(f" — THRESHOLD MET! Exporting and stopping...")
            threshold_met = True
            best_run_data = result
            best_csr = csr
            break
        elif csr > best_csr:
            print(f" — new best", end="")
            best_csr = csr
            best_run_data = result
            print()
        else:
            print(f" — below threshold, continuing")
    
    # If no threshold met, use best result
    if not threshold_met and best_run_data is not None:
        best_run = next((r for r in run_results if r['csr'] == best_csr), None)
        if best_run:
            run_num = best_run['run_num']
            print(f"\n[{disease_str.upper()}] Run {MAX_RUNS}/{MAX_RUNS}... all runs done, exporting best (CSR: {best_csr:.5f}%)")
    
    return best_run_data, best_csr, threshold_met, run_results


def export_batch_result(profile, best_run_data, best_csr, threshold_met, run_results):
    """
    Export batch result ke Excel
    
    Args:
        profile: User input profile
        best_run_data: Result tuple dari run_single_ga
        best_csr: CSR value
        threshold_met: Boolean flag
        run_results: List of run results untuk determine run_num
    """
    if best_run_data is None:
        print(f"  ✗ No valid results to export")
        return
    
    disease_str = "_".join(profile['disease'])
    best_solution, selected_df, portion_result_df, nutrition_result, guidelines, tdee, total_nutrition = best_run_data
    guidelines_all = nutrition_result['guidelines']['nutrients']
    
    # Determine filename
    if threshold_met:
        # Find which run number this was
        best_run = next((r for r in run_results if r['csr'] >= CSR_THRESHOLD), None)
        if best_run:
            run_num = best_run['run_num']
            excel_filename = f"batch_{disease_str}_run{run_num}.xlsx"
        else:
            excel_filename = f"batch_{disease_str}_run1.xlsx"
    else:
        excel_filename = f"batch_{disease_str}_best_of_10.xlsx"
    
    # Set output path
    output_dir = os.path.dirname(os.path.abspath(__file__))
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    excel_filepath = os.path.join(output_dir, excel_filename)
    
    # Export
    success = export_to_excel(
        filename=excel_filepath,
        user_input=profile,
        nutrition_result=nutrition_result,
        guidelines_all=guidelines_all,
        selected_df=selected_df,
        portion_result_df=portion_result_df,
        guidelines=guidelines,
        tdee=tdee,
        best_solution=best_solution
    )
    
    if success:
        print(f"  ✓ Exported: {excel_filename}")
    else:
        print(f"  ✗ Export failed for {excel_filename}")


# ════════════════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n" + "="*70)
    print("BATCH GA RUNNER - CSR-BASED FILTERING")
    print("="*70)
    print(f"Profiles: {len(BATCH_PROFILES)}")
    print(f"Max runs per case: {MAX_RUNS}")
    print(f"CSR threshold: {CSR_THRESHOLD}%\n")
    
    for profile_idx, profile in enumerate(BATCH_PROFILES, 1):
        try:
            # Run batch
            best_run_data, best_csr, threshold_met, run_results = batch_runner(profile)
            
            # Export result
            if best_run_data:
                export_batch_result(profile, best_run_data, best_csr, threshold_met, run_results)
            else:
                print(f"  ✗ No valid results for profile {profile_idx}")
            
            print(f"\n{'─'*70}")
        
        except Exception as e:
            print(f"\n✗ ERROR in profile {profile_idx}: {str(e)}")
            traceback.print_exc()
    
    print("\n" + "="*70)
    print("✓ BATCH GA RUNNER COMPLETE")
    print("="*70)

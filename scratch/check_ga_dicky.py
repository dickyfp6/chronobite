import sys
import os
import pandas as pd
import numpy as np

# Adjust paths
project_root = r"c:\Users\USERR\Documents\0. Mata Kuliah\8 -TA\Code\TugasAkhirDSS"
sys.path.insert(0, os.path.join(project_root, 'C. System Flow'))
sys.path.insert(0, os.path.join(project_root, 'D. Model', 'Genetic Algorithm'))

from nutrition_service import NutritionService
from ga_dicky import run_ga_numpy as run_ga, local_search, validate_final_solution
# Import config parameters
from ga_config import GA_PARAMS, LS_PARAMS

PROFILES = [
    {'name': 'Normal',                                'disease': ['normal']},
    {'name': 'Diabetes Melitus Type 2',               'disease': ['dm2']},
    {'name': 'Hypertension',                          'disease': ['hypertension']},
    {'name': 'Cardiovascular Disease',                'disease': ['cvd']},
    {'name': 'Hypercholesterolemia',                  'disease': ['cholesterol']},
    {'name': 'Chronic Kidney Disease Stage 1',        'disease': ['ckd']},
    {'name': 'Diabetes + Hipertensi',                 'disease': ['dm2', 'hypertension']},
    {'name': 'Diabetes + Hiperkolesterolemia',        'disease': ['dm2', 'cholesterol']},
    {'name': 'Hipertensi + Kardiovaskular',           'disease': ['hypertension', 'cvd']},
    {'name': 'CKD + Hipertensi',                      'disease': ['ckd', 'hypertension']},
    {'name': 'Diabetes + Hipertensi + Hiperkolesterolemia', 'disease': ['dm2', 'hypertension', 'cholesterol']},
    {'name': 'CKD + Diabetes + Hipertensi',           'disease': ['ckd', 'dm2', 'hypertension']},
    {'name': 'Hipertensi + Hiperkolesterolemia + CVD','disease': ['hypertension', 'cholesterol', 'cvd']},
]

def check_profile(profile, service):
    print(f"\n==================================================")
    print(f"PROFILE: {profile['name']} ({', '.join(profile['disease'])})")
    print(f"==================================================")
    
    # User input arguments
    user_input = {
        'gender': 'M',
        'age': 45,
        'weight': 70.0,
        'height': 175.0,
        'activity_factor': 1.4,
        'disease': profile['disease'],
        'food_preferences': []
    }
    
    # Calculate nutrition needs
    nutrition_result = service.calculate_nutrition_needs(user_input)
    if not nutrition_result['success']:
        print("✗ Nutrition calculator failed")
        return
    
    food_df = nutrition_result['food_data']['dataframe']
    guidelines_all = nutrition_result['guidelines']['nutrients']
    tdee = nutrition_result['energy']['tdee']
    
    # Split guidelines into hard/soft
    guidelines = {
        'hard': {k: v for k, v in guidelines_all.items() if v.get('hard_soft_type') == 'HARD'},
        'soft': {k: v for k, v in guidelines_all.items() if v.get('hard_soft_type') != 'HARD'}
    }
    
    print(f"TDEE: {tdee:.1f} kcal")
    print(f"Hard constraints: {list(guidelines['hard'].keys())}")
    
    # Run GA
    best_solution, top_solutions = run_ga(
        food_df=food_df,
        guidelines=guidelines,
        tdee=tdee,
        generations=GA_PARAMS.get('generations', 150),
        pop_size=GA_PARAMS.get('pop_size', 120),
        elite_ratio=GA_PARAMS.get('elite_ratio', 0.15),
        mutation_rate=GA_PARAMS.get('mutation_rate', 0.25),
        verbose=False
    )
    
    if best_solution is None:
        print("✗ GA run returned None")
        return
        
    print(f"GA Run best solution shape: {best_solution.shape}")
    
    # Run Local Search
    best_solution = local_search(
        solution=best_solution,
        food_df=food_df,
        guidelines=guidelines,
        tdee=tdee,
        iterations=LS_PARAMS.get('iterations', 50),
        verbose=False
    )
    
    # Validate final solution
    validation = validate_final_solution(best_solution, guidelines, tdee=tdee)
    print(f"Compliance Rate: {validation['compliance_rate']:.1f}%")
    print(f"Is Valid: {validation['is_valid']}")
    print(f"Summary: {validation['summary']}")
    if not validation['is_valid']:
        print("Violations:")
        for v in validation['violations']:
            print(f"  - {v[0]}: actual={v[1]:.2f}, target range={v[2]}-{v[3]} ({v[4]})")

def main():
    service = NutritionService()
    for profile in PROFILES:
        try:
            check_profile(profile, service)
        except Exception as e:
            print(f"✗ Error checking profile {profile['name']}: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()

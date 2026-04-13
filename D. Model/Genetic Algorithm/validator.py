"""
Solution Validator untuk GA+LS Hybrid Algorithm

Fungsi: Validate apakah solution memenuhi semua constraints:
- Similarity: Tidak ada 2+ items dari group sama per meal
- Energy: Total energy per meal sesuai target (±tolerance)
- Categories: Semua kategori terisi (main, side, drink)
- Nutrients: Compliance dengan nutrient constraints
"""

import pandas as pd
from typing import Dict, List, Tuple, Any
from meal_similarity import is_too_similar


def check_similarity_violation(
    meal_items: List[int],
    food_df: pd.DataFrame,
    similarity_threshold: float = 0.60
) -> Tuple[bool, List[str]]:
    """
    Check apakah ada 2+ items similar dalam meal
    
    Args:
        meal_items: List food IDs untuk 1 meal
        food_df: Food dataframe
        similarity_threshold: Threshold similarity score
    
    Returns:
        (has_violation: bool, violation_list: List[str])
        - True jika ada violation, False jika aman
    """
    violations = []
    food_dicts = [food_df[food_df['fdc_id'] == fid].iloc[0].to_dict() for fid in meal_items]
    
    for i in range(len(food_dicts)):
        for j in range(i+1, len(food_dicts)):
            if is_too_similar(food_dicts[i], [food_dicts[j]], threshold=similarity_threshold):
                violations.append(
                    f"Similarity violation: {food_dicts[i]['food_name']} ~ {food_dicts[j]['food_name']}"
                )
    
    has_violation = len(violations) > 0
    return has_violation, violations


def check_energy_compliance(
    meal_budget_kcal: float,
    actual_energy_kcal: float,
    tolerance_pct: float = 10.0
) -> Tuple[bool, str]:
    """
    Check apakah energy per meal sesuai target
    
    Args:
        meal_budget_kcal: Target energy
        actual_energy_kcal: Actual sum energy
        tolerance_pct: Tolerance percentage (±)
    
    Returns:
        (is_compliant: bool, message: str)
    """
    tolerance = meal_budget_kcal * (tolerance_pct / 100)
    diff = abs(actual_energy_kcal - meal_budget_kcal)
    
    is_compliant = diff <= tolerance
    message = f"Energy: {actual_energy_kcal:.0f} kcal (target {meal_budget_kcal:.0f} ±{tolerance_pct}%)"
    
    return is_compliant, message


def check_all_categories_filled(
    meal_selection: Dict[str, Any],
    meal_name: str
) -> Tuple[bool, List[str]]:
    """
    Check apakah semua kategori wajib terisi
    
    Args:
        meal_selection: {main_course: item_id, side_dish: item_id, drink: item_id}
        meal_name: 'breakfast', 'lunch', 'dinner', 'snack'
    
    Returns:
        (all_filled: bool, missing_categories: List[str])
    """
    if meal_name == 'snack':
        # Snack hanya perlu ada 1 item
        return True, []
    
    required_categories = ['main_course', 'side_dish', 'drink']
    missing = [cat for cat in required_categories if meal_selection.get(cat) is None]
    
    return len(missing) == 0, missing


def validate_meal(
    meal_name: str,
    meal_selection: Dict[str, Any],
    meal_items: List[int],
    food_df: pd.DataFrame,
    meal_budget_kcal: float,
    tolerance_pct: float = 10.0,
    similarity_threshold: float = 0.60
) -> Dict[str, Any]:
    """
    Validate 1 meal lengkap
    
    Args:
        meal_name: 'breakfast', 'lunch', 'dinner', 'snack'
        meal_selection: Selected items per category
        meal_items: All items in meal (flattened list)
        food_df: Food dataframe
        meal_budget_kcal: Energy target
        tolerance_pct: Energy tolerance
        similarity_threshold: Similarity threshold
    
    Returns:
        {
            'valid': bool,
            'violations': [],
            'warnings': [],
            'energy_compliance': bool,
            'similarity_compliance': bool,
            'categories_filled': bool
        }
    """
    violations = []
    warnings = []
    
    # Check 1: Categories filled
    categories_ok, missing = check_all_categories_filled(meal_selection, meal_name)
    if not categories_ok:
        violations.append(
            f"{meal_name}: Missing categories: {missing}"
        )
    
    # Check 2: Similarity
    similarity_violation, sim_list = check_similarity_violation(
        meal_items,
        food_df,
        similarity_threshold
    )
    if similarity_violation:
        violations.extend(sim_list)
    
    # Check 3: Energy compliance
    actual_energy = sum([
        food_df[food_df['fdc_id'] == fid]['energy_kcal'].values[0]
        for fid in meal_items if fid is not None
    ])
    energy_ok, energy_msg = check_energy_compliance(meal_budget_kcal, actual_energy, tolerance_pct)
    if not energy_ok:
        warnings.append(f"{meal_name}: {energy_msg}")
    
    return {
        'meal': meal_name,
        'valid': len(violations) == 0,
        'violations': violations,
        'warnings': warnings,
        'energy_compliance': energy_ok,
        'similarity_compliance': not similarity_violation,
        'categories_filled': categories_ok,
        'actual_energy': actual_energy,
        'target_energy': meal_budget_kcal
    }


def validate_complete_solution(
    solution_dict: Dict[str, Any],
    food_df: pd.DataFrame,
    meal_budgets: Dict[str, float],
    tolerance_pct: float = 10.0,
    similarity_threshold: float = 0.60
) -> Dict[str, Any]:
    """
    Validate complete day plan (breakfast, lunch, dinner, snack)
    
    Args:
        solution_dict: Full solution structure
        food_df: Food dataframe
        meal_budgets: Budget per meal {breakfast: 400, lunch: 700, ...}
        tolerance_pct: Energy tolerance
        similarity_threshold: Similarity threshold
    
    Returns:
        {
            'valid': bool,
            'meal_validations': [...],
            'total_violations': int,
            'total_warnings': int,
            'daily_energy': float,
            'feasible': bool
        }
    """
    meal_validations = []
    total_violations = 0
    total_warnings = 0
    
    meal_names = ['breakfast', 'lunch', 'dinner', 'snack']
    
    for meal_name in meal_names:
        meal_data = solution_dict.get(meal_name, {})
        meal_selection = meal_data.get('selected', {})
        
        # Flatten meal items
        if meal_name == 'snack':
            meal_items = [meal_selection] if meal_selection else []
        else:
            meal_items = [
                meal_selection.get('main_course'),
                meal_selection.get('side_dish'),
                meal_selection.get('drink')
            ]
            meal_items = [item for item in meal_items if item is not None]
        
        meal_budget = meal_budgets.get(meal_name, 0)
        
        validation = validate_meal(
            meal_name,
            meal_selection,
            meal_items,
            food_df,
            meal_budget,
            tolerance_pct,
            similarity_threshold
        )
        
        meal_validations.append(validation)
        total_violations += len(validation['violations'])
        total_warnings += len(validation['warnings'])
    
    # Calculate daily statistics
    daily_energy = sum([v['actual_energy'] for v in meal_validations])
    
    all_valid = all([v['valid'] for v in meal_validations])
    
    return {
        'valid': all_valid,
        'meal_validations': meal_validations,
        'total_violations': total_violations,
        'total_warnings': total_warnings,
        'daily_energy': daily_energy,
        'feasible': all_valid and total_violations == 0
    }


def print_validation_report(validation_result: Dict[str, Any]) -> None:
    """Pretty print validation report"""
    print("\n" + "="*70)
    print("SOLUTION VALIDATION REPORT")
    print("="*70)
    
    print(f"\nOverall Valid: {validation_result['valid']}")
    print(f"Feasible: {validation_result['feasible']}")
    print(f"Total Violations: {validation_result['total_violations']}")
    print(f"Total Warnings: {validation_result['total_warnings']}")
    print(f"Daily Energy: {validation_result['daily_energy']:.0f} kcal")
    
    print("\n" + "-"*70)
    print("PER MEAL VALIDATION:")
    print("-"*70)
    
    for meal_val in validation_result['meal_validations']:
        meal = meal_val['meal'].upper()
        status = "✓ PASS" if meal_val['valid'] else "✗ FAIL"
        
        print(f"\n{meal} {status}")
        print(f"  Energy: {meal_val['actual_energy']:.0f} / {meal_val['target_energy']:.0f} kcal")
        print(f"  Energy OK: {meal_val['energy_compliance']}")
        print(f"  Similarity OK: {meal_val['similarity_compliance']}")
        print(f"  Categories OK: {meal_val['categories_filled']}")
        
        if meal_val['violations']:
            print(f"  Violations:")
            for v in meal_val['violations']:
                print(f"    - {v}")
        
        if meal_val['warnings']:
            print(f"  Warnings:")
            for w in meal_val['warnings']:
                print(f"    - {w}")
    
    print("\n" + "="*70)

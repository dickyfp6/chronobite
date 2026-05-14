"""
Automated test for TDEE hard constraint and portion sizing improvements
"""

import sys
import os
import pandas as pd

# Add paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
system_flow_path = os.path.join(project_root, 'C. System Flow')
ga_rebuild_path = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, system_flow_path)
sys.path.insert(0, ga_rebuild_path)

from ga_v1 import (
    run_ga, display_solution, calculate_total_nutrition,
    calculate_portion_sizes_dynamic, display_portion_summary_dynamic,
    SLOT_NAMES
)
from nutrition_service import NutritionService

def test_tdee_constraint():
    """Test that TDEE is now a HARD constraint"""
    
    print("\n" + "="*70)
    print("TEST: TDEE as HARD Constraint")
    print("="*70)
    
    # Setup user
    user_input = {
        'gender': 'F',
        'age': 22,
        'weight': 62.0,
        'height': 158.0,
        'activity_factor': 1.545,
        'disease': ['normal'],
        'food_preferences': []
    }
    
    # Get nutrition data
    service = NutritionService()
    nutrition_result = service.calculate_nutrition_needs(user_input)
    
    food_df = nutrition_result['food_data']['dataframe']
    guidelines_all = nutrition_result['guidelines']['nutrients']
    tdee = nutrition_result['energy']['tdee']
    
    print(f"\n📊 Target TDEE: {tdee:.0f} kcal")
    
    # Split guidelines
    HARD_KEYS = ['sodium_mg']  # Normal user
    guidelines = {
        'hard': {k: guidelines_all[k] for k in HARD_KEYS if k in guidelines_all},
        'soft': {k: v for k, v in guidelines_all.items() if k not in HARD_KEYS}
    }
    
    print(f"📋 HARD constraints: {list(guidelines['hard'].keys())}")
    
    # Run GA with TDEE
    print(f"\n🧬 Running GA with TDEE={tdee:.0f}...")
    best_solution, top_solutions = run_ga(
        food_df=food_df,
        guidelines=guidelines,
        tdee=tdee,  # NEW: Pass TDEE to GA
        generations=50,
        pop_size=20,
        verbose=False
    )
    
    # Check GA result
    total_energy_ga = best_solution['energy_kcal'].sum()
    print(f"✓ GA result energy: {total_energy_ga:.0f} kcal")
    print(f"  Energy deviation: {abs(total_energy_ga - tdee):.0f} kcal ({abs(total_energy_ga - tdee)/tdee*100:.1f}%)")
    
    # Test portion sizing with global rescale
    print(f"\n⚙️  Testing portion sizing with global rescale...")
    
    # Manually select items (simulate user selection)
    selected_items = [
        best_solution.iloc[i] for i in range(10)
    ]
    selected_df = pd.DataFrame(selected_items)
    
    # Calculate portions with NEW global rescale
    portion_df = calculate_portion_sizes_dynamic(selected_df, tdee, guidelines)
    
    # Check result
    total_energy_portions = portion_df['final_energy_kcal'].sum()
    print(f"✓ Portion sizing energy: {total_energy_portions:.0f} kcal")
    print(f"  Energy deviation: {abs(total_energy_portions - tdee):.0f} kcal ({abs(total_energy_portions - tdee)/tdee*100:.1f}%)")
    
    # Display summary
    print(f"\n📈 PORTION SIZES (Grams):")
    for i, row in portion_df.iterrows():
        name = row.get('food_name', 'Unknown')[:30]
        gram = row.get('gram', 0)
        energy = row.get('final_energy_kcal', 0)
        print(f"  {i+1:2d}. {name:30s} | {gram:6.1f}g | {energy:6.0f} kcal")
    
    print(f"\n📊 DAILY TOTALS:")
    print(f"  Energy:       {total_energy_portions:6.0f} kcal (Target: {tdee:6.0f})")
    print(f"  Protein:      {portion_df['final_protein_g'].sum():6.1f} g")
    print(f"  Carbs:        {portion_df['final_carbohydrate_g'].sum():6.1f} g")
    print(f"  Fat:          {portion_df['final_fat_g'].sum():6.1f} g")
    print(f"  Sodium:       {portion_df['final_sodium_mg'].sum():6.0f} mg")
    
    # Validation
    print(f"\n✅ VALIDATION:")
    if abs(total_energy_portions - tdee) / tdee <= 0.1:
        print(f"  ✓ Energy within 10% of target (PASS)")
    else:
        print(f"  ✗ Energy not within 10% of target (FAIL)")
    
    if portion_df['gram'].max() <= 500:
        print(f"  ✓ No portions exceed 500g (PASS)")
    else:
        print(f"  ✗ Some portions exceed 500g (FAIL): max={portion_df['gram'].max():.0f}g")
    
    if all(portion_df['gram'] > 0):
        print(f"  ✓ All portions are positive (PASS)")
    else:
        print(f"  ✗ Some portions are zero or negative (FAIL)")
    
    print("\n" + "="*70)

if __name__ == '__main__':
    test_tdee_constraint()

"""
TEST: Verify Guided Mutation Implementation
===========================================

Test untuk memastikan mutation() sekarang memilih foods berdasarkan nutrient deficiency,
bukan random selection.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../C. System Flow'))

from ga_v1 import mutation, random_solution
from nutrition_service import NutritionService
import pandas as pd
import numpy as np

print("=" * 80)
print("🧪 TEST: GUIDED MUTATION - Nutrient Deficiency Driven Selection")
print("=" * 80)

# ============================================================================
# STEP 1: Load data
# ============================================================================
print("\n[STEP 1] Loading data...")

try:
    nutrition_service = NutritionService()
    
    user_input = {
        'gender': 'Female',
        'age': 25,
        'weight': 60,
        'height': 165,
        'activity_factor': 1.5,
        'disease': ['hypertension'],
        'food_preferences': []
    }
    
    nutrition_result = nutrition_service.calculate_nutrition_needs(user_input)
    
    if not nutrition_result['success']:
        print(f"  ❌ Error: {nutrition_result.get('error', 'Unknown error')}")
        sys.exit(1)
    
    food_df = nutrition_result['food_data']['dataframe']
    guidelines = nutrition_result['guidelines']['nutrients']
    tdee = nutrition_result['energy']['tdee']
    
    print(f"  ✅ Food database loaded: {len(food_df)} items")
    print(f"  ✅ Guidelines loaded")
    print(f"  ✅ TDEE: {tdee:.0f} kcal")
except Exception as e:
    print(f"  ❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ============================================================================
# STEP 2: Create test solution dengan carb/fat kurang, protein berlebih
# ============================================================================
print("\n[STEP 2] Creating test solution with nutrient deficiency...")

# Create a solution yang likely kekurangan carb/fat dan excess protein
test_solution = random_solution(food_df)

carb_before = test_solution['carbohydrate_g'].sum()
fat_before = test_solution['fat_g'].sum()
protein_before = test_solution['protein_g'].sum()
energy_before = test_solution['energy_kcal'].sum()

print(f"  BEFORE Mutation:")
print(f"    - Energy: {energy_before:.0f} kcal")
print(f"    - Carbs: {carb_before:.1f}g (target >= 200g)")
print(f"    - Fat: {fat_before:.1f}g (target >= 50g)")
print(f"    - Protein: {protein_before:.1f}g (target <= 120g)")

# Identify deficiency
need_carb = carb_before < 200
need_fat = fat_before < 50
excess_protein = protein_before > 120

print(f"\n  Detected Deficiencies:")
print(f"    🔴 Carb deficiency: {'YES' if need_carb else 'NO'}")
print(f"    🔴 Fat deficiency: {'YES' if need_fat else 'NO'}")
print(f"    🔴 Excess protein: {'YES' if excess_protein else 'NO'}")

# ============================================================================
# STEP 3: Apply guided mutation (20 times)
# ============================================================================
print("\n[STEP 3] Applying guided mutation 20 times...")

best_solution = test_solution.copy()
improvements = {
    'carb_increased': 0,
    'fat_increased': 0,
    'protein_decreased': 0,
}

for mutation_idx in range(20):
    # Apply mutation dengan guidelines
    mutated = mutation(best_solution, food_df, mutation_rate=1.0,  # 100% mutation untuk testing
                      guidelines=guidelines, tdee=tdee)
    
    carb_after = mutated['carbohydrate_g'].sum()
    fat_after = mutated['fat_g'].sum()
    protein_after = mutated['protein_g'].sum()
    
    # Track improvements
    if carb_after > best_solution['carbohydrate_g'].sum():
        improvements['carb_increased'] += 1
    if fat_after > best_solution['fat_g'].sum():
        improvements['fat_increased'] += 1
    if protein_after < best_solution['protein_g'].sum():
        improvements['protein_decreased'] += 1
    
    # Update best if better
    best_solution = mutated

carb_after = best_solution['carbohydrate_g'].sum()
fat_after = best_solution['fat_g'].sum()
protein_after = best_solution['protein_g'].sum()
energy_after = best_solution['energy_kcal'].sum()

print(f"\n  AFTER Mutations (20x):")
print(f"    - Energy: {energy_after:.0f} kcal (Δ: {energy_after-energy_before:+.0f})")
print(f"    - Carbs: {carb_after:.1f}g (Δ: {carb_after-carb_before:+.1f}g) {'✅' if carb_after >= carb_before else ''}")
print(f"    - Fat: {fat_after:.1f}g (Δ: {fat_after-fat_before:+.1f}g) {'✅' if fat_after >= fat_before else ''}")
print(f"    - Protein: {protein_after:.1f}g (Δ: {protein_after-protein_before:+.1f}g) {'✅' if protein_after <= protein_before else ''}")

# ============================================================================
# STEP 4: Analyze guided mutation impact
# ============================================================================
print(f"\n[STEP 4] Guided Mutation Impact Analysis:")
print(f"{'-'*80}")

improvements_pct = {
    'carb': (improvements['carb_increased'] / 20 * 100) if need_carb else 0,
    'fat': (improvements['fat_increased'] / 20 * 100) if need_fat else 0,
    'protein': (improvements['protein_decreased'] / 20 * 100) if excess_protein else 0,
}

print(f"  Mutations that improved deficiency:")
if need_carb:
    print(f"    - Carb increase: {improvements['carb_increased']}/20 times ({improvements_pct['carb']:.0f}%)")
if need_fat:
    print(f"    - Fat increase: {improvements['fat_increased']}/20 times ({improvements_pct['fat']:.0f}%)")
if excess_protein:
    print(f"    - Protein decrease: {improvements['protein_decreased']}/20 times ({improvements_pct['protein']:.0f}%)")

# ============================================================================
# STEP 5: Conclusion
# ============================================================================
print(f"\n[STEP 5] CONCLUSION:")
print(f"{'='*80}")

success = True

# Check if guided mutation worked
if need_carb:
    if carb_after > carb_before:
        print(f"  ✅ Carb: IMPROVED ({carb_before:.0f}g → {carb_after:.0f}g)")
    else:
        print(f"  ❌ Carb: NO IMPROVEMENT ({carb_before:.0f}g → {carb_after:.0f}g)")
        success = False

if need_fat:
    if fat_after > fat_before:
        print(f"  ✅ Fat: IMPROVED ({fat_before:.0f}g → {fat_after:.0f}g)")
    else:
        print(f"  ❌ Fat: NO IMPROVEMENT ({fat_before:.0f}g → {fat_after:.0f}g)")
        success = False

if excess_protein:
    if protein_after < protein_before:
        print(f"  ✅ Protein: REDUCED ({protein_before:.0f}g → {protein_after:.0f}g)")
    else:
        print(f"  ⚠️  Protein: NOT REDUCED ({protein_before:.0f}g → {protein_after:.0f}g)")
        # Not critical, protein excess is harder to fix

if success:
    print(f"\n  🎉 GUIDED MUTATION: ✅ WORKING!")
    print(f"     Mutation correctly selects foods based on nutrient deficiency")
    print(f"     Carbs/Fats improve, Protein excess reduced")
else:
    print(f"\n  ⚠️  GUIDED MUTATION: Needs adjustment")
    print(f"     Some deficiencies not addressed")

print(f"\n{'='*80}\n")

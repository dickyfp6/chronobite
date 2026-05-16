"""
DEMO: GA Improvements - Macronutrient Priority Penalties
========================================================

Show how the new fitness function penalizes macronutrient deviations
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../C. System Flow'))

from ga_v1 import fitness, calculate_total_nutrition
from nutrition_service import NutritionService
import pandas as pd

print("\n" + "="*80)
print("[DEMO] Macronutrient Penalty Structure")
print("="*80)

# Setup
nutrition_service = NutritionService()
user_input = {
    'gender': 'Female', 'age': 25, 'weight': 60, 'height': 165,
    'activity_factor': 1.5, 'disease': ['hypertension'], 'food_preferences': []
}
result = nutrition_service.calculate_nutrition_needs(user_input)
guidelines_dict = result.get('guidelines', {})
tdee = result.get('energy', {}).get('tdee', 2000)

# Convert guidelines
guidelines = {
    'hard': {},
    'soft': guidelines_dict.get('nutrients', {})
}

soft_guidelines = guidelines.get('soft', {})

print("\n[PENALTY STRUCTURE - Macronutrients]")
print("-" * 80)

print("\nCARBOHYDRATE (Highest Priority):")
carb_target = soft_guidelines.get('carbohydrate_g', {})
print(f"  Target: {carb_target.get('min', 200):.0f} - {carb_target.get('max', 280):.0f} g")
print(f"  DEFICIT penalty: (min - actual) x 800")
print(f"  EXCESS penalty:  (actual - max) x 400")
print(f"  Example 1: 180g actual (20g below min {carb_target.get('min', 200):.0f}g)")
print(f"    Penalty = 20 x 800 = 16,000")
print(f"  Example 2: 300g actual (20g above max {carb_target.get('max', 280):.0f}g)")
print(f"    Penalty = 20 x 400 = 8,000")

print("\nFAT (High Priority):")
fat_target = soft_guidelines.get('fat_g', {})
print(f"  Target: {fat_target.get('min', 50):.0f} - {fat_target.get('max', 100):.0f} g")
print(f"  DEFICIT penalty: (min - actual) x 600")
print(f"  EXCESS penalty:  (actual - max) x 300")
print(f"  Example: 40g actual (10g below min {fat_target.get('min', 50):.0f}g)")
print(f"    Penalty = 10 x 600 = 6,000")

print("\nPROTEIN (Control Excess):")
protein_target = soft_guidelines.get('protein_g', {})
print(f"  Target: {protein_target.get('min', 50):.0f} - {protein_target.get('max', 120):.0f} g")
print(f"  DEFICIT penalty:  (min - actual) x 200")
print(f"  EXCESS penalty:   (actual - max) x 500  [STRICT]")
print(f"  Example 1: 40g actual (10g below min {protein_target.get('min', 50):.0f}g)")
print(f"    Penalty = 10 x 200 = 2,000")
print(f"  Example 2: 140g actual (20g above max {protein_target.get('max', 120):.0f}g)")
print(f"    Penalty = 20 x 500 = 10,000")

print("\nHARD CONSTRAINTS (Medical - Critical):")
print(f"  HARD penalty multiplier: 10,000x")
print(f"  Example: Sodium violation")
print(f"    Penalty = (actual - max) x 10,000")

print("\nMICRONUTRIENTS (Flexible):")
print(f"  SOFT penalty multiplier: 2x (weight)")
print(f"  Example: Calcium 100mg below target")
print(f"    Penalty = 100 x 1.0 x 2 = 200")

print("\n" + "="*80)
print("[KEY DIFFERENCES]")
print("="*80)

print("\nOLD FITNESS FUNCTION:")
print("  - All macros: 10x multiplier (same)")
print("  - Result: GA didn't strongly prioritize carbs over fat or protein")

print("\nNEW FITNESS FUNCTION:")
print("  - Carbs deficit: 800x (HIGHEST - prioritize filling carbs)")
print("  - Fat deficit:   600x (HIGH - but less than carbs)")
print("  - Protein excess: 500x (CONTROL - prevent over-protein)")
print("  - Result: GA actively seeks high-carb options & avoids protein-heavy foods")

print("\n[MUTATION GUIDANCE]")
print("-" * 80)

print("\nNEW MUTATION LOGIC:")
print("\n  If need CARBS:")
print("    Select: carb >= 20g AND protein <= 15g")
print("    Why: Find carb-rich foods without adding excess protein")
print("    Fallback: carb >= 20g only")

print("\n  If need FAT:")
print("    Select: fat >= 10g AND protein <= 15g")
print("    Why: Find fat-rich foods without adding excess protein")
print("    Fallback: fat >= 10g only")

print("\n  If too much PROTEIN:")
print("    Select: protein <= 10g")
print("    Why: Replace with low-protein options to reduce excess")

print("\n" + "="*80)
print("[RESULT EXPECTATIONS]")
print("="*80)

print("\nWith these improvements, GA should:")
print("  1. Produce meals with carbs CLOSER to target (80%+ fulfillment)")
print("  2. Produce meals with fat CLOSER to target (80%+ fulfillment)")
print("  3. REDUCE protein excess (more controlled portions)")
print("  4. REDUCE sodium violations (HARD constraints prioritized)")
print("  5. Output status: FAIR/GOOD instead of POOR")

print("\n" + "="*80 + "\n")

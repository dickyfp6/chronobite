#!/usr/bin/env python
"""
Debug Local Search - Understand why no swaps are improving
"""

import sys
sys.path.insert(0, r"c:\Users\Silfia\Documents\FILE TA\TugasAkhirDSS\D. Model\GA_REBUILD")

import pandas as pd
import numpy as np
import random

random.seed(42)
np.random.seed(42)

print("[DEBUG] Testing Local Search Swap Candidates")
print("="*70)

# Load CSV files
food_df = pd.read_csv(r"c:\Users\Silfia\Documents\FILE TA\TugasAkhirDSS\A. Data\Data Processed\05_final_dataset.csv")
guideline_df = pd.read_csv(r"c:\Users\Silfia\Documents\FILE TA\TugasAkhirDSS\A. Data\Data Raw\guideline.csv")

# Build guidelines (only use macronutrients with HARD constraints)
guide_normal = guideline_df[guideline_df['disease'] == 'normal'].copy()
hard_nutrients = guide_normal[['nutrient', 'min', 'max']].drop_duplicates(subset=['nutrient'])

guidelines = {'hard': {}, 'soft': {}}

for _, row in hard_nutrients.iterrows():
    nutrient = row['nutrient']
    min_val = row['min'] if pd.notna(row['min']) else 0
    max_val = row['max'] if pd.notna(row['max']) else float('inf')
    guidelines['hard'][nutrient] = {
        'min': min_val,
        'max': max_val,
        'constraint_type': 'range',
        'hard_soft_type': 'HARD'
    }

print(f"\n[SETUP] {len(guidelines['hard'])} HARD constraints")
for nutrient, constraint in list(guidelines['hard'].items()):
    print(f"  - {nutrient}: {constraint['min']:.3f} - {constraint['max']:.3f}")

# Import GA functions
from ga_v1 import (
    calculate_total_nutrition,
    calculate_total_hard_deviation,
    is_feasible,
    run_ga,
    SLOT_LABEL_MAP,
    CHROMOSOME_SIZE
)

# Clean food
invalid_keywords = ['spice', 'powder', 'yeast', 'sauce', 'extract', 'flavoring', 'dressing', 'seasoning']
food_df_clean = food_df[~food_df['food_name'].str.lower().str.contains('|'.join(invalid_keywords), na=False)].copy()

print(f"\n[FILTER] {len(food_df)} → {len(food_df_clean)} items")

# Run GA briefly
print(f"\n[GA] Running 5 generations (quick test)...")
best_solution, _ = run_ga(
    food_df=food_df_clean,
    guidelines=guidelines,
    tdee=None,
    generations=5,
    pop_size=10,
    verbose=False
)

current_nutrition = calculate_total_nutrition(best_solution)
old_deviation = calculate_total_hard_deviation(best_solution, guidelines)

print(f"\n[GA RESULT]")
print(f"  Total deviation: {old_deviation:.1f}")

# ════════════════════════════════════════════════════════════════════════════
# ANALYZE VIOLATIONS
# ════════════════════════════════════════════════════════════════════════════

print(f"\n[VIOLATIONS]")
hard_violations = []
for nutrient, constraint in guidelines['hard'].items():
    actual = current_nutrition.get(nutrient, 0)
    min_val = constraint.get('min', 0)
    max_val = constraint.get('max', float('inf'))
    
    if actual < min_val:
        deviation = min_val - actual
        violation_type = 'LOW'
    elif actual > max_val:
        deviation = actual - max_val
        violation_type = 'HIGH'
    else:
        violation_type = 'OK'
        deviation = 0
    
    hard_violations.append({
        'nutrient': nutrient,
        'type': violation_type,
        'actual': actual,
        'min': min_val,
        'max': max_val,
        'deviation': deviation
    })
    
    print(f"  {nutrient:25} {violation_type:4} actual={actual:8.1f} target={min_val:.1f}-{max_val:.1f}")

hard_violations_sorted = sorted([v for v in hard_violations if v['deviation'] > 0], 
                                key=lambda x: x['deviation'], reverse=True)

if len(hard_violations_sorted) == 0:
    print("\n✓ No violations found!")
else:
    target = hard_violations_sorted[0]
    target_nutrient = target['nutrient']
    target_type = target['type']
    
    print(f"\n[TARGET] {target_nutrient} ({target_type})")
    print(f"  Actual: {target['actual']:.1f}")
    print(f"  Target: {target['min']:.1f} - {target['max']:.1f}")
    print(f"  Deviation: {target['deviation']:.1f}")
    
    # ════════════════════════════════════════════════════════════════════════════
    # DEBUG: Show candidate pool
    # ════════════════════════════════════════════════════════════════════════════
    
    print(f"\n[CANDIDATE POOL]")
    if target_type == 'LOW':
        min_threshold = target['min'] * 0.5
        candidate_pool = food_df_clean[food_df_clean[target_nutrient] >= min_threshold].copy()
        candidate_pool = candidate_pool.sort_values(by=target_nutrient, ascending=False)
        print(f"  Filter: {target_nutrient} >= {min_threshold:.1f}")
    else:  # HIGH
        max_threshold = target['max'] * 1.2
        candidate_pool = food_df_clean[food_df_clean[target_nutrient] <= max_threshold].copy()
        candidate_pool = candidate_pool.sort_values(by=target_nutrient, ascending=True)
        print(f"  Filter: {target_nutrient} <= {max_threshold:.1f}")
    
    print(f"  Total candidates: {len(candidate_pool)}")
    print(f"  Top 5 by {target_nutrient}:")
    for idx, (_, food) in enumerate(candidate_pool.head(5).iterrows()):
        print(f"    {idx+1}. {food['food_name']:40} {food[target_nutrient]:8.1f}g {food.get('consumption_label', '?')}")
    
    # ════════════════════════════════════════════════════════════════════════════
    # DEBUG: Try a single swap manually
    # ════════════════════════════════════════════════════════════════════════════
    
    print(f"\n[MANUAL SWAP TEST]")
    
    for gene_idx in range(min(3, len(best_solution))):
        print(f"\n  Slot {gene_idx}:")
        current_food = best_solution.iloc[gene_idx]
        current_name = current_food.get('food_name', '?')
        current_value = current_food.get(target_nutrient, 0)
        current_label = current_food.get('consumption_label', '?')
        
        print(f"    Current: {current_name:40} {current_value:8.1f}g ({current_label})")
        
        # Get candidates for this slot
        expected_label = SLOT_LABEL_MAP.get(gene_idx, 'Main Course')
        slot_candidates = candidate_pool[candidate_pool['consumption_label'] == expected_label].copy()
        
        print(f"    Matching label '{expected_label}': {len(slot_candidates)} candidates")
        
        if len(slot_candidates) > 0:
            for cand_idx in range(min(2, len(slot_candidates))):
                new_food = slot_candidates.iloc[cand_idx]
                new_name = new_food.get('food_name', '?')
                new_value = new_food.get(target_nutrient, 0)
                
                # Try swap
                test_solution = best_solution.copy()
                test_solution.iloc[gene_idx] = new_food
                test_nutrition = calculate_total_nutrition(test_solution)
                new_deviation = calculate_total_hard_deviation(test_solution, guidelines)
                
                improvement = old_deviation - new_deviation
                
                print(f"      Candidate: {new_name:36} {new_value:8.1f}g → Deviation: {old_deviation:.1f} → {new_deviation:.1f} (Δ{improvement:+.1f})")

print("\n[DEBUG COMPLETE]")

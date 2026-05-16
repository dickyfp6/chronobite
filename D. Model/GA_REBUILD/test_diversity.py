"""
TEST: Verify Premature Convergence FIX
=====================================

Menguji apakah GA sekarang menghasilkan variasi solusi yang berbeda di setiap run.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../C. System Flow'))

from ga_v1 import run_ga
from nutrition_service import NutritionService
import pandas as pd
import numpy as np
from collections import Counter

print("=" * 80)
print("🧪 TEST: PREMATURE CONVERGENCE FIX - Diversity Check")
print("=" * 80)

# ============================================================================
# STEP 1: Load data
# ============================================================================
print("\n[STEP 1] Loading data...")

try:
    nutrition_service = NutritionService()
    
    # Create sample user input
    user_input = {
        'gender': 'Female',
        'age': 25,
        'weight': 60,
        'height': 165,
        'activity_factor': 1.5,
        'disease': ['hypertension'],
        'food_preferences': []
    }
    
    # Calculate nutrition needs
    nutrition_result = nutrition_service.calculate_nutrition_needs(user_input)
    
    if not nutrition_result['success']:
        print(f"  ❌ Error: {nutrition_result.get('error', 'Unknown error')}")
        sys.exit(1)
    
    food_df = nutrition_result['food_data']['dataframe']
    guidelines = nutrition_result['guidelines']['nutrients']
    tdee = nutrition_result['energy']['tdee']
    
    print(f"  ✅ Food database loaded: {len(food_df)} items")
    print(f"  ✅ Guidelines loaded: {len(guidelines)} constraints")
    print(f"  ✅ TDEE: {tdee:.0f} kcal")
except Exception as e:
    print(f"  ❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ============================================================================
# STEP 2: Run GA multiple times and collect results
# ============================================================================
print("\n[STEP 2] Running GA 5 times to check diversity...")
print(f"{'Run':<5} | {'Best Fitness':<15} | {'Top 3 Items':<60}")
print(f"{'-'*85}")

all_solutions = []
fitness_scores = []
meal_signatures = []

for run_num in range(5):
    best_solution, top_solutions = run_ga(
        food_df=food_df,
        guidelines=guidelines,
        tdee=tdee,
        generations=50,
        pop_size=20,
        elite_ratio=0.2,
        mutation_rate=0.3,
        verbose=False
    )
    
    from ga_v1 import fitness
    best_fit = fitness(best_solution, guidelines, tdee=tdee)
    fitness_scores.append(best_fit)
    
    # Extract food names dari best solution (first 3 items)
    foods_in_solution = best_solution['food_name'].head(3).tolist()
    meal_signatures.append(tuple(foods_in_solution))
    
    all_solutions.append(best_solution)
    
    print(f"{run_num+1:<5} | {best_fit:<15.2f} | {' + '.join(foods_in_solution[:3]):<60}")

# ============================================================================
# STEP 3: Analyze diversity
# ============================================================================
print(f"\n[STEP 3] Diversity Analysis:")
print(f"{'-'*85}")

# Check if solutions are different
unique_signatures = len(set(meal_signatures))
print(f"  Total unique meal signatures: {unique_signatures}/5 runs")

if unique_signatures >= 4:
    print(f"  ✅ EXCELLENT diversity! Solutions are mostly different")
elif unique_signatures >= 3:
    print(f"  ✅ GOOD diversity! Most solutions are different")
elif unique_signatures >= 2:
    print(f"  ⚠️  FAIR diversity! Some variety in solutions")
else:
    print(f"  ❌ POOR diversity! Solutions are identical or nearly identical")

# Check fitness variation
fitness_array = np.array(fitness_scores)
fitness_std = np.std(fitness_array)
fitness_mean = np.mean(fitness_array)
fitness_cv = (fitness_std / fitness_mean * 100) if fitness_mean > 0 else 0

print(f"\n  Fitness Score Statistics:")
print(f"    - Mean: {fitness_mean:.2f}")
print(f"    - Std Dev: {fitness_std:.2f}")
print(f"    - Coefficient of Variation: {fitness_cv:.1f}%")

if fitness_cv > 5:
    print(f"    ✅ Good variation in fitness scores (CV > 5%)")
elif fitness_cv > 2:
    print(f"    ⚠️  Moderate variation in fitness scores (CV > 2%)")
else:
    print(f"    ❌ Low variation - may indicate convergence (CV < 2%)")

# ============================================================================
# STEP 4: Check food item distribution
# ============================================================================
print(f"\n[STEP 4] Food Item Distribution Across Runs:")
print(f"{'-'*85}")

# Count food items used in each solution
food_counter = Counter()
for solution in all_solutions:
    for food_name in solution['food_name'].unique():
        food_counter[food_name] += 1

# Top 10 most used foods
top_foods = food_counter.most_common(10)
print(f"  Top 10 most used food items:")
for rank, (food, count) in enumerate(top_foods, 1):
    bar = "█" * count + "░" * (5 - count)
    print(f"    {rank:2}. {food:<40} [{bar}] {count}x")

# Check for diversity in food selection
total_food_slots = 5 * 10  # 5 runs × 10 items per solution
unique_foods_used = len(food_counter)
avg_reuse = total_food_slots / unique_foods_used if unique_foods_used > 0 else 0

print(f"\n  Food item statistics:")
print(f"    - Total food slots filled: {total_food_slots}")
print(f"    - Unique food items used: {unique_foods_used}")
print(f"    - Average reuse per food: {avg_reuse:.2f}x")

if unique_foods_used >= 30:
    print(f"    ✅ EXCELLENT food diversity! {unique_foods_used} different items used")
elif unique_foods_used >= 20:
    print(f"    ✅ GOOD food diversity! {unique_foods_used} different items used")
elif unique_foods_used >= 10:
    print(f"    ⚠️  MODERATE food diversity! {unique_foods_used} different items used")
else:
    print(f"    ❌ LOW food diversity! Only {unique_foods_used} different items used")

# ============================================================================
# STEP 5: Summary & Conclusion
# ============================================================================
print(f"\n[STEP 5] CONCLUSION:")
print(f"{'='*85}")

improvements_detected = 0

# Check improvements
if unique_signatures >= 3:
    improvements_detected += 1
    print(f"  ✅ Diversity: Different meal plans generated (not stuck on same solution)")

if fitness_cv > 2:
    improvements_detected += 1
    print(f"  ✅ Variation: Fitness scores vary across runs (showing exploration)")

if unique_foods_used >= 15:
    improvements_detected += 1
    print(f"  ✅ Food Mix: GA explores different food combinations (not repetitive)")

print(f"\n  Improvements Detected: {improvements_detected}/3")

if improvements_detected >= 3:
    print(f"\n  🎉 PREMATURE CONVERGENCE FIX: ✅ SUCCESSFUL")
    print(f"     GA now produces diverse solutions with good exploration!")
elif improvements_detected >= 2:
    print(f"\n  ⚠️  PARTIAL IMPROVEMENT")
    print(f"     GA diversity improved but may need further tuning")
else:
    print(f"\n  ❌ NO SIGNIFICANT IMPROVEMENT")
    print(f"     Consider increasing mutation_rate further or adjusting parameters")

print(f"\n{'='*85}")

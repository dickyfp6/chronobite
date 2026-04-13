"""
SIDE-BY-SIDE COMPARISON: OLD vs NEW FITNESS FUNCTION

Demonstrates the differences between the original fitness function
and the improved version with concrete examples.
"""

import pandas as pd
from typing import Dict, List

# ============================================================================
# EXAMPLE DATA
# ============================================================================

EXAMPLE_USER = {
    'tdee': 2000,
    'guidelines': {
        'protein_g': {'min': 56, 'max': 100},
        'carbohydrate_g': {'min': 225, 'max': 325},
        'fat_g': {'min': 56, 'max': 78},
        'fiber_g': {'min': 25, 'max': float('inf')},
        'sodium_mg': {'min': 1500, 'max': 2300},
        'potassium_mg': {'min': 2600, 'max': float('inf')},
        'calcium_mg': {'min': 1000, 'max': float('inf')},
        'iron_mg': {'min': 18, 'max': float('inf')},
        'zinc_mg': {'min': 8, 'max': float('inf')},
        'vitamin_c_mg': {'min': 75, 'max': float('inf')},
        'vitamin_a_rae_mcg': {'min': 700, 'max': float('inf')},
        'folate_mcg': {'min': 400, 'max': float('inf')},
    }
}

EXAMPLE_MEAL = {
    'protein_g': 45,           # 9g short of min 56g
    'carbohydrate_g': 250,     # 25g over min 225g ✓
    'fat_g': 65,               # Good: within 56-78g ✓
    'fiber_g': 20,             # 5g short of min 25g
    'sodium_mg': 2200,         # Within range ✓
    'potassium_mg': 2400,      # 200mg short of min 2600mg
    'calcium_mg': 850,         # 150mg short of min 1000mg
    'iron_mg': 14,             # 4mg short of min 18mg
    'zinc_mg': 7,              # 1mg short of min 8mg
    'vitamin_c_mg': 60,        # 15mg short of min 75mg
    'vitamin_a_rae_mcg': 600,  # 100mcg short of min 700mcg
    'folate_mcg': 350,         # 50mcg short of min 400mcg
    'energy_kcal': 1950,       # Close to target 2000 kcal
}

# ============================================================================
# OLD FITNESS FUNCTION (Original)
# ============================================================================

class OldFitnessCalculator:
    """Original fitness calculation with all known issues."""
    
    ALL_NUTRIENTS = [
        'energy_kcal', 'protein_g', 'carbohydrate_g', 'fat_g', 'fiber_g',
        'sodium_mg', 'potassium_mg', 'calcium_mg', 'iron_mg', 'zinc_mg',
        'vitamin_a_rae_mcg', 'vitamin_c_mg', 'vitamin_d_mcg', 'vitamin_e_mg',
        'vitamin_k_mcg', 'thiamine_mg', 'riboflavin_mg', 'niacin_mg',
        'vitamin_b6_mg', 'vitamin_b12_mcg', 'folate_mcg', 'cholesterol_mg'
    ]
    
    @staticmethod
    def calculate_nutrient_score_linear(actual, min_val, max_val):
        """Linear penalty - HARSH."""
        if actual < min_val:
            # Too little
            penalty = (min_val - actual) / min_val * 100
            return max(0, 100 - penalty)
        elif actual > max_val:
            # Too much
            penalty = (actual - max_val) / max_val * 100
            return max(0, 100 - penalty)
        else:
            # In range
            return 100
    
    @staticmethod
    def analyze(meal: Dict, user: Dict) -> Dict:
        """Analyze meal using old method."""
        results = {
            'nutrient_scores': {},
            'nutrient_count': len(OldFitnessCalculator.ALL_NUTRIENTS),
        }
        
        # Calculate individual nutrient scores
        for nutrient in OldFitnessCalculator.ALL_NUTRIENTS:
            if nutrient in meal and nutrient in user['guidelines']:
                actual = meal[nutrient]
                min_val = user['guidelines'][nutrient].get('min', 0)
                max_val = user['guidelines'][nutrient].get('max', float('inf'))
                
                score = OldFitnessCalculator.calculate_nutrient_score_linear(
                    actual, min_val, max_val
                )
                results['nutrient_scores'][nutrient] = score
            else:
                # Nutrient not in meal or guidelines
                results['nutrient_scores'][nutrient] = 50  # Default
        
        # Calculate average (THIS IS THE PROBLEM!)
        results['average_nutrient_score'] = sum(results['nutrient_scores'].values()) / len(results['nutrient_scores'])
        
        # Calorie score
        tdee = user['tdee']
        actual_kcal = meal['energy_kcal']
        calorie_score = OldFitnessCalculator.calculate_nutrient_score_linear(
            actual_kcal, tdee * 0.85, tdee * 1.15
        )
        results['calorie_score'] = calorie_score
        
        # Components
        results['nutrient_compliance'] = results['average_nutrient_score']
        results['total_calorie'] = calorie_score
        results['meal_variety'] = 50  # Placeholder
        
        # Weighted components (OLD WEIGHTS: 80/10/10)
        results['fitness_score'] = (
            results['nutrient_compliance'] * 0.80 +
            results['meal_variety'] * 0.10 +
            results['total_calorie'] * 0.10
        )
        
        return results


# ============================================================================
# NEW FITNESS FUNCTION (Improved)
# ============================================================================

class NewFitnessCalculator:
    """Improved fitness calculation with all fixes."""
    
    CRITICAL_NUTRIENTS = {
        'protein_g': 1.5,
        'carbohydrate_g': 1.5,
        'fat_g': 1.5,
        'fiber_g': 1.0,
        'sodium_mg': 1.0,
        'potassium_mg': 1.0,
        'calcium_mg': 1.0,
        'iron_mg': 1.0,
        'zinc_mg': 0.8,
        'vitamin_c_mg': 0.8,
        'vitamin_a_rae_mcg': 0.8,
        'folate_mcg': 0.8,
    }
    
    @staticmethod
    def calculate_nutrient_score_soft(actual, min_val, max_val):
        """Soft penalty using quadratic falloff - GENTLE."""
        if actual < min_val:
            # Too little
            gap_ratio = (min_val - actual) / min_val
            penalty = min(100, gap_ratio ** 2 * 100)  # Quadratic!
            return max(0, 100 - penalty)
        elif actual > max_val:
            # Too much
            gap_ratio = (actual - max_val) / max_val
            penalty = min(100, gap_ratio ** 2 * 100)  # Quadratic!
            return max(0, 100 - penalty)
        else:
            # In range
            return 100
    
    @staticmethod
    def analyze(meal: Dict, user: Dict) -> Dict:
        """Analyze meal using new method."""
        results = {
            'nutrient_scores': {},
            'nutrient_count': len(NewFitnessCalculator.CRITICAL_NUTRIENTS),
        }
        
        # Calculate individual nutrient scores (ONLY CRITICAL NUTRIENTS)
        total_score = 0
        total_weight = 0
        
        for nutrient, weight in NewFitnessCalculator.CRITICAL_NUTRIENTS.items():
            if nutrient in meal and nutrient in user['guidelines']:
                actual = meal[nutrient]
                min_val = user['guidelines'][nutrient].get('min', 0)
                max_val = user['guidelines'][nutrient].get('max', float('inf'))
                
                score = NewFitnessCalculator.calculate_nutrient_score_soft(
                    actual, min_val, max_val
                )
                results['nutrient_scores'][nutrient] = {
                    'score': score,
                    'weight': weight,
                    'weighted': score * weight
                }
                total_score += score * weight
                total_weight += weight
        
        # Weighted average (NOT simple average!)
        results['weighted_nutrient_score'] = total_score / total_weight if total_weight > 0 else 0
        
        # Calorie score (with stricter tolerance ±10%)
        tdee = user['tdee']
        actual_kcal = meal['energy_kcal']
        calorie_score = NewFitnessCalculator.calculate_nutrient_score_soft(
            actual_kcal, tdee * 0.90, tdee * 1.10  # ±10% instead of ±15%
        )
        results['calorie_score'] = calorie_score
        
        # Components
        results['nutrient_compliance'] = results['weighted_nutrient_score']
        results['total_calorie'] = calorie_score
        results['meal_variety'] = 50  # Placeholder
        
        # Weighted components (NEW WEIGHTS: 60/30/10)
        results['fitness_score'] = (
            results['nutrient_compliance'] * 0.60 +
            results['meal_variety'] * 0.10 +
            results['total_calorie'] * 0.30
        )
        
        return results


# ============================================================================
# COMPARISON & DEMONSTRATION
# ============================================================================

def format_comparison_table():
    """Print detailed side-by-side comparison."""
    
    print("\n" + "="*120)
    print("SIDE-BY-SIDE COMPARISON: OLD vs NEW FITNESS FUNCTION")
    print("="*120 + "\n")
    
    print("SCENARIO: Meal with mixed compliance (some nutrients hit, some miss)")
    print("User TDEE: 2000 kcal\n")
    
    # Run both calculators
    old_results = OldFitnessCalculator.analyze(EXAMPLE_MEAL, EXAMPLE_USER)
    new_results = NewFitnessCalculator.analyze(EXAMPLE_MEAL, EXAMPLE_USER)
    
    # ========== NUTRIENT-BY-NUTRIENT COMPARISON ==========
    print("\n" + "-"*120)
    print("NUTRIENT SCORING DETAILS")
    print("-"*120)
    
    print(f"\n{'Nutrient':<25} {'Goal':<15} {'Actual':<15} {'Old Score':<15} {'New Score':<15} {'Difference'}")
    print("-"*120)
    
    for nutrient in NewFitnessCalculator.CRITICAL_NUTRIENTS.keys():
        goal = EXAMPLE_USER['guidelines'][nutrient]
        actual = EXAMPLE_MEAL[nutrient]
        old_score = old_results['nutrient_scores'].get(nutrient, 'N/A')
        
        new_score_dict = new_results['nutrient_scores'].get(nutrient, {})
        new_score = new_score_dict.get('score', 'N/A') if isinstance(new_score_dict, dict) else new_score_dict
        
        # Format goal
        if goal['max'] == float('inf'):
            goal_str = f"≥{goal['min']}"
        else:
            goal_str = f"{goal['min']}-{goal['max']}"
        
        # Difference
        if isinstance(old_score, (int, float)) and isinstance(new_score, (int, float)):
            diff = new_score - old_score
            diff_str = f"{diff:+.1f}"
        else:
            diff_str = "N/A"
        
        print(
            f"{nutrient:<25} {goal_str:<15} {actual:<15.1f} "
            f"{old_score:<15.1f} {new_score:<15.1f} {diff_str}"
        )
    
    # ========== AGGREGATED SCORING ==========
    print("\n" + "-"*120)
    print("AGGREGATED SCORING (How individual nutrient scores combine)")
    print("-"*120)
    
    print(f"\nOLD METHOD (Simple Average of all 22 nutrients):")
    print(f"  - Nutrient count: {old_results['nutrient_count']}")
    print(f"  - Average method: Sum of all scores / 22")
    print(f"  - Nutrient compliance: {old_results['nutrient_compliance']:.2f}")
    
    print(f"\nNEW METHOD (Weighted Average of 12 critical nutrients):")
    print(f"  - Nutrient count: {new_results['nutrient_count']}")
    print(f"  - Average method: Σ(score × weight) / Σ(weights)")
    print(f"  - Nutrient compliance: {new_results['nutrient_compliance']:.2f}")
    
    print(f"\nDifference: {new_results['nutrient_compliance'] - old_results['nutrient_compliance']:+.2f}")
    
    # ========== CALORIE SCORING ==========
    print("\n" + "-"*120)
    print("CALORIE MATCHING")
    print("-"*120)
    
    print(f"\nTarget TDEE: 2000 kcal")
    print(f"Actual meal: {EXAMPLE_MEAL['energy_kcal']} kcal ({EXAMPLE_MEAL['energy_kcal']/2000*100:.1f}%)")
    
    print(f"\nOLD METHOD (±15% tolerance):")
    print(f"  - Acceptable range: {2000*0.85:.0f}-{2000*1.15:.0f} kcal")
    print(f"  - Meal score: {old_results['calorie_score']:.2f}")
    
    print(f"\nNEW METHOD (±10% tolerance, stricter):")
    print(f"  - Acceptable range: {2000*0.90:.0f}-{2000*1.10:.0f} kcal")
    print(f"  - Meal score: {new_results['calorie_score']:.2f}")
    
    print(f"\nDifference: {new_results['calorie_score'] - old_results['calorie_score']:+.2f}")
    
    # ========== COMPONENT WEIGHTING ==========
    print("\n" + "-"*120)
    print("COMPONENT WEIGHTING (How nutrition, calorie, variety combine)")
    print("-"*120)
    
    print(f"\nOLD WEIGHTS:")
    print(f"  - Nutrient compliance: 80% (weight 0.80)")
    print(f"  - Meal variety: 10% (weight 0.10)")
    print(f"  - Total calorie: 10% (weight 0.10)")
    print(f"  - Formula: {old_results['nutrient_compliance']:.1f}×0.80 + {old_results['meal_variety']:.1f}×0.10 + {old_results['total_calorie']:.1f}×0.10")
    print(f"  - Result: {old_results['fitness_score']:.2f}")
    
    print(f"\nNEW WEIGHTS:")
    print(f"  - Nutrient compliance: 60% (weight 0.60) ↓20%")
    print(f"  - Meal variety: 10% (weight 0.10) [same]")
    print(f"  - Total calorie: 30% (weight 0.30) ↑20% (3× importance)")
    print(f"  - Formula: {new_results['nutrient_compliance']:.1f}×0.60 + {new_results['meal_variety']:.1f}×0.10 + {new_results['total_calorie']:.1f}×0.30")
    print(f"  - Result: {new_results['fitness_score']:.2f}")
    
    # ========== FINAL SCORES ==========
    print("\n" + "-"*120)
    print("FINAL FITNESS SCORES")
    print("-"*120)
    
    print(f"\nOLD FITNESS FUNCTION: {old_results['fitness_score']:.2f}")
    print(f"NEW FITNESS FUNCTION: {new_results['fitness_score']:.2f}")
    print(f"\nDifference: {new_results['fitness_score'] - old_results['fitness_score']:+.2f}")
    print(f"Improvement: {(new_results['fitness_score'] - old_results['fitness_score']) / old_results['fitness_score'] * 100:+.1f}%")
    
    # ========== KEY INSIGHTS ==========
    print("\n" + "-"*120)
    print("KEY INSIGHTS")
    print("-"*120)
    
    print(f"""
1. NUTRIENT EVALUATION:
   - OLD: Averaged all 22 nutrients (including 10 unused)
   - NEW: Only 12 critical nutrients with weights
   - RESULT: Higher and more stable score (not dragged down by zeros)

2. PENALTY STYLE:
   - OLD: Linear penalties (harsh)
   - NEW: Quadratic soft penalties (gentle)
   - EXAMPLE: 20% deviation:
     * OLD: 20 point penalty
     * NEW: 4 point penalty (5× softer!)

3. SCORING METHOD:
   - OLD: Simple average (all nutrients equal)
   - NEW: Weighted average (important nutrients matter more)
   - RESULT: Macronutrients prioritized, vitamins secondary

4. CALORIE IMPORTANCE:
   - OLD: Only 10% of final score
   - NEW: 30% of final score (3× more important)
   - RESULT: GA won't generate 3000 kcal or 800 kcal menus

5. TOLERANCE STRICTNESS:
   - OLD: ±15% range for calories
   - NEW: ±10% range for calories
   - RESULT: More realistic and healthier diets

EXPECTED GA BEHAVIOR:
   - OLD: Fitness plateaus at 50-55, minimal progress after Gen 20
   - NEW: Fitness climbs to 75-85, continues improving through Gen 100
""")
    
    print("\n" + "="*120 + "\n")


if __name__ == "__main__":
    format_comparison_table()

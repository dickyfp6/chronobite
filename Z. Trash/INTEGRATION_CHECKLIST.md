"""
Integration Checklist untuk GA dengan main system
"""

INTEGRATION_README = """
# Genetic Algorithm Integration Checklist

## ✅ Component Files Created

- [x] ga_validators.py - Chromosome validation & repair
- [x] ga_operators.py - Genetic operators (crossover, mutation, selection)
- [x] ga_fitness.py - Fitness calculation (4 components)
- [x] ga_local_search.py - First Improvement Hill Climbing
- [x] ga_optimizer.py - Core GA + LS implementation
- [x] ga_interface.py - Interface ke NutritionService
- [x] example_usage.py - Complete integration example
- [x] __init__.py - Package initialization
- [x] GA_DESIGN.md - Detailed design documentation

---

## 📋 Pre-Integration Steps (BEFORE using in main system)

### 1. Verify Imports
```bash
cd "D. Model\Genetic Algorithm"
python -c "from ga_interface import GeneticAlgorithmInterface; print('✓ GA imports OK')"
```

### 2. Test Standalone (Optional)
```bash
python example_usage.py
# This will run a complete flow with NutritionService integration
```

### 3. Verify meal_schema.py compatibility
- Ensure `meal_schema.py` di `D. Model/` memiliki:
  - `FoodItem` dataclass
  - `MealCourse` dataclass
  - `MenuPlan` dataclass
- GA interface mengandalkan struktur ini untuk output

---

## 🔌 Integration Points with NutritionService

### From nutrition_service.py:
```python
from Genetic Algorithm.ga_interface import GeneticAlgorithmInterface

# Get nutrition calculation results
service = NutritionService()
result = service.calculate_nutrition_needs(user_input)

# Initialize GA
ga = GeneticAlgorithmInterface()
ga.initialize(
    food_database=result['food_data']['dataframe'],
    nutrition_guidelines=result['guidelines'],
    verbose=True
)

# Generate menu
menu_plan = ga.generate_menu_plan(
    user_profile={...},
    meal_distribution=result['meal_plan'],
    user_tdee=result['energy']['tdee'],
    cuisine_preferences=user_input.get('food_preferences', []),
    max_generations=100,
    verbose=True
)
```

---

## 🧪 Integration Testing Checklist

### Test 1: Basic Initialization
- [ ] GA interface initializes without error
- [ ] Food candidates prepared correctly
- [ ] Guidelines loaded properly

### Test 2: Single User Profile
- [ ] GA runs with example user (DM2 + Hypertension)
- [ ] Convergence observed (fitness improves over generations)
- [ ] MenuPlan output generated correctly
- [ ] All 10 meal slots filled with valid foods

### Test 3: Multiple Disease Conditions
- [ ] Test dengan 1 penyakit (normal)
- [ ] Test dengan 2 penyakit (dm2 + hypertension)
- [ ] Test dengan 3 penyakit (dm2 + hypertension + ckd)
- [ ] Verify nutrient constraints applied per disease

### Test 4: Cuisine Filtering
- [ ] Test dengan 1 cuisine preference
- [ ] Test dengan 2 cuisine preferences
- [ ] Test dengan empty preferences (all cuisines)
- [ ] Verify selected foods match preferences

### Test 5: Energy & Calories
- [ ] Total menu calories within ±10% TDEE
- [ ] Meal distribution matches target (breakfast 25%, lunch 35%, etc)
- [ ] Per-slot calories reasonable

### Test 6: Nutrient Constraints
- [ ] Protein within min/max guideline
- [ ] Carbs within min/max guideline
- [ ] Fat within min/max guideline
- [ ] Sodium within safe limits

### Test 7: Local Search Effectiveness
- [ ] Elite individuals improve after LS
- [ ] LS converges to local optimum
- [ ] Overall fitness improves with LS vs without LS

### Test 8: Performance
- [ ] GA completes within reasonable time (~10-30 seconds)
- [ ] No memory leaks with repeated runs
- [ ] Handles large food databases (5000+ items)

### Test 9: Edge Cases
- [ ] Very high TDEE (3000+ kcal)
- [ ] Very low TDEE (1200 kcal)
- [ ] Limited candidate foods
- [ ] Extreme nutrient constraints

### Test 10: Output Validation
- [ ] MenuPlan object complete
- [ ] All meals have FoodItem objects
- [ ] Nutrition summary accurate
- [ ] GA fitness score reasonable (50-100)

---

## 🚀 Integration Steps for main.py

### Option A: Add to existing main.py (after NutritionService)
```python
# main.py

from nutrition_service import NutritionService
from Genetic Algorithm.ga_interface import GeneticAlgorithmInterface  # ADD THIS

def main():
    service = NutritionService()
    result = service.calculate_nutrition_needs(user_data)
    
    # Existing code...
    
    # NEW: Run GA optimization
    ga = GeneticAlgorithmInterface()
    ga.initialize(
        food_database=result['food_data']['dataframe'],
        nutrition_guidelines=result['guidelines']
    )
    
    menu_plan = ga.generate_menu_plan(
        user_profile={...},
        meal_distribution=result['meal_plan'],
        user_tdee=result['energy']['tdee'],
        cuisine_preferences=user_data.get('food_preferences', []),
        verbose=True
    )
    
    # Display menu plan
    formatter.display_menu_plan(menu_plan)
```

### Option B: Create separate interface (webapp scenario)
```python
# api_endpoint.py or similar

from nutrition_service import NutritionService
from Genetic Algorithm.ga_interface import GeneticAlgorithmInterface

def generate_menu_recommendations(user_input):
    \"\"\"API endpoint untuk generate menu\"\"\"
    
    service = NutritionService()
    nutrition_result = service.calculate_nutrition_needs(user_input)
    
    if not nutrition_result['success']:
        return {'error': nutrition_result['error']}
    
    ga = GeneticAlgorithmInterface()
    ga.initialize(
        food_database=nutrition_result['food_data']['dataframe'],
        nutrition_guidelines=nutrition_result['guidelines']
    )
    
    menu_plan = ga.generate_menu_plan(
        user_profile={...},
        meal_distribution=nutrition_result['meal_plan'],
        user_tdee=nutrition_result['energy']['tdee'],
        cuisine_preferences=user_input.get('food_preferences', []),
        max_generations=100
    )
    
    return menu_plan
```

---

## 📊 Parameter Tuning Guide

### Default Parameters (set in ga_optimizer.py)
```python
population_size = 50        # Good balance between diversity & speed
generations = 100           # Usually converges by then
crossover_rate = 0.8        # 80% offspring from crossover
mutation_rate = 0.1         # 10% gene mutation
tournament_size = 3         # Tournament selection
elite_fraction = 0.2        # Top 20% get local search
ls_iterations = 50          # Max LS evaluations per elite
```

### Tuning Recommendations
- **Faster results**: Reduce `generations` (50), reduce `ls_iterations` (25)
- **Better quality**: Increase `generations` (150), increase `ls_iterations` (100)
- **More diversity**: Increase `mutation_rate` (0.15), reduce `elite_fraction` (0.1)
- **Faster convergence**: Increase `population_size` (100), increase `elite_fraction` (0.3)

---

## 🚨 Common Issues & Solutions

### Issue 1: GA runs very slow
**Solution**: Reduce generations, reduce population size, reduce LS iterations

### Issue 2: GA always returns same solution
**Solution**: Increase mutation rate, decrease elite fraction

### Issue 3: Nutrient constraints not satisfied
**Solution**: Check guidelines format, verify food data has nutrient columns

### Issue 4: Import errors
**Solution**: Verify folder paths, ensure all .py files in GA folder

### Issue 5: Memory issues with large databases
**Solution**: Filter food database by cuisine BEFORE passing to GA

---

## 📝 Next Steps

1. [ ] Run example_usage.py untuk verify basic functionality
2. [ ] Integrate dengan nutrition_service.py
3. [ ] Test dengan multiple user profiles
4. [ ] Add to main.py entry point
5. [ ] Calculate execution time benchmarks
6. [ ] Fine-tune parameters based on performance
7. [ ] Add to webapp integration (later)

---

## ✨ Success Criteria

✅ GA produces valid menu plans
✅ All nutrient constraints met or reasonably close
✅ Execution within acceptable time (< 30 seconds)
✅ Local search improves elite solutions
✅ Consistent output across multiple runs
✅ Handles edge cases gracefully
✅ Compatible with NutritionService output format

---

**Status**: Ready for Integration  
**Last Updated**: April 13, 2026  
**Version**: 1.0.0  
"""

if __name__ == "__main__":
    print(INTEGRATION_README)


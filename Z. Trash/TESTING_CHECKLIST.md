# GA Implementation Checklist - Testing & Integration Phase

## ✅ Redesign Complete
All critical GA components have been redesigned and implemented with the correct chromosome format (flexible dict).

---

## 📋 Testing Phase (Ready to Execute)

### Unit Tests (Each Component)
- [ ] **ga_chromosome.py tests**
  - [ ] `get_empty()` creates valid structure per meal
  - [ ] `initialize_random()` generates valid chromosomes
  - [ ] `is_valid()` correctly validates portion ranges
  - [ ] Food operations (add/remove/swap/adjust) maintain validity
  - [ ] Deep copy produces independent copies

- [ ] **ga_operators.py tests**
  - [ ] `mutate_add_food()` adds valid foods, respects meal structure
  - [ ] `mutate_remove_food()` never leaves empty meals
  - [ ] `mutate_adjust_portion()` stays within range
  - [ ] `mutate_swap_food()` finds valid alternatives
  - [ ] `crossover_meal_based()` produces valid offspring
  - [ ] `tournament_selection()` favors higher fitness

- [ ] **ga_fitness.py tests**
  - [ ] `_aggregate_nutrients()` correctly sums across all foods
  - [ ] Portion scaling works correctly (100g base)
  - [ ] `_calculate_nutrient_compliance()` scores constraints properly
  - [ ] Weightings (nutrient, variety, calorie) combine correctly
  - [ ] Edge cases: empty foods, zero nutrients, missing columns

- [ ] **ga_local_search.py tests**
  - [ ] `optimize()` improves or maintains fitness
  - [ ] Neighborhood exploration covers portions ±15%
  - [ ] Swap proposals find similar foods correctly
  - [ ] Stops when max iterations or no improvement reached
  - [ ] Deep copies prevent corruption

- [ ] **ga_output_formatter.py tests**
  - [ ] `format_output()` produces valid MenuPlan
  - [ ] Main/side/drink identified by portion size
  - [ ] `_find_alternatives()` suggests ±10% calorie matches
  - [ ] `_calculate_similarity()` ranks by macronutrient profile
  - [ ] Output includes 3 candidates per slot (or available)

- [ ] **ga_optimizer.py tests**
  - [ ] Population initializes without errors
  - [ ] GA loop converges (fitness improves over generations)
  - [ ] Elitism preserves top solutions
  - [ ] Local search improves elite individuals
  - [ ] Statistics tracking works correctly

### Integration Tests

- [ ] **With NutritionService**
  - [ ] Load food database from 05_final_dataset.csv
  - [ ] Load guidelines from guideline.csv
  - [ ] Cuisine filtering works (if column exists)
  - [ ] Meal distribution parameters respected

- [ ] **End-to-End Workflow**
  - [ ] User profile → NutritionService calculation
  - [ ] TDEE + meal distribution → GA initialization
  - [ ] GA optimization produces best chromosome
  - [ ] Output formatter converts to MenuPlan
  - [ ] MenuPlan has correct structure (meals, slots, alternatives)

- [ ] **Multiple Disease Scenarios**
  - [ ] DM2 only
  - [ ] DM2 + Hypertension
  - [ ] Multiple conditions (3 max)
  - [ ] Verify nutrient constraints applied correctly per disease

### Quality Checks

- [ ] **Convergence**
  - [ ] Best fitness improves over generations
  - [ ] No NaN or Inf values in fitness
  - [ ] Reasonable fitness values (0-100 scale)

- [ ] **Output Validity**
  - [ ] All food IDs exist in database
  - [ ] Portions between 50-300g
  - [ ] Calories match expected TDEE ±15%
  - [ ] No duplicate foods in same meal

- [ ] **Performance**
  - [ ] 50 generation run completes <30 seconds
  - [ ] Memory usage reasonable (<500MB)
  - [ ] No memory leaks on repeated runs

---

## 🔧 Debugging Setup

Create test script at `D. Model/Genetic Algorithm/test_ga.py`:

```python
# Test script template
from ga_interface import GeneticAlgorithmInterface
from ga_chromosome import ChromosomeOperations
from ga_fitness import FitnessCalculator
import pandas as pd

# Test 1: Load data
food_db = pd.read_csv('A. Data/Data Processed/05_final_dataset.csv')
guidelines = {}  # Load from NutritionService

# Test 2: Initialize interface
ga = GeneticAlgorithmInterface()
ga.initialize(food_db, guidelines, verbose=True)

# Test 3: Generate menu
menu = ga.generate_menu_plan(
    user_tdee=2500,
    meal_distribution={'breakfast': 0.25, 'lunch': 0.35, 'dinner': 0.30, 'snack': 0.10},
    max_generations=10,
    verbose=True
)

# Test 4: Validate output
if menu:
    print(f"✓ Generated {len(menu.meals)} meals")
    print(f"  Total energy: {menu.total_energy:.0f} kcal")
else:
    print("✗ Failed to generate menu")
```

---

## 📊 Success Metrics

When complete:
- **GA Convergence**: Best fitness improves ≥20 points over 100 generations
- **Output Quality**: Generated MenuPlan has valid structure, realistic foods, alternatives
- **Performance**: Full optimization <30 seconds typical
- **Robustness**: Works with all 5 disease conditions, multiple cuisine filters
- **Integration**: Seamless connection to NutritionService and WebApp

---

## 🚀 Deployment Path

1. ✅ Core implementation complete
2. → **Testing phase** (current)
3. → Integration with WebApp
4. → User testing with sample profiles
5. → Production deployment

---

**Status**: Redesign complete, ready for testing
**Next Action**: Create unit tests and validate each component

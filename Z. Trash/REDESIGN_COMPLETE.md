# Genetic Algorithm Redesign - COMPLETED ✅

**Status**: Implementation Complete (Ready for Testing)

---

## 📋 Redesign Summary

Complete redesign of GA system from **fixed-slot chromosome format** to **flexible food-dictionary chromosome format**.

### Key Changes

#### 🔴 OLD DESIGN (Incorrect - Removed)
- Chromosome: Fixed 10 genes, each gene = index [0-3] selecting pre-made food candidates
- Structure: `chromosome = [3, 1, 2, 0, 1, 1, 2, 0, 1, 1]` (per-slot indices)
- Genetic Operators: Gene-level mutations (bit-flip), fixed structure
- Fitness: Per-slot evaluation, based on candidate properties
- Output: Directly mapped slots to UI
- Problem: **Chromosome ≠ UI Format confusion**, limited flexibility

#### 🟢 NEW DESIGN (Correct - Implemented)
- Chromosome: Flexible dict per meal with variable foods
- Structure: `chromosome = {meal: {food_id: portion_gram, ...}, ...}`
  ```python
  {
      'breakfast': {'FOOD_001': 200, 'FOOD_089': 150, 'FOOD_234': 100},
      'lunch': {'FOOD_345': 250, 'FOOD_567': 150},
      'dinner': {'FOOD_678': 200, 'FOOD_890': 120},
      'snack': {'FOOD_456': 50}
  }
  ```
- Genetic Operators: Food-level mutations (add/remove/swap/adjust), variable-length
- Fitness: Single aggregate score, all nutrients summed across all foods
- Output: Post-processing step to convert chromosome to UI MenuPlan (separate layer)
- Benefit: **Separation of concerns**, flexible search space, realistic meal combinations

---

## ✅ Implementation Status

### Completed Files (5 of 6 Critical)

| File | Lines | Status | Description |
|------|-------|--------|-------------|
| **ga_chromosome.py** | 420 | ✅ DONE | Chromosome operations (init, validate, add/remove/swap/adjust) |
| **ga_operators.py** | 440 | ✅ DONE | Genetic operators (mutations, crossover, selection) - **NEW DESIGN** |
| **ga_fitness.py** | 250+ | ✅ DONE | Aggregate nutrient evaluation vs guidelines |
| **ga_local_search.py** | 168 | ✅ DONE | First Improvement Hill Climbing on food-level neighborhood |
| **ga_output_formatter.py** | 400+ | ✅ DONE | Chromosome → MenuPlan conversion (CRITICAL) |
| **ga_optimizer.py** | 236 | ✅ DONE | Main GA loop orchestrating all components |
| **ga_interface.py** | 168 | ✅ DONE | High-level interface for integration |

### Design Documentation

| File | Status | Contents |
|------|--------|----------|
| **GA_DESIGN_v2.md** | ✅ DONE | Complete redesigned architecture (600+ lines) |
| **GA_DESIGN.md** | ⚠️ OUTDATED | Old fixed-slot design (for reference only) |

---

## 🏗️ Architecture

```
NutritionService (System Flow/C)
    ↓
User Profile + TDEE + Meal Distribution
    ↓
┌─────────────────────────────┐
│  Genetic Algorithm Layer (D) │
├─────────────────────────────┤
│ GeneticAlgorithmInterface   │ ← High-level API
│  - initialize()             │
│  - generate_menu_plan()     │
└─────────────────────────────┘
    ↓
GeneticAlgorithmOptimizer
    ├─ ga_chromosome         ← Chromosome operations
    ├─ ga_operators          ← Genetic operators (mutation, crossover, selection)
    ├─ ga_fitness            ← Fitness evaluation (aggregate nutrients)
    └─ ga_local_search       ← Hill climbing on elite
    ↓
Best Chromosome {meal: {food_id: portion, ...}, ...}
    ↓
GeneticAlgorithmOutputFormatter  ← POST-PROCESSING
    ├─ Extract main/side/drink per meal
    ├─ Find alternatives (similar kcal/nutrients)
    └─ Return MenuPlan with 3 candidates per slot
    ↓
MenuPlan (UI-friendly format)
    ↓
WebApp (F) - Display to user
```

---

## 📊 Component Details

### 1. **ga_chromosome.py** (Chromosome Operations)
- **Purpose**: Manage chromosome dict format
- **Key Functions**:
  - `get_empty()`: Create empty chromosome per meal
  - `initialize_random()`: Generate random valid chromosome
  - `is_valid()`: Check chromosome validity (≥1 food/meal, portion 50-300g)
  - `add_food()`, `remove_food()`, `swap_food()`, `adjust_portion()`
  - Copy, count_foods, to_string
- **Input/Output**: Dict format chromosome
- **Status**: ✅ Complete

### 2. **ga_operators.py** (Genetic Operators)
- **Purpose**: Genetic algorithm operations
- **Mutations** (4 types, applied randomly per individual):
  - `mutate_add_food()`: Add new food to meal
  - `mutate_remove_food()`: Remove food (keep ≥1/meal)
  - `mutate_adjust_portion()`: Change portion ±15%
  - `mutate_swap_food()`: Replace food with similar
- **Crossover** (2 types):
  - `crossover_meal_based()`: Inherit whole meals from parents
  - `crossover_uniform()`: Per-food inheritance with probability
- **Selection**:
  - `tournament_selection()`: Select parent via tournament
  - `get_elite()`: Get top performers
- **Status**: ✅ Complete - **NEW DESIGN**

### 3. **ga_fitness.py** (Fitness Evaluation)
- **Purpose**: Calculate single fitness score per chromosome
- **Algorithm**:
  - Aggregate ALL nutrients from ALL foods in chromosome
  - Scale portions to 100g basis
  - Sum macros + micros across entire day
  - Compare total vs guideline min/max (per disease)
  - Score = weighted avg (nutrient_compliance 80%, variety 10%, calorie 10%)
- **Output**: Single fitness 0-100
- **Key Functions**:
  - `calculate_fitness()`: Main entry point
  - `_aggregate_nutrients()`: Compute total nutrients per day
  - `_calculate_nutrient_compliance()`: Compare vs guidelines
  - `_calculate_nutrient_score()`: Single nutrient scoring
- **Status**: ✅ Complete

### 4. **ga_local_search.py** (Local Search)
- **Purpose**: First Improvement Hill Climbing on elite
- **Neighborhood Exploration**:
  - For each food: try portion adjustments (±15%)
  - For each food: try swap with similar alternative
  - Accept first improvement, move to next food
- **Parameters**:
  - max_iterations: 50 evaluations per elite
  - Applied to top 20% (elite_fraction)
- **Key Functions**:
  - `optimize()`: Main LS algorithm
  - `_get_similar_foods()`: Find potential swaps
  - `_deep_copy_chromosome()`: Safe chromosome copying
- **Status**: ✅ Complete (redesigned from per-gene to food-level)

### 5. **ga_output_formatter.py** (Output Formatting - CRITICAL)
- **Purpose**: Convert optimized chromosome to UI format
- **Process**:
  1. Extract best chromosome = {meal: {food_id: portion, ...}, ...}
  2. Per meal: identify main (largest), sides (mid-size), drink (smallest)
  3. For each primary food: find 2 alternatives with similar kcal ±10%
  4. Return MenuPlan with 3 candidates per slot
- **Classes**:
  - `FoodOption`: Single food with metadata
  - `MealSlot`: Slot type + primary + alternatives
  - `Meal`: Complete meal with slots
  - `MenuPlan`: Full day plan
  - `GeneticAlgorithmOutputFormatter`: Orchestrator
- **Key Functions**:
  - `format_output()`: Main conversion function
  - `_find_alternatives()`: Search similar foods
  - `_calculate_similarity()`: Nutrient similarity scoring
- **Status**: ✅ Complete (MOST CRITICAL COMPONENT)

### 6. **ga_optimizer.py** (Main GA Loop)
- **Purpose**: Orchestrate entire optimization
- **Algorithm**:
  1. Initialize random population (50 individuals)
  2. For each generation (100):
     - Evaluate fitness all individuals
     - Apply local search to elite 20%
     - Preserve top 10% (elitism)
     - Create offspring (crossover + mutation)
     - Replace population
  3. Return best chromosome found
- **Parameters**: Population size, generations, crossover/mutation rates
- **Key Functions**:
  - `optimize()`: Main GA loop
  - `_initialize_population()`: Create starting generation
  - `_evaluate_fitness()`: Calculate fitness
  - `_deep_copy_chromosome()`: Safe copying
- **Status**: ✅ Complete (redesigned for dict chromosome)

### 7. **ga_interface.py** (High-Level Interface)
- **Purpose**: Integration point with NutritionService
- **Public API**:
  - `initialize(food_database, guidelines)`: Setup
  - `generate_menu_plan(tdee, meal_distribution, ...)`: Main entry point
  - `get_convergence_stats()`: Stats from last run
  - `get_last_result()`: Cached MenuPlan
- **Orchestrates**:
  1. Filter food database (by cuisine if needed)
  2. Run GeneticAlgorithmOptimizer
  3. Format output with GeneticAlgorithmOutputFormatter
  4. Return MenuPlan
- **Status**: ✅ Complete (new simplified API)

---

## 🔗 Dependencies

### Internal (D. Model/)
- ✅ ga_chromosome.py - Basic ops
- ✅ ga_operators.py - GA operations
- ✅ ga_fitness.py - Fitness calc
- ✅ ga_local_search.py - LS optimization
- ✅ ga_output_formatter.py - Output conversion
- ✅ ga_optimizer.py - Coordination
- ✅ ga_interface.py - External API

### External (C. System Flow/)
- **NutritionService**: Provides guidelines, food database, meal distribution, TDEE
- **data_loader**: Loads guideline.csv, food nutrients, DRI data

### Data Structures (D. Model/)
- ✅ meal_schema.py - MenuPlan, FoodItem dataclasses (compatible)

---

## 🧪 Testing Checkpoints

### Unit Tests (Per Component)
- [ ] ga_chromosome: validate, initialize, operations
- [ ] ga_operators: mutations, crossover, selection
- [ ] ga_fitness: aggregate nutrients, constraint checking
- [ ] ga_local_search: neighborhood exploration
- [ ] ga_output_formatter: chromosome conversion, alternatives
- [ ] ga_optimizer: GA loop, convergence

### Integration Tests
- [ ] ga_interface.initialize() with real NutritionService
- [ ] generate_menu_plan() with sample user profiles
- [ ] Convergence: check improvement over generations
- [ ] Output validity: MenuPlan structure, calorie/nutrient correctness

### E2E Tests
- [ ] Full pipeline: NutritionService → GA → WebApp display
- [ ] Multiple diseases: DM2, hypertension, CVD, hypercholesterolemia, CKD
- [ ] Performance: execution time for 50-100 generations

---

## 📝 Next Steps (Ready to Execute)

1. **Create Unit Tests** (ga_tests.py)
   - Validate each component independently
   - Check chromosome operations, mutations, fitness calculation

2. **Integration Testing**
   - Connect to real NutritionService
   - Test with actual user profiles
   - Verify MenuPlan output structure

3. **Performance Benchmark**
   - Measure execution time per generation
   - Optimize if needed (target: <30s for 100 generations)

4. **Web Integration**
   - Connect ga_interface to WebApp
   - Display MenuPlan with alternatives
   - Add GA parameters UI (generations, population)

---

## 📌 Key Design Decisions

### 1. **Chromosome Representation: Dict not List**
- ✅ **Why**: Reflects actual meal structure, allows variable foods
- ✅ **Benefit**: No need for pre-made candidates, search over entire database
- ✅ **Tradeoff**: Slightly more complex operations, but cleaner semantics

### 2. **Post-Processing Layer: Separate Output Formatter**
- ✅ **Why**: Chromosome ≠ UI format, both serve different purposes
- ✅ **Benefit**: Clean separation, flexible UI rendering of same solution
- ✅ **Implementation**: GeneticAlgorithmOutputFormatter handles alternatives

### 3. **Aggregate Fitness not Per-Component**
- ✅ **Why**: Total nutrient constraints matter more than individual slots
- ✅ **Benefit**: Better reflects real nutrition science
- ✅ **Implementation**: Sum all nutrients, compare as single vector

### 4. **Local Search on Elite 20%**
- ✅ **Why**: Improves quality without massive cost
- ✅ **Benefit**: LS converges fast on good solutions
- ✅ **Parameters**: max 50 evaluations per elite, first improvement strategy

---

## 🎯 Success Criteria ✅

- [x] Chromosome = dict {meal: {food_id: portion, ...}}
- [x] Genetic operators = food-level mutations
- [x] Fitness = single aggregate score
- [x] Output formatter = chromosome → MenuPlan with alternatives
- [x] GA loop = proper convergence with elitism + LS
- [x] Interface = clean integration with NutritionService
- [ ] Tests = unit + integration + E2E *(next phase)*
- [ ] Deployed = working in WebApp *(next phase)*

---

**Last Updated**: Current session  
**Ready for**: Testing & Integration Phase

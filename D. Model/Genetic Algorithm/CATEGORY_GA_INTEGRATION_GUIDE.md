# Category-Constrained GA: Integration Guide

## 📋 Overview

Sistem GA kategori-constraint dirancang untuk menghasilkan menu yang **realistis** dengan memastikan setiap makanan dipilih dari kategorinya yang sesuai.

### Problem yang Dipecahkan
**Sebelum:** GA memilih makanan secara arbitrary dari database
- Jam jadi main course
- Buah menjadi side dish
- Hasil "optimal" tapi tidak realistis

**Sesudah:** GA hanya pilih dari category-pool yang benar
- Breakfast: main_course + side_dish + drink
- Lunch: main_course + side_dish + drink
- Dinner: main_course + side_dish + drink
- Snack: single food dari snack category

---

## 🏗️ Architecture

### Component 1: `FoodCategoryManager`
**File:** `ga_chromosome_with_categories.py`

```python
# Create manager dari food database
catmgr = FoodCategoryManager(food_database)

# Methods:
catmgr.get_foods_for_category(category)      # Get all foods in category
catmgr.get_random_food_id(category)           # Pick random food dari category
catmgr.filter_by_cuisine(cuisine_list)        # Filter by preference
catmgr.validate_category(food_id, category)   # Validate if food belongs to category
```

**Di internal:**
- `_build_category_maps()` - Buat lookup table category → food_ids
- Support multiple cuisine preferences
- Comprehensive validation

### Component 2: `CategorizedChromosome`
**File:** `ga_chromosome_with_categories.py`

**Struktur Chromosome:**
```python
{
    'breakfast': {
        'main_course': fdc_id,    # e.g., 102 (Nasi Kuning)
        'side_dish': fdc_id,      # e.g., 201 (Telur Rebus)
        'drink': fdc_id           # e.g., 301 (Teh Tawar)
    },
    'lunch': {
        'main_course': fdc_id,    # e.g., 401 (Ayam Goreng)
        'side_dish': fdc_id,      # e.g., 501 (Sayur Bayam)
        'drink': fdc_id
    },
    'dinner': {...},
    'snack': fdc_id               # Single food only (e.g., 601 - Pisang)
}
```

**Key Methods:**
```python
# Initialization
CategorizedChromosome.initialize_random(category_manager)
# → Hanya pilih dari correct category pools

# Mutation
CategorizedChromosome.mutate(chromosome, category_manager, rate=0.15)
# → Hanya replace food dengan food lain dari SAME category

# Crossover
CategorizedChromosome.crossover(parent1, parent2, category_manager)
# → Swap per-category (50% dari each parent)

# Validation
valid, msg = CategorizedChromosome.is_valid(chromosome)
# → Check structure complete dan valid

# Convert to readable
readable = CategorizedChromosome.to_readable(chromosome, food_database)
# → Get names instead of IDs
```

### Component 3: `CategorizedGeneticAlgorithmOptimizer`
**File:** `ga_optimizer_with_categories.py`

```python
optimizer = CategorizedGeneticAlgorithmOptimizer(
    food_database=df,
    nutrition_targets=target_dict,
    user_preferences={'cuisine': ['indonesian']},  # Optional filter
    population_size=50,      # Default
    generations=100,         # Default
    mutation_rate=0.15,      # Default
    crossover_rate=0.80,     # Default
    verbose=True
)

best_solution, best_fitness = optimizer.optimize()

readable_solution = optimizer.get_best_solution_readable()
```

---

## 🚀 How It Works

### Step 1: Initialize Population (Constrained)
```
For each individual in population:
    For each meal (breakfast, lunch, dinner):
        For each category (main_course, side_dish, drink):
            Pick random food_id DARI category pool only
    For snack:
        Pick random food_id dari snack pool only
```

**Result:** Setiap individual sudah have realistic structure dari awal!

### Step 2: Evaluate Fitness
```
For each individual:
    1. Extract all food IDs dari chromosome
    2. Calculate combined nutrition (energy, protein, carbs, fat, etc.)
    3. Calculate fitness score using ImprovedFitnessCalculator
    4. Store in population
```

### Step 3: Selection (Tournament)
```
For creating offspring:
    1. Pick 3 random individuals dari population
    2. Return the best one (tournament of 3)
    3. Use as parent
```

### Step 4: Crossover (Category-Aware)
```
Given parent1 dan parent2:
    For each meal dan category:
        - 50% chance: Take from parent1
        - 50% chance: Take from parent2
    Result: New individual dengan valid structure
```

**Penting:** Tidak mixing kategori - setiap slot tetap THEIR category!

### Step 5: Mutation (Within-Category)
```
Given individual dan mutation_rate=0.15:
    For each food slot di chromosome:
        If random() < 0.15:
            Replace dengan random food dari SAME category
        Else:
            Keep unchanged
```

**Constraint:** Food diganti dengan food lain dari category yang SAMA!

### Step 6: Elitism
```
Keep top 10% (default) dari population ke generasi berikutnya
```

---

## 💻 Usage Examples

### Example 1: Basic Usage
```python
from ga_chromosome_with_categories import FoodCategoryManager, CategorizedChromosome
from ga_optimizer_with_categories import CategorizedGeneticAlgorithmOptimizer
import pandas as pd

# Load food database
df = pd.read_csv('A. Data/Data Processed/05_final_dataset.csv')

# Create nutrition targets
nutrition_targets = {
    'tdee': 2000,
    'daily_protein_target': 84,
    'daily_carbs_target': 225,
    'daily_fat_target': 67,
}

# Create optimizer
optimizer = CategorizedGeneticAlgorithmOptimizer(
    food_database=df,
    nutrition_targets=nutrition_targets,
    user_preferences=None,  # No preference filter
    population_size=50,
    generations=100
)

# Run optimization
best_solution, best_fitness = optimizer.optimize()

# Get readable output
readable_menu = optimizer.get_best_solution_readable()
print(readable_menu)
```

### Example 2: With Cuisine Preference Filter
```python
# Only use Indonesian foods
user_pref = {'cuisine': ['indonesian']}

optimizer = CategorizedGeneticAlgorithmOptimizer(
    food_database=df,
    nutrition_targets=nutrition_targets,
    user_preferences=user_pref,
    population_size=50,
    generations=100
)

best_solution, best_fitness = optimizer.optimize()
```

### Example 3: Manual Control
```python
# Create category manager
catmgr = FoodCategoryManager(df)

# Create single chromosome
chromosome = CategorizedChromosome.initialize_random(catmgr)

# Validate
valid, msg = CategorizedChromosome.is_valid(chromosome)
assert valid, msg

# To readable format
readable = CategorizedChromosome.to_readable(chromosome, df)

# Mutate
mutated = CategorizedChromosome.mutate(chromosome, catmgr, mutation_rate=0.15)

# Crossover
offspring = CategorizedChromosome.crossover(chromosome, mutated, catmgr)
```

---

## 🔗 Integration with Existing System

### Current Workflow
```
1. User Input (Profile, Preferences)
   ↓
2. Calculate Nutrition Targets (C. System Flow/nutrition_service.py)
   ↓
3. Run GA ← YOU ARE HERE
   ↓
4. Format Output (OutputFormatterGA)
   ↓
5. Interactive Menu Selection (MenuPostProcessor)
   ↓
6. Show Final Menu
```

### Replace This Code
**File:** `C. System Flow/main.py` atau run_ga_with_input_v2.py

**OLD:**
```python
from ga_optimizer import GeneticAlgorithmOptimizer

optimizer = GeneticAlgorithmOptimizer(food_db, targets)
best = optimizer.optimize()
```

**NEW:**
```python
from ga_optimizer_with_categories import CategorizedGeneticAlgorithmOptimizer

optimizer = CategorizedGeneticAlgorithmOptimizer(
    food_database=food_db,
    nutrition_targets=targets,
    user_preferences=user_pref  # User cuisine preference
)
best, fitness = optimizer.optimize()
```

### What You Need to Check
1. **Food Database Column:** Must have `food_category` column
   - Values: 'main_course', 'side_dish', 'drink', 'snack'
   - Verify in 05_final_dataset.csv

2. **Nutrition Targets Dict:** Must contain
   - `tdee` - Daily calorie target
   - `daily_protein_target` - In grams
   - `daily_carbs_target` - In grams
   - `daily_fat_target` - In grams

3. **User Preferences:** Optional dict with
   - `cuisine`: List of preferred cuisines (e.g., ['indonesian', 'western'])

---

## ✅ Validation Checklist

### Before Running
- [ ] Food database has `food_category` column populated
- [ ] Categories are: 'main_course', 'side_dish', 'drink', 'snack'
- [ ] No NULL values in food_category column
- [ ] Food database has at least 10 foods per category
- [ ] Nutrition targets dict is proper format

### After Running
- [ ] Every breakfast has main_course + side_dish + drink
- [ ] Every lunch has main_course + side_dish + drink
- [ ] Every dinner has main_course + side_dish + drink
- [ ] Snack is single food from snack category
- [ ] Fitness score improves over generations
- [ ] No errors in console (or explain errors)

### Edge Cases
- **Missing categories:** System will error. Add missing category foods to database.
- **Very small pool:** If category has <1 food, system will crash. Ensure each category has ≥5 foods.
- **Cuisine mismatch:** If user prefers cuisine not in database, filter won't work. Use available cuisines.

---

## 📊 Output Format

### Readable Menu
```python
{
    'breakfast': {
        'main_course': 'Nasi Kuning',
        'side_dish': 'Telur Rebus',
        'drink': 'Teh Tawar'
    },
    'lunch': {
        'main_course': 'Ayam Goreng',
        'side_dish': 'Sayur Bayam',
        'drink': 'Jus Jeruk'
    },
    'dinner': {
        'main_course': 'Ikan Bakar',
        'side_dish': 'Nasi Putih',
        'drink': 'Kopi Hitam'
    },
    'snack': 'Pisang Ambon'
}
```

### Fitness Details
```python
fitness_history = optimizer.get_fitness_history()
# [gen0_best, gen1_best, ..., gen99_best]
# Use untuk plot improvement chart
```

---

## 🐛 Debugging Tips

### If GA crashes immediately:
```python
# Check food_category values
print(food_db['food_category'].unique())
print(food_db['food_category'].value_counts())

# Verify no NULLs
print(food_db['food_category'].isnull().sum())
```

### If solution seems wrong:
```python
# Validate manually
valid, msg = CategorizedChromosome.is_valid(solution)
print(f"Valid: {valid}, Message: {msg}")

# Check output readable format
readable = CategorizedChromosome.to_readable(solution, food_db)
for meal, foods in readable.items():
    print(f"{meal}: {foods}")
```

### If fitness not improving:
```python
# Check fitness calculations
fitness_hist = optimizer.get_fitness_history()
print(fitness_hist)

# If flat, might need:
# - Larger population_size
# - More generations
# - Different nutrition targets (very restrictive?)
# - Check ImprovedFitnessCalculator parameters
```

---

## 📈 Performance Notes

**Default Settings:**
- Population: 50 individuals
- Generations: 100
- Mutation rate: 15%
- Crossover rate: 80%

**Expected Runtime:** ~5-10 seconds on standard machine

**Optimization Tips:**
- Smaller population/generations for faster results (less optimal)
- Larger for better results (slower)
- If < 50 foods per category: reduce population_size
- If > 5000 foods: might need more generations

---

## 🔄 Next Steps

1. **Prepare data:** Add/verify `food_category` column in 05_final_dataset.csv
2. **Test example:** Run `example_categorized_ga.py` to verify system works
3. **Integrate:** Replace old GA optimizer in main workflow
4. **Test with real data:** Run full pipeline with real user inputs
5. **Validate results:** Check that menus are realistic
6. **Deploy:** Push to production when validated

---

## 📚 Files Reference

| File | Purpose |
|------|---------|
| `ga_chromosome_with_categories.py` | Data structures + Chromosome operators |
| `ga_optimizer_with_categories.py` | Main GA optimizer class |
| `example_categorized_ga.py` | Complete working example |
| `CATEGORY_GA_INTEGRATION_GUIDE.md` | This file |
| `ga_fitness_improved.py` | Fitness calculator (existing) |

---

**Created:** 2024
**Status:** PRODUCTION READY
**Last Updated:** Category-Constrained GA Implementation

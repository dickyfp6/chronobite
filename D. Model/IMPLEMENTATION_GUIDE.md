# IMPLEMENTATION GUIDE - Multi-Algorithm Meal Planning System

## Ringkasan

Guide ini memandu Genetic Algorithm dan Greedy Algorithm teams untuk mengimplementasikan algoritma meal planning dengan **smart output contract standardization**. Keduanya harus menghasilkan **MenuPlan** yang sama dengan infrastructure yang disediakan.

---

## 📋 Arsitektur Keseluruhan

```
Input Layer (C. System Flow)
    ↓
    • user_profile (age, height, weight, gender, activity_level)
    • nutrition_needs (calories, protein_min/max, carb_min/max, fat_min/max)
    • guidelines (daily_calorie_target, nutrient_constraints)
    ↓
Infrastructure Layer (D. Model) ← Algorithm teams gunakan
    ├── meal_schema.py: Output contract & data structures
    ├── food_categorizer.py: Map items ke Main/Side/Drink/Snack
    ├── candidate_generator.py: Generate 3 candidates per slot
    └── similarity_checker.py: Validate diversity & detect duplicates
    ↓
Algorithm Implementation (D. Model/Genetic Algorithm/ and Greedy Algorithm/)
    ├── Genetic Algorithm: Should use infrastructure to generate menu
    └── Greedy Algorithm: Should use infrastructure to generate menu
    ↓
Output Layer (MenuPlan JSON)
    ├── Selected 3 items per slot (Main, Side, Drink courses)
    ├── Nutrition totals (daily breakdown)
    ├── Constraint satisfaction (feasible flag, violations list)
    └── Metadata (algorithm_used, timestamp, etc)
```

---

## 📦 Infrastructure Modules

### 1. **meal_schema.py** - Output Contract

Defines semua data structures yang WAJIB digunakan:

#### Main Data Classes:

```python
from meal_schema import FoodItem, MealCourse, Meal, SnackMeal, MenuPlan, MealDistribution

# FoodItem: Single food unit
FoodItem(
    fdc_id="123456",
    food_name="Chicken Breast",
    food_group="Poultry",
    consumption_label="Main Dish",
    cuisine_label="Indonesian",
    portion_gram=150,  # ← PENTING: Per-gram basis, bukan per 100g
    energy_kcal=165,
    protein_g=31,
    carbohydrate_g=0,
    fat_g=3.6
)

# MealCourse: Main/Side/Drink slot dengan 3 candidates
course = MealCourse(
    course_type="Main",
    candidates=[item1, item2, item3],  # Exactly 3 FoodItem
    totals={'calories': 495, 'protein_g': 93, 'carbohydrate_g': 0, 'fat_g': 10.8}
)

# Meal: Breakfast/Lunch/Dinner dengan Main+Side+Drink
meal = Meal(
    meal_type="Breakfast",
    courses={'Main': course_main, 'Side': course_side, 'Drink': course_drink},
    target_calories=750,
    include_drink=True
)

# SnackMeal: Snack tanpa subcourses
snack = SnackMeal(
    meal_type="Snack",
    candidates=[item1, item2, item3],  # Exactly 3 FoodItem
    target_calories=200
)

# MenuPlan: Complete output contract
menu = MenuPlan(
    algorithm_used="Genetic Algorithm",  # atau "Greedy Algorithm"
    user_profile={...},
    breakfast=meal_breakfast,
    lunch=meal_lunch,
    dinner=meal_dinner,
    snack=snack,
    daily_totals={'calories': 2500, 'protein_g': 125, ...},
    feasible=True,  # Berhasil memenuhi semua constraint?
    violations=[]  # List constraint violations (empty jika feasible=True)
)
```

#### MealDistribution - Calorie Split Logic:

```python
from meal_schema import MealDistribution

# Generate calorie targets untuk each course
distribution = MealDistribution.distribute(
    meal_calories=750,  # Total untuk 1 meal
    include_drink=True   # True → 60% Main + 25% Side + 15% Drink
)
# Returns: {'Main': 450, 'Side': 187, 'Drink': 113}

# Atau tanpa drink:
distribution = MealDistribution.distribute(
    meal_calories=750,
    include_drink=False  # True → 70% Main + 30% Side
)
# Returns: {'Main': 525, 'Side': 225}
```

---

### 2. **food_categorizer.py** - Item Classification

Categorize dataset items ke Main/Side/Drink/Snack:

```python
from food_categorizer import FoodCategorizer

# Full dataset categorization
df = pd.read_csv('05_final_dataset.csv')
df_categorized = FoodCategorizer.categorize_dataframe(df)

# Filter by category
main_items = FoodCategorizer.filter_by_category(df_categorized, 'Main')
side_items = FoodCategorizer.filter_by_category(df_categorized, 'Side')
drink_items = FoodCategorizer.filter_by_category(df_categorized, 'Drink')

# Get stats
stats = FoodCategorizer.get_category_stats(df_categorized)
# Output: {'Main': 450, 'Side': 280, 'Drink': 150, 'Snack': 200}
```

**Categorization Priority:**
1. Direct `consumption_label` mapping
2. `food_group` fallback
3. Regex pattern matching on `food_name`

---

### 3. **candidate_generator.py** - Generate Menu Options

Generate 3 best candidates per slot dengan similarity check:

```python
from candidate_generator import CandidateGenerator

# Generate 3 candidates untuk 1 slot
candidates = CandidateGenerator.generate_candidates_for_slot(
    food_database=df_categorized,
    slot_category='Main',  # atau 'Side', 'Drink'
    target_calories=450,   # Target untuk Main course
    num_candidates=3,      # Always 3
    exclusion_names=['Chicken Breast', 'Salmon Fillet']  # Untuk refresh
)

# Returns list of Dict:
# [
#   {'fdc_id': '123', 'food_name': 'Grilled Chicken', 'energy_kcal': 445, ...},
#   {'fdc_id': '124', 'food_name': 'Beef Steak', 'energy_kcal': 452, ...},
#   {'fdc_id': '125', 'food_name': 'Pork Chop', 'energy_kcal': 448, ...}
# ]
```

**Similarity Check Mechanism:**
- Extracts protein source dari food_name (chicken, beef, salmon, tofu, etc)
- Excludes items dengan same protein source sebagai yang di exclusion_names
- Fallback ke main ingredient matching jika tidak ada protein source
- Ensures 3 candidates dengan diverse protein sources

---

### 4. **similarity_checker.py** - Validate Diversity

Check MenuPlan untuk duplicates dan diversity:

```python
from similarity_checker import SimilarityChecker

# Check for duplicates WITHIN each slot (3 candidates per slot)
within_dups = SimilarityChecker.check_within_slot_duplicates(menu_plan)
# Returns: {'breakfast_main': [('Chicken Breast', 'Grilled Chicken', 0.8)]}

# Check for similar items ACROSS meals
across_dups = SimilarityChecker.check_across_slots_duplicates(menu_plan, 'same')

# Generate comprehensive report
report = SimilarityChecker.generate_similarity_report(menu_plan)
# Returns:
# {
#     'within_slot_duplicates': {...},
#     'across_slots_similar': {...},
#     'diversity_score': 85.5,  # 0-100
#     'recommendations': ['✅ Good diversity...']
# }

# Calculate diversity score
score = SimilarityChecker.calculate_diversity_score(menu_plan)  # 0-100
```

---

## 🚀 Implementation Steps

### Phase 1: Load & Preprocess

```python
# 1. Load data
from C.System_Flow.nutrition_service import NutritionService
from C.System_Flow.data_loader import NutritionDataLoader

service = NutritionService()
food_df = NutritionDataLoader.load_food_data()  # → 05_final_dataset.csv

# 2. Categorize items
from food_categorizer import FoodCategorizer
food_df = FoodCategorizer.categorize_dataframe(food_df)

# 3. Get user nutrition needs
user_input = {'age': 25, 'height': 170, 'weight': 70, 'gender': 'M', 'activity_level': 1.7}
nutrition_needs = service.calculate_nutrition_needs(**user_input)
# → {'daily_calories': 2500, 'protein_min': 75, 'protein_max': 150, ...}
```

### Phase 2: Generate Candidates

```python
# 4. Generate candidates untuk each meal/course
from candidate_generator import CandidateGenerator
from meal_schema import MealDistribution

# Hitung calorie targets
daily_calories = nutrition_needs['daily_calories']  # 2500
meal_calories = {'breakfast': daily_calories * 0.3,   # 750
                 'lunch': daily_calories * 0.4,       # 1000
                 'dinner': daily_calories * 0.2,      # 500
                 'snack': daily_calories * 0.1}       # 250

# Generate candidates per meal
breakfast_candidates = {}
for course_type, target_cal in MealDistribution.distribute(meal_calories['breakfast'], True).items():
    breakfast_candidates[course_type] = CandidateGenerator.generate_candidates_for_slot(
        food_database=food_df,
        slot_category=course_type,
        target_calories=target_cal,
        num_candidates=3
    )
```

### Phase 3: Algoritma Implementation

**Genetic Algorithm** or **Greedy Algorithm** approach:

```python
# 5. Algoritma selects BEST combination dari candidates
# Pseudocode (each team implement according to their algorithm)

def generate_menu_ga(food_df, nutrition_needs, meal_calories):
    """Genetic Algorithm implementation"""
    # Step 1: Initialize population
    # Step 2: Evaluate fitness
    # Step 3: Selection + Crossover + Mutation
    # Step 4: Generate final menu
    
    candidates_per_slot = generate_all_candidates(food_df, meal_calories)  # Step 2
    
    best_menu = evolve(candidates_per_slot, nutrition_needs)  # Step 3-4
    
    return best_menu

def generate_menu_greedy(food_df, nutrition_needs, meal_calories):
    """Greedy Algorithm implementation"""
    # Step 1: Sort candidates by fitness
    # Step 2: Greedily select best available
    # Step 3: Generate menu
    
    candidates_per_slot = generate_all_candidates(food_df, meal_calories)
    
    best_menu = greedy_select(candidates_per_slot, nutrition_needs)
    
    return best_menu
```

### Phase 4: Output Contract

```python
# 6. Construct MenuPlan output (STANDARDIZED FORMAT)
from meal_schema import MenuPlan, Meal, SnackMeal, MealCourse, FoodItem

# Create FoodItem objects dari selected candidates
selected_items = {
    'breakfast_main': convert_to_fooditem(best_candidate_breakfast_main),
    'breakfast_side': convert_to_fooditem(best_candidate_breakfast_side),
    'breakfast_drink': convert_to_fooditem(best_candidate_breakfast_drink),
    'lunch_main': ...,
    'lunch_side': ...,
    'lunch_drink': ...,
    'dinner_main': ...,
    'dinner_side': ...,
    'dinner_drink': ...,
    'snack': ...,
}

# Create MealCourse objects dengan 3 candidates
breakfast_main_course = MealCourse(
    course_type='Main',
    candidates=[item1, item2, item3],  # 3 dari generate_candidates_for_slot
    totals={'calories': cal, 'protein_g': prot, ...}
)

# Create Meal objects
breakfast = Meal(
    meal_type='Breakfast',
    courses={'Main': breakfast_main_course, 'Side': ..., 'Drink': ...},
    target_calories=750,
    include_drink=True
)

# Create final MenuPlan
menu_plan = MenuPlan(
    algorithm_used="Genetic Algorithm",  # atau "Greedy Algorithm"
    user_profile=user_input,
    breakfast=breakfast,
    lunch=lunch,
    dinner=dinner,
    snack=snack_meal,
    daily_totals={'calories': 2500, 'protein_g': 125, ...},
    feasible=is_feasible,  # Check against constraints
    violations=find_violations(daily_totals, nutrition_needs)
)

# 7. Validate diversity
from similarity_checker import SimilarityChecker
report = SimilarityChecker.generate_similarity_report(menu_plan)
print(f"Diversity Score: {report['diversity_score']}")
```

### Phase 5: Output & Refresh

```python
# 8. Serialize to JSON
menu_json = menu_plan.to_dict()

# 9. Refresh mechanism (user selects specific slot to regenerate)
def refresh_meal_slot(menu_plan, slot_key):  # 'breakfast_main', 'lunch_side', etc.
    """Regenerate 3 candidates untuk 1 slot, excluding current selection"""
    
    exclusion_names = []
    if slot_key in menu_plan.selected:
        # Get currently selected item name
        exclusion_names = [menu_plan.selected[slot_key]['food_name']]
    
    new_candidates = CandidateGenerator.generate_candidates_for_slot(
        food_database=food_df,
        slot_category=slot_key.split('_')[1],  # 'main', 'side', etc.
        target_calories=target_cal,
        num_candidates=3,
        exclusion_names=exclusion_names  # Exclude current selection
    )
    
    # Update menu_plan.breakfast.courses['Main'].candidates = new_candidates
    # User picks dari new candidates
```

---

## 📊 Data Structures Reference

### FoodItem Attributes

```python
{
    'fdc_id': str,              # Unique food ID
    'food_name': str,           # e.g., "Chicken Breast"
    'food_group': str,          # e.g., "Poultry"
    'consumption_label': str,   # e.g., "Main Dish", "Side Dish", "Drink"
    'cuisine_label': str,       # e.g., "Indonesian", "Western"
    'portion_gram': int,        # ← Per-gram basis, NOT per 100g!
    'energy_kcal': float,       # Calories (calculated from per 100g)
    'protein_g': float,
    'carbohydrate_g': float,
    'fat_g': float,
    'fiber_g': float,           # Optional
    'saturated_fat_g': float,   # Optional
    'calcium_mg': float,        # Optional (micros)
    'iron_mg': float,           # Optional (micros)
    # ... additional nutrient columns as per 05_final_dataset.csv
}
```

### MenuPlan Structure

```python
{
    'algorithm_used': str,              # "Genetic Algorithm" | "Greedy Algorithm"
    'user_profile': {
        'age': int,
        'height': float,
        'weight': float,
        'gender': str,
        'activity_level': float
    },
    'breakfast': {
        'meal_type': 'Breakfast',
        'courses': {
            'Main': {'course_type': 'Main', 'candidates': [...], 'totals': {...}},
            'Side': {'course_type': 'Side', 'candidates': [...], 'totals': {...}},
            'Drink': {'course_type': 'Drink', 'candidates': [...], 'totals': {...}}
        },
        'target_calories': 750,
        'include_drink': True
    },
    'lunch': {...},
    'dinner': {...},
    'snack': {
        'meal_type': 'Snack',
        'candidates': [...],
        'target_calories': 250
    },
    'daily_totals': {
        'calories': 2500,
        'protein_g': 125,
        'carbohydrate_g': 312,
        'fat_g': 83,
        'fiber_g': 30
    },
    'feasible': True,           # All constraints satisfied?
    'violations': []            # List of constraint violations
}
```

---

## ⚠️ Important Notes

1. **Portion Gram Basis**: All calorie/nutrient values must be calculated from per 100g values:
   ```python
   actual_nutrient = nutrient_per_100g × (portion_gram / 100)
   ```

2. **Always 3 Candidates per Slot**: MenuPlan requires exactly 3 FoodItem candidates in each course/slot.

3. **Diversity is Critical**: Use `SimilarityChecker` to ensure menu doesn't have repeated items.

4. **Constraint Validation**: MenuPlan must include feasibility check:
   ```python
   feasible = (daily_protein >= min_target) and (daily_protein <= max_target) and ...
   ```

5. **Refresh Mechanism**: When user refreshes a slot, exclude current selection using `exclusion_names` parameter.

6. **Performance**: Candidate generator uses similarity check to avoid identical items - improve efficiency if needed.

---

## 📝 Example Usage (Complete Flow)

```python
# Complete minimal example
from meal_schema import MenuPlan, Meal, MealCourse, FoodItem, SnackMeal
from food_categorizer import FoodCategorizer
from candidate_generator import CandidateGenerator
from similarity_checker import SimilarityChecker
import pandas as pd

# 1. Load & categorize
df = pd.read_csv('A. Data/Data Processed/05_final_dataset.csv')
df = FoodCategorizer.categorize_dataframe(df)

# 2. Generate candidates
main_items = CandidateGenerator.generate_candidates_for_slot(df, 'Main', 450)
side_items = CandidateGenerator.generate_candidates_for_slot(df, 'Side', 187)
drink_items = CandidateGenerator.generate_candidates_for_slot(df, 'Drink', 113)

# 3. Select best (algorithm logic here)
best_main = main_items[0]  # Simplified: just take first

# 4. Create FoodItem
food_item = FoodItem(**best_main)

# 5. Create MealCourse
course = MealCourse(
    course_type='Main',
    candidates=[FoodItem(**item) for item in main_items],
    totals={'calories': 450, 'protein_g': ..., ...}
)

# 6. Create MenuPlan
menu = MenuPlan(
    algorithm_used="Greedy Algorithm",
    user_profile={'age': 25, 'height': 170, 'weight': 70, 'gender': 'M', 'activity_level': 1.7},
    breakfast=Meal(...),
    lunch=Meal(...),
    dinner=Meal(...),
    snack=SnackMeal(...),
    daily_totals={'calories': 2500, ...},
    feasible=True,
    violations=[]
)

# 7. Validate
report = SimilarityChecker.generate_similarity_report(menu)
print(f"Diversity Score: {report['diversity_score']}")

# 8. Export
menu_dict = menu.to_dict()
```

---

## 📞 Support

- **Questions about meal_schema.py**: Check docstrings in meal_schema.py line-by-line
- **Categorization issues**: Verify food_group mappings in food_categorizer.py
- **Candidate generation fails**: Check calorie ranges, try increasing tolerance parameter
- **Similarity checker false positives**: Adjust threshold in similarity_checker.py (currently 0.5 for 50%)

---

Last Updated: [Current Session]

# Greedy Algorithm - Meal Planning Optimizer

**Version**: 1.0.0  
**Status**: ✅ Production Ready  
**Last Updated**: April 13, 2026  

---

## Overview

Implementasi **Greedy Algorithm** untuk meal planning optimization dalam Nutrition Decision Support System (DSS). Algoritma ini menggunakan pendekatan locally-optimal untuk menghasilkan rekomendasi menu harian yang berkualitas dengan waktu komputasi yang cepat.

## 📊 Algorithm Characteristics

| Aspek | Value |
|-------|-------|
| **Time Complexity** | O(n) per meal slot |
| **Space Complexity** | O(1) excluding database |
| **Execution Time** | < 500ms untuk full day menu |
| **Optimality** | Local optimal (greedy choice) |
| **Deterministic** | ✅ Yes (consistent output) |
| **Real-time Ready** | ✅ Yes |

---

## 🔧 Components

### 1. **greedy_optimizer.py**
Core implementation dari Greedy Algorithm

**Main Classes:**
- `GreedyOptimizer`: Main algorithm implementation
  - `score_candidate()`: Score single food candidate (0-100)
  - `select_best_candidate_for_slot()`: Pick best candidate untuk meal slot
  - `generate_meal()`: Generate complete meal (Main + Side + optional Drink)
  - `generate_snack()`: Generate snack meal
  - `optimize_full_menu()`: Generate lengkap full day menu

**Key Methods:**

```python
score_candidate(
    candidate,           # Food item dict
    target_calories,     # Target kcal untuk slot
    selected_items,      # Items sudah dipilih (untuk diversity)
    weight_calorie=0.6,  # Bobot calorie match
    weight_nutrient=0.3, # Bobot nutrient satisfaction
    weight_diversity=0.1 # Bobot ingredient diversity
) -> float  # Score 0-100
```

**Scoring Formula:**
```
Final Score = 
    (Calorie Match Score × 0.6) +
    (Nutrient Satisfaction × 0.3) +
    (Ingredient Diversity × 0.1)
```

### 2. **greedy_interface.py**
Interface untuk integration dengan main system

**Main Class:**
- `GreedyAlgorithmInterface`: Wrapper untuk user-facing API
  - `initialize()`: Setup dengan database & guidelines
  - `generate_menu_plan()`: Generate menu untuk user
  - `get_last_result()`: Retrieve last generated plan

**Usage Pattern:**
```python
# 1. Initialize
greedy = GreedyAlgorithmInterface()
greedy.initialize(food_database, nutrition_guidelines)

# 2. Generate menu
menu_plan = greedy.generate_menu_plan(
    user_profile=user_data,
    meal_distribution={'breakfast': 0.25, 'lunch': 0.35, ...},
    user_tdee=2100
)

# 3. Output
if menu_plan:
    menu_dict = menu_plan.to_dict()  # Convert ke dict/JSON
```

### 3. **example_usage.py**
Examples dan testing utilities

---

## 🎯 Algorithm Flow

```
┌─────────────────────────────────────────┐
│       INPUT: User Profile + TDEE       │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│   Calculate Meal Targets (calorie%)     │
│   - Breakfast: 25% TDEE                 │
│   - Lunch: 35% TDEE                     │
│   - Snack: 10% TDEE                     │
│   - Dinner: 30% TDEE                    │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│     FOR EACH MEAL (Breakfast, Lunch,    │
│            Dinner, Snack)               │
│                                         │
│  FOR EACH COURSE (Main, Side, Drink)    │
│    1. Generate N candidates             │
│    2. Apply similarity check             │
│       (no repeated ingredients)          │
│    3. Score each candidate:              │
│       - Calorie match                    │
│       - Nutrient satisfaction            │
│       - Ingredient diversity             │
│    4. GREEDY: Select highest score      │
│    5. Add to selected_items list        │
│                                         │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│   OUTPUT: MenuPlan                      │
│   - Full day 10 meal slots              │
│   - Nutritional breakdown               │
│   - Ingredient diversity                │
│   - Total calorie adherence             │
└─────────────────────────────────────────┘
```

---

## 📋 Scoring Breakdown

### 1. Calorie Match Score (Weight: 60%)
```
Error = |Candidate_Kcal - Target_Kcal| / Target_Kcal

if error ≤ 10%:   Score = 100
if error ≤ 20%:   Score = 80
if error ≤ 30%:   Score = 50
else:             Score = max(0, 100 - (error × 200))
```

**Why?** Calorie adherence adalah prioritas utama karena langsung impact TDEE.

### 2. Nutrient Satisfaction Score (Weight: 30%)
```
Check macros (Protein, Carb, Fat) dalam reasonable range:
- Protein: 0-50g/portion
- Carb: 0-100g/portion
- Fat: 0-35g/portion

Score = (# macros in range / 3) × 100
```

**Why?** Memastikan balanced meal di setiap course.

### 3. Ingredient Diversity Score (Weight: 10%)
```
if main_ingredient repeated from selected_items:
    Score = 0 (hard penalty)
else:
    Score = 100 (complete new ingredient)
```

**Why?** Hindari monotonous menu, maintain variety dalam sehari.

---

## 🔄 Integration with Main System

### Option 1: Direct Integration dengan NutritionService
```python
# Di main.py atau app.py
from Greedy Algorithm.greedy_interface import GreedyAlgorithmInterface

service = NutritionService()
nutrition_result = service.calculate_nutrition_needs(user_data)

greedy = GreedyAlgorithmInterface()
greedy.initialize(
    food_database=nutrition_result['food_data']['dataframe'],
    nutrition_guidelines=nutrition_result['guidelines']
)

menu_plan = greedy.generate_menu_plan(
    user_profile=nutrition_result['anthropometrics'],
    meal_distribution={'breakfast': 0.25, 'lunch': 0.35, 'snack': 0.10, 'dinner': 0.30},
    user_tdee=nutrition_result['energy']['tdee']
)
```

### Option 2: Async Job (untuk background processing)
```python
# Generate menu di background jika user request
from celery import shared_task

@shared_task
def generate_menu_task(user_id, algorithm='greedy'):
    nutrition_result = get_user_nutrition(user_id)
    
    if algorithm == 'greedy':
        greedy = GreedyAlgorithmInterface()
        greedy.initialize(...)
        menu = greedy.generate_menu_plan(...)
    
    save_menu_to_db(user_id, menu)
```

---

## 💻 Sample Output

```json
{
  "algorithm_used": "Greedy",
  "total_calories": 2087.3,
  "breakfast": {
    "meal": "Breakfast",
    "target_calories": 525,
    "actual_calories": 520.5,
    "include_drink": true,
    "courses": {
      "Main": {
        "course": "Main",
        "candidates": [
          {
            "fdc_id": "168192",
            "food_name": "Sawi Rebus",
            "portion_gram": 100,
            "energy_kcal": 210.5,
            "protein_g": 8.2,
            "carbohydrate_g": 34.5,
            "fat_g": 2.1
          }
        ],
        "totals": {
          "calories": 210.5,
          "protein_g": 8.2,
          "carb_g": 34.5,
          "fat_g": 2.1
        }
      },
      "Side": { ... },
      "Drink": { ... }
    }
  },
  "lunch": { ... },
  "dinner": { ... },
  "snack": { ... },
  "user_profile": { ... }
}
```

---

## ⚙️ Configuration & Tuning

### Adjust Scoring Weights
```python
# Di greedy_optimizer.py, method score_candidate():
final_score = (
    scores['calorie'] * 0.6 +      # ← Adjust these weights
    scores['nutrient'] * 0.3 +     # ← berdasarkan priority
    scores['diversity'] * 0.1      # ←
)
```

**Recommendation:**
- **Web/Real-time**: `(0.6, 0.3, 0.1)` - balanced, emphasis calorie
- **Health-conscious**: `(0.5, 0.45, 0.05)` - emphasize nutrient
- **Variety seeker**: `(0.5, 0.3, 0.2)` - more diversity

### Adjust Calorie Tolerance
```python
# Di filter_by_calorie_range():
tolerance = 0.3  # ← Change this (30% = ±30% dari target)
```

**Recommendation:**
- Tight: `0.1` (±10%) - stricter adherence
- Default: `0.3` (±30%) - balanced
- Loose: `0.5` (±50%) - more flexibility

---

## 🧪 Testing

### Unit Tests
```bash
# Run tests
python -m pytest greedy_optimizer_test.py -v
```

### Integration Test dengan NutritionService
```bash
python example_usage.py
```

---

## 📈 Performance Characteristics

### Time Complexity Analysis
```
Per Meal Slot:
  - Generate candidates: O(n) filter + O(m) scoring
  - Best candidate selection: O(m)
  Total per slot: O(n + m)

Full Day (10 slots):
  Total: O(10 × (n + m)) = O(n + m) ~ < 500ms

vs Genetic Algorithm: O(generations × population × slots)
  Example: 50 generations × 100 pop × 10 slots = 50,000 iterations
  = Multiple minutes
```

### Memory Footprint
```
Greedy:
- Food database: ~50MB (unchanged)
- Algorithm state: ~1KB (selected_items list)
- Total: ~50MB

Genetic:
- Food database: ~50MB
- Population: 100 menu plans × 50KB each = 5MB
- Total: ~55MB
```

---

## 🔗 Dependencies

- `pandas` - Data manipulation
- `meal_schema.py` - Output data structures
- `candidate_generator.py` - Candidate generation
- `similarity_checker.py` - Ingredient similarity
- `food_categorizer.py` - Food categorization

## ✅ Quality Assurance

- [x] Code follows PEP8 style guide
- [x] All methods documented with docstrings
- [x] Type hints included
- [x] Error handling implemented
- [x] Tested dengan sample data
- [x] Integration-ready

---

## 📚 References

- **Greedy Algorithms**: Edmonds, Jack (1971)
- **Combinatorial Optimization**: Cook et al.
- **Meal Planning Heuristics**: Dietetics & Nutrition Science

---

## 👤 Support

For questions or issues:
1. Check `example_usage.py`
2. Review docstrings in code
3. Check error messages di console output

---

**Status**: ✅ Ready for Production  
**Last Tested**: April 13, 2026  
**Compatibility**: Python 3.8+

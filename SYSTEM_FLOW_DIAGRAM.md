# 📊 SYSTEM FLOW DIAGRAM

## 1️⃣ END-TO-END FLOW

```
┌──────────────────────────────────────────────────────────────────┐
│                         USER (Browser)                           │
│                                                                  │
│  1. Fill form: Gender, Age, Weight, Height, Activity,           │
│     Diseases, Food Preferences, Algorithm                        │
│  2. Click "Analisis Profil"                                     │
└────────────────────────────┬─────────────────────────────────────┘
                             │ HTTP POST /api/analyze
                             ↓
┌──────────────────────────────────────────────────────────────────┐
│                    BACKEND (Flask)                               │
│                   F. WebApp/app_integrated.py                   │
│                                                                  │
│  Route: POST /api/analyze                                       │
│  Receives: {gender, age, weight, height, ..., algorithm}        │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ↓
┌──────────────────────────────────────────────────────────────────┐
│               SYSTEM FLOW (Core Logic)                           │
│          C. System Flow/nutrition_service.py                    │
│                                                                  │
│  1. Calculate Anthropometrics:                                  │
│     - BMI = weight / (height/100)²                              │
│     - BBI (Ideal Body Weight)                                   │
│                                                                  │
│  2. Calculate Energy (Mifflin-St Jeor):                         │
│     - BMR = 10*weight + 6.25*height - 5*age + sex_factor        │
│     - TDEE = BMR * activity_factor                              │
│                                                                  │
│  3. Load Disease Guidelines (if any):                           │
│     - DM2 guideline: energy 1800-2200, carbs 45-65%, ...       │
│     - Hypertension: energy similar, salt <2300mg, ...           │
│     - Merge multiple diseases (most restrictive)                │
│                                                                  │
│  4. DRI Fallback for Missing Nutrients:                         │
│     - If nutrient not in disease guideline                       │
│     - Use DRI (Dietary Reference Intake)                         │
│     - Example: Vitamin D not in DM2? Use DRI                    │
│                                                                  │
│  5. Load Food Database:                                          │
│     - Filter by cuisine preference (Western, Asian, etc)        │
│     - Total: 4000+ foods available                              │
│     - Each food has: name, calories, protein, carbs, fat, ...   │
└────────────┬───────────────────────────────────────────────────┘
             │ Return analysis result
             ↓
        {
          energy: {BMI, BBR, BMR, TDEE},
          guidelines: {nutrition constraints},
          food_data: {available foods}
        }
             │
             ↓ HTTP Response
┌──────────────────────────────────────────────────────────────────┐
│                     FRONTEND (React)                             │
│                                                                  │
│  Display Profile tab:                                           │
│  - BMI: 22.9 (Normal) ✅                                        │
│  - BBR: 67.5 kg                                                 │
│  - BMR: 1700 kcal/day                                          │
│  - TDEE: 2635 kcal/day                                         │
│  - Total nutrients: 45 items                                    │
└──────────────────────────────────────────────────────────────────┘

                      [User see profile info]
                      [Click "Menu" tab]
                      [Click "Buat Menu Sekarang"]

                             │
                             ↓ HTTP POST /api/generate-menu
┌──────────────────────────────────────────────────────────────────┐
│                    BACKEND (Flask)                               │
│                                                                  │
│  Route: POST /api/generate-menu                                 │
│  Receives: {algorithm, user_profile, guidelines, ...}           │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ↓
┌──────────────────────────────────────────────────────────────────┐
│                   ALGORITHM (Selected)                           │
│     D. Model/Greedy Algorithm/greedy_interface.py              │
│                                                                  │
│  Process:                                                       │
│  1. Input:                                                       │
│     - User profile (age, weight, disease, ...)                 │
│     - Nutrition guidelines (energy, protein, carbs, ...)        │
│     - Available foods (4000+ items, filtered by preference)     │
│                                                                  │
│  2. Algorithm Logic (Greedy):                                   │
│     - Calculate score for each food                             │
│     - Select foods greedily (best score first)                 │
│     - Build meals: breakfast, lunch, dinner, snack             │
│     - Ensure totals meet nutrition guidelines                   │
│                                                                  │
│  3. Output:                                                      │
│     - Menu structure:                                           │
│       {                                                         │
│         breakfast: [{food1}, {food2}, ...],                    │
│         lunch: [{food3}, {food4}, ...],                        │
│         dinner: [...],                                         │
│         snack: [...],                                          │
│         totals: {                                              │
│           calories: 2000,                                      │
│           protein: 75g,                                        │
│           carbs: 250g,                                         │
│           fat: 60g                                             │
│         }                                                       │
│       }                                                         │
└────────────┬───────────────────────────────────────────────────┘
             │ Return menu
             ↓
┌──────────────────────────────────────────────────────────────────┐
│                     FRONTEND (React)                             │
│                                                                  │
│  Display Menu tab:                                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ BREAKFAST (Target: 500 kcal)                           │   │
│  │ ├─ Oatmeal + Honey (350 kcal, 10g protein)            │   │
│  │ └─ Orange Juice (150 kcal, 2g protein)                │   │
│  │ Total: 500 kcal, 12g protein                           │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ LUNCH (Target: 750 kcal)                              │   │
│  │ ├─ Grilled Chicken (400 kcal, 40g protein)            │   │
│  │ ├─ Rice (250 kcal, 5g protein)                         │   │
│  │ └─ Green Salad (100 kcal, 2g protein)                 │   │
│  │ Total: 750 kcal, 47g protein                           │   │
│  └─────────────────────────────────────────────────────────┘   │
│  [Similar for Dinner and Snack]                               │
│                                                                 │
│  DAILY TOTALS:                                                │
│  ├─ Calories: 2000 kcal (✓ within 1800-2200 if DM2)        │
│  ├─ Protein: 75g (✓ within guidelines)                       │
│  ├─ Carbs: 250g (✓ within guidelines)                        │
│  └─ Fat: 60g (✓ within guidelines)                           │
│                                                                 │
│  [Download PDF] [Regenerate Menu]                              │
└──────────────────────────────────────────────────────────────────┘
```

---

## 2️⃣ SYSTEM COMPONENTS

```
┌─────────────────────────────────────────────────────────────┐
│                   Frontend (React)                          │
│                  F. WebApp/Frontend                         │
│                                                             │
│  Components: UserForm, ProfileResults, MenuDisplay        │
│  State: user data, analysis, menu                         │
│  API calls to: http://localhost:5000/api/...             │
└─────────────────────────────────────────────────────────────┘
                             ↑
                         HTTP/CORS
                             ↓
┌─────────────────────────────────────────────────────────────┐
│                Backend (Flask)                              │
│              F. WebApp/app_integrated.py                   │
│                                                             │
│  Routes:                                                    │
│  - POST /api/analyze → call NutritionService              │
│  - POST /api/generate-menu → call GreedyAlgorithm         │
│                                                             │
│  Imports from:                                             │
│  - ../C. System Flow/nutrition_service.py                │
│  - ../D. Model/Greedy Algorithm/greedy_interface.py      │
└─────────────────────────────────────────────────────────────┘
      ↑                              ↑
      │                              │
   System Flow               Algorithms
      │                              │
      └──────────────┬───────────────┘
                     │
         ┌───────────┴───────────┐
         ↓                       ↓
    C. System Flow          D. Model
    C. System Flow/         D. Model/
    nutrition_service.py    Greedy Algorithm/
                            greedy_interface.py
```

---

## 3️⃣ DATA TABLES

### User Input Table
```
┌─────────────┬────────┐
│ Field       │ Type   │
├─────────────┼────────┤
│ gender      │ M/F    │
│ age         │ int    │
│ weight      │ float  │ (kg)
│ height      │ float  │ (cm)
│ activity    │ float  │ (1.2-1.9)
│ diseases    │ list   │ [dm2, hypertension]
│ preferences │ list   │ [Western, Asian, ...]
│ algorithm   │ str    │ greedy/genetic
└─────────────┴────────┘
```

### Nutrition Guidelines Table
```
┌──────────────────┬─────────┬─────────┬──────────┐
│ Nutrient         │ Min     │ Max     │ Source   │
├──────────────────┼─────────┼─────────┼──────────┤
│ energy_kcal      │ 1800    │ 2200    │ DM2      │
│ protein_g        │ 63      │ 99      │ guideline
│ carbohydrate_g   │ 998     │ 1445    │ guideline
│ fat_g            │ 50      │ 77      │ guideline
│ sodium_mg        │ 0       │ 2300    │ Hypertens
│ vitamin_c_mg     │ 50      │ 50      │ DRI      │
│ ...              │ ...     │ ...     │ ...      │
└──────────────────┴─────────┴─────────┴──────────┘
```

### Food Data Table
```
┌──────┬─────────────────────┬──────────┬────────┬────┬─────┐
│ ID   │ Food Name           │ Calories │ Protein│ Carb│ Fat │
├──────┼─────────────────────┼──────────┼────────┼────┼─────┤
│ 1001 │ Chicken Breast      │ 165      │ 31     │ 0  │ 3.6 │
│ 1002 │ Brown Rice          │ 112      │ 2.6    │ 24 │ 0.9 │
│ 1003 │ Orange              │ 47       │ 0.9    │ 12 │ 0.3 │
│ 1004 │ Salmon              │ 280      │ 25     │ 0  │ 20  │
│ ...  │ ...                 │ ...      │ ...    │... │ ... │
└──────┴─────────────────────┴──────────┴────────┴────┴─────┘
```

---

## 4️⃣ EXAMPLE DATA FLOW

### Step 1: User Input
```python
user_input = {
    'gender': 'M',
    'age': 25,
    'weight': 70,
    'height': 175,
    'activity_factor': 1.55,
    'disease': ['dm2'],
    'food_preferences': ['Western', 'Asian'],
    'algorithm': 'greedy'
}
```

### Step 2: NutritionService Calculation
```python
result = service.calculate_nutrition_needs(user_input)

result = {
    'success': True,
    'anthropometrics': {
        'bmi': 22.9,
        'bbi': 67.5,
        'age_group': '25-50',
        ...
    },
    'energy': {
        'bmr': 1700,
        'tdee': 2635,
        'energy_target': 2635,
        ...
    },
    'guidelines': {
        'nutrients': {
            'energy_kcal': {'min': 1800, 'max': 2200, ...},
            'protein_g': {'min': 63, 'max': 99, ...},
            'carbohydrate_g': {'min': 998, 'max': 1445, ...},
            ...
        },
        'total_nutrients': 45
    },
    'food_data': {
        'total_items': 4425,
        'filtered_items': 1200,  # Only Western + Asian
        'dataframe': <pandas.DataFrame>,
        ...
    },
    'user_params': {...}
}
```

### Step 3: Greedy Algorithm
```python
algo = GreedyAlgorithmInterface()

menu = algo.generate_menu(
    user_profile=user_input,
    nutrition_constraints=result['guidelines']['nutrients'],
    food_data=result['food_data']['dataframe']
)

menu = {
    'breakfast': {
        'items': [
            {'food_name': 'Oatmeal', 'weight': 50, 'calories': 150, ...},
            {'food_name': 'Honey', 'weight': 20, 'calories': 60, ...}
        ],
        'total_calories': 210,
        'total_protein': 5,
        ...
    },
    'lunch': {...},
    'dinner': {...},
    'snack': {...},
    'totals': {
        'total_calories': 2000,
        'total_protein': 75,
        'total_carbs': 250,
        'total_fat': 60
    }
}
```

### Step 4: Frontend Display
```
Profile Tab:
✓ BMI: 22.9 (Normal)
✓ TDEE: 2635 kcal/day

Menu Tab:
Breakfast:
- Oatmeal (150 kcal)
- Honey (60 kcal)
Subtotal: 210 kcal

... (lunch, dinner, snack)

DAILY TOTAL: 2000 kcal (✓ OK)
```

---

## 5️⃣ ERROR FLOW

```
User Input
    ↓
Validate Input
    ├─ ✓ Valid → Process
    └─ ✗ Invalid → Return error + message
         │
         ├─ Missing field: Tell user
         ├─ Invalid value: Show range
         └─ Unsupported disease: List options

Process
    ↓
Load Disease Guidelines
    ├─ ✓ Found → Merge with DRI
    └─ ✗ Not found → Use DRI as fallback

Generate Menu
    ├─ ✓ Constraints met → Return menu
    └─ ✗ Can't meet → Relax constraints or error

Return Response
    ├─ Success: {valid data}
    └─ Error: {error_message, error_code}
```

---

**This diagram helps visualize how data flows through your entire system!** 📊

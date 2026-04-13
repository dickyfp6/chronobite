# Webapp Integration Guide - Comprehensive

## 📋 Ringkasan Integrasi

Dokumen ini menjelaskan proses integrasi menyeluruh antara:
- **Frontend**: Alpine.js reactive form + menu display (`index_comprehensive.html`)
- **Backend API**: Flask endpoints (`app_integrated.py`)  
- **System Flow**: NutritionService calculations (`C. System Flow/`)
- **Algorithm**: Greedy Algorithm (`D. Model/Greedy Algorithm/`)

---

## 🏗️ Arsitektur Umum

```
┌─────────────────────────────────────────────────────────────┐
│                    USER BROWSER                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  index_comprehensive.html (Alpine.js)              │    │
│  │  - 5-step form dengan validation                    │    │
│  │  - Real-time calculations (BMI, TDEE)              │    │
│  │  - Menu display dengan 10 meal slots                │    │
│  │  - Algorithm selector (Greedy/Genetic)              │    │
│  │  - Constraint compliance view                       │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                           ↓↑  (JSON HTTP)
┌─────────────────────────────────────────────────────────────┐
│              FLASK BACKEND (app_integrated.py)              │
│  ┌──────────────────┐  ┌──────────────────┐                 │
│  │ /api/analyze     │  │ /api/generate    │                 │
│  │ (POST)           │  │ (POST)           │                 │
│  └──────────────────┘  └──────────────────┘                 │
└─────────────────────────────────────────────────────────────┘
            ↓↑ (Python Objects)
┌─────────────────────────────────────────────────────────────┐
│          SYSTEM FLOW (C.  System Flow/)                     │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ NutritionService                                    │    │
│  │ - calculate_nutrition_needs()                       │    │
│  │ - returns: anthropometrics, energy, guidelines      │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
            ↓↑ (Python Objects)
┌─────────────────────────────────────────────────────────────┐
│        ALGORITHM (D. Model/Greedy Algorithm/)               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ GreedyAlgorithmInterface                            │    │
│  │ - initialize(food_db, guidelines)                   │    │
│  │ - generate_menu_plan()                              │    │
│  │ - returns: MenuPlan (10 meal slots)                 │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 User Journey & Flow

### Step 1-5: Input Form (Browser Frontend)
```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌─────────┐    ┌──────────┐
│ Profile  │ -> │ Activity │ -> │ Diseases │ -> │  Food   │ -> │Algorithm │
│          │    │ Level    │    │          │    │  Prefs  │    │ Selection│
└──────────┘    └──────────┘    └──────────┘    └─────────┘    └──────────┘
    ^
    |
Step 1: Gender, Age, Weight, Height
- Validasi: Age 18-100, Height 100-300, Weight > 0
- Real-time: BMI calculation

Step 2: Activity Level
- 3 pilihan: Sedentary (1.545), Moderate (1.845), Vigorous (2.2)
- Real-time: TDEE calculation

Step 3: Diseases (1-3 kondisi)
- Pilihan: Normal, DM2, Hypertension, CVD, Cholesterol, CKD
- Multi-select dengan max 3
- "Normal" exclusive mode

Step 4: Food Preferences (0-3 pilihan)
- Pilihan: Western, Asian, Mediterranean
- Optional (kosong = all)
- Multi-select

Step 5: Algorithm Selection
- Pilihan: Greedy (available), Genetic (coming soon)
- Default: Greedy
```

### Step 6+: Analysis & Results (Backend → Frontend)

#### Endpoint 1: POST /api/analyze
```
FLOW:
User Form (Step 5) 
  ↓ submitForm()
  ↓ fetch('/api/analyze', POST)
  ↓
Flask: /api/analyze()
  ↓ Parse user_input
  ↓ Validate ranges (Age/Height/Weight)
  ↓ nutrition_service.calculate_nutrition_needs()
  ↓ Return: anthropometrics, energy, guidelines, meal_distribution
  ↓
Browser: analysisResult = data
  ↓ currentStep = 6
  ↓ Show 4 tabs: Profile | Nutrition | Menu | Constraints
```

**Input Format (JSON)**:
```json
{
  "gender": "M",
  "age": 30,
  "weight": 70.0,
  "height": 170.0,
  "activity": "1.845",
  "diseases": ["normal"],
  "food_preferences": []
}
```

**Output Format (JSON)**:
```json
{
  "success": true,
  "user_input": {...},
  "anthropometrics": {
    "bmi": 24.2,
    "bmi_category": "Normal",
    "bmi_color": "green",
    "bbi": 63.0,
    "age_group": {
      "group": "young_people",
      "label": "Young People",
      "range": "18-65 years"
    },
    ...
  },
  "energy": {
    "bmr": 1750,
    "tdee": 3228
  },
  "guidelines": {
    "nutrients": {
      "Energy": {"min": 2100, "max": 2100, "unit": "kkal"},
      "Carbohydrate": {"min": 1102.5, "max": 1367.1, "unit": "g"},
      "Protein": {"min": 75.6, "max": 181.5, "unit": "g"},
      "Total Fat": {"min": 52.8, "max": 79.3, "unit": "g"},
      ...27 nutrients total
    }
  },
  "meal_distribution": {
    "breakfast": 0.2375,
    "lunch": 0.3375,
    "snack": 0.1375,
    "dinner": 0.2875
  },
  "food_data": {
    "total_items": 1234
  }
}
```

#### Tab 1: Profile & Anthropometrics (Display)
Menampilkan:
- BMI card (data + kategori + color)
- Energy card (BMR + TDEE)
- Macro breakdown (Carbs/Protein/Fat dari TDEE)
- Conditions & Preferences summary

#### Tab 2: Nutrition Guidelines (Display)
Menampilkan:
- Filter: Semua / Makro / Mikro
- Grid nutrient cards
- Setiap card: nama, range, unit, description

#### Tab 3: Menu Generation (Interactive)
```
┌─────────────────────────────────────────────┐
│ GENERATE MENU PANEL (Gradient Blue)         │
│ "Click to generate menu using selected"      │
│  [Generate Menu] button                      │
└─────────────────────────────────────────────┘
         ↓ click "Generate Menu"
generateMenu()
  ↓ POST to /api/generate-menu with:
    {
      algorithm: "greedy",
      user_profile: {gender, age, weight, height, activity, diseases, food_preferences},
      analysis_data: {energy, guidelines, food_data},
      user_input: {...}
    }
  ↓
Flask: /api/generate-menu()
  ↓ greedy_algorithm.initialize(food_db, guidelines)
  ↓ greedy_algorithm.generate_menu_plan(user_profile, meal_distribution, tdee)
  ↓ Return: MenuPlan object as dict
  ↓
Browser: menuResult = data.menu_plan
  ↓ Display 4 meals: Breakfast, Lunch, Dinner, Snack
  ↓ Each meal shows:
    - Items (name, serving_size, calories, macros, score)
    - Total calories + percentage of TDEE
    - Click item → show details modal
  ↓ Action buttons: Regenerate, Download JSON, Print, Save, Share
```

**Input Format**:
```json
{
  "algorithm": "greedy",
  "user_profile": {
    "gender": "M",
    "age": 30,
    ...
  },
  "analysis_data": { ...from /api/analyze response... },
  "user_input": { ...same as user_profile... }
}
```

**Output Format (MenuPlan as JSON)**:
```json
{
  "success": true,
  "menu_plan": {
    "algorithm_used": "Greedy",
    "total_calories": 2150,
    "breakfast": {
      "total_calories": 512,
      "items": [
        {
          "name": "Oatmeal dengan Banana",
          "serving_size": 200,
          "calories": 256,
          "macros": {"carbs": 45, "protein": 8, "fat": 3},
          "score": 87.5,
          "main_ingredients": ["oats", "banana"],
          "food_category": "Cereals"
        },
        ...
      ],
      "macros": {"carbs": 72, "protein": 12, "fat": 6}
    },
    "lunch": {...},
    "dinner": {...},
    "snack": {...}
  }
}
```

#### Tab 3: Menu Display
```
Meal Card Structure:
┌──────────────────────────────────────┐
│ BREAKFAST          512 kkal | 23.8%  │ (gradient header)
├──────────────────────────────────────┤
│ ☐ Item 1 Name                [Score] │
│   100g | 150 kkal | [ingredients]    │
│                                      │
│ ☐ Item 2 Name                [Score] │
│   150g | 200 kkal | [ingredients]    │
├──────────────────────────────────────┤
│ Carbs: 45g | Protein: 12g | Fat: 6g  │
└──────────────────────────────────────┘

Features:
- Click item → show details modal
- Hover → highlight row
- Macros footer
- 4 meals total (breakfast, lunch, dinner, snack)
```

#### Tab 4: Constraint Compliance
```
Constraint Cards Structure:
┌──────────────────────────────────────────────┐
│ ✓ Calorie Target (Green if compliant)       │
│ Current: 2150 kkal vs Target: 2100 kkal    │
│ [████████░░] 102%                          │
│                                             │
│ ✗ Nutrient Profile (Red if violated)       │
│ Carbs: 250g/270g  [████░]                  │
│ Protein: 85g/100g [███░░]                  │
└──────────────────────────────────────────────┘
```

#### Item Details Modal
```
┌─────────────────────────────────────────────┐
│ ITEM NAME                              [X]  │
├─────────────────────────────────────────────┤
│ Porsi: 100g | Kalori: 250 kkal             │
│ Score: 87.5/100 | Category: Vegetable      │
├─────────────────────────────────────────────┤
│ MAKRONUTRIEN                                │
│ Carbs: 45g | Protein: 8g | Fat: 3g        │
├─────────────────────────────────────────────┤
│ MIKRONUTRIEN (Top 10)                      │
│ Vitamin A: 1200 IU | Vitamin C: 45 mg      │
│ Calcium: 150 mg | Iron: 8 mg               │
├─────────────────────────────────────────────┤
│ BAHAN UTAMA                                 │
│ [✓ oats] [✓ banana] [✓ milk]              │
├─────────────────────────────────────────────┤
│ STATUS HALAL: Halal ✓                       │
├─────────────────────────────────────────────┤
│              [Close]                        │
└─────────────────────────────────────────────┘
```

---

## 📝 Frontend Implementation Details

### Alpine.js Data Model
```javascript
nutritionApp() {
  return {
    // State
    currentStep: 1,              // 1-5: form, 6+: results
    activeTab: 'profile',        // profile|nutrition|menu|constraints
    isLoading: false,
    showItemDetailsModal: false,
    
    // Form Data
    formData: {
      gender: 'M',
      age: 30,
      weight: 70,
      height: 170,
      activity: '1.845',
      diseases: ['normal'],
      food_preferences: [],
      algorithm: 'greedy'
    },
    
    // Results
    analysisResult: null,        // dari /api/analyze
    menuResult: null,            // dari /api/generate-menu
    
    // Methods
    submitForm(),                // POST /api/analyze
    generateMenu(),              // POST /api/generate-menu
    regenerateMenu(),            // call generateMenu() lagi
    
    // Calculations (real-time)
    calculateBMI(),              // frontend calc
    calculateBBR(),
    calculateBMR(),
    calculateTDEE(),
    calculateMacro(type),
    
    // Utilities
    toggleDisease(disease),
    toggleFoodPreference(pref),
    getNutrientList(),           // filter berdasarkan nutrientFilter
    showNotification(msg, type)  // toast notification
  }
}
```

### Form Validation Rules

**Step 1 - Profile**:
- Age: 18-100 ✓
- Height: 100-300 cm ✓
- Weight: > 0 kg ✓
- All fields required ✓

**Step 2 - Activity**:
- Must select one: 1.545 | 1.845 | 2.2 ✓

**Step 3 - Diseases**:
- Minimum 1 selected
- Maximum 3 selected
- "Normal" is exclusive
- Multiple disease constraints merged (most restrictive) ✓

**Step 4 - Food Preferences**:
- 0-3 selections
- Empty = all cuisines ✓

**Step 5 - Algorithm**:
- Default: Greedy
- Genetic: disabled (coming soon) ✓

### Real-time Calculations (Frontend)

**BMI** (updated on weight/height change):
```javascript
const h = formData.height / 100;
bmi = formData.weight / (h * h);

// Category
if (bmi < 18.5) return "Underweight"
else if (bmi < 25) return "Normal"
else if (bmi < 30) return "Overweight"
else return "Obesitas"
```

**TDEE** (updated on activity change):
```javascript
bmr = 88.362 + 13.397*weight + 4.799*height - 5.677*age (M)
tdee = bmr * activity_factor

// Displayed in Tab 2 Energy card as estimate
// Actual calculation done in backend
```

**Macronutrients** (from disease constraints):
```javascript
// Get range for each disease
ranges = merge_disease_constraints(diseases)

// Calculate from TDEE
carbs_g = (tdee * carbs_percent) / 4
protein_g = (tdee * protein_percent) / 4
fat_g = (tdee * fat_percent) / 9
```

---

## 🖥️ Backend Implementation Details

### Flask app_integrated.py

**Structure**:
```
app_integrated.py
├── IMPORTS & INITIALIZATION
│   ├── NutritionService (C. System Flow)
│   ├── GreedyAlgorithmInterface (D. Model)
│   └── init_services() - lazy load on first request
│
├── LEGACY HELPERS (backward compatible)
│   ├── calculate_bmi()
│   ├── calculate_bbr()
│   ├── calculate_bmr()
│   ├── calculate_tdee()
│   └── classify_age_group()
│
├── CONSTANTS
│   ├── DISEASE_LABELS
│   ├── DISEASE_MACROS
│   ├── ACTIVITY_LABELS
│   └── FOOD_PREFERENCES_LABELS
│
├── ROUTES: STATIC
│   ├── / → landing.html
│   ├── /app → index_comprehensive.html
│   ├── /manifest.json
│   └── /sw.js
│
└── ROUTES: API
    ├── POST /api/analyze
    ├── POST /api/generate-menu
    ├── POST /api/refresh-menu
    └── GET /api/health-check
```

### Endpoint 1: POST /api/analyze

**Purpose**: Analyze user profile & calculate nutrition needs

**Validation**:
```python
# Age range
if not 18 <= age <= 100:
    return error("Age must be 18-100")

# Height range  
if not 100 <= height <= 300:
    return error("Height must be 100-300 cm")

# Weight positive
if weight <= 0:
    return error("Weight must be positive")
```

**Flow**:
```python
1. init_services() → load NutritionService
2. Parse request JSON
3. Create user_input dict
4. Call nutrition_service.calculate_nutrition_needs(user_input)
5. Check result.success
6. Add meal_distribution (hardcoded: 23.75%, 33.75%, 13.75%, 28.75%)
7. Return result as JSON
```

**Error Handling**:
```python
try:
    ...
except Exception as e:
    return jsonify({
        "success": False,
        "error": str(e)
    }), 500
```

### Endpoint 2: POST /api/generate-menu

**Purpose**: Generate meal menu using Greedy Algorithm

**Input Validation**:
```python
# Check algorithm choice
if algorithm not in ['greedy', 'genetic']:
    return error("Unknown algorithm")

# Must have come from /api/analyze first
if not analysis_data or not food_database:
    return error("Missing analysis data")
```

**Flow**:
```python
1. init_services() → load GreedyAlgorithmInterface
2. Extract analysis_data & user_input
3. Get TDEE from analysis_data['energy']['tdee']
4. Get food database from analysis_data['food_data']['dataframe']
5. Get nutrition_guidelines from analysis_data['guidelines']
6. Call greedy_algorithm.initialize(food_database, guidelines)
7. Call greedy_algorithm.generate_menu_plan(
     user_profile,
     meal_distribution,
     user_tdee
   )
8. Convert MenuPlan object to dict
9. Return as JSON
```

**Error Handling**:
- Missing database → return error
- Initialize fails → return error  
- Menu generation fails → return error
- Insufficient candidates → return error

---

## 🔗 Integration Points & Dependencies

### File Dependencies

```
F. WebApp/
├── app_integrated.py (MODIFIED)
│   ├── imports → C. System Flow/nutrition_service.py
│   ├── imports → D. Model/Greedy Algorithm/greedy_interface.py
│   ├── imports → D. Model/candidate_generator.py (via Greedy)
│   ├── imports → D. Model/similarity_checker.py (via Greedy)
│   ├── serves → templates/index_comprehensive.html
│   └── serves → static/ (CSS, JS)
│
└── templates/
    └── index_comprehensive.html (NEW)
        ├── Alpine.js (frontend logic)
        ├── Tailwind CSS (styling)
        ├── Chart.js (visualization - future)
        └── calls → /api/analyze
            └── calls → /api/generate-menu

C. System Flow/
├── nutrition_service.py (used by app_integrated.py)
│   ├── imports → modules/calculations.py
│   ├── imports → modules/guidelines.py
│   ├── imports → A. Data/Processed/final_dataset.csv
│   └── imports → A. Data/Raw/guideline.csv
│
└── modules/
    ├── calculations.py (BMI, BBR, BMR, TDEE)
    ├── guidelines.py (load & manage guidelines)
    └── input_handler.py (validation)

D. Model/
├── Greedy Algorithm/
│   ├── greedy_interface.py (used by app_integrated.py)
│   ├── greedy_optimizer.py (core algorithm)
│   ├── imports → ../candidate_generator.py
│   ├── imports → ../similarity_checker.py
│   └── imports → ../meal_schema.py
│
├── candidate_generator.py (REFACTORED)
│   ├── imports → ../food_categorizer.py
│   └── imports → ../similarity_checker.py
│
└── similarity_checker.py
    └── ingredient diversity checking
```

---

## 🚀 How to Run

### 1. Start Flask Backend
```bash
cd "F. WebApp"
python app_integrated.py
# Output:
# ✓ NutritionService imported successfully
# ✓ NutritionService initialized
# ✓ GreedyAlgorithmInterface imported successfully
# ✓ GreedyAlgorithmInterface initialized
# * Running on http://127.0.0.1:5000
```

### 2. Open Browser
```
http://localhost:5000/app
```

### 3. Complete User Flow
1. Fill Form (5 steps)
2. Click "Analisis Profile" → calls `/api/analyze`
3. View Results Tabs
4. Click "Generate Menu" → calls `/api/generate-menu`
5. View Menu with 10 meal slots
6. Click item → see details modal
7. Download/Save/Share menu

---

## 🔧 File Mapping

| File | Purpose | Status | Created/Modified |
|------|---------|--------|-----------------|
| `app_integrated.py` | Flask app dengan 3 endpoints | ✅ Ready | NEW |
| `index_comprehensive.html` | Frontend dengan 5-step form + results | ✅ Ready | NEW |
| `nutrition_service.py` | System Flow orchestrator | ✅ Ready | Existing |
| `greedy_interface.py` | Algorithm wrapper | ✅ Ready | Existing |
| `candidate_generator.py` | Ingredient diversity | ✅ Refactored | Modified |

---

## ⚠️ Known Limitations & TODOs

### Current (MVP)
- ✅ Form input validation (18-100 age, 100-300 height)
- ✅ Activity factor (3 levels: 1.545, 1.845, 2.2)
- ✅ Disease selection (1-3, "Normal" exclusive)
- ✅ Greedy Algorithm integration
- ✅ Menu display (4 meals, 10 slots total)
- ✅ Item details modal
- ✅ Constraint display

### Phase 2 (Polish)
- ⏳ Alternative item suggestions (click to swap)
- ⏳ Constraint report details
- ⏳ PDF/JSON/PNG download functionality
- ⏳ Print-friendly layout
- ⏳ Local storage persistence
- ⏳ User profiles (save history)

### Phase 3+ (Advanced)
- ⏳ Genetic Algorithm integration
- ⏳ Chart.js visualizations (macros, timeline)
- ⏳ Shopping list generator
- ⏳ Meal prep instructions
- ⏳ Calorie counter app integration
- ⏳ User authentication
- ⏳ Database persistence (not localStorage)

---

## 📊 Testing Checklist

### Frontend Tests
- [ ] Form validation on each step
- [ ] Real-time BMI/TDEE calculation
- [ ] Multi-disease logic (merger constraints)
- [ ] Food preferences display
- [ ] Navigation between steps
- [ ] Error messages on invalid input

### Backend Tests
- [ ] `/api/analyze` with valid input
- [ ] `/api/analyze` with invalid age/height
- [ ] `/api/generate-menu` after analyze
- [ ] `/api/generate-menu` without analyze (error case)
- [ ] Health check endpoint
- [ ] NutritionService initialization
- [ ] Greedy Algorithm initialization

### Integration Tests
- [ ] Complete user journey (form → analyze → menu)
- [ ] Menu display accuracy
- [ ] Calorie calculation correctness
- [ ] Constraint compliance reporting
- [ ] Error handling end-to-end

---

## 💡 Debug Tips

### Check Logs
```bash
# Flask logs
# Look for "✓" and "❌" initialization messages
# Look for request logs: POST /api/analyze
```

### Inspect Network
```javascript
// Browser DevTools → Network tab
// Click /api/analyze → check Response
// Look for "success": true/false
```

### Check Console
```javascript
// Browser DevTools → Console tab
// Check for JavaScript errors
// Check Alpine.js state: console.log(document.__x)
```

### Test Endpoints Manually
```bash
# Test /api/health-check
curl http://localhost:5000/api/health-check

# Test /api/analyze
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "gender": "M",
    "age": 30,
    "weight": 70,
    "height": 170,
    "activity": "1.845",
    "diseases": ["normal"],
    "food_preferences": []
  }'
```

---

## 📚 Related Files

- [NutritionService Docs](../C.%20System%20Flow/INTEGRATION_GUIDE.md)
- [Greedy Algorithm Docs](../D.%20Model/Greedy%20Algorithm/README.md)
- [Candidate Generator](../D.%20Model/candidate_generator.py)

---

**Last Updated**: Now  
**Version**: 1.0 - MVP Complete Integration  
**Status**: Ready for Testing


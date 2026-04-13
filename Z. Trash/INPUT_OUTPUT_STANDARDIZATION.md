# GA INPUT/OUTPUT STANDARDIZATION GUIDE
## Version 2: Aligned with input_handler.py Specifications

---

## 📋 RINGKASAN PERUBAHAN

### **Old Version** (`run_ga_with_input.py`)
- Activity factor: 1.4, 1.55, 1.725, 1.9 (non-standard)
- Food preferences tidak ditampilkan (hardcoded)
- Output sangat singkat (hanya menu + fitness score)

### **New Version** (`run_ga_with_input_v2.py`)
- ✅ Activity factor: 1.545, 1.845, 2.2 (sesuai FAO/WHO/UNU spec)
- ✅ Health conditions: Multi-select dengan validation
- ✅ Food preferences: Multi-select dengan validation
- ✅ 2-phase output: Nutrition summary + GA menu

---

## 🔧 INPUT STANDARDIZATION

### Activity Factor (Sedentary, Active, Vigorous)

| Level | PAL Value | Description |
|-------|-----------|-------------|
| 1     | 1.545     | Sedentary/Light (office worker, jarang olahraga) |
| 2     | 1.845     | Active/Moderately (konstruksi, rutin jogging) |
| 3     | 2.2       | Vigorous/Vigorously (atlet, intense sports) |

**Sumber:** FAO/WHO/UNU Guidelines (International standard)

---

### Health Conditions (Multi-Select)

User dapat memilih:
- **1 kondisi saja:** Contoh: `2` = DM2
- **Multiple (max 3):** Contoh: `2,3,5` = DM2 + Hypertension + Cholesterol
- **Special:** `1` = Normal (tidak bisa combine dengan kondisi lain)

**Opsi yang tersedia:**
```
1. Normal
2. Diabetes Type 2 (DM2)
3. Hypertension
4. Cardiovascular Disease (CVD)
5. High Cholesterol
6. Chronic Kidney Disease (CKD)
```

**Validation:**
```
❌ INVALID: Input "1,2" → "Normal" tidak bisa combine dengan DM2
✅ VALID:  Input "2,3,4" → DM2 + Hypertension + CVD (3 kondisi)
✅ VALID:  Input "1" → Normal (hanya 1)
❌ INVALID: Input "2,3,4,5" → Lebih dari 3 kondisi
```

---

### Food Preferences (Optional Multi-Select)

User dapat memilih:
- **Kosong (Enter saja):** Semua cuisines included
- **Single:** Contoh: `2` = Western saja
- **Multiple:** Contoh: `1,2` = Asian + Western

**Opsi yang tersedia:**
```
1. Asian
2. Western
3. Mediterranean
```

**Behavior:**
```
User input: "2" → Filter ke 2005 Western foods
User input: "1,3" → Filter ke Asian + Mediterranean foods
User input: "" (blank) → Semua ~3920 foods included
```

---

## 📊 OUTPUT FORMAT (2-PHASE)

### **PHASE 1: Nutrition Profile Summary**

Ditampilkan SEBELUM GA optimization dimulai.

```
================================================================================
NUTRITION PROFILE SUMMARY
================================================================================

[ANTHROPOMETRIC MEASUREMENTS]
────────────────────────────────────────────────────────────────────────────────
Body Mass Index (BMI): 22.9 kg/m²
  Classification: Normal weight (18.5–24.9)
Ideal Body Weight (IBW): 52.9 kg

[ENERGY REQUIREMENTS]
────────────────────────────────────────────────────────────────────────────────
Basal Metabolic Rate (BMR): 1268 kcal/day
Total Daily Energy Expenditure (TDEE): 2339 kcal/day
  (Based on activity level: 1.845 PAL)

[DEMOGRAPHIC & HEALTH PROFILE]
────────────────────────────────────────────────────────────────────────────────
Age Group: 18-65 years old
Health Condition(s): DM2
Cuisine Preference(s): Western

[NUTRITION GUIDELINES]
────────────────────────────────────────────────────────────────────────────────
Total Nutrients Evaluated: 31
  Includes macronutrients and micronutrients based on health conditions

================================================================================
```

**Informasi yang ditampilkan:**
- BMI dengan classification (Underweight, Normal, Overweight, Obesity I/II/III)
- Ideal Body Weight (IBW)
- Basal Metabolic Rate (BMR)
- Total Daily Energy Expenditure (TDEE) + PAL factor
- Age group classification
- Health conditions yang dipilih
- Food preferences yang dipilih
- Jumlah nutrient guidelines yang akan dievaluasi

---

### **PHASE 2: Personalized Menu Recommendations**

Ditampilkan SETELAH GA optimization selesai.

#### **Format per Meal:**

```
BREAKFAST
Total Energy: 650 kcal
Macros: Protein 18.2g | Carbs 85.5g | Fat 15.3g

  MAIN COURSE OPTIONS:
    [1] Scrambled Eggs with Whole Wheat Toast (280g, 520 kcal)
    [2] Oatmeal with Berries and Almonds (250g, 485 kcal)
    [3] Whole Grain Pancakes with Honey (300g, 510 kcal)

  SIDE DISH OPTIONS:
    [1] Fresh Orange Juice (250ml, 110 kcal)
    [2] Fruit Salad (200g, 95 kcal)
    [3] Yogurt with Granola (150g, 185 kcal)

  DRINK OPTIONS (Optional):
    [1] Green Tea (250ml, 2 kcal)
    [2] Coffee with Milk (200ml, 45 kcal)
    [3] Fresh Lemon Water (250ml, 10 kcal)

LUNCH
Total Energy: 850 kcal
Macros: Protein 35.8g | Carbs 95.2g | Fat 20.5g
... (same format)

DINNER
Total Energy: 720 kcal
... (same format)

SNACK/DESSERT
Total Energy: 119 kcal
... (options)
```

**Struktur:**
- **MAIN COURSE OPTIONS:** 3 pilihan (user harus pilih 1)
- **SIDE DISH OPTIONS:** 3 pilihan (user harus pilih 1)
- **DRINK OPTIONS:** 3 pilihan (user dapat pilih atau skip - OPTIONAL)
- Total 3 meals × 3 courses = 9 potential main items + 9 sides + 9 drinks

**User dapat:**
- Pilih main course 1 + side dish 2 + drink 3 → kombinasi untuk breakfast
- Atau pilih main 1 + side 1 + no drink → breakfast tanpa minuman
- Atau pilih main 2 + side 3 + drink 1 → kombinasi lain

---

#### **Evaluation Metrics:**

```
[EVALUATION METRICS]
────────────────────────────────────────────────────────────────────────────────

Daily Energy Balance:
  Recommended TDEE: 2339 kcal
  Menu Total:       2190 kcal
  Difference:       -149 kcal (-6.4%)

Genetic Algorithm Fitness Score: 52.45 / 100
Quality Rating: FAIR
```

**Metrik yang ditampilkan:**
- Recommended TDEE
- Menu total (sum dari semua meals)
- Difference & percentage deviation
- GA fitness score (0-100)
- Quality rating (EXCELLENT: >75, GOOD: 60-75, FAIR: 45-60, NEEDS IMPROVEMENT: <45)

---

#### **Important Notes:**

```
[IMPORTANT NOTES]
────────────────────────────────────────────────────────────────────────────────

[OK] EVALUATED:
  • Menu composition from food database
  • Nutritional compliance to 31 guidelines
  • Energy coverage vs TDEE target
  • Macronutrient balance

[FUTURE] NOT YET IMPLEMENTED:
  • Cost analysis & budget feasibility
  • Preparation time & difficulty
  • Detailed micronutrient analysis

[DISCLAIMER]
  • This is a RECOMMENDATION from optimization algorithm
  • NOT a medical prescription or diagnosis
  • Consult a nutritionist for medical needs
  • Use as guidance for meal planning
```

---

## 🎯 COMPARISON: OLD vs NEW

### Input Phase

| Aspek | Old | New |
|-------|-----|-----|
| Activity values | 1.4, 1.55, 1.725, 1.9 | 1.545, 1.845, 2.2 ✅ |
| Health conditions | Hardcoded input | Multi-select ✅ |
| Food preferences | Not shown | Multi-select ✅ |
| Input validation | Basic | Comprehensive ✅ |

### Output Phase

| Aspek | Old | New |
|-------|-----|-----|
| Pre-GA summary | No | Yes ✅ |
| Nutrition details | No | BMI, IBW, TDEE ✅ |
| Menu format | List with slots | Organized per category ✅ |
| Food options | Few | Multiple alternatives ✅ |
| Evaluation | Basic | Comprehensive ✅ |
| Transparency | Medium | High ✅ |

---

## 📝 TECHNICAL NOTES

### Files
- **Old:** `run_ga_with_input.py` (deprecated)
- **New:** `run_ga_with_input_v2.py` (RECOMMENDED)

### Dependencies
- Same as before: `ga_interface.py`, `nutrition_service.py`, `ga_output_formatter.py`
- No new libraries required

### Flow
```
run_ga_with_input_v2.py
├── get_user_input()          ← Standardized input
│   ├── Gender validation
│   ├── Anthropometric input (age, weight, height)
│   ├── Activity level (1.545, 1.845, 2.2)
│   ├── Health conditions (multi-select with validation)
│   └── Food preferences (multi-select optional)
│
├── NutritionService.calculate_nutrition_needs()
│   └── Returns: BMI, IBW, BMR, TDEE, guidelines
│
├── display_nutrition_summary()  ← PHASE 1 OUTPUT
│
├── GeneticAlgorithmInterface.generate_menu_plan()
│   └── GA optimization loop
│
└── display_ga_results()         ← PHASE 2 OUTPUT
    ├── Meals with category-based options
    ├── Evaluation metrics
    └── Important disclaimers
```

---

## 🚀 USAGE

```bash
cd "C:\Users\Silfia\Documents\FILE TA\TugasAkhirDSS\D. Model\Genetic Algorithm"
python run_ga_with_input_v2.py
```

**Input Example:**
```
Gender (M/F): F
Age (years, 18-100): 25
Weight (kg): 60
Height (cm, 100-300): 165

Activity Level: 2 (PAL 1.845)

Health Conditions:
Select conditions (e.g., '2,3' or '1'): 2,3
[OK] Selected: ['dm2', 'hypertension']

Food Preferences:
Select preferences (leave blank for all): 1,2
[OK] Selected: ['Asian', 'Western']

→ GA optimization starts...
→ Menu recommendations displayed
```

---

## ✅ VALIDATION CHECKLIST

### Input Validation
- [x] Gender: M or F only
- [x] Age: 18-100 years
- [x] Weight: Positive number
- [x] Height: 100-300 cm
- [x] Activity: 1, 2, or 3 only
- [x] Health conditions: Valid selection + max 3 + no "Normal" mixing
- [x] Food preferences: Valid selection or empty + max 3

### Output Display
- [x] Nutrition summary before GA
- [x] BMI with proper classification
- [x] IBW, BMR, TDEE values
- [x] GA menu with main/side/drink categories
- [x] Multiple options per food category
- [x] Evaluation metrics
- [x] Important disclaimers

---

## 💡 FOR TA PRESENTATION

**Your talking points:**
1. Input validation matches professional nutrition standards (FAO/WHO/UNU)
2. 2-phase output gives clear separation between profile & recommendations
3. Multiple food options per meal slot provides flexibility
4. Comprehensive evaluation metrics show system capability
5. Disclaimers ensure academic integrity & responsible AI use


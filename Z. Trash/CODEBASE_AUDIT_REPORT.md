# Comprehensive Codebase Audit Report
**Project**: NutriPlan DSS - Nutrition Decision Support System  
**Date**: April 12, 2026  
**Scope**: A-F Folders (Excluding Z. Trash)

---

## Executive Summary

This DSS system has **3 main entry points** and follows a modular architecture:
1. **CLI Entry Point**: `C. System Flow/main.py` (nutrition calculation + system flow)
2. **Web Entry Point**: `F. WebApp/app.py` (Flask web interface)
3. **Preprocessing**: `B. Preprocessing/` (data preparation & ML)

The system is designed to:
- Calculate user nutrition needs based on anthropometrics and disease conditions
- Generate meal recommendations using genetic/greedy algorithms
- Provide web-based interface for user interaction

**Key Finding**: Most core files are **actively used**. There are minimal unused files, but some exploratory/analysis scripts lack clear integration points.

---

## 1. PYTHON FILE INVENTORY (A-F Folders Only)

### Total: 31 Active Python Files

#### A. Data (0 files)
No Python files - contains only CSV data files.

#### B. Preprocessing (6 files + 2 in subdirectory)
```
01_join_usda.py
02_pivot_nutrients.py
03_clean_dataset.py
04_analyze_constraints.py
05_final_dataset.py

ML Klasifikasi/
├── __init__.py
├── food_classifier.py
```

#### C. System Flow (7 files + 5 in modules/)
```
main.py                           ← ACTIVE ENTRY POINT (CLI)
nutrition_service.py              ← ACTIVE SERVICE LAYER
data_loader.py                    ← ACTIVE DATA LOADER

modules/
├── __init__.py
├── input_handler.py              ← ACTIVE (used by main.py)
├── output_formatter.py           ← ACTIVE (used by main.py)
├── calculations.py               ← ACTIVE (used by nutrition_service.py)
├── guidelines.py                 ← PRESENT (unclear direct usage)
```

#### D. Model (8 files)
```
candidate_generator.py            ← ACTIVE ALGORITHM COMPONENT
food_categorizer.py               ← ACTIVE (used by candidate_generator)
meal_schema.py                    ← ACTIVE DATA STRUCTURES
similarity_checker.py             ← ACTIVE ALGORITHM COMPONENT

Genetic Algorithm/
├── step1_load_data.py            ← EXPLORATION/REFERENCE
├── step2_prepare_guidelines.py   ← EXPLORATION/REFERENCE
├── step3_user_nutrition_needs.py ← EXPLORATION/REFERENCE (used by step4)
├── step4_prepare_food_candidates.py ← EXPLORATION/REFERENCE

Greedy Algorithm/                 ← EMPTY (no files)

File/ (directory exists, purpose unclear)
```

#### E. Evaluation (1 file)
```
evaluation.py                     ← EMPTY FILE
```

#### F. WebApp (2 files + assets)
```
app.py                            ← ACTIVE ENTRY POINT (FLASK)
start.py                          ← ACTIVE LAUNCHER SCRIPT

static/
├── manifest.json
├── css/
├── js/

templates/
├── index.html
├── landing.html
```

#### Root Level (3 files)
```
compare_formats.py                ← ANALYSIS/EXPLORATION SCRIPT
finalize_micronutrient_guidelines.py ← DATA PROCESSING SCRIPT
```

---

## 2. ACTIVE FILES (In Active Use)

### **SYSTEM FLOW - Main Application**

| File | Purpose | Used By | Status |
|------|---------|---------|--------|
| `C. System Flow/main.py` | CLI entry point for nutrition calculation | Direct entry point | ✅ ACTIVE |
| `C. System Flow/nutrition_service.py` | Orchestrates nutrition calculations & data | main.py | ✅ ACTIVE |
| `C. System Flow/data_loader.py` | Loads guideline & food data from CSV | nutrition_service.py | ✅ ACTIVE |
| `C. System Flow/modules/input_handler.py` | Gets user input (CLI) | main.py | ✅ ACTIVE |
| `C. System Flow/modules/output_formatter.py` | Formats output display | main.py | ✅ ACTIVE |
| `C. System Flow/modules/calculations.py` | BMI, BBI, BMR, TDEE calculations | nutrition_service.py | ✅ ACTIVE |

### **ALGORITHM MODEL - Decision Logic**

| File | Purpose | Used By | Status |
|------|---------|---------|--------|
| `D. Model/meal_schema.py` | Data structures: FoodItem, Meal, MealCourse | candidate_generator.py, similarity_checker.py | ✅ ACTIVE |
| `D. Model/candidate_generator.py` | Generate 3 candidates per meal slot with similarity check | Algorithms (genetic/greedy) | ✅ ACTIVE |
| `D. Model/food_categorizer.py` | Map foods to meal categories (Main/Side/Drink) | candidate_generator.py | ✅ ACTIVE |
| `D. Model/similarity_checker.py` | Detect duplicates/similar items across menu | Algorithms (genetic/greedy) | ✅ ACTIVE |

### **WEB APPLICATION**

| File | Purpose | Used By | Status |
|------|---------|---------|--------|
| `F. WebApp/app.py` | Flask web interface with routes | Direct entry point or start.py | ✅ ACTIVE |
| `F. WebApp/start.py` | Quick start launcher script | Direct entry point | ✅ ACTIVE |

### **DATA PREPROCESSING**

| File | Purpose | Used By | Status |
|------|---------|---------|--------|
| `B. Preprocessing/05_final_dataset.py` | Apply ML classification to finalize dataset | One-time data pipeline | ✅ ACTIVE |
| `B. Preprocessing/ML Klasifikasi/food_classifier.py` | ML model for food consumption/cuisine labels | 05_final_dataset.py | ✅ ACTIVE |
| `B. Preprocessing/01_join_usda.py` | Join USDA data | Data pipeline | ✅ ACTIVE |
| `B. Preprocessing/02_pivot_nutrients.py` | Pivot nutrient columns | Data pipeline | ✅ ACTIVE |
| `B. Preprocessing/03_clean_dataset.py` | Clean & normalize dataset | Data pipeline | ✅ ACTIVE |
| `B. Preprocessing/04_analyze_constraints.py` | Analyze constraint coverage | Data analysis | ✅ ACTIVE |

### **SUPPORTING/UTILITY SCRIPTS**

| File | Purpose | Used By | Status |
|------|---------|---------|--------|
| `finalize_micronutrient_guidelines.py` | Finalize micronutrient guideline CSV | One-time setup | ✅ ACTIVE |
| `compare_formats.py` | Compare wide vs long format for guidelines | Development/analysis | ✅ ACTIVE |

---

## 3. POTENTIALLY UNUSED OR ORPHANED FILES

### **UNCLEAR USAGE**

| File | Issue | Details |
|------|-------|---------|
| `C. System Flow/modules/guidelines.py` | Orphaned module | Imports defined but no visible usage in main execution flow. Contains `GuidelineProcessor` class that's not imported elsewhere. |
| `E. Evaluation/evaluation.py` | Empty file | File exists but contains no code. Purpose unclear. |
| `D. Model/Genetic Algorithm/step*.py` (4 files) | Exploration/Reference Only | These are step-by-step scripts for understanding GA workflow, but appear to be **development/learning files** not integrated into main system. Only `step3` is referenced by `step4`. No integration with main application. |
| `D. Model/Greedy Algorithm/` | Empty directory | Directory exists but contains no files. |
| `D. Model/File/` | Empty directory | Directory exists but purpose unclear. |

### **UNCERTAIN STATUS**

- **D. Model/Genetic Algorithm/** folder: Intended for genetic algorithm implementation, but appears to be **exploratory/prototyping** code, not integrated into the production flow. The files load data and prepare guidelines but don't connect to `main.py` or `app.py`.

---

## 4. FILE DEPENDENCY GRAPH

```
┌─────────────────────────────────────────────────────────────────┐
│                      ENTRY POINTS                                │
├─────────────────────────────────────────────────────────────────┤
│  • main.py (CLI) → nutrition_system flow                         │
│  • app.py (Flask Web) → web interface                            │
│  • start.py → launcher for app.py                                │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              C. SYSTEM FLOW (Orchestration)                      │
├─────────────────────────────────────────────────────────────────┤
│  main.py
│    ├─→ modules/input_handler.py      [Get user input]
│    ├─→ modules/output_formatter.py   [Format output]
│    └─→ nutrition_service.py (Main orchestrator)
│            ├─→ modules/calculations.py    [BMI, TDEE, etc]
│            └─→ data_loader.py             [Load guidelines/food]
│                    ├─→ guideline.csv
│                    ├─→ dri_micro.csv
│                    └─→ 05_final_dataset.csv
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│            D. MODEL (Algorithm Components Ready)                 │
├─────────────────────────────────────────────────────────────────┤
│  candidate_generator.py
│    ├─→ meal_schema.py           [Data structures]
│    └─→ food_categorizer.py      [Categorize foods]
│
│  similarity_checker.py
│    └─→ meal_schema.py           [Data structures]
│
│  Note: GA/Greedy algorithms will use these components
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│            B. PREPROCESSING (One-time/Setup)                     │
├─────────────────────────────────────────────────────────────────┤
│  05_final_dataset.py
│    └─→ ML Klasifikasi/food_classifier.py [ML classification]
│
│  01_join_usda.py, 02_pivot_nutrients.py, 03_clean_dataset.py
│    └─→ Sequential data pipeline
│
│  04_analyze_constraints.py  [Analysis only]
│
│  finalize_micronutrient_guidelines.py  [Guideline setup]
│  compare_formats.py  [Format comparison analysis]
└─────────────────────────────────────────────────────────────────┘

EXPLORATION CODE (Not integrated):
┌─────────────────────────────────────────────────────────────────┐
│  D. Model/Genetic Algorithm/step*.py
│    └─→ Development/learning files (isolated from main flow)
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. ANALYSIS BY COMPONENT

### A. DATA LAYER (`A. Data/`)
- **Status**: All CSV files, no Python files
- **Purpose**: Stores nutrition guidelines, food datasets, and raw data
- **Key Files**:
  - `Data Raw/guideline.csv` - Nutrition constraints for diseases
  - `Data Raw/dri_micro.csv` - DRI micronutrient standards
  - `Data Processed/05_final_dataset.csv` - Main food dataset

### B. PREPROCESSING LAYER (`B. Preprocessing/`)
- **Status**: Active but mostly one-time scripts
- **Used For**: Initial data preparation and ML classification
- **Key Integration**: `05_final_dataset.py` → produces `05_final_dataset.csv` used by system
- **ML Component**: `food_classifier.py` trains/predicts food labels
- **When Used**: Setup phase, potentially re-run if data needs reprocessing

### C. SYSTEM FLOW LAYER (`C. System Flow/`)
- **Status**: Core active system
- **Main Entry**: `main.py` (CLI) - fully integrated
- **Orchestration**: `nutrition_service.py` - coordinates all calculations
- **Data Access**: `data_loader.py` - loads from A. Data/
- **I/O Handling**: `input_handler.py`, `output_formatter.py`
- **Calculation Engine**: `modules/calculations.py` - BMI, TDEE, nutrition math
- **Status**: ⚠️ **`guidelines.py` appears orphaned** - contains `GuidelineProcessor` but never called

### D. MODEL LAYER (`D. Model/`)
- **Status**: Core algorithm components ready
- **Core Components**:
  - `meal_schema.py` - Data contract (FoodItem, Meal, MealCourse, MenuPlan)
  - `candidate_generator.py` - Generates food candidates for each meal slot
  - `food_categorizer.py` - Maps foods to meal categories
  - `similarity_checker.py` - Detects menu diversity/duplicates
- **Status**: These are ready-to-use but not yet called by `main.py` or `app.py`
- **Exploration**: `Genetic Algorithm/` folder contains development scripts (not production-integrated)

### E. EVALUATION LAYER (`E. Evaluation/`)
- **Status**: Empty (`evaluation.py` has no code)
- **Purpose**: Intended for algorithm evaluation/validation
- **Action Needed**: Implementation pending

### F. WEB APPLICATION (`F. WebApp/`)
- **Status**: Active Flask web interface
- **Entry Points**: 
  - `app.py` - Main Flask application with routes
  - `start.py` - Launcher script
- **Status**: Functional but appears to use sample data (not integrated with `nutrition_service.py` yet)

---

## 6. ACTIVE VS UNUSED - SUMMARY TABLE

### DEFINITELY ACTIVE (10 files)
- ✅ `C. System Flow/main.py`
- ✅ `C. System Flow/nutrition_service.py`
- ✅ `C. System Flow/data_loader.py`
- ✅ `C. System Flow/modules/input_handler.py`
- ✅ `C. System Flow/modules/output_formatter.py`
- ✅ `C. System Flow/modules/calculations.py`
- ✅ `F. WebApp/app.py`
- ✅ `F. WebApp/start.py`
- ✅ `D. Model/meal_schema.py`
- ✅ `D. Model/candidate_generator.py`

### ACTIVELY USED IN PIPELINE (8 files)
- ✅ `D. Model/food_categorizer.py` (used by candidate_generator)
- ✅ `D. Model/similarity_checker.py` (algorithm component ready)
- ✅ `B. Preprocessing/05_final_dataset.py` (produces core data)
- ✅ `B. Preprocessing/ML Klasifikasi/food_classifier.py` (ML classification)
- ✅ `B. Preprocessing/01_join_usda.py` (data preparation)
- ✅ `B. Preprocessing/02_pivot_nutrients.py` (data preparation)
- ✅ `B. Preprocessing/03_clean_dataset.py` (data preparation)
- ✅ `finalize_micronutrient_guidelines.py` (setup/data generation)

### EXPLORATORY/DEVELOPMENT (5 files)
- 📊 `B. Preprocessing/04_analyze_constraints.py` (analysis only)
- 📊 `compare_formats.py` (format comparison analysis)
- 🔧 `D. Model/Genetic Algorithm/step1_load_data.py` (development)
- 🔧 `D. Model/Genetic Algorithm/step2_prepare_guidelines.py` (development)
- 🔧 `D. Model/Genetic Algorithm/step3_user_nutrition_needs.py` (development)
- 🔧 `D. Model/Genetic Algorithm/step4_prepare_food_candidates.py` (development)

### ORPHANED/UNCLEAR (3 files)
- ❓ `C. System Flow/modules/guidelines.py` (imported nowhere)
- ❓ `E. Evaluation/evaluation.py` (empty)
- ❌ `D. Model/Greedy Algorithm/` (empty directory)

---

## 7. WHICH FILES ARE NEEDED FOR EACH SYSTEM ASPECT

### **For CLI Nutrition Calculation System** ✅ COMPLETE
```
Required:
- C. System Flow/main.py (entry point)
- C. System Flow/nutrition_service.py (orchestration)
- C. System Flow/data_loader.py (data access)
- C. System Flow/modules/input_handler.py (user input)
- C. System Flow/modules/output_formatter.py (output display)
- C. System Flow/modules/calculations.py (nutrition math)
- A. Data/*.csv (nutrition data)
```

### **For Genetic/Greedy Algorithm** ⚠️ PARTIALLY READY
```
Ready Components:
- D. Model/meal_schema.py (data structures)
- D. Model/candidate_generator.py (food selection)
- D. Model/food_categorizer.py (food categorization)
- D. Model/similarity_checker.py (diversity checking)
- B. Preprocessing/05_final_dataset.csv (food data)

Missing/Needed:
- GA/Greedy algorithm implementations (not yet in D. Model/)
- Integration with nutrition_service.py (not yet done)
- Actual algorithm code (step files are exploration only)
```

### **For Web Application** ⚠️ PARTIALLY INTEGRATED
```
Ready:
- F. WebApp/app.py (Flask app with routes)
- F. WebApp/start.py (launcher)
- F. WebApp/templates/*.html
- F. WebApp/static/* (assets)

Needs Integration:
- Connection to C. System Flow/nutrition_service.py
- Backend algorithm integration
- Currently uses hardcoded sample data
```

### **For Data Pipeline** ✅ COMPLETE
```
Setup Phase:
- B. Preprocessing/01_join_usda.py
- B. Preprocessing/02_pivot_nutrients.py
- B. Preprocessing/03_clean_dataset.py
- B. Preprocessing/04_analyze_constraints.py (optional analysis)
- B. Preprocessing/ML Klasifikasi/food_classifier.py

Finalization:
- finalize_micronutrient_guidelines.py
```

---

## 8. RECOMMENDATIONS

### 🔴 **HIGH PRIORITY - REMOVE/CONSOLIDATE**

1. **`C. System Flow/modules/guidelines.py`**
   - **Status**: Orphaned module with unused `GuidelineProcessor`
   - **Action**: Either integrate into workflow or remove
   - **Impact**: Low - no systems depend on it

2. **`E. Evaluation/evaluation.py`**
   - **Status**: Empty file
   - **Action**: Either implement evaluation logic or delete
   - **Impact**: Low

### 🟡 **MEDIUM PRIORITY - CLARIFY/INTEGRATE**

3. **`D. Model/Genetic Algorithm/*.py` (step files)**
   - **Status**: Development/exploration code, not integrated
   - **Action**: Either:
     - Convert to production genetic algorithm implementation in `D. Model/`
     - Move to `Z. Trash/` if only reference material
   - **Impact**: Medium - blocks algorithm feature completion

4. **`D. Model/Greedy Algorithm/` (empty directory)**
   - **Status**: Placeholder directory, no files
   - **Action**: Either create greedy algorithm or remove directory
   - **Impact**: Medium - design placeholder

5. **`B. Preprocessing/04_analyze_constraints.py`**
   - **Status**: Analysis script, pure exploratory
   - **Action**: Clarify if this needs to be part of pipeline or move to analysis folder
   - **Impact**: Low - doesn't affect main flow

### 🟢 **LOW PRIORITY - NICE TO HAVE**

6. **`compare_formats.py`**
   - **Status**: Format comparison analysis
   - **Action**: Can stay as reference or move to documentation
   - **Impact**: None - purely informational

### ✅ **KEEP AS-IS**

- All B. Preprocessing files (active data pipeline)
- All C. System Flow files except `guidelines.py`
- All D. Model core files (meal_schema, candidate_generator, food_categorizer, similarity_checker)
- All F. WebApp files
- `finalize_micronutrient_guidelines.py` (setup)

---

## 9. PROJECT STRUCTURE HEALTH CHECK

| Aspect | Status | Notes |
|--------|--------|-------|
| **Code Organization** | ✅ Good | Clear separation: System Flow, Model, Preprocessing, WebApp |
| **Active Integration** | ⚠️ Partial | Main CLI works; Web & algorithms partially integrated |
| **Dead Code** | 🟡 Minor | 3-5 files are orphaned or empty |
| **Dependencies** | ✅ Clean | No circular dependencies observed |
| **Entry Points** | ⚠️ Limited | Only main.py fully active; app.py needs backend integration |
| **Data Pipeline** | ✅ Clear | B. Preprocessing → A. Data → C. System Flow |
| **Algorithm Status** | 🟡 Incomplete | Components ready but not integrated into main flow |

---

## 10. QUICK FILE REFERENCE

### Must Not Delete
```
C. System Flow/main.py
C. System Flow/nutrition_service.py
C. System Flow/data_loader.py
C. System Flow/modules/*
D. Model/candidate_generator.py
D. Model/meal_schema.py
D. Model/food_categorizer.py
D. Model/similarity_checker.py
F. WebApp/app.py
B. Preprocessing/05_final_dataset.py
B. Preprocessing/ML Klasifikasi/food_classifier.py
```

### Can Delete
```
C. System Flow/modules/guidelines.py (orphaned)
E. Evaluation/evaluation.py (empty)
D. Model/Greedy Algorithm/ (empty folder)
```

### Consider Moving to Trash
```
D. Model/Genetic Algorithm/*.py (if only for learning, not production)
B. Preprocessing/04_analyze_constraints.py (if purely exploratory)
compare_formats.py (if not needed for documentation)
```

---

## Conclusion

The codebase is **well-organized with clear separation of concerns**. The CLI nutrition system (`main.py` → `nutrition_service.py`) is fully functional. The model components for meal planning are in place and ready for integration. The main gaps are:

1. **Algorithm integration** - Genetic/Greedy implementations need finalization and integration
2. **Web backend** - Flask app needs connection to `nutrition_service.py`
3. **Code cleanup** - Remove 3-5 orphaned files for cleaner codebase

**Overall Assessment**: Strong foundation with minor cleanup needed. Ready for the next phase of algorithm implementation and web integration.

# IMPLEMENTATION CHECKLIST: 3-Phase Output Redesign

## 📋 PREPARATION CHECKLIST

Sebelum mulai implementasi, pastikan:

- [ ] File `output_formatter_ga.py` sudah ada di `D. Model/Genetic Algorithm/`
- [ ] Backup `run_ga_with_input_v2.py` original (rename ke `run_ga_with_input_v2_backup.py`)
- [ ] Sudah baca `THREE_PHASE_OUTPUT_GUIDE.py`
- [ ] Sudah lihat `EXAMPLE_THREE_PHASE_IMPLEMENTATION.py`

---

## 🔧 STEP-BY-STEP IMPLEMENTATION

### STEP 1: Update Imports (2 menit)

**File:** `D. Model/Genetic Algorithm/run_ga_with_input_v2.py`

**FIND:** (Line ~10-15, section imports)
```python
from ga_interface import GeneticAlgorithmInterface
from nutrition_service import NutritionService
```

**REPLACE WITH:**
```python
from ga_interface import GeneticAlgorithmInterface
from nutrition_service import NutritionService
from output_formatter_ga import OutputFormatterGA  # <-- TAMBAH INI
```

---

### STEP 2: Delete Old Display Functions (3 menit)

**FIND and DELETE complete functions:**

1. `display_nutrition_summary()` - Delete entire function
2. `display_ga_results()` - Delete entire function

**Why:** Ganti dengan OutputFormatterGA methods

---

### STEP 3: Rewrite main() Function (10 menit)

**File:** `D. Model/Genetic Algorithm/run_ga_with_input_v2.py`

**REPLACE ENTIRE main() function dengan:**

```python
def main():
    """
    Main flow dengan 3-phase output terstruktur:
      Phase 1: User Profile & Nutrition Assessment
      Phase 2: GA Optimization Processing
      Phase 3: Menu Recommendations
    """
    
    try:
        # ======================================================================
        # HEADER
        # ======================================================================
        print("\n" + "="*100)
        print("GENETIC ALGORITHM PERSONAL NUTRITION MENU GENERATOR")
        print("="*100 + "\n")
        
        # ======================================================================
        # PHASE 1: USER INPUT & PROFILE DISPLAY
        # ======================================================================
        
        print("[PHASE 1] Personal Input & Nutrition Calculation")
        print("-" * 100)
        
        # Get user input
        user_input = get_user_input()
        
        # Calculate nutrition
        print("\nCalculating nutrition requirements...")
        service = NutritionService()
        nutrition_result = service.calculate_nutrition_needs(user_input)
        
        # Check if calculation successful
        if not nutrition_result['success']:
            print(f"[ERROR] Calculation failed: {nutrition_result['error']}")
            return
        
        # Display user profile SEBELUM GA (INI YANG BARU)
        success = OutputFormatterGA.display_phase1_user_profile(
            user_input=user_input,
            nutrition_result=nutrition_result
        )
        
        if not success:
            print("[ERROR] Failed to display user profile")
            return
        
        # ======================================================================
        # PHASE 2: GA OPTIMIZATION
        # ======================================================================
        
        print("\n[PHASE 2] Genetic Algorithm Optimization")
        print("-" * 100)
        
        # Prepare GA parameters info
        if service.food_database is not None:
            food_count = len(service.food_database)
        else:
            food_count = 0
        
        ga_params = {
            'population_size': 50,
            'generations': 100,
            'food_count': food_count
        }
        
        # Display GA processing info (INI YANG BARU)
        OutputFormatterGA.display_phase2_ga_processing(ga_params)
        
        # Run GA
        ga = GeneticAlgorithmInterface(
            user_data=user_input,
            nutrition_service=service,
            population_size=50,
            generations=100,
            display_progress=False  # Progress dalam log saja, tidak print
        )
        
        menu_plan, best_fitness = ga.optimize()
        
        # Display GA completion (INI YANG BARU)
        OutputFormatterGA.display_phase2_ga_complete(
            best_fitness=best_fitness,
            generations_run=100
        )
        
        # ======================================================================
        # PHASE 3: MENU RECOMMENDATIONS
        # ======================================================================
        
        print("\n[PHASE 3] Personalized Menu Recommendations")
        print("-" * 100)
        
        # Get TDEE for display
        user_tdee = nutrition_result['energy']['tdee']
        
        # Display menu recommendations (INI YANG BARU - terstruktur)
        OutputFormatterGA.display_phase3_menu_recommendations(
            menu_plan=menu_plan,
            user_tdee=user_tdee,
            user_input=user_input
        )
        
        # ======================================================================
        # COMPLETION
        # ======================================================================
        
        print("[SUCCESS] All phases completed successfully!")
        
    except Exception as e:
        print(f"\n[ERROR] Process failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
```

---

## 📊 BEFORE & AFTER COMPARISON

### BEFORE (Old main())
```
Input User
  ↓
Calculate Nutrition
  ↓
[LANGSUNG tampilkan hasil GA]
[Profil tidak terlihat dengan jelas]
[Output bercampur-campur]
```

### AFTER (New main() dengan 3-phase)
```
Input User
  ↓
Calculate Nutrition
  ↓
PHASE 1: Display User Profile
  ├─ Personal Information
  ├─ Anthropometric Measurements
  ├─ Energy Requirements
  ├─ Health & Preferences
  └─ Nutrition Guidelines
  ↓
PHASE 2: GA Optimization
  ├─ GA Parameters
  └─ Completion Status
  ↓
PHASE 3: Menu Recommendations
  ├─ Breakfast (3 options per category)
  ├─ Lunch (3 options per category)
  ├─ Dinner (3 options per category)
  ├─ Daily Nutrition Summary
  ├─ Optimization Quality
  └─ Disclaimer
```

---

## 🧪 TESTING CHECKLIST

After implementation, test dengan:

### Test 1: Basic Functionality
- [ ] Script runs tanpa error
- [ ] No "ModuleNotFoundError" untuk OutputFormatterGA
- [ ] No "AttributeError" untuk methods

### Test 2: Phase 1 Output
```bash
# Input:
Gender: F
Age: 25
Weight: 60
Height: 165
Activity: 2
Disease: Normal
Cuisine: Western

# Expected output:
✓ Personal Information section
✓ BMI Value: ~22.0 kg/m²
✓ BMI Category: Normal Weight
✓ IBW: ~58.5 kg
✓ TDEE: ~1800 kcal
✓ Age Group: Young Adult
✓ Health/Preferences shown
```

### Test 2: Phase 2 Output
```
Expected:
✓ GA PARAMETERS message
✓ Processing info
✓ "GA OPTIMIZATION COMPLETE" message
✓ Final Fitness Score shown
```

### Test 3: Phase 3 Output
```
Expected:
✓ BREAKFAST section with 3 main/side/drink options
✓ LUNCH section with 3 main/side/drink options
✓ DINNER section with 3 main/side/drink options
✓ Daily Nutrition Summary
✓ Fitness Score with progress bar
✓ User Selection Guide
✓ Disclaimer
```

### Test 4: Integration
```bash
# Full run test:
python run_ga_with_input_v2.py

# Verify:
✓ All 3 phases display in order
✓ No formatting issues
✓ Output readable
✓ Takes ~30-60 seconds total (10s input + 20-40s GA + 5s output)
```

---

## 📄 DELIVERABLES

Files yang sudah dibuat:

| File | Tujuan | Status |
|------|--------|--------|
| `output_formatter_ga.py` | Main formatter class | ✅ Ready |
| `EXAMPLE_THREE_PHASE_IMPLEMENTATION.py` | Code examples | ✅ Ready |
| `THREE_PHASE_OUTPUT_GUIDE.py` | Detailed guide | ✅ Ready |
| `run_ga_with_input_v2.py` | **PERLU DIEDIT** | ⏳ PendingEdit |

---

## 🎯 EXPECTED RESULTS

### Output Structure
```
PHASE 1: USER PROFILE
├── Personal Information
├── Anthropometric Measurements
├── Energy Requirements
├── Health & Preferences
└── Nutrition Guidelines

PHASE 2: GA PROCESSING
└── Completion Status

PHASE 3: MENU RECOMMENDATIONS
├── Breakfast with 3 options per category
├── Lunch with 3 options per category
├── Dinner with 3 options per category
├── Daily Nutrition Summary
├── Optimization Quality Score
└── User Selection Guide + Disclaimer
```

### Output Quality
- ✅ Clear and structured
- ✅ User understands profile before seeing menu
- ✅ Complies with DSS paradigm
- ✅ Professional presentation
- ✅ Easy to read and follow

---

## ⚡ QUICK REFERENCE

### Methods Available

```python
# Phase 1
OutputFormatterGA.display_phase1_user_profile(user_input, nutrition_result)

# Phase 2
OutputFormatterGA.display_phase2_ga_processing(ga_params)
OutputFormatterGA.display_phase2_ga_progress(generation, best, avg)  # optional
OutputFormatterGA.display_phase2_ga_complete(best_fitness, generations)

# Phase 3
OutputFormatterGA.display_phase3_menu_recommendations(menu_plan, tdee, user_input)
```

### Helper Methods (Internal)
```python
OutputFormatterGA._display_meal_options(meal_obj, meal_type)
OutputFormatterGA._get_bmi_category_info(bmi, category)
OutputFormatterGA._get_weight_status(current, ibw)
OutputFormatterGA._get_activity_label(activity_factor)
```

---

## 🐛 TROUBLESHOOTING

### Problem: ImportError: cannot import name 'OutputFormatterGA'
**Solution:**
- Check `output_formatter_ga.py` exists in `D. Model/Genetic Algorithm/`
- Check import statement: `from output_formatter_ga import OutputFormatterGA`
- Verify current directory is correct

### Problem: AttributeError: 'OutputFormatterGA' has no attribute...
**Solution:**
- Check method name spelling
- Verify OutputFormatterGA.py syntax is valid
- Run Python syntax check: `python -m py_compile output_formatter_ga.py`

### Problem: Output formatting looks broken
**Solution:**
- Terminal width must be at least 100 characters
- Try full-screen terminal
- Check for special characters compatibility

### Problem: Want to revert to old version
**Solution:**
- Use backup: `rename run_ga_with_input_v2_backup.py to run_ga_with_input_v2.py`
- Or restore from git: `git checkout run_ga_with_input_v2.py`

---

## ✅ COMPLETION CHECKLIST

- [ ] Imports updated
- [ ] Old functions deleted
- [ ] main() function replaced
- [ ] Script tested with sample input
- [ ] All 3 phases display correctly
- [ ] Formatting looks good
- [ ] No errors in console
- [ ] Ready for TA/presentation

---

## 📞 SUPPORT

If you encounter issues:

1. Check `THREE_PHASE_OUTPUT_GUIDE.py` section 6 (Troubleshooting)
2. Review `EXAMPLE_THREE_PHASE_IMPLEMENTATION.py` for reference
3. Verify `output_formatter_ga.py` syntax: `python -m py_compile output_formatter_ga.py`
4. Test individual methods in Python REPL

---

**Status:** Ready for implementation! 🚀

All files created and documented. Just follow the 3 steps above.

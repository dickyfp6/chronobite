"""
Dokumentasi: 3-PHASE OUTPUT REDESIGN
Implementasi struktur output yang terstruktur: Profil → GA → Menu

File ini menjelaskan:
1. Masalah saat ini
2. Solusi yang direkomendasikan
3. Bagaimana mengintegrasikan
4. Step-by-step implementation
5. Testing checklist
"""

# ═══════════════════════════════════════════════════════════════════════════
# 1. MASALAH SAAT INI
# ═══════════════════════════════════════════════════════════════════════════

"""
❌ OUTPUT FLOW SAAT INI (run_ga_with_input_v2.py):

1. User input (gender, age, weight, height, activity, disease, preferences)
2. LANGSUNG jalankan GA
3. LANGSUNG tampilkan hasil GA (menu)
4. Profil user (BMI, TDEE, etc) tidak jelas sebelum GA

MASALAH:
✗ User tidak tahu profilenya dulu sebelum lihat menu
✗ Tidak sesuai dengan DSS paradigm (user harus paham inputnya dulu)
✗ Output structure tidak ideal untuk interaksi user
✗ GA progress tercampur dengan hasil akhir
"""

# ═══════════════════════════════════════════════════════════════════════════
# 2. SOLUSI YANG DIREKOMENDASIKAN
# ═══════════════════════════════════════════════════════════════════════════

"""
✓ 3-PHASE OUTPUT FLOW (Rekomendasi):

PHASE 1: PROFIL USER (Display SEBELUM GA)
├─ Personal Information (Gender, Age, Weight, Height)
├─ Anthropometric Measurements (BMI Value, BMI Category, IBW)
├─ Energy Requirements (BMR, TDEE, Activity Level)
├─ Health & Preferences (Health Conditions, Cuisine Preferences)
└─ Nutrition Guidelines (Total nutrients, macros, micros)

PHASE 2: GA PROCESSING (Optional/Log)
├─ GA Parameters Display
├─ Progress Info (optional)
└─ Completion Status

PHASE 3: MENU RECOMMENDATIONS (Display SESUDAH GA)
├─ BREAKFAST (Main/Side/Drink dengan 3 pilihan masing-masing)
├─ LUNCH
├─ DINNER
├─ SNACK (jika ada)
├─ Daily Nutrition Summary
├─ Optimization Quality (Fitness Score)
├─ User Selection Guide
└─ Disclaimer

BENEFITS:
✓ Terstruktur dan jelas
✓ Sesuai DSS paradigm
✓ User tahu profilenya dulu
✓ Menu recommendations comprehensif
✓ User-friendly untuk interaksi
"""

# ═══════════════════════════════════════════════════════════════════════════
# 3. BAGAIMANA MENGINTEGRASIKAN
# ═══════════════════════════════════════════════════════════════════════════

"""
FILES YANG PERLU DISIAPKAN:

1. ✓ output_formatter_ga.py
   - SUDAH DIBUAT
   - Lokasi: D. Model/Genetic Algorithm/
   - Isi: Class OutputFormatterGA dengan 3-phase methods
   
2. run_ga_with_input_v2.py
   - PERLU DIEDIT
   - Ubah main() function untuk menggunakan OutputFormatterGA
   - Lihat section 4 di bawah untuk detil

INTEGRATION POINTS:

OLD main() func:
────────────────
user_input = get_user_input()
nutrition_result = calculate_nutrition_needs()
menu_plan = ga.optimize()
display_old_results()

NEW main() func:
────────────────
user_input = get_user_input()
nutrition_result = calculate_nutrition_needs()

# PHASE 1
OutputFormatterGA.display_phase1_user_profile(user_input, nutrition_result)

# PHASE 2
OutputFormatterGA.display_phase2_ga_processing(ga_params)
menu_plan = ga.optimize()
OutputFormatterGA.display_phase2_ga_complete(best_fitness, 100)

# PHASE 3
OutputFormatterGA.display_phase3_menu_recommendations(menu_plan, tdee, user_input)
"""

# ═══════════════════════════════════════════════════════════════════════════
# 4. STEP-BY-STEP IMPLEMENTATION
# ═══════════════════════════════════════════════════════════════════════════

"""
STEP 1: Update imports di run_ga_with_input_v2.py
────────────────────────────────────────────────

CURRENT (cari bagian imports):
    from ga_interface import GeneticAlgorithmInterface
    from nutrition_service import NutritionService

UBAH MENJADI:
    from ga_interface import GeneticAlgorithmInterface
    from nutrition_service import NutritionService
    from output_formatter_ga import OutputFormatterGA  # <-- TAMBAH INI


STEP 2: Hapus old display functions
────────────────────────────────────────────────

CARI dan HAPUS functions:
    - display_nutrition_summary(nutrition_result, user_input)
    - display_ga_results(menu_plan, user_tdee)

(Ganti dengan OutputFormatterGA methods)


STEP 3: Rewrite main() function
────────────────────────────────────────────────

REPLACE entire main() function dengan code di bawah ini:

```python
def main():
    '''Main flow dengan 3-phase output terstruktur'''
    
    try:
        # Display header
        print("\n" + "="*100)
        print("GENETIC ALGORITHM PERSONAL NUTRITION MENU GENERATOR")
        print("="*100 + "\n")
        
        # ═════════════════════════════════════════════════════════════════
        # PHASE 1: USER INPUT & PROFILE
        # ═════════════════════════════════════════════════════════════════
        
        print("[PHASE 1] Personal Input & Nutrition Calculation")
        print("-" * 100)
        
        # Get user input
        user_input = get_user_input()
        
        # Calculate nutrition
        print("\nCalculating nutrition requirements...")
        service = NutritionService()
        nutrition_result = service.calculate_nutrition_needs(user_input)
        
        if not nutrition_result['success']:
            print(f"[ERROR] {nutrition_result['error']}")
            return
        
        # Display user profile menggunakan OutputFormatterGA
        success = OutputFormatterGA.display_phase1_user_profile(user_input, nutrition_result)
        
        if not success:
            print("[ERROR] Failed to display profile")
            return
        
        # ═════════════════════════════════════════════════════════════════
        # PHASE 2: GA OPTIMIZATION
        # ═════════════════════════════════════════════════════════════════
        
        print("\n[PHASE 2] Genetic Algorithm Optimization")
        print("-" * 100)
        
        # Display GA parameters
        if service.food_database is not None:
            food_count = len(service.food_database)
        else:
            food_count = 0
        
        ga_params = {
            'population_size': 50,
            'generations': 100,
            'food_count': food_count
        }
        
        OutputFormatterGA.display_phase2_ga_processing(ga_params)
        
        # Run GA
        ga = GeneticAlgorithmInterface(
            user_data=user_input,
            nutrition_service=service,
            population_size=50,
            generations=100,
            display_progress=False  # Log progress, tidak print
        )
        
        menu_plan, best_fitness = ga.optimize()
        
        # Display GA completion
        OutputFormatterGA.display_phase2_ga_complete(best_fitness, 100)
        
        # ═════════════════════════════════════════════════════════════════
        # PHASE 3: MENU RECOMMENDATIONS
        # ═════════════════════════════════════════════════════════════════
        
        print("\n[PHASE 3] Personalized Menu Recommendations")
        print("-" * 100)
        
        user_tdee = nutrition_result['energy']['tdee']
        OutputFormatterGA.display_phase3_menu_recommendations(
            menu_plan=menu_plan,
            user_tdee=user_tdee,
            user_input=user_input
        )
        
        print("[SUCCESS] All phases completed!")
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
```


STEP 4: Test implementation
────────────────────────────────────────────────

1. Run script: python run_ga_with_input_v2.py
2. Provide test input:
   - Gender: F
   - Age: 25
   - Weight: 60
   - Height: 165
   - Activity: 2 (Moderately Active)
   - Disease: Normal
   - Cuisine: Western

3. Verify output tampil dalam 3 phases:
   ✓ Phase 1: Profil user (BMI, TDEE, etc)
   ✓ Phase 2: GA optimization message
   ✓ Phase 3: Menu recommendations dengan 3 pilihan per kategori
"""

# ═══════════════════════════════════════════════════════════════════════════
# 5. OUTPUT STRUKTUR DETAIL
# ═══════════════════════════════════════════════════════════════════════════

"""
PHASE 1 OUTPUT:

═════════════════════════════════════════════════════════════════════════════════
  PHASE 1: USER PROFILE & NUTRITION ASSESSMENT
═════════════════════════════════════════════════════════════════════════════════
Generated: 2024-04-13 10:30:45

┌─ [1] PERSONAL INFORMATION
├──────────────────────────────────────────────────────────────────────────────
│  Gender:        F
│  Age:           25 years old (Young Adult)
│  Weight:        60.0 kg
│  Height:        165.0 cm
└──────────────────────────────────────────────────────────────────────────────

┌─ [2] ANTHROPOMETRIC MEASUREMENTS (WHO Standards)
├──────────────────────────────────────────────────────────────────────────────
│  BMI Value:     22.0 kg/m²
│  BMI Category:  Normal Weight (18.5–24.9)
│                ✓ NORMAL
│
│  Ideal Body Weight (IBW): 58.5 kg
│  Current vs IBW:          Within ideal range (±10% IBW)
└──────────────────────────────────────────────────────────────────────────────

[... dst ...]

Status: ✓ PROFIL SIAP
Next: GA akan mengoptimasi menu berdasarkan profil di atas


PHASE 2 OUTPUT:

═════════════════════════════════════════════════════════════════════════════════
  PHASE 2: GENETIC ALGORITHM OPTIMIZATION (Running...)
═════════════════════════════════════════════════════════════════════════════════
Timestamp: 2024-04-13 10:30:46

├─ GA PARAMETERS:
│  Population Size:     50
│  Generations:         100
│  Optimization Target: Nutrient Compliance + Calorie Accuracy
│  Food Database:       3920 items available
│
├─ PROCESSING:
│  [In progress...] GA is searching optimal menu combinations
│  [This may take 10-30 seconds depending on database size]
└──────────────────────────────────────────────────────────────────────────────

✓ GA OPTIMIZATION COMPLETE
  Final Best Fitness: 75.45 / 100
  Generations Run:    100
  Status:             Menu optimization successful


PHASE 3 OUTPUT:

╔═════════════════════════════════════════════════════════════════════════════════╗
║                     PERSONALIZED NUTRITION MENU - GENETIC ALGORITHM              ║
║                                    Complete Daily Plan                           ║
╚═════════════════════════════════════════════════════════════════════════════════╝

┌──────────────────────────────────────────────────────────────────────────────────
│ 🌅 BREAKFAST (Sarapan pukul 06:00-07:00)
├──────────────────────────────────────────────────────────────────────────────────
│
│  🍖 MAIN COURSE (Choose 1):
│     [1] Nasi Kuning
│         └─ 150g | 240 kcal | Protein 5.2g | Carbs 52.1g | Fat 2.8g
│     [2] Roti Gandum
│         └─ 100g | 265 kcal | Protein 8.1g | Carbs 49.2g | Fat 3.2g
│     [3] Bubur Ayam
│         └─ 200g | 180 kcal | Protein 12.5g | Carbs 21.3g | Fat 4.1g
│
│  🥗 SIDE DISH (Choose 1):
│     [1] Telur Rebus
│         └─ 50g | 78 kcal | Protein 6.3g | Carbs 0.6g | Fat 5.3g
│     [2] Tempe Goreng
│         └─ 75g | 195 kcal | Protein 19.3g | Carbs 4.2g | Fat 10.8g
│     [3] Sayuran Hijau
│         └─ 100g | 42 kcal | Protein 3.2g | Carbs 7.8g | Fat 0.3g
│
│  🥤 DRINK (Optional - Choose 0 or 1):
│     [1] Teh Tawar
│         └─ 200mL | 2 kcal
│     [2] Susu Rendah Lemak
│         └─ 200mL | 102 kcal
│     [3] Jus Jeruk
│         └─ 250mL | 125 kcal
│
│  📊 Meal Summary: 515 kcal | P:27.1g C:73.2g F:21.7g
└──────────────────────────────────────────────────────────────────────────────────

[... LUNCH, DINNER similar ...]

┌──────────────────────────────────────────────────────────────────────────────────
│ 📊 DAILY NUTRITION SUMMARY
├──────────────────────────────────────────────────────────────────────────────────
│  ├─ Daily Energy Target (TDEE): 1822 kcal
│  ├─ Menu Total Energy:          1805 kcal
│  ├─ Difference:                 -17 kcal (-0.9%)
│  └─ Status:                     ✓ EXCELLENT (within ±10%)
│
│  Total Macronutrients:
│  ├─ Protein:  68.5 g
│  ├─ Carbs:    245.3 g
│  └─ Fat:      62.1 g
└──────────────────────────────────────────────────────────────────────────────────

[... OPTIMIZATION QUALITY, DISCLAIMER ...]

✓ Menu generation complete!
═════════════════════════════════════════════════════════════════════════════════
"""

# ═══════════════════════════════════════════════════════════════════════════
# 6. TESTING CHECKLIST
# ═══════════════════════════════════════════════════════════════════════════

"""
UNIT TESTING CHECKLIST:

Phase 1 (User Profile):
  ✓ BMI calculated correctly (should match formula: weight/(height/100)²)
  ✓ BMI category correct (Normal, Overweight, etc)
  ✓ IBW calculated correctly
  ✓ TDEE calculated correctly = BMR × Activity Factor
  ✓ Age group classification correct
  ✓ Health conditions displayed
  ✓ Cuisine preferences displayed

Phase 2 (GA Processing):
  ✓ GA params displayed (population, generations, food count)
  ✓ GA runs without errors
  ✓ Best fitness score displayed
  ✓ Completion message shown

Phase 3 (Menu Recommendations):
  ✓ Breakfast, Lunch, Dinner shown
  ✓ Each meal has Main/Side/Drink options
  ✓ Each option shows: food name, portion, kcal, protein, carbs, fat
  ✓ Max 3 options per category
  ✓ Daily summary shows total kcal, macros
  ✓ Fitness score displayed with progress bar
  ✓ Disclaimer shown

Integration Testing:
  ✓ Full flow runs without errors
  ✓ No missing imports
  ✓ Output formatting correct (no broken lines)
  ✓ All 3 phases display in order
  ✓ User can input values at each step
  ✓ Output readable on different terminal sizes

Regression Testing:
  ✓ Existing GA logic unchanged
  ✓ Nutrition calculation unchanged
  ✓ Menu optimization unchanged
  ✓ Only display layer changed
"""

# ═══════════════════════════════════════════════════════════════════════════
# 7. ADDITIONAL FEATURES (Optional - untuk ditambah nanti)
# ═══════════════════════════════════════════════════════════════════════════

"""
OPTIONAL FEATURES (Bisa diimplementasikan nanti):

1. PHASE 4: INTERACTIVE MENU SELECTION
   - User picks 1 main + 1 side + 1 drink per meal
   - Calculate actual nutrition dari selection
   - Compare vs target

2. SAVE TO FILE
   - Export menu to PDF
   - Export menu to JSON
   - Export menu to CSV

3. SHOPPING LIST
   - Generate shopping list dari selected menu
   - Show portion quantities
   - Show estimated cost

4. DETAILED NUTRIENT BREAKDOWN
   - Per-food nutrient detail
   - Per-meal nutrient detail
   - Compare vs guideline

5. MEAL TIMING
   - Suggest meal times (breakfast 06:00, lunch 12:00, etc)
   - Calorie distribution per meal (30%, 40%, 20%, 10%)

6. SUSTAINABILITY
   - Show if menu sustainable (repeat daily vs variety)
   - Suggest rotation for weekly menu

IMPLEMENTATION ORDER:
Priority 1 (Current): 3-phase output display ✓
Priority 2: Phase 4 interactive selection
Priority 3: Save to file
Priority 4: Shopping list
"""

# ═══════════════════════════════════════════════════════════════════════════
# 8. QUICK REFERENCE
# ═══════════════════════════════════════════════════════════════════════════

"""
QUICK REFERENCE (Untuk copy-paste):

1. Add import:
   from output_formatter_ga import OutputFormatterGA

2. Phase 1 display:
   OutputFormatterGA.display_phase1_user_profile(user_input, nutrition_result)

3. Phase 2 init:
   OutputFormatterGA.display_phase2_ga_processing(ga_params)

4. Phase 2 progress (optional, per generation):
   OutputFormatterGA.display_phase2_ga_progress(gen, best_fitness, avg_fitness)

5. Phase 2 complete:
   OutputFormatterGA.display_phase2_ga_complete(best_fitness, 100)

6. Phase 3 results:
   OutputFormatterGA.display_phase3_menu_recommendations(menu_plan, tdee, user_input)

File Locations:
- output_formatter_ga.py: D. Model/Genetic Algorithm/
- run_ga_with_input_v2.py: D. Model/Genetic Algorithm/
- This guide: D. Model/Genetic Algorithm/THREE_PHASE_OUTPUT_GUIDE.py

Support:
- Read EXAMPLE_THREE_PHASE_IMPLEMENTATION.py for code examples
- Check OutputFormatterGA docstrings for method details
- Test with sample input (F, 25, 60, 165, 2, Normal, Western)
"""

print(__doc__)

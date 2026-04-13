"""
EXAMPLE IMPLEMENTATION: Mengintegrasikan OutputFormatterGA
Menunjukkan bagaimana mengubah run_ga_with_input_v2.py untuk menggunakan 3-phase output

File ini adalah CONTOH/REFERENCE - tidak perlu di-run langsung
Tunjukkan struktur kode yang direkomendasikan
"""

# ============================================================================
# STEP 1: IMPORT statements (tambahkan OutputFormatterGA)
# ============================================================================

import sys
import os
import pandas as pd
from ga_interface import GeneticAlgorithmInterface
from nutrition_service import NutritionService
from output_formatter_ga import OutputFormatterGA  # <-- NEW IMPORT


# ============================================================================
# STEP 2: INPUT function (bisa tetap sama atau sedikit modifikasi)
# ============================================================================

def get_user_input():
    """Input user - TIDAK PERLU DIUBAH"""
    # ... existing code tetap sama ...
    pass


# ============================================================================
# STEP 3: MAIN FLOW dengan 3-PHASE OUTPUT (INI YANG DIUBAH)
# ============================================================================

def main_with_three_phase_output():
    """
    Main flow dengan 3-phase output terstruktur:
      Phase 1: User Profile Display
      Phase 2: GA Processing
      Phase 3: Menu Recommendations
    
    Ini adalah struktur yang DIREKOMENDASIKAN untuk implementasi
    """
    
    try:
        # =====================================================================
        # INPUT: Get user input
        # =====================================================================
        print("\n" + "="*100)
        print("GENETIC ALGORITHM PERSONAL NUTRITION MENU GENERATOR")
        print("="*100 + "\n")
        
        user_input = get_user_input()
        
        # =====================================================================
        # PHASE 1: Calculate Nutrition & Display User Profile
        # =====================================================================
        
        print("\n[PHASE 1] Calculating nutrition requirements...")
        service = NutritionService()
        nutrition_result = service.calculate_nutrition_needs(user_input)
        
        if not nutrition_result['success']:
            print(f"[ERROR] {nutrition_result['error']}")
            return
        
        # Display user profile SEBELUM GA
        OutputFormatterGA.display_phase1_user_profile(user_input, nutrition_result)
        
        # =====================================================================
        # PHASE 2: GA Processing
        # =====================================================================
        
        print("[PHASE 2] Starting Genetic Algorithm optimization...")
        
        # Display GA parameters info
        ga_params = {
            'population_size': 50,
            'generations': 100,
            'food_count': len(service.food_database) if service.food_database is not None else 0
        }
        OutputFormatterGA.display_phase2_ga_processing(ga_params)
        
        # Run GA
        ga = GeneticAlgorithmInterface(
            user_data=user_input,
            nutrition_service=service,
            population_size=50,
            generations=100,
            display_progress=True  # Enable progress display
        )
        
        print("│")
        menu_plan, best_fitness = ga.optimize()
        
        # Display GA completion
        OutputFormatterGA.display_phase2_ga_complete(best_fitness, 100)
        
        # =====================================================================
        # PHASE 3: Menu Recommendations
        # =====================================================================
        
        print("[PHASE 3] Displaying optimized menu recommendations...\n")
        
        user_tdee = nutrition_result['energy']['tdee']
        OutputFormatterGA.display_phase3_menu_recommendations(
            menu_plan=menu_plan,
            user_tdee=user_tdee,
            user_input=user_input
        )
        
        print("[OK] Process completed successfully!")
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()


# ============================================================================
# STEP 4: ALTERNATIVE FLOW (Manual phases jika tidak mau auto)
# ============================================================================

def main_with_optional_ga_display():
    """
    Alternative: GA processing display bisa dibuat optional
    Kalau user tidak ingin melihat GA progress, bisa di-skip
    """
    
    user_input = get_user_input()
    service = NutritionService()
    nutrition_result = service.calculate_nutrition_needs(user_input)
    
    # PHASE 1
    OutputFormatterGA.display_phase1_user_profile(user_input, nutrition_result)
    
    # PHASE 2 (OPTIONAL)
    show_ga_progress = input("\nShow GA progress? (y/n): ").lower() == 'y'
    
    if show_ga_progress:
        ga_params = {'population_size': 50, 'generations': 100, 'food_count': 3920}
        OutputFormatterGA.display_phase2_ga_processing(ga_params)
    
    # Run GA (dengan atau tanpa display)
    ga = GeneticAlgorithmInterface(
        user_data=user_input,
        nutrition_service=service,
        population_size=50,
        generations=100,
        display_progress=show_ga_progress
    )
    
    menu_plan, best_fitness = ga.optimize()
    
    if show_ga_progress:
        OutputFormatterGA.display_phase2_ga_complete(best_fitness, 100)
    
    # PHASE 3
    user_tdee = nutrition_result['energy']['tdee']
    OutputFormatterGA.display_phase3_menu_recommendations(
        menu_plan=menu_plan,
        user_tdee=user_tdee,
        user_input=user_input
    )


# ============================================================================
# CODE CHANGES CHECKLIST
# ============================================================================

"""
Untuk mengintegrasikan 3-phase output ke run_ga_with_input_v2.py:

1. ✓ IMPORT
   - Tambahkan: from output_formatter_ga import OutputFormatterGA
   
2. ✓ HAPUS old display functions (jika ada)
   - Hapus: display_nutrition_summary()
   - Hapus: display_ga_results()
   
3. ✓ UBAH main() flow menjadi 3 phase:
   
   OLD:
   ────────────────────────────────────────────────
   user_input = get_user_input()
   nutrition_result = calculate_nutrition_needs(user_input)
   menu_plan = ga.optimize()
   display_old_results()
   
   NEW:
   ────────────────────────────────────────────────
   user_input = get_user_input()
   nutrition_result = calculate_nutrition_needs(user_input)
   
   # PHASE 1: Display profile
   OutputFormatterGA.display_phase1_user_profile(user_input, nutrition_result)
   
   # PHASE 2: GA processing
   OutputFormatterGA.display_phase2_ga_processing(ga_params)
   menu_plan = ga.optimize()
   OutputFormatterGA.display_phase2_ga_complete(best_fitness, 100)
   
   # PHASE 3: Menu recommendations
   OutputFormatterGA.display_phase3_menu_recommendations(menu_plan, tdee, user_input)

4. ✓ OPTIONAL: Add interactive selection
   - User bisa memilih 1 main + 1 side + 1 drink per meal
   - (Bisa ditambahkan nanti sebagai "Phase 4")

5. ✓ TEST
   - Run with sample input
   - Verify 3 phases display correctly
   - Check formatting dan alignment
"""


# ============================================================================
# CODE SNIPPETS: Contoh main() yang direkomendasikan
# ============================================================================

def main_recommended_implementation():
    """
    MAIN FUNCTION - Rekomendasi implementasi final
    Ini bisa langsung di-copy ke run_ga_with_input_v2.py
    """
    
    try:
        # ═══════════════════════════════════════════════════════════════════
        # PHASE 1: USER INPUT & PROFILE DISPLAY
        # ═══════════════════════════════════════════════════════════════════
        
        print("\n" + "="*100)
        print("GENETIC ALGORITHM PERSONAL NUTRITION MENU GENERATOR")
        print("="*100 + "\n")
        
        # 1. Get user input
        user_input = get_user_input()
        
        # 2. Calculate nutrition
        print("\n[PHASE 1] Calculating nutrition requirements...")
        service = NutritionService()
        nutrition_result = service.calculate_nutrition_needs(user_input)
        
        if not nutrition_result['success']:
            print(f"[ERROR] Calculation failed: {nutrition_result['error']}")
            return
        
        # 3. Display user profile (BEFORE GA)
        success = OutputFormatterGA.display_phase1_user_profile(user_input, nutrition_result)
        
        if not success:
            print("[ERROR] Failed to display profile")
            return
        
        # ═══════════════════════════════════════════════════════════════════
        # PHASE 2: GA OPTIMIZATION
        # ═══════════════════════════════════════════════════════════════════
        
        print("\n[PHASE 2] Starting Genetic Algorithm optimization...")
        
        # Display GA info
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
            display_progress=False  # Progress dalam log saja
        )
        
        menu_plan, best_fitness = ga.optimize()
        
        # Display GA completion
        OutputFormatterGA.display_phase2_ga_complete(best_fitness, 100)
        
        # ═══════════════════════════════════════════════════════════════════
        # PHASE 3: MENU RECOMMENDATIONS
        # ═══════════════════════════════════════════════════════════════════
        
        print("\n[PHASE 3] Displaying optimized menu recommendations...\n")
        
        user_tdee = nutrition_result['energy']['tdee']
        OutputFormatterGA.display_phase3_menu_recommendations(
            menu_plan=menu_plan,
            user_tdee=user_tdee,
            user_input=user_input
        )
        
        print("\n[OK] All phases completed successfully!")
    
    except Exception as e:
        print(f"\n[ERROR] Process failed: {e}")
        import traceback
        traceback.print_exc()


# ============================================================================
# IMPORTANT NOTES UNTUK IMPLEMENTASI
# ============================================================================

"""
NOTES PENTING:

1. BACKWARD COMPATIBILITY
   ✓ OutputFormatterGA bisa digunakan tanpa mengubah struktur GA
   ✓ Hanya mengubah DISPLAY, bukan LOGIC
   
2. INTEGRATION POINTS
   ✓ Setelah calculate_nutrition_needs() → display_phase1_user_profile()
   ✓ Sebelum GA.optimize() → display_phase2_ga_processing()
   ✓ Sesudah GA.optimize() → display_phase2_ga_complete()
   ✓ Sesudah GA selesai → display_phase3_menu_recommendations()

3. OPTIONAL FEATURES (bisa ditambah nanti)
   ✓ Interactive menu selection (user pick 1 main + 1 side + 1 drink)
   ✓ Save menu to file (PDF/JSON)
   ✓ Shopping list generation
   ✓ Detailed nutrient breakdown per food

4. FILES UNTUK DIEDIT
   - run_ga_with_input_v2.py (MAIN FILE - ganti main() function)
   - Optionally: run_ga_with_input.py (jika masih dipakai)

5. FILES YANG SUDAH SIAP
   ✓ output_formatter_ga.py (BARU - formatter dengan 3 phase)
   ✓ ga_interface.py (EXISTING - menu optimization)
   ✓ nutrition_service.py (EXISTING - nutrient calculation)
"""


if __name__ == "__main__":
    # Choose which implementation to test
    print("This is an EXAMPLE file showing recommended implementation")
    print("\nTo use, copy the code from:")
    print("  - main_recommended_implementation() function")
    print("Into your run_ga_with_input_v2.py main() function")
    print("\nDo NOT run this file directly - it's for reference only")

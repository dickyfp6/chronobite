"""
Greedy Algorithm Usage Example
Demonstrates how to use Greedy Algorithm untuk generate menu recommendations
"""

from greedy_interface import GreedyAlgorithmInterface, get_greedy_algorithm
import json


def example_greedy_with_nutrition_service():
    """
    Example: Integrate Greedy Algorithm dengan NutritionService
    
    Ini adalah cara recommended untuk menggunakan Greedy Algorithm dari main sistem.
    """
    
    print("=" * 70)
    print("EXAMPLE: Greedy Algorithm dengan NutritionService")
    print("=" * 70)
    
    # 1. Setup NutritionService (dari main sistem)
    try:
        from nutrition_service import NutritionService
    except ImportError:
        print("❌ Tidak bisa import NutritionService, run dari project root")
        return
    
    # 2. User input simulasi
    user_input = {
        'gender': 'M',
        'age': 30,
        'weight': 70.0,
        'height': 170.0,
        'activity_factor': 1.845,  # FAO/WHO/UNU sedang
        'disease': 'normal',
        'food_preferences': ['Asian']
    }
    
    # 3. Load nutrition service
    service = NutritionService()
    result = service.calculate_nutrition_needs(user_input)
    
    if not result['success']:
        print(f"❌ Nutrition calculation failed: {result.get('error')}")
        return
    
    print(f"\n✓ User Profile:")
    print(f"  Name: {result.get('anthropometrics', {}).get('bmi', 'N/A')}")
    print(f"  TDEE: {result.get('energy', {}).get('tdee', 'N/A')} kcal/day")
    
    # 4. Initialize Greedy Algorithm
    greedy = GreedyAlgorithmInterface()
    
    success = greedy.initialize(
        food_database=result.get('food_data', {}).get('dataframe'),
        nutrition_guidelines=result.get('guidelines', {})
    )
    
    if not success:
        print("❌ Failed to initialize Greedy Algorithm")
        return
    
    # 5. Generate menu
    tdee = result.get('energy', {}).get('tdee', 2000)
    
    # Standard meal distribution (breakfast, lunch, snack, dinner)
    meal_distribution = {
        'breakfast': 0.25,
        'lunch': 0.35,
        'snack': 0.10,
        'dinner': 0.30,
    }
    
    menu_plan = greedy.generate_menu_plan(
        user_profile=result.get('anthropometrics', {}),
        meal_distribution=meal_distribution,
        user_tdee=tdee
    )
    
    if menu_plan:
        print(f"\n✅ Menu Plan Generated!")
        print(f"\nFull Menu Output:")
        print(json.dumps(menu_plan.to_dict(), indent=2, default=str))
    else:
        print("❌ Failed to generate menu plan")


def example_greedy_minimal():
    """
    Minimal example: Direct usage tanpa NutritionService
    (Untuk testing/debugging hanya)
    """
    
    print("\n" + "=" * 70)
    print("EXAMPLE: Greedy Algorithm Minimal (Direct Usage)")
    print("=" * 70)
    
    # Simulate minimal inputs
    print("Note: This is for development/debugging only")
    print("In production, use example_greedy_with_nutrition_service() instead")


# ========================================
# COMPARISON: Greedy vs Genetic
# ========================================

def comparison_algorithms():
    """
    Comparison between Greedy dan Genetic Algorithm
    """
    
    print("\n" + "=" * 70)
    print("ALGORITHM COMPARISON")
    print("=" * 70)
    
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                     GREEDY ALGORITHM                                ║
╚══════════════════════════════════════════════════════════════════════╝

  Strategi: Locally Optimal Choice (pick terbaik di setiap step)
  
  Mekanisme:
  1. Untuk setiap meal slot (Breakfast Main, Breakfast Side, dst)
  2. Generate candidates dengan similarity check
  3. Score setiap candidate berdasarkan:
     - Calorie match (60% weight)
     - Nutrient satisfaction (30% weight)
     - Ingredient diversity (10% weight)
  4. Pick candidate dengan score tertinggi
  5. Update exclusion list untuk diversity di slot berikutnya
  
  Kecepatan: CEPAT (O(n) per slot)
  Kompleksitas: LOW
  Memori: LOW
  
  Keuntungan:
  ✓ Cepat (real-time response mungkin)
  ✓ Deterministic (hasil konsisten untuk input sama)
  ✓ Mudah di-debug
  ✓ Cocok untuk MVP/prototype
  
  Kekurangan:
  ✗ Tidak global optimal (local maxima)
  ✗ Tidak explore kombinasi kompleks
  ✗ Tidak bisa backtrack kalau pilihan awal buruk


╔══════════════════════════════════════════════════════════════════════╗
║                     GENETIC ALGORITHM                               ║
╚══════════════════════════════════════════════════════════════════════╝

  Strategi: Population-based Evolution (explore banyak kombinasi)
  
  Mekanisme:
  1. Buat populasi awal menu plans random
  2. Evaluasi fitness setiap menu dengan scoring kompleks
  3. Selection: pick best-scored menus
  4. Crossover: combine characteristics dari 2 parents
  5. Mutation: random change untuk explore space
  6. Repeat sampai convergent
  
  Kecepatan: LAMBAT (O(generations × population × slots))
  Kompleksitas: HIGH
  Memori: HIGH
  
  Keuntungan:
  ✓ Global optimization (explore banyak area)
  ✓ Bisa handle constraint kompleks
  ✓ Adaptive (parameter bisa di-tune)
  ✓ Production-grade solution
  
  Kekurangan:
  ✗ Lambat (butuh multiple minutes)
  ✗ Non-deterministic (hasil beda per run)
  ✗ Kompleks untuk debug
  ✗ Susah tune parameter

╔══════════════════════════════════════════════════════════════════════╗
║                     REKOMENDASI PENGGUNAAN                          ║
╚══════════════════════════════════════════════════════════════════════╝

Web Application / Real-time Response:
  → Gunakan GREEDY (response dalam <500ms)

Batch Processing / Pembuatan Laporan Mingguan:
  → Gunakan GENETIC (quality lebih tinggi, waktu tidak kritis)

Mobile App / Limited Resource:
  → Gunakan GREEDY (hemat memory & CPU)

Academic Research / Publication:
  → GENETIC lebih impressive, GREEDY bisa sebagai baseline

User Preference (Frontend Option):
  → "Fast & Simple" → GREEDY
  → "Optimal & Detailed" → GENETIC
    """)


if __name__ == "__main__":
    print("✓ Greedy Algorithm Examples Module")
    print("\nRun one of these functions to test:")
    print("  - example_greedy_with_nutrition_service()")
    print("  - example_greedy_minimal()")
    print("  - comparison_algorithms()")
    
    # Print comparison untuk reference
    comparison_algorithms()

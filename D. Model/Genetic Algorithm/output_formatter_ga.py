"""
Enhanced Output Formatter untuk Genetic Algorithm Menu Generator
Menyediakan 3-phase structured output:
  Phase 1: User Profile (sebelum GA)
  Phase 2: GA Processing (log only)
  Phase 3: Menu Recommendations (terstruktur dengan pilihan)

Designed untuk Decision Support System dengan user-friendly presentation
"""

import json
from datetime import datetime


class OutputFormatterGA:
    """
    Enhanced output formatter untuk GA menu generator
    Struktur output yang clear, terurut, dan sesuai DSS paradigm
    """
    
    # === STYLE CONSTANTS ===
    LINE_CHAR = "═"
    LINE_SHORT = "─"
    WIDTH = 100
    
    @staticmethod
    def _create_line(length=None, char="─"):
        """Buat garis separator"""
        if length is None:
            length = OutputFormatterGA.WIDTH
        return char * length
    
    @staticmethod
    def _box_title(title, width=None):
        """Buat title dengan box decoration"""
        if width is None:
            width = OutputFormatterGA.WIDTH
        
        padding = (width - len(title) - 4) // 2
        return f"\n{'═' * width}\n  {title}\n{'═' * width}\n"
    
    # ========================================================================
    # PHASE 1: USER PROFILE DISPLAY
    # ========================================================================
    
    @staticmethod
    def display_phase1_user_profile(user_input, nutrition_result):
        """
        PHASE 1: Display user profile SEBELUM GA dijalankan
        
        Input:
          - user_input: dict dengan gender, age, weight, height, activity_factor, disease, food_preferences
          - nutrition_result: dict hasil calculate_nutrition_needs()
        
        Output terstruktur:
          1. Personal Information
          2. Anthropometric Measurements
          3. Energy Requirements
          4. Health & Preferences
          5. Nutrition Guidelines
        """
        
        if not nutrition_result['success']:
            print(f"\n[ERROR] Perhitungan gagal: {nutrition_result['error']}")
            return False
        
        anthro = nutrition_result['anthropometrics']
        energy = nutrition_result['energy']
        guidelines = nutrition_result['guidelines']
        
        # === HEADER ===
        print(OutputFormatterGA._box_title("PHASE 1: USER PROFILE & NUTRITION ASSESSMENT"))
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # === 1. PERSONAL INFORMATION ===
        print("┌─ [1] PERSONAL INFORMATION")
        print("├─" + "─" * 98)
        print(f"│  Gender:        {user_input['gender'].upper()}")
        print(f"│  Age:           {user_input['age']} years old ({anthro['age_range']})")
        print(f"│  Weight:        {user_input['weight']:.1f} kg")
        print(f"│  Height:        {user_input['height']:.1f} cm")
        print("└─" + "─" * 98 + "\n")
        
        # === 2. ANTHROPOMETRIC MEASUREMENTS ===
        print("┌─ [2] ANTHROPOMETRIC MEASUREMENTS (WHO Standards)")
        print("├─" + "─" * 98)
        
        bmi = anthro['bmi']
        bmi_category = anthro['bmi_category']
        
        # BMI Value & Category
        bmi_info = OutputFormatterGA._get_bmi_category_info(bmi, bmi_category)
        print(f"│  BMI Value:     {bmi:.1f} kg/m²")
        print(f"│  BMI Category:  {bmi_info['name']} ({bmi_info['range']})")
        
        # Color coding untuk BMI
        if bmi_category == 'normal':
            status = "✓ NORMAL"
        elif bmi_category == 'underweight':
            status = "⚠ UNDERWEIGHT"
        elif bmi_category == 'overweight':
            status = "⚠ OVERWEIGHT"
        else:
            status = "⚠ OBESITY"
        
        print(f"│                {status}")
        print(f"│")
        print(f"│  Ideal Body Weight (IBW): {anthro['bbi']:.1f} kg")
        print(f"│  Current vs IBW:          {OutputFormatterGA._get_weight_status(user_input['weight'], anthro['bbi'])}")
        print("└─" + "─" * 98 + "\n")
        
        # === 3. ENERGY REQUIREMENTS ===
        print("┌─ [3] ENERGY REQUIREMENTS (Daily Calorie Needs)")
        print("├─" + "─" * 98)
        print(f"│  Activity Level: {OutputFormatterGA._get_activity_label(user_input['activity_factor'])} (PAL: {user_input['activity_factor']:.3f})")
        print(f"│")
        print(f"│  Basal Metabolic Rate (BMR):  {energy['bmr']:.0f} kcal/day")
        print(f"│    → Minimum energy untuk fungsi tubuh (resting)")
        print(f"│")
        print(f"│  Total Daily Energy Expenditure (TDEE): {energy['tdee']:.0f} kcal/day")
        print(f"│    → Termasuk aktivitas fisik sehari-hari")
        print("└─" + "─" * 98 + "\n")
        
        # === 4. HEALTH & PREFERENCES ===
        print("┌─ [4] HEALTH CONDITIONS & FOOD PREFERENCES (Nutrition Filtering)")
        print("├─" + "─" * 98)
        
        # Health conditions
        disease_display = user_input['disease']
        if isinstance(disease_display, list):
            disease_display = ', '.join([d.upper() for d in disease_display])
        else:
            disease_display = disease_display.upper()
        
        print(f"│  Health Condition(s): {disease_display}")
        print(f"│    → Nutrition guidelines disesuaikan dengan kondisi kesehatan")
        print(f"│")
        
        # Food preferences
        if user_input['food_preferences']:
            prefs = ', '.join(user_input['food_preferences'])
            print(f"│  Cuisine Preference(s): {prefs}")
        else:
            print(f"│  Cuisine Preference(s): All cuisines included")
        
        print(f"│    → Menu akan difokuskan ke preferensi kuliner Anda")
        print("└─" + "─" * 98 + "\n")
        
        # === 5. NUTRITION GUIDELINES ===
        print("┌─ [5] NUTRITION GUIDELINES (Untuk Menu Optimization)")
        print("├─" * 99)
        print(f"│  Total Nutrients Evaluated: {guidelines['total_nutrients']}")
        print(f"├─ MACRONUTRIENTS (Energy sources):")
        print(f"│    • Protein (g):")
        print(f"│    • Carbohydrates (g):")
        print(f"│    • Fat (g):")
        print(f"│    • Fiber (g):")
        print(f"│")
        print(f"├─ MINERALS (Important for body functions):")
        print(f"│    • Sodium, Potassium, Calcium, Iron, Zinc, etc.")
        print(f"│")
        print(f"├─ VITAMINS (Essential micronutrients):")
        print(f"│    • Vitamin A, C, D, E, K, B Complex (B1, B6, B12), Folate, etc.")
        print(f"│")
        print(f"└─ Notes: Untuk detail spesifik per nutrient, konsultasikan dengan ahli gizi")
        print("└─" + "─" * 98 + "\n")
        
        # === SUMMARY ===
        print("┌─ [SUMMARY] Profil Anda untuk Optimasi Menu")
        print("├─" + "─" * 98)
        print(f"│  ✓ Kebutuhan energi harian:    ~{energy['tdee']:.0f} kcal")
        print(f"│  ✓ Kategori BMI:               {bmi_info['name']}")
        print(f"│  ✓ Kondisi kesehatan:          {disease_display}")
        print(f"│  ✓ Preferensi kuliner:         {prefs if user_input['food_preferences'] else 'Semua'}")
        print(f"│  ✓ Nutrient guidelines:        {guidelines['total_nutrients']} nutrients")
        print("└─" + "─" * 98 + "\n")
        
        print("Status: ✓ PROFIL SIAP")
        print("Next: GA akan mengoptimasi menu berdasarkan profil di atas\n")
        
        return True
    
    # ========================================================================
    # PHASE 2: GA PROCESSING DISPLAY
    # ========================================================================
    
    @staticmethod
    def display_phase2_ga_processing(ga_params):
        """
        PHASE 2: Display GA processing info (optional, bisa log saja)
        
        Input:
          - ga_params: dict dengan population_size, generations, constraints, etc
        """
        print(OutputFormatterGA._box_title("PHASE 2: GENETIC ALGORITHM OPTIMIZATION (Running...)"))
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        print("├─ GA PARAMETERS:")
        print(f"│  Population Size:     {ga_params.get('population_size', 'N/A')}")
        print(f"│  Generations:         {ga_params.get('generations', 'N/A')}")
        print(f"│  Optimization Target: Nutrient Compliance + Calorie Accuracy")
        print(f"│  Food Database:       {ga_params.get('food_count', 'N/A')} items available")
        print("│")
        print("├─ PROCESSING:")
        print("│  [In progress...] GA is searching optimal menu combinations")
        print("│  [This may take 10-30 seconds depending on database size]")
        print("└─ " + "─" * 97 + "\n")
    
    @staticmethod
    def display_phase2_ga_progress(generation, best_fitness, avg_fitness):
        """
        Display GA progress (per generation)
        Bisa di-call selama GA running untuk show progress
        """
        bar_length = 40
        progress = min(best_fitness / 100, 1.0)
        filled = int(bar_length * progress)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        print(f"│  [Gen {generation:3d}] Fitness: {best_fitness:6.2f} {bar} | Avg: {avg_fitness:6.2f}")
    
    @staticmethod
    def display_phase2_ga_complete(best_fitness, generations_run):
        """Display ketika GA selesai"""
        print("└─" + "─" * 97)
        print(f"\n✓ GA OPTIMIZATION COMPLETE")
        print(f"  Final Best Fitness: {best_fitness:.2f} / 100")
        print(f"  Generations Run:    {generations_run}")
        print(f"  Status:             Menu optimization successful\n")
    
    # ========================================================================
    # PHASE 3: MENU RECOMMENDATIONS
    # ========================================================================
    
    @staticmethod
    def display_phase3_menu_recommendations(menu_plan, user_tdee, user_input):
        """
        PHASE 3: Display recommended menu dalam format terstruktur
        
        Format:
          BREAKFAST
            Main Course (3 pilihan)
            Side Dish (3 pilihan)
            Drink (3 pilihan, optional)
          
          LUNCH
            ...
          
          DINNER
            ...
          
          SNACK
            (3 pilihan snack)
        
        Input:
          - menu_plan: MenuPlan object dengan breakfast, lunch, dinner
          - user_tdee: float, daily calorie target
          - user_input: dict dengan activity_factor, disease, dll
        """
        
        if menu_plan is None:
            print("\n[ERROR] Gagal generate menu")
            return False
        
        print(OutputFormatterGA._box_title("PHASE 3: MENU RECOMMENDATIONS"))
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        print("╔════════════════════════════════════════════════════════════════════════════════════════════════════╗")
        print("║                     PERSONALIZED NUTRITION MENU - GENETIC ALGORITHM                              ║")
        print("║                                    Complete Daily Plan                                            ║")
        print("╚════════════════════════════════════════════════════════════════════════════════════════════════════╝\n")
        
        # === 1. BREAKFAST ===
        print("┌─────────────────────────────────────────────────────────────────────────────────────────────────────")
        print("│ 🌅 BREAKFAST (Sarapan pukul 06:00-07:00)")
        print("├─────────────────────────────────────────────────────────────────────────────────────────────────────")
        
        if menu_plan.breakfast:
            OutputFormatterGA._display_meal_options(menu_plan.breakfast, 'breakfast')
        else:
            print("│ (No breakfast planned)")
        
        print("└─────────────────────────────────────────────────────────────────────────────────────────────────────\n")
        
        # === 2. LUNCH ===
        print("┌─────────────────────────────────────────────────────────────────────────────────────────────────────")
        print("│ 🍽️  LUNCH (Makan siang pukul 12:00-13:00)")
        print("├─────────────────────────────────────────────────────────────────────────────────────────────────────")
        
        if menu_plan.lunch:
            OutputFormatterGA._display_meal_options(menu_plan.lunch, 'lunch')
        else:
            print("│ (No lunch planned)")
        
        print("└─────────────────────────────────────────────────────────────────────────────────────────────────────\n")
        
        # === 3. DINNER ===
        print("┌─────────────────────────────────────────────────────────────────────────────────────────────────────")
        print("│ 🌙 DINNER (Makan malam pukul 18:00-19:00)")
        print("├─────────────────────────────────────────────────────────────────────────────────────────────────────")
        
        if menu_plan.dinner:
            OutputFormatterGA._display_meal_options(menu_plan.dinner, 'dinner')
        else:
            print("│ (No dinner planned)")
        
        print("└─────────────────────────────────────────────────────────────────────────────────────────────────────\n")
        
        # === 4. SNACK (jika ada) ===
        if menu_plan.snack:
            print("┌─────────────────────────────────────────────────────────────────────────────────────────────────────")
            print("│ 🍎 SNACK (Optional - Makanan ringan antara waktu makan)")
            print("├─────────────────────────────────────────────────────────────────────────────────────────────────────")
            OutputFormatterGA._display_meal_options(menu_plan.snack, 'snack')
            print("└─────────────────────────────────────────────────────────────────────────────────────────────────────\n")
        
        # === NUTRITION SUMMARY ===
        print("┌─────────────────────────────────────────────────────────────────────────────────────────────────────")
        print("│ 📊 DAILY NUTRITION SUMMARY")
        print("├─────────────────────────────────────────────────────────────────────────────────────────────────────")
        
        total_energy = menu_plan.total_energy_kcal
        energy_diff = total_energy - user_tdee
        energy_diff_pct = (energy_diff / user_tdee * 100) if user_tdee > 0 else 0
        
        print(f"│  ├─ Daily Energy Target (TDEE): {user_tdee:7.0f} kcal")
        print(f"│  ├─ Menu Total Energy:          {total_energy:7.0f} kcal")
        print(f"│  ├─ Difference:                 {energy_diff:+7.0f} kcal ({energy_diff_pct:+5.1f}%)")
        
        # Status indicator
        if abs(energy_diff) <= user_tdee * 0.1:
            energy_status = "✓ EXCELLENT (within ±10%)"
        elif abs(energy_diff) <= user_tdee * 0.15:
            energy_status = "✓ GOOD (within ±15%)"
        else:
            energy_status = "⚠ FAIR (outside target range)"
        
        print(f"│  └─ Status:                     {energy_status}")
        print("│")
        print(f"│  Total Macronutrients:")
        print(f"│  ├─ Protein:  {menu_plan.total_protein:6.1f} g")
        print(f"│  ├─ Carbs:    {menu_plan.total_carbs:6.1f} g")
        print(f"│  └─ Fat:      {menu_plan.total_fat:6.1f} g")
        print("└─────────────────────────────────────────────────────────────────────────────────────────────────────\n")
        
        # === FITNESS SCORE ===
        print("┌─────────────────────────────────────────────────────────────────────────────────────────────────────")
        print("│ 🎯 OPTIMIZATION QUALITY")
        print("├─────────────────────────────────────────────────────────────────────────────────────────────────────")
        
        fitness_score = menu_plan.ga_fitness_score
        
        if fitness_score > 80:
            quality = "EXCELLENT"
            quality_emoji = "🟢"
        elif fitness_score > 65:
            quality = "GOOD"
            quality_emoji = "🟢"
        elif fitness_score > 50:
            quality = "FAIR"
            quality_emoji = "🟡"
        else:
            quality = "NEEDS IMPROVEMENT"
            quality_emoji = "🔴"
        
        # Progress bar
        bar_length = 50
        filled = int(bar_length * fitness_score / 100)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        print(f"│  Fitness Score: {fitness_score:6.2f} / 100.00")
        print(f"│  {bar} {fitness_score:.1f}%")
        print(f"│  Quality: {quality_emoji} {quality}")
        print("│")
        print("│  Meaning:")
        print("│  • Fitness Score mengukur sebaik apa menu mengikuti:")
        print("│    - Nutrient compliance (60%)")
        print("│    - Energy accuracy (30%)")
        print("│    - Meal diversity (10%)")
        print("└─────────────────────────────────────────────────────────────────────────────────────────────────────\n")
        
        # === USER SELECTION GUIDE ===
        print("┌─────────────────────────────────────────────────────────────────────────────────────────────────────")
        print("│ 📋 HOW TO USE THIS MENU")
        print("├─────────────────────────────────────────────────────────────────────────────────────────────────────")
        print("│")
        print("│  For each meal (Breakfast, Lunch, Dinner), you can choose:")
        print("│")
        print("│    1. MAIN COURSE       → Select 1 from 3 options")
        print("│    2. SIDE DISH         → Select 1 from 3 options")
        print("│    3. DRINK (optional)  → Select 1 from available options (or skip)")
        print("│")
        print("│  The options are already optimized by GA for:")
        print("│    ✓ Meeting your daily nutrition needs")
        print("│    ✓ Matching your calorie target")
        print("│    ✓ Respecting your health conditions")
        print("│    ✓ Considering your cuisine preferences")
        print("│")
        print("│  Notes:")
        print("│    • You can swap foods between recommendations")
        print("│    • Portion sizes are suggestions (adjust based on appetite)")
        print("│    • Stay within calorie range for best results")
        print("│")
        print("└─────────────────────────────────────────────────────────────────────────────────────────────────────\n")
        
        # === DISCLAIMER ===
        print("┌─────────────────────────────────────────────────────────────────────────────────────────────────────")
        print("│ ⚠️  IMPORTANT DISCLAIMER")
        print("├─────────────────────────────────────────────────────────────────────────────────────────────────────")
        print("│")
        print("│  ✓ This is a PERSONALIZED RECOMMENDATION from AI optimization")
        print("│  ✓ Based on your profile: BMI, TDEE, health conditions, preferences")
        print("│  ✓ Designed as a TOOL for meal planning and nutrition awareness")
        print("│")
        print("│  ✗ NOT a medical prescription or clinical diagnosis")
        print("│  ✗ NOT a substitute for professional medical advice")
        print("│  ✗ Should be reviewed by healthcare professional for special cases")
        print("│")
        print("│  For medical nutrition therapy, consult a registered dietitian/nutritionist")
        print("│")
        print("└─────────────────────────────────────────────────────────────────────────────────────────────────────\n")
        
        print("✓ Menu generation complete!")
        print("═" * 100 + "\n")
        
        return True
    
    # ========================================================================
    # HELPER FUNCTIONS
    # ========================================================================
    
    @staticmethod
    def _display_meal_options(meal_obj, meal_type):
        """
        Display meal dengan 3 pilihan per kategori
        Format:
          MAIN COURSE OPTIONS (Choose 1):
          [1] Food A ...
          [2] Food B ...
          [3] Food C ...
        """
        
        if not meal_obj or not meal_obj.slots:
            print("│ (Empty meal)")
            return
        
        # Organize foods by category
        mains = []
        sides = []
        drinks = []
        
        for slot_type, slot in meal_obj.slots.items():
            if slot and slot.primary:
                if 'side' in slot_type:
                    sides.append(slot.primary)
                elif 'drink' in slot_type:
                    drinks.append(slot.primary)
                else:
                    mains.append(slot.primary)
        
        # === MAIN COURSE ===
        if mains:
            print("│")
            print("│  🍖 MAIN COURSE (Choose 1):")
            for i, food in enumerate(mains[:3], 1):  # Limit to 3
                print(f"│     [{i}] {food.name}")
                print(f"│         └─ {food.portion_gram:.0f}g | {food.energy_kcal:.0f} kcal | " + \
                      f"Protein {food.protein_g:.1f}g | Carbs {food.carbs_g:.1f}g | Fat {food.fat_g:.1f}g")
        
        # === SIDE DISH ===
        if sides:
            print("│")
            print("│  🥗 SIDE DISH (Choose 1):")
            for i, food in enumerate(sides[:3], 1):  # Limit to 3
                print(f"│     [{i}] {food.name}")
                print(f"│         └─ {food.portion_gram:.0f}g | {food.energy_kcal:.0f} kcal | " + \
                      f"Protein {food.protein_g:.1f}g | Carbs {food.carbs_g:.1f}g | Fat {food.fat_g:.1f}g")
        
        # === DRINK ===
        if drinks:
            print("│")
            print("│  🥤 DRINK (Optional - Choose 0 or 1):")
            for i, food in enumerate(drinks[:3], 1):  # Limit to 3
                print(f"│     [{i}] {food.name}")
                print(f"│         └─ {food.portion_gram:.0f}mL | {food.energy_kcal:.0f} kcal")
        
        # Meal summary
        print("│")
        print(f"│  📊 Meal Summary: {meal_obj.total_energy:.0f} kcal | " + \
              f"P:{meal_obj.total_protein:.1f}g C:{meal_obj.total_carbs:.1f}g F:{meal_obj.total_fat:.1f}g")
    
    @staticmethod
    def _get_bmi_category_info(bmi, category):
        """Dapatkan info lengkap BMI category"""
        categories = {
            'underweight': {'name': 'Underweight', 'range': '<18.5', 'color': '🔵'},
            'normal': {'name': 'Normal Weight', 'range': '18.5–24.9', 'color': '🟢'},
            'overweight': {'name': 'Overweight', 'range': '25–29.9', 'color': '🟡'},
            'obesity_class_1': {'name': 'Obesity Class I', 'range': '30–34.9', 'color': '🔴'},
            'obesity_class_2': {'name': 'Obesity Class II', 'range': '35–39.9', 'color': '🔴'},
            'obesity_class_3': {'name': 'Obesity Class III', 'range': '≥40', 'color': '🔴'},
        }
        
        return categories.get(category, {'name': 'Unknown', 'range': 'N/A', 'color': '⚪'})
    
    @staticmethod
    def _get_weight_status(current_weight, ibw):
        """Dapatkan status berat badan vs IBW"""
        diff = current_weight - ibw
        diff_pct = (diff / ibw) * 100
        
        if diff_pct < -10:
            return f"{abs(diff):.1f} kg less than IBW ({diff_pct:.1f}%) - Underweight"
        elif diff_pct > 10:
            return f"{abs(diff):.1f} kg more than IBW ({diff_pct:.1f}%) - Overweight"
        else:
            return f"Within ideal range (±10% IBW)"
    
    @staticmethod
    def _get_activity_label(activity_factor):
        """Dapatkan label activity level dari PAL value"""
        if activity_factor <= 1.55:
            return "Sedentary/Light Activity"
        elif activity_factor <= 1.85:
            return "Moderately Active"
        else:
            return "Vigorously Active"


if __name__ == "__main__":
    # Test the formatter
    print("OutputFormatterGA loaded successfully")
    print("Methods available:")
    print("  - display_phase1_user_profile(user_input, nutrition_result)")
    print("  - display_phase2_ga_processing(ga_params)")
    print("  - display_phase2_ga_progress(generation, best_fitness, avg_fitness)")
    print("  - display_phase2_ga_complete(best_fitness, generations_run)")
    print("  - display_phase3_menu_recommendations(menu_plan, user_tdee, user_input)")

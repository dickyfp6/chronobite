"""
Module untuk format dan display output hasil perhitungan
"""


class OutputFormatter:
    """Class untuk format output"""
    
    @staticmethod
    def display_welcome():
        """Display welcome message"""
        print("\n" + "="*70)
        print("WELCOME TO NUTRITION CALCULATION SYSTEM")
        print("="*70)
        print("Sistem ini akan membantu Anda menghitung:")
        print("1. Body Mass Index (BMI)")
        print("2. Berat Badan Ideal (BBI)")
        print("3. Basal Metabolic Rate (BMR)")
        print("4. Total Daily Energy Expenditure (TDEE)")
        print("5. Kebutuhan Nutrisi Berdasarkan Kondisi Kesehatan")
        print("="*70 + "\n")
    
    @staticmethod
    def display_user_data(user_data):
        """Display input data user"""
        print("\n" + "="*70)
        print("DATA YANG ANDA MASUKKAN")
        print("="*70)
        
        gender_text = "Laki-laki" if user_data['gender'] == 'M' else "Perempuan"
        
        print(f"Jenis Kelamin      : {gender_text}")
        print(f"Usia               : {user_data['age']} tahun")
        print(f"Berat Badan        : {user_data['weight']} kg")
        print(f"Tinggi Badan       : {user_data['height']} cm")
        print(f"Faktor Aktivitas   : {user_data['activity_factor']}")
        disease_val = user_data['disease']
        disease_text = ", ".join(d.upper() for d in disease_val) if isinstance(disease_val, list) else disease_val.upper()
        print(f"Kondisi Kesehatan  : {disease_text}")
        if user_data['food_preferences']:
            print(f"Preferensi Makanan : {', '.join(user_data['food_preferences'])}")
        print("="*70 + "\n")
    
    @staticmethod
    def display_calculation_results(nutrition_results):
        """Display hasil perhitungan antropometri & energi"""
        print("\n" + "="*70)
        print("HASIL PERHITUNGAN")
        print("="*70)
        
        print(f"\nAnthropometric Measurements:")
        print(f"  BMI (Body Mass Index)        : {nutrition_results['bmi']} ({nutrition_results['bmi_category']})")
        print(f"  BBI (Berat Badan Ideal)     : {nutrition_results['bbi']} kg")
        print(f"  Age Classification          : {nutrition_results['age_label']} ({nutrition_results['age_range']})")
        
        print(f"\nEnergy Expenditure:")
        print(f"  BMR (Basal Metabolic Rate)  : {nutrition_results['bmr']} kcal/hari")
        print(f"  TDEE (Total Daily Exp.)     : {nutrition_results['tdee']} kcal/hari")
        print("="*70 + "\n")
    
    @staticmethod
    def display_summary(user_data, nutrition_results, guidelines_result):
        """Display ringkasan lengkap"""
        print("\n" + "="*70)
        print("RINGKASAN LENGKAP")
        print("="*70)
        
        print(f"\nProfil User:")
        print(f"  • Status BMI: {nutrition_results['bmi_category']}")
        print(f"  • Klasifikasi Usia: {nutrition_results['age_label']} ({nutrition_results['age_range']})")
        print(f"  • Kebutuhan Kalori: {nutrition_results['tdee']} kcal/hari")
        
        if guidelines_result and guidelines_result['guidelines']:
            print(f"\n  • Kondisi Kesehatan: {guidelines_result['disease'].upper()}")
            print(f"  • Total Nutrient Guidelines: {guidelines_result['total_guidelines']}")
            
            # Show sample key nutrients
            guidelines = guidelines_result['guidelines']
            key_nutrients = ['energy_kcal', 'carbohydrate_g', 'protein_g', 'fat_g']
            
            print(f"\n  Nutrient Highlights:")
            for nutrient in key_nutrients:
                if nutrient in guidelines:
                    constraint = guidelines[nutrient]
                    if constraint['constraint_type'] != 'unlimited':
                        print(f"    - {nutrient}: {constraint['min']:.1f} - {constraint['max']:.1f}")
        
        print("\n" + "="*70)
    
    @staticmethod
    def display_meal_distribution(meal_plan):
        """Display recommended meal distribution"""
        print("\n" + "="*70)
        print("REKOMENDASI PEMBAGIAN PORSI MAKANAN")
        print("="*70)
        
        dist = meal_plan['distribution']
        perc = meal_plan['percentages']
        
        total_tdee = meal_plan['total']
        print(f"\nBerdasarkan TDEE {total_tdee} kcal/hari:")
        print(f"\n  🌅 Breakfast: {dist['breakfast']:>7} kcal  ({perc['breakfast']})")  
        print(f"  🍽️  Lunch:    {dist['lunch']:>7} kcal  ({perc['lunch']})")
        print(f"  🌙 Dinner:   {dist['dinner']:>7} kcal  ({perc['dinner']})")
        print(f"  🍪 Snack:    {dist['snack']:>7} kcal  ({perc['snack']})")
        print(f"\n  📊 Total:    {total_tdee:>7} kcal  (100.00%)")
        print("\n" + "="*70 + "\n")
    
    @staticmethod
    def display_error(message):
        """Display error message"""
        print(f"\n[ERROR] ERROR: {message}\n")
    
    @staticmethod
    def display_success(message):
        """Display success message"""
        print(f"\n[OK] {message}\n")
    
    @staticmethod
    def display_info(message):
        """Display info message"""
        print(f"\nℹ {message}\n")

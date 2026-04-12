"""
Module untuk perhitungan BMI, BBI, TDEE, dan konversi guideline
"""

import math


class NutritionCalculator:
    """Class untuk semua perhitungan nutrisi"""
    
    @staticmethod
    def calculate_bmi(weight, height):
        """
        Hitung Body Mass Index
        
        Args:
            weight: float (kg)
            height: float (cm)
        
        Returns:
            dict dengan keys: value, category
        """
        height_m = height / 100
        bmi = weight / (height_m ** 2)
        
        if bmi < 18.5:
            category = "Underweight"
        elif bmi < 25:
            category = "Healthy Weight" # Sesuai gambar
        elif bmi < 30:
            category = "Overweight"
        elif bmi < 35:
            category = "Class 1 Obesity" # Tambahan sesuai gambar
        elif bmi < 40:
            category = "Class 2 Obesity" # Tambahan sesuai gambar
        else:
            category = "Class 3 Obesity (Severe Obesity)" # Tambahan sesuai gambar
        
        return {
            'value': round(bmi, 2),
            'category': category
        }
    
    @staticmethod
    def calculate_bbi(height):
        """
        Hitung Berat Badan Ideal (BBI) menggunakan target BMI 22
        Rumus: BBI = 22 * (height_in_meters ^ 2)
        
        Args:
            height: float (cm)
        
        Returns:
            float: Berat badan ideal (kg)
        """
        # Konversi tinggi dari cm ke meter
        height_m = height / 100
        
        # Hitung BBI
        bbi = 22 * (height_m ** 2)
        
        return round(bbi, 2)
    
    @staticmethod
    def calculate_bmr_harris_benedict(weight, height, age, gender):
        """
        Rumus Harris-Benedict untuk orang Sehat (Normal)
        
        Pria: BMR = 66,4730 + 13,7516 x BB + 5,0033 x TB – 6,7550 x usia
        Wanita: BMR = 655,0955 + 9,5634 x BB + 1,8496 x TB – 4,6756 x usia
        """
        if gender == 'M':
            bmr = 66.4730 + (13.7516 * weight) + (5.0033 * height) - (6.7550 * age)
        else:
            bmr = 655.0955 + (9.5634 * weight) + (1.8496 * height) - (4.6756 * age)
        return round(bmr, 2)

    @staticmethod
    def calculate_bmr_mifflin_st_jeor(weight, height, age, gender):
        """Rumus untuk orang Sakit (DM, Hipertensi, dll)"""
        if gender == 'M':
            bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
        else:
            bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
        return round(bmr, 2)

    @staticmethod
    def calculate_bmr(weight, height, age, gender, disease_status):
        """
        Logika Flow: Memilih rumus berdasarkan kondisi kesehatan.
        """
        if disease_status.lower() == 'normal':
            return NutritionCalculator.calculate_bmr_harris_benedict(weight, height, age, gender)
        else:
            return NutritionCalculator.calculate_bmr_mifflin_st_jeor(weight, height, age, gender)
    
    @staticmethod
    def calculate_tdee(bmr, activity_factor):
        """
        Hitung Total Daily Energy Expenditure
        TDEE = BMR * Activity Factor
        
        Args:
            bmr: float (hasil calculate_bmr)
            activity_factor: float (1.2-1.9)
        
        Returns:
            float: TDEE (kcal/hari)
        """
        tdee = bmr * activity_factor
        return round(tdee, 2)
    
    @staticmethod
    def classify_age_group(age):
        """
        Klasifikasi usia berdasarkan WHO (World Health Organization) guidelines
        
        Args:
            age: int (usia dalam tahun)
        
        Returns:
            dict dengan keys: 'group', 'label', 'age_range'
        """
        if age < 17 or age > 125:
            return {
                'group': 'invalid',
                'label': 'Invalid Age',
                'age_range': 'N/A'
            }
        elif age <= 65:
            return {
                'group': 'young_people',
                'label': 'Young People',
                'age_range': '18-65 years old'
            }
        elif age <= 79:
            return {
                'group': 'middle_aged',
                'label': 'Middle-Aged',
                'age_range': '66-79 years old'
            }
        elif age <= 99:
            return {
                'group': 'elderly',
                'label': 'Elderly People',
                'age_range': '80-99 years old'
            }
        else:
            return {
                'group': 'very_elderly',
                'label': 'Very Elderly',
                'age_range': '100+ years old'
            }
    
    @staticmethod
    def convert_guideline_value(min_val, max_val, basis, user_params):
        """
        Konversi nilai guideline berdasarkan basis
        
        Args:
            min_val: float atau str (nilai minimum)
            max_val: float atau str (nilai maximum)
            basis: str ('1', 'TDEE', 'BB', 'BBI')
            user_params: dict dengan keys: tdee, weight, bbi
        
        Returns:
            dict dengan keys: min_converted, max_converted, constraint_type
        """
        
        # Handle empty/missing values (unlimited)
        if not str(min_val) or not str(max_val) or str(min_val).strip() == '' or str(max_val).strip() == '':
            return {
                'min_converted': 0,
                'max_converted': float('inf'),
                'constraint_type': 'unlimited'
            }
        
        try:
            min_float = float(min_val)
            max_float = float(max_val)
        except (ValueError, TypeError):
            return {
                'min_converted': 0,
                'max_converted': float('inf'),
                'constraint_type': 'invalid'
            }
        
        # Basis: Absolute value (tidak dikonversi)
        if basis == '1' or basis == 1:
            return {
                'min_converted': min_float,
                'max_converted': max_float,
                'constraint_type': 'absolute'
            }
        
        # Basis: TDEE (multiply by TDEE)
        elif basis == 'TDEE':
            tdee = user_params.get('tdee', 2000)
            return {
                'min_converted': round(min_float * tdee, 2),
                'max_converted': round(max_float * tdee, 2),
                'constraint_type': 'tdee_based'
            }
        
        # Basis: BB (Berat Badan - multiply by weight)
        elif basis == 'BB':
            weight = user_params.get('weight', 70)
            return {
                'min_converted': round(min_float * weight, 2),
                'max_converted': round(max_float * weight, 2),
                'constraint_type': 'weight_based'
            }
        
        # Basis: BBI (Berat Badan Ideal - multiply by BBI)
        elif basis == 'BBI':
            bbi = user_params.get('bbi', 70)
            return {
                'min_converted': round(min_float * bbi, 2),
                'max_converted': round(max_float * bbi, 2),
                'constraint_type': 'bbi_based'
            }
        
        else:
            return {
                'min_converted': 0,
                'max_converted': float('inf'),
                'constraint_type': 'unknown'
            }


def calculate_user_nutrition_needs(user_data):
    """
    Main function untuk menghitung semua kebutuhan nutrisi user
    Sesuai Flow: Memilih BB vs BBI dan Rumus BMR berdasarkan kondisi user.
    """
    
    calc = NutritionCalculator()
    
    # 1. Hitung BMI (Body Mass Index)
    bmi_result = calc.calculate_bmi(user_data['weight'], user_data['height'])
    
    # 2. Hitung BBI (Berat Badan Ideal) - Menggunakan rumus BBI = 22 * H^2
    bbi = calc.calculate_bbi(user_data['height'])
    
    # 3. LOGIKA FLOW: Pilih BB yang akan digunakan untuk BMR
    # Jika BMI masuk kategori 'Healthy Weight', gunakan BB Aktual.
    # Selain itu (Underweight/Obese), gunakan BBI (Ideal Weight).
    if bmi_result['category'] == "Healthy Weight":
        weight_for_bmr = user_data['weight']
    else:
        weight_for_bmr = bbi
    
    # 4. Hitung BMR (Basal Metabolic Rate)
    # Sekarang memasukkan weight_for_bmr dan status penyakit ke switcher BMR
    bmr = calc.calculate_bmr(
        weight_for_bmr,
        user_data['height'],
        user_data['age'],
        user_data['gender'],
        user_data['disease']
    )
    
    # 5. Hitung TDEE
    tdee = calc.calculate_tdee(bmr, user_data['activity_factor'])
    
    results = {
        'user_data': user_data,
        'bmi': bmi_result['value'],
        'bmi_category': bmi_result['category'],
        'bbi': bbi,
        'weight_used_for_bmr': weight_for_bmr, # Catatan BB mana yang dipakai
        'bmr': bmr,
        'tdee': tdee,
        'user_params': {
            'tdee': tdee,
            'weight': user_data['weight'],
            'bbi': bbi
        }
    }
    
    return results
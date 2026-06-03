"""
Module untuk perhitungan BMI, BBI, TDEE, dan konversi guideline
"""

import math
import pandas as pd


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
            category = "Healthy Weight"
        elif bmi < 30:
            category = "Overweight"
        elif bmi < 35:
            category = "Class 1 Obesity"
        elif bmi < 40:
            category = "Class 2 Obesity"
        else:
            category = "Class 3 Obesity (Severe Obesity)"
        
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
        height_m = height / 100
        bbi = 22 * (height_m ** 2)
        return round(bbi, 2)
    
    @staticmethod
    def calculate_bmr_harris_benedict(weight, height, age, gender):
        """
        Rumus Harris-Benedict untuk orang Sehat (Normal)
        
        Pria:   BMR = 66,4730 + 13,7516 x BB + 5,0033 x TB – 6,7550 x usia
        Wanita: BMR = 655,0955 + 9,5634 x BB + 1,8496 x TB – 4,6756 x usia
        """
        if gender == 'M':
            bmr = 66.4730 + (13.7516 * weight) + (5.0033 * height) - (6.7550 * age)
        else:
            bmr = 655.0955 + (9.5634 * weight) + (1.8496 * height) - (4.6756 * age)
        return round(bmr, 2)

    @staticmethod
    def calculate_bmr_mifflin_st_jeor(weight, height, age, gender):
        """Rumus Mifflin-St Jeor untuk orang Sakit (DM, Hipertensi, dll)"""
        if gender == 'M':
            bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
        else:
            bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
        return round(bmr, 2)

    @staticmethod
    def calculate_bmr(weight, height, age, gender, disease_status):
        """
        Logika Flow: Memilih rumus berdasarkan kondisi kesehatan.
        - Normal  → Harris-Benedict
        - Sakit   → Mifflin-St Jeor
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
            activity_factor: float (1.4–2.2)
        
        Returns:
            float: TDEE (kcal/hari)
        """
        tdee = bmr * activity_factor
        return round(tdee, 2)
    
    @staticmethod
    def calculate_meal_distribution(tdee):
        """
        Hitung pembagian porsi TDEE per waktu makan (Total 100%)
        
        Breakfast : 20–25% → 23.75%
        Lunch     : 30–35% → 33.75%
        Dinner    : 25–30% → 28.75%
        Snack     : 10–15% → 13.75%
        
        Args:
            tdee: float (total daily energy expenditure)
        
        Returns:
            dict dengan kalori untuk setiap waktu makan
        """
        distribution = {
            'breakfast': round(tdee * 0.2375, 2),
            'lunch':     round(tdee * 0.3375, 2),
            'dinner':    round(tdee * 0.2875, 2),
            'snack':     round(tdee * 0.1375, 2),
        }
        return distribution
    
    @staticmethod
    def classify_age_group(age):
        """
        Klasifikasi usia berdasarkan WHO (World Health Organization) guidelines
        
        Args:
            age: int (usia dalam tahun)
        
        Returns:
            dict dengan keys: 'group', 'label', 'age_range'
        """
        if age < 17 or age > 100:
            return {'group': 'invalid',      'label': 'Invalid Age',    'age_range': 'N/A'}
        elif age <= 65:
            return {'group': 'young_people', 'label': 'Young People',   'age_range': '18-65 years old'}
        elif age <= 79:
            return {'group': 'middle_aged',  'label': 'Middle-Aged',    'age_range': '66-79 years old'}
        elif age <= 99:
            return {'group': 'elderly',      'label': 'Elderly People', 'age_range': '80-99 years old'}
        else:
            return {'group': 'very_elderly', 'label': 'Very Elderly',   'age_range': '100+ years old'}
    
    @staticmethod
    def _get_tdee_divisor(nutrient_name):
        """
        Tentukan kalori divisor untuk konversi TDEE → gram.
        
        - Fat (lemak)         : 1g = 9 kcal  → divisor 9
        - Carbs / Protein     : 1g = 4 kcal  → divisor 4
        - Energy / lainnya    : sudah dalam kcal → divisor 1
        
        Args:
            nutrient_name: str (nama kolom nutrient dari guideline)
        
        Returns:
            int: 1, 4, atau 9
        """
        fat_nutrients = [
            'fat_g',
            'saturated_fat_g',
            'trans_fat_g',
            'polyunsaturated_fat_g',   # ← dari File 2
            'monounsaturated_fat_g',   # ← dari File 2
        ]
        carb_protein_nutrients = [
            'carbohydrate_g',
            'protein_g',
            'fiber_g',
        ]

        if nutrient_name in fat_nutrients:
            return 9
        elif nutrient_name in carb_protein_nutrients:
            return 4
        else:
            # energy_kcal dan nutrient lain yang sudah dalam satuan absolut
            return 1
    
    @staticmethod
    def convert_guideline_value(min_val, max_val, basis, user_params, nutrient_name=None):
        """
        Konversi nilai guideline berdasarkan basis
        
        Args:
            min_val       : float atau str (nilai minimum)
            max_val       : float atau str (nilai maximum)
            basis         : str ('1', 'TDEE', 'BB', 'BBI')
            user_params   : dict dengan keys: tdee, weight, bbi
            nutrient_name : str (optional, digunakan untuk TDEE conversion)
        
        Returns:
            dict dengan keys: min_converted, max_converted, constraint_type
        """
        
        def _to_float_or_none(value):
            if value is None or pd.isna(value):
                return None
            if isinstance(value, str) and value.strip() == '':
                return None
            return float(value)

        try:
            min_float = _to_float_or_none(min_val)
            max_float = _to_float_or_none(max_val)
        except (ValueError, TypeError):
            return {
                'min_converted': 0,
                'max_converted': float('inf'),
                'constraint_type': 'invalid'
            }

        # Jika kedua bound kosong → tidak ada batasan
        if min_float is None and max_float is None:
            return {
                'min_converted': 0,
                'max_converted': float('inf'),
                'constraint_type': 'unlimited'
            }

        # ── Basis: Absolute (tidak dikonversi) ──────────────────────────────
        if basis == '1' or basis == 1:
            return {
                'min_converted': min_float if min_float is not None else 0,
                'max_converted': max_float if max_float is not None else float('inf'),
                'constraint_type': (
                    'absolute' if min_float is not None and max_float is not None
                    else 'partial_absolute'
                )
            }
        
        # ── Basis: TDEE → konversi ke gram menggunakan divisor per nutrient ──
        elif basis == 'TDEE':
            tdee = user_params.get('tdee', 2000)
            divisor = NutritionCalculator._get_tdee_divisor(nutrient_name) if nutrient_name else 4

            min_converted = round(min_float * tdee / divisor, 2) if min_float is not None else 0
            max_converted = round(max_float * tdee / divisor, 2) if max_float is not None else float('inf')

            return {
                'min_converted': min_converted,
                'max_converted': max_converted,
                'constraint_type': (
                    'tdee_based' if min_float is not None and max_float is not None
                    else 'partial_tdee_based'
                )
            }
        
        # ── Basis: BB (Berat Badan aktual) ───────────────────────────────────
        elif basis == 'BB':
            weight = user_params.get('weight', 70)
            return {
                'min_converted': round(min_float * weight, 2) if min_float is not None else 0,
                'max_converted': round(max_float * weight, 2) if max_float is not None else float('inf'),
                'constraint_type': (
                    'weight_based' if min_float is not None and max_float is not None
                    else 'partial_weight_based'
                )
            }
        
        # ── Basis: BBI (Berat Badan Ideal) ───────────────────────────────────
        elif basis == 'BBI':
            bbi = user_params.get('bbi', 70)
            return {
                'min_converted': round(min_float * bbi, 2) if min_float is not None else 0,
                'max_converted': round(max_float * bbi, 2) if max_float is not None else float('inf'),
                'constraint_type': (
                    'bbi_based' if min_float is not None and max_float is not None
                    else 'partial_bbi_based'
                )
            }
        
        else:
            return {
                'min_converted': 0,
                'max_converted': float('inf'),
                'constraint_type': 'unknown'
            }


def calculate_user_nutrition_needs(user_data):
    """
    Main function untuk menghitung semua kebutuhan nutrisi user.
    
    Flow:
      1. Hitung BMI
      2. Hitung BBI
      3. Pilih BB untuk BMR: BB aktual jika Healthy Weight, BBI jika tidak
      4. Hitung BMR (Harris-Benedict / Mifflin-St Jeor sesuai kondisi)
      5. Hitung TDEE
    
    Args:
        user_data: dict dengan keys:
            weight, height, age, gender, disease, activity_factor
    
    Returns:
        dict hasil kalkulasi lengkap
    """
    calc = NutritionCalculator()
    
    # 1. BMI
    bmi_result = calc.calculate_bmi(user_data['weight'], user_data['height'])
    
    # 2. BBI
    bbi = calc.calculate_bbi(user_data['height'])
    
    # 3. Pilih BB untuk BMR
    if bmi_result['category'] == "Healthy Weight":
        weight_for_bmr = user_data['weight']   # gunakan BB aktual
    else:
        weight_for_bmr = bbi                   # gunakan BBI
    
    # 4. BMR
    bmr = calc.calculate_bmr(
        weight_for_bmr,
        user_data['height'],
        user_data['age'],
        user_data['gender'],
        user_data['disease']
    )
    
    # 5. TDEE
    tdee = calc.calculate_tdee(bmr, user_data['activity_factor'])
    
    return {
        'user_data':          user_data,
        'bmi':                bmi_result['value'],
        'bmi_category':       bmi_result['category'],
        'bbi':                bbi,
        'weight_used_for_bmr': weight_for_bmr,
        'bmr':                bmr,
        'tdee':               tdee,
        'user_params': {
            'tdee':   tdee,
            'weight': user_data['weight'],
            'bbi':    bbi,
        }
    }
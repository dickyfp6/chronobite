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
            category = "Normal"
        elif bmi < 30:
            category = "Overweight"
        else:
            category = "Obese"
        
        return {
            'value': round(bmi, 2),
            'category': category
        }
    
    @staticmethod
    def calculate_bbi(height, gender):
        """
        Hitung Berat Badan Ideal menggunakan rumus Broca
        BBI = (height - 100) * 0.9 untuk pria
        BBI = (height - 100) * 0.85 untuk wanita
        
        Args:
            height: float (cm)
            gender: 'M' atau 'F'
        
        Returns:
            float: Berat badan ideal (kg)
        """
        height_cm = height - 100
        
        if gender == 'M':
            bbi = height_cm * 0.9
        else:  # gender == 'F'
            bbi = height_cm * 0.85
        
        return round(bbi, 2)
    
    @staticmethod
    def calculate_bmr(weight, height, age, gender):
        """
        Hitung Basal Metabolic Rate menggunakan Harris-Benedict equation
        
        Args:
            weight: float (kg)
            height: float (cm)
            age: int (tahun)
            gender: 'M' atau 'F'
        
        Returns:
            float: BMR (kcal/hari)
        """
        if gender == 'M':
            bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
        else:  # gender == 'F'
            bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
        
        return round(bmr, 2)
    
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
    
    Args:
        user_data: dict dari input_handler.get_user_input()
    
    Returns:
        dict dengan semua hasil perhitungan
    """
    
    calc = NutritionCalculator()
    
    # Hitung BMI
    bmi_result = calc.calculate_bmi(user_data['weight'], user_data['height'])
    
    # Hitung BBI
    bbi = calc.calculate_bbi(user_data['height'], user_data['gender'])
    
    # Hitung BMR
    bmr = calc.calculate_bmr(
        user_data['weight'],
        user_data['height'],
        user_data['age'],
        user_data['gender']
    )
    
    # Hitung TDEE
    tdee = calc.calculate_tdee(bmr, user_data['activity_factor'])
    
    results = {
        'user_data': user_data,
        'bmi': bmi_result['value'],
        'bmi_category': bmi_result['category'],
        'bbi': bbi,
        'bmr': bmr,
        'tdee': tdee,
        'user_params': {
            'tdee': tdee,
            'weight': user_data['weight'],
            'bbi': bbi
        }
    }
    
    return results

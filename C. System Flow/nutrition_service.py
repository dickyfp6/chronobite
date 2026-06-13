"""
Nutrition Calculation Service
Consolidated file untuk orchestrate semua input, calculations, dan output
Designed untuk easy integration dengan Genetic Algorithm dan Greedy Algorithm

Usage:
    from nutrition_service import NutritionService
    
    service = NutritionService()
    result = service.calculate_nutrition_needs(user_data)
    # result['guidelines'] untuk constraint GA/Greedy
    # result['food_df'] untuk candidate items
"""

import sys
import os
import pandas as pd

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.calculations import NutritionCalculator
from data_loader import GuidelineLoader


class NutritionService:
    """
    Centralized service untuk semua nutrition calculations
    Interface tunggal untuk integrate dengan algorithms
    """
    
    def __init__(self):
        """Initialize service dengan loader"""
        self.calculator = NutritionCalculator()
        self.guideline_loader = GuidelineLoader()
        self.guideline_loader.load_food_data()
        
        self.last_result = None
    
    def calculate_nutrition_needs(self, user_input):
        """
        Main function: Calculate semua kebutuhan nutrisi user
        
        Args:
            user_input: dict dengan keys:
                - gender: 'M' atau 'F'
                - age: int (14-100)
                - weight: float (kg)
                - height: float (cm)
                - activity_factor: float (1.4-2.2)
                - disease: str or list (normal, dm2, hypertension, cvd, cholesterol, ckd)
                           jika list: merge semua disease guidelines (min terendah, max tertinggi)
                - food_preferences: list (optional, default: [])
        
        Returns:
            dict dengan struktur:
            {
                'success': bool,
                'user_input': dict (user data yang diinput),
                'anthropometrics': {
                    'bmi': float,
                    'bmi_category': str,
                    'bbi': float,
                    'age_group': str (minors/young_people/middle_aged/elderly/very_elderly),
                    'age_label': str (WHO classification label),
                    'age_range': str (age range description)
                },
                'energy': {
                    'bmr': float,
                    'tdee': float
                },
                'guidelines': {
                    'disease': str,
                    'nutrients': {
                        'nutrient_name': {
                            'min': float,
                            'max': float,
                            'basis': str,
                            'unit': str (inferred)
                        },
                        ...
                    }
                },
                'food_data': {
                    'total_items': int,
                    'by_cuisine': {...},
                    'dataframe': pd.DataFrame (full food data)
                },
                'user_params': {
                    'tdee': float,
                    'weight': float,
                    'bbi': float,
                    'energy_target': float
                },
                'error': None atau str (jika ada error)
            }
        """
        
        result = {
            'success': False,
            'user_input': user_input,
            'anthropometrics': None,
            'energy': None,
            'guidelines': None,
            'food_data': None,
            'user_params': None,
            'error': None
        }
        
        try:
            # 1. Extract & validate input
            gender = user_input.get('gender', 'M')
            age = int(user_input.get('age', 25))
            weight = float(user_input.get('weight', 70))
            height = float(user_input.get('height', 170))
            activity_factor = float(user_input.get('activity_factor', 1.375))
            disease = user_input.get('disease', 'normal')
            food_preferences = user_input.get('food_preferences', [])
            
            # Convert disease to list jika string
            if isinstance(disease, str):
                disease = [disease] if disease else ['normal']
            elif not isinstance(disease, list):
                disease = ['normal']
            
            # Remove empty strings, strip, dan remove duplicates
            disease = [d.strip() for d in disease if d and d.strip()]
            disease = list(set(disease))  # Remove duplicates
            
            if not disease:
                disease = ['normal']
            
            # Validate ranges
            if not (18 <= age <= 100):
                raise ValueError(f"Age must be 18-100, got {age}")
            if weight <= 0 or height <= 0:
                raise ValueError("Weight and height must be positive")
            if not (1.4 <= activity_factor <= 2.2):
                raise ValueError(f"Activity factor must be 1.4-2.2, got {activity_factor}")
            
            valid_diseases = ['normal', 'dm2', 'hypertension', 'cvd', 'cholesterol', 'ckd']
            for d in disease:
                if d not in valid_diseases:
                    raise ValueError(f"Disease must be one of {valid_diseases}, got {d}")
            
            # 2. Calculate anthropometrics
            bmi_calc = self.calculator.calculate_bmi(weight, height)
            bbi = self.calculator.calculate_bbi(height, gender)
            age_group = self.calculator.classify_age_group(age)
            
            result['anthropometrics'] = {
                'bmi': bmi_calc['value'],
                'bmi_category': bmi_calc['category'],
                'bbi': bbi,
                'age_group': age_group['group'],
                'age_label': age_group['label'],
                'age_range': age_group['age_range']
            }
            
            # 3. Calculate energy (BMR, TDEE)
            # LOGIC: Pilih BB untuk BMR berdasarkan BMI category
            # - Jika BMI Normal (Healthy Weight): gunakan BB aktual
            # - Selain itu (Underweight/Obese): gunakan BBI (Ideal Weight)
            weight_for_bmr = weight if bmi_calc['category'] == "Healthy Weight" else bbi

            disease_status_for_bmr = 'normal' if set(disease) == {'normal'} else 'diseased'
            bmr = self.calculator.calculate_bmr(weight_for_bmr, height, age, gender, disease_status_for_bmr)
            tdee = self.calculator.calculate_tdee(bmr, activity_factor)
            
            result['energy'] = {
                'bmr': bmr,
                'tdee': tdee
            }
            
            # 4. Load & merge guidelines (untuk multiple diseases)
            user_params = {
                'tdee': tdee,
                'weight': weight,
                'bbi': bbi
            }
            
            # Merge disease guidelines (dengan user_params untuk konversi basis yang tepat)
            merged_guidelines = self.guideline_loader.merge_disease_guidelines(
                disease, age, gender, user_params=user_params
            )
            
            if not merged_guidelines:
                raise ValueError(f"No guideline found for {disease}, age {age}")
            
            # BUG FIX: Clamp TDEE according to disease-specific energy_kcal guidelines (min/max boundaries)
            # If Kal. User A > Min-Max, maka Kal. A=Max
            # If Kal. User A ~ Min-Max, maka Kal. A=Kal. A
            # If Kal. User A < Min-Max, maka Kal. A=Min
            energy_guideline = merged_guidelines.get('energy_kcal')
            if energy_guideline:
                energy_min = energy_guideline.get('min')
                energy_max = energy_guideline.get('max')
                
                original_tdee = tdee
                
                if energy_min is not None and energy_min > 0:
                    if tdee < energy_min:
                        tdee = energy_min
                if energy_max is not None and energy_max < float('inf'):
                    if tdee > energy_max:
                        tdee = energy_max
                
                if tdee != original_tdee:
                    print(f"[INFO] TDEE clamped by disease guidelines: {original_tdee:.2f} -> {tdee:.2f}")
                    # Update result['energy'] to reflect clamped tdee
                    result['energy']['tdee'] = tdee
                    # Update user_params tdee
                    user_params['tdee'] = tdee
                    # Re-run merge_disease_guidelines so other relative macronutrients (e.g. basis: 'TDEE')
                    # are correctly converted using the clamped tdee value as their basis.
                    merged_guidelines = self.guideline_loader.merge_disease_guidelines(
                        disease, age, gender, user_params=user_params
                    )
            
            # Get DRI untuk fallback
            dri_row = self.guideline_loader.get_dri_by_age_gender(age, gender)
            
            # Process merged guideline nutrients (nilai SUDAH dikonversi di merge_disease_guidelines)
            nutrients_dict = {}
            for nutrient, guideline_data in merged_guidelines.items():
                tipe = guideline_data.get('tipe', 'range')  # Get tipe from guideline
                diseases_list = guideline_data['diseases']
                
                # Nilai sudah dikonversi di merge_disease_guidelines, ambil langsung
                min_converted = guideline_data['min']
                max_converted = guideline_data['max']
                constraint_type = 'absolute'  # semua sudah dalam unit aktual
                
                # Infer unit from nutrient name
                unit = self._infer_unit(nutrient)
                
                # Determine HARD/SOFT based on tipe column
                # tipe in ["range", "max"] → HARD constraint (disease guideline)
                # otherwise → SOFT constraint (DRI micronutrient)
                hard_soft_type = 'HARD' if tipe in ['range', 'max'] else 'SOFT'
                
                nutrients_dict[nutrient] = {
                    'min': min_converted,
                    'max': max_converted,
                    'basis': '1',              # sudah dikonversi, basis = absolut
                    'tipe': tipe,              # Store original tipe from CSV
                    'constraint_type': constraint_type,  # nilai sudah absolut
                    'hard_soft_type': hard_soft_type,  # HARD or SOFT for GA purposes
                    'unit': unit,
                    'source': 'guideline',
                    'diseases': diseases_list  # Track which diseases contributed
                }
            
            # Add DRI fallback untuk nutrients yang tidak ada di guideline
            # Berlaku untuk semua kondisi (normal maupun sakit) karena guideline.csv
            # hanya mencakup hard constraint makronutrient, sedangkan micronutrient
            # (vitamin, mineral, dll) diambil dari dri_micro.csv sebagai SOFT constraint
            if dri_row is not None:
                dri_columns = dri_row.keys()
                for dri_col in dri_columns:
                    # Skip non-nutrient columns
                    if dri_col in ['age_min', 'age_max', 'gender']:
                        continue
                    
                    nutrient_key = dri_col
                    
                    # Check if this nutrient already exists di guideline
                    if nutrient_key not in nutrients_dict:
                        dri_value = dri_row[dri_col]
                        
                        # Only add jika value tidak null/NaN
                        if pd.notna(dri_value):
                            unit = self._infer_unit(nutrient_key)
                            nutrients_dict[nutrient_key] = {
                                'min': float(dri_value),
                                'max': float('inf'),  # DRI is minimum, not exact target; excess micronutrients are safe
                                'basis': 'DRI',
                                'tipe': 'dri',
                                'constraint_type': 'dri_micronutrient',
                                'hard_soft_type': 'SOFT',  # DRI nutrients are always SOFT
                                'unit': unit,
                                'source': 'DRI fallback'
                            }
            
            result['guidelines'] = {
                'disease': disease,
                'nutrients': nutrients_dict,
                'total_nutrients': len(nutrients_dict)
            }
            
            # 5. Load food data
            food_df = self.guideline_loader.food_df
            if food_df is not None:
                # Count by cuisine
                cuisine_counts = {}
                if 'cuisine' in food_df.columns:
                    cuisine_counts = food_df['cuisine'].value_counts().to_dict()
                    
                    # Filter by preferences jika ada
                    if food_preferences:
                        normalized_prefs = [p.title() if isinstance(p, str) else p for p in food_preferences]
                        filtered_df = food_df[food_df['cuisine'].isin(normalized_prefs)].copy()
                    else:
                        filtered_df = food_df.copy()
                else:
                    filtered_df = food_df.copy()
                
                result['food_data'] = {
                    'total_items': len(food_df),
                    'filtered_items': len(filtered_df),
                    'by_cuisine': cuisine_counts,
                    'preferences': food_preferences,
                    'dataframe': filtered_df
                }
            
            # 6. Calculate meal distribution
            meal_distribution = self.calculator.calculate_meal_distribution(tdee)
            
            result['meal_plan'] = {
                'distribution': meal_distribution,
                'total': tdee,
                'percentages': {
                    'breakfast': '23.75%',
                    'lunch': '33.75%',
                    'dinner': '28.75%',
                    'snack': '13.75%'
                }
            }
            
            # 7. Store user params untuk algorithm
            result['user_params'] = {
                'tdee': tdee,
                'weight': weight,
                'bbi': bbi,
                'energy_target': tdee,
                'age': age,
                'gender': gender,
                'disease': disease,
                'meal_distribution': meal_distribution
            }
            
            result['success'] = True
            self.last_result = result
            
        except Exception as e:
            result['error'] = str(e)
            result['success'] = False
        
        return result
    
    @staticmethod
    def _infer_unit(nutrient_name):
        """Infer unit dari nutrient name"""
        nutrient_lower = nutrient_name.lower()
        
        if 'energy' in nutrient_lower or 'kcal' in nutrient_lower:
            return 'kcal'
        elif 'water' in nutrient_lower:
            return 'g'
        elif '_g' in nutrient_lower or 'carbo' in nutrient_lower or 'protein' in nutrient_lower or 'fat' in nutrient_lower:
            return 'g'
        elif '_mg' in nutrient_lower:
            return 'mg'
        elif '_mcg' in nutrient_lower or '_ug' in nutrient_lower:
            return 'mcg'
        else:
            return 'unit'
    
    def validate_menu(self, menu_items, guidelines):
        """
        Validate menu terhadap guidelines
        
        Args:
            menu_items: list of food items (dari GA/Greedy)
            guidelines: dict dari result['guidelines']
        
        Returns:
            dict dengan validation result
        """
        if not menu_items:
            return {
                'is_valid': False,
                'violations': ['Menu is empty'],
                'nutrient_totals': {}
            }

        # Build nutrient totals from menu item values.
        nutrient_totals = {}
        for item in menu_items:
            if not isinstance(item, dict):
                continue
            for key, value in item.items():
                if key in ['food_name', 'name', 'meal', 'index', 'fdc_id', 'cuisine', 'cuisine_label', 'food_group', 'consumption_label']:
                    continue
                try:
                    nutrient_totals[key] = nutrient_totals.get(key, 0.0) + float(value)
                except (TypeError, ValueError):
                    continue

        violations = []
        guideline_dict = guidelines.get('nutrients', guidelines) if isinstance(guidelines, dict) else {}

        for nutrient, constraint in guideline_dict.items():
            if not isinstance(constraint, dict):
                continue
            if constraint.get('constraint_type') == 'unlimited':
                continue

            actual = nutrient_totals.get(nutrient, 0.0)
            min_v = constraint.get('min', 0)
            max_v = constraint.get('max', float('inf'))

            if min_v is not None and actual < min_v:
                violations.append(f"{nutrient}: below minimum ({actual:.2f} < {min_v:.2f})")
            if max_v is not None and actual > max_v:
                violations.append(f"{nutrient}: above maximum ({actual:.2f} > {max_v:.2f})")

        return {
            'is_valid': len(violations) == 0,
            'violations': violations,
            'nutrient_totals': nutrient_totals
        }
    
    def get_last_result(self):
        """Get last calculation result"""
        return self.last_result
    
    def print_summary(self, result):
        """Print user-friendly summary"""
        if not result['success']:
            print(f"[ERROR] Error: {result['error']}")
            return
        
        print("\n" + "="*70)
        print("NUTRITION CALCULATION SUMMARY")
        print("="*70)
        
        # User data
        user = result['user_input']
        print(f"\nUser Profile:")
        print(f"  Gender: {user.get('gender')}")
        print(f"  Age: {user.get('age')}")
        print(f"  Weight: {user.get('weight')} kg")
        print(f"  Height: {user.get('height')} cm")
        print(f"  Disease: {user.get('disease')}")
        
        # Anthropometrics
        anthro = result['anthropometrics']
        print(f"\nAnthropometrics:")
        print(f"  BMI: {anthro['bmi']} ({anthro['bmi_category']})")
        print(f"  BBI: {anthro['bbi']} kg")
        print(f"  Age Group: {anthro['age_label']} ({anthro['age_range']})")
        
        # Energy
        energy = result['energy']
        print(f"\nEnergy Expenditure:")
        print(f"  BMR: {energy['bmr']} kcal/day")
        print(f"  TDEE: {energy['tdee']} kcal/day")
        
        # Guidelines
        guidelines = result['guidelines']
        print(f"\nNutrient Guidelines ({guidelines['total_nutrients']} items):")
        
        # Separate by source
        guideline_nutrients = []
        dri_nutrients = []
        
        for nutrient, constraint in guidelines['nutrients'].items():
            source = constraint.get('source', 'guideline')
            if source == 'DRI fallback':
                dri_nutrients.append((nutrient, constraint))
            else:
                guideline_nutrients.append((nutrient, constraint))
        
        # Display guideline nutrients
        if guideline_nutrients:
            print(f"\n  From Disease Guideline ({len(guideline_nutrients)}):")
            for nutrient, constraint in guideline_nutrients[:5]:
                print(f"    {nutrient}: {constraint['min']:.1f} - {constraint['max']:.1f} {constraint['unit']}")
        
        # Display DRI fallback nutrients
        if dri_nutrients:
            print(f"\n  From DRI Micronutrient ({len(dri_nutrients)}):")
            for nutrient, constraint in dri_nutrients[:5]:
                print(f"    {nutrient}: {constraint['min']:.1f} {constraint['unit']}")
        
        # Food data
        food_data = result['food_data']
        if food_data:
            print(f"\nFood Data:")
            print(f"  Total items: {food_data['total_items']}")
            print(f"  Filtered items: {food_data['filtered_items']}")
            if food_data['by_cuisine']:
                print(f"  By cuisine: {food_data['by_cuisine']}")
        
        print("\n" + "="*70)


def example_usage():
    """Example usage of NutritionService"""
    
    service = NutritionService()
    
    # Sample user input
    user_input = {
        'gender': 'M',
        'age': 25,
        'weight': 70,
        'height': 175,
        'activity_factor': 1.55,
        'disease': 'normal',
        'food_preferences': ['Western', 'Asian']
    }
    
    # Calculate
    result = service.calculate_nutrition_needs(user_input)
    
    # Print summary
    service.print_summary(result)
    
    # Access data for algorithms
    if result['success']:
        # pyrefly: ignore [unsupported-operation]
        guidelines = result['guidelines']['nutrients']
        # pyrefly: ignore [unsupported-operation]
        food_data = result['food_data']['dataframe']
        
        print("\n[OK] Ready for Genetic Algorithm / Greedy Algorithm!")
        print(f"  - Guidelines available: {len(guidelines)} constraints")
        print(f"  - Food items available: {len(food_data)} items")


if __name__ == "__main__":
    example_usage()
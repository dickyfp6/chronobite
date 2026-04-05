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
                - activity_factor: float (1.2-1.9)
                - disease: str (normal, dm2, hypertension, cvd, cholesterol, ckd)
                - food_preferences: list (optional, default: [])
        
        Returns:
            dict dengan struktur:
            {
                'success': bool,
                'user_input': dict (user data yang diinput),
                'anthropometrics': {
                    'bmi': float,
                    'bmi_category': str,
                    'bbi': float
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
            
            # Validate ranges
            if not (14 <= age <= 100):
                raise ValueError(f"Age must be 14-100, got {age}")
            if weight <= 0 or height <= 0:
                raise ValueError("Weight and height must be positive")
            if not (1.2 <= activity_factor <= 1.9):
                raise ValueError(f"Activity factor must be 1.2-1.9, got {activity_factor}")
            
            valid_diseases = ['normal', 'dm2', 'hypertension', 'cvd', 'cholesterol', 'ckd']
            if disease not in valid_diseases:
                raise ValueError(f"Disease must be one of {valid_diseases}, got {disease}")
            
            # 2. Calculate anthropometrics
            bmi_calc = self.calculator.calculate_bmi(weight, height)
            bbi = self.calculator.calculate_bbi(height, gender)
            
            result['anthropometrics'] = {
                'bmi': bmi_calc['value'],
                'bmi_category': bmi_calc['category'],
                'bbi': bbi
            }
            
            # 3. Calculate energy (BMR, TDEE)
            bmr = self.calculator.calculate_bmr(weight, height, age, gender)
            tdee = self.calculator.calculate_tdee(bmr, activity_factor)
            
            result['energy'] = {
                'bmr': bmr,
                'tdee': tdee
            }
            
            # 4. Load & convert guidelines
            guideline_df = self.guideline_loader.get_guideline_by_disease(
                disease, age, gender
            )
            
            if guideline_df.empty:
                raise ValueError(f"No guideline found for {disease}, age {age}")
            
            # Convert guideline values
            user_params = {
                'tdee': tdee,
                'weight': weight,
                'bbi': bbi
            }
            
            # Get DRI untuk fallback
            dri_row = self.guideline_loader.get_dri_by_age_gender(age, gender)
            
            # Process guideline nutrients (with convertion)
            nutrients_dict = {}
            for idx, row in guideline_df.iterrows():
                nutrient = row['nutrient']
                min_val = row['min']
                max_val = row['max']
                basis = row['basis']
                
                # Convert nilai
                converted = self.calculator.convert_guideline_value(
                    min_val, max_val, basis, user_params
                )
                
                # Infer unit from nutrient name
                unit = self._infer_unit(nutrient)
                
                nutrients_dict[nutrient] = {
                    'min': converted['min_converted'],
                    'max': converted['max_converted'],
                    'basis': basis,
                    'constraint_type': converted['constraint_type'],
                    'unit': unit
                }
            
            # Add DRI fallback untuk nutrients yang tidak ada di guideline
            if dri_row is not None and disease != 'normal':
                # DRI column mapping
                dri_columns = dri_row.keys()
                for dri_col in dri_columns:
                    # Skip non-nutrient columns
                    if dri_col in ['age_min', 'age_max', 'gender']:
                        continue
                    
                    # Normalize DRI column name ke guideline format
                    # e.g., "vitamin_a_rae_mg" -> "vitamin_a_rae_mg"
                    nutrient_key = dri_col
                    
                    # Check if this nutrient already exists di guideline
                    if nutrient_key not in nutrients_dict:
                        dri_value = dri_row[dri_col]
                        
                        # Only add jika value tidak null/NaN
                        if pd.notna(dri_value):
                            unit = self._infer_unit(nutrient_key)
                            nutrients_dict[nutrient_key] = {
                                'min': float(dri_value),
                                'max': float(dri_value),
                                'basis': 'DRI',
                                'constraint_type': 'dri_micronutrient',
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
                        filtered_df = food_df[food_df['cuisine'].isin(food_preferences)].copy()
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
            
            # 6. Store user params untuk algorithm
            result['user_params'] = {
                'tdee': tdee,
                'weight': weight,
                'bbi': bbi,
                'energy_target': tdee,
                'age': age,
                'gender': gender,
                'disease': disease
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
        # TODO: Implement meal validation
        pass
    
    def get_last_result(self):
        """Get last calculation result"""
        return self.last_result
    
    def print_summary(self, result):
        """Print user-friendly summary"""
        if not result['success']:
            print(f"❌ Error: {result['error']}")
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
        guidelines = result['guidelines']['nutrients']
        food_data = result['food_data']['dataframe']
        
        print("\n✓ Ready for Genetic Algorithm / Greedy Algorithm!")
        print(f"  - Guidelines available: {len(guidelines)} constraints")
        print(f"  - Food items available: {len(food_data)} items")


if __name__ == "__main__":
    example_usage()

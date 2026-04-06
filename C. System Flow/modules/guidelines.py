"""
Module untuk process dan convert guideline
"""

import sys
import os

# Add parent directory to path untuk import data_loader
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_loader import get_guideline_loader
from modules.calculations import NutritionCalculator


class GuidelineProcessor:
    """Class untuk process guideline berdasarkan kondisi user"""
    
    def __init__(self):
        """Initialize guideline processor"""
        self.loader = get_guideline_loader()
        self.calc = NutritionCalculator()
    
    def get_nutrition_guidelines(self, user_data, nutrition_results):
        """
        Get dan convert guideline nutrisi untuk user
        
        Args:
            user_data: dict dari input_handler
            nutrition_results: dict hasil dari calculations
        
        Returns:
            dict: Guidelines terkonversi dengan nutrient constraints
        """
        
        disease = user_data['disease']
        age = user_data['age']
        gender = user_data['gender']
        user_params = nutrition_results['user_params']
        
        # Handle both single disease (string) and multiple diseases (list)
        disease_list = disease if isinstance(disease, list) else [disease]
        
        # Aggregate guidelines from all diseases
        guidelines_dict = {}
        disease_names = []
        
        for disease_item in disease_list:
            # Get guideline dari CSV untuk setiap disease
            guideline_df = self.loader.get_guideline_by_disease(disease_item, age, gender)
            
            if guideline_df.empty:
                print(f"⚠ No guideline found for disease={disease_item}, age={age}, gender={gender}")
                continue
            
            disease_names.append(disease_item)
            
            # Process setiap nutrient guideline
            for idx, row in guideline_df.iterrows():
                nutrient = row['nutrient']
                min_val = row['min']
                max_val = row['max']
                basis = row['basis']
                
                # Convert nilai
                converted = self.calc.convert_guideline_value(
                    min_val, max_val, basis, user_params
                )
                
                if nutrient not in guidelines_dict:
                    guidelines_dict[nutrient] = {
                        'min': converted['min_converted'],
                        'max': converted['max_converted'],
                        'basis': basis,
                        'constraint_type': converted['constraint_type'],
                        'source': 'guideline'
                    }
                else:
                    # Aggregate: take most restrictive (smallest min, largest max)
                    guidelines_dict[nutrient]['min'] = min(
                        guidelines_dict[nutrient]['min'],
                        converted['min_converted']
                    )
                    guidelines_dict[nutrient]['max'] = max(
                        guidelines_dict[nutrient]['max'],
                        converted['max_converted']
                    )
        
        if not guidelines_dict:
            print(f"⚠ No guidelines found for any diseases")
            return None
        
        return {
            'disease': ', '.join(disease_names) if disease_names else str(disease),
            'guidelines': guidelines_dict,
            'total_guidelines': len(guidelines_dict)
        }
    
    def display_guidelines(self, guidelines_result, nutrition_results):
        """
        Display guideline dalam format yang readable
        
        Args:
            guidelines_result: dict dari get_nutrition_guidelines()
            nutrition_results: dict hasil dari calculations
        """
        
        if guidelines_result is None:
            print("No guidelines available")
            return
        
        print("\n" + "="*70)
        print("KEBUTUHAN NUTRISI BERDASARKAN GUIDELINE")
        print("="*70)
        print(f"\nKondisi Kesehatan: {guidelines_result['disease'].upper()}")
        print(f"Jumlah Nutrient: {guidelines_result['total_guidelines']}")
        
        print("\nDaftar Kebutuhan Nutrisi:")
        print("-" * 70)
        
        for nutrient, constraint in guidelines_result['guidelines'].items():
            min_val = constraint['min']
            max_val = constraint['max']
            basis = constraint['basis']
            constraint_type = constraint['constraint_type']
            
            # Format output berdasarkan tipe constraint
            if constraint_type == 'unlimited':
                print(f"{nutrient:30} | No limit (unlimited)")
            elif constraint_type == 'absolute':
                print(f"{nutrient:30} | {min_val:10.2f} - {max_val:10.2f}")
            elif constraint_type == 'tdee_based':
                print(f"{nutrient:30} | {min_val:10.2f} - {max_val:10.2f} (dari TDEE)")
            elif constraint_type == 'weight_based':
                print(f"{nutrient:30} | {min_val:10.2f} - {max_val:10.2f} (dari BB)")
            elif constraint_type == 'bbi_based':
                print(f"{nutrient:30} | {min_val:10.2f} - {max_val:10.2f} (dari BBI)")
            else:
                print(f"{nutrient:30} | Invalid constraint")
        
        print("-" * 70)


def process_user_guidelines(user_data, nutrition_results):
    """
    Main function untuk process guidelines
    
    Args:
        user_data: dict dari input_handler
        nutrition_results: dict hasil dari calculations
    
    Returns:
        dict: Guidelines result
    """
    processor = GuidelineProcessor()
    guidelines = processor.get_nutrition_guidelines(user_data, nutrition_results)
    return {
        'processor': processor,
        'guidelines': guidelines
    }

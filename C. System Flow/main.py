"""
Main application untuk System Flow perhitungan nutrisi
Menggunakan consolidated NutritionService dengan DRI fallback integration
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.input_handler import get_user_input
from modules.output_formatter import OutputFormatter
from nutrition_service import NutritionService


def main():
    """Main function untuk run aplikasi"""
    
    formatter = OutputFormatter()
    
    try:
        # 1. Display welcome
        formatter.display_welcome()
        
        # 2. Get user input
        user_data = get_user_input()
        
        formatter.display_user_data(user_data)
        
        # 3. Calculate nutrition needs (includes validation)
        print("\nCalculating nutrition parameters with DRI integration...")
        service = NutritionService()
        result = service.calculate_nutrition_needs(user_data)
        
        if not result['success']:
            formatter.display_error(f"Calculation failed: {result['error']}")
            return
        
        # Prepare data untuk display (combine anthropometrics + energy)
        display_data = {
            **result['anthropometrics'],  # BMI, BBI, age_group, age_label, age_range
            **result['energy']  # BMR, TDEE
        }
        
        # Display anthropometrics
        formatter.display_calculation_results(display_data)
        
        # Display meal distribution
        formatter.display_meal_distribution(result['meal_plan'])
        
        # 4. Display detailed guidelines + summary with age classification
        service.print_summary(result)
        
        print("\n✓ Process completed successfully!")
        print("\n✓ Ready for Genetic Algorithm / Greedy Algorithm!")
        print(f"  - Total nutrients: {result['guidelines']['total_nutrients']}")
        print(f"  - Food items available: {result['food_data']['total_items'] if result['food_data'] else 'N/A'}")
        
    except FileNotFoundError as e:
        formatter.display_error(f"File not found: {e}")
    except Exception as e:
        formatter.display_error(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

"""
Main application untuk System Flow perhitungan nutrisi
Menggunakan consolidated NutritionService dengan DRI fallback integration
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.input_handler import get_user_input, validate_user_input
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
        
        # 3. Validate input
        if not validate_user_input(user_data):
            formatter.display_error("Invalid user input")
            return
        
        formatter.display_success("Input validated successfully")
        formatter.display_user_data(user_data)
        
        # 4. Calculate nutrition needs using consolidated service
        print("\nCalculating nutrition parameters with DRI integration...")
        service = NutritionService()
        result = service.calculate_nutrition_needs(user_data)
        
        if not result['success']:
            formatter.display_error(f"Calculation failed: {result['error']}")
            return
        
        # Display anthropometrics
        formatter.display_calculation_results(result)
        
        # 5. Display detailed guidelines (with DRI fallback)
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

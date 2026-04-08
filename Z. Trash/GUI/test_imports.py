"""
Quick test script untuk GUI - check imports
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    print("Testing imports...")
    from modules.input_handler import validate_user_input
    from modules.calculations import calculate_user_nutrition_needs
    from modules.guidelines import process_user_guidelines
    print("✓ All imports OK")
    print("\nGUI files ready!")
    print("To run GUI:")
    print("  cd GUI")
    print("  python main_gui.py")
except Exception as e:
    print(f"✗ Import error: {e}")
    import traceback
    traceback.print_exc()

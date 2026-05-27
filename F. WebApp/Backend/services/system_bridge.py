"""
Adapter/Bridge Layer: Connects Flask routes to C. System Flow & D. Model logic
PURPOSE: Wrap existing system logic WITHOUT rewriting it
SAFETY: Zero logic changes - just imports and passes data through
"""

import sys
import os
import importlib.util

# ─── Path Setup ───────────────────────────────────────────────────────────
# F. WebApp/Backend/services/system_bridge.py
# needs to reach:
#   - C. System Flow/nutrition_service.py (3 dirs up)
#   - D. Model/Greedy Algorithm/greedy_interface.py (3 dirs up)

ROOT_PATH = os.path.join(os.path.dirname(__file__), '../../..')

sys.path.insert(0, os.path.join(ROOT_PATH, 'C. System Flow'))
sys.path.insert(0, os.path.join(ROOT_PATH, 'D. Model'))

# ─── Import Core Services (UNTOUCHED) ──────────────────────────────────────

try:
    from nutrition_service import NutritionService
    print("✓ NutritionService imported successfully")
except ImportError as e:
    print(f"❌ Failed to import NutritionService: {e}")
    NutritionService = None

# ─── Import Greedy Algorithm (Special handling for folder with spaces) ──────

GreedyAlgorithmInterface = None
try:
    greedy_path = os.path.join(
        ROOT_PATH, 'D. Model', 'Greedy Algorithm', 'greedy_interface.py'
    )
    spec = importlib.util.spec_from_file_location("greedy_interface", greedy_path)
    if spec is not None and spec.loader is not None:
        greedy_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(greedy_module)
        GreedyAlgorithmInterface = greedy_module.GreedyAlgorithmInterface
        print("✓ GreedyAlgorithmInterface imported successfully")
    else:
        print("⚠ Failed to create spec for GreedyAlgorithmInterface")
except Exception as e:
    print(f"⚠ Warning: Greedy Algorithm import failed: {e}")

# ─── Service Instances (Lazy Loading) ──────────────────────────────────────

_nutrition_service = None
_greedy_algorithm = None


def _get_nutrition_service():
    """Lazy load NutritionService on first use"""
    global _nutrition_service
    if _nutrition_service is None:
        if NutritionService is None:
            raise RuntimeError("NutritionService not available")
        _nutrition_service = NutritionService()
    return _nutrition_service


def _get_greedy_algorithm():
    """Lazy load GreedyAlgorithm on first use"""
    global _greedy_algorithm
    if _greedy_algorithm is None:
        if GreedyAlgorithmInterface is None:
            raise RuntimeError("GreedyAlgorithmInterface not available")
        _greedy_algorithm = GreedyAlgorithmInterface()
    return _greedy_algorithm


# ─── Public API (Called by routes) ─────────────────────────────────────────

def analyze_profile(user_data):
    """
    Wrapper: Call NutritionService.calculate_nutrition_needs()
    
    Args:
        user_data: dict with keys {gender, age, weight, height, activity, diseases, food_preferences}
    
    Returns:
        dict with {success, anthropometrics, energy, guidelines}
    """
    normalized_user_data = dict(user_data)

    if 'activity_factor' not in normalized_user_data:
        activity_value = normalized_user_data.get('activity', 1.845)
        try:
            normalized_user_data['activity_factor'] = float(activity_value)
        except (TypeError, ValueError):
            normalized_user_data['activity_factor'] = 1.845

    if 'disease' not in normalized_user_data and 'diseases' in normalized_user_data:
        normalized_user_data['disease'] = normalized_user_data.get('diseases', ['normal'])

    service = _get_nutrition_service()
    return service.calculate_nutrition_needs(normalized_user_data)


def generate_menu(menu_request):
    """
    Wrapper: Call GreedyAlgorithmInterface.generate()
    
    Args:
        menu_request: dict with {algorithm, user_profile, analysis_data}
    
    Returns:
        dict with {success, menu_plan: {meals, total_calories, ...}}
    """
    algo = _get_greedy_algorithm()
    return algo.generate(menu_request)

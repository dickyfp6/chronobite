"""Debug script untuk trace TDEE calculation"""
import sys
sys.path.insert(0, 'C. System Flow')

from nutrition_service import NutritionService

# User profile dari screenshot
user_input = {
    'gender': 'M',
    'age': 27,
    'weight': 68,
    'height': 168,
    'activity_factor': 1.845,  # Moderate
    'disease': ['dm2'],  # Testing with diabetes
    'food_preferences': []
}

# Initialize service
service = NutritionService()

# Calculate
result = service.calculate_nutrition_needs(user_input)

if result['success']:
    print("=" * 70)
    print("DEBUG TDEE CALCULATION")
    print("=" * 70)
    print(f"\nUser Input:")
    print(f"  Gender: {user_input['gender']}")
    print(f"  Age: {user_input['age']}")
    print(f"  Weight: {user_input['weight']} kg")
    print(f"  Height: {user_input['height']} cm")
    print(f"  Activity: {user_input['activity_factor']}")
    print(f"  Disease: {user_input['disease']}")
    
    print(f"\nAnthropometrics:")
    print(f"  BMI: {result['anthropometrics']['bmi']} ({result['anthropometrics']['bmi_category']})")
    print(f"  BBI: {result['anthropometrics']['bbi']} kg")
    
    print(f"\nEnergy Calculation:")
    print(f"  BMR: {result['energy']['bmr']} kcal")
    print(f"  TDEE: {result['energy']['tdee']} kcal")
    print(f"  Activity Factor: {user_input['activity_factor']}")
    print(f"  Calculated TDEE: {result['energy']['bmr']} × {user_input['activity_factor']} = {result['energy']['bmr'] * user_input['activity_factor']}")
    
    print(f"\nGuideline Macros (from backend):")
    if 'guidelines' in result and 'nutrients' in result['guidelines']:
        nutrients = result['guidelines']['nutrients']
        for key in ['energy_kcal', 'carbohydrate_g', 'protein_g', 'fat_g']:
            if key in nutrients:
                n = nutrients[key]
                print(f"  {key}: {n['min']}-{n['max']} {n['unit']}")
else:
    print(f"Error: {result.get('error')}")

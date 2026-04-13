#!/usr/bin/env python
# Test new single-page form with backend API

import sys
import json
import requests

sys.path.insert(0, r"F. WebApp")

# Test data matching new form structure
test_data = {
    "gender": "M",
    "age": 30,
    "weight": 70,
    "height": 170,
    "activity": "1.845",
    "diseases": ["normal"],
    "food_preferences": [],
    "algorithm": "greedy"
}

print("=" * 60)
print("Testing New Single-Page Form with Backend API")
print("=" * 60)

print("\nTest Data:")
print(json.dumps(test_data, indent=2))

print("\n[1] Testing /api/analyze endpoint...")
try:
    r = requests.post("http://127.0.0.1:5000/api/analyze", json=test_data)
    print(f"    ✓ Status Code: {r.status_code}")
    
    resp = r.json()
    print(f"    ✓ Success: {resp.get('success', False)}")
    
    if resp.get('success'):
        energy = resp.get('energy', {})
        print(f"    ✓ BMI: {energy.get('bmi')} kg/m²")
        print(f"    ✓ BMR: {energy.get('bmr')} kkal")
        print(f"    ✓ TDEE: {energy.get('tdee')} kkal")
        print(f"\n✅ Form structure is working correctly!")
    else:
        print(f"    ✗ Error: {resp.get('error')}")
        
except requests.ConnectionError:
    print("    ✗ Cannot connect to Flask app. Make sure it's running on http://127.0.0.1:5000")
except Exception as e:
    print(f"    ✗ Error: {e}")

print("\n" + "=" * 60)

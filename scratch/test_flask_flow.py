import sys
import os
import time

# Set paths
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(base_dir, "C. System Flow"))
sys.path.insert(0, os.path.join(base_dir, "D. Model"))
sys.path.insert(0, os.path.join(base_dir, "F. WebApp"))

import app_integrated

app = app_integrated.app
app.testing = True
client = app.test_client()

user_profile = {
    "gender": "F",
    "age": 25,
    "weight": 60,
    "height": 160,
    "activity": "active",
    "diseases": ["normal"],
    "food_preferences": ["Asian", "Western"],
}

print("1. Calling /api/analyze...")
analyze_res = client.post("/api/analyze", json=user_profile)
print(f"Status: {analyze_res.status_code}")
analysis_data = analyze_res.json

if analyze_res.status_code != 200 or not analysis_data.get("success"):
    print("Analyze failed!")
    sys.exit(1)

print("2. Calling /api/generate-menu with genetic algorithm...")
generate_payload = {
    "algorithm": "genetic",
    "user_input": user_profile,
    "analysis_data": analysis_data,
}

gen_res = client.post("/api/generate-menu", json=generate_payload)
print(f"Status: {gen_res.status_code}")
gen_data = gen_res.json

if gen_res.status_code != 202:
    print(f"Generate menu failed: {gen_data}")
    sys.exit(1)

job_id = gen_data["job_id"]
print(f"Job ID: {job_id}")

print("3. Polling /api/job-status/<job_id>...")
while True:
    status_res = client.get(f"/api/job-status/{job_id}")
    status_data = status_res.json
    print(f"Status Response: {status_data}")

    if status_data.get("status") in ["done", "error"]:
        if status_data.get("status") == "done":
            print("Job completed successfully!")
            print(f"Menu plan algorithm used: {status_data['menu_plan']['algorithm_used']}")
            print(f"Total Daily Calories: {status_data['menu_plan']['total_daily_calories']}")
            
            for meal_name in ['breakfast', 'lunch', 'dinner']:
                meal = status_data['menu_plan'][meal_name]
                print(f"\n{meal_name.upper()}:")
                if 'courses' in meal:
                    for c_type in ['Main', 'Side', 'Drink']:
                        course = meal['courses'].get(c_type, {})
                        candidates = course.get('candidates', [])
                        if candidates:
                            primary = candidates[0]
                            print(f"  {c_type}: {primary['name']} ({primary['serving_size']}g)")
        else:
            print(f"Job failed with error: {status_data.get('error')}")
        break

    time.sleep(3)

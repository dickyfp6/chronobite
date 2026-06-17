import sys
import os
import time

# Set paths
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(base_dir, 'C. System Flow'))
sys.path.insert(0, os.path.join(base_dir, 'D. Model'))

import app_integrated
app = app_integrated.app
app.testing = True
client = app.test_client()

payload = {
    "gender": "F",
    "age": 25,
    "weight": 60,
    "height": 160,
    "activity_factor": 1.55,
    "disease": ["normal"],
    "food_preferences": ["Asian", "Western"],
    "algorithm": "genetic_algorithm"
}

print("POST /api/generate-menu")
res = client.post('/api/generate-menu', json=payload)
print(res.status_code, res.json)

if res.status_code == 202:
    job_id = res.json['job_id']
    print(f"Job started with ID: {job_id}")
    
    # Poll until finished
    while True:
        poll_res = client.get(f'/api/job-status/{job_id}')
        status_data = poll_res.json
        print("Polling:", status_data)
        
        if status_data.get('status') in ['completed', 'error']:
            break
        
        time.sleep(5)

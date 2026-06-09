import requests
import json
import time

base_url = "http://127.0.0.1:5000"

diseases_to_test = [
    ["normal"],
    ["dm2"],
    ["ckd"],
    ["hypertension", "cholesterol"]
]

for diseases in diseases_to_test:
    print(f"\n==========================================")
    print(f"Testing diseases: {diseases}")
    print(f"==========================================")
    
    # 1. Analyze profile
    analyze_payload = {
        "gender": "male",
        "age": 45,
        "weight": 70,
        "height": 165,
        "activity": "1.545",
        "diseases": diseases,
        "food_preferences": [],
        "algorithm": "greedy"
    }
    try:
        r_analyze = requests.post(f"{base_url}/api/analyze", json=analyze_payload)
        analysis_res = r_analyze.json()
        if not analysis_res.get("success"):
            print("Analyze failed:", analysis_res)
            continue
    except Exception as e:
        print("Analyze request failed:", e)
        continue
        
    # 2. Test Greedy
    greedy_payload = {
        "algorithm": "greedy",
        "user_profile": {
            "gender": "M",
            "age": 45,
            "weight": 70,
            "height": 165,
            "activity": "1.545",
            "diseases": diseases,
            "food_preferences": [],
            "algorithm": "greedy"
        },
        "analysis_data": analysis_res,
        "user_input": analysis_res
    }
    
    t0 = time.time()
    try:
        r = requests.post(f"{base_url}/api/generate-menu", json=greedy_payload)
        print(f"Greedy Status: {r.status_code}, Time: {time.time() - t0:.2f}s")
        if r.status_code != 200:
            print("Response:", r.text)
    except Exception as e:
        print("Greedy Failed:", e)

    # 3. Test Genetic
    genetic_payload = {
        "algorithm": "genetic",
        "user_profile": {
            "gender": "M",
            "age": 45,
            "weight": 70,
            "height": 165,
            "activity": "1.545",
            "diseases": diseases,
            "food_preferences": [],
            "algorithm": "genetic"
        },
        "analysis_data": analysis_res,
        "user_input": analysis_res
    }
    
    t0 = time.time()
    try:
        r = requests.post(f"{base_url}/api/generate-menu", json=genetic_payload)
        print(f"Genetic Status: {r.status_code}, Time: {time.time() - t0:.2f}s")
        if r.status_code != 200:
            print("Response:", r.text)
    except Exception as e:
        print("Genetic Failed:", e)

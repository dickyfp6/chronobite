import requests  # type: ignore
import json
import time

base_url = "http://127.0.0.1:5000"

print("==================================================")
print("TESTING BACKEND CORS AND ENDPOINT INTEGRITY")
print("==================================================")

# 1. Test OPTIONS Preflight Request for /api/generate-menu
print("\n--- 1. Testing OPTIONS preflight request ---")
preflight_headers = {
    "Origin": "https://chronobite.vercel.app",
    "Access-Control-Request-Method": "POST",
    "Access-Control-Request-Headers": "Content-Type"
}
try:
    r_options = requests.options(f"{base_url}/api/generate-menu", headers=preflight_headers)
    print(f"Status Code: {r_options.status_code}")
    print("Response Headers:")
    for h, v in r_options.headers.items():
        if h.lower().startswith("access-control-"):
            print(f"  {h}: {v}")
    
    assert r_options.status_code in (200, 204), f"Preflight status code is {r_options.status_code}"
    assert "Access-Control-Allow-Origin" in r_options.headers, "Access-Control-Allow-Origin header is missing!"
    print("[OK] Preflight OPTIONS check PASSED!")
except Exception as e:
    print(f"[ERROR] OPTIONS Preflight Failed: {e}")
    exit(1)

# 2. Test 404 CORS Headers
print("\n--- 2. Testing 404 Error CORS Headers ---")
try:
    r_404 = requests.get(f"{base_url}/api/does-not-exist-route", headers={"Origin": "https://chronobite.vercel.app"})
    print(f"Status Code: {r_404.status_code}")
    print(f"Content: {r_404.text}")
    print(f"Access-Control-Allow-Origin: {r_404.headers.get('Access-Control-Allow-Origin')}")
    
    assert r_404.status_code == 404
    assert r_404.headers.get('Access-Control-Allow-Origin') == "*", "CORS header not present on 404 response!"
    print("[OK] 404 CORS check PASSED!")
except Exception as e:
    print(f"[ERROR] 404 CORS check failed: {e}")
    exit(1)

# 3. Test /api/analyze (POST)
print("\n--- 3. Testing /api/analyze ---")
analyze_payload = {
    "gender": "male",
    "age": 22,
    "weight": 65,
    "height": 170,
    "activity": "1.845",
    "diseases": [],
    "food_preferences": [],
    "algorithm": "greedy"
}
try:
    r_analyze = requests.post(
        f"{base_url}/api/analyze", 
        json=analyze_payload,
        headers={"Origin": "https://chronobite.vercel.app"}
    )
    print(f"Status Code: {r_analyze.status_code}")
    if r_analyze.status_code != 200:
        print(r_analyze.text)
        exit(1)
    analysis_res = r_analyze.json()
    print("[OK] Analyze endpoint check PASSED!")
except Exception as e:
    print(f"[ERROR] Analyze request failed: {e}")
    exit(1)

# 4. Test /api/generate-menu (POST) using Genetic Algorithm
print("\n--- 4. Testing /api/generate-menu with Genetic Algorithm ---")
generate_payload = {
    "algorithm": "genetic",
    "user_profile": {
        "gender": "M",
        "age": 22,
        "weight": 65,
        "height": 170,
        "activity": "1.845",
        "diseases": ["normal"],
        "food_preferences": [],
        "algorithm": "genetic"
    },
    "analysis_data": analysis_res,
    "user_input": analysis_res
}

t_start = time.time()
try:
    r_generate = requests.post(
        f"{base_url}/api/generate-menu", 
        json=generate_payload,
        headers={"Origin": "https://chronobite.vercel.app"}
    )
    t_end = time.time()
    
    print(f"Status Code: {r_generate.status_code}")
    print(f"Time Taken: {t_end - t_start:.2f} seconds")
    print(f"Access-Control-Allow-Origin: {r_generate.headers.get('Access-Control-Allow-Origin')}")
    
    assert r_generate.status_code == 200, f"Expected 200 but got {r_generate.status_code}"
    assert r_generate.headers.get('Access-Control-Allow-Origin') == "*", "CORS header not present on 200 response!"
    
    menu_plan = r_generate.json().get("menu_plan", {})
    print(f"Menu Plan keys: {list(menu_plan.keys()) if menu_plan else 'None'}")
    print("[OK] Genetic Algorithm generate-menu check PASSED!")
except Exception as e:
    print(f"[ERROR] Generate Menu request failed: {e}")
    exit(1)

print("\n==================================================")
print("ALL TESTS COMPLETED SUCCESSFULLY!")
print("==================================================")


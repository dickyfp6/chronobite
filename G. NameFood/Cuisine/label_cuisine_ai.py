import os
import sys
import json
import pandas as pd
# pyrefly: ignore [missing-source-for-stubs]
import requests
import time
import math
import traceback

# =====================================================================
# CONFIGURATION
# =====================================================================
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)

INPUT_FILE = os.path.normpath(os.path.join(PARENT_DIR, "output", "03_dataset_halal_ai.csv"))
OUTPUT_FILE = os.path.normpath(os.path.join(CURRENT_DIR, "03_dataset_halal_cuisine.csv"))
CACHE_FILE = os.path.normpath(os.path.join(CURRENT_DIR, "cuisine_cache.json"))
ENV_FILE = os.path.normpath(os.path.join(PARENT_DIR, ".env"))

MODEL_NAME = "gemini-2.0-flash"
API_BASE_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent"

ALLOWED_CUISINES = ["Asian", "Western", "Mediteranian", "Generic"]
BATCH_SIZE = 50

def load_env():
    """Load API keys from .env if it exists"""
    if os.path.exists(ENV_FILE):
        try:
            with open(ENV_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        parts = line.split("=", 1)
                        if len(parts) == 2:
                            key, val = parts[0].strip(), parts[1].strip()
                            val = val.strip('"').strip("'")
                            os.environ[key] = val
        except Exception as e:
            print(f"[WARN] Error loading .env file: {e}")

def get_api_key():
    return os.environ.get("GEMINI_API_KEY")

def call_ai_batch(names_list, api_key):
    """Call Gemini AI to classify a batch of foods at once"""
    headers = {
        "Content-Type": "application/json"
    }
    
    categories_str = ", ".join(ALLOWED_CUISINES)
    foods_text = "\n".join([f"{i+1}. {name}" for i, name in enumerate(names_list)])
    
    prompt = (
        f"You are an expert culinary classifier. Your task is to categorize each of the given food names "
        f"into exactly ONE of the following cuisine categories: [{categories_str}].\n"
        f"Rules:\n"
        f"- Asian: Specific to Asian countries (e.g., Japanese, Chinese, Indonesian, Indian).\n"
        f"- Western: European/American cuisines.\n"
        f"- Mediteranian: Middle-Eastern or Mediterranean cuisines.\n"
        f"- Generic: Raw ingredients, plain fruits, plain vegetables, raw meats, sweets, or no specific cultural origin.\n\n"
        f"Output format: Return ONLY a valid JSON array of strings matching the exact length and order of the input list.\n\n"
        f"Foods to classify:\n{foods_text}"
    )
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.0,
            "response_mime_type": "application/json"
        }
    }
    
    for attempt in range(5):
        try:
            url = f"{API_BASE_URL}?key={api_key}"
            response = requests.post(url, headers=headers, json=payload, timeout=40)
            
            if response.status_code == 429:
                sleep_sec = 60 # Default fallback
                try:
                    res_json = response.json()
                    for detail in res_json.get("error", {}).get("details", []):
                        if "retryDelay" in detail:
                            delay_str = detail["retryDelay"] # e.g., "51s" or "51.19s"
                            if delay_str.endswith("s"):
                                sleep_sec = float(delay_str[:-1]) + 2.0
                            break
                except Exception:
                    pass
                print(f"  -> [RATE LIMIT] Terlalu cepat (Gemini Rate Limit). Response: {response.text}")
                print(f"  -> Menunggu {sleep_sec} detik sebelum mencoba lagi...")
                time.sleep(sleep_sec)
                continue
                
            if response.status_code in [500, 502, 503, 504]:
                print(f"  -> [SERVER ERROR] Gemini API sedang padat/down ({response.status_code}). Response: {response.text}")
                print("  -> Menunggu 10 detik sebelum mencoba lagi...")
                time.sleep(10)
                continue

            if response.status_code == 200:
                res_data = response.json()
                try:
                    raw_ans = res_data["candidates"][0]["content"]["parts"][0]["text"].strip()
                    result_list = json.loads(raw_ans)
                    
                    if isinstance(result_list, list) and len(result_list) == len(names_list):
                        cleaned = []
                        for ans in result_list:
                            ans_lower = str(ans).lower()
                            matched = "Generic"
                            for cat in ALLOWED_CUISINES:
                                if cat.lower() in ans_lower:
                                    matched = cat
                                    break
                            if matched == "Generic" and "mediterranean" in ans_lower:
                                    matched = "Mediteranian"
                            cleaned.append(matched)
                        return cleaned
                    else:
                        print(f"  -> [WARN] Length mismatch. Expected {len(names_list)}, got {len(result_list) if isinstance(result_list, list) else 'Not a list'}")
                except Exception as e:
                    print(f"  -> [WARN] Failed to parse JSON from AI response: {e}")
                    print(f"  -> [DEBUG] Raw Output: {res_data}")
            else:
                print(f"  -> [ERROR] API Error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"  -> [ERROR] API call failed with exception: {e}")
            traceback.print_exc()
            
        time.sleep(5) # wait before retry
        
    print("  -> [FAIL] Giving up on this batch after 5 attempts.")
    return None

def main():
    print("="*60)
    print("STEP 08: Classify Cuisines using GEMINI AI (BATCH MODE)")
    print("="*60)

    os.makedirs(CURRENT_DIR, exist_ok=True)

    if not os.path.exists(INPUT_FILE):
        print(f"[ERROR] Input file not found: {INPUT_FILE}")
        sys.exit(1)

    print(f"Reading dataset from: {INPUT_FILE}")
    df = pd.read_csv(INPUT_FILE)
    print(f"Loaded {len(df)} rows.")

    cache = {}
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                cache = json.load(f)
            print(f"[OK] Loaded {len(cache)} classified cuisines from cache.")
        except Exception:
            pass

    unique_names = df["food_name"].unique()
    missing_names = [name for name in unique_names if name not in cache]
    print(f"Unique foods in dataset: {len(unique_names)}")
    print(f"Foods missing in cache: {len(missing_names)}")

    if missing_names:
        load_env()
        api_key = get_api_key()
        if api_key:
            total_batches = math.ceil(len(missing_names) / BATCH_SIZE)
            print(f"Using GEMINI AI to classify {len(missing_names)} missing foods in {total_batches} batches of {BATCH_SIZE}...")
            
            for i in range(0, len(missing_names), BATCH_SIZE):
                batch_names = missing_names[i:i+BATCH_SIZE]
                batch_num = (i // BATCH_SIZE) + 1
                
                print(f"[{batch_num}/{total_batches}] Classifying {len(batch_names)} foods...")
                safe_batch = [str(n) if pd.notna(n) and str(n).strip() != "" else "Unknown" for n in batch_names]
                
                results = call_ai_batch(safe_batch, api_key)
                if results is None:
                    print("  -> [FATAL] Gagal mendapatkan respon dari AI setelah beberapa percobaan.")
                    print("  -> Menghentikan program untuk mencegah data cache rusak.")
                    print("  -> Silakan tunggu 1 menit lalu jalankan kembali program ini.")
                    sys.exit(1)
                
                for name, res in zip(batch_names, results):
                    if pd.isna(name) or str(name).strip() == "":
                        cache[name] = "Generic"
                    else:
                        cache[name] = res
                        
                try:
                    with open(CACHE_FILE, "w", encoding="utf-8") as f:
                        json.dump(cache, f, ensure_ascii=False, indent=2)
                except Exception:
                    pass
                    
                time.sleep(5) 
        else:
            print("[WARN] GEMINI_API_KEY not found in .env! Please add it.")
            for name in missing_names:
                cache[name] = "Generic"

    print("\nApplying cuisines to dataset...")
    df["cuisine"] = df["food_name"].map(lambda x: cache.get(x, "Generic"))

    print("\nCuisine Distribution:")
    print(df["cuisine"].value_counts())

    print(f"\nSaving final dataset to: {OUTPUT_FILE}")
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"[OK] Process completed successfully! Total rows: {len(df)}")
    print("="*60)

if __name__ == "__main__":
    main()

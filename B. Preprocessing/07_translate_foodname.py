import os
import sys
import json
import pandas as pd
# pyrefly: ignore [missing-source-for-stubs]
import requests
import re
import time

# =====================================================================
# CONFIGURATION
# =====================================================================
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.normpath(os.path.join(CURRENT_DIR, "..", "A. Data", "Data Processed", "06_final_dataset.csv"))
OUTPUT_FILE = os.path.normpath(os.path.join(CURRENT_DIR, "..", "A. Data", "Data Processed", "07_super_final.csv"))
CACHE_FILE = os.path.normpath(os.path.join(CURRENT_DIR, "..", "G. NameFood", "output", "translation_cache.json"))
ENV_FILE = os.path.normpath(os.path.join(CURRENT_DIR, "..", "G. NameFood", ".env"))

MODEL_NAME = "gpt-4o-mini"
API_BASE_URL = "https://models.inference.ai.azure.com/chat/completions"

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
            print(f"[OK] Loaded environment variables from {ENV_FILE}")
        except Exception as e:
            print(f"[WARN] Error loading .env file: {e}")

def get_api_key():
    return os.environ.get("GITHUB_TOKEN")

def call_ai_single(name, api_key):
    """Fallback function to translate a single name if missing in cache"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    system_prompt = (
        "You are a food name simplification assistant. Your task is to convert raw USDA food descriptions "
        "into a short, natural, friendly, and appetizing culinary name in English.\n"
        "Output format: Return ONLY the simplified name. No quotes, no explanations, no markdown."
    )
    payload = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": name}
        ],
        "model": MODEL_NAME,
        "temperature": 0.0,
        "max_tokens": 50
    }
    for attempt in range(3):
        try:
            response = requests.post(API_BASE_URL, headers=headers, json=payload, timeout=20)
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 5))
                time.sleep(retry_after)
                continue
            if response.status_code == 200:
                res_data = response.json()
                return res_data["choices"][0]["message"]["content"].strip().strip('"')
        except Exception:
            pass
        time.sleep(2)
    return None

def main():
    print("="*60)
    print("STEP 07: Translate Cleaned Food Names to Super Final Dataset")
    print("="*60)

    # 1. Load data
    if not os.path.exists(INPUT_FILE):
        print(f"[ERROR] Input file not found: {INPUT_FILE}")
        sys.exit(1)

    print(f"Reading cleaned dataset from: {INPUT_FILE}")
    df = pd.read_csv(INPUT_FILE)
    print(f"Loaded {len(df)} rows.")

    # 2. Load translation cache
    cache = {}
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                cache = json.load(f)
            print(f"[OK] Loaded {len(cache)} translated names from cache.")
        except Exception as e:
            print(f"[WARN] Error loading cache: {e}")
    else:
        print(f"[WARN] Cache file not found at: {CACHE_FILE}")

    # 3. Identify missing translations
    unique_names = df["food_name"].unique()
    missing_names = [name for name in unique_names if name not in cache]
    print(f"Unique names in dataset: {len(unique_names)}")
    print(f"Names missing in cache: {len(missing_names)}")

    # 4. If there are missing names, try to translate them using API
    if missing_names:
        load_env()
        api_key = get_api_key()
        if api_key:
            print(f"Using AI to translate {len(missing_names)} missing names...")
            for i, name in enumerate(missing_names):
                print(f"[{i+1}/{len(missing_names)}] Translating: {name[:40]}...")
                translated = call_ai_single(name, api_key)
                if translated:
                    cache[name] = translated
                    # Save cache incrementally
                    try:
                        with open(CACHE_FILE, "w", encoding="utf-8") as f:
                            json.dump(cache, f, ensure_ascii=False, indent=2)
                    except Exception:
                        pass
                else:
                    print(f"  -> [WARN] Failed to translate. Falling back to original.")
                    cache[name] = name
        else:
            print("[WARN] GITHUB_TOKEN not found. Missing names will fallback to original names.")
            for name in missing_names:
                cache[name] = name

    # 5. Map translations to dataset
    print("Applying translations to food names...")
    df["food_name_original"] = df["food_name"] # Keep a copy of original just in case
    df["food_name"] = df["food_name"].map(lambda x: cache.get(x, x))

    # Reorder columns slightly to keep food_name at the front and food_name_original near it if desired,
    # or keep existing schema. Let's just update food_name in-place and optionally keep original.
    # To keep schema exact but with translated names, we just save the df as-is with food_name updated.
    # The user said "menghasilkan produk di folder Data Processed 07_super_final.csv".

    # Save to 07_super_final.csv
    print(f"Saving super final dataset to: {OUTPUT_FILE}")
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"[OK] Process completed successfully! Total rows: {len(df)}")
    print("="*60)

if __name__ == "__main__":
    main()

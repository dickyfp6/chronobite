import os
import sys
import csv
import json
import time
import re
# pyrefly: ignore [missing-source-for-stubs]
import requests

# =====================================================================
# CONFIGURATION
# =====================================================================
# Paste your GitHub Token or GitHub Copilot API Key here.
# You can also set the GITHUB_TOKEN environment variable.
GITHUB_TOKEN = "PASTE_YOUR_GITHUB_TOKEN_HERE"

# Model to use. gpt-4o-mini is recommended (fast, high limits, smart).
MODEL_NAME = "gpt-4o-mini"
API_BASE_URL = "https://models.inference.ai.azure.com/chat/completions"

# Batch size: how many names to translate in one API request (1-50).
BATCH_SIZE = 30

# Output paths
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_CSV = os.path.join(CURRENT_DIR, "..", "A. Data", "Data Processed", "03_dataset_halal.csv")
OUTPUT_CSV = os.path.join(CURRENT_DIR, "output", "03_dataset_halal_ai.csv")
CACHE_FILE = os.path.join(CURRENT_DIR, "output", "translation_cache.json")
# =====================================================================

def load_env_file():
    """Load simple .env file manually to avoid dependency on python-dotenv"""
    env_path = os.path.join(CURRENT_DIR, ".env")
    if not os.path.exists(env_path):
        env_path = os.path.join(CURRENT_DIR, "..", ".env")
        
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        parts = line.split("=", 1)
                        if len(parts) == 2:
                            key, val = parts[0].strip(), parts[1].strip()
                            val = val.strip('"').strip("'")
                            os.environ[key] = val
            print(f"[OK] Loaded environment variables from {os.path.basename(env_path)}")
        except Exception as e:
            print(f"[WARN] Error loading .env file: {e}")

def get_api_key():
    """Get API key from GITHUB_TOKEN variable or env variable"""
    if GITHUB_TOKEN and GITHUB_TOKEN != "PASTE_YOUR_GITHUB_TOKEN_HERE":
        return GITHUB_TOKEN
    env_token = os.environ.get("GITHUB_TOKEN")
    if env_token:
        return env_token
    return None

def load_cache():
    """Load cached translations from JSON file"""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[WARN] Error loading cache file: {e}. Starting fresh.")
    return {}

def save_cache(cache):
    """Save translations cache to JSON file"""
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[WARN] Error saving cache file: {e}")

def call_ai_batch(names_batch, api_key):
    """Call GitHub Models API to translate a batch of names"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    system_prompt = (
        "You are a food name simplification assistant. Your task is to convert raw USDA food descriptions "
        "into short, natural, friendly, and appetizing culinary names in English.\n"
        "Input format: A JSON array of raw food names.\n"
        "Output format: A JSON array of the same length containing only the simplified names. "
        "Do not return markdown (e.g. no ```json blocks), do not return any explanations. "
        "Return ONLY the plain JSON array.\n\n"
        "Example Input:\n"
        '[\n  "Pillsbury Golden Layer Buttermilk Biscuits, Artificial Flavor, refrigerated dough",\n'
        '  "Waffle, buttermilk, frozen, ready-to-heat, toasted",\n'
        '  "Crackers, cream, Gamesa Sabrosas"\n]\n\n'
        "Example Output:\n"
        '[\n  "Buttermilk Biscuits",\n  "Toasted Buttermilk Waffles",\n  "Cream Crackers"\n]'
    )
    
    payload = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(names_batch)}
        ],
        "model": MODEL_NAME,
        "temperature": 0.0,
        "max_tokens": 1000
    }
    
    # Try calling the API
    for attempt in range(5):
        try:
            response = requests.post(API_BASE_URL, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 429:
                # Rate limit
                retry_after = int(response.headers.get("Retry-After", 5))
                print(f"[RATE LIMIT] Hit rate limit. Waiting {retry_after} seconds (Attempt {attempt+1}/5)...")
                time.sleep(retry_after)
                continue
                
            if response.status_code != 200:
                print(f"[ERROR] API returned error status {response.status_code}: {response.text}")
                time.sleep(3)
                continue
                
            res_data = response.json()
            ai_output = res_data["choices"][0]["message"]["content"].strip()
            
            # Clean markdown codeblocks if AI returned them
            if ai_output.startswith("```"):
                ai_output = re.sub(r"^```(?:json)?\n", "", ai_output)
                ai_output = re.sub(r"\n```$", "", ai_output)
                ai_output = ai_output.strip()
            
            # Parse the JSON array
            results = json.loads(ai_output)
            
            if not isinstance(results, list):
                raise ValueError("Response is not a list")
                
            if len(results) != len(names_batch):
                raise ValueError(f"Response length mismatch (Expected {len(names_batch)}, got {len(results)})")
                
            return results
            
        except Exception as e:
            print(f"[WARN] Error during batch processing (Attempt {attempt+1}/5): {e}")
            time.sleep(3)
            
    return None

def call_ai_single(name, api_key):
    """Fallback function to translate a single name if batch fails"""
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
    print("USDA Food Name AI Simplification Script")
    print("="*60)
    
    # Load environment variables from .env if it exists
    load_env_file()
    
    # 1. Verify API Key
    api_key = get_api_key()
    if not api_key:
        print("[CRITICAL] API Key (GITHUB_TOKEN) not found!")
        print("Please edit the script and set the GITHUB_TOKEN variable at the top,")
        print("or set the GITHUB_TOKEN environment variable in your shell.")
        sys.exit(1)
        
    print(f"Using API Key: {api_key[:8]}...{api_key[-8:] if len(api_key)>16 else ''}")
    print(f"Using model: {MODEL_NAME}")
    print(f"Input path: {INPUT_CSV}")
    print(f"Output path: {OUTPUT_CSV}")
    
    # 2. Check input file
    if not os.path.exists(INPUT_CSV):
        print(f"[CRITICAL] Input file not found at: {INPUT_CSV}")
        sys.exit(1)
        
    # 3. Read dataset
    rows = []
    unique_names = set()
    with open(INPUT_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames) if reader.fieldnames else []
        for row in reader:
            rows.append(row)
            unique_names.add(row["food_name"])
            
    total_rows = len(rows)
    total_unique = len(unique_names)
    print(f"Loaded {total_rows} rows from dataset containing {total_unique} unique food names.")
    
    # 4. Load cache
    cache = load_cache()
    print(f"Loaded {len(cache)} translated names from cache.")
    
    # Filter names that need translation
    names_to_translate = [name for name in unique_names if name not in cache]
    total_to_translate = len(names_to_translate)
    print(f"Remaining food names to translate: {total_to_translate}")
    
    if total_to_translate > 0:
        # 5. Perform translation in batches
        print(f"Translating in batches of {BATCH_SIZE}...")
        
        for i in range(0, total_to_translate, BATCH_SIZE):
            batch = names_to_translate[i:i+BATCH_SIZE]
            print(f"Processing batch {i//BATCH_SIZE + 1}/{(total_to_translate-1)//BATCH_SIZE + 1} (Size: {len(batch)})...")
            
            # Try batch API call
            batch_results = call_ai_batch(batch, api_key)
            
            if batch_results:
                # Successfully received batch translations
                for raw_name, clean_name in zip(batch, batch_results):
                    cache[raw_name] = clean_name
                print(f"  -> Successfully translated {len(batch)} names.")
            else:
                # Batch failed, fallback to single calls
                print(f"  -> [WARN] Batch call failed. Falling back to single item translation for this batch.")
                for raw_name in batch:
                    single_res = call_ai_single(raw_name, api_key)
                    if single_res:
                        cache[raw_name] = single_res
                        print(f"     Translated: '{raw_name[:30]}...' -> '{single_res}'")
                    else:
                        print(f"     [ERROR] Failed to translate: '{raw_name[:30]}...'")
                        cache[raw_name] = raw_name # fallback to original to avoid blocking forever
                        
            # Save cache incrementally
            save_cache(cache)
            time.sleep(0.5) # small throttle between calls
            
    print("\n[OK] Translation complete or up to date!")
    
    # 6. Generate final dataset with AI names
    print(f"Saving final dataset to: {OUTPUT_CSV}")
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    
    # We will replace 'food_name' with the simplified AI name
    # But let's write out the new dataset
    with open(OUTPUT_CSV, "w", encoding="utf-8", newline="") as f:
        # We can write the same fieldnames
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in rows:
            orig_name = row["food_name"]
            # Get from cache (fallback to original name if missing)
            row["food_name"] = cache.get(orig_name, orig_name)
            writer.writerow(row)
            
    print("[OK] Process completed successfully!")
    print(f"Total entries written: {len(rows)}")

if __name__ == "__main__":
    main()

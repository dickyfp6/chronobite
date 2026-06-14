import os
import sys
import json
import pandas as pd

# =====================================================================
# CONFIGURATION
# =====================================================================
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.normpath(os.path.join(CURRENT_DIR, "..", "A. Data", "Data Processed", "06_final_dataset.csv"))
OUTPUT_FILE = os.path.normpath(os.path.join(CURRENT_DIR, "..", "A. Data", "Data Processed", "07_super_final.csv"))

FOOD_NAME_CACHE = os.path.normpath(os.path.join(CURRENT_DIR, "..", "G. NameFood", "output", "food_name_cache.json"))
CUISINE_CACHE = os.path.normpath(os.path.join(CURRENT_DIR, "..", "G. NameFood", "output", "cuisine_cache.json"))
CATEGORY_CACHE = os.path.normpath(os.path.join(CURRENT_DIR, "..", "G. NameFood", "output", "category_cache.json"))

def load_cache(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    print(f"[WARN] Cache not found: {path}")
    return {}

def main():
    print("="*60)
    print("STEP 07: Apply AI Enhancements to Super Final Dataset")
    print("="*60)

    # 1. Load data
    if not os.path.exists(INPUT_FILE):
        print(f"[ERROR] Input file not found: {INPUT_FILE}")
        sys.exit(1)

    print(f"Reading cleaned dataset from: {INPUT_FILE}")
    df = pd.read_csv(INPUT_FILE)
    print(f"Loaded {len(df)} rows.")

    # 2. Load caches
    food_name_cache = load_cache(FOOD_NAME_CACHE)
    cuisine_cache = load_cache(CUISINE_CACHE)
    category_cache = load_cache(CATEGORY_CACHE)

    print(f"[OK] Loaded {len(food_name_cache)} name translations.")
    print(f"[OK] Loaded {len(cuisine_cache)} cuisine labels.")
    print(f"[OK] Loaded {len(category_cache)} category labels.")

    # 3. Apply mappings
    print("Applying AI enhancements...")
    df["food_name_original"] = df["food_name"] # Keep a copy of original
    
    # Map food name to short name
    df["food_name"] = df["food_name_original"].apply(lambda x: food_name_cache.get(str(x), x))
    
    # Map short name to cuisine and category
    df["cuisine"] = df["food_name"].apply(lambda x: cuisine_cache.get(str(x), "Generic"))
    df["consumption_label"] = df["food_name"].apply(lambda x: category_cache.get(str(x), "Generic"))

    # Save to 07_super_final.csv
    print(f"Saving super final dataset to: {OUTPUT_FILE}")
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"[OK] Process completed successfully! Total rows: {len(df)}")
    print("="*60)

if __name__ == "__main__":
    main()


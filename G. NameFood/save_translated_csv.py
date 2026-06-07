import os
import csv
import json

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_CSV = os.path.join(CURRENT_DIR, "..", "A. Data", "Data Processed", "03_dataset_halal.csv")
OUTPUT_CSV = os.path.join(CURRENT_DIR, "output", "03_dataset_halal_ai.csv")
CACHE_FILE = os.path.join(CURRENT_DIR, "output", "translation_cache.json")

def generate_partial_csv():
    print("="*60)
    print("Generating CSV Dataset from current Translation Cache")
    print("="*60)
    
    # 1. Check files
    if not os.path.exists(INPUT_CSV):
        print(f"[ERROR] Input CSV not found: {INPUT_CSV}")
        return
        
    if not os.path.exists(CACHE_FILE):
        print(f"[ERROR] Cache file not found: {CACHE_FILE}")
        return
        
    # 2. Load cache
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        cache = json.load(f)
    print(f"Loaded {len(cache)} translated food names from cache.")
    
    # 3. Read input rows
    rows = []
    fieldnames = []
    with open(INPUT_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames) if reader.fieldnames else []
        for row in reader:
            rows.append(row)
            
    print(f"Read {len(rows)} rows from original dataset.")
    
    # 4. Generate output with translated names
    translated_count = 0
    fallback_count = 0
    
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    with open(OUTPUT_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in rows:
            orig_name = row["food_name"]
            if orig_name in cache:
                row["food_name"] = cache[orig_name]
                translated_count += 1
            else:
                # Keep original name as fallback
                row["food_name"] = orig_name
                fallback_count += 1
            writer.writerow(row)
            
    print(f"[OK] Saved dataset to: {OUTPUT_CSV}")
    print(f"  - Translated names: {translated_count} rows")
    # Calculate unique translation coverage
    unique_orig = set(r["food_name"] for r in rows)
    coverage = len(cache) / len(unique_orig) if unique_orig else 0
    print(f"  - Un-translated (original) names: {fallback_count} rows")
    print(f"  - Unique names translation coverage: {coverage:.1%}")

if __name__ == "__main__":
    generate_partial_csv()

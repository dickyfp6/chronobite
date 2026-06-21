import os
import sys
import json
import pandas as pd

"""
Script 04: AI Enhancement
Tujuan: Memperkaya dataset akhir menggunakan hasil pemrosesan AI (LLM).
Tahapan:
1. Membaca dataset yang sudah bersih dari tahap 03 (03_final_dataset.csv)
2. Memuat cache hasil LLM untuk nama makanan (short naming) dan kategori asal masakan (cuisine)
3. Mengganti nama makanan dengan nama pendek yang lebih "user-friendly"
4. Mengisi kolom cuisine dengan hasil analisis AI
Catatan: Script ini TIDAK MENIMPA `consumption_label` bawaan rule-based agar filter nutrisi tetap valid!
"""

# =====================================================================
# CONFIGURATION
# =====================================================================
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.normpath(os.path.join(CURRENT_DIR, "..", "A. Data", "Data Processed", "03_final_dataset.csv"))
OUTPUT_FILE = os.path.normpath(os.path.join(CURRENT_DIR, "..", "A. Data", "Data Processed", "04_super_final.csv"))

FOOD_NAME_CACHE = os.path.normpath(os.path.join(CURRENT_DIR, "..", "G. NameFood", "output", "food_name_cache.json"))
CUISINE_CACHE = os.path.normpath(os.path.join(CURRENT_DIR, "..", "G. NameFood", "output", "cuisine_cache.json"))
# Kategori cache tidak dipakai lagi karena kita pakai RuleBased

def load_cache(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    print(f"[WARN] Cache not found: {path}")
    return {}

def main():
    print("="*60)
    print("STEP 04: Apply AI Enhancements to Dataset")
    print("="*60)

    # 1. Load data
    if not os.path.exists(INPUT_FILE):
        print(f"[ERROR] Input file not found: {INPUT_FILE}")
        sys.exit(1)

    print(f"[1/3] Reading cleaned dataset from: {INPUT_FILE}")
    df = pd.read_csv(INPUT_FILE)
    print(f"Loaded {len(df)} rows.")

    # 2. Load caches
    print("\n[2/3] Memuat cache AI...")
    food_name_cache = load_cache(FOOD_NAME_CACHE)
    cuisine_cache = load_cache(CUISINE_CACHE)

    print(f"  [OK] Loaded {len(food_name_cache)} name translations.")
    print(f"  [OK] Loaded {len(cuisine_cache)} cuisine labels.")

    # Build fallback mapping from food_name_ai.csv by fdc_id
    fallback_name_map = {}
    FOOD_NAME_AI_CSV = os.path.normpath(os.path.join(CURRENT_DIR, "..", "G. NameFood", "output", "food_name_ai.csv"))
    if os.path.exists(FOOD_NAME_AI_CSV):
        print(f"  Memuat fallback names dari: {FOOD_NAME_AI_CSV}")
        try:
            fallback_df = pd.read_csv(FOOD_NAME_AI_CSV)
            if "fdc_id" in fallback_df.columns and "food_name" in fallback_df.columns:
                for _, row_item in fallback_df.iterrows():
                    try:
                        fid = int(row_item["fdc_id"])
                        fallback_name_map[fid] = str(row_item["food_name"])
                    except (ValueError, TypeError):
                        pass
                print(f"  [OK] Loaded {len(fallback_name_map)} fallback name mappings by fdc_id.")
        except Exception as e:
            print(f"  [WARN] Error loading fallback food name CSV: {e}")

    # 3. Apply mappings
    print("\n[3/3] Menerapkan AI Enhancements...")
    df["food_name_original"] = df["food_name"] # Keep a copy of original
    
    # Map food name to short name using cache first, then fallback fdc_id, then keep original
    def map_name(row_data):
        orig_name = str(row_data["food_name_original"])
        try:
            fid = int(row_data["fdc_id"])
        except (ValueError, TypeError):
            fid = None
            
        if orig_name in food_name_cache:
            return food_name_cache[orig_name]
        if fid is not None and fid in fallback_name_map:
            return fallback_name_map[fid]
        return orig_name

    df["food_name"] = df.apply(map_name, axis=1)
    
    # Map short name to cuisine
    df["cuisine"] = df["food_name"].apply(lambda x: cuisine_cache.get(str(x), "Generic"))

    # PERHATIAN: Baris overwrite category_cache sudah dihapus permanen agar tidak bentrok dengan RuleBased

    # Save to 04_super_final.csv
    print(f"\nSaving super final dataset to: {OUTPUT_FILE}")
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"[OK] Process completed successfully! Total rows: {len(df)}")
    print("="*60)

if __name__ == "__main__":
    main()

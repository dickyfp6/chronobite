"""
PERBAIKAN: Re-generate 07_super_final.csv dengan pemetaan nama yang konsisten.

MASALAH:
food_name_cache.json (dipakai 07_ai_implemen.py) dan food_name_ai.csv
(basis untuk cuisine_ai.py & category_ai.py) menghasilkan simplifikasi nama
yang sedikit berbeda untuk fdc_id yang sama (misal: "Dutch Apple Pie" vs
"Commercial Dutch Apple Pie"). Akibatnya, pencocokan nama ke cuisine_cache
dan category_cache gagal untuk item-item yang terkena kasus ini, sehingga
jatuh ke nilai default ("Generic").

SOLUSI:
Gunakan food_name_ai.csv (berdasarkan fdc_id) sebagai SATU-SATUNYA sumber
nama simplified, karena cuisine_cache dan category_cache memang dibangun
dari nama-nama di file ini. Ini menjamin konsistensi pencocokan.
"""

import pandas as pd
import json
import os

# =====================================================================
# SESUAIKAN PATH INI DENGAN LOKASI DI KOMPUTERMU
# =====================================================================
INPUT_06 = r"c:\Users\Silfia\Documents\FILE TA\TugasAkhirDSS\A. Data\Data Processed\06_final_dataset.csv"
FOOD_NAME_AI_CSV = r"c:\Users\Silfia\Documents\FILE TA\TugasAkhirDSS\G. NameFood\output\food_name_ai.csv"
CUISINE_CACHE = r"c:\Users\Silfia\Documents\FILE TA\TugasAkhirDSS\G. NameFood\output\cuisine_cache.json"
CATEGORY_CACHE = r"c:\Users\Silfia\Documents\FILE TA\TugasAkhirDSS\G. NameFood\output\category_cache.json"
OUTPUT_FILE = r"c:\Users\Silfia\Documents\FILE TA\TugasAkhirDSS\A. Data\Data Processed\07_super_final_fixed.csv"


def load_cache(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    print(f"[WARN] Cache not found: {path}")
    return {}


def main():
    print("=" * 60)
    print("PERBAIKAN: Re-generate dataset final dengan nama konsisten")
    print("=" * 60)

    # 1. Load dataset hasil cleaning (06)
    print(f"Membaca dataset dari: {INPUT_06}")
    df = pd.read_csv(INPUT_06)
    print(f"Loaded {len(df)} baris.")

    # 2. Load food_name_ai.csv sebagai SATU-SATUNYA sumber nama simplified
    #    (berdasarkan fdc_id, karena ini basis cuisine_ai.py & category_ai.py)
    print(f"Membaca nama simplified dari: {FOOD_NAME_AI_CSV}")
    name_df = pd.read_csv(FOOD_NAME_AI_CSV)
    name_map = dict(zip(name_df["fdc_id"], name_df["food_name"]))
    print(f"[OK] Loaded {len(name_map)} pemetaan nama berdasarkan fdc_id.")

    # 3. Load cache cuisine & category
    cuisine_cache = load_cache(CUISINE_CACHE)
    category_cache = load_cache(CATEGORY_CACHE)
    print(f"[OK] Loaded {len(cuisine_cache)} label cuisine.")
    print(f"[OK] Loaded {len(category_cache)} label kategori.")

    # 4. Terapkan pemetaan nama berdasarkan fdc_id (SATU SUMBER, KONSISTEN)
    df["food_name_original"] = df["food_name"]
    df["food_name"] = df["fdc_id"].map(name_map).fillna(df["food_name"])

    # 5. Terapkan label cuisine & kategori berdasarkan nama yang sudah konsisten
    df["cuisine"] = df["food_name"].apply(lambda x: cuisine_cache.get(str(x), "Generic"))
    df["consumption_label"] = df["food_name"].apply(lambda x: category_cache.get(str(x), "Snack"))

    # 6. Cek hasil: berapa item yang masih fallback ke default?
    n_generic_cuisine = (df["cuisine"] == "Generic").sum()
    n_fallback_category = df["consumption_label"].isin(["Main Course", "Side Dish", "Drink", "Snack"]).sum()
    n_total = len(df)

    print()
    print("DISTRIBUSI SETELAH PERBAIKAN:")
    print("-" * 60)
    print("Consumption label:")
    print(df["consumption_label"].value_counts())
    print()
    print("Cuisine:")
    print(df["cuisine"].value_counts())
    print()
    print(f"Item dengan consumption_label valid (4 kategori): {n_fallback_category}/{n_total}")

    # 7. Simpan
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"\n[OK] Dataset hasil perbaikan disimpan ke: {OUTPUT_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    main()
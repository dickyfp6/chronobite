import pandas as pd
from pathlib import Path

"""
Script 03: Apply Constraints & Deduplication
Tujuan:
1. Menghitung jumlah kelengkapan gizi wajib (Hard Constraint / HC) dan gizi pendukung (Soft Constraint / SC)
2. Memfilter makanan yang nutrisinya terlalu banyak kosong (NULL). Syarat: HC >= 16 dan SC >= 7.
3. Menghapus data duplikat berdasarkan fdc_id
4. Mengubah nilai sisa NULL menjadi 0 agar siap digunakan dalam model Algoritma Genetika
"""

def main():
    print("="*70)
    print("STEP 03: Apply Constraints (HC/SC) & Deduplication")
    print("="*70)

    # 1. Load data
    input_file = Path(__file__).parent.parent / 'A. Data/Data Processed/02_cleaned_dataset.csv'
    if not input_file.exists():
        print(f"Error: {input_file} tidak ditemukan!")
        return

    print(f"[1/4] Membaca data: {input_file.name}")
    data = pd.read_csv(input_file)
    print(f"Jumlah baris awal: {len(data)}")

    # ======================
    # HARD CONSTRAINT
    # ======================
    HC = [
        "water_g","energy_kcal","potassium_mg","calcium_mg",
        "carbohydrate_g","cholesterol_mg","saturated_fat_g",
        "fat_g","magnesium_mg","sodium_mg","protein_g","zinc_mg",
        "phosphorus_mg","fiber_g","vitamin_a_rae_mg","vitamin_b12_mg",
        "vitamin_b6_mg","vitamin_c_mg","iron_mg","trans_fat_g"
    ]

    # ======================
    # SOFT CONSTRAINT
    # ======================
    SC = [
        "sugar_g","fluoride_mg","folate_mg","choline_mg",
        "manganese_mg","selenium_mg","copper_mg","vitamin_b1_thiamin_mg","vitamin_b2_riboflavin_mg",
        "vitamin_b3_niacin_mg","vitamin_b5_pantothenic_acid_mg","vitamin_d_mg",
        "vitamin_e_mg","vitamin_k_mg"
    ]

    # ======================
    # HITUNG HC SC
    # ======================
    print("\n[2/4] Menghitung jumlah nutrisi terisi (Constraint Filtering)...")
    data["HC_count"] = data[HC].notna().sum(axis=1)
    data["SC_count"] = data[SC].notna().sum(axis=1)

    # ======================
    # FILTER DATASET
    # ======================
    filtered = data[
        (data["HC_count"] >= 16) &
        (data["SC_count"] >= 7)
    ].copy()

    print(f"Jumlah dataset lolos filter (HC>=16, SC>=7): {len(filtered)}")

    # ======================
    # CEK DUPLIKASI
    # ======================
    print("\n[3/4] Menghapus data duplikat dan null handling...")
    dup_fdc = filtered.duplicated(subset=["fdc_id"]).sum()
    dup_name = filtered.duplicated(subset=["food_name"]).sum()
    print(f"Duplikasi fdc_id: {dup_fdc}")
    print(f"Duplikasi food_name: {dup_name}")

    filtered = filtered.drop_duplicates(subset=["fdc_id"])

    # Ganti sisa NULL dengan 0
    filtered.fillna(0, inplace=True)

    # Drop kolom analisis HC/SC
    filtered.drop(columns=["HC_count","SC_count"], inplace=True)

    # ======================
    # CEK DISTRIBUSI FINAL
    # ======================
    print("\n[4/4] Final distribution after HC/SC filtering:")

    print("\n" + "="*70)
    print("CONSUMPTION DISTRIBUTION (LABEL):")
    print("="*70)
    consumption_dist = filtered["consumption_label"].value_counts().sort_values(ascending=False)
    for label, count in consumption_dist.items():
        pct = (count / len(filtered)) * 100
        print(f"  {label:20s}: {count:5d} ({pct:5.1f}%)")

    # ======================
    # SIMPAN DATASET FINAL
    # ======================
    output_file = Path(__file__).parent.parent / 'A. Data/Data Processed/03_final_dataset.csv'
    filtered.to_csv(output_file, index=False)

    print("\n" + "="*70)
    print("[OK] COMPLETE - Dataset berhasil disimpan")
    print("="*70)
    print(f"  Total items: {len(filtered)}")
    print(f"  Output file: {output_file.name}")
    print("\n" + "="*70)

if __name__ == "__main__":
    main()

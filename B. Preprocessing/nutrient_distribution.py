"""
Analisis kelengkapan data nutrisi pada dataset final 07_super_final.csv
"""

import pandas as pd

# =====================================================================
# SESUAIKAN PATH INI
# =====================================================================
FILE_PATH = r"c:\Users\Silfia\Documents\FILE TA\TugasAkhirDSS\A. Data\Data Processed\07_super_final_fixed.csv"

# =====================================================================
# DAFTAR NUTRISI HC DAN SC
# =====================================================================
HC = [
    "energy_kcal", "protein_g", "carbohydrate_g", "fat_g",
    "fiber_g", "water_g", "vitamin_a_rae_mg", "cholesterol_mg",
    "saturated_fat_g", "trans_fat_g", "phosphorus_mg", "potassium_mg",
    "sodium_mg", "zinc_mg", "calcium_mg", "iron_mg",
    "magnesium_mg", "vitamin_b12_mg", "vitamin_b6_mg", "vitamin_c_mg"
]

SC = [
    "sugar_g", "fluoride_mg", "folate_mg", "choline_mg",
    "manganese_mg", "selenium_mg", "copper_mg",
    "vitamin_b1_thiamin_mg", "vitamin_b2_riboflavin_mg",
    "vitamin_b3_niacin_mg", "vitamin_b5_pantothenic_acid_mg",
    "vitamin_d_mg", "vitamin_e_mg", "vitamin_k_mg"
]

def main():
    df = pd.read_csv(FILE_PATH)
    total = len(df)

    print("=" * 70)
    print(f"Dataset: {FILE_PATH}")
    print(f"Total item: {total}")
    print("=" * 70)

    print("\nANALISIS HARD CONSTRAINT (HC):")
    print("-" * 70)
    print(f"{'Nutrisi':<35} {'Tersedia':>10} {'Kosong (0)':>12} {'% Tersedia':>12}")
    print("-" * 70)
    for col in HC:
        if col in df.columns:
            # Nilai 0 dianggap "kosong" karena fillna(0) sudah dilakukan sebelumnya
            non_zero = (df[col] != 0).sum()
            zero = total - non_zero
            pct = (non_zero / total) * 100
            print(f"  {col:<33} {non_zero:>10} {zero:>12} {pct:>11.1f}%")
        else:
            print(f"  {col:<33} {'(kolom tidak ditemukan)':>35}")

    print("\nANALISIS SOFT CONSTRAINT (SC):")
    print("-" * 70)
    print(f"{'Nutrisi':<35} {'Tersedia':>10} {'Kosong (0)':>12} {'% Tersedia':>12}")
    print("-" * 70)
    for col in SC:
        if col in df.columns:
            non_zero = (df[col] != 0).sum()
            zero = total - non_zero
            pct = (non_zero / total) * 100
            print(f"  {col:<33} {non_zero:>10} {zero:>12} {pct:>11.1f}%")
        else:
            print(f"  {col:<33} {'(kolom tidak ditemukan)':>35}")

    print("\n" + "=" * 70)
    print("RINGKASAN:")
    print("-" * 70)

    # HC summary
    hc_exist = [c for c in HC if c in df.columns]
    hc_avg = sum((df[c] != 0).sum() for c in hc_exist) / (len(hc_exist) * total) * 100
    print(f"  Rata-rata kelengkapan HC: {hc_avg:.1f}%")

    # SC summary
    sc_exist = [c for c in SC if c in df.columns]
    sc_avg = sum((df[c] != 0).sum() for c in sc_exist) / (len(sc_exist) * total) * 100
    print(f"  Rata-rata kelengkapan SC: {sc_avg:.1f}%")

    # Nutrisi HC paling sering kosong
    hc_worst = min(hc_exist, key=lambda c: (df[c] != 0).sum())
    hc_worst_pct = (df[hc_worst] != 0).sum() / total * 100
    print(f"  HC paling sedikit data : {hc_worst} ({hc_worst_pct:.1f}%)")

    # Nutrisi SC paling sering kosong
    sc_worst = min(sc_exist, key=lambda c: (df[c] != 0).sum())
    sc_worst_pct = (df[sc_worst] != 0).sum() / total * 100
    print(f"  SC paling sedikit data : {sc_worst} ({sc_worst_pct:.1f}%)")

    print("=" * 70)

if __name__ == "__main__":
    main()
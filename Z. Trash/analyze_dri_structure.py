import pandas as pd
import numpy as np

dri = pd.read_csv("A. Data/Data Raw/dri.csv")

print("="*70)
print("ANALISIS DRI.CSV - Struktur dan Tipe Nutrient")
print("="*70)

print("\n[1] STRUKTUR DATA:")
print(f"Rows: {len(dri)}")
print(f"Columns: {len(dri.columns)}")
print(f"\nColumn names:")
for i, col in enumerate(dri.columns, 1):
    print(f"  {i:2d}. {col}")

print("\n[2] KATEGORI NUTRIENT:")
print("\nMakronutrient (Range/Formula):")
macro_cols = ['energy_kcal', 'protein_g', 'avg_protein_g', 'min_fat_g', 'max_fat_g', 
              'avg_carb_g', 'min_carb_g', 'max_carb_g', 'fiber_g']
for col in macro_cols:
    if col in dri.columns:
        val = dri[col].iloc[0]
        print(f"  • {col:30s} = {val}")

print("\nMikronutrient (Single Value/Exact):")
micro_cols = [col for col in dri.columns if col not in ['age_min', 'age_max', 'gender'] + macro_cols + ['water_g']]
print(f"  Total: {len(micro_cols)} nutrient")
for col in micro_cols[:5]:
    val = dri[col].iloc[0]
    print(f"  • {col:30s} = {val}")
print(f"  ... dan {len(micro_cols)-5} lagi")

print("\n[3] ISSUE IDENTIFIKASI:")
print("\n❌ Masalah yang ditemukan:")
print("  1. Ada formula/text di cell (TDEE, '20% × TDEE', dll)")
print("  2. Column naming tidak konsisten")
print("  3. Makronutrient ada nilai range (min/max/avg)")
print("  4. Satuan nutrient berbeda (mg, g, %) - perlu normalisasi")

print("\n[4] SAMPLE DATA (Row 1):")
print(dri.iloc[0].to_string())

print("\n" + "="*70)

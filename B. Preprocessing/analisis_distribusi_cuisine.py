"""
File Analisis: Distribusi Cuisine & Label
Tujuan: Menganalisis sebaran jumlah makanan berdasarkan label konsumsi (Main Course, Snack, dll)
serta memetakan hasil silang (cross-tabulation) antara slot makanan dan cuisine asalnya.
Menggunakan dataset final (04_super_final.csv).
"""

import pandas as pd

import os
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.normpath(os.path.join(CURRENT_DIR, "..", "A. Data", "Data Processed", "04_super_final.csv"))

df = pd.read_csv(FILE_PATH)

print("="*70)
print(f"Total item dataset final: {len(df)}")
print("="*70)

print("\nDISTRIBUSI CONSUMPTION_LABEL (Slot Makanan):")
print("-"*70)
dist_consumption = df["consumption_label"].value_counts()
for label, count in dist_consumption.items():
    pct = (count / len(df)) * 100
    print(f"  {label:20s}: {count:5d} ({pct:5.1f}%)")

print("\nDISTRIBUSI CUISINE:")
print("-"*70)
dist_cuisine = df["cuisine"].value_counts()
for label, count in dist_cuisine.items():
    pct = (count / len(df)) * 100
    print(f"  {label:20s}: {count:5d} ({pct:5.1f}%)")

print("\nCROSS-TABULATION: SLOT MAKANAN x CUISINE")
print("-"*70)
crosstab = pd.crosstab(
    df["consumption_label"],
    df["cuisine"],
    margins=True
)
print(crosstab)
print("="*70)
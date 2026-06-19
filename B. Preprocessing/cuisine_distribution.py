import pandas as pd

# Sesuaikan path ini dengan lokasi file di komputermu
FILE_PATH = r"c:\Users\Silfia\Documents\FILE TA\TugasAkhirDSS\A. Data\Data Processed\07_super_final_fixed.csv"

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
import pandas as pd
import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path = os.path.normpath(os.path.join(base_dir, "A. Data", "Data Processed", "07_super_final.csv"))

if not os.path.exists(path):
    print(f"File not found: {path}")
    exit(1)

df = pd.read_csv(path)
print("=== Dataset Columns ===")
print(df.columns.tolist())
print("\n=== Dataset Size ===")
print(len(df))

print("\n=== Cuisine Distribution ===")
if "cuisine" in df.columns:
    print(df["cuisine"].value_counts(dropna=False))
if "cuisine_label" in df.columns:
    print("\n=== Cuisine Label Distribution ===")
    print(df["cuisine_label"].value_counts(dropna=False))

print("\n=== Sample Western Foods (Top 20 by calories) ===")
western_df = df[df["cuisine"] == "Western"]
print(western_df[["fdc_id", "food_name", "energy_kcal", "cuisine"]].head(20))

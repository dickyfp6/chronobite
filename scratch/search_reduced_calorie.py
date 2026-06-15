import pandas as pd
import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path = os.path.normpath(os.path.join(base_dir, "A. Data", "Data Processed", "07_super_final.csv"))

df = pd.read_csv(path)

print("=== Search for Reduced-Calorie ===")
reduced = df[df["food_name"].str.contains("Reduced", case=False, na=False)]
print(f"Found {len(reduced)} items containing 'Reduced'")
for idx, row in reduced.iterrows():
    if "white bread" in row["food_name"].lower() or "tenders" in row["food_name"].lower() or "dressing" in row["food_name"].lower():
        print(f"  {row['fdc_id']}: {row['food_name']} ({row['energy_kcal']} kcal) - {row['cuisine']}")

print("\n=== Search for White Bread ===")
white = df[df["food_name"].str.contains("White Bread", case=False, na=False)]
print(f"Found {len(white)} items containing 'White Bread'")
for idx, row in white.iterrows():
    print(f"  {row['fdc_id']}: {row['food_name']} ({row['energy_kcal']} kcal) - {row['cuisine']}")

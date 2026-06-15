import pandas as pd
import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path = os.path.normpath(os.path.join(base_dir, "A. Data", "Data Processed", "07_super_final.csv"))

df = pd.read_csv(path)

print("=== Search for Bread ===")
bread_items = df[df["food_name"].str.contains("Bread", case=False, na=False)]
print(f"Found {len(bread_items)} items containing 'Bread'")
print(bread_items[["fdc_id", "food_name", "energy_kcal", "cuisine"]].head(20))

print("\n=== Search for Chicken ===")
chicken_items = df[df["food_name"].str.contains("Chicken", case=False, na=False)]
print(f"Found {len(chicken_items)} items containing 'Chicken'")
print(chicken_items[["fdc_id", "food_name", "energy_kcal", "cuisine"]].head(20))

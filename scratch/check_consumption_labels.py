import pandas as pd
import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path = os.path.normpath(os.path.join(base_dir, "A. Data", "Data Processed", "07_super_final.csv"))

df = pd.read_csv(path)
print("=== Consumption Label counts (All) ===")
print(df["consumption_label"].value_counts(dropna=False))

print("\n=== Consumption Label counts (Western) ===")
print(df[df["cuisine"] == "Western"]["consumption_label"].value_counts(dropna=False))

print("\n=== Sample Drinks (Western) ===")
print(df[(df["cuisine"] == "Western") & (df["consumption_label"] == "Drink")][["fdc_id", "food_name", "energy_kcal"]])

print("\n=== Sample Side Dishes (Western) ===")
print(df[(df["cuisine"] == "Western") & (df["consumption_label"] == "Side Dish")][["fdc_id", "food_name", "energy_kcal"]].head(10))

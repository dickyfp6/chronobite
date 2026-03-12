import pandas as pd

data = pd.read_csv("Data Processed/01_hc_sc_filtered.csv")

pivot = data.pivot_table(
    index=["fdc_id", "food_name", "food_group"],
    columns="nutrient_name",
    values="amount"
).reset_index()

pivot.to_csv(
    "Data Processed/02_pivot_food_nutrients.csv",
    index=False
)

print("Pivot selesai")
print(pivot.shape)
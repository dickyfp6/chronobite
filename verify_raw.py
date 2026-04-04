import pandas as pd

data = pd.read_csv("A. Data/Data Processed/05_final_dataset.csv")

raw_items = data[data['food_name'].str.lower().str.contains('raw', na=False)]
print(f'Total raw items: {len(raw_items)}')
print(f'All Generic: {(raw_items["cuisine_label"] == "Generic").all()}')
print(f'\nCuisine distribution:\n{data["cuisine_label"].value_counts()}')

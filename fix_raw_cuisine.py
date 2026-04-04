import pandas as pd

# Load the dataset
data = pd.read_csv("A. Data/Data Processed/05_final_dataset.csv")

print("Before:")
print(f"Total items: {len(data)}")
print(f"Items with 'raw' in food_name: {data['food_name'].str.lower().str.contains('raw', na=False).sum()}")
print(f"Generic cuisine before: {(data['cuisine_label'] == 'Generic').sum()}")

# Convert items with "raw" to Generic cuisine
mask = data['food_name'].str.lower().str.contains('raw', na=False)
items_with_raw = data[mask].copy()

print(f"\nItems with 'raw' before update:")
print(items_with_raw[['food_name', 'cuisine_label']].to_string())

# Update cuisine label
data.loc[mask, 'cuisine_label'] = 'Generic'

print(f"\nAfter:")
print(f"Generic cuisine after: {(data['cuisine_label'] == 'Generic').sum()}")

print(f"\nItems with 'raw' after update:")
print(data[mask][['food_name', 'cuisine_label']].to_string())

# Save updated dataset
data.to_csv("A. Data/Data Processed/05_final_dataset.csv", index=False)
print(f"\n✓ Dataset updated and saved!")

# Show updated cuisine distribution
print("\nUpdated cuisine distribution:")
print(data['cuisine_label'].value_counts())

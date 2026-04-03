import pandas as pd

# ======================
# LOAD DATASET
# ======================
data = pd.read_csv("../Data Processed/05_final_dataset.csv")

print("Total data:", len(data))
print("\nFood group distribution:")
print(data["food_group"].value_counts())

# ======================
# MAPPING: food_group → consumption_label
# ======================
# High confidence mapping (jelas kategorinya)
mapping_high = {
    "Beverages": "Drink",
    "Poultry Products": "Main Course",
    "Beef Products": "Main Course",
    "Finfish and Shellfish Products": "Main Course",
    "Pork Products": "Main Course",
    "Lamb, Veal, and Game Products": "Main Course",
    "Legumes and Legume Products": "Main Course",
    "Cereal Grains and Pasta": "Main Course",
    "Sausages and Luncheon Meats": "Main Course",
    "Spices and Herbs": "Side Dish",
    "Fruits and Fruit Juices": "Snack",
    "Nut and Seed Products": "Snack",
    "Fast Foods": "Main Course",
    "Alcoholic Beverages": "Drink",
}

# Medium confidence mapping (ada overlap, tapi bias dominan)
mapping_medium = {
    "Snacks": "Snack",
    "Sweets": "Snack",
    "Breakfast Cereals": "Snack",
    "Baby Foods": "Snack",
    "Soups, Sauces, and Gravies": "Side Dish",
    "Fats and Oils": "Side Dish",
    "Vegetables and Vegetable Products": "Side Dish",
}

# Low confidence mapping (sangat ambigu, perlu manual review)
mapping_low = {
    "Dairy and Egg Products": "Snack",  # bisa Drink, Snack, Side
    "Baked Products": "Snack",  # bisa Main, Snack, Side
    "Meals, Entrees, and Side Dishes": "Main Course",  # mixed
    "Restaurant Foods": "Main Course",  # mixed
    "American Indian/Alaska Native Foods": "Main Course",  # mixed
}

# ======================
# CREATE CONSUMPTION LABEL
# ======================
def get_label_and_confidence(food_group):
    """
    Return: (label, confidence_level)
    """
    if food_group in mapping_high:
        return mapping_high[food_group], "high"
    elif food_group in mapping_medium:
        return mapping_medium[food_group], "medium"
    elif food_group in mapping_low:
        return mapping_low[food_group], "low"
    else:
        return "Unknown", "unknown"

# Apply mapping
data[["consumption_label", "label_confidence"]] = data["food_group"].apply(
    lambda x: pd.Series(get_label_and_confidence(x))
)

data["label_source"] = "auto"

# ======================
# CEK HASIL
# ======================
print("\n" + "="*50)
print("CONSUMPTION LABEL DISTRIBUTION:")
print("="*50)
print(data["consumption_label"].value_counts())

print("\n" + "="*50)
print("CONFIDENCE DISTRIBUTION:")
print("="*50)
print(data["label_confidence"].value_counts())

print("\n" + "="*50)
print("MAPPING BREAKDOWN:")
print("="*50)
for conf in ["high", "medium", "low"]:
    count = len(data[data["label_confidence"] == conf])
    pct = (count / len(data)) * 100
    print(f"{conf:8} | {count:5} items ({pct:5.1f}%)")

# ======================
# SIMPAN DATASET DRAFT
# ======================
output_path = "../Data Processed/05_final_dataset_with_consumption_draft.csv"
data.to_csv(output_path, index=False)
print(f"\n✓ Dataset draft berhasil disimpan ke: {output_path}")

# ======================
# REKOMENDASI REVIEW
# ======================
print("\n" + "="*50)
print("REKOMENDASI REVIEW MANUAL:")
print("="*50)
low_conf = data[data["label_confidence"] == "low"]
print(f"\nPerlu review: {len(low_conf)} items (confidence=low)")
print("\nTop items per food_group yang perlu review:")
for group in low_conf["food_group"].unique():
    count = len(low_conf[low_conf["food_group"] == group])
    print(f"  - {group}: {count} items")

print("\n" + "="*50)
print("NEXT STEP:")
print("="*50)
print("1. Buka file draft di Excel/CSV editor")
print("2. Filter: label_confidence = 'low' atau 'medium'")
print("3. Koreksi label yang salah")
print("4. Update kolom 'label_source' menjadi 'manual_corrected' saat edit")
print("5. Export sebagai final dataset")
print("="*50)

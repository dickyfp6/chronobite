import pandas as pd

# ======================
# LOAD DATASET
# ======================
data = pd.read_csv("Data Processed/03_dataset_halal.csv")

print("Jumlah data awal:", len(data))


# ======================
# HARD CONSTRAINT
# ======================
HC = [
"Water","Energy","Sugars, Total","Potassium, K","Calcium, Ca",
"Carbohydrate, by difference","Cholesterol","Fatty acids, total saturated",
"Total lipid (fat)","Magnesium, Mg","Sodium, Na","Protein","Zinc, Zn",
"Fiber, total dietary","Vitamin A, RAE","Vitamin B-12","Vitamin B-6",
"Vitamin C, total ascorbic acid","Iron, Fe","Phosphorus, P"
]

# ======================
# SOFT CONSTRAINT
# ======================
SC = [
"Sugars, Total","Fluoride, F","Folate, DFE","Choline, total","Manganese, Mn",
"Selenium, Se","Copper, Cu","Thiamin","Riboflavin","Niacin",
"Pantothenic acid","Vitamin D (D2 + D3)",
"Vitamin E (alpha-tocopherol)",
"Vitamin K (phylloquinone)"
]


# ======================
# HITUNG HC SC
# ======================
data["HC_count"] = data[HC].notna().sum(axis=1)
data["SC_count"] = data[SC].notna().sum(axis=1)


# ======================
# FILTER DATASET
# ======================
filtered = data[
    (data["HC_count"] >= 18) &
    (data["SC_count"] >= 9)
].copy()

print("Jumlah dataset setelah filter:", len(filtered))


# ======================
# CEK DUPLIKASI
# ======================
print("Duplikasi fdc_id:",
      filtered.duplicated(subset=["fdc_id"]).sum())

print("Duplikasi food_name:",
      filtered.duplicated(subset=["food_name"]).sum())

filtered = filtered.drop_duplicates(subset=["fdc_id"])


# ======================
# GANTI NULL → 0
# ======================
filtered.fillna(0, inplace=True)


# ======================
# DROP KOLOM ANALISIS
# ======================
filtered.drop(columns=["HC_count","SC_count"], inplace=True)


# ======================
# FOOD TYPE MAPPING
# ======================
food_type_map = {

"Baked Products": "Snack",
"Snacks": "Snack",
"Sweets": "Dessert",
"Vegetables and Vegetable Products": "Side Dish",
"American Indian/Alaska Native Foods": "Main Course",
"Restaurant Foods": "Main Course",
"Beverages": "Drink",
"Fats and Oils": "Side Dish",
"Dairy and Egg Products": "Drink",
"Baby Foods": "Snack",
"Sausages and Luncheon Meats": "Main Course",
"Poultry Products": "Main Course",
"Breakfast Cereals": "Snack",
"Legumes and Legume Products": "Main Course",
"Finfish and Shellfish Products": "Main Course",
"Fruits and Fruit Juices": "Dessert",
"Cereal Grains and Pasta": "Main Course",
"Nut and Seed Products": "Snack",
"Beef Products": "Main Course",
"Meals, Entrees, and Side Dishes": "Main Course",
"Fast Foods": "Main Course",
"Spices and Herbs": "Side Dish",
"Soups, Sauces, and Gravies": "Side Dish",
"Lamb, Veal, and Game Products": "Main Course"
}

filtered["food_type"] = filtered["food_group"].map(food_type_map)


# ======================
# CEK DISTRIBUSI
# ======================
print("\nDistribusi food_type:")
print(filtered["food_type"].value_counts())


# ======================
# SIMPAN DATASET FINAL
# ======================
filtered.to_csv(
    "Data Processed/05_final_dataset.csv",
    index=False
)

print("\nDataset berhasil disimpan.")
print("Total makanan:", len(filtered))
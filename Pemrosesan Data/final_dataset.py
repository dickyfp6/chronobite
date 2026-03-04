import pandas as pd

data = pd.read_csv("Data Processed/dataset_no_haram.csv")

# HARD CONSTRAINT
HC = [
"Water",
"Energy",
"Sugars, Total",
"Potassium, K",
"Calcium, Ca",
"Carbohydrate, by difference",
"Cholesterol",
"Fatty acids, total saturated",
"Total lipid (fat)",
"Magnesium, Mg",
"Sodium, Na",
"Protein",
"Zinc, Zn",
"Fiber, total dietary",
"Vitamin A, RAE",
"Vitamin B-12",
"Vitamin B-6",
"Vitamin C, total ascorbic acid",
"Iron, Fe"
]

# SOFT CONSTRAINT
SC = [
"Fluoride, F",
"Folate, DFE",
"Choline, total",
"Manganese, Mn",
"Selenium, Se",
"Copper, Cu",
"Thiamin",
"Riboflavin",
"Niacin",
"Pantothenic acid",
"Vitamin D (D2 + D3)",
"Vitamin E (alpha-tocopherol)",
"Vitamin K (phylloquinone)",
"Phosphorus, P"
]

# Hitung jumlah constraint yang tersedia
data["HC_count"] = data[HC].notna().sum(axis=1)
data["SC_count"] = data[SC].notna().sum(axis=1)

# Filter dataset
filtered = data[
    (data["HC_count"] == 19) &
    (data["SC_count"] >= 11)
]

print("Jumlah dataset final:", len(filtered))

# Simpan dataset
filtered.to_csv(
    "Data Processed/final_dataset_4012.csv",
    index=False
)

print("Dataset final berhasil disimpan.")
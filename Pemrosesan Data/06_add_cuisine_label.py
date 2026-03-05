import pandas as pd


# ==============================
# LOAD DATASET
# ==============================

data = pd.read_csv("./Data Processed/05_final_dataset.csv", encoding="utf-8")

print("Jumlah data awal:", len(data))


# ==============================
# KEYWORD CUISINE
# ==============================

western_keywords = [
    "bread", "toast", "sandwich", "burger", "hamburger",
    "pizza", "pasta", "spaghetti", "macaroni", "lasagna",
    "biscuit", "bagel",
    "cheddar", "parmesan", "mozzarella",
    "steak",
    "sausage", "ham", "bacon",
    "omelet", "omelette",
    "pancake", "waffle",
    "cake", "cookie", "brownie",
    "pie", "muffin"
]


asian_keywords = [
    "rice",
    "noodle", "ramen", "udon", "soba",
    "soy", "tofu",
    "kimchi",
    "miso",
    "teriyaki",
    "curry",
    "sesame",
    "ginger"
]


# ==============================
# FUNCTION CLASSIFICATION
# ==============================

def classify_cuisine(name):

    name = str(name).lower()

    # PRIORITAS ASIAN
    for k in asian_keywords:
        if k in name:
            return "Asian"

    # PRIORITAS WESTERN
    for k in western_keywords:
        if k in name:
            return "Western"

    return "Other"


# ==============================
# APPLY CLASSIFICATION
# ==============================

data["cuisine"] = data["food_name"].apply(classify_cuisine)


# ==============================
# CEK DISTRIBUSI
# ==============================

print("\nDistribusi cuisine:")
print(data["cuisine"].value_counts())


# ==============================
# SAVE DATASET BARU
# ==============================

data.to_csv(
    "./Data Processed/06_final_dataset_with_cuisine.csv",
    index=False
)

print("\nDataset baru berhasil disimpan:")
print("Data Processed/06_final_dataset_with_cuisine.csv")
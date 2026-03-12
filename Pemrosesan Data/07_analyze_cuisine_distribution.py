import pandas as pd


# ==============================
# LOAD DATASET
# ==============================

data = pd.read_csv("./Data Processed/06_final_cek_cuisine_manual.csv")

print("Jumlah data:", len(data))


# ==============================
# DISTRIBUSI CUISINE
# ==============================

print("\nDistribusi cuisine:")
print(data["cuisine"].value_counts())


# ==============================
# DISTRIBUSI FOOD TYPE
# ==============================

print("\nDistribusi food_type:")
print(data["food_type"].value_counts())


# ==============================
# CUISINE x FOOD TYPE
# ==============================

print("\nDistribusi food_type per cuisine:\n")

table = pd.crosstab(
    data["cuisine"],
    data["food_type"]
)

print(table)


# ==============================
# SAVE ANALYSIS
# ==============================

table.to_csv(
"./Data Processed/07_cuisine_foodtype_distribution.csv"
)

print("\nTabel distribusi disimpan di:")
print("Data Processed/07_cuisine_foodtype_distribution.csv")
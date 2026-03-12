import pandas as pd


# ==============================
# LOAD DATASET
# ==============================

data = pd.read_csv("./Data Processed/06_final_cek_cuisine_manual.csv")

print("Jumlah data sebelum hapus baby food:", len(data))


# ==============================
# HAPUS BABY FOOD
# ==============================

data_no_baby = data[
    data["food_group"] != "Baby Foods"
]


print("Jumlah data setelah hapus baby food:", len(data_no_baby))


# ==============================
# SAVE DATASET BARU
# ==============================

data_no_baby.to_csv(
    "./Data Processed/08_data_cek_manual_no_babyfood.csv",
    index=False
)

print("\nDataset berhasil disimpan:")
print("Data Processed/08_data_cek_manual_no_babyfood.csv")
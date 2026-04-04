# import pandas as pd

# # ================= LOAD DATA =================
# df = pd.read_csv("A. Data/Data Processed/05_final_dataset.csv")

# print("Jumlah data:", len(df))
# print("="*50)


# # ================= KOLOM YANG DICEK =================
# cols = ["carbohydrate_g", "protein_g", "fat_g"]


# # ================= STATISTIK DASAR =================
# print("\nSTATISTIK DESKRIPTIF")
# print(df[cols].describe())


# # ================= CEK NILAI 0 =================
# print("\nJUMLAH NILAI 0")
# for col in cols:
#     print(f"{col}: {(df[col] == 0).sum()}")


# # ================= CEK NILAI NULL =================
# print("\nJUMLAH NULL")
# print(df[cols].isnull().sum())


# # ================= CEK NILAI EKSTREM =================
# print("\nNILAI TERBESAR")
# print(df[cols].max())

# print("\nNILAI TERKECIL")
# print(df[cols].min())


# # ================= CEK DATA ANEH =================
# print("\nDATA ANEH (protein=0 & fat=0 & carbo=0)")
# weird = df[
#     (df["protein_g"] == 0) &
#     (df["fat_g"] == 0) &
#     (df["carbohydrate_g"] == 0)
# ]

# print("Jumlah:", len(weird))


# # ================= CEK DISTRIBUSI SIMPEL =================
# print("\nDISTRIBUSI SEDERHANA")

# for col in cols:
#     print(f"\n{col}:")
#     print(df[col].value_counts(bins=5))
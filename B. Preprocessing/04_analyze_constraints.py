import pandas as pd

data = pd.read_csv("A. Data/Data Processed/03_dataset_halal.csv")

print("Jumlah kolom dataset:", len(data.columns))
print("Jumlah total makanan:", len(data))

# ======================
# HARD CONSTRAINT (UPDATED)
# ======================
HC = [
    "water_g","energy_kcal","potassium_mg","calcium_mg",
    "carbohydrate_g","cholesterol_mg","saturated_fat_g",
    "fat_g","magnesium_mg","sodium_mg","protein_g","zinc_mg",
    "phosphorus_mg","fiber_g","vitamin_a_rae_mg","vitamin_b12_mg",
    "vitamin_b6_mg","vitamin_c_mg","iron_mg","trans_fat_g"
]

# ======================
# SOFT CONSTRAINT (UPDATED)
# ======================
SC = [
    "sugar_g","fluoride_mg","folate_mg","choline_mg",
    "manganese_mg","selenium_mg","copper_mg","vitamin_b1_thiamin_mg","vitamin_b2_riboflavin_mg",
    "vitamin_b3_niacin_mg","vitamin_b5_pantothenic_acid_mg","vitamin_d_mg",
    "vitamin_e_mg","vitamin_k_mg"
]

# ======================
# CEK KOLUMN YANG ADA
# ======================

HC_exist = [c for c in HC if c in data.columns]
SC_exist = [c for c in SC if c in data.columns]

print("HC ditemukan:", len(HC_exist))
print("SC ditemukan:", len(SC_exist))

print("HC missing:", set(HC) - set(HC_exist))
print("SC missing:", set(SC) - set(SC_exist))


# ======================
# HITUNG JUMLAH NUTRIENT TIDAK NULL
# ======================

data["HC_count"] = data[HC_exist].notna().sum(axis=1)
data["SC_count"] = data[SC_exist].notna().sum(axis=1)


# ======================
# ANALISIS KOMBINASI HC SC
# ======================

analysis = (
    data.groupby(["HC_count","SC_count"])
    .size()
    .reset_index(name="Total Makanan")
    .sort_values(["HC_count","SC_count"], ascending=[False,False])
)

print("\nJumlah kombinasi constraint:", len(analysis))


# ======================
# CEK MAKANAN SEMUA NUTRIENT NULL
# ======================

all_null = data[
    (data["HC_count"] == 0) &
    (data["SC_count"] == 0)
]

jumlah_all_null = len(all_null)

print("\nJumlah makanan dengan semua nutrient NULL:", jumlah_all_null)


# ======================
# TAMBAHKAN BARIS KE HASIL
# ======================

if jumlah_all_null > 0:
    extra_row = pd.DataFrame({
        "HC_count":[0],
        "SC_count":[0],
        "Total Makanan":[jumlah_all_null]
    })
    
    analysis = pd.concat([analysis, extra_row], ignore_index=True)


# ======================
# SIMPAN HASIL
# ======================

analysis.to_csv(
    "A. Data/Data Processed/04_hc_sc_analysis.csv",
    index=False
)

print("\nHasil analisis (20 teratas):")
print(analysis.head(20))
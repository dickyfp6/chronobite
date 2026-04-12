import pandas as pd
import os


# =====================================================
# PATH PROJECT
# =====================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))

FOOD_PATH = os.path.join(PROJECT_ROOT, "Data Processed", "06_final_cek_cuisine_manual.csv")
AKG_PATH = os.path.join(PROJECT_ROOT, "Data Raw", "akg.csv")
GUIDELINE_PATH = os.path.join(PROJECT_ROOT, "Data Raw", "guideline.csv")


# =====================================================
# 34 NUTRIENTS (sesuai dataset USDA)
# =====================================================

NUTRIENT_COLUMNS = [

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
    "Iron, Fe",

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


# =====================================================
# LOAD FOOD DATASET
# =====================================================

def load_food_dataset():

    df = pd.read_csv(FOOD_PATH)

    # bersihkan nama kolom
    df.columns = df.columns.str.strip()

    # pastikan kolom penting ada
    required_columns = [
        "fdc_id",
        "food_name",
        "food_group",
        "food_type",
        "cuisine"
    ]

    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Column {col} tidak ditemukan di dataset")

    # konversi nutrisi menjadi numeric
    for col in NUTRIENT_COLUMNS:

        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
        else:
            # jika kolom nutrisi tidak ada → buat 0
            df[col] = 0

    # pastikan id numeric
    df["fdc_id"] = pd.to_numeric(df["fdc_id"], errors="coerce")

    return df


# =====================================================
# LOAD AKG DATASET
# =====================================================

def load_akg_dataset():

    akg = pd.read_csv(AKG_PATH)

    akg.columns = akg.columns.str.strip()

    return akg


# =====================================================
# LOAD GUIDELINE PENYAKIT
# =====================================================

def load_guideline_dataset():

    guideline = pd.read_csv(GUIDELINE_PATH)

    guideline.columns = guideline.columns.str.strip()

    return guideline


# =====================================================
# TEST
# =====================================================

if __name__ == "__main__":

    print("=== DATASET PATH CHECK ===")

    print("Food dataset:", FOOD_PATH)
    print("AKG dataset:", AKG_PATH)
    print("Guideline dataset:", GUIDELINE_PATH)

    print("\n=== LOADING DATA ===")

    food_df = load_food_dataset()
    akg_df = load_akg_dataset()
    guideline_df = load_guideline_dataset()

    print("\nFood dataset shape:", food_df.shape)
    print("AKG dataset shape:", akg_df.shape)
    print("Guideline dataset shape:", guideline_df.shape)

    print("\n=== SAMPLE FOOD DATA ===")
    print(food_df.head())

    print("\n=== SAMPLE NUTRIENTS ===")
    print(food_df[NUTRIENT_COLUMNS].head())
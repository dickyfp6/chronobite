import pandas as pd
from pathlib import Path
import sys

# ======================
# STEP 05: APPLY ML + FINAL DATASET
# ======================
# This step combines:
# - ML classification (from previous step 04)
# - HC/SC filtering
# - Deduplication and normalization

# Import classifier
ml_path = Path(__file__).parent / 'ML Klasifikasi'
sys.path.insert(0, str(ml_path))
from food_classifier import FoodClassifier  # type: ignore


# ======================
# APPLY ML CLASSIFICATION
# ======================
print("\n" + "="*70)
print("STEP 05: Apply ML Classification + Final Dataset")
print("="*70)

print("\n[1/4] Loading ML classifier...")
model_path = Path(__file__).parent / 'ML Klasifikasi/food_classifier_model.pkl'
classifier = FoodClassifier.load(str(model_path))
print(f"✓ Model loaded: {model_path}")

print(f"\n[2/4] Loading raw data (03_dataset_halal.csv)...")
input_file = Path(__file__).parent.parent / 'A. Data/Data Processed/03_dataset_halal.csv'
data = pd.read_csv(input_file)
print(f"✓ Loaded {len(data)} items")

print(f"\n[3/4] Predicting consumption labels...")
data['consumption_label'] = classifier.predict(data)
print(f"✓ Labels predicted")
print("\nLabel Distribution (before HC/SC filter):")
print(data['consumption_label'].value_counts())

print(f"\nJumlah data awal: {len(data)}")


# ======================
# HARD CONSTRAINT
# ======================
HC = [ "Water","Energy", "Potassium, K", "Calcium, Ca",
"Carbohydrate, by difference", "Cholesterol", "Fatty acids, total saturated",
"Total lipid (fat)", "Magnesium, Mg", "Sodium, Na", "Protein", "Zinc, Zn", 
"Phosphorus, P", "Fiber, total dietary", "Vitamin A, RAE", "Vitamin B-12",
"Vitamin B-6", "Vitamin C, total ascorbic acid", "Iron, Fe", "Fatty acids, total trans"
]

# ======================
# SOFT CONSTRAINT
# ======================
SC = [ "Sugars, Total", "Fluoride, F", "Folate, DFE", "Choline, total",
"Manganese, Mn", "Selenium, Se", "Copper, Cu", "Thiamin", "Riboflavin",
"Niacin", "Pantothenic acid", "Vitamin D (D2 + D3)",
"Vitamin E (alpha-tocopherol)", "Vitamin K (phylloquinone)"
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
    (data["HC_count"] >= 19) &
    (data["SC_count"] >= 8)
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
# FOOD TYPE MAPPING (via ML)
# ======================

# consumption_label sudah ada dari ML classification
if 'consumption_label' not in filtered.columns:
    print("\nWarning: consumption_label tidak ditemukan, menggunakan fallback mapping...")
    
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
    
    filtered["consumption_label"] = filtered["food_group"].map(food_type_map)


# ======================
# CEK DISTRIBUSI FINAL
# ======================
print("\n[4/4] Final distribution after HC/SC filtering:")
print(filtered["consumption_label"].value_counts())


# ======================
# SIMPAN DATASET FINAL
# ======================
output_file = Path(__file__).parent.parent / 'A. Data/Data Processed/05_final_dataset.csv'
filtered.to_csv(output_file, index=False)

print("\n" + "="*70)
print("✓ COMPLETE - Dataset berhasil disimpan")
print("="*70)
print(f"Total items final: {len(filtered)}")
print(f"Distribution: {dict(filtered['consumption_label'].value_counts())}")
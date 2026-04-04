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

print(f"\n[3/4] Predicting consumption and cuisine labels...")
predictions = classifier.predict(data, return_both=True)
data['consumption_label'] = predictions.get('consumption_label', 'Snack')
data['cuisine_label'] = predictions.get('cuisine_label', 'Generic')

# Clean up cuisine labels (remove leading/trailing spaces)
if 'cuisine_label' in data.columns:
    data['cuisine_label'] = data['cuisine_label'].str.strip()

print(f"✓ Labels predicted")

print(f"\nJumlah data awal: {len(data)}")

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
# HITUNG HC SC
# ======================
data["HC_count"] = data[HC].notna().sum(axis=1)
data["SC_count"] = data[SC].notna().sum(axis=1)


# ======================
# FILTER DATASET
# ======================
filtered = data[
    (data["HC_count"] >= 18) &
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
# CUISINE LABEL (from ML)
# ======================
# Cuisine label sudah ada dari ML prediction


# ======================
# CEK DISTRIBUSI FINAL
# ======================
print("\n[4/4] Final distribution after HC/SC filtering:")
print("\n" + "-"*70)
print("CONSUMPTION DISTRIBUTION:")
print("-"*70)
for label, count in filtered["consumption_label"].value_counts().items():
    pct = (count / len(filtered)) * 100
    print(f"  {label:15s}: {count:5d} ({pct:5.1f}%)")

print("\n" + "-"*70)
print("CUISINE DISTRIBUTION:")
print("-"*70)
for label, count in filtered["cuisine_label"].value_counts().items():
    pct = (count / len(filtered)) * 100
    print(f"  {label:15s}: {count:5d} ({pct:5.1f}%)")
print("-"*70)


# ======================
# SIMPAN DATASET FINAL
# ======================
output_file = Path(__file__).parent.parent / 'A. Data/Data Processed/05_final_dataset.csv'
filtered.to_csv(output_file, index=False)

print("\n" + "="*70)
print("✓ COMPLETE - Dataset berhasil disimpan")
print("="*70)
print(f"\n📊 SUMMARY:")
print(f"  Total items: {len(filtered)}")
print(f"  Output file: {output_file}")
print("\n" + "="*70)
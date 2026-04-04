import pandas as pd

print("="*70)
print("ANALISIS CUISINE DISTRIBUTION - Training vs Prediction")
print("="*70)

# Load original labels
label_cuisine = pd.read_csv('A. Data/Data Raw/label_cuisine.csv')

print("\n[1] ORIGINAL LABEL_CUISINE DISTRIBUTION:")
print("-"*70)
print("\nAuto predictions (cuisine_auto):")
print(label_cuisine['cuisine_auto'].value_counts())

print("\nManual validations (cuisine_manual):")
manual_counts = label_cuisine['cuisine_manual'].value_counts()
print(manual_counts)

print(f"\n✓ Total manual validated: {manual_counts.sum()}")
print(f"✓ Total missing manual: {label_cuisine['cuisine_manual'].isna().sum()}")

# Load training data
label_makanan = pd.read_csv('A. Data/Data Raw/label_makanan.csv', sep=';')
label_cuisine_merged = label_makanan.merge(
    label_cuisine[['fdc_id', 'cuisine_manual', 'cuisine_auto']],
    on='fdc_id',
    how='left'
)

# Simulate training data
training_cuisine = label_cuisine_merged['cuisine_manual'].fillna(label_cuisine_merged['cuisine_auto'])
print("\n[2] TRAINING DATA CUISINE DISTRIBUTION (4263 items):")
print("-"*70)
print(training_cuisine.value_counts())

# Load final dataset
final_df = pd.read_csv('A. Data/Data Processed/05_final_dataset.csv')
print("\n[3] FINAL DATASET CUISINE DISTRIBUTION (after HC/SC filter):")
print("-"*70)
print(final_df['cuisine_label'].value_counts())

print("\n[4] COMPARISON:")
print("-"*70)
for cuisine in ['Western', 'Asian', 'Mediterranean', 'Generic']:
    training = (training_cuisine.str.strip() == cuisine).sum() if not training_cuisine.isna().all() else 0
    try:
        final = (final_df['cuisine_label'].str.strip() == cuisine).sum()
    except:
        final = (final_df['cuisine_label'] == cuisine).sum()
    
    print(f"  {cuisine:15s} - Training: {training:4d} → Final: {final:4d}")

print("\n[5] INSIGHTS:")
print("-"*70)
print("✓ Western mendominasi karena USDA database lebih banyak produk Western")
print("✓ Asian & Mediterranean adalah minority classes (data imbalance)")
print("✓ Ini BUKAN kesalahan ML, tapi karakteristik dataset")
print("-"*70)

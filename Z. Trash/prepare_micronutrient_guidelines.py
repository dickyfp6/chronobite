import pandas as pd
import numpy as np

print("="*70)
print("PREPARE MICRONUTRIENT GUIDELINES - Exact Values Only")
print("="*70)

# Load DRI
dri = pd.read_csv("A. Data/Data Raw/dri.csv")
print(f"\n[1] Loading DRI data: {len(dri)} age/gender groups")

# Extract micronutrient columns (exclude macronutrient)
macro_cols = {'age_min', 'age_max', 'gender', 'energy_kcal', 'protein_g', 
              'avg_protein_g', 'min_fat_g', 'max_fat_g', 'avg_carb_g', 
              'min_carb_g', 'max_carb_g', 'fiber_g', 'water_g'}

micro_cols = [col for col in dri.columns if col not in macro_cols]

print(f"\n[2] Found {len(micro_cols)} micronutrient columns:")
for i, col in enumerate(micro_cols, 1):
    print(f"    {i:2d}. {col}")

# Create micronutrient reference table
micro_ref = dri[['age_min', 'age_max', 'gender'] + micro_cols].copy()

print(f"\n[3] Micronutrient Reference Table Structure:")
print(f"    Rows: {len(micro_ref)} (age/gender groups)")
print(f"    Columns: {len(micro_ref.columns)} (age_min, age_max, gender + {len(micro_cols)} nutrients)")

# Display sample
print(f"\n[4] Sample data (Males 14-18):");
print(micro_ref.iloc[0].to_string())

# Save
output_file = "A. Data/Data Processed/guideline_micronutrient.csv"
micro_ref.to_csv(output_file, index=False)
print(f"\n✓ Saved: {output_file}")

# Check against final dataset
final_df = pd.read_csv("A. Data/Data Processed/05_final_dataset.csv")
print(f"\n[5] Mapping Check with 05_final_dataset.csv:")
print(f"    Final dataset columns: {len(final_df.columns)}")

# Compare which micronutrients are in final dataset
final_cols = set(final_df.columns)
micro_set = set(micro_cols)
matched = micro_set & final_cols
missing = micro_set - final_cols
extra = final_cols - micro_set - {'fdc_id', 'food_name', 'food_group', 'consumption_label', 'cuisine_label'}

print(f"\n    ✓ Matched micronutrients: {len(matched)}")
for col in sorted(matched)[:5]:
    print(f"      • {col}")
if len(matched) > 5:
    print(f"      ... dan {len(matched)-5} lagi")

if missing:
    print(f"\n    ❌ Missing in final_dataset: {len(missing)}")
    for col in sorted(missing):
        print(f"      • {col}")

print(f"\n" + "="*70)
print(f"✓ READY FOR MAPPING - guideline_micronutrient.csv siap digunakan")
print("="*70)

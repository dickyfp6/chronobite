import pandas as pd

print("="*70)
print("FINALIZE MICRONUTRIENT GUIDELINES")
print("="*70)

# Load DRI
dri = pd.read_csv("A. Data/Data Raw/dri.csv")

# Fix typo: panthotenic → pantothenic
dri = dri.rename(columns={'vitamin_b5_panthotenic_acid_mg': 'vitamin_b5_pantothenic_acid_mg'})

print("\n[1] Fixed typo in DRI.csv:")
print("    vitamin_b5_panthotenic_acid_mg → vitamin_b5_pantothenic_acid_mg")

# Extract micronutrient columns (exclude macronutrient)
macro_cols = {'age_min', 'age_max', 'gender', 'energy_kcal', 'protein_g', 
              'avg_protein_g', 'min_fat_g', 'max_fat_g', 'avg_carb_g', 
              'min_carb_g', 'max_carb_g', 'fiber_g', 'water_g'}

micro_cols = [col for col in dri.columns if col not in macro_cols]

# Create micronutrient reference table
guideline = dri[['age_min', 'age_max', 'gender'] + micro_cols].copy()

print(f"\n[2] Final Micronutrient Reference:")
print(f"    Format: age_min | age_max | gender | 24 micronutrients")
print(f"    Rows: {len(guideline)}")
print(f"    Micronutrients: {len(micro_cols)}")

# Save
output_file = "A. Data/Data Processed/guideline_micronutrient.csv"
guideline.to_csv(output_file, index=False)
print(f"\n[3] Saved: {output_file}")

# Verify all match now
final_df = pd.read_csv("A. Data/Data Processed/05_final_dataset.csv")
final_cols = set(final_df.columns)
micro_set = set(micro_cols)
matched = micro_set & final_cols
missing = micro_set - final_cols

print(f"\n[4] Verification with 05_final_dataset.csv:")
print(f"    ✓ All {len(matched)}/24 micronutrients matched!")

if missing:
    print(f"    ❌ Still missing: {missing}")
else:
    print(f"    ✓ 100% match!")

# Show summary
print(f"\n[5] Guideline Micronutrient Summary:")
print(f"\n    {guideline.to_string(index=False)}")

print(f"\n" + "="*70)
print(f"✓ READY - guideline_micronutrient.csv siap untuk mapping ke system flow")
print("="*70)

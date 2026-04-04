import pandas as pd

print("="*70)
print("COMPARE: Wide Format vs Long Format")
print("="*70)

# Load current guideline (wide format)
wide = pd.read_csv("A. Data/Data Processed/guideline_micronutrient.csv")

print("\n[1] CURRENT FORMAT (WIDE):")
print(f"    Rows: {len(wide)}")
print(f"    Columns: {len(wide.columns)}")
print(f"    Total cells: {len(wide) * len(wide.columns)}")
print("\n    Structure:")
print(wide.head(2).to_string())

# Convert to long format
micro_cols = [col for col in wide.columns if col not in ['age_min', 'age_max', 'gender']]
long = wide.melt(
    id_vars=['age_min', 'age_max', 'gender'],
    value_vars=micro_cols,
    var_name='nutrient',
    value_name='value'
)

print("\n[2] LONG FORMAT (Alternative):")
print(f"    Rows: {len(long)}")
print(f"    Columns: {len(long.columns)}")
print(f"    Total cells: {len(long) * len(long.columns)}")
print("\n    Structure:")
print(long.head(10).to_string())

print("\n[3] USE CASE COMPARISON:")
print("\n    WIDE format:")
print("    ✓ Compact (10 rows)")
print("    ✓ All age_group in satu view")
print("    ✗ Sulit filter per-nutrient")
print("    ✗ Tidak normalized untuk mapping")
print("\n    LONG format:")
print("    ✓ Normalized (1 nutrient per row)")
print("    ✓ Easy to filter/merge by nutrient")
print("    ✓ Better untuk database design")
print("    ✗ Lebih banyak rows (240 rows)")

print("\n[4] UNTUK SYSTEM FLOW (genetic algorithm):")
print("    Kemungkinan kebutuhan:")
print("    • User select age + gender")
print("    • Ambil 24 requirement untuk user → WIDE lebih praktis")
print("    • Atau iterate per nutrient untuk check satu-satu → LONG lebih praktis")

print("\n" + "="*70)
print("❓ PERTANYAAN: Nanti di system flow, data flow gimana?")
print("   Apakah filter by (age, gender) dulu baru ambil all 24 nutrients?")
print("   Atau filter per nutrient?")
print("="*70)

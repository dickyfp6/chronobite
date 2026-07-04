import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.normpath(os.path.join(CURRENT_DIR, "..", "A. Data", "Data Processed"))

# Funnel Table Data Collection
try:
    c1 = len(pd.read_csv(os.path.join(DATA_DIR, "01_base_dataset.csv")))
    c2 = len(pd.read_csv(os.path.join(DATA_DIR, "02_cleaned_dataset.csv")))
    c3 = len(pd.read_csv(os.path.join(DATA_DIR, "03_final_dataset.csv")))
    c4 = len(pd.read_csv(os.path.join(DATA_DIR, "04_super_final.csv")))
    print("="*50)
    print("FUNNEL TABLE (Pengurangan Item Data)")
    print(f"Tahap 1 (Dataset Awal): {c1} item")
    print(f"Tahap 2 (Filtering Rule-Based): {c2} item (Sisa {(c2/c1*100):.1f}%)")
    print(f"Tahap 3 (Missing Value & Ambang Batas): {c3} item (Sisa {(c3/c1*100):.1f}%)")
    print(f"Tahap 4 (Dataset Final + AI Labels): {c4} item (Sisa {(c4/c1*100):.1f}%)")
    print("="*50)
except Exception as e:
    print(f"Error reading datasets for funnel table: {e}")

# Visualization using final dataset
df = pd.read_csv(os.path.join(DATA_DIR, "04_super_final.csv"))

plt.figure(figsize=(8, 6))

# Heatmap: Cross-tabulation
crosstab = pd.crosstab(df['consumption_label'], df['cuisine'])
# Reorder index
crosstab = crosstab.reindex(['Main Course', 'Side Dish', 'Snack', 'Drink'])

sns.heatmap(crosstab, annot=True, fmt='d', cmap='YlGnBu', cbar=True)
plt.title('Heatmap: Jenis Makanan vs Cuisine', fontsize=14, pad=15)
plt.xlabel('Cuisine', fontsize=12)
plt.ylabel('Jenis Makanan', fontsize=12)

plt.tight_layout()
output_path = os.path.join(CURRENT_DIR, "distribution_heatmap.png")
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"Chart saved to: {output_path}")

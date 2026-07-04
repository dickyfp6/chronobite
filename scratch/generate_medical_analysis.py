import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.normpath(os.path.join(CURRENT_DIR, "..", "A. Data", "Data Processed", "04_super_final.csv"))

df = pd.read_csv(FILE_PATH)

# Define safe conditions
df['safe_hypertension'] = df['sodium_mg'] <= 600
df['safe_diabetes'] = df['carbohydrate_g'] <= 50
df['safe_ckd'] = (df['protein_g'] <= 15) & (df['phosphorus_mg'] <= 300)
df['safe_cvd'] = (df['cholesterol_mg'] <= 60) & (df['saturated_fat_g'] <= 5)

conditions = [
    ('safe_hypertension', 'Hipertensi (Sodium ≤ 600mg)'),
    ('safe_diabetes', 'Diabetes (Karbohidrat ≤ 50g)'),
    ('safe_ckd', 'CKD (Protein ≤ 15g, Fosfor ≤ 300mg)'),
    ('safe_cvd', 'CVD (Kolesterol ≤ 60mg, Lemak Jenuh ≤ 5g)')
]

plt.figure(figsize=(14, 10))

for i, (col, title) in enumerate(conditions, 1):
    plt.subplot(2, 2, i)
    
    # Calculate counts of safe vs unsafe per consumption_label
    counts = df.groupby(['consumption_label', col]).size().unstack(fill_value=0)
    
    # Rename columns to strings to avoid pandas boolean indexing issues
    counts.rename(columns={True: 'Aman', False: 'Tidak Aman'}, inplace=True)
    
    # Ensure both columns exist
    if 'Aman' not in counts.columns: counts['Aman'] = 0
    if 'Tidak Aman' not in counts.columns: counts['Tidak Aman'] = 0
        
    counts = counts[['Aman', 'Tidak Aman']] # Order: Safe, Unsafe
    
    # Calculate percentages for labels
    totals = counts.sum(axis=1)
    safe_pct = (counts['Aman'] / totals * 100).round(1)
    
    # Plot stacked bar
    ax = counts.plot(kind='barh', stacked=True, color=['#2ca02c', '#d62728'], ax=plt.gca(), legend=False)
    
    plt.title(title, fontsize=12, pad=10)
    plt.xlabel('Jumlah Item Makanan', fontsize=10)
    plt.ylabel('Jenis Makanan', fontsize=10)
    
    # Add percentage text on the green bars
    for j, (p, pct) in enumerate(zip(ax.patches[:len(counts)], safe_pct)):
        width, height = p.get_width(), p.get_height()
        x, y = p.get_xy() 
        if width > 0:
            ax.text(x + width/2, 
                    y + height/2, 
                    f'{pct}%', 
                    ha='center', 
                    va='center', 
                    color='white',
                    fontweight='bold',
                    fontsize=9)

# Add a single legend at the top
plt.figlegend(['Aman (Memenuhi Batasan)', 'Tidak Aman (Melebihi Batas)'], 
              loc='upper center', ncol=2, fontsize=11, bbox_to_anchor=(0.5, 1.02))

plt.tight_layout()
output_path = os.path.join(CURRENT_DIR, "medical_safety_chart.png")
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"Chart saved to: {output_path}")

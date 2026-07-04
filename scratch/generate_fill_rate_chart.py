import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.normpath(os.path.join(CURRENT_DIR, "..", "A. Data", "Data Processed", "02_cleaned_dataset.csv"))

HC = [
    "energy_kcal", "protein_g", "carbohydrate_g", "fat_g",
    "fiber_g", "water_g", "vitamin_a_rae_mg", "cholesterol_mg",
    "saturated_fat_g", "trans_fat_g", "phosphorus_mg", "potassium_mg",
    "sodium_mg", "zinc_mg", "calcium_mg", "iron_mg",
    "magnesium_mg", "vitamin_b12_mg", "vitamin_b6_mg", "vitamin_c_mg"
]

SC = [
    "sugar_g", "fluoride_mg", "folate_mg", "choline_mg",
    "manganese_mg", "selenium_mg", "copper_mg",
    "vitamin_b1_thiamin_mg", "vitamin_b2_riboflavin_mg",
    "vitamin_b3_niacin_mg", "vitamin_b5_pantothenic_acid_mg",
    "vitamin_d_mg", "vitamin_e_mg", "vitamin_k_mg"
]

# Load data
df = pd.read_csv(FILE_PATH)

# Calculate fill rate
fill_rates = {}
for col in HC + SC:
    if col in df.columns:
        fill_rates[col] = df[col].notna().mean() * 100

# Convert to DataFrame
df_fill = pd.DataFrame(list(fill_rates.items()), columns=["Nutrisi", "Fill Rate (%)"])
df_fill["Tipe"] = df_fill["Nutrisi"].apply(lambda x: "Hard Constraint (HC)" if x in HC else "Soft Constraint (SC)")
df_fill = df_fill.sort_values(by="Fill Rate (%)", ascending=False).reset_index(drop=True)

# Save chart
plt.figure(figsize=(12, 10))
ax = sns.barplot(x="Fill Rate (%)", y="Nutrisi", hue="Tipe", data=df_fill, dodge=False, palette={"Hard Constraint (HC)": "#ff7f0e", "Soft Constraint (SC)": "#1f77b4"})
plt.axvline(x=80, color='gray', linestyle='--', label='Threshold 80%')

# Add labels to the right of each bar
for p in ax.patches:
    width = p.get_width()
    if pd.notna(width) and width > 0:
        ax.text(width + 1,
                p.get_y() + p.get_height() / 2,
                f'{width:.1f}%',
                ha='left',
                va='center',
                fontsize=9)

plt.title("Persentase Keterisian Data (Fill Rate) per Atribut Nutrisi pada Dataset Awal", fontsize=14, pad=15)
plt.xlabel("Fill Rate (%)", fontsize=12)
plt.ylabel("Atribut Nutrisi", fontsize=12)
plt.legend(title="Kategori Nutrisi", loc='lower right')
plt.xlim(0, 110) # Give space for text labels
plt.tight_layout()

output_path = os.path.join(CURRENT_DIR, "fill_rate_chart.png")
plt.savefig(output_path, dpi=300)
print(f"Chart saved to: {output_path}")

# Print table for LLM reference
print("\nTABEL FILL RATE NUTRISI:")
print(df_fill.to_string())

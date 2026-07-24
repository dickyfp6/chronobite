import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
import os

"""
Script 05: EDA Visualization
Tujuan: Membuat visualisasi untuk analisis data eksploratif (EDA) pada dataset final.
Menghasilkan 5 grafik:
1. Distribusi jumlah item per kategori slot (consumption_label)
2. Distribusi jumlah item per kelompok kategori USDA (food_group)
3. Fill rate per atribut nutrisi (HC dan SC) -- dihitung dari dataset sebelum fillna
4. Kelayakan batasan medis per kategori slot untuk masing-masing penyakit
5. Heatmap distribusi jenis makanan vs cuisine
"""

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Dataset final (04_super_final.csv) untuk grafik distribusi, kelayakan medis, dan heatmap
INPUT_FILE = os.path.normpath(os.path.join(CURRENT_DIR, "..", "A. Data", "Data Processed", "04_super_final.csv"))

# Dataset sebelum fillna (02_cleaned_dataset.csv setelah filter HC/SC) untuk fill rate
INPUT_FILE_BEFORE_FILLNA = os.path.normpath(os.path.join(CURRENT_DIR, "..", "A. Data", "Data Processed", "02_cleaned_dataset.csv"))

OUTPUT_DIR = os.path.normpath(os.path.join(CURRENT_DIR, "EDA Visualization"))

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


def chart_distribusi_slot(df, output_dir):
    """Chart 0a: Distribusi jumlah item per kategori slot (consumption_label)."""
    counts = df["consumption_label"].value_counts()
    order = ["Snack", "Side Dish", "Main Course", "Drink"]
    counts = counts.reindex(order)
    total = counts.sum()

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(counts.index, counts.values, color="#3B6F8F")
    for bar, val in zip(bars, counts.values):
        pct = val / total * 100
        ax.text(bar.get_x() + bar.get_width() / 2, val + 10, f"{val}\n({pct:.1f}%)",
                 ha="center", va="bottom", fontsize=9)

    ax.set_xlabel("Kategori Slot")
    ax.set_ylabel("Jumlah Item")
    ax.set_title("Distribusi Jumlah Item Makanan per Kategori Slot")
    ax.set_ylim(0, counts.max() * 1.2)

    plt.tight_layout()
    out_path = os.path.join(output_dir, "4_3_1_distribusi_slot.png")
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"[OK] Tersimpan: {out_path}")

    return counts


def chart_distribusi_food_group(df, output_dir, top_n=15):
    """Chart 0b: Distribusi jumlah item per kelompok kategori USDA (food_group), top N."""
    counts = df["food_group"].value_counts().head(top_n)

    fig, ax = plt.subplots(figsize=(9, 7))
    ax.barh(counts.index[::-1], counts.values[::-1], color="#E07B39")
    for i, val in enumerate(counts.values[::-1]):
        ax.text(val + 3, i, str(val), va="center", fontsize=8)

    ax.set_xlabel("Jumlah Item")
    ax.set_ylabel("Kelompok Kategori USDA (food_group)")
    ax.set_title(f"Distribusi Jumlah Item per Kelompok Kategori USDA (Top {top_n})")

    plt.tight_layout()
    out_path = os.path.join(output_dir, "4_3_1_distribusi_food_group.png")
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"[OK] Tersimpan: {out_path}")

    return counts


def chart_fill_rate(df_before_fillna, output_dir):
    """Chart 1: Fill rate per atribut nutrisi (HC dan SC).
    Dihitung dari seluruh dataset sebelum fillna (02_cleaned_dataset.csv, tanpa filter apa pun)
    menggunakan notna() agar nilai nol asli tidak dihitung sebagai data kosong.
    """
    total = len(df_before_fillna)

    hc_fill = pd.Series({c: df_before_fillna[c].notna().sum() / total * 100 for c in HC})
    sc_fill = pd.Series({c: df_before_fillna[c].notna().sum() / total * 100 for c in SC})
    all_fill = pd.concat([hc_fill, sc_fill]).sort_values(ascending=False)
    colors = ["#E07B39" if c in HC else "#3B6F8F" for c in all_fill.index]

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.barh(all_fill.index[::-1], all_fill.values[::-1], color=colors[::-1])
    ax.axvline(80, color="gray", linestyle="--", linewidth=1)
    all_fill_rev = all_fill[::-1]
    for i, (nutrient_name, val) in enumerate(all_fill_rev.items()):
        ax.text(val + 0.5, i, f"{val:.1f}%", va="center", fontsize=8)

    ax.set_xlabel("Fill Rate (%)")
    ax.set_ylabel("Atribut Nutrisi")
    ax.set_title("Persentase Keterisian Data (Fill Rate) per Atribut Nutrisi pada Dataset Awal")
    ax.set_xlim(0, 110)

    legend_elements = [
        Patch(facecolor="#E07B39", label="Hard Constraint (HC)"),
        Patch(facecolor="#3B6F8F", label="Soft Constraint (SC)"),
        Line2D([0], [0], color="gray", linestyle="--", label="Threshold 80%"),
    ]
    ax.legend(handles=legend_elements, loc="lower right", title="Kategori Nutrisi")

    plt.tight_layout()
    out_path = os.path.join(output_dir, "4_3_3_fill_rate.png")
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"[OK] Tersimpan: {out_path}")

    return hc_fill, sc_fill


def chart_kelayakan_medis(df, output_dir):
    """Chart 2: Kelayakan batasan medis per kategori slot untuk tiap penyakit."""
    slots = ["Snack", "Side Dish", "Main Course", "Drink"]

    conditions = {
        "Hipertensi (Sodium <= 600mg)": lambda d: d["sodium_mg"] <= 600,
        "Diabetes (Karbohidrat <= 50g)": lambda d: d["carbohydrate_g"] <= 50,
        "CKD (Protein <= 15g, Fosfor <= 300mg)": lambda d: (d["protein_g"] <= 15) & (d["phosphorus_mg"] <= 300),
        "CVD (Kolesterol <= 60mg, Lemak Jenuh <= 5g)": lambda d: (d["cholesterol_mg"] <= 60) & (d["saturated_fat_g"] <= 5),
    }

    fig, axes = plt.subplots(2, 2, figsize=(12, 9))

    for ax, (title, cond) in zip(axes.flat, conditions.items()):
        aman_counts, tidak_counts = [], []
        for slot in slots:
            sub = df[df["consumption_label"] == slot]
            n = len(sub)
            aman = cond(sub).sum()
            aman_counts.append(aman)
            tidak_counts.append(n - aman)

        y_pos = np.arange(len(slots))
        ax.barh(y_pos, aman_counts, color="#2E8B57", label="Aman (Memenuhi Batasan)")
        ax.barh(y_pos, tidak_counts, left=aman_counts, color="#C0392B", label="Tidak Aman (Melebihi Batas)")

        for i, slot in enumerate(slots):
            n = len(df[df["consumption_label"] == slot])
            pct = aman_counts[i] / n * 100
            ax.text(aman_counts[i] / 2, i, f"{pct:.1f}%", va="center", ha="center",
                     fontsize=9, color="white", fontweight="bold")

        ax.set_yticks(y_pos)
        ax.set_yticklabels(slots)
        ax.set_xlabel("Jumlah Item Makanan")
        ax.set_ylabel("Jenis Makanan")
        ax.set_title(title, fontsize=10)

    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=2, bbox_to_anchor=(0.5, 0.98))
    fig.suptitle("Analisis Kelayakan Batasan Medis per Kategori Slot", fontsize=13, y=1.04)
    plt.tight_layout(rect=(0.0, 0.0, 1.0, 0.92))

    out_path = os.path.join(output_dir, "4_3_4_kelayakan_medis.png")
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"[OK] Tersimpan: {out_path}")


def chart_heatmap_cuisine(df, output_dir):
    """Chart 3: Heatmap distribusi jenis makanan vs cuisine."""
    ct = pd.crosstab(df["consumption_label"], df["cuisine"])
    ct = ct.reindex(["Main Course", "Side Dish", "Snack", "Drink"])
    ct = ct[["Asian", "Generic", "Mediterranean", "Western"]]

    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(ct.values, cmap="YlGnBu")
    ax.set_xticks(range(len(ct.columns)))
    ax.set_xticklabels(ct.columns)
    ax.set_yticks(range(len(ct.index)))
    ax.set_yticklabels(ct.index)

    for i in range(len(ct.index)):
        for j in range(len(ct.columns)):
            val = ct.values[i, j]
            color = "white" if val > 350 else "black"
            ax.text(j, i, str(val), ha="center", va="center", color=color)

    ax.set_xlabel("Cuisine")
    ax.set_ylabel("Jenis Makanan")
    ax.set_title("Heatmap: Jenis Makanan vs Cuisine")
    plt.colorbar(im)
    plt.tight_layout()

    out_path = os.path.join(output_dir, "4_3_1_heatmap_cuisine.png")
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"[OK] Tersimpan: {out_path}")

    return ct

def tabel_statistik_nutrisi_utama(df, output_dir):
    """Tabel 4.13 (a): Statistik deskriptif nutrisi utama pada dataset final."""
    nutrisi_cols = {
        "energy_kcal": "Energi (kkal)",
        "protein_g": "Protein (g)",
        "carbohydrate_g": "Karbohidrat (g)",
        "fat_g": "Lemak Total (g)",
        "fiber_g": "Serat (g)",
        "sodium_mg": "Sodium (mg)",
        "sugar_g": "Gula (g)",
    }

    stat = df[list(nutrisi_cols.keys())].describe().T[["mean", "std", "min", "50%", "max"]]
    stat.columns = ["Mean", "Std", "Min", "Median", "Maks"]
    stat.index = [nutrisi_cols[c] for c in stat.index]
    stat = stat.round(2)

    out_path = os.path.join(output_dir, "tabel_4_13a_statistik_nutrisi_utama.csv")
    stat.to_csv(out_path)
    print(f"[OK] Tersimpan: {out_path}")
    print(stat)

    # Grafik pendukung: boxplot distribusi nutrisi utama
    fig, ax = plt.subplots(figsize=(10, 6))
    df[list(nutrisi_cols.keys())].rename(columns=nutrisi_cols).boxplot(ax=ax, rot=30)
    ax.set_title("Distribusi Nilai Nutrisi Utama pada Dataset Final")
    ax.set_ylabel("Nilai")

    plt.tight_layout()
    fig_path = os.path.join(output_dir, "4_3_2_boxplot_nutrisi_utama.png")
    plt.savefig(fig_path, dpi=150)
    plt.close()
    print(f"[OK] Tersimpan: {fig_path}")

    return stat


def tabel_statistik_energi_sodium_slot(df, output_dir):
    """Tabel 4.13 (b): Statistik energi dan sodium per kategori slot waktu makan."""
    order = ["Snack", "Main Course", "Side Dish", "Drink"]

    stat = df.groupby("consumption_label")[["energy_kcal", "sodium_mg"]].agg(["mean", "median"]).round(2)
    stat.columns = ["Energi Mean (kkal)", "Energi Median (kkal)", "Sodium Mean (mg)", "Sodium Median (mg)"]
    stat = stat.reindex(order)

    out_path = os.path.join(output_dir, "tabel_4_13b_statistik_slot.csv")
    stat.to_csv(out_path)
    print(f"[OK] Tersimpan: {out_path}")
    print(stat)

    # Grafik pendukung: bar chart energi & sodium per slot (berdampingan)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    axes[0].bar(stat.index, stat["Energi Mean (kkal)"], color="#3B6F8F")
    axes[0].set_title("Rata-rata Energi per Kategori Slot")
    axes[0].set_ylabel("Energi (kkal)")
    axes[0].set_xlabel("Kategori Slot")

    axes[1].bar(stat.index, stat["Sodium Mean (mg)"], color="#E07B39")
    axes[1].set_title("Rata-rata Sodium per Kategori Slot")
    axes[1].set_ylabel("Sodium (mg)")
    axes[1].set_xlabel("Kategori Slot")

    plt.tight_layout()
    fig_path = os.path.join(output_dir, "4_3_2_bar_energi_sodium_slot.png")
    plt.savefig(fig_path, dpi=150)
    plt.close()
    print(f"[OK] Tersimpan: {fig_path}")

    return stat

def main():
    print("=" * 60)
    print("STEP 05: EDA Visualization")
    print("=" * 60)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"\n[1/5] Membaca dataset final: {INPUT_FILE}")
    df = pd.read_csv(INPUT_FILE)
    total = len(df)
    print(f"Total item: {total}")

    print("\n[EXTRA] Membuat Tabel 4.13: statistik nutrisi utama...")
    tabel_statistik_nutrisi_utama(df, OUTPUT_DIR)

    print("\n[EXTRA] Membuat Tabel 4.13: statistik energi & sodium per slot...")
    tabel_statistik_energi_sodium_slot(df, OUTPUT_DIR)

    print("\n[2/5] Membuat grafik distribusi kategori slot...")
    chart_distribusi_slot(df, OUTPUT_DIR)

    print("\n[3/5] Membuat grafik distribusi food_group...")
    chart_distribusi_food_group(df, OUTPUT_DIR)

    print(f"\n[4/5] Membuat grafik fill rate nutrisi (HC & SC)...")
    print(f"  Membaca dataset sebelum fillna: {INPUT_FILE_BEFORE_FILLNA}")
    df_before_fillna = pd.read_csv(INPUT_FILE_BEFORE_FILLNA)
    hc_fill, sc_fill = chart_fill_rate(df_before_fillna, OUTPUT_DIR)
    print(f"  Rata-rata fill rate HC: {hc_fill.mean():.1f}%")
    print(f"  Rata-rata fill rate SC: {sc_fill.mean():.1f}%")

    print("\n[5/5] Membuat grafik kelayakan batasan medis dan heatmap cuisine...")
    chart_kelayakan_medis(df, OUTPUT_DIR)
    ct = chart_heatmap_cuisine(df, OUTPUT_DIR)
    print(ct)

    print("\n" + "=" * 60)
    print(f"[OK] Selesai. Seluruh grafik tersimpan di: {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
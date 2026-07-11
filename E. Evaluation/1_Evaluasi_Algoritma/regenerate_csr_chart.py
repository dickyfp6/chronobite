import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

# ─── Load Data ────────────────────────────────────────────────────────────────
script_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(script_dir, "output", "greedy_26", "summary.csv")
df = pd.read_csv(csv_path)
df = df.dropna(subset=["Profile", "CS Rate"])

# ─── Color Coding per Kelompok ────────────────────────────────────────────────
def get_group(profile):
    if profile == "Normal":
        return "normal"
    count = profile.count("+")
    if count == 0:
        return "single"
    elif count == 1:
        return "dual"
    else:
        return "triple"

df["group"] = df["Profile"].apply(get_group)

color_map = {
    "normal":  "#1a6b5c",
    "single":  "#2a9d8f",
    "dual":    "#e9c46a",
    "triple":  "#e76f51",
}

df["color"] = df["group"].map(color_map)

# ─── Sort: Normal → Single → Dual → Triple, each by CSR descending ───────────
group_order = {"normal": 0, "single": 1, "dual": 2, "triple": 3}
df["group_order"] = df["group"].map(group_order)
df = df.sort_values(["group_order", "CS Rate"], ascending=[True, False]).reset_index(drop=True)

# ─── Plot ─────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(12, 11))

bars = ax.barh(
    df["Profile"],
    df["CS Rate"],
    color=df["color"],
    edgecolor="white",
    linewidth=0.6,
    height=0.72,
)

# Value labels di ujung bar
for bar, val in zip(bars, df["CS Rate"]):
    ax.text(
        val + 0.5,
        bar.get_y() + bar.get_height() / 2,
        f"{val:.1f}%",
        va="center",
        ha="left",
        fontsize=8.5,
        color="#333333",
        fontweight="bold",
    )

# Garis rata-rata keseluruhan
mean_csr = df["CS Rate"].mean()
ax.axvline(mean_csr, color="#555555", linestyle="--", linewidth=1.2, alpha=0.7)
ax.text(
    mean_csr + 0.5,
    len(df) - 0.5,
    f"Rata-rata: {mean_csr:.1f}%",
    color="#555555",
    fontsize=8.5,
    va="top",
    fontstyle="italic",
)

# Garis pemisah antar kelompok
group_sizes = df.groupby("group_order").size()
cumulative = 0
separators = []
for g in sorted(group_sizes.index)[:-1]:
    cumulative += group_sizes[g]
    separators.append(cumulative - 0.5)

for sep in separators:
    ax.axhline(sep, color="#aaaaaa", linewidth=0.9, linestyle="-")

# Styling
ax.set_xlabel("Constraint Satisfaction Rate (%)", fontsize=11, labelpad=10)
ax.set_title("Constraint Satisfaction Rate per Skenario Profil\n(Algoritma Greedy)", 
             fontsize=13, fontweight="bold", pad=15)
ax.set_xlim(0, 108)
ax.set_ylim(-0.7, len(df) - 0.3)
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0f}%"))
ax.tick_params(axis="y", labelsize=9)
ax.tick_params(axis="x", labelsize=9)
ax.grid(axis="x", linestyle="--", alpha=0.3, color="gray")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.invert_yaxis()

# Legend
legend_patches = [
    mpatches.Patch(color=color_map["normal"],  label="Normal"),
    mpatches.Patch(color=color_map["single"],  label="Penyakit Tunggal"),
    mpatches.Patch(color=color_map["dual"],    label="Dua Penyakit (Komplikasi)"),
    mpatches.Patch(color=color_map["triple"],  label="Tiga Penyakit (Komplikasi)"),
]
ax.legend(
    handles=legend_patches,
    loc="lower right",
    fontsize=9,
    framealpha=0.85,
    edgecolor="#cccccc",
)

plt.tight_layout()

# ─── Save ─────────────────────────────────────────────────────────────────────
out_path = os.path.join(script_dir, "output", "greedy_26", "overall_cs_greedy_v2.png")
plt.savefig(out_path, dpi=180, bbox_inches="tight", facecolor="white")
print(f"[OK] Saved to: {out_path}")
plt.close()

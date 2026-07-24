import json
import numpy as np
import matplotlib.pyplot as plt

# Load existing raw results (no re-run needed)
with open(r'C:\Users\Silfia\Documents\FILE TA\TugasAkhirDSS\E. Evaluation\1_Evaluasi_Algoritma\output\ga_26\raw_results.json') as f:    data = json.load(f)
results = data['results']

profiles = []
means = []
stds = []
is_ckd = []

for r in results:
    cs_rates = r['cs_rate_per_run']
    profiles.append(r['profile'])
    means.append(np.mean(cs_rates))
    stds.append(np.std(cs_rates))
    is_ckd.append('ckd' in r['disease'])

# Sort descending by mean CSR
order = np.argsort(means)[::-1]
profiles = [profiles[i] for i in order]
means = [means[i] for i in order]
stds = [stds[i] for i in order]
is_ckd = [is_ckd[i] for i in order]

colors = ['#d9534f' if ckd else '#5b9bd5' for ckd in is_ckd]

fig, ax = plt.subplots(figsize=(16, 8))

bars = ax.bar(
    profiles, means, yerr=stds, capsize=4,
    color=colors, edgecolor='black', linewidth=0.5,
    error_kw={'elinewidth': 1.2, 'ecolor': 'black'}
)

for bar, mean_val in zip(bars, means):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 2,
        f'{mean_val:.1f}',
        ha='center', va='bottom', fontsize=8, fontweight='bold'
    )

ax.set_title('Rata-rata Constraint Satisfaction Rate (CSR) per Profil (Genetic Algorithm)\n± 1 Standar Deviasi dari 10 Run', fontsize=14)
ax.set_xlabel('Profil Penyakit')
ax.set_ylabel('CSR (%)')
ax.set_ylim(0, 115)
ax.axhline(100, color='gray', linestyle='--', linewidth=0.7)
plt.xticks(rotation=45, ha='right', fontsize=9)

# Legend
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='#5b9bd5', edgecolor='black', label='Profil non-CKD'),
    Patch(facecolor='#d9534f', edgecolor='black', label='Profil dengan CKD'),
]
ax.legend(handles=legend_elements, loc='upper right')

plt.tight_layout()
plt.savefig(r'C:\Users\Silfia\Documents\FILE TA\TugasAkhirDSS\E. Evaluation\1_Evaluasi_Algoritma\output\ga_26\csr_mean_std_by_profile.png', dpi=200)
print("Saved.")

# Print summary table for quick sanity check
print(f"{'Profile':<45}{'Mean':>8}{'Std':>8}")
for p, m, s in zip(profiles, means, stds):
    print(f"{p:<45}{m:>8.1f}{s:>8.1f}")
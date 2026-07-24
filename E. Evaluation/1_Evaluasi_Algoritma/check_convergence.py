import json
import numpy as np

with open (r'E. Evaluation\1_Evaluasi_Algoritma\output\ga_26\raw_results.json') as f:
    data = json.load(f)

results = data['results']

rows = []
for r in results:
    cs = r['cs_rate_per_run']
    n = len(cs)
    half = n // 2
    first_half = cs[:half]      # run 1-5
    second_half = cs[half:]     # run 6-10

    mean_full = np.mean(cs)
    mean_first = np.mean(first_half)
    mean_second = np.mean(second_half)
    diff = abs(mean_first - mean_second)

    rows.append({
        'profile': r['profile'],
        'is_ckd': 'ckd' in r['disease'],
        'mean_full_n10': mean_full,
        'mean_run1_5': mean_first,
        'mean_run6_10': mean_second,
        'abs_diff': diff
    })

# Sort by absolute difference descending (largest instability first)
rows_sorted = sorted(rows, key=lambda x: x['abs_diff'], reverse=True)

print(f"{'Profile':<45}{'Run1-5':>10}{'Run6-10':>10}{'|Diff|':>10}{'CKD':>6}")
print('-' * 85)
for row in rows_sorted:
    print(f"{row['profile']:<45}{row['mean_run1_5']:>10.1f}{row['mean_run6_10']:>10.1f}{row['abs_diff']:>10.1f}{'Yes' if row['is_ckd'] else 'No':>6}")

diffs = [row['abs_diff'] for row in rows]
print('\n--- Summary ---')
print(f"Mean |diff| across 26 profiles : {np.mean(diffs):.2f} percentage points")
print(f"Max  |diff|                      : {np.max(diffs):.2f} percentage points ({rows_sorted[0]['profile']})")
print(f"Profiles with |diff| <= 5pp      : {sum(1 for d in diffs if d <= 5)} / {len(diffs)}")
print(f"Profiles with |diff| <= 10pp     : {sum(1 for d in diffs if d <= 10)} / {len(diffs)}")
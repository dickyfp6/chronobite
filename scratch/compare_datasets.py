import pandas as pd
import subprocess
import io

# Get current dataset
df_curr = pd.read_csv("A. Data/Data Processed/07_super_final.csv")

# Get previous dataset via git show
cmd = ["git", "show", "dfbfe34728375b38f9441546131825fe52d3ef62:A. Data/Data Processed/07_super_final.csv"]
res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
if res.returncode != 0:
    print(f"Error checking out old dataset: {res.stderr}")
    exit(1)

df_prev = pd.read_csv(io.StringIO(res.stdout))

print(f"Previous size: {len(df_prev)}")
print(f"Current size: {len(df_curr)}")

# Compare fdc_id 174922 and 171514
for fid in [174922, 171514]:
    print(f"\n=== FDC ID {fid} ===")
    prev_match = df_prev[df_prev["fdc_id"] == fid]
    curr_match = df_curr[df_curr["fdc_id"] == fid]
    
    if not prev_match.empty:
        p_row = prev_match.iloc[0]
        print(f"  PREV: Name={p_row['food_name']}, Energy={p_row['energy_kcal']}, Cuisine={p_row['cuisine']}, CuisineLabel={p_row['cuisine_label']}")
    else:
        print("  PREV: Not found")
        
    if not curr_match.empty:
        c_row = curr_match.iloc[0]
        print(f"  CURR: Name={c_row['food_name']}, Energy={c_row['energy_kcal']}, Cuisine={c_row['cuisine']}, CuisineLabel={c_row['cuisine_label']}")
    else:
        print("  CURR: Not found")

# Compare general stats
print("\n=== Previous Cuisine distribution ===")
print(df_prev["cuisine"].value_counts(dropna=False))
print("\n=== Current Cuisine distribution ===")
print(df_curr["cuisine"].value_counts(dropna=False))

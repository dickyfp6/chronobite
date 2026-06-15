import pandas as pd
import subprocess
import io
import json

def get_git_file(commit, path):
    cmd = ["git", "show", f"{commit}:{path}"]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if res.returncode != 0:
        return None
    return res.stdout

# 1. Compare 07_super_final.csv
print("=== 07_super_final.csv comparison ===")
curr_csv = pd.read_csv("A. Data/Data Processed/07_super_final.csv")
old_csv_content = get_git_file("544dd1d587cdc8d736b49ded44bbcc8ae34f8a90", "A. Data/Data Processed/07_super_final.csv")

if old_csv_content:
    old_csv = pd.read_csv(io.StringIO(old_csv_content))
    print("\nOLD CSV columns:", old_csv.columns.tolist())
    print("\nOLD CSV cuisine_label counts:")
    if "cuisine_label" in old_csv.columns:
        print(old_csv["cuisine_label"].value_counts(dropna=False))
    if "cuisine" in old_csv.columns:
        print(old_csv["cuisine"].value_counts(dropna=False))
        
    for fid in [174922, 171514]:
        print(f"\nFDC ID {fid}:")
        old_match = old_csv[old_csv["fdc_id"] == fid]
        curr_match = curr_csv[curr_csv["fdc_id"] == fid]
        
        if not old_match.empty:
            row = old_match.iloc[0]
            print(f"  OLD: Name={row['food_name']}, Energy={row['energy_kcal']}, CuisineLabel={row.get('cuisine_label', 'N/A')}, Cuisine={row.get('cuisine', 'N/A')}")
        else:
            print("  OLD: Not found")
            
        if not curr_match.empty:
            row = curr_match.iloc[0]
            print(f"  CURR: Name={row['food_name']}, Energy={row['energy_kcal']}, CuisineLabel={row.get('cuisine_label', 'N/A')}, Cuisine={row.get('cuisine', 'N/A')}")
        else:
            print("  CURR: Not found")
else:
    print("Could not read old CSV")

# 2. Compare food_name_cache.json
print("\n=== food_name_cache.json comparison ===")
old_fn_content = get_git_file("544dd1d587cdc8d736b49ded44bbcc8ae34f8a90", "G. NameFood/output/food_name_cache.json")
if old_fn_content:
    old_fn = json.loads(old_fn_content)
    curr_fn_path = "G. NameFood/output/food_name_cache.json"
    with open(curr_fn_path, "r", encoding="utf-8") as f:
        curr_fn = json.load(f)
        
    print(f"OLD size: {len(old_fn)}, CURR size: {len(curr_fn)}")
    
    # Check for original names of interest:
    # 174922 orig name: "Bread, reduced-calorie, white"
    # 171514 orig name: "Chicken, breast, tenders, breaded, cooked, start to finish"
    # Let's search keys
    for k in ["Bread, reduced-calorie, white", "Chicken, breast, tenders, breaded, cooked, start to finish", "Chicken, breast, tenders, breaded, cooked, prepared-from-recipe"]:
        print(f"\nSearch key: {k}")
        print(f"  OLD: {old_fn.get(k)}")
        print(f"  CURR: {curr_fn.get(k)}")
else:
    print("Could not read old food name cache")

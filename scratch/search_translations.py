import json
import os
import pandas as pd

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

food_name_path = os.path.normpath(os.path.join(base_dir, "G. NameFood", "output", "food_name_cache.json"))
fallback_csv_path = os.path.normpath(os.path.join(base_dir, "G. NameFood", "output", "food_name_ai.csv"))

print("=== Searching food_name_cache.json ===")
if os.path.exists(food_name_path):
    with open(food_name_path, "r", encoding="utf-8") as f:
        cache = json.load(f)
    for k, v in cache.items():
        if "reduced-calorie" in k.lower() or "reduced-calorie" in str(v).lower() or "tenders" in k.lower() or "tenders" in str(v).lower():
            print(f"  Key: {k} -> Val: {v}")

print("\n=== Searching food_name_ai.csv ===")
if os.path.exists(fallback_csv_path):
    df = pd.read_csv(fallback_csv_path)
    # Search by fdc_id 174922 and 171514
    for fid in [174922, 171514]:
        match = df[df["fdc_id"] == fid]
        if not match.empty:
            print(f"  FDC ID {fid}: {match.iloc[0].to_dict()}")
        else:
            print(f"  FDC ID {fid}: Not found")
            
    # Search for names containing tenders or reduced-calorie
    matches = df[df["food_name_original"].str.contains("reduced-calorie|tenders|chicken, breast, tenders|bread, reduced-calorie", case=False, na=False) | 
                 df["food_name"].str.contains("reduced-calorie|tenders|chicken, breast, tenders|bread, reduced-calorie", case=False, na=False)]
    print(f"\n  Found {len(matches)} rows matching terms in csv:")
    print(matches[["fdc_id", "food_name_original", "food_name"]].head(10))

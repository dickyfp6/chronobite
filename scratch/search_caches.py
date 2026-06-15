import json
import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

food_name_path = os.path.normpath(os.path.join(base_dir, "G. NameFood", "output", "food_name_cache.json"))
cuisine_path = os.path.normpath(os.path.join(base_dir, "G. NameFood", "output", "cuisine_cache.json"))
category_path = os.path.normpath(os.path.join(base_dir, "G. NameFood", "output", "category_cache.json"))

def search_cache(path, query):
    if not os.path.exists(path):
        print(f"Path not found: {path}")
        return
    with open(path, "r", encoding="utf-8") as f:
        cache = json.load(f)
    print(f"\n=== Searching {os.path.basename(path)} for '{query}' ===")
    matches = 0
    for k, v in cache.items():
        if query.lower() in k.lower() or query.lower() in str(v).lower():
            print(f"  {k} : {v}")
            matches += 1
            if matches >= 15:
                print("  ... truncated ...")
                break
    print(f"Total matches: {matches}")

search_cache(food_name_path, "Reduced-Calorie White Bread")
search_cache(food_name_path, "Breaded Chicken Tenders")

search_cache(cuisine_path, "Reduced-Calorie White Bread")
search_cache(cuisine_path, "Breaded Chicken Tenders")
search_cache(cuisine_path, "White Bread")
search_cache(cuisine_path, "Chicken Tenders")

search_cache(category_path, "Reduced-Calorie White Bread")
search_cache(category_path, "Breaded Chicken Tenders")
search_cache(category_path, "White Bread")
search_cache(category_path, "Chicken Tenders")

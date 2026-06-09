import json
import os

CACHE_FILE = "cuisine_cache.json"

if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        cache = json.load(f)
    
    initial_len = len(cache)
    # Filter out all "Generic" entries so they can be re-evaluated correctly
    cleaned_cache = {k: v for k, v in cache.items() if v != "Generic"}
    
    print(f"Initial cache size: {initial_len}")
    print(f"Cleaned cache size (without Generic): {len(cleaned_cache)}")
    print(f"Removed {initial_len - len(cleaned_cache)} 'Generic' entries.")
    
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cleaned_cache, f, ensure_ascii=False, indent=2)
    print("Cache cleaned successfully!")
else:
    print("Cache file not found.")

import os
import sys
import json
import re
import pandas as pd
# pyrefly: ignore [missing-source-for-stubs]
import requests
import time
import math
import traceback

# =====================================================================
# CONFIGURATION
# =====================================================================
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

INPUT_FILE = os.path.join(CURRENT_DIR, "output", "cuisine_ai.csv")
OUTPUT_FILE = os.path.join(CURRENT_DIR, "output", "category_ai.csv")
CACHE_FILE = os.path.join(CURRENT_DIR, "output", "category_cache.json")
ENV_FILE = os.path.join(CURRENT_DIR, ".env")

# AI Provider options: "github" atau "gemini"
# Secara default menggunakan "github" (Copilot/GitHub Models API), 
# jika key tidak ada atau limit habis, bisa diganti ke "gemini".
AI_PROVIDER = "github"

# Model Names
GEMINI_MODEL = "gemini-2.5-flash"
GITHUB_MODEL = "gpt-4o-mini"

ALLOWED_CATEGORIES = ["Main Course", "Side Dish", "Drink", "Snack"]
BATCH_SIZE = 50

# Safe cache key untuk NaN/empty
UNKNOWN_KEY = "__unknown__"


def load_env():
    """Load API keys from .env if it exists"""
    if os.path.exists(ENV_FILE):
        try:
            with open(ENV_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        parts = line.split("=", 1)
                        if len(parts) == 2:
                            key, val = parts[0].strip(), parts[1].strip()
                            val = val.strip('"').strip("'")
                            os.environ[key] = val
        except Exception as e:
            print(f"[WARN] Error loading .env file: {e}")


def get_api_key(provider):
    if provider == "gemini":
        return os.environ.get("GEMINI_API_KEY")
    else:
        return os.environ.get("GITHUB_TOKEN")


def safe_cache_key(name):
    if pd.isna(name) or str(name).strip() == "":
        return UNKNOWN_KEY
    return str(name).strip()


def normalize_category(ans):
    """Ensure classification output fits EXACTLY into ALLOWED_CATEGORIES"""
    ans_stripped = str(ans).strip().lower()

    # Exact match (case-insensitive)
    for cat in ALLOWED_CATEGORIES:
        if ans_stripped == cat.lower():
            return cat
            
    # Substring match / normalization for common variations
    if "main" in ans_stripped:
        return "Main Course"
    if "side" in ans_stripped:
        return "Side Dish"
    if "drink" in ans_stripped or "beverage" in ans_stripped:
        return "Drink"
    if "snack" in ans_stripped or "dessert" in ans_stripped:
        return "Snack"

    return "Snack"  # Default fallback (safest nutritionally)


def call_ai_batch(items_list, provider, api_key):
    """Call AI (Gemini or GitHub Models API) to classify a batch of food items at once"""
    categories_str = ", ".join(ALLOWED_CATEGORIES)
    
    # Format list makanan dengan food_group untuk memberikan konteks tambahan
    foods_text = "\n".join([f"- Name: \"{item['name']}\" | Group: \"{item['group']}\"" for item in items_list])

    prompt = (
        f"You are an expert culinary and nutrition classifier. Your task is to categorize each of the given food items "
        f"into exactly ONE of the following consumption categories: [{categories_str}].\n\n"
        f"Strict Guidelines:\n"
        f"1. Main Course:\n"
        f"   - Primary, filling meals or components of a meal that serve as the main source of energy/protein.\n"
        f"   - Includes: Main protein dishes (fried chicken, beef steak, fish fillet, tofu/tempeh main dishes).\n"
        f"   - Includes: Rice, pasta, noodle dishes, oatmeal, porridge, and all breakfast cereals (e.g., rolled oats, cornflakes, muesli).\n"
        f"   - Includes: Main course soups (chicken soup, beef stew, ramen).\n"
        f"   - Includes: Prepared egg dishes serving as main protein components (scrambled eggs, fried eggs, omelettes, hard-boiled eggs, poached eggs).\n"
        f"2. Side Dish:\n"
        f"   - Accompaniments, condiments, raw ingredients, cooking fats, or toppings.\n"
        f"   - Includes: Plain vegetables (e.g., broccoli, carrots) and vegetable salads (without main protein).\n"
        f"   - Includes: Sauces, dressings, oils, butter, margarine, spices, herbs.\n"
        f"   - Includes: Baking/cooking ingredients that are NOT eaten directly as main meals or drinks, such as Evaporated Milk (e.g., Evaporated Nonfat Milk), Condensed Milk (used as sweetener), Whipped Topping, or cream.\n"
        f"   - Includes: Cheese, dips, and spreads.\n"
        f"3. Drink:\n"
        f"   - Liquids intended primarily for hydration or beverage consumption.\n"
        f"   - Includes: Water, fruit juices, vegetable juices, teas, coffees, carbonated sodas.\n"
        f"   - Includes: Fluid milk (e.g., whole milk, low-fat milk, skim milk), soymilk, almond milk, and other fluid dairy/plant-based milks.\n"
        f"4. Snack:\n"
        f"   - Light foods eaten between meals, desserts, sweets, and confectioneries.\n"
        f"   - Includes: Cookies, crackers, potato chips, pretzels, cakes, pastries, donuts, pudding.\n"
        f"   - Includes: Fruits (whole, sliced, raw fruits are classified as Snack, e.g., Apples, Bananas, unless processed into a drink).\n"
        f"   - Includes: Nuts and seeds (e.g., almonds, peanuts) eaten directly as snack.\n\n"
        f"Output format:\n"
        f"Return ONLY a valid JSON object where the keys are the exact food names from the input list, "
        f"and the values are their corresponding category (exactly one of 'Main Course', 'Side Dish', 'Drink', 'Snack').\n"
        f"Do not return markdown (e.g. no ```json blocks), do not return any explanations. "
        f"Return ONLY the plain JSON object.\n\n"
        f"Foods to classify:\n{foods_text}"
    )

    if provider == "gemini":
        if api_key.startswith("AQ.") or api_key.startswith("ya29."):
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
        else:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={api_key}"
            headers = {
                "Content-Type": "application/json"
            }
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.0,
                "response_mime_type": "application/json"
            }
        }
    else:  # github
        url = "https://models.inference.ai.azure.com/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "messages": [
                {"role": "system", "content": prompt}
            ],
            "model": GITHUB_MODEL,
            "temperature": 0.0,
            "max_tokens": 4096,
            "response_format": {"type": "json_object"}
        }

    for attempt in range(5):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=40)

            if response.status_code == 429:
                sleep_sec = 60
                if provider == "github":
                    try:
                        sleep_sec = int(response.headers.get("Retry-After", 10))
                    except Exception:
                        pass
                else:  # gemini
                    try:
                        res_json = response.json()
                        for detail in res_json.get("error", {}).get("details", []):
                            if "retryDelay" in detail:
                                delay_str = detail["retryDelay"]
                                if delay_str.endswith("s"):
                                    sleep_sec = float(delay_str[:-1]) + 2.0
                                break
                    except Exception:
                        pass
                print(f"  -> [RATE LIMIT] Terlalu cepat ({provider} Rate Limit). Response: {response.text}")
                print(f"  -> [RETRY] Menunggu {sleep_sec} detik sebelum mencoba lagi...")
                time.sleep(sleep_sec)
                continue

            if response.status_code in [500, 502, 503, 504]:
                print(f"  -> [SERVER ERROR] AI API sedang padat/down ({response.status_code}). Response: {response.text}")
                print("  -> Menunggu 10 detik sebelum mencoba lagi...")
                time.sleep(10)
                continue

            if response.status_code == 200:
                res_data = response.json()
                try:
                    if provider == "gemini":
                        raw_ans = res_data["candidates"][0]["content"]["parts"][0]["text"].strip()
                    else:
                        raw_ans = res_data["choices"][0]["message"]["content"].strip()

                    if raw_ans.startswith("```"):
                        raw_ans = re.sub(r"^```(?:json)?\n", "", raw_ans)
                        raw_ans = re.sub(r"\n```$", "", raw_ans)
                        raw_ans = raw_ans.strip()

                    result_data = json.loads(raw_ans)

                    if isinstance(result_data, dict):
                        # Key-based lookup (case-insensitive & stripped match for reliability)
                        normalized_results = {str(k).strip().lower(): v for k, v in result_data.items()}
                        cleaned = []
                        for item in items_list:
                            key = str(item['name']).strip().lower()
                            val = normalized_results.get(key, "Snack")
                            cleaned.append(normalize_category(val))
                        return cleaned
                    else:
                        print(f"  -> [WARN] Unexpected JSON format from AI (not dict): {type(result_data)}")
                except Exception as e:
                    print(f"  -> [WARN] Failed to parse JSON from AI response: {e}")
                    print(f"  -> [DEBUG] Raw Output: {res_data}")
            else:
                print(f"  -> [ERROR] API Error {response.status_code}: {response.text}")

        except Exception as e:
            print(f"  -> [ERROR] API call failed with exception: {e}")
            traceback.print_exc()

        time.sleep(5)

    print("  -> [FAIL] Giving up on this batch after 5 attempts.")
    return None


def main():
    print("="*60)
    print(f"KATEGORISASI MAKANAN DENGAN AI ({AI_PROVIDER.upper()})")
    print("="*60)

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)

    if not os.path.exists(INPUT_FILE):
        print(f"[ERROR] Input file tidak ditemukan: {INPUT_FILE}")
        sys.exit(1)

    print(f"Membaca dataset dari: {INPUT_FILE}")
    df = pd.read_csv(INPUT_FILE)
    print(f"Berhasil memuat {len(df)} baris data.")

    cache = {}
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                cache = json.load(f)
            print(f"[OK] Memuat {len(cache)} kategori terklasifikasi dari cache.")
        except Exception:
            pass

    # Ambil baris makanan unik berdasarkan nama
    unique_items_df = df.drop_duplicates(subset=["food_name"])[["food_name", "food_group"]]
    
    missing_items = []
    for _, row in unique_items_df.iterrows():
        name = row["food_name"]
        group = row["food_group"]
        if safe_cache_key(name) not in cache:
            missing_items.append({
                "name": name,
                "group": group
            })
            
    print(f"Total makanan unik di dataset: {len(unique_items_df)}")
    print(f"Makanan belum terklasifikasi di cache: {len(missing_items)}")

    if missing_items:
        load_env()
        api_key = get_api_key(AI_PROVIDER)
        if api_key:
            total_batches = math.ceil(len(missing_items) / BATCH_SIZE)
            print(f"Menggunakan {AI_PROVIDER.upper()} untuk mengklasifikasi {len(missing_items)} makanan dalam {total_batches} batch (size={BATCH_SIZE})...")

            for i in range(0, len(missing_items), BATCH_SIZE):
                batch_items = missing_items[i:i+BATCH_SIZE]
                batch_num = (i // BATCH_SIZE) + 1

                print(f"[{batch_num}/{total_batches}] Memproses batch dengan {len(batch_items)} makanan...")
                
                # Panggilan batch
                results = call_ai_batch(batch_items, AI_PROVIDER, api_key)
                if results is None:
                    print("  -> [FATAL] Gagal mendapatkan respon dari AI setelah beberapa percobaan.")
                    print("  -> Menyimpan cache sementara dan keluar.")
                    break

                for item, res in zip(batch_items, results):
                    key = safe_cache_key(item['name'])
                    cache[key] = res

                # Simpan cache secara inkremental
                try:
                    with open(CACHE_FILE, "w", encoding="utf-8") as f:
                        json.dump(cache, f, ensure_ascii=False, indent=2)
                except Exception:
                    pass

                time.sleep(2)
        else:
            print(f"[WARN] API Key untuk {AI_PROVIDER.upper()} tidak ditemukan di .env! Menggunakan default 'Snack'.")
            for item in missing_items:
                cache[safe_cache_key(item['name'])] = "Snack"

    print("\nMenerapkan kategori ke dataset...")
    df["consumption_label"] = df["food_name"].map(lambda x: cache.get(safe_cache_key(x), "Snack"))

    print("\nDistribusi Kategori Konsumsi (consumption_label):")
    print(df["consumption_label"].value_counts())

    print(f"\nMenyimpan dataset akhir ke: {OUTPUT_FILE}")
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"[OK] Selesai! Total baris tersimpan: {len(df)}")
    print("="*60)


if __name__ == "__main__":
    main()

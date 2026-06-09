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
import shutil

# =====================================================================
# CONFIGURATION
# =====================================================================
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

INPUT_FILE = os.path.join(CURRENT_DIR, "output", "03_dataset_halal_ai.csv")
OUTPUT_FILE = os.path.join(CURRENT_DIR, "output", "03_dataset_halal_cuisine.csv")
CACHE_FILE = os.path.join(CURRENT_DIR, "output", "cuisine_cache.json")
ENV_FILE = os.path.join(CURRENT_DIR, ".env")

# Migration of old cache
OLD_CACHE_FILE = os.path.join(CURRENT_DIR, "Cuisine", "cuisine_cache.json")

# AI Provider options: "gemini" atau "github"
# PENTING: GitHub Models memiliki limit harian yang rendah (150 request per hari).
# Jika terkena limit GitHub, Anda bisa beralih ke "gemini" yang limitnya jauh lebih besar.
AI_PROVIDER = "github"

# Model Names
GEMINI_MODEL = "gemini-2.5-flash"  # atau "gemini-1.5-flash"
GITHUB_MODEL = "gpt-4o-mini"

# FIX #1: Typo "Mediteranian" → "Mediterranean" (konsisten di seluruh kode)
ALLOWED_CUISINES = ["Asian", "Western", "Mediterranean", "Generic"]
BATCH_SIZE = 50

# FIX #2: Safe cache key untuk NaN/empty
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


def migrate_cache():
    """Migrate cache from old folder if new cache does not exist"""
    if not os.path.exists(CACHE_FILE) and os.path.exists(OLD_CACHE_FILE):
        try:
            os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
            shutil.copy2(OLD_CACHE_FILE, CACHE_FILE)
            print(f"[MIGRATION] Berhasil memindahkan cache lama dari {OLD_CACHE_FILE} ke {CACHE_FILE}")
        except Exception as e:
            print(f"[WARN] Gagal memindahkan cache lama: {e}")


def clean_cache():
    """Remove 'Generic' entries from cache so they can be re-classified"""
    migrate_cache()
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                cache = json.load(f)
            initial_len = len(cache)
            cleaned_cache = {k: v for k, v in cache.items() if v != "Generic"}

            print(f"Initial cache size: {initial_len}")
            print(f"Cleaned cache size (without Generic): {len(cleaned_cache)}")
            print(f"Removed {initial_len - len(cleaned_cache)} 'Generic' entries.")

            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(cleaned_cache, f, ensure_ascii=False, indent=2)
            print("[OK] Cache cleaned successfully!")
        except Exception as e:
            print(f"[ERROR] Gagal membersihkan cache: {e}")
    else:
        print("[WARN] Cache file tidak ditemukan.")


def safe_cache_key(name):
    """
    FIX #2: Konversi nama makanan ke cache key yang aman.
    NaN atau string kosong → UNKNOWN_KEY
    """
    if pd.isna(name) or str(name).strip() == "":
        return UNKNOWN_KEY
    return str(name).strip()


def normalize_cuisine(ans):
    """
    FIX #3: Exact match dulu, baru fallback substring.
    Mencegah 'asian' match ke 'caucasian', dll.
    """
    ans_stripped = str(ans).strip()

    # Exact match (case-insensitive) — prioritas utama
    for cat in ALLOWED_CUISINES:
        if ans_stripped.lower() == cat.lower():
            return cat

    # FIX #1 lanjutan: handle jika AI masih balas "Mediteranian" (typo lama)
    if ans_stripped.lower() in ("mediteranian", "mediterranean"):
        return "Mediterranean"

    # Fallback substring — hanya jika exact match gagal
    ans_lower = ans_stripped.lower()
    for cat in ALLOWED_CUISINES:
        # Pastikan match adalah kata utuh, bukan substring dari kata lain
        # Contoh: "asian" tidak boleh match ke "caucasian"
        pattern = r'\b' + re.escape(cat.lower()) + r'\b'
        if re.search(pattern, ans_lower):
            return cat

    return "Generic"


def call_ai_batch(names_list, provider, api_key):
    """Call AI (Gemini or GitHub Models API) to classify a batch of foods at once"""
    categories_str = ", ".join(ALLOWED_CUISINES)
    foods_text = "\n".join([f"- {name}" for name in names_list])

    prompt = (
        f"You are an expert culinary classifier. Your task is to categorize each of the given food names "
        f"into exactly ONE of the following cuisine categories: [{categories_str}].\n"
        f"Rules:\n"
        f"- Asian: Specific to Asian countries (e.g., Japanese, Chinese, Indonesian, Indian).\n"
        f"- Western: European/American cuisines.\n"
        f"- Mediterranean: Middle-Eastern or Mediterranean cuisines.\n"
        f"- Generic: Raw ingredients, plain fruits, plain vegetables, raw meats, sweets, or no specific cultural origin.\n\n"
        f"Output format: Return ONLY a valid JSON object where the keys are the exact food names from the input list, "
        f"and the values are their corresponding cuisine categories. "
        f"Do not return markdown (e.g. no ```json blocks), do not return any explanations. "
        f"Return ONLY the plain JSON object.\n\n"
        f"Foods to classify:\n{foods_text}"
    )

    if provider == "gemini":
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
            "max_tokens": 1000
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
                        for name in names_list:
                            key = str(name).strip().lower()
                            val = normalized_results.get(key, "Generic")
                            cleaned.append(normalize_cuisine(val))
                        return cleaned
                    elif isinstance(result_data, list):
                        if len(result_data) == len(names_list):
                            cleaned = [normalize_cuisine(ans) for ans in result_data]
                            return cleaned
                        else:
                            print(f"  -> [WARN] Length mismatch for list response. Expected {len(names_list)}, got {len(result_data)}")
                    else:
                        print(f"  -> [WARN] Unexpected JSON format from AI (not dict or list): {type(result_data)}")
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
    # Cek parameter CLI untuk clean cache
    if len(sys.argv) > 1 and sys.argv[1] == "--clean":
        print("="*60)
        print("CLEAN CACHE MODE (Removing 'Generic' Entries)")
        print("="*60)
        clean_cache()
        sys.exit(0)

    print("="*60)
    print(f"STEP 08: Classify Cuisines using {AI_PROVIDER.upper()} AI (BATCH MODE)")
    print("="*60)

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    if not os.path.exists(INPUT_FILE):
        print(f"[ERROR] Input file not found: {INPUT_FILE}")
        sys.exit(1)

    print(f"Reading dataset from: {INPUT_FILE}")
    df = pd.read_csv(INPUT_FILE)
    print(f"Loaded {len(df)} rows.")

    migrate_cache()

    cache = {}
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                cache = json.load(f)
            print(f"[OK] Loaded {len(cache)} classified cuisines from cache.")
        except Exception:
            pass

    unique_names = df["food_name"].unique()
    # FIX #2: Gunakan safe_cache_key untuk lookup cache
    missing_names = [name for name in unique_names if safe_cache_key(name) not in cache]
    print(f"Unique foods in dataset: {len(unique_names)}")
    print(f"Foods missing in cache: {len(missing_names)}")

    if missing_names:
        load_env()
        api_key = get_api_key(AI_PROVIDER)
        if api_key:
            total_batches = math.ceil(len(missing_names) / BATCH_SIZE)
            print(f"Using {AI_PROVIDER.upper()} to classify {len(missing_names)} missing foods in {total_batches} batches of {BATCH_SIZE}...")

            for i in range(0, len(missing_names), BATCH_SIZE):
                batch_names = missing_names[i:i+BATCH_SIZE]
                batch_num = (i // BATCH_SIZE) + 1

                print(f"[{batch_num}/{total_batches}] Classifying {len(batch_names)} foods...")
                safe_batch = [str(n) if pd.notna(n) and str(n).strip() != "" else "Unknown" for n in batch_names]

                results = call_ai_batch(safe_batch, AI_PROVIDER, api_key)
                if results is None:
                    print("  -> [FATAL] Gagal mendapatkan respon dari AI setelah beberapa percobaan.")
                    print("  -> Menghentikan program untuk mencegah data cache rusak.")
                    print("  -> Silakan tunggu 1 menit lalu jalankan kembali program ini.")
                    sys.exit(1)

                for name, res in zip(batch_names, results):
                    # FIX #2: Selalu pakai safe_cache_key saat menyimpan ke cache
                    key = safe_cache_key(name)
                    cache[key] = res

                try:
                    with open(CACHE_FILE, "w", encoding="utf-8") as f:
                        json.dump(cache, f, ensure_ascii=False, indent=2)
                except Exception:
                    pass

                time.sleep(2)
        else:
            print(f"[WARN] API key untuk {AI_PROVIDER.upper()} tidak ditemukan di .env! Menggunakan default 'Generic'.")
            for name in missing_names:
                cache[safe_cache_key(name)] = "Generic"

    print("\nApplying cuisines to dataset...")
    # FIX #2: Lookup cache pakai safe_cache_key
    df["cuisine"] = df["food_name"].map(lambda x: cache.get(safe_cache_key(x), "Generic"))

    print("\nCuisine Distribution:")
    print(df["cuisine"].value_counts())

    print(f"\nSaving final dataset to: {OUTPUT_FILE}")
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"[OK] Process completed successfully! Total rows: {len(df)}")
    print("="*60)


if __name__ == "__main__":
    main()
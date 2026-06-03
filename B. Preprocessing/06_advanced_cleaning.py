import pandas as pd
import os

INPUT_FILE = r'C:\Users\Silfia\Documents\FILE TA\TugasAkhirDSS\A. Data\Data Processed\05_final_dataset-old.csv'
OUTPUT_FILE = r'C:\Users\Silfia\Documents\FILE TA\TugasAkhirDSS\A. Data\Data Processed\05_final_dataset.csv'

def bersihkan_dataset(input_file, output_file):
    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' tidak ditemukan!")
        return

    df = pd.read_csv(input_file)
    print(f"Jumlah baris awal: {len(df)}")

    # Daftar kata kunci yang harus dihapus
    kategori_dihapus = ["raw", "dry", "powder", "flour", "meal", "crude", "unprepared", "undiluted", "liquid from"]
    allowed_categories = ['Main Course', 'Side Dish', 'Snack', 'Drink']

    def is_usable(row):
        name = str(row.get('food_name', '')).lower()
        category = str(row.get('consumption_label', ''))
        group = str(row.get('food_group', ''))
        
        # 1. Hapus jika bukan kategori yang diinginkan
        if category not in allowed_categories:
            return False
            
        # 2. Logika Khusus 'raw'
        # Hapus jika mengandung kata 'raw' TAPI grupnya BUKAN 'Vegetables and Vegetable Products'
        # Juga abaikan jika kategori adalah Drink (minuman raw valid)
        if "raw" in name and group != 'Vegetables and Vegetable Products' and category != 'Drink':
            return False
            
        # 3. Hapus untuk kata kunci lain (selain 'raw')
        kunci_lain = [k for k in kategori_dihapus if k != "raw"]
        if any(k in name for k in kunci_lain):
            return False
            
        return True

    # Terapkan filter
    df_cleaned = df[df.apply(is_usable, axis=1)]

    # FILTER 1: Keyword filter - bumbu dan junk food
    invalid_keywords = ['spice', 'extract', 'flavoring', 'seasoning', 'yeast']
    junk_keywords = ['candy', 'candy bar', 'confection', 'sweet candy',
                     'fudge', 'brownie', 'frosting', 'icing', 'ice cream', 
                     'mousse', 'caramel']
    all_keywords = invalid_keywords + junk_keywords
    
    # Filter keyword normal untuk semua kategori
    keyword_mask = df_cleaned['food_name'].str.lower().str.contains(
        '|'.join(all_keywords), na=False)
    
    # Filter 'powder' hanya untuk non-Drink (minuman bubuk valid seperti susu bubuk)
    powder_mask = (
        df_cleaned['food_name'].str.lower().str.contains('powder', na=False) &
        (df_cleaned['consumption_label'] != 'Drink')
    )
    
    before = len(df_cleaned)
    df_cleaned = df_cleaned[~(keyword_mask | powder_mask)]
    print(f"[FILTER 1] Keyword filter: {before - len(df_cleaned)} items removed")

    # FILTER 2: Energy filter - hanya untuk Main Course dan Drink
    before = len(df_cleaned)
    main_low = (df_cleaned['consumption_label'] == 'Main Course') & (df_cleaned['energy_kcal'] < 50)
    drink_low = (df_cleaned['consumption_label'] == 'Drink') & (df_cleaned['energy_kcal'] < 10)
    df_cleaned = df_cleaned[~(main_low | drink_low)]
    print(f"[FILTER 2] Energy too low (Main Course < 50, Drink < 10 kcal): {before - len(df_cleaned)} items removed")
   
    # FILTER 3: Sodium filter
    before = len(df_cleaned)
    df_cleaned = df_cleaned[df_cleaned['sodium_mg'] <= 2000]
    print(f"[FILTER 3] Sodium > 2000mg: {before - len(df_cleaned)} items removed")

    # FILTER 4: Main Course quality filter (dilonggarkan)
    before = len(df_cleaned)
    main_mask = df_cleaned['consumption_label'] == 'Main Course'
    quality_mask = (
        (df_cleaned['protein_g'] >= 3) &
        (df_cleaned['fat_g'] <= 50) &              # naikkan dari 40 → 50
        ((df_cleaned['carbohydrate_g'] + df_cleaned['protein_g']) >= 10)  # turunkan dari 15 → 10
    )
    # Hapus batas energy_kcal >= 150 dan <= 400 sama sekali
    df_cleaned = df_cleaned[~main_mask | quality_mask]
    print(f"[FILTER 4] Main Course quality: {before - len(df_cleaned)} items removed")

    # FILTER 5: Tandai suitable_for_cvd_cholesterol
    df_cleaned['suitable_for_cvd_cholesterol'] = df_cleaned['trans_fat_g'] <= 0.5
    count_unsuitable = (~df_cleaned['suitable_for_cvd_cholesterol']).sum()
    print(f"[FILTER 5] Marked {count_unsuitable} items unsuitable for CVD/Cholesterol")

    print(f"\n[SUMMARY] Dataset awal: {len(df)} items")
    print(f"[SUMMARY] Dataset final: {len(df_cleaned)} items")
    print(f"[SUMMARY] Total removed: {len(df) - len(df_cleaned)} items")

    df_cleaned.to_csv(output_file, index=False)
    print(f"Jumlah baris setelah dibersihkan: {len(df_cleaned)}")
    print(f"Total baris yang dihapus: {len(df) - len(df_cleaned)}")

if __name__ == "__main__":
    bersihkan_dataset(INPUT_FILE, OUTPUT_FILE)
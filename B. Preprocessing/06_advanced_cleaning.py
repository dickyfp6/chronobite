import pandas as pd
import os
import re

INPUT_FILE = r'C:\Users\Silfia\Documents\FILE TA\TugasAkhirDSS\A. Data\Data Processed\05_final_dataset.csv'
OUTPUT_FILE = r'C:\Users\Silfia\Documents\FILE TA\TugasAkhirDSS\A. Data\Data Processed\06_final_dataset.csv'

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
            
        # 2. Logika Khusus 'raw' - lebih lenient
        if "raw" in name:
            # Pengecualian: sayuran, minuman, buah-buahan, dan kacang mentah tetap valid
            if group in ('Vegetables and Vegetable Products', 
                         'Fruits and Fruit Juices', 
                         'Nut and Seed Products'):
                pass  # biarkan lolos
            elif category == 'Drink':
                pass  # biarkan lolos
            else:
                return False
        
        # 3. Hapus pasta/grain kering (unprepared) tapi pertahankan dry roasted nuts
        if "dry" in name:
            if group == 'Nut and Seed Products':
                pass  # dry roasted nuts tetap valid
            elif category == 'Drink':
                pass  # minuman powder/dry tetap valid (sudah dihandle filter powder)
            elif any(k in name for k in ['dry roasted', 'dry mix prepared', 'dry heat']):
                pass  # dry roasted atau sudah diproses tetap valid
            elif group in ('Cereal Grains and Pasta', 'Breakfast Cereals', 'Sweets', 
                           'Soups, Sauces, and Gravies', 'Meals, Entrees, and Side Dishes',
                           'Baked Products'):
                return False  # dry mix/raw grain tidak siap konsumsi
        
        # 4. Pertahankan ayam goreng dengan tepung (cooked, fried, flour) 
        if "flour" in name:
            if group == 'Poultry Products' and 'cooked' not in name:
                return False
            elif group not in ('Poultry Products', 'Baked Products', 
                              'Snacks', 'Legumes and Legume Products'):
                if group in ('Cereal Grains and Pasta', 'Nut and Seed Products'):
                    return False  # tepung mentah tidak siap konsumsi
        
        # 5. Hapus untuk kata kunci lain (selain 'raw', 'dry', 'flour')
        kunci_lain = [k for k in kategori_dihapus if k not in ["raw", "dry", "flour", "meal"]]
        if any(k in name for k in kunci_lain):
            return False
            
        return True

    # Terapkan filter
    df_cleaned = df[df.apply(is_usable, axis=1)]

    # FILTER 1: Keyword filter - bumbu dan junk food
    invalid_keywords = ['extract', 'flavoring', 'seasoning', 'yeast']
    junk_keywords = ['candy', 'candy bar', 'confection', 'sweet candy',
                     'fudge', 'brownie', 'frosting', 'icing', 'ice cream', 
                     'mousse', 'caramel']
    all_keywords = invalid_keywords + junk_keywords
    
    # Filter keyword normal untuk semua kategori
    keyword_mask = df_cleaned['food_name'].str.lower().str.contains(
        '|'.join(all_keywords), na=False)
    
    # Jangan hapus oatmeal, meal replacement, dan arepa (mengandung 'meal' tapi valid)
    meal_exception_mask = (
        df_cleaned['food_name'].str.lower().str.contains('oatmeal|meal replacement|arepa', na=False)
    )
    # Update keyword_mask: exclude false positives dari 'meal'
    keyword_mask = keyword_mask & ~meal_exception_mask
    print(f"[FILTER 1 - EXCEPTION] Meal exceptions (oatmeal, meal replacement, arepa): {meal_exception_mask.sum()} items protected")
    
    # Jangan hapus roti dan baked goods berbahan yeast (yeast adalah bahan valid)
    yeast_bread_mask = (
        df_cleaned['food_name'].str.lower().str.contains('yeast', na=False) &
        (df_cleaned['food_group'] == 'Baked Products')
    )
    keyword_mask = keyword_mask & ~yeast_bread_mask
    print(f"[FILTER 1 - EXCEPTION] Yeast bread exceptions (Baked Products): {yeast_bread_mask.sum()} items protected")
    
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

    # FILTER 6: Fast food quality filter
    before = len(df_cleaned)
    fast_food_mask = df_cleaned['food_group'].isin(['Fast Foods', 'Restaurant Foods'])

    # Kriteria 6a: Hapus items dengan cholesterol > 130mg dari fast food/restaurant
    # (terlalu mendekati limit harian 200mg hanya dari 1 item)
    crit_cholesterol = (
        fast_food_mask &
        (df_cleaned['cholesterol_mg'] > 130)
    )

    # Kriteria 6b: Hapus dessert dan minuman manis dari fast food
    dessert_keywords = [
        'shake', 'frosty', 'mcflurry', 'sundae', 'french toast',
        'cinnamon roll', 'parfait', 'ice cream', 'vanilla cone'
    ]
    crit_dessert = (
        fast_food_mask &
        df_cleaned['food_name'].str.lower().str.contains(
            '|'.join(dessert_keywords), na=False
        )
    )

    # Kriteria 6c: Hapus pizza chain brand besar (processed, saturated fat tinggi)
    pizza_chain_keywords = [
        'pizza hut', "domino's", "papa john's", 'little caesars',
        'fast food, pizza chain', 'fast foods, pizza chain',
        'digiorno'
    ]
    crit_pizza_chain = (
        fast_food_mask &
        df_cleaned['food_name'].str.lower().str.contains(
            '|'.join([re.escape(k) for k in pizza_chain_keywords]), na=False
        )
    )

    # Kriteria 6d: Hapus breakfast items dengan sausage (cholesterol + fat tinggi)
    breakfast_sausage_keywords = [
        'sausage mcmuffin', 'sausage biscuit', 'sausage burrito',
        'sausage mcgriddles', 'big breakfast', 'croissan\'wich with sausage',
        'english muffin, with cheese and sausage',
        'biscuit, with egg and sausage', 'biscuit, with sausage',
        'griddle cake sandwich, sausage', 'griddle cake sandwich, egg, cheese, and sausage',
        'croissant, with egg, cheese, and sausage',
        'hotcakes and sausage', 'sausage muffin'
    ]
    crit_breakfast_sausage = (
        fast_food_mask &
        df_cleaned['food_name'].str.lower().str.contains(
            '|'.join([re.escape(k) for k in breakfast_sausage_keywords]), na=False
        )
    )

    # Kriteria 6e: Hapus junk snacks dari fast food
    junk_snack_keywords = [
        'miniature cinnamon rolls', 'french toast sticks',
        'popcorn chicken', 'hush puppies', 'onion rings, breaded and fried',
        'fast foods, shrimp, breaded and fried',
        'fast foods, chicken, breaded and fried, boneless',
        'fast foods, chicken tenders',
        'fast foods, fried chicken, skin and breading'
    ]
    crit_junk_snack = (
        fast_food_mask &
        df_cleaned['food_name'].str.lower().str.contains(
            '|'.join([re.escape(k) for k in junk_snack_keywords]), na=False
        )
    )

    # Gabungkan semua kriteria
    filter6_mask = (
        crit_cholesterol |
        crit_dessert |
        crit_pizza_chain |
        crit_breakfast_sausage |
        crit_junk_snack
    )

    df_cleaned = df_cleaned[~filter6_mask]
    after = len(df_cleaned)
    print(f"[FILTER 6a] Cholesterol > 130mg (fast food): {crit_cholesterol.sum()} items")
    print(f"[FILTER 6b] Dessert/minuman manis (fast food): {crit_dessert.sum()} items")
    print(f"[FILTER 6c] Pizza chain brand besar: {crit_pizza_chain.sum()} items")
    print(f"[FILTER 6d] Breakfast sausage items: {crit_breakfast_sausage.sum()} items")
    print(f"[FILTER 6e] Junk snacks fast food: {crit_junk_snack.sum()} items")
    print(f"[FILTER 6] Total fast food filter: {before - after} items removed")

    print(f"\n[SUMMARY] Dataset awal: {len(df)} items")
    print(f"[SUMMARY] Dataset final: {len(df_cleaned)} items")
    print(f"[SUMMARY] Total removed: {len(df) - len(df_cleaned)} items")

    df_cleaned.to_csv(output_file, index=False)
    print(f"Jumlah baris setelah dibersihkan: {len(df_cleaned)}")
    print(f"Total baris yang dihapus: {len(df) - len(df_cleaned)}")

if __name__ == "__main__":
    bersihkan_dataset(INPUT_FILE, OUTPUT_FILE)
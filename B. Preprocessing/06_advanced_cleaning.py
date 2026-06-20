import pandas as pd
import os
import re

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.normpath(os.path.join(CURRENT_DIR, "..", "A. Data", "Data Processed", "05_final_dataset.csv"))
OUTPUT_FILE = os.path.normpath(os.path.join(CURRENT_DIR, "..", "A. Data", "Data Processed", "06_final_dataset.csv"))

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
                     'mousse', 'caramel', 'human milk', 'infant formula', 
                     'nutritional shake', 'nutritional drink', 'shake mix']
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

    # FILTER 7: Hapus sisa fast food chain brand besar
    before = len(df_cleaned)
    fast_food_mask = df_cleaned['food_group'].isin(['Fast Foods', 'Restaurant Foods'])

    # Brand chain besar yang semua itemnya tidak cocok untuk diet penyakit kronis
    chain_brand_keywords = [
        "kfc,",
        "popeyes,",
        "burger king,",
        "wendy's,",
        "taco bell,",
        "chick-fil-a,",
        "arby's,",
        "mcdonald's,",
    ]

    # Generic fast food items bermasalah (sodium/saturated fat tinggi)
    generic_problematic = [
        "fast food, biscuit",
        "fast foods, biscuit, with crispy chicken",
        "fast foods, roast beef sandwich, plain",
        "fast foods, fried chicken, skin and breading",
        "fast foods, fried chicken, thigh, meat and skin",
        "fast foods, fried chicken, wing, meat and skin",
        "fast foods, fried chicken, breast, meat and skin",
    ]

    all_remove = chain_brand_keywords + generic_problematic

    filter7_mask = (
        fast_food_mask &
        df_cleaned['food_name'].str.lower().str.contains(
            '|'.join([re.escape(k.lower()) for k in all_remove]), na=False
        )
    )

    df_cleaned = df_cleaned[~filter7_mask]
    after = len(df_cleaned)
    print(f"[FILTER 7] Sisa fast food chain brand besar: {before - after} items removed")

    # FILTER 8: Blacklist item mentah/ingredient/tidak lazim dikonsumsi langsung
    before = len(df_cleaned)
    blacklist_keywords = [
        # Pastry/dough mentah - baking ingredient
        'pie crust', 'puff pastry', 'pastry shell', 'pastry dough',
        'tart shell', 'phyllo', 'filo', 'wafer crust', 'graham cracker crust',
        'deep dish crust', 'cookie crust',

        # Baking ingredient / tepung / bahan mentah
        'vital wheat gluten', 'wheat gluten',
        'baking mix', 'pancake mix',
        'soy flour', 'potato flour', 'corn flour', 'rice flour', 'oat flour',
        'wheat flour', 'almond flour', 'coconut flour', 'tapioca flour',
        'cornmeal', 'corn meal',        # tepung jagung - tidak dimakan langsung
        'wheat germ',                   # bahan suplemen, bukan makanan
        'wheat bran',                   # bahan suplemen
        'rice bran',

        # Biji/grain mentah - tidak siap konsumsi
        'uncooked', 'raw grain', 'rye grain', 'wheat grain', 'barley grain',
        'millet grain', 'oat grain', 'triticale',

        # Produk dehidrasi/kering yang tidak lazim dimakan langsung
        'freeze-dried', 'dehydrated', 'dried agar', 'dried seaweed',
        'sun-dried tomato',             # terlalu pekat, bukan makanan siap saji

        # Item kontraindikasi konsisten per penyakit
        'natto',            # tinggi protein & fosfor - kontraindikasi CKD
        'eggnog',           # tinggi gula & kolesterol - kontraindikasi DM2/CVD
        'pickled herring',  # sangat tinggi sodium - kontraindikasi hipertensi
        'salted lima beans', # kontraindikasi hipertensi

        # Item tidak layak konsumsi dewasa / tidak lazim
        'human milk',       # ASI - tidak untuk konsumsi dewasa
        'infant formula',   # susu bayi
        'baby food',        # makanan bayi
        'breadnut seeds',   # tidak lazim
        'fireweed',         # tidak lazim
        'lambsquarters',    # tidak lazim
        'poi ',             # makanan hawaii tidak familiar
        'conch',            # tidak lazim
        'pepao',            # jamur tidak lazim
        'pepeao',           # jamur tidak lazim
        'muscle milk',      # suplemen olahraga, bukan makanan umum
        'peanut meal supplement', # suplemen, bukan minuman biasa

        # Item yang masih lolos filter sebelumnya (tambahan spesifik)
        'human milk',           # ASI - tidak untuk konsumsi dewasa
        'fried chicken skin',   # kulit ayam goreng - kontraindikasi CKD & kolesterol
        'chicken skin',         # kulit ayam
        'raw potatoes',         # kentang mentah
        'raw garland',          # raw garland chrysanthemum - sayur mentah tidak lazim
        'raw european chestnut',# chestnuts mentah
        'raw california avocado',# avocado mentah (versi raw spesifik USDA)
        'dried agar',           # seaweed kering tidak lazim
        'sun-dried tomato',     # tomat kering - ingredient, bukan makanan siap saji
    ]

    blacklist_mask = df_cleaned['food_name'].str.lower().str.contains(
        '|'.join([re.escape(k) for k in blacklist_keywords]), na=False
    )
    df_cleaned = df_cleaned[~blacklist_mask]
    print(f"[FILTER 8] Blacklist item mentah/kontraindikasi: {before - len(df_cleaned)} items removed")

    # FILTER 9: Validasi food group per consumption_label (slot)
    # Tujuan: memastikan Main Course = protein/karbohidrat matang,
    # Side Dish = sayur/buah/legum matang, Drink = minuman, Snack = camilan bergizi
    before = len(df_cleaned)

    # Mapping food_group yang diizinkan per slot
    ALLOWED_GROUPS = {
        'Main Course': [
            'Beef Products',
            'Poultry Products',
            'Finfish and Shellfish Products',
            'Legumes and Legume Products',
            'Meals, Entrees, and Side Dishes',
            'Fast Foods',
            'Restaurant Foods',
            'Sausages and Luncheon Meats',
            'Baked Products',           # roti/sandwich sebagai main
            'Cereal Grains and Pasta',  # nasi matang, pasta, mie
            'Dairy and Egg Products',   # telur sebagai main
            'Lamb, Veal, and Game Products',
            'Pork Products',
        ],
        'Side Dish': [
            'Vegetables and Vegetable Products',
            'Fruits and Fruit Juices',
            'Legumes and Legume Products',
            'Nut and Seed Products',
            'Meals, Entrees, and Side Dishes',
            'Dairy and Egg Products',   # keju, yogurt sebagai side
            'Snacks',                   # crackers sebagai side
        ],
        'Drink': [
            'Beverages',
            'Dairy and Egg Products',   # susu, yogurt minum
            'Fruits and Fruit Juices',  # jus buah
        ],
        'Snack': [
            'Snacks',
            'Fruits and Fruit Juices',
            'Nut and Seed Products',
            'Dairy and Egg Products',
            'Baked Products',           # muffin, granola bar
            'Vegetables and Vegetable Products',
            'Legumes and Legume Products',
            'Sweets',                   # camilan manis sesekali
        ],
    }

    # Keyword tambahan untuk exclude item mentah di dalam food_group yang diizinkan
    # (misal: Raw Potatoes lolos Filter 9 karena food_group-nya Vegetables, padahal mentah)
    RAW_UNFIT_KEYWORDS = [
        'raw potato', 'raw yam', 'raw cassava', 'raw taro',   # umbi mentah
        'raw leek', 'raw onion', 'raw garlic', 'raw ginger',  # bumbu mentah
        'raw chrysanthemum', 'raw spinach leaves',             # sayur mentah tidak lazim
    ]

    raw_unfit_mask = df_cleaned['food_name'].str.lower().str.contains(
        '|'.join([re.escape(k) for k in RAW_UNFIT_KEYWORDS]), na=False
    )

    def is_valid_slot_group(row):
        label = row.get('consumption_label', '')
        group = row.get('food_group', '')
        allowed = ALLOWED_GROUPS.get(label)
        if allowed is None:
            return True  # label tidak dikenal, biarkan lolos
        return group in allowed

    filter9_mask = ~df_cleaned.apply(is_valid_slot_group, axis=1) | raw_unfit_mask
    df_cleaned = df_cleaned[~filter9_mask]
    print(f"[FILTER 9] Food group tidak sesuai slot + item mentah/unfit: {before - len(df_cleaned)} items removed")
    # Logging per slot setelah filter 9
    for label in ['Main Course', 'Side Dish', 'Drink', 'Snack']:
        count = (df_cleaned['consumption_label'] == label).sum()
        print(f"[FILTER 9] {label}: {count} items tersisa")

    # FILTER 10: Blacklist berdasarkan fdc_id (item yang lolos filter nama tapi tetap tidak layak)
    before = len(df_cleaned)
    fdc_blacklist = [
        # === Batch 1: item parah (Human Milk, Chicken Skin, dll) ===
        171279,  # Human Milk
        171453,  # Fried Chicken Skin (variant 1)
        171454,  # Fried Chicken Skin (variant 2)
        170026,  # Raw Potatoes (variant 1)
        170032,  # Raw Potatoes (variant 2)
        170090,  # Dried Agar Seaweed
        168567,  # Sun-Dried Tomatoes (variant 1)
        169384,  # Sun-Dried Tomatoes (variant 2)
        169995,  # Raw Garland Chrysanthemum
        170574,  # Raw European Chestnuts
        171706,  # Raw California Avocados

        # === Batch 2: tepung/biji mentah/bumbu kering ===
        172435,  # Low Fat Peanut Flour (tepung)
        174267,  # Defatted Peanut Flour (tepung)
        168579,  # Dried Pasilla Peppers (cabai kering = bumbu, bukan side dish)
        168891,  # Soft Red Winter Wheat (biji gandum mentah)
        168581,  # Dried Cloud Ears (jamur kering tidak lazim)
        168933,  # Semolina (tepung)
        169715,  # Enriched Semolina (tepung)

        # === Batch 3: tanaman tidak umum / mentah tidak lazim ===
        170078,  # Raw Eppaw (tanaman tidak dikenal)
        170070,  # Raw Winged Bean
        170476,  # Raw Winged Beans
        170477,  # Cooked Winged Beans (variant 1) - tidak lazim
        170478,  # Raw Winged Bean Leaves
        170550,  # Salted Cooked Winged Beans
        172453,  # Cooked Winged Beans (variant 2)
        172477,  # Winged Beans

        # === Batch 4: suplemen medis / meal replacement ===
        170892,  # Diabetes Nutritional Supplement (suplemen medis, bukan minuman)
        173170,  # High Protein SlimFast Shake (meal replacement)
        173171,  # SlimFast Meal Replacement

        # === Batch 5: biji buah mentah/tidak lazim ===
        170144,  # Raw Breadfruit Seeds
        170145,  # Boiled Breadfruit Seeds
        170595,  # Roasted Breadfruit Seeds

        # === Batch 6: item mentah/tidak lazim yang masih lolos ===
        167535,  # Flour Tortillas (tepung, bukan side dish)
        173242,  # Flour Tortillas (variant 2)
        175037,  # Flour Tortillas (variant 3)
        169205,  # Raw Artichokes (artichoke mentah)
        171939,  # Peanut Meal Supplement Drink (suplemen)
        168436,  # Dried Shiitake Mushrooms (jamur kering, tidak lazim)
        169396,  # Dried Ancho Peppers (cabai kering = bumbu)
        169241,  # Dried Gourd Strips (labu kering tidak lazim)
        169282,  # Raw Green Soybeans (edamame mentah)
        170431,  # Poi (makanan hawaii tidak familiar)
        167727,  # Ensure Plus Drink (suplemen medis)
        171707,  # Raw Florida Avocados (alpukat mentah)
        170028,  # Raw White Potatoes (kentang mentah)
        168396,  # Raw Lima Beans (kacang mentah)
        168890,  # Hard Red Winter Wheat (biji gandum mentah)
        170288,  # Yellow Corn (jagung mentah/biji)
        172452,  # Okara (ampas tahu, tidak lazim sbg side dish)

        # === Batch 7: tepung, biji/produk kering tidak layak konsumsi langsung ===
        173755,  # Carob Flour (tepung karob - bahan mentah)
        174288,  # Chickpea Flour (tepung kacang - bahan mentah)
        170147,  # Partially Defatted Cottonseed Meal (bahan pakan/industri)
        170559,  # Safflower Seed Meal (bahan pakan/industri)
        170561,  # Partially Defatted Sesame Meal (bahan pakan/industri)
        172750,  # Cracker Meal (tepung cracker untuk breading)
        168591,  # Raw Lotus Seeds (biji mentah perlu dimasak)
        169413,  # Raw Japanese Chestnuts (biji mentah perlu dimasak)
        170157,  # Raw Acorns (biji mentah beracun - perlu diproses)
        170164,  # Raw Chestnuts (biji mentah perlu dimasak)
        170552,  # Raw Breadnut Seeds (biji mentah tidak lazim)
        170553,  # Dried Breadnut Seeds (biji kering tidak lazim)
        170895,  # Dried Egg Whites (bahan industri/baking)
        171274,  # Dried Buttermilk (bahan industri/baking)
        171281,  # Dried Whey (bahan industri/baking)
        172188,  # Dried Whole Egg (bahan industri/baking)
        173425,  # Dried Whole Eggs (bahan industri/baking)
        173426,  # Dried Egg Whites variant 2 (bahan industri/baking)
        173428,  # Dried Egg Yolk (bahan industri/baking)
        172450,  # Dried Tofu (bahan masak, bukan siap saji)
        174303,  # Dried Tofu variant 2 (bahan masak, bukan siap saji)
        170495,  # Dried Spirulina (suplemen, bukan snack)
        168570,  # Sun-Dried Hot Chile Peppers (bumbu kering)
        168453,  # Dried Oriental Radishes (bahan masak kering)
        168587,  # Dried Sisymbrium Seeds (biji tanaman tidak lazim)

        # === Batch 8: suplemen alga + kacang/biji kering tidak lazim ===
        170091,  # Raw Spirulina (suplemen alga, bukan side dish)
        170565,  # Dried Acorns (biji oak kering, tidak lazim dimakan)
        170161,  # Dried Beechnuts (tidak lazim)
        170177,  # Dried Hickorynuts (tidak lazim)
        170570,  # Dried Butternuts (tidak lazim)
        170590,  # Dried Pili Nuts (tidak lazim di konteks Indonesia)

        # === batch 9 = raw/unfit item yang masih lolos filter sebelumnya ===
        170432,  # Raw Pokeberry Shoots (BERACUN — pokeberry tumbuhan berbahaya)
        170433,  # Cooked Pokeberry Shoots (sama, tetap berbahaya)
        170518,  # Cooked Pokeberry Shoots (v2) (sama)
        169234,  # Raw Hyacinth Beans (mentah = beracun, mengandung sianida)
        168573,  # Raw Lemongrass (bumbu, bukan snack siap makan)
        168583,  # Raw Wasabi (condiment, bukan side dish)
        169230,  # Raw Garlic (bumbu mentah, bukan side dish)
        169994,  # Raw Chives (bumbu/garnish)
        170499,  # Raw Shallots (bumbu mentah)
        168456,  # Raw Irish Moss (seaweed mentah, tidak lazim)
        168457,  # Raw Kelp (seaweed mentah)
        168458,  # Raw Seaweed (seaweed mentah)
        169280,  # Raw Agar Seaweed (seaweed mentah)
        170496,  # Raw Wakame Seaweed (seaweed mentah)
        168490,  # Raw Arrowroot (umbi pati mentah, bahan tepung)
        169308,  # Raw Taro (umbi perlu dimasak)
        169310,  # Raw Taro (v2) (sama)
        169985,  # Raw Cassava (BERACUN mentah, singkong)
        170071,  # Raw Yam (umbi perlu dimasak)
        170027,  # Raw Russet Potatoes (kentang mentah)
        168405,  # Raw Cowpeas (kacang mentah)
        168574,  # Raw Fava Beans (kacang mentah)
        171283,  # Sweet Whey Powder (bahan industri/baking)
        169993,  # Raw Chicory Roots (akar tanaman, bukan side dish)
        170481,  # Raw Borage (tanaman herbal, tidak lazim)
        170000,  # Raw Onions (bumbu mentah, bukan side dish)
        168889,  # Raw Hard Red Spring Wheat (biji gandum mentah)
        169719,  # Hard White Wheat (biji gandum mentah)
        169720,  # Soft White Wheat (biji gandum mentah)
        169725,  # Raw Wheat (biji gandum mentah)
        175042,  # Compressed Yeast (bahan industri/baking)
        170497,  # Raw Green Chili Peppers (sayuran mentah)
        168215,  # Raw Green Plantains (buah seperti pisang hijau mentah)
        170086,  # Raw Sprouted Pinto Beans (kacang pinto, biji matang, berkecambah, mentah)
        169957,  # Raw Sprouted Mung Beans (kacang hijau, biji matang, berkecambah, mentah)
        169284,  # Raw Sprouted Soybeans (kedelai, biji matang, berkecambah, mentah)
        169213,  # Raw Sprouted Kidney Beans (kacang merah, biji matang, berkecambah, mentah)
        169139,  # Raw Sprouted Navy Beans (kacang navy, biji matang, berkecambah, mentah)
        168427,  # Raw Sprouted Lentils (lentil, berkecambah, mentah)
        170422,  # Raw Sprouted Peas (kacang polong, biji matang, berkecambah, mentah)
        171282,  # Sweet Whey (bahan industri/baking)
        170885,  # Acid Whey (bahan industri/baking)
        170686,  # Roasted Buckwheat Groats (cereal grains and pasta)
        170286,  # Buckwheat (cereal grains and pasta)
        169277,  # Raw Salsify (vegetables and vegetable products)

    ]
    df_cleaned = df_cleaned[~df_cleaned['fdc_id'].isin(fdc_blacklist)]
    print(f"[FILTER 10] fdc_id blacklist: {before - len(df_cleaned)} items removed")

    print(f"\n[SUMMARY] Dataset awal: {len(df)} items")
    print(f"[SUMMARY] Dataset final: {len(df_cleaned)} items")
    print(f"[SUMMARY] Total removed: {len(df) - len(df_cleaned)} items")

    df_cleaned.to_csv(output_file, index=False)
    print(f"Jumlah baris setelah dibersihkan: {len(df_cleaned)}")
    print(f"Total baris yang dihapus: {len(df) - len(df_cleaned)}")

if __name__ == "__main__":
    bersihkan_dataset(INPUT_FILE, OUTPUT_FILE)
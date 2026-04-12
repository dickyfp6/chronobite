"""
Module untuk menangani input dari user
"""

def get_user_input():
    """
    Mengambil input dari user melalui CLI
    
    Returns:
        dict: Data user dengan keys:
            - gender: 'M' atau 'F'
            - age: int (tahun)
            - weight: float (kg)
            - height: float (cm)
            - activity_factor: float (1.2-1.9)
            - disease: str (kondisi kesehatan)
            - food_preferences: list (preferensi makanan)
    """
    
    print("\n" + "="*60)
    print("SISTEM PERHITUNGAN KEBUTUHAN NUTRISI")
    print("="*60 + "\n")
    
    # Input Demografis
    while True:
        gender = input("Gender (M/F): ").upper().strip()
        if gender in ['M', 'F']:
            break
        print("Input invalid. Choose M or F.")
        
    while True:
        try:
            age = int(input("Age (years): "))
            if 18 <= age <= 100: 
                break
            print("Age must be between 18-100 years.")
        except ValueError:
            print("Input must be a number.")
    
    while True:
        try:
            weight = float(input("Weight (kg): "))
            if weight > 0: 
                break
            print("Weight must be a positive number.")
        except ValueError:
            print("Input must be a number.")
    while True:
        try:
            height = float(input("Height (cm): "))
            if 100 <= height <= 300: 
                break
            print("Height must be between 100-300 cm.")
        except ValueError:
            print("Input must be a number.")
    
    # Activity Factor (Updated based on FAO/WHO/UNU Guidelines)
    print("\nPilihan Aktivitas (Berdasarkan Gaya Hidup):")
    print("1. Sedentary or Light Activity (Contoh: Pekerja kantoran, jarang olahraga) [PAL: 1.40]")
    print("2. Active or Moderately Active (Contoh: Konstruksi, guru, rutin jogging) [PAL: 1.70]")
    print("3. Vigorous or Vigorously Active (Contoh: Atlet, kuli panggul, olahraga intens) [PAL: 2.00]")
    
    activity_mapping = {
        '1': 1.40,  # Batas bawah kategori Sedentary/Light
        '2': 1.70,  # Batas bawah kategori Active/Moderate
        '3': 2.00   # Batas bawah kategori Vigorous
    }

    while True:
        activity_choice = input("Pilih aktivitas (1-3): ").strip()
        if activity_choice in activity_mapping:
            activity_factor = activity_mapping[activity_choice]
            break
        print("Input tidak valid. Pilih 1-3.")
    
    # Kondisi Kesehatan (Bisa Multi-Penyakit)
    print("\nKondisi Kesehatan (Bisa pilih maksimal 3, pisahkan dengan koma):")
    print("1. Normal")
    print("2. Diabetes Tipe 2 (DM2)")
    print("3. Hipertensi")
    print("4. Penyakit Kardiovaskular (CVD)")
    print("5. Kolesterol Tinggi")
    print("6. Penyakit Ginjal Kronis (CKD)")
    
    disease_mapping = {
        '1': 'normal',
        '2': 'dm2',
        '3': 'hypertension',
        '4': 'cvd',
        '5': 'cholesterol',
        '6': 'ckd'
    }
    
    while True:
        choices = input("Pilih kondisi kesehatan (contoh: 2 atau 2,3): ").strip()
        
        # 1. Pecah input jadi list (misal "2,3" jadi ["2", "3"])
        choice_list = [c.strip() for c in choices.split(',') if c.strip()]
        
        # 2. Cek apakah ada input kosong
        if not choice_list:
            print("Input tidak boleh kosong.")
            continue

        # 3. Validasi: Apakah semua angka ada di menu 1-6?
        if not all(c in disease_mapping for c in choice_list):
            print("Input tidak valid. Masukkan angka 1-6.")
            continue
            
        # 4. Ambil label penyakitnya
        selected_labels = [disease_mapping[c] for c in choice_list]
        
        # 5. SATPAM: Cek kontradiksi 'Normal' vs Penyakit
        if 'normal' in selected_labels:
            if len(selected_labels) > 1:
                print("⚠ Pilihan 'Normal' tidak bisa digabung dengan penyakit lain!")
                continue
            disease = 'normal' # Output string tunggal jika normal
        
        # 6. SATPAM: Cek jumlah maksimal
        elif len(selected_labels) > 3:
            print("⚠ Maksimal pilih 3 kombinasi penyakit.")
            continue
            
        else:
            disease = selected_labels # Output list jika penyakit (misal: ['dm2', 'hypertension'])
            
        break # Berhasil lolos semua validasi!
    
    # 1. Menampilkan pilihan ke user
    print("\nPreferensi Makanan (Pilih angka, pisahkan dengan koma):")
    print("1. Asian")
    print("2. Western")
    print("3. Mediterranean")
    
    cuisine_mapping = {
        '1': 'Asian',
        '2': 'Western',
        '3': 'Mediterranean'
    }
    
    while True:
        # 2. Mengambil input mentah (misal user ketik: "1, 2")
        cuisine_input = input("Masukkan pilihan (contoh: 1,2 atau biarkan kosong untuk semua): ").strip()
        
        # 3. Handling jika user tidak memilih (Langsung Enter)
        if not cuisine_input:
            food_preferences = []
            break
            
        # 4. MEMECAH INPUT: Mengubah "1, 2" menjadi ["1", "2"]
        # Pakai 'cuisine_input', bukan 'choices' (tadi sempat typo di sini)
        choice_list = [c.strip() for c in cuisine_input.split(',') if c.strip()]
        
        # 5. VALIDASI ANGKA: Cek apakah semua angka ada di menu (1-3)
        if all(c in cuisine_mapping for c in choice_list):
            # Jika valid, ubah angka jadi label teks (misal: ["Asian", "Western"])
            food_preferences = [cuisine_mapping[c] for c in choice_list]
            break
        else:
            print("⚠ Input tidak valid. Masukkan angka 1-3 saja.")
    
    user_data = {
        'gender': gender,
        'age': age,
        'weight': weight,
        'height': height,
        'activity_factor': activity_factor,
        'disease': disease,
        'food_preferences': food_preferences
    }
    
    return user_data

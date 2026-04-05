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
        gender = input("Jenis Kelamin (M/F): ").upper().strip()
        if gender in ['M', 'F']:
            break
        print("Input tidak valid. Pilih M atau F.")
    
    while True:
        try:
            age = int(input("Usia (tahun): "))
            if 14 <= age <= 100:
                break
            print("Usia harus antara 14-100 tahun.")
        except ValueError:
            print("Input harus berupa angka.")
    
    while True:
        try:
            weight = float(input("Berat Badan (kg): "))
            if weight > 0:
                break
            print("Berat badan harus lebih dari 0.")
        except ValueError:
            print("Input harus berupa angka.")
    
    while True:
        try:
            height = float(input("Tinggi Badan (cm): "))
            if height > 0:
                break
            print("Tinggi badan harus lebih dari 0.")
        except ValueError:
            print("Input harus berupa angka.")
    
    # Activity Factor
    print("\nPilihan Aktivitas:")
    print("1. Sedentary (jarang olahraga) - 1.2")
    print("2. Light (olahraga 1-3 hari/minggu) - 1.375")
    print("3. Moderate (olahraga 3-5 hari/minggu) - 1.55")
    print("4. Very Active (olahraga 6-7 hari/minggu) - 1.725")
    print("5. Extremely Active (olahraga setiap hari/atlet) - 1.9")
    
    activity_mapping = {
        '1': 1.2,
        '2': 1.375,
        '3': 1.55,
        '4': 1.725,
        '5': 1.9
    }
    
    while True:
        activity_choice = input("Pilih aktivitas (1-5): ").strip()
        if activity_choice in activity_mapping:
            activity_factor = activity_mapping[activity_choice]
            break
        print("Input tidak valid. Pilih 1-5.")
    
    # Kondisi Kesehatan
    print("\nKondisi Kesehatan:")
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
        disease_choice = input("Pilih kondisi kesehatan (1-6): ").strip()
        if disease_choice in disease_mapping:
            disease = disease_mapping[disease_choice]
            break
        print("Input tidak valid. Pilih 1-6.")
    
    # Preferensi Makanan
    print("\nPreferensi Makanan (pisahkan dengan koma):")
    print("Contoh: Western, Asian, Other")
    cuisine_input = input("Masukkan preferensi (atau biarkan kosong): ").strip()
    food_preferences = [c.strip() for c in cuisine_input.split(',')] if cuisine_input else []
    
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


def validate_user_input(user_data):
    """
    Validasi data user
    
    Args:
        user_data: dict dari get_user_input()
    
    Returns:
        bool: True jika valid, False jika tidak
    """
    required_keys = ['gender', 'age', 'weight', 'height', 'activity_factor', 'disease']
    
    if not all(key in user_data for key in required_keys):
        return False
    
    if user_data['gender'] not in ['M', 'F']:
        return False
    
    if not (14 <= user_data['age'] <= 100):
        return False
    
    if user_data['weight'] <= 0 or user_data['height'] <= 0:
        return False
    
    if not (1.2 <= user_data['activity_factor'] <= 1.9):
        return False
    
    valid_diseases = ['normal', 'dm2', 'hypertension', 'cvd', 'cholesterol', 'ckd']
    if user_data['disease'] not in valid_diseases:
        return False
    
    return True

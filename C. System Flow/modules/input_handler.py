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
    
    # Handle both single disease (string) and multiple diseases (list)
    disease = user_data['disease']
    if isinstance(disease, list):
        # If list, all diseases must be valid
        if not disease or not all(d in valid_diseases for d in disease):
            return False
    else:
        # If string, must be valid disease
        if disease not in valid_diseases:
            return False
    
    return True

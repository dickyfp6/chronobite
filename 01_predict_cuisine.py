"""
CUISINE PREDICTION - Heuristic Auto-labeling
Prediksi cuisine label (Asian, Western, Mediterranean, International)
untuk dataset 03_dataset_halal yang akan di-validate manual
"""

import pandas as pd
import re
from pathlib import Path

# ======================
# LOAD DATA
# ======================
print("\n" + "="*70)
print("CUISINE PREDICTION - Auto-labeling")
print("="*70)

input_file = Path("A. Data/Data Processed/03_dataset_halal.csv")
data = pd.read_csv(input_file)
print(f"\n[1/3] Loading data: {len(data)} items")

# ======================
# DEFINE KEYWORDS
# ======================

asian_keywords = [
    r'asian', r'thai', r'vietnam', r'chinese', r'japanese', r'korean',
    r'sushi', r'pho', r'dumpling', r'noodle', r'wonton', r'baozi',
    r'soy sauce', r'ginger', r'sesame', r'wasabi', r'miso', r'tofu',
    r'stir.?fry', r'pad thai', r'ramen', r'udon', r'teriyaki', r'gyoza',
    r'edamame', r'kimchi', r'tempeh', r'bok choy'
]

western_keywords = [
    r'beef', r'pork', r'chicken', r'pasta', r'burger', r'steak',
    r'sandwich', r'pizza', r'cheese', r'butter', r'cream', r'milk',
    r'yogurt(?!.*greek)', r'bacon', r'ham', r'sausage', r'meatball',
    r'hotdog', r'frankfurter', r'lasagna', r'macaroni', r'spaghetti',
    r'bread', r'bagel', r'donut', r'cookie', r'cake', r'pie'
]

mediterranean_keywords = [
    r'olive', r'feta', r'hummus', r'tahini', r'greek', r'italian',
    r'spanish', r'portuguese', r'mediterranean', r'pita', r'tzatziki',
    r'risotto', r'polenta', r'pesto', r'calamari', r'squid', r'anchovy',
    r'eggplant', r'zucchini', r'falafel', r'kebab', r'gyro', r'shawarma',
    r'harissa', r'couscous', r'tabbouleh', r'moussaka', r'paella'
]

# ======================
# PREDICTION FUNCTION
# ======================

def predict_cuisine(row):
    """Predict cuisine based on food_name and food_group"""
    
    text = f"{row['food_name']} {row['food_group']}".lower()
    
    # Check Asian
    if any(re.search(kw, text) for kw in asian_keywords):
        return 'Asian'
    
    # Check Mediterranean
    if any(re.search(kw, text) for kw in mediterranean_keywords):
        return 'Mediterranean'
    
    # Check Western
    if any(re.search(kw, text) for kw in western_keywords):
        return 'Western'
    
    # Default: International
    return 'International'

# ======================
# APPLY PREDICTION
# ======================
print(f"\n[2/3] Predicting cuisine labels...")
data['cuisine_prediction'] = data.apply(predict_cuisine, axis=1)

# ======================
# DISTRIBUTION
# ======================
print(f"\n[3/3] Distribution hasil prediksi:")
print(data['cuisine_prediction'].value_counts())

# ======================
# SAVE
# ======================
output_file = Path("A. Data/Data Raw/03_dataset_cuisine_prediction.csv")
data.to_csv(output_file, index=False)
print(f"\n✓ Saved: {output_file}")
print("\n" + "="*70)
print("Ready untuk manual validation!")
print("="*70)
print("\nNext step: Validasi hasil prediksi, kemudian upload file yang sudah")
print("di-validate untuk training cuisine_classifier")

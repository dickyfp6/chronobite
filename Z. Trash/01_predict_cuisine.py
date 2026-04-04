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

def predict_cuisine_with_confidence(row):
    """Predict cuisine based on food_name and food_group with confidence score"""
    
    text = f"{row['food_name']} {row['food_group']}".lower()
    
    # Count matches for each cuisine
    asian_matches = sum(1 for kw in asian_keywords if re.search(kw, text))
    mediterranean_matches = sum(1 for kw in mediterranean_keywords if re.search(kw, text))
    western_matches = sum(1 for kw in western_keywords if re.search(kw, text))
    
    # Find max matches
    max_matches = max(asian_matches, mediterranean_matches, western_matches)
    
    # Determine cuisine and calculate base confidence
    if max_matches == 0:
        cuisine = 'International'
        base_confidence = 0.0
    elif asian_matches == max_matches:
        cuisine = 'Asian'
        # Base: 30% + (5% per match), capped at 95%
        base_confidence = min(95.0, 30 + (asian_matches * 12))
    elif mediterranean_matches == max_matches:
        cuisine = 'Mediterranean'
        base_confidence = min(95.0, 30 + (mediterranean_matches * 12))
    elif western_matches == max_matches:
        cuisine = 'Western'
        base_confidence = min(95.0, 30 + (western_matches * 12))
    
    # Adjust confidence based on ambiguity
    if max_matches > 0:
        # Count how many cuisines have matches
        cuisines_with_matches = sum([asian_matches > 0, mediterranean_matches > 0, western_matches > 0])
        
        # If multiple cuisines have strong matches, reduce confidence
        match_list = sorted([asian_matches, mediterranean_matches, western_matches], reverse=True)
        if len([x for x in match_list if x > 0]) > 1:
            # Multiple cuisines have matches - reduce confidence
            if match_list[0] - match_list[1] <= 1:
                base_confidence *= 0.5  # Very ambiguous
            elif match_list[0] - match_list[1] <= 2:
                base_confidence *= 0.7  # Somewhat ambiguous
            else:
                base_confidence *= 0.85  # Small ambiguity
    
    confidence = round(max(5, base_confidence), 2)  # Minimum 5% for default predictions
    return pd.Series({'cuisine_prediction': cuisine, 'confidence': confidence})

# ======================
# APPLY PREDICTION
# ======================
print(f"\n[2/3] Predicting cuisine labels with confidence...")
prediction_result = data.apply(predict_cuisine_with_confidence, axis=1)
data['cuisine_prediction'] = prediction_result['cuisine_prediction']
data['confidence'] = prediction_result['confidence']

# ======================
# DISTRIBUTION
# ======================
print(f"\n[3/3] Distribution hasil prediksi:")
print(data['cuisine_prediction'].value_counts())

print(f"\n📊 Confidence Summary (per cuisine):")
for cuisine in data['cuisine_prediction'].unique():
    subset = data[data['cuisine_prediction'] == cuisine]['confidence']
    print(f"\n  {cuisine}:")
    print(f"    Count: {len(subset)}")
    print(f"    Avg Confidence: {subset.mean():.2f}%")
    print(f"    Min Confidence: {subset.min():.2f}%")
    print(f"    Max Confidence: {subset.max():.2f}%")
    low_confidence = (subset < 30).sum()
    if low_confidence > 0:
        print(f"    ⚠️  Low Confidence (<30%): {low_confidence} items")

# ======================
# SAVE
# ======================
output_file = Path("A. Data/Data Raw/03_dataset_cuisine_prediction.csv")
data.to_csv(output_file, index=False)
print(f"\n✓ Saved: {output_file}")
print("\n" + "="*70)
print("🔍 VALIDATION GUIDE:")
print("="*70)
print(f"\nTotal items to validate: {len(data)}")
print(f"Priority checks (Low Confidence < 30%): {(data['confidence'] < 30).sum()} items")
print(f"\nFilter dalam CSV dengan confidence < 30% untuk validasi lebih detail.")
print("\nColumn baru tersedia:")
print("  - confidence: Tingkat keyakinan model (0-100%)")
print("                Semakin tinggi = semakin yakin prediksinya benar")
print("\n" + "="*70)

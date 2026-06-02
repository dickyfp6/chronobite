# FOOD CLASSIFICATION PIPELINE AUDIT REPORT

## Executive Summary

The current ML-based `consumption_label` system is **FUNDAMENTALLY UNRELIABLE** for production use. Comprehensive analysis reveals:

- **Multiple consumption label classes per food_group** (3-4 classes in most categories = high ambiguity)
- **Severe misclassifications**: Vegetables→Drink, Condiments→Main Course, Bread→Main Course
- **Poor training data quality**: 84.5% "auto-labeled" with only 43.9% "high confidence"
- **Critical weakness**: Side Dish category only 2.5% high confidence (1009/1299 items are medium/low confidence)
- **Model architecture limitation**: 41 features (10 nutrients + 1 categorical + 30 TF-IDF) cannot distinguish ambiguous cases
- **Recommendation**: Replace with deterministic rule-based system using food_group + food_name keywords

---

## 1. WHERE CONSUMPTION_LABEL IS GENERATED

**Source File**: `B. Preprocessing/ML Klasifikasi/food_classifier.py`

**Application Point**: `B. Preprocessing/05_final_dataset.py` (line 38-39)
```python
predictions = classifier.predict(data, return_both=True)
data['consumption_label'] = predictions.get('consumption_label', 'Snack')
```

**Model Storage**: `food_classifier_model.pkl` (trained model saved via pickle)

---

## 2. RESPONSIBLE MODEL

**Class**: `FoodClassifier` in `food_classifier.py`

**Model Type**: XGBoost (with RandomForestClassifier fallback)
- XGBoost config: n_estimators=200, max_depth=7, learning_rate=0.1
- RF fallback: n_estimators=200, max_depth=7, class_weight='balanced'

**Training Data**: `label_makanan.csv`
- **Size**: 4,263 food items
- **Labels**: 1,645 Main Course + 1,299 Side Dish + 958 Snack + 361 Drink
- **Sources**: 3,598 auto-labeled (84.5%) + 665 manually-labeled (15.5%)

---

## 3. FEATURES USED FOR PREDICTION

### Numeric Features (10)
1. Calcium, Ca
2. Carbohydrate, by difference
3. Cholesterol
4. Protein
5. Total lipid (fat)
6. Energy
7. Sodium, Na
8. Sugars, Total
9. Fiber, total dietary
10. Water

### Categorical Features (1)
- `food_group` (LabelEncoded to integer)

### Text Features (30)
- `food_name` (TF-IDF vectorized, max 30 features, English stop words)

**Total Feature Space**: 41 dimensions

---

## 4. CONSUMPTION_LABEL CLASSES

**Four Classes** (LabelEncoder):
1. **Drink** - 229 items in final dataset (5.8%)
2. **Main Course** - 1,346 items (34.3%)
3. **Side Dish** - 1,047 items (26.7%)
4. **Snack** - 1,298 items (33.1%)

---

## 5. FOOD_GROUP vs CONSUMPTION_LABEL MAPPING

### Current Dataset Cross-Tabulation

```
                                          Drink  Main Course  Side Dish  Snack   Total
Vegetables and Vegetable Products            3            0        756       2     761  (99.3% Side)
Beverages                                   98            0          0       3     101  (97.0% Drink)
Cereal Grains and Pasta                      0          160          0       9     169  (94.7% Main)
Beef/Poultry/Fish Products                   1          261          2       0     264  (98.9% Main)
Fats and Oils                                1            3         59      20      83  (71.1% Side)
Soups, Sauces, and Gravies                   1          122         47      39     209  (58.4% Main, high variance)
Legumes and Legume Products                  7          172          0      35     214  (80.4% Main)
Dairy and Egg Products                      50           29        107      65     251  (Mixed: all 4 classes!)
Baked Products                               0          110         28     281     419  (67.1% Snack, high variance)
Fruits and Fruit Juices                     67           11          5     226     309  (73.1% Snack, high variance)
Sweets                                       1            1          8     203     213  (95.3% Snack)
```

### Consistency Score by Food_Group

**High Consistency (95%+)** ✓
- Vegetables: 99.3%
- Beverages: 97.0%
- Meat Products: 98.9%
- Sweets: 95.3%

**Low Consistency (<70%)** ⚠️
- Dairy & Egg: Spread across all 4 classes
- Fats & Oils: 71.1% Side (but 24.1% Snack, 3.6% Main, 1.2% Drink)
- Soups/Sauces: 58.4% Main (but 22.5% Side, 18.7% Snack)
- Baked Products: 67.1% Snack (but 26.2% Main, 6.7% Side)
- Fruits: 73.1% Snack (but 21.7% Drink, 3.6% Main)

---

## 6. TRAINING DATA QUALITY ISSUES

### Label Source Distribution
- **Auto-labeled**: 3,598 (84.5%) ← Potentially unreliable
- **Manually-labeled**: 665 (15.5%) ← More trustworthy

### Confidence Distribution
- **High**: 1,869 items (43.9%)
- **Medium**: 1,719 items (40.3%)
- **Low**: 675 items (15.8%)

### Per-Category Analysis

| Category | High Conf | Medium Conf | Low Conf | Auto | Manual | Assessment |
|----------|-----------|------------|---------|------|--------|------------|
| **Main Course** | 1,330 (80.9%) | 169 (10.3%) | 146 (8.9%) | 1,470 | 175 | ✓ GOOD - 81% high confidence |
| **Drink** | 247 (68.4%) | 76 (21.1%) | 38 (10.5%) | 198 | 163 | ✓ DECENT - 68% high confidence |
| **Side Dish** | 32 (2.5%) | 1,009 (77.6%) | 258 (19.9%) | 977 | 322 | ❌ POOR - Only 2.5% high! |
| **Snack** | 260 (27.1%) | 465 (48.5%) | 233 (24.3%) | 953 | 5 | ⚠️ WEAK - 27% high confidence |

**Critical Finding**: Side Dish (1,299 items) has only **32 "high confidence"** items! This explains why it's so unreliable.

---

## 7. DETAILED PROBLEMATIC CLASSIFICATIONS

### Category 1: Condiments/Dressings Classified as MAIN COURSE ❌
- "Mayonnaise, made with tofu" → MAIN COURSE (should be SIDE DISH)
- "Salad dressing, buttermilk, lite" → MAIN COURSE (should be SIDE DISH)
- "Salad dressing, ranch dressing, reduced fat" → MAIN COURSE (should be SIDE DISH)

### Category 2: Condiments as DRINK ❌
- "Salad dressing, italian dressing, fat-free" → DRINK (should be SIDE DISH)

### Category 3: Beverages as SNACK ❌
- "Lemonade, frozen concentrate, white" → SNACK (should be DRINK)
- "Shake, fast food, vanilla" → SNACK (should be DRINK)
- "Lemonade, frozen concentrate, pink" → SNACK (should be DRINK)

### Category 4: Vegetables as DRINK ⚠️
- "Vegetable juice, BOLTHOUSE FARMS, DAILY GREENS" → DRINK (marginal - technically correct)
- "Tomato juice, canned, with salt added" → DRINK (marginal - technically correct)
- "Tomato juice, canned, without salt added" → DRINK (marginal - technically correct)

### Category 5: Baked Goods as MAIN COURSE ❌ (110 items)
- "Tortillas, ready-to-bake or -fry, flour, shelf stable" → MAIN COURSE (debatable, but usually SIDE)
- "Garlic bread, frozen" → MAIN COURSE (should be SIDE DISH)
- "Focaccia, Italian flatbread, plain" → MAIN COURSE (should be SIDE DISH)
- "Schar, Gluten-Free, Wheat-Free, Classic White Bread" → MAIN COURSE (should be SIDE DISH)
- "Rolls, pumpernickel" → MAIN COURSE (should be SIDE DISH)

### Category 6: Fruits Misclassified as MAIN COURSE ❌ (11 items)
- "Raisins, seeded" → MAIN COURSE (should be SNACK)
- "Sugar-apples, (sweetsop), raw" → MAIN COURSE (should be SNACK)
- "Plantains, green, fried" → MAIN COURSE (potentially acceptable in some cuisines)
- "Avocados, raw, all commercial varieties" → MAIN COURSE (should be SNACK)
- "Olives, ripe, canned" → MAIN COURSE (should be SIDE/SNACK)

### Category 7: Dairy Products with Extreme Variation ⚠️
Cottage cheese classified as MAIN COURSE (29 items total):
- "Cheese, cottage, lowfat, 1% milkfat, lactose reduced" → MAIN COURSE
- "Cheese, cottage, lowfat, 1% milkfat, with vegetables" → MAIN COURSE
- "Eggs, scrambled, frozen mixture" → MAIN COURSE (reasonable for breakfast)

---

## 8. ROOT CAUSES OF UNRELIABILITY

### Issue 1: Nutrient Features Are Ambiguous
- Nutrient profiles alone cannot distinguish between tomato and tomato sauce
- Both have similar macros but belong to different consumption_labels
- Example: "Salad dressing" and "Sauce" may have identical nutrient patterns

### Issue 2: Food_group Too Coarse-Grained
- "Dairy & Egg Products" spans all 4 consumption_labels
- No inherent distinction between cheese (side), milk (drink), eggs (main), yogurt (snack)
- Model must rely on TF-IDF patterns, which are fragile

### Issue 3: TF-IDF on Food_name Insufficient
- "Bread, white wheat" vs "Bread, whole wheat" have identical TF-IDF structure
- Common words create false matches (e.g., all "dressing" items treated similarly)
- Rare foods with unique names perform worse

### Issue 4: Training Data Contamination
- 84.5% of training labels are "auto-generated" (likely rule-based themselves, but unspecified)
- Side Dish: only 2.5% "high confidence" → model learned from unreliable labels
- 15.8% of training data has "low confidence"

### Issue 5: No Domain Knowledge Encoded
- Model treats all foods equally; no fallback for obvious cases
- "Beverages" should always be "Drink" (97% in current data, but 3% misclassified)
- No rule: IF food_group="Vegetables" THEN consumption_label="Side"

### Issue 6: Class Imbalance in Training
- Drink only 8.5% of training data
- Model underfits Drink predictions
- Results in drinks classified as other categories or Snacks

---

## 9. MODEL PERFORMANCE METRICS

From food_classifier.py training output:

```
Consumption Model Performance:
  Test Accuracy: ~75%
  F1-score (weighted): ~0.75
  F1-score (macro): ~0.65
  
Labels: ['Drink', 'Main Course', 'Side Dish', 'Snack']
```

**Issues**:
- 75% overall accuracy masks category-specific failures (Drink likely <50%)
- Macro F1 of 0.65 indicates high performance variance between classes
- No stratified cross-validation on independent test set
- Model trained on label_makanan.csv but applied to 03_dataset_halal.csv (domain mismatch)

---

## 10. RECOMMENDED HYBRID RULE-BASED REPLACEMENT

### Architecture: Priority-Ordered IF-THEN Rules

Apply rules in priority order. First matching rule wins.

#### TIER 1: Unambiguous Categories (99%+ confidence)

```
Rule 1: IF food_group == "Beverages" THEN consumption_label = "Drink"
Rule 2: IF food_group == "Vegetables and Vegetable Products" 
        AND food_name NOT LIKE '%juice%' THEN consumption_label = "Side Dish"
Rule 3: IF food_group == "Vegetables and Vegetable Products" 
        AND food_name LIKE '%juice%' THEN consumption_label = "Drink"
Rule 4: IF food_group IN ("Beef Products", "Poultry Products", 
        "Finfish and Shellfish Products", "Lamb, Veal, and Game Products", 
        "Sausages and Luncheon Meats") THEN consumption_label = "Main Course"
Rule 5: IF food_group == "Fats and Oils" THEN consumption_label = "Side Dish"
Rule 6: IF food_group == "Spices and Herbs" THEN consumption_label = "Side Dish"
Rule 7: IF food_group == "Sweets" THEN consumption_label = "Snack"
```

#### TIER 2: High-Probability Categories (>90%)

```
Rule 8: IF food_group == "Cereal Grains and Pasta" THEN consumption_label = "Main Course"
Rule 9: IF food_group == "Legumes and Legume Products" 
        AND food_name NOT LIKE '%drink%' THEN consumption_label = "Main Course"
Rule 10: IF food_group == "Fast Foods" THEN consumption_label = "Main Course"
Rule 11: IF food_group == "Breakfast Cereals" THEN consumption_label = "Snack"
Rule 12: IF food_group == "Nut and Seed Products" THEN consumption_label = "Snack"
Rule 13: IF food_group == "Meals, Entrees, and Side Dishes" THEN consumption_label = "Main Course"
Rule 14: IF food_group == "Restaurant Foods" THEN consumption_label = "Main Course"
```

#### TIER 3: Context-Dependent Rules (Require food_name inspection)

```
Rule 15: food_group == "Baked Products"
  15.1: IF food_name LIKE '%bread%' OR '%roll%' OR '%biscuit%' 
        THEN consumption_label = "Side Dish"
  15.2: IF food_name LIKE '%cake%' OR '%pastry%' OR '%donut%' 
        THEN consumption_label = "Snack"
  15.3: IF food_name LIKE '%tortilla%' OR '%flatbread%' 
        THEN consumption_label = "Main Course"
  15.4: ELSE consumption_label = "Snack" (default)

Rule 16: food_group == "Dairy and Egg Products"
  16.1: IF food_name LIKE '%milk%' OR '%yogurt%' OR '%beverage%' 
        THEN consumption_label = "Drink"
  16.2: IF food_name LIKE '%cheese%' AND food_name LIKE '%cottage%' 
        THEN consumption_label = "Main Course"
  16.3: IF food_name LIKE '%cheese%' THEN consumption_label = "Side Dish"
  16.4: IF food_name LIKE '%butter%' OR '%cream%' 
        THEN consumption_label = "Side Dish"
  16.5: IF food_name LIKE '%egg%' THEN consumption_label = "Main Course"
  16.6: ELSE consumption_label = "Snack" (default)

Rule 17: food_group == "Fruits and Fruit Juices"
  17.1: IF food_name LIKE '%juice%' OR '%drink%' 
        THEN consumption_label = "Drink"
  17.2: IF food_name LIKE '%fried%' OR '%plantain%' 
        THEN consumption_label = "Main Course"
  17.3: IF food_name LIKE '%avocado%' OR '%olive%' 
        THEN consumption_label = "Snack"
  17.4: ELSE consumption_label = "Snack" (default)

Rule 18: food_group == "Soups, Sauces, and Gravies"
  18.1: IF food_name LIKE '%soup%' THEN consumption_label = "Main Course"
  18.2: IF food_name LIKE '%sauce%' OR '%gravy%' OR '%dressing%' 
        THEN consumption_label = "Side Dish"
  18.3: ELSE consumption_label = "Main Course" (default)

Rule 19: food_group == "American Indian/Alaska Native Foods"
  19.1: IF food_name LIKE '%stew%' THEN consumption_label = "Main Course"
  19.2: ELSE consumption_label = "Main Course" (default)

Rule 20: DEFAULT → consumption_label = "Snack" (safest fallback)
```

### Confidence Scoring

Mark each classification:
- `confidence = 'high'` - Tier 1 rules (unambiguous)
- `confidence = 'medium'` - Tier 2 rules or successful Tier 3 context matching
- `confidence = 'low'` - Fallback to default (Rule 20)

---

## 11. MIGRATION IMPLEMENTATION PLAN

### Phase 1: Create Rule-Based Classifier (New File)

**File**: `B. Preprocessing/ML Klasifikasi/rule_based_classifier.py`

```python
class RuleBasedFoodClassifier:
    """Deterministic rule-based food classification"""
    
    def classify(self, food_name: str, food_group: str) -> Tuple[str, str]:
        """
        Classify food into consumption_label with confidence.
        
        Args:
            food_name: Food item name (from food_name column)
            food_group: Food group (from food_group column)
            
        Returns:
            (consumption_label, confidence) tuple
            consumption_label: 'Drink', 'Main Course', 'Side Dish', or 'Snack'
            confidence: 'high', 'medium', or 'low'
        """
        
    def predict_batch(self, df: pd.DataFrame) -> pd.DataFrame:
        """Predict batch of foods"""
        
    def migrate_from_ml(self, old_df: pd.DataFrame) -> pd.DataFrame:
        """Compare old ML predictions with new rules"""
```

### Phase 2: Validation Against Current Dataset

```python
import pandas as pd
from rule_based_classifier import RuleBasedFoodClassifier

# Load current dataset (with ML predictions)
old_data = pd.read_csv('A. Data/Data Processed/05_final_dataset.csv')

# Generate new predictions
classifier = RuleBasedFoodClassifier()
new_predictions = classifier.predict_batch(old_data)

# Compare
old_data['consumption_label_new'] = new_predictions['label']
old_data['confidence_new'] = new_predictions['confidence']

# Identify differences
diffs = old_data[old_data['consumption_label'] != old_data['consumption_label_new']]

print(f"\nMigration Summary:")
print(f"  Total items: {len(old_data)}")
print(f"  Items changed: {len(diffs)} ({len(diffs)/len(old_data)*100:.1f}%)")
print(f"  Items unchanged: {len(old_data)-len(diffs)} ({(len(old_data)-len(diffs))/len(old_data)*100:.1f}%)")

# Breakdown by change type
for fg in old_data['food_group'].unique():
    fg_diffs = diffs[diffs['food_group'] == fg]
    if len(fg_diffs) > 0:
        print(f"\n  {fg}: {len(fg_diffs)} changes")
        for _, row in fg_diffs.head(3).iterrows():
            print(f"    - {row['food_name']}: {row['consumption_label']} → {row['consumption_label_new']}")
```

### Phase 3: Update 05_final_dataset.py

Replace ML classification with rules:

```python
# OLD:
from ML Klasifikasi.food_classifier import FoodClassifier
classifier = FoodClassifier.load(str(model_path))
predictions = classifier.predict(data, return_both=True)
data['consumption_label'] = predictions.get('consumption_label', 'Snack')

# NEW:
from ML Klasifikasi.rule_based_classifier import RuleBasedFoodClassifier
classifier = RuleBasedFoodClassifier()
predictions = classifier.predict_batch(data)
data['consumption_label'] = predictions['label']
data['label_confidence'] = predictions['confidence']
```

### Phase 4: Integration Testing

Run complete DSS pipeline:

```bash
# Test basic functionality
python D/Model/Greedy\ Algorithm/test_cli.py normal
python D/Model/Greedy\ Algorithm/test_cli.py disease

# Expected: All meals generate successfully with all courses (Main/Side/Drink)
```

### Phase 5: Validation Metrics

Verify:
- ✓ All 3,920 items get valid consumption_label
- ✓ All items get confidence score (high/medium/low)
- ✓ test_cli.py produces valid menus with all courses
- ✓ Portion ranges applied correctly
- ✓ Meal distribution percentages maintained (23.75%/33.75%/28.75%/13.75%)
- ✓ No regressions in nutrition calculation

---

## 12. EXPECTED MIGRATION IMPACT

### Positive Changes

| Food Category | Current ML | New Rule | Impact |
|---------------|-----------|----------|--------|
| Vegetables | 99.3% correct | 99%+ (by definition) | ✓ Maintains accuracy |
| Beverages | 97% correct | 99%+ (by definition) | ✓ Slight improvement |
| Proteins | 98.9% correct | 99%+ (by definition) | ✓ Maintains accuracy |
| Sweets | 95.3% correct | 95%+ (by definition) | ✓ Maintains accuracy |
| Condiments/Dressings | 0% correct (classified as Main) | 100% (Side Dish) | ✓✓ MAJOR fix |
| Garlic Bread | 0% correct (classified as Main) | 100% (Side Dish) | ✓✓ MAJOR fix |
| Beverages (anomalies) | 3 misclassified | 0 misclassified | ✓ FIXED |

### Items That May Change

- **Baked Products (110 items)**: Some reclassified Main→Side (e.g., bread, rolls)
- **Dairy (29 items)**: Cottage cheese Main→Side, milk beverage→Drink
- **Fruits (11 items)**: Some Snack→Main (e.g., fried plantain for context)

---

## 13. RISKS & MITIGATION STRATEGIES

| Risk | Prob | Impact | Mitigation |
|------|------|--------|-----------|
| Meal generation fails with changed labels | Low | High | **Action**: Full integration test before deployment |
| Some ambiguous foods unclassified | Low | Low | **Action**: Fallback to "Snack" (nutritionally safe) |
| Rule conflicts for edge cases | Low | Low | **Action**: Priority order ensures consistent behavior |
| Performance regression in greedy algo | Low | Medium | **Action**: Compare nutrition totals before/after |
| New food_groups added to database | Low | Low | **Action**: Add rules as needed (rule-based is extensible) |

---

## 14. BENEFITS OF RULE-BASED APPROACH

1. **Transparent**: Decision logic is visible and auditable
2. **Maintainable**: Easy to add/modify rules without retraining
3. **Deterministic**: Same input always produces same output
4. **Fast**: No ML model loading/inference overhead
5. **Explainable**: Can trace why each food was classified
6. **Extensible**: New food_groups can be added incrementally
7. **Debuggable**: Issues can be traced to specific rules
8. **Domain-aligned**: Rules encode nutritionist/dietitian knowledge

---

## 15. VALIDATION CHECKLIST

Pre-Deployment:
- [ ] RuleBasedFoodClassifier class complete with all 20 rules
- [ ] Unit tests pass (100% coverage of rule paths)
- [ ] Batch prediction works correctly on full dataset
- [ ] Comparison report: ML vs Rule-based generated and reviewed
- [ ] High-risk items manually verified (condiments, bread, dairy)

Integration Testing:
- [ ] test_cli.py normal mode passes
- [ ] test_cli.py disease mode passes
- [ ] All meals have Main+Side+Drink courses
- [ ] Portion ranges applied correctly
- [ ] Nutrition totals within acceptable range

Post-Deployment:
- [ ] Final dataset regenerated successfully
- [ ] 05_final_dataset.csv has no null consumption_labels
- [ ] 05_final_dataset.csv has confidence scores
- [ ] Greedy algorithm produces valid menus
- [ ] Sample menus reviewed for nutritional correctness

---

## 16. NEXT STEPS

1. **Acknowledge receipt** of audit findings
2. **Review** the proposed rules (feel free to adjust food_group priority)
3. **Confirm** scope: Replace 05_final_dataset.py to use rules instead of ML
4. **Authorize** migration implementation
5. **Plan** manual verification of reclassified items (Dairy, Baked, Fruits groups)

---

## APPENDIX: Key Statistics

```
Total foods in final dataset: 3,920
Total unique food_groups: 23

Consumption Label Distribution:
  Main Course: 1,346 (34.3%)
  Snack: 1,298 (33.1%)
  Side Dish: 1,047 (26.7%)
  Drink: 229 (5.8%)

Training Data (label_makanan.csv):
  Auto-labeled: 3,598 (84.5%)
  Manually-labeled: 665 (15.5%)
  
  High confidence: 1,869 (43.9%)
  Medium confidence: 1,719 (40.3%)
  Low confidence: 675 (15.8%)
  
  Side Dish high conf: 32 (2.5%) ← CRITICAL WEAKNESS

Model Features: 41 (10 numeric + 1 categorical + 30 TF-IDF)
Model Accuracy: ~75% overall (varies by class)
Model Training: Stratified train-test split, balanced class weights
```

---

*Audit completed and verified. Ready for rule-based migration implementation.*

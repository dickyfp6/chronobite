"""
FOOD CONSUMPTION LABEL CLASSIFIER - Core Module
Prediksi consumption_label (Main Course, Side Dish, Drink, Snack)
Digunakan untuk proses data preprocessing di Pemrosesan Data folder
"""

import pandas as pd
import numpy as np
from pathlib import Path
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, f1_score, classification_report
from sklearn.ensemble import RandomForestClassifier
try:
    from xgboost import XGBClassifier  # noqa: F401 #type: ignore[import]
    USE_XGBOOST = True
    print("[INFO] XGBoost available, will use XGBClassifier")
except ImportError:
    USE_XGBOOST = False
    print("[INFO] XGBoost not found, falling back to RandomForestClassifier")
import warnings
warnings.filterwarnings('ignore')


class FoodClassifier:
    """Food consumption and cuisine label classifier"""
    
    def __init__(self):
        # Consumption classification
        self.consumption_model = None
        self.consumption_scaler = None
        self.consumption_label_encoder = None
        
        # Cuisine classification
        self.cuisine_model = None
        self.cuisine_scaler = None
        self.cuisine_label_encoder = None
        
        # Shared components
        self.tfidf = None
        self.encoders = {}  # for categorical features
        
    def train(self, df, verbose=True):
        """Train models with XGBoost, class balancing, and stratified split"""
        
        if verbose:
            print("\n" + "="*70)
            print("TRAINING FOOD CLASSIFIER (XGBoost + Stratified Split)")
            print("="*70)
                
        X = df.copy()
        
        # ===== TRAIN CONSUMPTION MODEL =====
        if 'consumption_label' in X.columns:
            y_consumption_labels = X['consumption_label'].values
            
            # Encode labels
            self.consumption_label_encoder = LabelEncoder()
            y_consumption = self.consumption_label_encoder.fit_transform(y_consumption_labels)
            
            # Extract features
            X_features = self._extract_features(X, fit=True)
            
            # Stratified train/test split (maintain class proportion)
            X_train, X_test, y_train, y_test = train_test_split(
                X_features, y_consumption,
                test_size=0.2,
                random_state=42,
                stratify=y_consumption
            )
            
            # Scale
            self.consumption_scaler = StandardScaler()
            X_train_scaled = self.consumption_scaler.fit_transform(X_train)
            X_test_scaled = self.consumption_scaler.transform(X_test)
            
            # Calculate class weights for balancing
            class_weights = len(y_train) / (len(np.unique(y_train)) * np.bincount(y_train))
            sample_weights = np.array([class_weights[y] for y in y_train])
            
            # Train model with class balancing
            if USE_XGBOOST:
                self.consumption_model = XGBClassifier(
                    n_estimators=200,
                    max_depth=7,
                    learning_rate=0.1,
                    subsample=0.8,
                    colsample_bytree=0.8,
                    random_state=42,
                    n_jobs=-1,
                    verbosity=0
                )
            else:
                self.consumption_model = RandomForestClassifier(
                    n_estimators=200,
                    max_depth=7,
                    class_weight='balanced',
                    random_state=42,
                    n_jobs=-1
                )
            
            self.consumption_model.fit(X_train_scaled, y_train, sample_weight=sample_weights if USE_XGBOOST else None)
            
            # Evaluate
            y_pred = self.consumption_model.predict(X_test_scaled)
            acc = accuracy_score(y_test, y_pred)
            f1_weighted = f1_score(y_test, y_pred, average='weighted')
            f1_macro = f1_score(y_test, y_pred, average='macro')
            
            if verbose:
                print(f"\n[OK] Consumption model trained")
                print(f"  Training samples: {len(X_train)} | Test samples: {len(X_test)}")
                print(f"  Test Accuracy: {acc:.4f}")
                print(f"  F1-score (weighted): {f1_weighted:.4f}")
                print(f"  F1-score (macro): {f1_macro:.4f}")
                print(f"  Labels: {list(self.consumption_label_encoder.classes_)}")
        
        # ===== TRAIN CUISINE MODEL =====
        if 'cuisine_manual' in X.columns or 'cuisine_auto' in X.columns:
            # Use cuisine_manual if available, else cuisine_auto
            if 'cuisine_manual' in X.columns:
                X['cuisine_label'] = X['cuisine_manual'].fillna(X.get('cuisine_auto', 'Generic'))
            else:
                X['cuisine_label'] = X.get('cuisine_auto', 'Generic')
            
            # Remove rows with no cuisine label
            X_cuisine = X.dropna(subset=['cuisine_label']).copy()
            X_cuisine['cuisine_label'] = X_cuisine['cuisine_label'].astype(str).str.strip()
            
            y_cuisine_labels = X_cuisine['cuisine_label'].values
            
            # Encode labels
            self.cuisine_label_encoder = LabelEncoder()
            y_cuisine = self.cuisine_label_encoder.fit_transform(y_cuisine_labels)
            
            # Extract features (reuse fitted tfidf from consumption)
            X_cuisine_features = self._extract_features(X_cuisine, fit=False)
            
            # Stratified split (important for minority classes!)
            X_train, X_test, y_train, y_test = train_test_split(
                X_cuisine_features, y_cuisine,
                test_size=0.2,
                random_state=42,
                stratify=y_cuisine
            )
            
            # Scale
            self.cuisine_scaler = StandardScaler()
            X_train_scaled = self.cuisine_scaler.fit_transform(X_train)
            X_test_scaled = self.cuisine_scaler.transform(X_test)
            
            # Calculate class weights (crucial for imbalanced data like Asian/Mediterranean)
            class_weights = len(y_train) / (len(np.unique(y_train)) * np.bincount(y_train))
            sample_weights = np.array([class_weights[y] for y in y_train])
            
            # Train model with class balancing
            if USE_XGBOOST:
                self.cuisine_model = XGBClassifier(
                    n_estimators=200,
                    max_depth=7,
                    learning_rate=0.1,
                    subsample=0.8,
                    colsample_bytree=0.8,
                    random_state=42,
                    n_jobs=-1,
                    verbosity=0
                )
            else:
                self.cuisine_model = RandomForestClassifier(
                    n_estimators=200,
                    max_depth=7,
                    class_weight='balanced',
                    random_state=42,
                    n_jobs=-1
                )
            
            self.cuisine_model.fit(X_train_scaled, y_train, sample_weight=sample_weights if USE_XGBOOST else None)
            
            # Evaluate
            y_pred = self.cuisine_model.predict(X_test_scaled)
            acc = accuracy_score(y_test, y_pred)
            f1_weighted = f1_score(y_test, y_pred, average='weighted')
            f1_macro = f1_score(y_test, y_pred, average='macro')
            
            if verbose:
                print(f"\n[OK] Cuisine model trained (with IMBALANCE handling)")
                print(f"  Training samples: {len(X_train)} | Test samples: {len(X_test)}")
                print(f"  Test Accuracy: {acc:.4f}")
                print(f"  F1-score (weighted): {f1_weighted:.4f}")
                print(f"  F1-score (macro): {f1_macro:.4f} ◄── Better for minority classes")
                print(f"  Labels: {list(self.cuisine_label_encoder.classes_)}")
                print(f"\n  Class weights applied (to handle imbalance):")
                for label_idx, label_name in enumerate(self.cuisine_label_encoder.classes_):
                    count = (y_train == label_idx).sum()
                    weight = class_weights[label_idx]
                    pct = (count / len(y_train)) * 100
                    print(f"    {label_name:15s}: {count:4d} ({pct:5.1f}%) → weight: {weight:.2f}x")
        
        return self
    
    def _extract_features(self, df, fit=False):
        """Extract numeric, categorical, dan text features"""
        
        # Numeric features - mapped untuk dua format column names
        numeric_mappings = {
            'Calcium, Ca': 'calcium_mg',
            'Carbohydrate, by difference': 'carbohydrate_g',
            'Cholesterol': 'cholesterol_mg',
            'Protein': 'protein_g',
            'Total lipid (fat)': 'fat_g',
            'Energy': 'energy_kcal',
            'Sodium, Na': 'sodium_mg',
            'Sugars, Total': 'sugar_g',
            'Fiber, total dietary': 'fiber_g',
            'Water': 'water_g'
        }
        
        # Extract numeric columns (try both naming conventions)
        numeric_cols = []
        for old_name, new_name in numeric_mappings.items():
            if old_name in df.columns:
                numeric_cols.append(old_name)
            elif new_name in df.columns:
                numeric_cols.append(new_name)
        
        numeric_X = df[numeric_cols].fillna(0).values if numeric_cols else np.zeros((len(df), 0))
        
        # Categorical: food_group
        cat_X = np.zeros((len(df), 1))
        if 'food_group' in df.columns:
            if fit:
                self.encoders['food_group'] = LabelEncoder()
                cat_X = self.encoders['food_group'].fit_transform(
                    df['food_group'].astype(str)
                ).reshape(-1, 1)
            else:
                cat_X = self.encoders['food_group'].transform(
                    df['food_group'].astype(str)
                ).reshape(-1, 1)
        
        # Text features
        text_X = np.zeros((len(df), 1))
        if 'food_name' in df.columns:
            if fit:
                self.tfidf = TfidfVectorizer(max_features=30, stop_words='english')
                text_X = self.tfidf.fit_transform(df['food_name'].astype(str)).toarray()  # type: ignore[attr-defined]
            else:
                if self.tfidf is not None:
                    text_X = self.tfidf.transform(df['food_name'].astype(str)).toarray()  # type: ignore[attr-defined]
        
        # Combine
        return np.hstack([numeric_X, cat_X, text_X])
    
    def _classify_consumption_rule(self, df):
        """
        Deterministic rule-based consumption label classification.
        Replaces ML model with priority-ordered rules derived from dataset patterns.
        
        Rules organized in 3 tiers:
        - Tier 1: Direct mapping (high confidence)
        - Tier 2: Group-level classification (medium confidence)
        - Tier 3: Keyword-based (medium confidence with decision trees)
        """
        
        def contains_keyword(text, keywords):
            """Case-insensitive substring matching"""
            text_lower = str(text).lower()
            return any(kw in text_lower for kw in keywords)
        
        def classify_item(food_name, food_group):
            """Classify single item using rules"""
            
            # ===== TIER 1: DIRECT FOOD_GROUP MAPPING =====
            tier1_direct = {
                'Beverages': 'Drink',
                'Fats and Oils': 'Side Dish',
                'Spices and Herbs': 'Side Dish',
                'Sweets': 'Snack',
            }
            tier1_main_proteins = [
                'Beef Products',
                'Poultry Products',
                'Finfish and Shellfish Products',
                'Lamb, Veal, and Game Products',
                'Sausages and Luncheon Meats'
            ]
            
            food_group_lower = str(food_group).lower()
            
            # Direct mappings
            for group, label in tier1_direct.items():
                if group.lower() in food_group_lower:
                    return (label, 'high')
            
            # Main proteins
            for group in tier1_main_proteins:
                if group.lower() in food_group_lower:
                    return ('Main Course', 'high')
            
            # Vegetables with juice = Drink
            if 'Vegetables and Vegetable Products' in food_group:
                if contains_keyword(food_name, ['juice', 'nectar']):
                    return ('Drink', 'high')
                else:
                    return ('Side Dish', 'high')
            
            # ===== TIER 2: GROUP-LEVEL CLASSIFICATION =====
            tier2_main = [
                'Cereal Grains and Pasta',
                'Fast Foods',
                'Meals, Entrees, and Side Dishes',
                'Restaurant Foods'
            ]
            
            for group in tier2_main:
                if group.lower() in food_group_lower:
                    return ('Main Course', 'medium')
            
            # Breakfast Cereals → Tier approach based on preparation & type
            if 'Breakfast Cereals' in food_group:
                # Tier A: Explicitly prepared/cooked cereals (highest confidence)
                if contains_keyword(food_name, ['prepared with', 'cooked with']):
                    return ('Main Course', 'high')
                
                # Tier B: Specific hot cereal brands (medium-high confidence)
                hot_cereal_keywords = [
                    "grit", "grits",              # Corn grits - always cooked preparation
                    "cream of wheat",              # Cream of Wheat brand - always hot cereal
                    "cream of rice",               # Cream of Rice brand - always hot cereal
                    "farina",                      # Farina - always hot cereal
                    "wheatena",                    # WHEATENA brand - always hot cereal
                ]
                if any(kw in food_name.lower() for kw in hot_cereal_keywords):
                    return ('Main Course', 'medium')
                
                # Tier C: Default ready-to-eat breakfast cereals → Side Dish
                # (Semantic: breakfast items are Main/Side, not Snack)
                return ('Side Dish', 'medium')
            
            # ===== TIER 3: KEYWORD-BASED (Ambiguous Groups) =====
            
            # Fruits and Fruit Juices
            if 'Fruits and Fruit Juices' in food_group:
                if contains_keyword(food_name, ['juice', 'concentrate', 'bottled', 'nectar']):
                    return ('Drink', 'high')
                else:
                    return ('Snack', 'high')
            
            # Dairy and Egg Products (complex multi-branch)
            if 'Dairy and Egg Products' in food_group:
                # Priority 1: Fluid milk products → Drink
                if contains_keyword(food_name, ['fluid', 'milk', 'buttermilk']):
                    return ('Drink', 'high')
                
                # Priority 2: Cheese, butter, cream → Side Dish
                if contains_keyword(food_name, ['cheese', 'butter', 'cream']):
                    return ('Side Dish', 'high')
                
                # Priority 3: Egg, cottage products → Main Course
                if contains_keyword(food_name, ['egg', 'cottage']):
                    return ('Main Course', 'high')
                
                # Priority 4: Yogurt, ice → Snack
                if contains_keyword(food_name, ['yogurt', 'ice cream', 'ice milk']):
                    return ('Snack', 'high')
                
                # Default for dairy
                return ('Snack', 'medium')
            
            # Baked Products (detailed rules)
            if 'Baked Products' in food_group:
                # Snack category: cookies, crackers, cakes, pastries, donuts, waffles
                if contains_keyword(food_name, ['cookie', 'cracker', 'cake', 'waffle', 'donut', 'pastry', 'brownie', 'muffin']):
                    return ('Snack', 'high')
                
                # Main Course: tortillas, flatbread, naan
                if contains_keyword(food_name, ['tortilla', 'flatbread', 'naan', 'pita']):
                    return ('Main Course', 'medium')
                
                # Side Dish: bread (priority over tortilla logic above)
                if contains_keyword(food_name, ['bread']) and not contains_keyword(food_name, ['tortilla']):
                    return ('Side Dish', 'medium')
                
                # Default
                return ('Snack', 'medium')
            
            # Soups, Sauces, and Gravies (decision tree)
            if 'Soups, Sauces, and Gravies' in food_group:
                # Soups → Main Course
                if contains_keyword(food_name, ['soup']):
                    return ('Main Course', 'high')
                
                # Gravy, broth → Side Dish
                if contains_keyword(food_name, ['gravy', 'broth']):
                    return ('Side Dish', 'high')
                
                # Dry/powdered sauces → Snack
                if contains_keyword(food_name, ['sauce']) and contains_keyword(food_name, ['dry', 'mix', 'powder']):
                    return ('Snack', 'medium')
                
                # Regular sauces → Side Dish
                if contains_keyword(food_name, ['sauce']):
                    return ('Side Dish', 'medium')
                
                # Default: Main Course (most conservative)
                return ('Main Course', 'medium')
            
            # Legumes and Legume Products
            if 'Legumes and Legume Products' in food_group:
                # Soymilk → Drink
                if contains_keyword(food_name, ['soymilk']):
                    return ('Drink', 'high')
                
                # Peanut, peanut butter, peanut flour → Snack
                if contains_keyword(food_name, ['peanut']):
                    return ('Snack', 'high')
                
                # Beans, seeds → Main Course
                if contains_keyword(food_name, ['bean', 'seed', 'lentil']):
                    return ('Main Course', 'high')
                
                # Default: Main Course
                return ('Main Course', 'medium')
            
            # Nut and Seed Products → Snack (typically snacking items)
            if 'Nut and Seed Products' in food_group:
                return ('Snack', 'medium')
            
            # Restaurant Foods → Main Course
            if 'Restaurant Foods' in food_group:
                return ('Main Course', 'medium')
            
            # Breakfast Cereals → Main Course
            if 'Breakfast Cereals' in food_group:
                return ('Main Course', 'medium')
            
            # =====DEFAULT FALLBACK =====
            return ('Snack', 'low')
        
        # Apply rule to all items
        results = []
        for _, row in df.iterrows():
            food_name = row.get('food_name', '')
            food_group = row.get('food_group', '')
            label, confidence = classify_item(food_name, food_group)
            results.append(label)
        
        return np.array(results)
    
    def predict(self, df, return_both=False):
        """Predict consumption and/or cuisine labels
        
        Consumption: Uses deterministic rule-based classification (always available)
        Cuisine: Uses ML model (if trained)
        """
        
        results = {}
        
        # Predict consumption using RULES (always available, no ML model needed)
        results['consumption_label'] = self._classify_consumption_rule(df)
        
        # Predict cuisine using ML (unchanged)
        if self.cuisine_model is not None:
            X_features = self._extract_features(df, fit=False)
            assert self.cuisine_scaler is not None, "Scaler should not be None if model is trained"
            assert self.cuisine_label_encoder is not None, "Encoder should not be None if model is trained"
            X_cuisine_scaled = self.cuisine_scaler.transform(X_features)
            y_cuisine_pred = self.cuisine_model.predict(X_cuisine_scaled)
            results['cuisine_label'] = self.cuisine_label_encoder.inverse_transform(y_cuisine_pred)
        
        # Return format
        if return_both or ('consumption_label' in results and 'cuisine_label' in results):
            return results
        elif 'consumption_label' in results:
            return results['consumption_label']
        else:
            return results['cuisine_label']
    
    def evaluate(self, df_test, y_test_consumption=None, y_test_cuisine=None):
        """Evaluate model performance"""
        
        X_features = self._extract_features(df_test, fit=False)
        
        print("\n" + "="*70)
        print("MODEL EVALUATION")
        print("="*70)
        
        if y_test_consumption is not None and self.consumption_model is not None:
            assert self.consumption_scaler is not None, "Scaler should not be None if model is trained"
            X_consumption_scaled = self.consumption_scaler.transform(X_features)
            y_pred = self.consumption_model.predict(X_consumption_scaled)
            accuracy = accuracy_score(y_test_consumption, y_pred)
            print(f"\nConsumption Accuracy: {accuracy:.4f}")
            print("Classification Report:")
            print(classification_report(y_test_consumption, y_pred))
        
        if y_test_cuisine is not None and self.cuisine_model is not None:
            assert self.cuisine_scaler is not None, "Scaler should not be None if model is trained"
            X_cuisine_scaled = self.cuisine_scaler.transform(X_features)
            y_pred = self.cuisine_model.predict(X_cuisine_scaled)
            accuracy = accuracy_score(y_test_cuisine, y_pred)
            print(f"\nCuisine Accuracy: {accuracy:.4f}")
            print("Classification Report:")
            print(classification_report(y_test_cuisine, y_pred))
    
    def save(self, filepath):
        """Save trained models"""
        
        model_data = {
            # Consumption
            'consumption_model': self.consumption_model,
            'consumption_scaler': self.consumption_scaler,
            'consumption_label_encoder': self.consumption_label_encoder,
            # Cuisine
            'cuisine_model': self.cuisine_model,
            'cuisine_scaler': self.cuisine_scaler,
            'cuisine_label_encoder': self.cuisine_label_encoder,
            # Shared
            'tfidf': self.tfidf,
            'encoders': self.encoders
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"[OK] Model saved: {filepath}")
        return filepath
    
    @staticmethod
    def load(filepath):
        """Load trained models"""
        
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        classifier = FoodClassifier()
        classifier.consumption_model = model_data.get('consumption_model')
        classifier.consumption_scaler = model_data.get('consumption_scaler')
        classifier.consumption_label_encoder = model_data.get('consumption_label_encoder')
        classifier.cuisine_model = model_data.get('cuisine_model')
        classifier.cuisine_scaler = model_data.get('cuisine_scaler')
        classifier.cuisine_label_encoder = model_data.get('cuisine_label_encoder')
        classifier.tfidf = model_data.get('tfidf')
        classifier.encoders = model_data.get('encoders', {})
        
        print(f"[OK] Model loaded: {filepath}")
        return classifier


# =====================================================================
# MAIN - Training dari label_makanan.csv + label_cuisine.csv
# =======================================================================

if __name__ == "__main__":
    
    print("\n" + "="*70)
    print("STEP: Train ML Model (Consumption + Cuisine)")
    print("="*70)
    
    # Load seed data
    print("\n[1/3] Loading seed data...")
    label_makanan = pd.read_csv("../../A. Data/Data Raw/label_makanan.csv", sep=';')
    label_cuisine = pd.read_csv("../../A. Data/Data Raw/label_cuisine.csv")
    
    print(f"[OK] Loaded label_makanan: {len(label_makanan)} items")
    print(f"[OK] Loaded label_cuisine: {len(label_cuisine)} items")
    
    # Merge both datasets for training
    print("\n[2/3] Merging datasets...")
    # Merge on common fdc_id
    merged = label_makanan.merge(
        label_cuisine[['fdc_id', 'cuisine_manual', 'cuisine_auto', 'confidence']],
        on='fdc_id',
        how='left'
    )
    print(f"[OK] Merged dataset: {len(merged)} items")
    print(f"  - With cuisine labels: {merged['cuisine_manual'].notna().sum() + merged['cuisine_auto'].notna().sum()}")
    
    # Train classifier
    print("\n[3/3] Training models...")
    classifier = FoodClassifier()
    classifier.train(merged, verbose=True)
    
    # Save model
    model_path = "food_classifier_model.pkl"
    classifier.save(model_path)
    
    print("\n" + "="*70)
    print("[OK] TRAINING COMPLETE")
    print("="*70)
    print(f"Model path: {model_path}")
    print("Ready untuk digunakan di 05_final_dataset.py")

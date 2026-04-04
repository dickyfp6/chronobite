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
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
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
        """Train models from labeled data"""
        
        if verbose:
            print("\n" + "="*70)
            print("TRAINING FOOD CLASSIFIER")
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
            
            # Scale
            self.consumption_scaler = StandardScaler()
            X_consumption_scaled = self.consumption_scaler.fit_transform(X_features)
            
            # Train model
            self.consumption_model = RandomForestClassifier(
                n_estimators=150,
                max_depth=15,
                random_state=42,
                n_jobs=-1
            )
            self.consumption_model.fit(X_consumption_scaled, y_consumption)
            
            if verbose:
                print(f"✓ Consumption model trained on {len(df)} items")
                print(f"  Labels: {list(self.consumption_label_encoder.classes_)}")
        
        # ===== TRAIN CUISINE MODEL =====
        if 'cuisine_manual' in X.columns or 'cuisine_auto' in X.columns:
            # Use cuisine_manual if available, else cuisine_auto
            if 'cuisine_manual' in X.columns:
                cuisine_col = 'cuisine_manual'
                # Fill NaN with auto predictions
                X['cuisine_label'] = X['cuisine_manual'].fillna(X.get('cuisine_auto', 'Generic'))
            else:
                cuisine_col = 'cuisine_auto'
                X['cuisine_label'] = X[cuisine_col]
            
            # Remove rows with no cuisine label
            X_cuisine = X.dropna(subset=['cuisine_label']).copy()
            
            y_cuisine_labels = X_cuisine['cuisine_label'].values
            
            # Encode labels
            self.cuisine_label_encoder = LabelEncoder()
            y_cuisine = self.cuisine_label_encoder.fit_transform(y_cuisine_labels)
            
            # Extract features
            X_cuisine_features = self._extract_features(X_cuisine, fit=False)
            
            # Scale
            self.cuisine_scaler = StandardScaler()
            X_cuisine_scaled = self.cuisine_scaler.fit_transform(X_cuisine_features)
            
            # Train model
            self.cuisine_model = RandomForestClassifier(
                n_estimators=150,
                max_depth=15,
                random_state=42,
                n_jobs=-1
            )
            self.cuisine_model.fit(X_cuisine_scaled, y_cuisine)
            
            if verbose:
                print(f"\n✓ Cuisine model trained on {len(X_cuisine)} items")
                print(f"  Labels: {list(self.cuisine_label_encoder.classes_)}")
        
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
                text_X = self.tfidf.fit_transform(df['food_name'].astype(str)).toarray()
            else:
                text_X = self.tfidf.transform(df['food_name'].astype(str)).toarray()
        
        # Combine
        return np.hstack([numeric_X, cat_X, text_X])
    
    def predict(self, df, return_both=False):
        """Predict consumption and/or cuisine labels"""
        
        if self.consumption_model is None and self.cuisine_model is None:
            raise ValueError("Belum ada model yang di-train")
        
        X_features = self._extract_features(df, fit=False)
        
        results = {}
        
        # Predict consumption
        if self.consumption_model is not None:
            X_consumption_scaled = self.consumption_scaler.transform(X_features)
            y_consumption_pred = self.consumption_model.predict(X_consumption_scaled)
            results['consumption_label'] = self.consumption_label_encoder.inverse_transform(y_consumption_pred)
        
        # Predict cuisine
        if self.cuisine_model is not None:
            X_cuisine_scaled = self.cuisine_scaler.transform(X_features)
            y_cuisine_pred = self.cuisine_model.predict(X_cuisine_scaled)
            results['cuisine_label'] = self.cuisine_label_encoder.inverse_transform(y_cuisine_pred)
        
        # Return format
        if return_both or (self.consumption_model is not None and self.cuisine_model is not None):
            return results
        elif self.consumption_model is not None:
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
            X_consumption_scaled = self.consumption_scaler.transform(X_features)
            y_pred = self.consumption_model.predict(X_consumption_scaled)
            accuracy = accuracy_score(y_test_consumption, y_pred)
            print(f"\nConsumption Accuracy: {accuracy:.4f}")
            print("Classification Report:")
            print(classification_report(y_test_consumption, y_pred))
        
        if y_test_cuisine is not None and self.cuisine_model is not None:
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
        
        print(f"✓ Model saved: {filepath}")
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
        
        print(f"✓ Model loaded: {filepath}")
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
    
    print(f"✓ Loaded label_makanan: {len(label_makanan)} items")
    print(f"✓ Loaded label_cuisine: {len(label_cuisine)} items")
    
    # Merge both datasets for training
    print("\n[2/3] Merging datasets...")
    # Merge on common fdc_id
    merged = label_makanan.merge(
        label_cuisine[['fdc_id', 'cuisine_manual', 'cuisine_auto', 'confidence']],
        on='fdc_id',
        how='left'
    )
    print(f"✓ Merged dataset: {len(merged)} items")
    print(f"  - With cuisine labels: {merged['cuisine_manual'].notna().sum() + merged['cuisine_auto'].notna().sum()}")
    
    # Train classifier
    print("\n[3/3] Training models...")
    classifier = FoodClassifier()
    classifier.train(merged, verbose=True)
    
    # Save model
    model_path = "food_classifier_model.pkl"
    classifier.save(model_path)
    
    print("\n" + "="*70)
    print("✓ TRAINING COMPLETE")
    print("="*70)
    print(f"Model path: {model_path}")
    print("Ready untuk digunakan di 05_final_dataset.py")

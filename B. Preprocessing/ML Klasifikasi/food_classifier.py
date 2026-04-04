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
    """Simple food consumption label classifier"""
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.tfidf = None
        self.encoders = {}
        
    def train(self, df, verbose=True):
        """Train model dari labeled data"""
        
        if verbose:
            print("\n" + "="*70)
            print("TRAINING FOOD CLASSIFIER")
            print("="*70)
        
        # Prepare data
        X = df.copy()
        y_labels = X['consumption_label'].values
        
        # Encode labels
        self.label_encoder = LabelEncoder()
        y = self.label_encoder.fit_transform(y_labels)
        
        # Extract features
        X_features = self._extract_features(X, fit=True)
        
        # Scale
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X_features)
        
        # Train model
        self.model = RandomForestClassifier(
            n_estimators=150,
            max_depth=15,
            random_state=42,
            n_jobs=-1
        )
        self.model.fit(X_scaled, y)
        
        if verbose:
            print(f"✓ Model trained on {len(df)} items")
            print(f"  Labels: {list(self.label_encoder.classes_)}")
        
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
    
    def predict(self, df):
        """Predict consumption labels"""
        
        if self.model is None:
            raise ValueError("Model belum di-train. Gunakan .train() terlebih dahulu")
        
        X_features = self._extract_features(df, fit=False)
        X_scaled = self.scaler.transform(X_features)
        
        y_pred = self.model.predict(X_scaled)
        labels = self.label_encoder.inverse_transform(y_pred)
        
        return labels
    
    def evaluate(self, df_test, y_test_true):
        """Evaluate model performance"""
        
        y_pred = self.model.predict(
            self.scaler.transform(self._extract_features(df_test, fit=False))
        )
        
        accuracy = accuracy_score(y_test_true, y_pred)
        
        print("\n" + "="*70)
        print("MODEL EVALUATION")
        print("="*70)
        print(f"Accuracy: {accuracy:.4f}")
        print("\nClassification Report:")
        print(classification_report(y_test_true, y_pred))
        
        return accuracy
    
    def save(self, filepath):
        """Save trained model"""
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'label_encoder': self.label_encoder,
            'tfidf': self.tfidf,
            'encoders': self.encoders
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"✓ Model saved: {filepath}")
        return filepath
    
    @staticmethod
    def load(filepath):
        """Load trained model"""
        
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        classifier = FoodClassifier()
        classifier.model = model_data['model']
        classifier.scaler = model_data['scaler']
        classifier.label_encoder = model_data['label_encoder']
        classifier.tfidf = model_data['tfidf']
        classifier.encoders = model_data['encoders']
        
        print(f"✓ Model loaded: {filepath}")
        return classifier


# =====================================================================
# MAIN - Training dari label_makanan.csv (Data Raw)
# =======================================================================

if __name__ == "__main__":
    
    # Train model dari seed data (label_makanan.csv dari Data Raw)
    print("\n" + "="*70)
    print("STEP: Train ML Model")
    print("="*70)
    
    # Load seed data
    seed_data = pd.read_csv("../../A. Data/Data Raw/label_makanan.csv", sep=';')
    print(f"✓ Loaded seed data: {len(seed_data)} items")
    
    # Train classifier
    classifier = FoodClassifier()
    classifier.train(seed_data, verbose=True)
    
    # Save model
    model_path = "food_classifier_model.pkl"
    classifier.save(model_path)
    
    print("\n" + "="*70)
    print("✓ TRAINING COMPLETE")
    print("="*70)
    print(f"Model path: {model_path}")
    print("Ready untuk digunakan di 04_apply_ml_labels.py")

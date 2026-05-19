"""
Module untuk load guideline dari CSV
"""

import pandas as pd
import os


class GuidelineLoader:
    """Class untuk load dan manage guideline nutrisi"""
    
    def __init__(self, guideline_path=None, dri_path=None):
        """
        Initialize guideline loader
        
        Args:
            guideline_path: str, path ke file guideline.csv
                           jika None, cari di default location
            dri_path: str, path ke file dri_micro.csv
                     jika None, cari di default location
        """
        if guideline_path is None:
            # Default path relatif ke script ini
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            guideline_path = os.path.join(
                base_dir, 
                "A. Data", 
                "Data Raw", 
                "guideline.csv"
            )
        
        if dri_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            dri_path = os.path.join(
                base_dir,
                "A. Data",
                "Data Raw",
                "dri_micro.csv"
            )
        
        self.guideline_path = guideline_path
        self.dri_path = dri_path
        self.guideline_df = None
        self.dri_df = None
        self.food_df = None
        
        self._load_guideline()
        self._load_dri()
    
    def _load_guideline(self):
        """Load guideline CSV"""
        try:
            self.guideline_df = pd.read_csv(self.guideline_path)
            print(f"[OK] Guideline loaded: {self.guideline_path}")
        except FileNotFoundError:
            raise FileNotFoundError(f"Guideline file not found: {self.guideline_path}")
        except Exception as e:
            raise Exception(f"Error loading guideline: {e}")
    
    def _load_dri(self):
        """Load DRI micronutrient CSV untuk fallback"""
        try:
            self.dri_df = pd.read_csv(self.dri_path)
            print(f"[OK] DRI Micronutrient loaded: {self.dri_path}")
        except FileNotFoundError:
            print(f"[WARN] DRI file not found: {self.dri_path}")
            self.dri_df = None
        except Exception as e:
            print(f"[WARN] Error loading DRI: {e}")
            self.dri_df = None
    
    def get_dri_by_age_gender(self, age, gender):
        """
        Get DRI micronutrient untuk age & gender tertentu
        
        Args:
            age: int (usia user)
            gender: str ('M' untuk Males, 'F' untuk Females)
        
        Returns:
            pd.Series atau None
        """
        if self.dri_df is None:
            return None
        
        gender_text = 'Males' if gender == 'M' else 'Females'
        
        # Find matching DRI row
        filtered = self.dri_df[
            (self.dri_df['age_min'] <= age) &
            (self.dri_df['age_max'] >= age) &
            (self.dri_df['gender'] == gender_text)
        ]
        
        if filtered.empty:
            return None
        
        return filtered.iloc[0]
    
    def get_guideline_by_disease(self, disease, age, gender='all'):
        """
        Get guideline untuk disease tertentu dengan filter age & gender
        
        Args:
            disease: str (normal, dm2, hypertension, cvd, cholesterol, ckd)
            age: int (usia user)
            gender: str ('M', 'F', 'all')
        
        Returns:
            pd.DataFrame: Filtered guideline
        """
        if self.guideline_df is None:
            raise Exception("Guideline not loaded")
        
        # Filter by disease
        filtered = self.guideline_df[self.guideline_df['disease'] == disease].copy()
        
        # Filter by age range
        filtered = filtered[
            (filtered['age_min'] <= age) & 
            (filtered['age_max'] >= age)
        ]
        
        # Filter by gender
        if gender != 'all':
            filtered = filtered[
                (filtered['gender'] == gender) | 
                (filtered['gender'] == 'all')
            ]
        else:
            filtered = filtered[filtered['gender'] == 'all']
        
        return filtered
    
    def merge_disease_guidelines(self, diseases, age, gender='all'):
        """
        Merge multiple disease guidelines dengan logic:
        - min value: MAXIMUM dari semua disease (most restrictive minimum)
        - max value: MINIMUM dari semua disease (most restrictive maximum)
        
        Contoh:
            DM2 energy: 1800-2200
            Hypertension energy: 1995-2205
            → Merged: 1995-2200 (max dari 1800 vs 1995, min dari 2200 vs 2205)
        
        Args:
            diseases: list of str (e.g., ['dm2', 'hypertension'])
            age: int (usia user)
            gender: str ('M', 'F', 'all')
        
        Returns:
            dict: merged nutrients
        """
        if not diseases:
            raise ValueError("diseases list cannot be empty")
        
        all_nutrients = {}
        
        for disease in diseases:
            guideline_df = self.get_guideline_by_disease(disease, age, gender)
            
            if guideline_df.empty:
                continue
            
            for idx, row in guideline_df.iterrows():
                nutrient = row['nutrient']
                min_val = row['min']
                max_val = row['max']
                basis = row['basis']
                tipe = row.get('tipe', 'range')  # Extract tipe column (range or max)
                
                try:
                    min_val = float(min_val) if pd.notna(min_val) else None
                    max_val = float(max_val) if pd.notna(max_val) else None
                except (ValueError, TypeError):
                    min_val = None
                    max_val = None
                
                if nutrient not in all_nutrients:
                    all_nutrients[nutrient] = {
                        'min': min_val,
                        'max': max_val,
                        'basis': basis,
                        'tipe': tipe,  # Store tipe column
                        'diseases': [disease]
                    }
                else:
                    # Min: Take MAXIMUM value (most restrictive minimum)
                    if min_val is not None:
                        if all_nutrients[nutrient]['min'] is None:
                            all_nutrients[nutrient]['min'] = min_val
                        else:
                            all_nutrients[nutrient]['min'] = max(
                                all_nutrients[nutrient]['min'], 
                                min_val
                            )
                    
                    # Max: Take MINIMUM value (most restrictive maximum)
                    if max_val is not None:
                        if all_nutrients[nutrient]['max'] is None:
                            all_nutrients[nutrient]['max'] = max_val
                        else:
                            all_nutrients[nutrient]['max'] = min(
                                all_nutrients[nutrient]['max'], 
                                max_val
                            )
                    
                    all_nutrients[nutrient]['diseases'].append(disease)
        
        return all_nutrients
    
    def load_food_data(self, food_path=None):
        """
        Load data makanan (untuk nanti dipakai GA)
        
        Args:
            food_path: str, path ke file food data
                      jika None, cari di default location
        """
        if food_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            food_path = os.path.join(
                base_dir,
                "A. Data",
                "Data Processed",
                "05_final_dataset.csv"
            )
        
        try:
            self.food_df = pd.read_csv(food_path)

            # Normalize cuisine column name for downstream modules.
            if 'cuisine' not in self.food_df.columns and 'cuisine_label' in self.food_df.columns:
                self.food_df['cuisine'] = self.food_df['cuisine_label']

            print(f"[OK] Food data loaded: {food_path}")
        except FileNotFoundError:
            print(f"[WARN] Food data not found: {food_path}")
        except Exception as e:
            print(f"[WARN] Error loading food data: {e}")
    
    def get_food_by_cuisine(self, cuisine):
        """
        Get food items dari cuisine tertentu
        
        Args:
            cuisine: str (Western, Asian, Other)
        
        Returns:
            pd.DataFrame: Food items dari cuisine tersebut
        """
        if self.food_df is None:
            return None
        
        return self.food_df[self.food_df['cuisine'] == cuisine].copy()


# Singleton instance untuk dipakai di modul lain
_loader_instance = None


def get_guideline_loader(guideline_path=None):
    """Get atau create loader instance (singleton pattern)"""
    global _loader_instance
    if _loader_instance is None:
        _loader_instance = GuidelineLoader(guideline_path)
    return _loader_instance

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
    
    def merge_disease_guidelines(self, diseases, age, gender='all', user_params=None):
        """
        Merge multiple disease guidelines dengan logic:
        - min value: MAXIMUM dari semua disease (most restrictive minimum)
        - max value: MINIMUM dari semua disease (most restrictive maximum)
        
        BUG FIX: Konversi nilai ke unit aktual SEBELUM merge untuk handle basis berbeda
        (basis '1', 'TDEE', 'BB', 'BBI' tidak boleh di-merge secara raw)
        
        Contoh:
            Hypertension energy (basis '1'): 1995-2205 kcal
            CVD energy (basis 'TDEE' 0.95x): 0.95 * 2257 = 2144 kcal
            → Merged: max(1995, 2144) = 2144 kcal (BENAR)
            Bukan: max(1995, 0.95) = 1995 lalu * 2257 = 4,502,715 (SALAH)
        
        Args:
            diseases: list of str (e.g., ['dm2', 'hypertension'])
            age: int (usia user)
            gender: str ('M', 'F', 'all')
            user_params: dict dengan keys {tdee, weight, bbi} untuk konversi basis
        
        Returns:
            dict: merged nutrients (nilai sudah dalam unit aktual)
        """
        from modules.calculations import NutritionCalculator
        calculator = NutritionCalculator()
        
        if user_params is None:
            user_params = {'tdee': 2000, 'weight': 70, 'bbi': 60}
        
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
                
                # Konversi ke unit aktual DULU sebelum merge
                converted = calculator.convert_guideline_value(
                    min_val, max_val, basis, user_params, nutrient_name=nutrient
                )
                
                # Skip jika konversi invalid
                if converted['constraint_type'] in ('invalid', 'unknown'):
                    continue
                
                min_converted = float(converted['min_converted']) if converted['min_converted'] is not None else None
                max_converted = float(converted['max_converted']) if converted['max_converted'] is not None else None
                
                # Merge nilai yang SUDAH dalam unit aktual
                if nutrient not in all_nutrients:
                    all_nutrients[nutrient] = {
                        'min': min_converted,
                        'max': max_converted,
                        'basis': '1',           # sudah dikonversi, basis efektif = absolut
                        'tipe': tipe,
                        'diseases': [disease]
                    }
                else:
                    # Merge nilai yang SUDAH dalam unit aktual (aman dibandingkan langsung)
                    if min_converted is not None and min_converted > 0:
                        all_nutrients[nutrient]['min'] = max(
                            all_nutrients[nutrient]['min'] or 0,
                            min_converted
                        )
                    if max_converted is not None and max_converted < float('inf'):
                        all_nutrients[nutrient]['max'] = min(
                            all_nutrients[nutrient]['max'] or float('inf'),
                            max_converted
                        )
                    all_nutrients[nutrient]['diseases'].append(disease)
        
        # ════════════════════════════════════════════════════════════════════════
        # CONFLICT RESOLUTION: Detect & fix min > max situations after merge
        # ════════════════════════════════════════════════════════════════════════
        
        for nutrient, data in all_nutrients.items():
            merged_min = data['min']
            merged_max = data['max']
            
            # Check if conflict: merged min >= merged max (or gap is zero/negative)
            if merged_min is not None and merged_max is not None and merged_min >= merged_max:
                midpoint = (merged_min + merged_max) / 2.0
                
                # Apply 5% tolerance window for breathing room (min 5.0 units or 50 kcal for energy)
                base_tolerance = 50.0 if 'energy' in nutrient.lower() else 5.0
                tolerance = max(midpoint * 0.05, base_tolerance)
                
                resolved_min = round(midpoint - tolerance, 1)
                resolved_max = round(midpoint + tolerance, 1)
                resolved_min = max(0.0, resolved_min)
                
                print(f"[WARN] Conflict/Tight Constraint on '{nutrient}': min {merged_min:.1f} >= max {merged_max:.1f}. "
                      f"Applying 5% tolerance compromise: {resolved_min:.1f} – {resolved_max:.1f}")
                
                data['min'] = resolved_min
                data['max'] = resolved_max
        
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
                "07_super_final.csv"
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

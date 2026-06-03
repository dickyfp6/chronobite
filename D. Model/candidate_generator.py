"""
Candidate Generator - Generate 3 kandidat makanan per slot dengan similarity check
Menggunakan regex-based similarity dari food_name untuk menghindari duplikasi jenis makanan
"""

import pandas as pd
import re
from typing import List, Dict, Set, Optional, cast
from meal_schema import FoodItem


class CandidateGenerator:
    """
    Generate kandidat makanan untuk slot meal dengan similarity check
    
    Mekanisme:
    1. Filter food items berdasarkan category slot (Main, Side, Drink)
    2. Ambil N top candidates berdasarkan kalori target
    3. Exclude items yang sudah ada di exclusion list (similarity check via regex food_name)
    4. Return top 3 kandidat yang paling cocok
    """
    
    @staticmethod
    def extract_main_ingredients(food_name: str) -> Optional[str]:
        """
        Extract main ingredient term(s) dari food_name untuk ingredient diversity check.
        Bukan hanya protein, tapi semua jenis ingredient: daging, sayur, karbo, dll.
        
        Contoh: 
        - "Chicken Breast Grilled" -> "chicken"
        - "Spinach Salad" -> "spinach"
        - "Grilled Salmon" -> "salmon"
        - "Nasi Kuning" -> "nasi"
        
        Args:
            food_name: Nama makanan dari dataset
        
        Returns:
            Main ingredient keyword (lowercase), atau None
        """
        # Remove commas and split
        food_name_clean = food_name.replace(',', ' ')
        words = food_name_clean.lower().split()
        
        # Skip common cooking descriptors
        skip_words = {
            'cooked', 'raw', 'fried', 'boiled', 'grilled', 'baked', 'steamed',
            'fresh', 'frozen', 'ready-to-eat', 'ready', 'toasted', 'microwaved',
            'commercially', 'prepared', 'toasted', 'roasted', 'sauteed', 'sautéed',
            'sliced', 'diced', 'chopped', 'made', 'with', 'and', 'or', 'the',
            'from', 'in', 'as', 'added', 'shelf', 'stable'
        }
        
        # Ambil word pertama yang meaningful (bukan descriptor)
        for word in words:
            # Skip short words dan descriptor
            if word not in skip_words and len(word) > 2 and not word.isdigit():
                return word
        
        # Fallback: return first word if exists
        return words[0] if words else None
    

    
    @staticmethod
    def is_similar_ingredient(food_name1: str, food_name2: str) -> bool:
        """
        Check apakah dua makanan memiliki main ingredient yang sama.
        Digunakan untuk ingredient diversity check - hindari duplikasi ingredient di meal time berbeda.
        
        Contoh similar:
        - "Chicken Breast" vs "Grilled Chicken" -> True (same ingredient: chicken)
        - "Spinach Salad" vs "Cooked Spinach" -> True (same ingredient: spinach)
        - "Salmon Fillet" vs "Grilled Chicken" -> False (different ingredient)
        
        Args:
            food_name1: Nama makanan pertama
            food_name2: Nama makanan kedua
        
        Returns:
            True jika memiliki main ingredient yang sama, False jika berbeda
        """
        ingredient1 = CandidateGenerator.extract_main_ingredients(food_name1)
        ingredient2 = CandidateGenerator.extract_main_ingredients(food_name2)
        
        if ingredient1 is None or ingredient2 is None:
            return False
        
        return ingredient1 == ingredient2
    
    @staticmethod
    def filter_by_calorie_range(candidates_df: pd.DataFrame, target_calories: float, tolerance: float = 0.2) -> pd.DataFrame:
        """
        Filter candidates yang kalorinya masuk dalam range target
        
        Args:
            candidates_df: DataFrame candidates
            target_calories: Target calorie untuk slot
            tolerance: Range tolerance % (default 20%)
        
        Returns:
            Filtered DataFrame
        """
        min_cal = target_calories * (1 - tolerance)
        max_cal = target_calories * (1 + tolerance)
        
        filtered = candidates_df[
            (candidates_df['energy_kcal'] >= min_cal) &
            (candidates_df['energy_kcal'] <= max_cal)
        ].copy()
        return cast(pd.DataFrame, filtered)
    
    @staticmethod
    def generate_candidates(
        candidates_df: pd.DataFrame,
        target_calories: float,
        num_candidates: int = 3,
        exclusion_list: Optional[List[str]] = None,
        ingredient_diversity: bool = True,
        tolerance: float = 0.3
    ) -> List[Dict]:
        """
        Generate N kandidat terbaik dari pool dengan ingredient diversity check.
        Hindari suggestion makanan dengan main ingredient yang sama dengan exclusion_list.
        
        Args:
            candidates_df: DataFrame dengan food items (harus punya kategori, kalori, nama)
            target_calories: Target calorie untuk slot
            num_candidates: Jumlah kandidat yang diinginkan (default 3)
            exclusion_list: List nama makanan yang sudah dipilih (untuk menghindari duplikat ingredient)
            ingredient_diversity: Apakah melakukan ingredient diversity check (default True)
        
        Returns:
            List of Dict candidates (max num_candidates)
        """
        
        if exclusion_list is None:
            exclusion_list = []
        
        candidates_df = candidates_df.copy()
        
        # Step 1: Filter by calorie range
        filtered = CandidateGenerator.filter_by_calorie_range(candidates_df, target_calories, tolerance=tolerance)
        
        if len(filtered) == 0:
            # Fallback: jika tidak ada yang cocok range, ambil terdekat
            filtered = candidates_df.copy()
            filtered['calorie_distance'] = abs(filtered['energy_kcal'] - target_calories)
            filtered = filtered.nsmallest(num_candidates + len(exclusion_list), 'calorie_distance')
        
        # Step 2: Remove exclusions based on ingredient similarity
        if ingredient_diversity and len(exclusion_list) > 0:
            result_candidates = []
            
            for idx, row in filtered.iterrows():
                food_name = str(row['food_name'])
                is_excluded = False
                
                # Check ingredient similarity dengan setiap item di exclusion list
                for excluded_name in exclusion_list:
                    # Check 1: exact name match (case-insensitive)
                    if food_name.lower() == excluded_name.lower():
                        is_excluded = True
                        break
                    # Check 2: ingredient similarity (existing logic)
                    if CandidateGenerator.is_similar_ingredient(food_name, excluded_name):
                        is_excluded = True
                        break
                
                if not is_excluded:
                    result_candidates.append(row)
                    if len(result_candidates) >= num_candidates:
                        break
            
            result = pd.DataFrame(result_candidates) if result_candidates else pd.DataFrame()
        else:
            # Tanpa exclusion, ambil top num_candidates
            result = filtered.head(num_candidates)
        
        # Step 3: Convert ke list of dict
        if len(result) == 0:
            return []
        
        candidates_list = []
        for idx, row in result.iterrows():
            candidate = row.to_dict()
            candidate['fdc_id'] = str(row['fdc_id'])
            candidate['food_name'] = str(row['food_name'])
            candidate['food_group'] = str(row['food_group'])
            candidate['consumption_label'] = str(row.get('consumption_label', row.get('menu_category', 'Unknown')))
            candidate['cuisine_label'] = str(row.get('cuisine_label', 'Unknown'))
            candidate['energy_kcal'] = float(row['energy_kcal'])
            candidate['protein_g'] = float(row.get('protein_g', 0))
            candidate['carbohydrate_g'] = float(row.get('carbohydrate_g', 0))
            candidate['fat_g'] = float(row.get('fat_g', 0))
            candidates_list.append(candidate)
        
        return candidates_list
    
    @staticmethod
    def generate_candidates_for_slot(
        food_database: pd.DataFrame,
        slot_category: str,
        target_calories: float,
        num_candidates: int = 3,
        exclusion_names: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Generate candidates untuk 1 slot menggunakan consumption_label dari dataset.
        
        slot_category mapping:
            'Main'  → consumption_label == 'Main Course'
            'Side'  → consumption_label == 'Side Dish'
            'Drink' → consumption_label == 'Drink'
            'Snack' → consumption_label == 'Snack'
        """
        
        SLOT_TO_LABEL = {
            'Main':  'Main Course',
            'Side':  'Side Dish',
            'Drink': 'Drink',
            'Snack': 'Snack',
        }

        # TAMBAHKAN INI SEMENTARA:
        print(f"[DEBUG] slot_category={slot_category}, label={SLOT_TO_LABEL.get(slot_category)}, candidates_df size will be filtered from consumption_label")
        
        label = SLOT_TO_LABEL.get(slot_category)
        if label is None:
            print(f"[WARN] Unknown slot_category: {slot_category}")
            return []
        
        if 'consumption_label' not in food_database.columns:
            print(f"[ERROR] consumption_label column not found")
            return []
        
        candidates_df = pd.DataFrame(
            food_database[food_database['consumption_label'] == label].copy()
        )
        
        if len(candidates_df) == 0:
            print(f"[WARN] No candidates found for {slot_category} ({label})")
            return []
        
        tol = 0.5 if slot_category == 'Drink' else 0.3
        
        return CandidateGenerator.generate_candidates(
            candidates_df=candidates_df,
            target_calories=target_calories,
            num_candidates=num_candidates,
            exclusion_list=exclusion_names,
            ingredient_diversity=True,
            tolerance=tol
        )

# Test
if __name__ == "__main__":
    # Test ingredient similarity
    test_cases = [
        ("Chicken Breast", "Grilled Chicken"),  # Same ingredient
        ("Spinach Salad", "Cooked Spinach"),    # Same ingredient
        ("Salmon Fillet", "Baked Salmon"),      # Same ingredient
        ("Salmon Fillet", "Grilled Chicken"),   # Different ingredient
        ("Sawi Rebus", "Sawi Goreng"),          # Same ingredient
        ("Nasi Kuning", "Nasi Goreng"),         # Same ingredient
    ]
    
    for name1, name2 in test_cases:
        similar = CandidateGenerator.is_similar_ingredient(name1, name2)
        print(f"{name1:30} ~ {name2:30} : {similar}")

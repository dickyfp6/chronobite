"""
Candidate Generator - Generate 3 kandidat makanan per slot dengan similarity check
Menggunakan regex-based similarity dari food_name untuk menghindari duplikasi jenis makanan
"""

import pandas as pd
import re
from typing import List, Dict, Set, Optional
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
    def extract_protein_source(food_name: str) -> Optional[str]:
        """
        Extract protein source dari food_name menggunakan regex
        Contoh: "Chicken Breast" -> "chicken", "Salmon Fillet" -> "salmon"
        
        Args:
            food_name: Nama makanan dari dataset
        
        Returns:
            Keyword protein source (lowercase), atau None
        """
        # Protein keywords untuk matching
        protein_keywords = [
            'chicken', 'beef', 'pork', 'lamb', 'turkey', 'duck',  # Daging
            'salmon', 'tuna', 'cod', 'tilapia', 'mackerel', 'anchovy', 'shrimp', 'crab', 'fish',  # Ikan
            'egg', 'tofu', 'tempeh', 'soya', 'soybean',  # Plant-based protein
            'milk', 'cheese', 'yogurt', 'dairy',  # Dairy
            'bean', 'lentil', 'legume',  # Legumes
        ]
        
        food_name_lower = food_name.lower()
        
        for keyword in protein_keywords:
            if re.search(r'\b' + keyword + r'\b', food_name_lower):
                return keyword
        
        return None
    
    @staticmethod
    def extract_main_ingredient(food_name: str) -> Optional[str]:
        """
        Extract main ingredient term (first few words, tidak termasuk adjektive)
        
        Args:
            food_name: Nama makanan
        
        Returns:
            Main ingredient keyword
        """
        # Tokenize
        words = food_name.lower().split()
        
        # Skip common descriptors
        skip_words = ['cooked', 'raw', 'fried', 'boiled', 'grilled', 'baked', 'steamed', 'fresh', 'frozen', 'ready-to-eat']
        
        for word in words:
            if word not in skip_words and len(word) > 2:
                return word
        
        return None if len(words) == 0 else words[0]
    
    @staticmethod
    def is_similar(food_name1: str, food_name2: str, similarity_type: str = 'protein') -> bool:
        """
        Check apakah dua makanan similar berdasarkan similarity_type
        
        Args:
            food_name1: Nama makanan pertama
            food_name2: Nama makanan kedua
            similarity_type: 'protein' (default) atau 'ingredient'
        
        Returns:
            True jika similar, False jika berbeda
        """
        if similarity_type == 'protein':
            protein1 = CandidateGenerator.extract_protein_source(food_name1)
            protein2 = CandidateGenerator.extract_protein_source(food_name2)
            
            if protein1 is None or protein2 is None:
                return False
            
            return protein1 == protein2
        
        elif similarity_type == 'ingredient':
            ingredient1 = CandidateGenerator.extract_main_ingredient(food_name1)
            ingredient2 = CandidateGenerator.extract_main_ingredient(food_name2)
            
            if ingredient1 is None or ingredient2 is None:
                return False
            
            return ingredient1 == ingredient2
        
        return False
    
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
        
        return candidates_df[
            (candidates_df['energy_kcal'] >= min_cal) &
            (candidates_df['energy_kcal'] <= max_cal)
        ].copy()
    
    @staticmethod
    def generate_candidates(
        candidates_df: pd.DataFrame,
        target_calories: float,
        num_candidates: int = 3,
        exclusion_list: List[str] = None,
        similarity_check: bool = True,
        similarity_type: str = 'protein'
    ) -> List[Dict]:
        """
        Generate N kandidat terbaik dari pool dengan similarity check
        
        Args:
            candidates_df: DataFrame dengan food items (harus punya kategori, kalori, nama)
            target_calories: Target calorie untuk slot
            num_candidates: Jumlah kandidat yang diinginkan (default 3)
            exclusion_list: List nama makanan yang sudah dipilih (untuk menghindari duplikat)
            similarity_check: Apakah melakukan similarity check (default True)
            similarity_type: Tipe similarity ('protein' atau 'ingredient')
        
        Returns:
            List of Dict candidates (max num_candidates)
        """
        
        if exclusion_list is None:
            exclusion_list = []
        
        candidates_df = candidates_df.copy()
        
        # Step 1: Filter by calorie range
        filtered = CandidateGenerator.filter_by_calorie_range(candidates_df, target_calories, tolerance=0.3)
        
        if len(filtered) == 0:
            # Fallback: jika tidak ada yang cocok range, ambil terdekat
            filtered = candidates_df.copy()
            filtered['calorie_distance'] = abs(filtered['energy_kcal'] - target_calories)
            filtered = filtered.nsmallest(num_candidates + len(exclusion_list), 'calorie_distance')
        
        # Step 2: Remove exclusions (similarity check)
        if similarity_check and len(exclusion_list) > 0:
            result_candidates = []
            
            for idx, row in filtered.iterrows():
                food_name = str(row['food_name'])
                is_excluded = False
                
                # Check similarity dengan setiap item di exclusion list
                for excluded_name in exclusion_list:
                    if CandidateGenerator.is_similar(food_name, excluded_name, similarity_type):
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
            candidate = {
                'fdc_id': str(row['fdc_id']),
                'food_name': str(row['food_name']),
                'food_group': str(row['food_group']),
                'consumption_label': str(row.get('consumption_label', row.get('menu_category', 'Unknown'))),
                'cuisine_label': str(row.get('cuisine_label', 'Unknown')),
                'energy_kcal': float(row['energy_kcal']),
                'protein_g': float(row.get('protein_g', 0)),
                'carbohydrate_g': float(row.get('carbohydrate_g', 0)),
                'fat_g': float(row.get('fat_g', 0)),
            }
            candidates_list.append(candidate)
        
        return candidates_list
    
    @staticmethod
    def generate_candidates_for_slot(
        food_database: pd.DataFrame,
        slot_category: str,  # 'Main', 'Side', 'Drink'
        target_calories: float,
        num_candidates: int = 3,
        exclusion_names: List[str] = None
    ) -> List[Dict]:
        """
        Convenience method: Generate candidates untuk 1 slot (sudah filter kategori)
        
        Args:
            food_database: Full food database dari NutritionService
            slot_category: 'Main', 'Side', atau 'Drink'
            target_calories: Target calorie untuk slot
            num_candidates: Jumlah kandidat (default 3)
            exclusion_names: List nama makanan yang exclude (untuk refresh)
        
        Returns:
            List of Dict candidates
        """
        from food_categorizer import FoodCategorizer
        
        # Filter by category
        if 'menu_category' not in food_database.columns:
            food_database = FoodCategorizer.categorize_dataframe(food_database)
        
        candidates_df = FoodCategorizer.filter_by_category(food_database, slot_category)
        
        if len(candidates_df) == 0:
            return []
        
        # Generate candidates
        return CandidateGenerator.generate_candidates(
            candidates_df=candidates_df,
            target_calories=target_calories,
            num_candidates=num_candidates,
            exclusion_list=exclusion_names,
            similarity_check=True,
            similarity_type='protein'
        )


# Test
if __name__ == "__main__":
    # Test similarity
    names = [
        "Chicken Breast",
        "Grilled Chicken",
        "Salmon Fillet",
        "Baked Salmon",
        "Tofu Scramble"
    ]
    
    for i in range(len(names)):
        for j in range(i+1, len(names)):
            similar = CandidateGenerator.is_similar(names[i], names[j], 'protein')
            print(f"{names[i]} ~ {names[j]}: {similar}")

"""
================================================================================
greedy_06_similarity_checker.py - Pemeriksa Kemiripan Menu (Similarity Checker)
================================================================================
File ini memproses:
1. Mendeteksi adanya item makanan yang serupa/duplikat baik di dalam slot waktu makan yang sama (kandidat alternatif) maupun antar waktu makan yang berbeda.
2. Mengekstrak jenis sumber protein utama (seperti ayam, sapi, ikan, telur, tahu, tempe) dan bahan makanan utama dari nama makanan menggunakan pencocokan teks berbasis kata kunci.
3. Menghitung nilai keberagaman menu harian (Diversity Score) dari 0 s.d. 100 dan memberikan rekomendasi perbaikan variasi menu.
================================================================================
"""

import sys
import os
import re
from typing import List, Dict, Set, Tuple, Optional

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from meal_schema import FoodItem, MenuPlan, Meal, SnackMeal


class SimilarityChecker:
    """
    Check similarity/duplicates dalam MenuPlan output
    
    Mekanisme:
    1. Extract protein source, main ingredient dari food_name
    2. Compare items across semua slots (Breakfast Main vs Lunch Main vs Dinner Main, dll)
    3. Generate similarity report (duplikat, similar items, diversity score)
    """
    
    @staticmethod
    def extract_protein_source(food_name: str) -> Optional[str]:
        """
        Extract protein jenis dari food_name
        
        Args:
            food_name: Nama makanan
        
        Returns:
            Protein keyword atau None
        """
        protein_keywords = {
            'poultry': ['chicken', 'duck', 'turkey', 'goose'],
            'beef': ['beef', 'cow'],
            'pork': ['pork'],
            'lamb': ['lamb', 'mutton'],
            'fish': ['salmon', 'tuna', 'cod', 'tilapia', 'mackerel', 'anchovy', 'snapper', 'bass', 'herring', 'fish'],
            'shrimp': ['shrimp', 'prawn', 'lobster', 'crab'],
            'egg': ['egg'],
            'tofu': ['tofu', 'soya', 'soybean'],
            'tempeh': ['tempeh'],
            'milk': ['milk', 'cheese', 'yogurt', 'dairy'],
            'bean': ['bean', 'lentil', 'pea'],
        }
        
        food_name_lower = food_name.lower()
        
        for category, keywords in protein_keywords.items():
            for keyword in keywords:
                if re.search(r'\b' + keyword + r'\b', food_name_lower):
                    return category
        
        return None
    
    @staticmethod
    def extract_main_ingredient(food_name: str) -> Optional[str]:
        """
        Extract main ingredient (key distinguishing term)
        
        Args:
            food_name: Nama makanan
        
        Returns:
            Main ingredient keyword
        """
        # Remove common words
        exclude_words = ['cooked', 'raw', 'fried', 'boiled', 'grilled', 'baked', 'steamed', 'fresh', 
                        'frozen', 'ready-to-eat', 'with', 'and', 'the', 'a', 'an']
        
        words = food_name.lower().split()
        for word in words:
            cleaned = re.sub(r'[^\w]', '', word)
            if cleaned not in exclude_words and len(cleaned) > 2:
                return cleaned
        
        return None
    
    @staticmethod
    def calculate_similarity_score(food_name1: str, food_name2: str) -> float:
        """
        Calculate similarity score antara 2 items (0-1)
        
        Args:
            food_name1: Nama makanan 1
            food_name2: Nama makanan 2
        
        Returns:
            Similarity score (0 = berbeda banget, 1 = identical)
        """
        if food_name1 == food_name2:
            return 1.0
        
        # Levenshtein-like similarity
        food_lower1 = food_name1.lower()
        food_lower2 = food_name2.lower()
        
        if food_lower1 == food_lower2:
            return 1.0
        
        # Protein source similarity
        protein1 = SimilarityChecker.extract_protein_source(food_name1)
        protein2 = SimilarityChecker.extract_protein_source(food_name2)
        
        if protein1 and protein2 and protein1 == protein2:
            return 0.8  # Sama jenis protein
        
        # Main ingredient similarity
        ing1 = SimilarityChecker.extract_main_ingredient(food_name1)
        ing2 = SimilarityChecker.extract_main_ingredient(food_name2)
        
        if ing1 and ing2:
            if ing1 == ing2:
                return 0.7  # Sama main ingredient
            
            # String substring check
            if ing1 in ing2 or ing2 in ing1:
                return 0.5
        
        return 0.0  # Berbeda
    
    @staticmethod
    def find_duplicates(food_items: List[str]) -> List[Tuple[str, str, float]]:
        """
        Find semua pasangan items yang similar dalam list
        
        Args:
            food_items: List of food names
        
        Returns:
            List of tuples (name1, name2, similarity_score)
        """
        duplicates = []
        
        for i in range(len(food_items)):
            for j in range(i + 1, len(food_items)):
                score = SimilarityChecker.calculate_similarity_score(food_items[i], food_items[j])
                if score >= 0.5:  # Threshold: similarity >= 50%
                    duplicates.append((food_items[i], food_items[j], score))
        
        return sorted(duplicates, key=lambda x: x[2], reverse=True)
    
    @staticmethod
    def extract_all_food_names(menu_plan: MenuPlan) -> Dict[str, List[str]]:
        """
        Extract semua food names dari MenuPlan terstruktur per kategori slot
        
        Args:
            menu_plan: MenuPlan object
        
        Returns:
            Dict {slot_key: [food_names]}
        """
        foods_by_slot = {}
        
        for meal in [menu_plan.breakfast, menu_plan.lunch, menu_plan.dinner]:
            meal_name = meal.meal_type.lower()
            
            for course_type, course in meal.courses.items():
                slot_key = f"{meal_name}_{course_type.lower()}"
                foods_by_slot[slot_key] = [
                    item.food_name for item in course.candidates
                ]
        
        snack_key = 'snack'
        foods_by_slot[snack_key] = [
            item.food_name for item in menu_plan.snack.candidates
        ] if menu_plan.snack is not None else []
        
        return foods_by_slot
    
    @staticmethod
    def check_within_slot_duplicates(menu_plan: MenuPlan) -> Dict[str, List[Tuple[str, str, float]]]:
        """
        Check for duplicates WITHIN masing-masing slot (dalam 3 candidates)
        
        Args:
            menu_plan: MenuPlan object
        
        Returns:
            Dict {slot_key: [(name1, name2, score)]}
        """
        foods_by_slot = SimilarityChecker.extract_all_food_names(menu_plan)
        duplicates_by_slot = {}
        
        for slot_key, food_names in foods_by_slot.items():
            dups = SimilarityChecker.find_duplicates(food_names)
            if dups:
                duplicates_by_slot[slot_key] = dups
        
        return duplicates_by_slot
    
    @staticmethod
    def check_across_slots_duplicates(menu_plan: MenuPlan, compare_types: str = 'same') -> Dict[str, List[Tuple[str, str, str, float]]]:
        """
        Check for duplicates ACROSS different slots
        
        Args:
            menu_plan: MenuPlan object
            compare_types: 'same' (Main vs Main vs Main), 'all' (semua vs semua)
        
        Returns:
            Dict {comparison: [(slot1, slot2, food1, food2, score)]}
        """
        foods_by_slot = SimilarityChecker.extract_all_food_names(menu_plan)
        duplicates_across = {}
        
        if compare_types == 'same':
            main_slots = {k: v for k, v in foods_by_slot.items() if '_main' in k}
            
            slots_list = list(main_slots.items())
            for i in range(len(slots_list)):
                for j in range(i + 1, len(slots_list)):
                    slot1_key, slot1_foods = slots_list[i]
                    slot2_key, slot2_foods = slots_list[j]
                    
                    for food1 in slot1_foods:
                        for food2 in slot2_foods:
                            score = SimilarityChecker.calculate_similarity_score(food1, food2)
                            if score >= 0.7:
                                comparison_key = f"main_across"
                                if comparison_key not in duplicates_across:
                                    duplicates_across[comparison_key] = []
                                duplicates_across[comparison_key].append((slot1_key, slot2_key, food1, food2, score))
        
        return duplicates_across
    
    @staticmethod
    def calculate_diversity_score(menu_plan: MenuPlan) -> float:
        """
        Calculate overall diversity score dari MenuPlan (0-100)
        """
        score = 0
        
        within_dups = SimilarityChecker.check_within_slot_duplicates(menu_plan)
        if len(within_dups) == 0:
            score += 20
        else:
            penalty = len(within_dups) * 5
            score += max(0, 20 - penalty)
        
        foods_by_slot = SimilarityChecker.extract_all_food_names(menu_plan)
        all_proteins = set()
        
        for foods in foods_by_slot.values():
            for food in foods:
                prot = SimilarityChecker.extract_protein_source(food)
                if prot:
                    all_proteins.add(prot)
        
        protein_score = min(50, len(all_proteins) * 10)
        score += protein_score
        
        across_dups = SimilarityChecker.check_across_slots_duplicates(menu_plan, 'same')
        if len(across_dups) == 0:
            score += 30
        else:
            score += max(0, 30 - len(across_dups) * 10)
        
        return min(100, score)
    
    @staticmethod
    def generate_similarity_report(menu_plan: MenuPlan) -> Dict:
        """
        Generate comprehensive similarity report untuk MenuPlan
        """
        report = {
            'within_slot_duplicates': SimilarityChecker.check_within_slot_duplicates(menu_plan),
            'across_slots_similar': SimilarityChecker.check_across_slots_duplicates(menu_plan, 'same'),
            'diversity_score': SimilarityChecker.calculate_diversity_score(menu_plan),
            'recommendations': []
        }
        
        if report['within_slot_duplicates']:
            report['recommendations'].append(
                "⚠️  Found similar items within same slot - regenerate candidates to increase variety"
            )
        
        if report['across_slots_similar']:
            report['recommendations'].append(
                "⚠️  Found similar protein sources across meals - consider refresh to add variety"
            )
        
        if report['diversity_score'] < 50:
            report['recommendations'].append(
                "❌ Low diversity score - recommendation to regenerate entire menu"
            )
        elif report['diversity_score'] < 70:
            report['recommendations'].append(
                "⚠️  Moderate diversity - consider refreshing some slots"
            )
        else:
            report['recommendations'].append(
                "✅ Good diversity in menu - acceptable for user"
            )
        
        return report


if __name__ == "__main__":
    test_pairs = [
        ("Chicken Breast", "Grilled Chicken"),
        ("Salmon Fillet", "Baked Salmon"),
        ("Rice", "Bread"),
        ("Chicken Breast", "Salmon Fillet"),
    ]
    
    print("=== Similarity Scores ===")
    for name1, name2 in test_pairs:
        score = SimilarityChecker.calculate_similarity_score(name1, name2)
        print(f"{name1} vs {name2}: {score:.2f}")

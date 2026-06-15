"""
================================================================================
c_post_processing.py - Penyeimbang Porsi & Pemeriksa Kemiripan (Post-Processing)
================================================================================
File ini memproses:
1. Phase 3 (Post-Selection Portion Rebalancing): Menghitung kembali dan menyesuaikan porsi makanan yang sudah terpilih setelah pengguna melakukan substitusi (misalnya mengganti minuman manis dengan air putih).
2. Menghitung kesenjangan gizi (Nutrition Gap) antara target harian dengan nutrisi saat ini setelah ada perubahan menu.
3. Mendeteksi adanya item makanan yang serupa/duplikat baik di dalam slot waktu makan yang sama (kandidat alternatif) maupun antar waktu makan yang berbeda.
4. Menghitung nilai keberagaman menu harian (Diversity Score) dari 0 s.d. 100 dan memberikan rekomendasi perbaikan variasi menu.
================================================================================
"""

import sys
import os
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from meal_schema import FoodItem, MenuPlan, Meal, SnackMeal, MealCourse

# Portion limits (same as in optimizer)
PORTION_RANGE = {
    'Main Course': (100, 400),
    'Side Dish': (50, 250),
    'Drink': (100, 300),
    'Snack': (30, 100)
}


@dataclass
class NutritionGap:
    """Represents a nutritional deficit"""
    energy_gap_kcal: float = 0.0
    protein_gap_g: float = 0.0
    fat_gap_g: float = 0.0
    carb_gap_g: float = 0.0
    magnitude: float = 0.0  # Total gap magnitude for prioritization


@dataclass
class PortionRebalanceResult:
    """Result of portion rebalancing operation"""
    success: bool
    nutrition_gap_before: NutritionGap
    nutrition_gap_after: NutritionGap
    rebalanced_items: List[Tuple[str, float, float]] = field(default_factory=list)  # (name, original_portion, new_portion)
    nutrition_coverage_before: Dict[str, float] = field(default_factory=dict)
    nutrition_coverage_after: Dict[str, float] = field(default_factory=dict)
    message: str = ""


# ═════════════════════════════════════════════════════════════════════════════════
# 1. PORTION REBALANCER (PHASE 3)
# ═════════════════════════════════════════════════════════════════════════════════

class PortionRebalancer:
    """
    Post-selection portion rebalancing utility.
    
    Workflow:
    1. Calculate nutritional deficits after user substitutions
    2. Identify which foods can absorb portion increases
    3. Increase portions of high-impact foods (calorie/nutrient dense)
    4. Respect realistic serving size limits
    5. Return rebalanced portions and updated nutrition summary
    """
    
    @staticmethod
    def calculate_nutrition_gap(
        target_nutrition: Dict[str, float],
        current_nutrition: Dict[str, float]
    ) -> NutritionGap:
        """
        Calculate nutritional deficit between target and current.
        
        Args:
            target_nutrition: Target daily nutrition (e.g., from DRI guidelines)
            current_nutrition: Current nutrition after user substitutions
        
        Returns:
            NutritionGap with all deficits
        """
        gap = NutritionGap(
            energy_gap_kcal=max(0, target_nutrition.get('energy_kcal', 0) - current_nutrition.get('energy_kcal', 0)),
            protein_gap_g=max(0, target_nutrition.get('protein_g', 0) - current_nutrition.get('protein_g', 0)),
            fat_gap_g=max(0, target_nutrition.get('fat_g', 0) - current_nutrition.get('fat_g', 0)),
            carb_gap_g=max(0, target_nutrition.get('carbohydrate_g', 0) - current_nutrition.get('carbohydrate_g', 0)),
        )
        
        # Calculate gap magnitude (normalized)
        gap.magnitude = (
            gap.energy_gap_kcal / max(target_nutrition.get('energy_kcal', 1), 1) * 0.4 +
            gap.protein_gap_g / max(target_nutrition.get('protein_g', 1), 1) * 0.3 +
            gap.fat_gap_g / max(target_nutrition.get('fat_g', 1), 1) * 0.15 +
            gap.carb_gap_g / max(target_nutrition.get('carbohydrate_g', 1), 1) * 0.15
        )
        
        return gap
    
    @staticmethod
    def calculate_nutrient_density(food_item: FoodItem) -> Dict[str, float]:
        """
        Calculate nutrient density per gram for a food.
        
        Returns:
            Dict with 'energy', 'protein', 'fat', 'carb' per gram
        """
        if food_item.portion_gram <= 0:
            return {'energy': 0, 'protein': 0, 'fat': 0, 'carb': 0}
        
        per_gram = food_item.portion_gram
        
        return {
            'energy': food_item.energy_kcal / per_gram,
            'protein': food_item.protein_g / per_gram,
            'fat': food_item.fat_g / per_gram,
            'carb': food_item.carbohydrate_g / per_gram,
        }
    
    @staticmethod
    def scale_food_to_portion(
        food_item: FoodItem,
        new_portion_gram: float
    ) -> FoodItem:
        """
        Create a new FoodItem with scaled nutrients for a new portion.
        
        Args:
            food_item: Original food item with current portion
            new_portion_gram: New portion size in grams
        
        Returns:
            New FoodItem with scaled nutrients
        """
        # Round to the nearest whole integer gram for practical usability
        rounded_portion_gram = float(round(new_portion_gram))
        
        if food_item.portion_gram <= 0:
            scale = 1.0
        else:
            scale = rounded_portion_gram / food_item.portion_gram
        
        # Create new item with scaled values
        return FoodItem(
            fdc_id=food_item.fdc_id,
            food_name=food_item.food_name,
            food_group=food_item.food_group,
            consumption_label=food_item.consumption_label,
            cuisine_label=food_item.cuisine_label,
            portion_gram=rounded_portion_gram,
            energy_kcal=round(food_item.energy_kcal * scale, 1),
            protein_g=round(food_item.protein_g * scale, 2),
            carbohydrate_g=round(food_item.carbohydrate_g * scale, 2),
            fat_g=round(food_item.fat_g * scale, 2),
        )
    
    @staticmethod
    def rebalance_meal(
        meal: Meal,
        nutrition_gap: NutritionGap,
        target_nutrition: Dict[str, float]
    ) -> Tuple[Meal, List[Tuple[str, float, float]]]:
        """
        Rebalance portions within a meal to close nutritional gaps.
        """
        if not meal or not meal.courses:
            return meal, []
        
        changes = []
        foods_to_rebalance = []
        
        for course_type, course in meal.courses.items():
            if not course or not course.candidates:
                continue
            
            food_item = course.candidates[0]
            consumption_label = food_item.consumption_label
            min_p, max_p = PORTION_RANGE.get(consumption_label, (50, 400))
            
            foods_to_rebalance.append({
                'item': food_item,
                'course_type': course_type,
                'current_portion': food_item.portion_gram,
                'min_portion': min_p,
                'max_portion': max_p,
                'density': PortionRebalancer.calculate_nutrient_density(food_item)
            })
        
        if nutrition_gap.magnitude < 0.05:
            return meal, changes
        
        total_gap_magnitude = nutrition_gap.magnitude
        
        for attempt in range(3):
            if total_gap_magnitude < 0.05:
                break
            
            main_port = None
            for f in foods_to_rebalance:
                if f['course_type'] == 'Main':
                    main_port = f['current_portion']
                    break

            best_food = None
            best_score = 0
            
            for idx, food_dict in enumerate(foods_to_rebalance):
                max_allowed_portion = food_dict['max_portion']
                if food_dict['course_type'] in ['Side', 'Drink'] and main_port is not None:
                    max_allowed_portion = min(max_allowed_portion, main_port - 1.0)

                if food_dict['current_portion'] >= max_allowed_portion:
                    continue
                
                score = 0
                if nutrition_gap.energy_gap_kcal > 0:
                    score += food_dict['density']['energy'] * nutrition_gap.energy_gap_kcal
                if nutrition_gap.protein_gap_g > 0:
                    score += food_dict['density']['protein'] * nutrition_gap.protein_gap_g * 2
                
                if score > best_score:
                    best_score = score
                    best_food = food_dict
            
            if best_food is None:
                break
            
            old_portion = best_food['current_portion']
            max_allowed_portion = best_food['max_portion']
            if best_food['course_type'] in ['Side', 'Drink'] and main_port is not None:
                max_allowed_portion = min(max_allowed_portion, main_port - 1.0)

            max_increase = max_allowed_portion - old_portion
            increment = max(1.0, max_increase * 0.2)
            new_portion = min(old_portion + increment, max_allowed_portion)
            new_portion = float(round(new_portion))
            
            best_food['current_portion'] = new_portion

        main_port = None
        for f in foods_to_rebalance:
            if f['course_type'] == 'Main':
                main_port = f['current_portion']
                break
                
        if main_port is not None:
            for f in foods_to_rebalance:
                if f['course_type'] in ['Side', 'Drink']:
                    if f['current_portion'] >= main_port:
                        f['current_portion'] = max(f['min_portion'], main_port - 1.0)
                        f['current_portion'] = float(round(f['current_portion']))
            
            new_totals = {
                'energy_kcal': 0.0,
                'protein_g': 0.0,
                'fat_g': 0.0,
                'carbohydrate_g': 0.0,
            }
            
            for food_dict in foods_to_rebalance:
                scale = food_dict['current_portion'] / food_dict['item'].portion_gram
                new_totals['energy_kcal'] += food_dict['item'].energy_kcal * scale
                new_totals['protein_g'] += food_dict['item'].protein_g * scale
                new_totals['fat_g'] += food_dict['item'].fat_g * scale
                new_totals['carbohydrate_g'] += food_dict['item'].carbohydrate_g * scale
            
            nutrition_gap = PortionRebalancer.calculate_nutrition_gap(target_nutrition, new_totals)
        
        new_meal = Meal(
            meal_type=meal.meal_type,
            courses={},
            target_calories=meal.target_calories,
            actual_calories=0,
            include_drink=meal.include_drink
        )
        
        actual_calories = 0
        
        for food_dict in foods_to_rebalance:
            original_item = food_dict['item']
            new_portion = food_dict['current_portion']
            
            if new_portion != food_dict['item'].portion_gram:
                changes.append((
                    original_item.food_name,
                    round(food_dict['item'].portion_gram, 1),
                    round(new_portion, 1)
                ))
            
            scaled_item = PortionRebalancer.scale_food_to_portion(original_item, new_portion)
            course_type = food_dict['course_type']
            candidates = [scaled_item]
            
            new_meal.courses[course_type] = MealCourse(
                course_type=course_type,
                candidates=candidates,
                total_calories=scaled_item.energy_kcal,
                total_protein_g=scaled_item.protein_g,
                total_carb_g=scaled_item.carbohydrate_g,
                total_fat_g=scaled_item.fat_g
            )
            
            actual_calories += scaled_item.energy_kcal
        
        new_meal.actual_calories = actual_calories
        
        return new_meal, changes
    
    @staticmethod
    def rebalance_menu(
        breakfast: Meal,
        lunch: Meal,
        dinner: Meal,
        snack: Optional[SnackMeal],
        target_nutrition: Dict[str, float],
        current_nutrition: Dict[str, float]
    ) -> PortionRebalanceResult:
        """
        Rebalance entire day's menu to close nutritional gaps.
        """
        gap_before = PortionRebalancer.calculate_nutrition_gap(target_nutrition, current_nutrition)
        all_changes = []
        
        breakfast, changes_b = PortionRebalancer.rebalance_meal(breakfast, gap_before, target_nutrition)
        all_changes.extend(changes_b)
        
        lunch, changes_l = PortionRebalancer.rebalance_meal(lunch, gap_before, target_nutrition)
        all_changes.extend(changes_l)
        
        dinner, changes_d = PortionRebalancer.rebalance_meal(dinner, gap_before, target_nutrition)
        all_changes.extend(changes_d)
        
        new_nutrition = {
            'energy_kcal': 0.0,
            'protein_g': 0.0,
            'fat_g': 0.0,
            'carbohydrate_g': 0.0,
        }
        
        if breakfast:
            new_nutrition['energy_kcal'] += breakfast.actual_calories
        if lunch:
            new_nutrition['energy_kcal'] += lunch.actual_calories
        if dinner:
            new_nutrition['energy_kcal'] += dinner.actual_calories
        if snack:
            new_nutrition['energy_kcal'] += snack.actual_calories
        
        gap_after = PortionRebalancer.calculate_nutrition_gap(target_nutrition, new_nutrition)
        
        coverage_before = {
            'energy': min(100, (current_nutrition.get('energy_kcal', 0) / target_nutrition.get('energy_kcal', 1)) * 100),
            'protein': min(100, (current_nutrition.get('protein_g', 0) / target_nutrition.get('protein_g', 1)) * 100),
        }
        
        coverage_after = {
            'energy': min(100, (new_nutrition['energy_kcal'] / target_nutrition.get('energy_kcal', 1)) * 100),
            'protein': min(100, (new_nutrition['protein_g'] / target_nutrition.get('protein_g', 1)) * 100),
        }
        
        return PortionRebalanceResult(
            success=True,
            nutrition_gap_before=gap_before,
            nutrition_gap_after=gap_after,
            rebalanced_items=all_changes,
            nutrition_coverage_before=coverage_before,
            nutrition_coverage_after=coverage_after,
            message=f"Rebalanced {len(all_changes)} food portions to recover nutritional deficits"
        )


# ═════════════════════════════════════════════════════════════════════════════════
# 2. SIMILARITY CHECKER
# ═════════════════════════════════════════════════════════════════════════════════

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
        """
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
        """
        if food_name1 == food_name2:
            return 1.0
        
        food_lower1 = food_name1.lower()
        food_lower2 = food_name2.lower()
        
        if food_lower1 == food_lower2:
            return 1.0
        
        protein1 = SimilarityChecker.extract_protein_source(food_name1)
        protein2 = SimilarityChecker.extract_protein_source(food_name2)
        
        if protein1 and protein2 and protein1 == protein2:
            return 0.8
        
        ing1 = SimilarityChecker.extract_main_ingredient(food_name1)
        ing2 = SimilarityChecker.extract_main_ingredient(food_name2)
        
        if ing1 and ing2:
            if ing1 == ing2:
                return 0.7
            
            if ing1 in ing2 or ing2 in ing1:
                return 0.5
        
        return 0.0
    
    @staticmethod
    def find_duplicates(food_items: List[str]) -> List[Tuple[str, str, float]]:
        """
        Find semua pasangan items yang similar dalam list
        """
        duplicates = []
        
        for i in range(len(food_items)):
            for j in range(i + 1, len(food_items)):
                score = SimilarityChecker.calculate_similarity_score(food_items[i], food_items[j])
                if score >= 0.5:
                    duplicates.append((food_items[i], food_items[j], score))
        
        return sorted(duplicates, key=lambda x: x[2], reverse=True)
    
    @staticmethod
    def extract_all_food_names(menu_plan: MenuPlan) -> Dict[str, List[str]]:
        """
        Extract semua food names dari MenuPlan terstruktur per kategori slot
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

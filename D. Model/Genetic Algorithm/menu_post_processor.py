"""
GA POST-PROCESSOR: Extract Multiple Solutions from GA Population
Mengambil TOP N chromosomes dan mengkonsolidasikan menjadi menu interaktif

Proses:
1. Ambil top K chromosome dari final population (berdasarkan fitness)
2. Extract semua foods dari setiap chromosome per meal per slot
3. Consolidate: unique foods dengan tracking frequency
4. Classify: main course vs side dish vs drink
5. Select: top 3 unique items per category

Cocok untuk menu selection dengan options.
"""

import pandas as pd
from typing import Dict, List, Tuple, Optional, Set
from collections import defaultdict


class MenuPostProcessor:
    """
    Post-processor untuk GA results
    Input: Population + fitness scores dari GA
    Output: Consolidated menu dengan 3 options per kategori
    """
    
    # ========================================================================
    # CLASSIFICATION RULES: Mendeteksi tipe food
    # ========================================================================
    
    MAIN_COURSE_KEYWORDS = {
        'nasi', 'roti', 'mie', 'pasta', 'rice', 'bread', 'noodle',
        'daging', 'ayam', 'ikan', 'sapi', 'babi', 'udang', 'telur',
        'meat', 'chicken', 'fish', 'beef', 'pork', 'shrimp', 'egg',
        'bubur', 'porridge', 'soup', 'sup', 'stew', 'curry', 'kare',
        'pizza', 'burger', 'sandwich', 'taco', 'kebab', 'soto', 'gado',
        'tumis', 'goreng', 'rebus', 'panggang', 'bakar', 'stir-fry',
        'baso', 'lumpia', 'spring roll', 'dim sum', 'dumpling'
    }
    
    SIDE_DISH_KEYWORDS = {
        'sayur', 'vegetable', 'salad', 'lalapan', 'ulam',
        'sambal', 'sauce', 'gravy', 'kuah',
        'kerupuk', 'chips', 'keripik', 'kripik',
        'tahu', 'tempe', 'kacang', 'nuts', 'beans',
        'acar', 'pickle', 'kimchi',
        'nori', 'seaweed'
    }
    
    DRINK_KEYWORDS = {
        'air', 'water', 'teh', 'tea', 'kopi', 'coffee',
        'susu', 'milk', 'yogurt', 'lassi',
        'jus', 'juice', 'smoothie', 'blend',
        'minuman', 'drink', 'beverage',
        'soda', 'sprite', 'fanta', 'cola',
        'sirup', 'syrup', 'cordial',
        'birch', 'kombucha', 'kopi'
    }
    
    SNACK_KEYWORDS = {
        'snack', 'cemilan', 'samping',
        'kue', 'cake', 'biscuit', 'biskuit', 'crackers', 'cookies',
        'coklat', 'chocolate', 'candy', 'permen', 'toffee',
        'buah', 'fruit', 'apel', 'jeruk', 'pisang', 'orange', 'banana',
        'granola', 'yogurt', 'pudding', 'dessert', 'ice cream', 'es krim',
        'popcorn', 'wafer', 'peanut', 'almond', 'cashew',
        'bar', 'energy bar', 'cereal'
    }
    
    # ========================================================================
    # MAIN METHODS
    # ========================================================================
    
    @staticmethod
    def extract_top_chromosomes(
        population: List[Dict],
        fitness_scores: List[float],
        top_k: int = 5
    ) -> List[Tuple[Dict, float]]:
        """
        Extract top K chromosomes dengan fitness scores
        
        Args:
            population: List of chromosomes dari GA
            fitness_scores: List of fitness scores matching population
            top_k: Banyak chromosome yang diambil (default 5)
        
        Returns:
            List of (chromosome, fitness) tuples, sorted by fitness descending
        """
        
        if len(population) == 0:
            return []
        
        # Zip dan sort
        population_with_scores = list(zip(population, fitness_scores))
        population_with_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Return top K
        return population_with_scores[:min(top_k, len(population_with_scores))]
    
    @staticmethod
    def extract_foods_from_chromosomes(
        top_chromosomes: List[Tuple[Dict, float]],
        food_database: pd.DataFrame
    ) -> Dict[str, List[Tuple[str, float, Dict]]]:
        """
        Extract semua foods dari top chromosomes
        Per meal, track frequency and nutrient info
        
        Args:
            top_chromosomes: List of (chromosome, fitness) from extract_top_chromosomes
            food_database: DataFrame dengan foods
        
        Returns:
            {meal_name: [(food_id, frequency, food_info), ...], ...}
        """
        
        foods_per_meal = defaultdict(lambda: defaultdict(list))
        # Structure: {meal: {food_id: [(frequency, portion, food_info), ...]}}
        
        for chromosome, fitness_score in top_chromosomes:
            if not chromosome:
                continue
            
            # Iterate per meal dalam chromosome
            for meal_name, meal_foods in chromosome.items():
                if not meal_foods:
                    continue
                
                # Iterate per food dalam meal
                for food_id, portion in meal_foods.items():
                    
                    # Get food info dari database
                    try:
                        food_info = MenuPostProcessor._get_food_info(
                            food_id, food_database
                        )
                        
                        foods_per_meal[meal_name][food_id].append({
                            'portion': portion,
                            'fitness': fitness_score,
                            'info': food_info
                        })
                    
                    except KeyError:
                        # Food not found in database, skip
                        continue
        
        return foods_per_meal
    
    @staticmethod
    def consolidate_foods_per_category(
        foods_per_meal: Dict[str, Dict],
    ) -> Dict[str, Dict[str, List[Tuple[str, float]]]]:
        """
        Consolidate foods per meal per category (main/side/drink)
        
        Returns:
            {meal: {category: [(food_id, avg_frequency), ...], ...}, ...}
        
        Example:
            {'breakfast': {
                'main_course': [('nasi_kuning', 3.5), ('roti', 2.1), ...],
                'side_dish': [('telur', 4.2), ('tempe', 2.0), ...],
                'drink': [('teh', 3.0), ('susu', 1.5), ...]
            }, ...}
        """
        
        meal_categories = defaultdict(lambda: defaultdict(list))
        
        for meal_name, foods_dict in foods_per_meal.items():
            
            for food_id, occurrences in foods_dict.items():
                
                # Dapatkan average frequency dan sample food info
                avg_frequency = sum(occ['fitness'] for occ in occurrences) / len(occurrences)
                sample_info = occurrences[0]['info']  # Use first occurrence
                
                # Classify category
                category = MenuPostProcessor.classify_food_category(sample_info)
                
                # Add to category
                meal_categories[meal_name][category].append({
                    'food_id': food_id,
                    'food_name': sample_info.get('food_name', food_id),
                    'avg_frequency': avg_frequency,
                    'portion': occurrences[0]['portion'],  # Use first portion as reference
                    'energy_kcal': sample_info.get('energy_kcal', 0),
                    'protein_g': sample_info.get('protein_g', 0),
                    'carbs_g': sample_info.get('carbohydrate_g', 0),
                    'fat_g': sample_info.get('fat_g', 0),
                })
        
        return meal_categories
    
    @staticmethod
    def select_top_options(
        meal_categories: Dict[str, Dict[str, List[Dict]]],
        top_n: int = 3
    ) -> Dict[str, Dict[str, List[Dict]]]:
        """
        Select top N unique items per meal per category (based on frequency)
        
        Args:
            meal_categories: Output dari consolidate_foods_per_category
            top_n: Berapa items per kategori (default 3)
        
        Returns:
            {meal: {category: [top_n_items], ...}, ...}
        """
        
        selected_options = defaultdict(dict)
        
        for meal_name, categories in meal_categories.items():
            
            for category, foods_list in categories.items():
                
                # Sort by avg_frequency descending
                sorted_foods = sorted(
                    foods_list,
                    key=lambda x: x['avg_frequency'],
                    reverse=True
                )
                
                # Take top N
                selected_options[meal_name][category] = sorted_foods[:top_n]
        
        return selected_options
    
    @staticmethod
    def classify_food_category(food_info: Dict) -> str:
        """
        Klasifikasi food ke kategori (main_course, side_dish, drink, snack)
        
        Args:
            food_info: Dict dengan food_name and nama other info
        
        Returns:
            str: 'main_course', 'side_dish', 'drink', atau 'snack'
        """
        
        food_name = food_info.get('food_name', '').lower()
        
        # Check setiap kategori
        if any(keyword in food_name for keyword in MenuPostProcessor.DRINK_KEYWORDS):
            return 'drink'
        
        elif any(keyword in food_name for keyword in MenuPostProcessor.SNACK_KEYWORDS):
            return 'snack'
        
        elif any(keyword in food_name for keyword in MenuPostProcessor.SIDE_DISH_KEYWORDS):
            return 'side_dish'
        
        elif any(keyword in food_name for keyword in MenuPostProcessor.MAIN_COURSE_KEYWORDS):
            return 'main_course'
        
        # Default classification based on energy
        energy = food_info.get('energy_kcal', 0)
        if energy > 300:
            return 'main_course'
        elif energy > 100:
            return 'side_dish'
        elif energy > 50:
            return 'snack'
        else:
            return 'drink'
    
    @staticmethod
    def process_snacks_separately(
        foods_per_meal: Dict[str, Dict]
    ) -> List[Dict]:
        """
        Extract snacks dari semua meals dan return sebagai separate list
        
        Returns:
            List of snack items: [{'food_id': ..., 'food_name': ..., ...}, ...]
        """
        
        all_snacks = {}  # food_id -> {info with frequency}
        
        for meal_name, foods_dict in foods_per_meal.items():
            
            for food_id, occurrences in foods_dict.items():
                
                sample_info = occurrences[0]['info']
                
                # Check if snack
                if MenuPostProcessor.classify_food_category(sample_info) == 'snack':
                    
                    avg_frequency = sum(occ['fitness'] for occ in occurrences) / len(occurrences)
                    
                    all_snacks[food_id] = {
                        'food_id': food_id,
                        'food_name': sample_info.get('food_name', food_id),
                        'avg_frequency': avg_frequency,
                        'energy_kcal': sample_info.get('energy_kcal', 0),
                        'portion': occurrences[0]['portion'],
                        'protein_g': sample_info.get('protein_g', 0),
                        'carbs_g': sample_info.get('carbohydrate_g', 0),
                        'fat_g': sample_info.get('fat_g', 0),
                    }
        
        # Sort by frequency dan return top 3
        sorted_snacks = sorted(
            all_snacks.values(),
            key=lambda x: x['avg_frequency'],
            reverse=True
        )
        
        return sorted_snacks[:3]  # Top 3 snacks
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    @staticmethod
    def _get_food_info(food_id: str, food_database: pd.DataFrame) -> Dict:
        """
        Get food information dari database
        
        Args:
            food_id: fdc_id
            food_database: DataFrame
        
        Returns:
            Dict dengan food info
        
        Raises:
            KeyError if food not found
        """
        
        food_row = food_database[food_database['fdc_id'] == food_id]
        
        if food_row.empty:
            raise KeyError(f"Food {food_id} not found in database")
        
        row = food_row.iloc[0]
        
        return {
            'food_name': row.get('food_name', food_id),
            'energy_kcal': row.get('energy_kcal', 0),
            'protein_g': row.get('protein_g', 0),
            'carbohydrate_g': row.get('carbohydrate_g', 0),
            'fat_g': row.get('fat_g', 0),
            'fiber_g': row.get('fiber_g', 0),
        }
    
    # ========================================================================
    # MAIN WORKFLOW
    # ========================================================================
    
    @staticmethod
    def process(
        population: List[Dict],
        fitness_scores: List[float],
        food_database: pd.DataFrame,
        top_k: int = 5,
        top_n_options: int = 3
    ) -> Tuple[Dict[str, Dict[str, List[Dict]]], List[Dict]]:
        """
        Main processing pipeline
        
        Args:
            population: GA final population
            fitness_scores: Fitness scores untuk setiap chromosome
            food_database: DataFrame dengan foods
            top_k: Top K chromosomes to process (default 5)
            top_n_options: Top N options per category (default 3)
        
        Returns:
            (meal_options, snack_options)
            
            meal_options = {
                'breakfast': {
                    'main_course': [{'food_id': ..., 'food_name': ..., }, ...],
                    'side_dish': [...],
                    'drink': [...]
                },
                'lunch': {...},
                'dinner': {...}
            }
            
            snack_options = [
                {'food_id': ..., 'food_name': ..., },
                ...
            ]
        """
        
        # Step 1: Extract top K chromosomes
        top_chromosomes = MenuPostProcessor.extract_top_chromosomes(
            population, fitness_scores, top_k
        )
        
        if not top_chromosomes:
            return {}, []
        
        # Step 2: Extract foods dari setiap chromosome
        foods_per_meal = MenuPostProcessor.extract_foods_from_chromosomes(
            top_chromosomes, food_database
        )
        
        # Step 3: Consolidate per category
        meal_categories = MenuPostProcessor.consolidate_foods_per_category(
            foods_per_meal
        )
        
        # Step 4: Select top N per category
        meal_options = MenuPostProcessor.select_top_options(
            meal_categories, top_n_options
        )
        
        # Step 5: Extract snacks
        snack_options = MenuPostProcessor.process_snacks_separately(
            foods_per_meal
        )
        
        return dict(meal_options), snack_options


if __name__ == "__main__":
    print("MenuPostProcessor module loaded")
    print("Use: from menu_post_processor import MenuPostProcessor")

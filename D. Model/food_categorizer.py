"""
Food Categorizer - Map dataset consumption_label ke slot categories
Mengubah food items dari dataset ke kategori yang bisa digunakan untuk slot menu
"""

import pandas as pd
from typing import Dict, List, Optional, cast


class FoodCategorizer:
    """
    Kategorisasi makanan dari dataset ke slot menu (Main, Side, Drink, Snack)
    
    Mapping:
    - Dari consumption_label di dataset, pisahkan ke kategori slot
    - Jika consumption_label tidak cocok, gunakan food_group sebagai fallback
    """
    
    # Mapping dari consumption_label ke kategori slot
    LABEL_MAPPING = {
        # Main Course
        'Main': 'Main',
        'Main Dish': 'Main',
        'Main Course': 'Main',
        
        # Side Dish
        'Side': 'Side',
        'Side Dish': 'Side',
        'Sides': 'Side',
        'Vegetables and Vegetable Products': 'Side',
        'Breakfast Cereals': 'Side',
        'Baked Products': 'Side',  # Roti, nasi, pasta
        'Legumes': 'Side',
        'Nuts and Seeds': 'Side',
        
        # Drink
        'Drink': 'Drink',
        'Beverage': 'Drink',
        'Beverages': 'Drink',
        'Juice': 'Drink',
        'Tea': 'Drink',
        'Coffee': 'Drink',
        'Water': 'Drink',
        
        # Snack
        'Snack': 'Snack',
        'Sweets': 'Snack',
        'Dessert': 'Snack',
        'Candy': 'Snack',
    }
    
    # Fallback: jika label tidak ditemukan, gunakan food_group
    FOODGROUP_FALLBACK = {
        'Meat and Meat Products': 'Main',
        'Poultry Products': 'Main',
        'Fish and Seafood': 'Main',
        'Dairy and Egg Products': 'Main',
        'Legumes and Legume Products': 'Side',
        'Cereal Grains and Pasta': 'Side',
        'Baked Products': 'Side',
        'Vegetables and Vegetable Products': 'Side',
        'Fruits and Fruit Juices': 'Side',
        'Nut and Seed Products': 'Side',
        'Sweets': 'Snack',
        'Spices and Herbs': 'Side',
    }
    
    @staticmethod
    def categorize_item(item_dict: Dict) -> Optional[str]:
        """
        Kategorisasi satu item makanan ke slot category
        
        Args:
            item_dict: Diet dari food dataset (dengan columns: consumption_label, food_group)
        
        Returns:
            Category: 'Main', 'Side', 'Drink', 'Snack', atau None jika tidak bisa dikategorisasi
        """
        
        # Try consumption_label first
        consumption_label = str(item_dict.get('consumption_label', '')).strip()
        if consumption_label and consumption_label in FoodCategorizer.LABEL_MAPPING:
            return FoodCategorizer.LABEL_MAPPING[consumption_label]
        
        # Fallback ke food_group
        food_group = str(item_dict.get('food_group', '')).strip()
        if food_group and food_group in FoodCategorizer.FOODGROUP_FALLBACK:
            return FoodCategorizer.FOODGROUP_FALLBACK[food_group]
        
        # Jika masih tidak ketemu, coba regex pada food_name sebagai last resort
        food_name = str(item_dict.get('food_name', '')).lower()
        
        # Drink patterns
        if any(keyword in food_name for keyword in ['juice', 'beverage', 'coffee', 'tea', 'milk', 'drink', 'water', 'soda']):
            return 'Drink'
        
        # Snack patterns
        if any(keyword in food_name for keyword in ['candy', 'chocolate', 'sweet', 'dessert', 'ice cream', 'cookie', 'cracker', 'candy']):
            return 'Snack'
        
        # Side patterns
        if any(keyword in food_name for keyword in ['rice', 'pasta', 'bread', 'vegetable', 'grain', 'bean', 'legume']):
            return 'Side'
        
        return None
    
    @staticmethod
    def categorize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """
        Tambahkan kolom category ke dataframe
        
        Args:
            df: DataFrame dari NutritionService dengan food data
        
        Returns:
            DataFrame dengan kolom 'menu_category' tambahan
        """
        df = df.copy()
        df['menu_category'] = df.apply(FoodCategorizer.categorize_item, axis=1)
        return df
    
    @staticmethod
    def filter_by_category(df: pd.DataFrame, category: str) -> pd.DataFrame:
        """
        Filter food items berdasarkan category
        
        Args:
            df: DataFrame dengan kolom 'menu_category'
            category: 'Main', 'Side', 'Drink', 'Snack'
        
        Returns:
            Filtered DataFrame
        """
        if 'menu_category' not in df.columns:
            df = FoodCategorizer.categorize_dataframe(df)
        
        return cast(pd.DataFrame, df[df['menu_category'] == category].reset_index(drop=True))
    
    @staticmethod
    def get_category_stats(df: pd.DataFrame) -> Dict[str, int]:
        """
        Get jumlah item per category
        
        Args:
            df: DataFrame dengan kolom 'menu_category'
        
        Returns:
            Dict dengan count per category
        """
        if 'menu_category' not in df.columns:
            df = FoodCategorizer.categorize_dataframe(df)
        
        return cast(Dict[str, int], df['menu_category'].value_counts().to_dict())


# Test
if __name__ == "__main__":
    sample_items = [
        {
            'food_name': 'Chicken Breast',
            'consumption_label': 'Main',
            'food_group': 'Poultry Products'
        },
        {
            'food_name': 'White Rice',
            'consumption_label': 'Side Dish',
            'food_group': 'Cereal Grains and Pasta'
        },
        {
            'food_name': 'Orange Juice',
            'consumption_label': 'Drink',
            'food_group': 'Fruits and Fruit Juices'
        },
        {
            'food_name': 'Chocolate Bar',
            'consumption_label': 'Snack',
            'food_group': 'Sweets'
        }
    ]
    
    for item in sample_items:
        category = FoodCategorizer.categorize_item(item)
        print(f"{item['food_name']} -> {category}")

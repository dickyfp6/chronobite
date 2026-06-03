"""
RULE-BASED FOOD CONSUMPTION LABEL CLASSIFIER
Data-driven deterministic rules derived from keyword analysis of 3,920 food items.

Rules organized in 3 tiers:
- Tier 1: Unambiguous food_groups (99%+ consistency)
- Tier 2: High-probability food_groups (>90% consistency)  
- Tier 3: Ambiguous groups requiring keyword inspection

This replaces unreliable ML-based RandomForestClassifier with deterministic rules.
"""

import pandas as pd
import numpy as np
from typing import Tuple, Dict, List


class RuleBasedFoodClassifier:
    """
    Deterministic rule-based food consumption label classifier.
    
    Rules are applied in priority order. First matching rule wins.
    Each classification includes a confidence score (high/medium/low).
    """
    
    def __init__(self):
        """Initialize classifier with no state needed"""
        pass
    
    def classify(self, food_name: str, food_group: str) -> Tuple[str, str]:
        """
        Classify a single food into consumption_label with confidence.
        
        Args:
            food_name: Name of the food (e.g., "Milk, buttermilk, fluid, cultured")
            food_group: Food group classification (e.g., "Dairy and Egg Products")
            
        Returns:
            Tuple of (consumption_label, confidence)
            consumption_label: "Drink", "Main Course", "Side Dish", or "Snack"
            confidence: "high", "medium", or "low"
        """
        
        # Normalize inputs to lowercase for case-insensitive matching
        food_name_lower = food_name.lower() if food_name else ""
        food_group_lower = food_group.lower() if food_group else ""
        
        # TIER 1: UNAMBIGUOUS FOOD_GROUPS (99%+ consistency)
        # ========================================================================

        # Rule 1.1: Beverages
        if food_group_lower == "beverages":
            # Concentrate undiluted = bahan masak, bukan minuman siap minum
            if "concentrate" in food_name_lower:
                return ("Snack", "medium")
            return ("Drink", "high")
        
        # Rule 1.2-1.3: Vegetables (with juice distinction)
        if food_group_lower == "vegetables and vegetable products":
            if "juice" in food_name_lower:
                return ("Drink", "high")
            else:
                return ("Side Dish", "high")
        
        # Rule 1.4: Protein-based Main Courses
        meat_groups = [
            "beef products", "poultry products", 
            "finfish and shellfish products",
            "lamb, veal, and game products",
            "sausages and luncheon meats"
        ]
        if food_group_lower in meat_groups:
            return ("Main Course", "high")
        
        # Rule 1.5: Fats and Oils
        if food_group_lower == "fats and oils":
            return ("Side Dish", "high")
        
        # Rule 1.6: Spices and Herbs
        if food_group_lower == "spices and herbs":
            return ("Side Dish", "high")
        
        # Rule 1.7: Sweets
        if food_group_lower == "sweets":
            return ("Snack", "high")
        
        # TIER 2: HIGH-PROBABILITY FOOD_GROUPS (>90% consistency)
        # ========================================================================
        
        # Rule 2.1: Cereal Grains and Pasta
        if food_group_lower == "cereal grains and pasta":
            return ("Main Course", "medium")
        
        # Rule 2.2: Fast Foods
        if food_group_lower == "fast foods":
            return ("Main Course", "medium")
        
        # Rule 2.3: Breakfast Cereals - Tier approach based on preparation & type
        if food_group_lower == "breakfast cereals":
            # Tier A: Explicitly prepared/cooked cereals (highest confidence)
            if any(kw in food_name_lower for kw in ["prepared with", "cooked with"]):
                return ("Main Course", "high")
            
            # Tier B: Specific hot cereal brands (medium-high confidence)
            hot_cereal_keywords = [
                "grit", "grits",              # Corn grits - always cooked preparation
                "cream of wheat",              # Cream of Wheat brand - always hot cereal
                "cream of rice",               # Cream of Rice brand - always hot cereal
                "farina",                      # Farina - always hot cereal
                "wheatena",                    # WHEATENA brand - always hot cereal
            ]
            if any(kw in food_name_lower for kw in hot_cereal_keywords):
                return ("Main Course", "medium")
            
            # Tier C: Default ready-to-eat breakfast cereals → Side Dish
            # (Semantic: breakfast items are Main/Side, not Snack)
            return ("Side Dish", "medium")
        
        # Rule 2.4: Nut and Seed Products
        if food_group_lower == "nut and seed products":
            return ("Snack", "medium")
        
        # Rule 2.5: Meals, Entrees, and Side Dishes
        if food_group_lower == "meals, entrees, and side dishes":
            return ("Main Course", "medium")
        
        # Rule 2.6: Restaurant Foods
        if food_group_lower == "restaurant foods":
            return ("Main Course", "medium")
        
        # TIER 3: AMBIGUOUS FOOD_GROUPS - KEYWORD-BASED RULES
        # ========================================================================
        
        # Rule 3.1: FRUITS AND FRUIT JUICES
        if food_group_lower == "fruits and fruit juices":
            # Exclude: olive/pickle bukan minuman
            if any(x in food_name_lower for x in ['olive', 'pickle']):
                return ("Side Dish", "high")
            # Exclude: concentrate undiluted = bahan masak
            if 'concentrate' in food_name_lower and 'undiluted' in food_name_lower:
                return ("Snack", "medium")
            # Juice/nectar = Drink
            if any(x in food_name_lower for x in ['juice', 'nectar', 'concentrate']):
                return ("Drink", "high")
            # Buah biasa = Snack
            return ("Snack", "high")
                
        # Rule 3.2: DAIRY AND EGG PRODUCTS
        if food_group_lower == "dairy and egg products":
            
            # Cream, butter, cheese → Side Dish DULU sebelum cek milk
            if any(x in food_name_lower for x in ["cream", "cheese", "butter", "ricotta"]):
                return ("Side Dish", "high")

            # Fluid milk → Drink
            if "fluid" in food_name_lower:
                return ("Drink", "high")

            # Milk dessert/frozen/bar → Snack, bukan Drink
            if "milk" in food_name_lower:
                if any(x in food_name_lower for x in 
                    ["dessert", "frozen", "bar", "topping", "shake", 
                        "ice", "canned", "evaporated", "condensed"]):
                    return ("Snack", "medium")
                return ("Drink", "medium")
                    
        # Rule 3.3: BAKED PRODUCTS
        if food_group_lower == "baked products":
            # Priority: sweet indicators > bread indicators > else
            # 3.3.0: Bread dengan kata "bread" di nama → Side Dish dulu
            if "bread" in food_name_lower:
                return ("Side Dish", "medium")

            # 3.3.1: Cookies, crackers, waffles (clearly Snack)
            if any(x in food_name_lower for x in ["cookie", "cracker", "waffle", "cake", "pastry"]):
                return ("Snack", "high")
            
            # 3.3.2: Cake or pastry (Snack)
            if "cake" in food_name_lower or "pastry" in food_name_lower:
                return ("Snack", "high")
            
            # 3.3.3: Tortilla or flatbread (Main Course)
            if "tortilla" in food_name_lower or "flatbread" in food_name_lower:
                return ("Main Course", "medium")
            
            # 3.3.4: Bread with qualifiers (Side Dish)
            if "bread" in food_name_lower:
                if any(x in food_name_lower for x in ["roll", "bagel", "wheat", "grain"]):
                    return ("Side Dish", "medium")
                # Plain "bread" in name could go to Main or Snack
                # Fallback to 3.3.5
            
            # 3.3.5: else (default Snack for baked)
            return ("Snack", "medium")
        
        # Rule 3.4: SOUPS, SAUCES, AND GRAVIES
        if food_group_lower == "soups, sauces, and gravies":
            # Priority: soup > gravy/broth > sauce-context > else
            
            # 3.4.1: Soup (90.9% Main Course)
            if "soup" in food_name_lower:
                return ("Main Course", "high")
            
            # 3.4.2: Gravy or broth (Side Dish)
            if "gravy" in food_name_lower or "broth" in food_name_lower:
                return ("Side Dish", "high")
            
            # 3.4.3-3.4.5: Sauce (context-dependent)
            if "sauce" in food_name_lower:
                # Dry, mix, or powder sauces are Snack
                if any(x in food_name_lower for x in ["dry", "mix", "powder"]):
                    return ("Snack", "medium")
                # Ready-to-serve sauces are Side Dish
                elif "ready" in food_name_lower or "serve" in food_name_lower:
                    return ("Side Dish", "medium")
                # Default sauces are Side Dish
                else:
                    return ("Side Dish", "medium")
            
            # 3.4.6: else (fallback Main for unmatched soups/sauces)
            return ("Main Course", "low")
        
        # Rule 3.5: LEGUMES AND LEGUME PRODUCTS
        if food_group_lower == "legumes and legume products":
            # Priority: soymilk > peanut/butter/flour > bean/seed > else
            
            # 3.5.1: Soymilk (100% Drink)
            if "soymilk" in food_name_lower:
                return ("Drink", "high")
            
            # 3.5.2: Peanut (Snack)
            if "peanut" in food_name_lower:
                return ("Snack", "high")
            
            # 3.5.3: Butter (Snack - in legume context)
            if "butter" in food_name_lower:
                return ("Snack", "high")
            
            # 3.5.4: Flour (Snack - in legume context)
            if "flour" in food_name_lower:
                return ("Snack", "medium")
            
            # 3.5.5: Bean or seed (Main Course)
            if "bean" in food_name_lower or "seed" in food_name_lower:
                return ("Main Course", "high")
            
            # 3.5.6: else (fallback Main for legumes)
            return ("Main Course", "medium")
        
        # DEFAULT FALLBACK (for any unmatched food_group)
        # ========================================================================
        # Rule 9.1: Default to Snack (nutritionally safest default - smallest portions)
        return ("Snack", "low")
    
    def predict_batch(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Classify a batch of foods.
        
        Args:
            df: DataFrame with 'food_name' and 'food_group' columns
            
        Returns:
            DataFrame with 'label' and 'confidence' columns
        """
        results = []
        
        for idx, row in df.iterrows():
            food_name = row.get('food_name', '')
            food_group = row.get('food_group', '')
            label, confidence = self.classify(food_name, food_group)
            results.append({
                'label': label,
                'confidence': confidence
            })
        
        return pd.DataFrame(results)
    
    def predict(self, df: pd.DataFrame, return_both: bool = False):
        """
        Classify foods. Returns consumption_label predictions.
        
        Args:
            df: DataFrame with 'food_name' and 'food_group' columns
            return_both: If True, returns dict with 'consumption_label' and 'confidence'
            
        Returns:
            Array of consumption_labels if return_both=False
            Dict with 'consumption_label' array if return_both=True
        """
        predictions = self.predict_batch(df)
        
        if return_both:
            return {
                'consumption_label': predictions['label'].values,
                'confidence': predictions['confidence'].values
            }
        else:
            return predictions['label'].values


if __name__ == "__main__":
    # Quick test
    print("Rule-Based Food Classifier - Quick Test")
    print("=" * 60)
    
    classifier = RuleBasedFoodClassifier()
    
    # Test cases
    test_cases = [
        ("Milk, buttermilk, fluid, cultured", "Dairy and Egg Products"),
        ("Cheese, cheddar, sharp", "Dairy and Egg Products"),
        ("Lemon juice, raw", "Fruits and Fruit Juices"),
        ("Apples, raw", "Fruits and Fruit Juices"),
        ("Bread, white wheat", "Baked Products"),
        ("Cookies, chocolate chip", "Baked Products"),
        ("Soup, chicken, canned", "Soups, Sauces, and Gravies"),
        ("Sauce, teriyaki, dry", "Soups, Sauces, and Gravies"),
        ("Beans, baked, canned", "Legumes and Legume Products"),
        ("Peanut butter, creamy", "Legumes and Legume Products"),
    ]
    
    for food_name, food_group in test_cases:
        label, confidence = classifier.classify(food_name, food_group)
        print(f"{food_name:40} [{food_group:30}] -> {label:15} ({confidence})")

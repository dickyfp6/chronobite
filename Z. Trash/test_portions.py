import sys
import os
import pandas as pd
import numpy as np

# Setup path
project_root = r"c:\Users\USERR\Documents\0. Mata Kuliah\8 -TA\Code\TugasAkhirDSS"
sys.path.insert(0, os.path.join(project_root, 'D. Model'))
sys.path.insert(0, os.path.join(project_root, 'D. Model', 'Genetic Algorithm'))
sys.path.insert(0, os.path.join(project_root, 'D. Model', 'greedy'))

from ga_v1 import calculate_portion_sizes_dynamic  # type: ignore
from portion_rebalancer import PortionRebalancer  # type: ignore
from meal_schema import FoodItem, Meal, MealCourse

print("--- Testing GA Portion Sizing (Nearest 10g) ---")
# Create mock selected_df (10 items)
mock_cols = ['fdc_id', 'food_name', 'food_group', 'consumption_label', 'cuisine_label', 'energy_kcal', 'protein_g', 'fat_g', 'carbohydrate_g', 'fiber_g_g', 'sodium_mg_mg']
data = [
    ['1', 'Main 1', 'Group', 'Main Course', 'Generic', 300, 10, 5, 50, 2, 100],
    ['2', 'Side 1', 'Group', 'Side Dish', 'Generic', 150, 4, 2, 25, 1, 50],
    ['3', 'Drink 1', 'Group', 'Drink', 'Generic', 100, 2, 1, 20, 0, 20],
    ['4', 'Main 2', 'Group', 'Main Course', 'Generic', 320, 12, 6, 52, 2, 110],
    ['5', 'Side 2', 'Group', 'Side Dish', 'Generic', 140, 3, 2, 24, 1, 40],
    ['6', 'Drink 2', 'Group', 'Drink', 'Generic', 90, 1.5, 1, 18, 0, 15],
    ['7', 'Main 3', 'Group', 'Main Course', 'Generic', 280, 9, 4, 48, 2, 90],
    ['8', 'Side 3', 'Group', 'Side Dish', 'Generic', 160, 5, 3, 26, 1, 60],
    ['9', 'Drink 3', 'Group', 'Drink', 'Generic', 110, 2.5, 1.5, 22, 0, 25],
    ['10', 'Snack 1', 'Group', 'Snack', 'Generic', 200, 4, 3, 30, 1, 70]
]
selected_df = pd.DataFrame(data, columns=mock_cols)

# Rename to end with _g, _mg for task 1 mapping
selected_df = selected_df.rename(columns={'fiber_g_g': 'fiber_g', 'sodium_mg_mg': 'sodium_mg'})

# Run dynamic portion sizing (TDEE = 2000)
result_df = calculate_portion_sizes_dynamic(selected_df, 2000.0, guidelines=None)
print("GA Sizing Output Portions (grams):")
for idx, row in result_df.iterrows():
    print(f"  Item {idx+1} ({row['food_name']} - {row['consumption_label']}): {row['gram']}g (Type: {type(row['gram'])})")
    # Assert portion is a whole number (e.g. 154.0 is fine, but not 154.3)
    assert row['gram'] == float(int(row['gram'])), f"Error: portion {row['gram']} is not a whole number!"

print("OK: GA portion verification passed!")

print("\n--- Testing Greedy Rebalancer Portion Sizing ---")
# Create mock FoodItem
food1 = FoodItem(
    fdc_id='1',
    food_name='Test Main',
    food_group='Group',
    consumption_label='Main Course',
    cuisine_label='Generic',
    portion_gram=150.0,
    energy_kcal=300.0,
    protein_g=10.0,
    carbohydrate_g=50.0,
    fat_g=5.0,
    micronutrients={}
)

# Test scale_food_to_portion
scaled = PortionRebalancer.scale_food_to_portion(food1, 154.3)
print(f"Scale food 154.3g -> Rounded portion: {scaled.portion_gram}g (expected 154.0)")
assert scaled.portion_gram == 154.0, "Rebalancer scale_food_to_portion rounding failed!"

scaled_up = PortionRebalancer.scale_food_to_portion(food1, 157.8)
print(f"Scale food 157.8g -> Rounded portion: {scaled_up.portion_gram}g (expected 158.0)")
assert scaled_up.portion_gram == 158.0, "Rebalancer scale_food_to_portion rounding failed!"

print("OK: Rebalancer portion verification passed!")

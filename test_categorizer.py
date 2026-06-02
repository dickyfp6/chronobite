import sys
import os
sys.path.insert(0, 'D. Model')

import pandas as pd
from food_categorizer import FoodCategorizer

# Load dataset
df = pd.read_csv('A. Data/Data Processed/05_final_dataset.csv')

# Categorize
df_categorized = FoodCategorizer.categorize_dataframe(df)

# Check categories
print('Menu Categories after categorization:')
print(df_categorized['menu_category'].value_counts())
print()

# Check Drink category specifically
drinks = df_categorized[df_categorized['menu_category'] == 'Drink']
print(f'Total Drinks available: {len(drinks)}')
print(f'Sample drinks:')
print(drinks[['food_name', 'menu_category', 'energy_kcal']].head(10))

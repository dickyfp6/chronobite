import pandas as pd
df = pd.read_csv(r'C:\Users\Silfia\Documents\FILE TA\TugasAkhirDSS\A. Data\Data Processed\06_final_dataset.csv')
fast = df[df['food_group'].isin(['Fast Foods'])]
print(f"Sisa fast food/restaurant: {len(fast)}")
print(fast[['food_name', 'sodium_mg', 'fat_g', 'saturated_fat_g', 'cholesterol_mg']].to_string())
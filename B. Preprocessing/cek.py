import pandas as pd

df = pd.read_csv(r'C:\Users\Silfia\Documents\FILE TA\TugasAkhirDSS\A. Data\Data Processed\06_final_dataset.csv')
fast = df[df['food_group'].isin(['Fast Foods', 'Restaurant Foods'])].copy()

# Threshold per item yang lebih realistis
# Sodium: budget harian 2300mg dibagi 28 slot ≈ 82mg per slot
# tapi main course lebih besar, sekitar 200-400mg per item masih ok
# Fat: budget harian misal 65g dibagi 28 slot ≈ 2.3g, main course ~10-15g ok
# Saturated fat: max 10% TDEE (misal 2000kcal = 200kcal = 22g per hari)
# per main course max ~7-8g saturated fat

fast['flag_sodium'] = fast['sodium_mg'] > 800        # per item >800mg terlalu tinggi
fast['flag_sat_fat'] = fast['saturated_fat_g'] > 8   # per item >8g saturated fat tinggi
fast['flag_cholesterol'] = fast['cholesterol_mg'] > 200
fast['flag_trans_fat'] = fast['trans_fat_g'] > 0.5
fast['flag_fat'] = fast['fat_g'] > 25               # total fat >25g per item tinggi

fast['n_flags'] = (fast['flag_sodium'].astype(int) + 
                   fast['flag_sat_fat'].astype(int) +
                   fast['flag_cholesterol'].astype(int) + 
                   fast['flag_trans_fat'].astype(int) +
                   fast['flag_fat'].astype(int))

print(f"Sodium > 800mg: {fast['flag_sodium'].sum()} items")
print(f"Saturated fat > 8g: {fast['flag_sat_fat'].sum()} items")
print(f"Cholesterol > 200mg: {fast['flag_cholesterol'].sum()} items")
print(f"Trans fat > 0.5g: {fast['flag_trans_fat'].sum()} items")
print(f"Fat > 25g: {fast['flag_fat'].sum()} items")

print(f"\nItems dengan 0 flag: {(fast['n_flags']==0).sum()}")
print(f"Items dengan 1 flag: {(fast['n_flags']==1).sum()}")
print(f"Items dengan 2+ flags: {(fast['n_flags']>=2).sum()}")

print("\n" + "="*70)
print("ITEMS DENGAN 0 FLAG (benar-benar aman secara nutrisi):")
print("="*70)
safe = fast[fast['n_flags']==0]
print(safe[['food_name','sodium_mg','fat_g','saturated_fat_g','cholesterol_mg','trans_fat_g']].to_string())
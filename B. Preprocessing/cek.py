import pandas as pd

df = pd.read_csv(r"C:\Users\Silfia\Documents\FILE TA\TugasAkhirDSS\A. Data\Data Processed\06_final_dataset.csv")
print(df['food_group'].unique().tolist())
print()
print(df['consumption_label'].value_counts())

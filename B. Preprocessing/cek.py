import pandas as pd
food = pd.read_csv("../A. Data/Data Raw/food.csv")
print(food['data_type'].value_counts())
print(food['fdc_id'].min(), food['fdc_id'].max())
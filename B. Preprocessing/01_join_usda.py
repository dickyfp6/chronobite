import pandas as pd
import os

# ======================
# LOAD DATA
# ======================

food = pd.read_csv("A. Data/Data Raw/food.csv")
nutrient = pd.read_csv("A. Data/Data Raw/nutrient.csv")
food_nutrient = pd.read_csv("A. Data/Data Raw/food_nutrient.csv")
food_category = pd.read_csv("A. Data/Data Raw/food_category.csv")

print("Food:", food.shape)
print("Nutrient:", nutrient.shape)
print("Food Nutrient:", food_nutrient.shape)
print("Food Category:", food_category.shape)


# ======================
# JOIN TABLE
# ======================

df = food_nutrient.merge(
    nutrient,
    left_on="nutrient_id",
    right_on="id",
    how="left"
)

df = df.merge(
    food[["fdc_id", "description", "food_category_id"]],
    on="fdc_id",
    how="left"
)

df = df.merge(
    food_category[["id", "description"]],
    left_on="food_category_id",
    right_on="id",
    how="left"
)

df.rename(columns={
    "name": "nutrient_name",
    "description_x": "food_name",
    "description_y": "food_group"
}, inplace=True)


# ======================
# FILTER HC + SC
# ======================

nutrient_ids = [

# HC
1008, 1005, 1003, 1004, # Makro Nutrien
1079, 1051, 1106, 1253, # Fiber, Water, Vit A, Cholesterol
1258, 1257, 1091, 1092, # Saturated Fat, Trans fat, Phosphorus, Potassium
1093, 1095, 1087, 1089, # Sodium, Zinc, Calcium, Iron
1090, 1178, 1175, 1162, # Magnesium, Vit B12, Vit B6, Vit C

# SC
1099, 1180, 1190, # Fluoride, Choline, Folate DFE
1101, 1103, 1098, # Manganese, Selenium, Copper
1165, 1166, 1167, 1170, # Thiamin, Riboflavin, Niacin, Pantothenic acid
1114, 1109, 1185, 2000, # Vit D, Vit E, Vit K, Sugars Total

]

filtered = df[df["nutrient_id"].isin(nutrient_ids)]


# ======================
# SAVE
# ======================

os.makedirs("A. Data/Data Processed", exist_ok=True)

filtered.to_csv(
    "A. Data/Data Processed/01_hc_sc_filtered.csv",
    index=False
)

print("Dataset HC+SC disimpan.")
print(filtered.shape)
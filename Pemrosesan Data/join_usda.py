import pandas as pd
import os

# ======================
# LOAD DATA
# ======================

food = pd.read_csv("Data Raw/food.csv")
nutrient = pd.read_csv("Data Raw/nutrient.csv")
food_nutrient = pd.read_csv("Data Raw/food_nutrient.csv")
food_category = pd.read_csv("Data Raw/food_category.csv")

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
1003,1004,1005,1008,1051,
1079,1087,1089,1090,1091,
1092,1093,1095,
1106,1114,1109,
1162,1178,1175,
1253,1258,
2000,

# SC
1176,1099,1190,1180,
1101,1103,1098,
1165,1166,1167,1170,
1185
]

filtered = df[df["nutrient_id"].isin(nutrient_ids)]


# ======================
# SAVE
# ======================

os.makedirs("Data Processed", exist_ok=True)

filtered.to_csv(
    "Data Processed/hc_sc_filtered.csv",
    index=False
)

print("Dataset HC+SC disimpan.")
print(filtered.shape)
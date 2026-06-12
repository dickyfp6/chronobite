from nutrition_service import NutritionService

service = NutritionService()
result = service.calculate_nutrition_needs({
    'gender': 'M', 'age': 45, 'weight': 70, 'height': 175,
    'activity_factor': 1.4, 'disease': ['ckd'],
    'food_preferences': []
})

food_df = result['food_data']['dataframe']

print(f"Total items: {len(food_df)}")
print(f"\nKolom tersedia: {list(food_df.columns)}")

if 'consumption_label' in food_df.columns:
    print(f"\nPer consumption_label:")
    print(food_df['consumption_label'].value_counts())

if 'calcium_mg' in food_df.columns and 'phosphorus_mg' in food_df.columns:
    feasible = food_df[
        (food_df['calcium_mg'] >= 800/10) &
        (food_df['phosphorus_mg'] <= 1000/10)
    ]
    print(f"\nItem feasible calcium+phosphorus (estimasi): {len(feasible)}")
    if 'consumption_label' in food_df.columns:
        print(f"Per consumption_label:")
        print(feasible['consumption_label'].value_counts())
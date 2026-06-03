import sys
sys.path.insert(0, 'D. Model')

from candidate_generator import CandidateGenerator

# Test the extract_main_ingredients function
test_foods = [
    "Tortillas, ready-to-bake or -fry, flour, shelf stable",
    "Sweet Potatoes, french fried, frozen as packaged, salt added in processing",
    "Beverages, ABBOTT, ENSURE PLUS, ready-to-drink",
    "Bagels, wheat",
    "Vital wheat gluten",
    "Bread, white wheat",
    "DENNY'S, chicken nuggets, star shaped, from kid's menu",
]

print("Testing extract_main_ingredients:")
for food in test_foods:
    ingredient = CandidateGenerator.extract_main_ingredients(food)
    print(f"  '{food}' -> '{ingredient}'")

print("\nTesting is_similar_ingredient:")
pairs = [
    ("Tortillas, ready-to-bake or -fry, flour, shelf stable", "Beverages, ABBOTT, ENSURE PLUS, ready-to-drink"),
    ("Bagels, wheat", "Beverages, ABBOTT, ENSURE PLUS, ready-to-drink"),
    ("Vital wheat gluten", "Beverages, ABBOTT, ENSURE PLUS, ready-to-drink"),
    ("DENNY'S, chicken nuggets, star shaped, from kid's menu", "Beverages, ABBOTT, ENSURE PLUS, ready-to-drink"),
]

for food1, food2 in pairs:
    similar = CandidateGenerator.is_similar_ingredient(food1, food2)
    ing1 = CandidateGenerator.extract_main_ingredients(food1)
    ing2 = CandidateGenerator.extract_main_ingredients(food2)
    print(f"  '{ing1}' vs '{ing2}' -> {similar}")

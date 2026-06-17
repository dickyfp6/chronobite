import sys
import os
import pandas as pd

# Add paths
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'C. System Flow')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'D. Model')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'D. Model', 'Genetic Algorithm')))

from nutrition_service import NutritionService
from ga_interface import GeneticAlgorithmInterface

# Initialize
ns = NutritionService()
user_input = {
    'gender': 'M',
    'age': 25,
    'weight': 70,
    'height': 170,
    'activity_factor': 1.55,
    'disease': ['normal'],
    'food_preferences': ['Asian', 'Western']
}

print("Calculating nutrition needs...")
res = ns.calculate_nutrition_needs(user_input)
tdee = res['energy']['tdee']
guidelines = res['guidelines']
food_df = ns.guideline_loader.food_df

print("Initializing GA interface...")
ga = GeneticAlgorithmInterface(food_df, guidelines)

print("Running GA generation...")
import time
start = time.time()
menu_plan = ga.generate_menu_plan(user_input, tdee, deadline=start + 150.0)

if menu_plan:
    print("Success! Best fitness:", menu_plan.best_fitness_score)
else:
    print("Failed to generate menu plan")

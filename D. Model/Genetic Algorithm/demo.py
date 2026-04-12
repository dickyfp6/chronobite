"""
INTERACTIVE DEMO - Hybrid GA+LS Meal Planning System

Cara pakai:
1. Run: python demo.py
2. Input user profile (age, weight, height, etc)
3. System generates 9-meal day plan (3 meals + snacks with GA/LS/Hybrid)
"""

import sys
import os
import time
import pandas as pd
from typing import Dict, Any

# Add path to NutritionService
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../C. System Flow'))

from nutrition_service import NutritionService
from ga_main import run_genetic_algorithm
from ls_main import run_local_search


def get_user_input_interactive() -> Dict[str, Any]:
    """Get user input from terminal interactively"""
    print("\n" + "="*70)
    print("MEAL PLANNING SYSTEM - USER PROFILE INPUT")
    print("="*70 + "\n")
    
    print("Enter your profile data:\n")
    
    try:
        gender = input("Gender (M/F): ").strip().upper()
        if gender not in ['M', 'F']:
            gender = 'M'
        
        age = int(input("Age (years): "))
        weight = float(input("Weight (kg): "))
        height = float(input("Height (cm): "))
        
        while True:
            activity = float(input("Activity factor (1.4-2.2, default 1.55): ") or "1.55")
            if 1.4 <= activity <= 2.2:
                break
            print("  ❌ Invalid! Must be 1.4-2.2. Try again...")
        
        disease = input("Health condition (dm2, hypertension, normal - default 'normal'): ").strip().lower()
        if disease not in ['dm2', 'hypertension', 'normal']:
            disease = 'normal'
        
        return {
            'gender': gender,
            'age': age,
            'weight': weight,
            'height': height,
            'activity_factor': activity,
            'disease': disease,
            'food_preferences': ['Indonesian', 'Asian']
        }
    except ValueError as e:
        print(f"❌ Invalid input: {e}")
        print("Using default profile instead...")
        return {
            'gender': 'M',
            'age': 30,
            'weight': 70.0,
            'height': 175.0,
            'activity_factor': 1.55,
            'disease': 'dm2',
            'food_preferences': ['Indonesian', 'Asian']
        }


def format_meal_name(text):
    """Format food item name for display"""
    if isinstance(text, str):
        return text[:50] if len(text) > 50 else text
    return "Unknown"


def display_meal_plan(result: Dict[str, Any], food_df: pd.DataFrame, meal_name: str):
    """Display the generated meal plan"""
    print("\n" + "="*70)
    print(f"{meal_name.upper()}")
    print("="*70)
    
    meal_plan = result.get('meal_plan', {})
    
    for time_period in ['breakfast', 'lunch', 'dinner', 'snack']:
        meal = meal_plan.get(time_period, {})
        budget = meal.get('budget_kcal', 0)
        selected = meal.get('selected', {})
        
        print(f"\n🍽️ {time_period.upper():<12} (Budget: {budget:.0f} kcal)")
        
        if isinstance(selected, dict):
            # Breakfast, lunch, dinner format
            for role, fdc_id in selected.items():
                if fdc_id is not None:
                    # Look up food name
                    try:
                        match = food_df[food_df['fdc_id'] == int(fdc_id)]
                        if not match.empty:
                            name = match.iloc[0].get('description', f'Item {fdc_id}')
                            kcal = match.iloc[0].get('energy_kcal', 0)
                            print(f"   • {format_meal_name(name):<45} ({kcal:>6.0f} kcal) [{role}]")
                        else:
                            print(f"   • Item {fdc_id:<41} [{role}]")
                    except:
                        print(f"   • Item {fdc_id:<41} [{role}]")
        elif isinstance(selected, int):
            # Snack format
            try:
                match = food_df[food_df['fdc_id'] == selected]
                if not match.empty:
                    name = match.iloc[0].get('description', f'Item {selected}')
                    kcal = match.iloc[0].get('energy_kcal', 0)
                    print(f"   • {format_meal_name(name):<45} ({kcal:>6.0f} kcal)")
                else:
                    print(f"   • Item {selected}")
            except:
                print(f"   • Item {selected}")
    
    print("\n" + "="*70)


def display_results(results: Dict[str, Any], food_df: pd.DataFrame):
    """Display comparison and best result"""
    print("\n" + "="*70)
    print("ALGORITHM COMPARISON")
    print("="*70)
    
    print(f"{'Algorithm':<20} {'Fitness':<15} {'Time (s)':<12} {'Feasible':<10}")
    print("-"*70)
    
    best_algo = None
    best_fitness = float('-inf')
    
    for algo_name, result in results.items():
        summary = result.get('summary', {})
        fitness = summary.get('fitness_score', 0)
        exec_time = summary.get('execution_time', 0)
        feasible = "✓" if summary.get('feasible', False) else "✗"
        
        print(f"{algo_name:<20} {fitness:>14.1f} {exec_time:>11.2f} {feasible:>9}")
        
        if fitness > best_fitness:
            best_fitness = fitness
            best_algo = algo_name
    
    print("-"*70)
    if best_algo:
        print(f"\n🏆 BEST RESULT: {best_algo} (Fitness: {best_fitness:.1f})")
        display_meal_plan(results[best_algo], food_df, f"Recommended Meal Plan ({best_algo})")


def main():
    """Main demo"""
    print("\n" + "#"*70)
    print("# HYBRID GA+LS MEAL PLANNING SYSTEM")
    print("#"*70)
    
    # 1. Get user input
    user_input = get_user_input_interactive()
    
    print("\n✓ User Profile Loaded:")
    print(f"  • Gender: {user_input['gender']}")
    print(f"  • Age: {user_input['age']}")
    print(f"  • Weight: {user_input['weight']} kg")
    print(f"  • Height: {user_input['height']} cm")
    print(f"  • Activity: {user_input['activity_factor']}")
    print(f"  • Condition: {user_input['disease']}")
    
    # 2. Initialize NutritionService
    print("\n2. Loading nutrition data...")
    service = NutritionService()
    result = service.calculate_nutrition_needs(user_input)
    
    if not result['success']:
        print(f"❌ Error: {result.get('error', 'Unknown')}")
        return
    
    food_df = result.get('food_data', {}).get('dataframe')
    tdee = result.get('energy', {}).get('tdee', 2000)
    
    # Calculate meal budgets from TDEE
    meal_budgets = {
        'breakfast': round(tdee * 0.2375, 2),
        'lunch': round(tdee * 0.3375, 2),
        'dinner': round(tdee * 0.2875, 2),
        'snack': round(tdee * 0.1375, 2)
    }
    
    user_constraints = {
        'age': user_input['age'],
        'gender': user_input['gender'],
        'disease': user_input['disease'],
        'tdee': tdee
    }
    
    print(f"\n✓ Nutrition Data Loaded:")
    print(f"  • TDEE: {tdee:.0f} kcal/day")
    print(f"  • Breakfast: {meal_budgets['breakfast']:.0f} kcal")
    print(f"  • Lunch: {meal_budgets['lunch']:.0f} kcal")
    print(f"  • Dinner: {meal_budgets['dinner']:.0f} kcal")
    print(f"  • Snack: {meal_budgets['snack']:.0f} kcal")
    print(f"  • Food items: {len(food_df)}")
    
    # 3. Run algorithms
    print("\n" + "="*70)
    print("RUNNING ALGORITHMS")
    print("="*70)
    
    results = {}
    
    # GA
    print("\n▶ Genetic Algorithm (GA) Only...")
    try:
        start_time = time.time()
        ga_result = run_genetic_algorithm(
            food_df=food_df,
            user_constraints=user_constraints,
            meal_budgets=meal_budgets,
            tdee=tdee,
            pop_size=20,
            generations=10,
            crossover_rate=0.8,
            mutation_rate=0.2,
            verbose=False
        )
        ga_result['summary']['execution_time'] = time.time() - start_time
        results['GA'] = ga_result
        print(f"  ✓ Completed (Fitness: {ga_result['summary']['fitness_score']:.1f})")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    # LS
    print("\n▶ Local Search (LS) Only...")
    try:
        start_time = time.time()
        ls_result = run_local_search(
            food_df=food_df,
            user_constraints=user_constraints,
            meal_budgets=meal_budgets,
            tdee=tdee,
            strategy='hill_climbing',
            max_iterations=20
        )
        ls_result['summary']['execution_time'] = time.time() - start_time
        results['LS'] = ls_result
        print(f"  ✓ Completed (Fitness: {ls_result['summary']['fitness_score']:.1f})")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    # Display results
    if results:
        display_results(results, food_df)
    
    print("\n" + "#"*70)
    print("# DEMO COMPLETED")
    print("#"*70 + "\n")


if __name__ == '__main__':
    main()
"""
Demo & Benchmarking Script

Test GA, LS, dan Hybrid dengan actual input dari NutritionService
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
import sys
import os
import time

# Add parent paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../C. System Flow'))

# Import algorithms
from ga_main import run_genetic_algorithm
from ls_main import run_local_search
from hybrid_algorithm import run_hybrid_algorithm
from validator import print_validation_report
from nutrition_service import NutritionService


def create_sample_user_input() -> Dict[str, Any]:
    """
    Get user profile dari terminal interaktif
    """
    print("\n" + "="*70)
    print("MASUKKAN PROFIL ANDA")
    print("="*70)
    
    try:
        gender = input("\nJenis Kelamin (M/F): ").strip().upper()
        if gender not in ['M', 'F']:
            gender = 'M'
            
        age = int(input("Umur (tahun): "))
        weight = float(input("Berat Badan (kg): "))
        height = float(input("Tinggi Badan (cm): "))
        
        print("\nAktivitas Fisik:")
        print("  1. Sedentary (Tidak aktif)")
        print("  2. Lightly Active (Ringan)")
        print("  3. Moderately Active (Sedang)")
        print("  4. Very Active (Tinggi)")
        activity_choice = input("Pilih (1-4) [default: 3]: ").strip()
        activity_map = {'1': 1.2, '2': 1.375, '3': 1.55, '4': 1.725}
        activity_factor = activity_map.get(activity_choice, 1.55)
        
        print("\nKondisi Kesehatan:")
        print("  1. Diabetes Type 2")
        print("  2. Hipertensi")
        print("  3. Normal")
        disease_choice = input("Pilih (1-3) [default: 1]: ").strip()
        disease_map = {'1': 'dm2', '2': 'hypertension', '3': 'normal'}
        disease = disease_map.get(disease_choice, 'dm2')
        
        preferences = input("\nPilihan Makanan (comma-separated, e.g. Indonesian,Asian) [default: Indonesian,Asian]: ").strip()
        if not preferences:
            preferences = "Indonesian,Asian"
        food_preferences = [p.strip() for p in preferences.split(',')]
        
    except ValueError:
        print("\n⚠️ Input tidak valid, menggunakan default...")
        return {
            'gender': 'M',
            'age': 30,
            'weight': 70.0,
            'height': 175.0,
            'activity_factor': 1.55,
            'disease': 'dm2',
            'food_preferences': ['Indonesian', 'Asian']
        }
    
    return {
        'gender': gender,
        'age': age,
        'weight': weight,
        'height': height,
        'activity_factor': activity_factor,
        'disease': disease,
        'food_preferences': food_preferences
    }


def get_nutrition_data() -> Dict[str, Any]:
    """
    Get proper nutrition data dari NutritionService dengan user input interaktif
    
    Returns:
        {
            'food_df': DataFrame,
            'meal_budgets': Dict,
            'user_constraints': Dict,
            'tdee': float,
            'guidelines': Dict
        }
    """
    print("\n1. Initializing NutritionService...")
    service = NutritionService()
    
    print("2. Accepting user input...")
    user_input = create_sample_user_input()
    
    print("\n3. Calculating nutrition needs...")
    result = service.calculate_nutrition_needs(user_input)
    
    if not result['success']:
        print(f"❌ Error: {result.get('error', 'Unknown error')}")
        return None
    
    # Extract hasil
    food_df = result.get('food_data', {}).get('dataframe')
    guidelines = result.get('guidelines', {}).get('nutrients', {})
    
    # Calculate meal budgets
    tdee = result.get('energy', {}).get('tdee', 2000)
    meal_budgets = {
        'breakfast': round(tdee * 0.2375, 2),
        'lunch': round(tdee * 0.3375, 2),
        'dinner': round(tdee * 0.2875, 2),
        'snack': round(tdee * 0.1375, 2)
    }
    
    user_constraints = {
        'age': user_input.get('age'),
        'gender': user_input.get('gender'),
        'disease': user_input.get('disease'),
        'food_preferences': user_input.get('food_preferences', []),
        'tdee': tdee
    }
    
    print(f"\n✓ Profil Anda Berhasil Disimpan:")
    print(f"  • TDEE: {tdee:.0f} kcal/hari")
    print(f"  • Sarapan: {meal_budgets['breakfast']:.0f} kcal")
    print(f"  • Makan Siang: {meal_budgets['lunch']:.0f} kcal")
    print(f"  • Makan Malam: {meal_budgets['dinner']:.0f} kcal")
    print(f"  • Snack: {meal_budgets['snack']:.0f} kcal")
    print(f"  • Total Makanan: {len(food_df)}")
    print(f"  • Panduan Nutrisi: {len(guidelines)}")
    
    return {
        'food_df': food_df,
        'meal_budgets': meal_budgets,
        'user_constraints': user_constraints,
        'tdee': tdee,
        'guidelines': guidelines
    }


def print_meal_plan(meal_plan: Dict[str, Any], food_df: pd.DataFrame, title: str = "MEAL PLAN"):
    """Pretty print meal plan"""
    print("\n" + "="*70)
    print(title)
    print("="*70)
    
    def get_food_name_and_kcal(fdc_id):
        """Get food name and kcal from food_df"""
        if isinstance(fdc_id, int):
            match = food_df[food_df['fdc_id'] == fdc_id]
            if not match.empty:
                name = match.iloc[0].get('description', 'Unknown')
                kcal = match.iloc[0].get('energy_kcal', 0)
                return name, kcal
        return 'Unknown', 0
    
    for meal_name in ['breakfast', 'lunch', 'dinner', 'snack']:
        meal = meal_plan.get(meal_name, {})
        selected = meal.get('selected', {})
        budget = meal.get('budget_kcal', 0)
        
        print(f"\n{meal_name.upper()}")
        print(f"  Budget: {budget:.0f} kcal")
        
        if isinstance(selected, dict):
            for role, item_id in selected.items():
                if item_id:
                    name, kcal = get_food_name_and_kcal(item_id)
                    print(f"    • {name} ({kcal:.0f} kcal) [{role}]")
        elif isinstance(selected, int):
            name, kcal = get_food_name_and_kcal(selected)
            print(f"    • {name} ({kcal:.0f} kcal)")
        elif isinstance(selected, list):
            for item_id in selected:
                name, kcal = get_food_name_and_kcal(item_id)
                print(f"    • {name} ({kcal:.0f} kcal)")
    
    print("="*70)


def compare_results(results: Dict[str, Dict[str, Any]]):
    """Compare GA vs LS vs Hybrid"""
    print("\n" + "="*70)
    print("COMPARISON TABLE")
    print("="*70)
    
    # Header
    print(f"{'Algorithm':<25} {'Fitness':<15} {'Time (s)':<15} {'Feasible':<10} {'Violations':<10}")
    print("-"*70)
    
    # Rows
    for algo_name, result in results.items():
        summary = result.get('summary', {})
        fitness = summary.get('fitness_score', 0)
        exec_time = summary.get('execution_time', 0)
        feasible = "✓" if summary.get('feasible', False) else "✗"
        violations = summary.get('violations', 0)
        
        print(f"{algo_name:<25} {fitness:>14.1f} {exec_time:>14.2f} {feasible:>9} {violations:>10}")
    
    print("="*70)
    
    # Find best
    if results:
        best_name = max(results.keys(), key=lambda x: results[x].get('summary', {}).get('fitness_score', 0))
        best_fitness = results[best_name]['summary']['fitness_score']
        print(f"\nBest: {best_name} with fitness {best_fitness:.1f}")


def main():
    """Main demo"""
    print("\n" + "#"*70)
    print("# HYBRID GA+LS MEAL PLANNING SYSTEM - DEMO")
    print("#"*70)
    
    # Get nutrition data dari NutritionService
    nutrition_data = get_nutrition_data()
    
    if nutrition_data is None:
        print("❌ Failed to load nutrition data!")
        return
    
    food_df = nutrition_data['food_df']
    meal_budgets = nutrition_data['meal_budgets']
    user_constraints = nutrition_data['user_constraints']
    
    # Run algorithms
    results = {}
    
    print("\n" + "="*70)
    print("RUNNING ALGORITHMS")
    print("="*70)
    
    # 1. GA Only
    print("\n" + "-"*70)
    print("1. GENETIC ALGORITHM Only")
    print("-"*70)
    try:
        start_time = time.time()
        ga_result = run_genetic_algorithm(
            food_df=food_df,
            user_constraints=user_constraints,
            meal_budgets=meal_budgets,
            tdee=nutrition_data['tdee'],
            pop_size=10,
            generations=5,
            crossover_rate=0.8,
            mutation_rate=0.2
        )
        ga_result['summary']['execution_time'] = time.time() - start_time
        results['GA'] = ga_result
        print("✓ GA completed successfully")
    except Exception as e:
        print(f"✗ GA Error: {e}")
        import traceback
        traceback.print_exc()
    
    # 2. LS Only
    print("\n" + "-"*70)
    print("2. LOCAL SEARCH Only (Hill Climbing)")
    print("-"*70)
    try:
        start_time = time.time()
        ls_result = run_local_search(
            food_df=food_df,
            user_constraints=user_constraints,
            meal_budgets=meal_budgets,
            tdee=nutrition_data['tdee'],
            strategy='hill_climbing',
            max_iterations=15
        )
        ls_result['summary']['execution_time'] = time.time() - start_time
        results['LS'] = ls_result
        print("✓ LS completed successfully")
    except Exception as e:
        print(f"✗ LS Error: {e}")
        import traceback
        traceback.print_exc()
    
    # 3. Hybrid
    print("\n" + "-"*70)
    print("3. HYBRID (GA + LS per Generation)")
    print("-"*70)
    try:
        start_time = time.time()
        hybrid_result = run_hybrid_algorithm(
            food_df=food_df,
            user_constraints=user_constraints,
            meal_budgets=meal_budgets,
            tdee=nutrition_data['tdee'],
            pop_size=10,
            ga_generations=5,
            crossover_rate=0.8,
            mutation_rate=0.2,
            ls_strategy='hill_climbing',
            ls_iterations=2
        )
        hybrid_result['summary']['execution_time'] = time.time() - start_time
        results['Hybrid'] = hybrid_result
        print("✓ Hybrid completed successfully")
    except Exception as e:
        print(f"✗ Hybrid Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Comparison
    if results:
        compare_results(results)
        
        # Show first successful meal plan
        for algo_name, result in results.items():
            if 'meal_plan' in result:
                print_meal_plan(result['meal_plan'], food_df, f"{algo_name.upper()} MEAL PLAN")
                break
    
    print("\n" + "#"*70)
    print("# DEMO COMPLETED")
    print("#"*70 + "\n")


if __name__ == '__main__':
    main()

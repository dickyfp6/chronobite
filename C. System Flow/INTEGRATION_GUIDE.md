"""
Integration Guide: Genetic Algorithm & Greedy Algorithm
Bagaimana cara meng-integrate GA dan Greedy dengan NutritionService

=============================================================================
MULTIPLE DISEASE MERGE
=============================================================================

NutritionService SEKARANG support MULTIPLE DISEASE selection dengan merge logic:

Jika user punya 2+ diseases, guideline merges dengan:
  - min value: MAXIMUM dari semua diseases (most restrictive)
  - max value: MINIMUM dari semua diseases (most restrictive)

Contoh: DM2 + Hypertension
  DM2 energy: 1800-2200
  Hypertension energy: 1995-2205
  → Merged: 1995-2200 (max dari 1800 vs 1995, min dari 2200 vs 2205)

Kenapa ini logic? Agar user yang punya multiple conditions dapat:
  - Memenuhi MINIMUM requirement yang paling ketat (kesehatan optimal)
  - Tetap memiliki batas maksimal yang tidak terlalu lebar (safety)
  - Range makin SEMPIT = LEBIH AMAN untuk multiple conditions

=============================================================================
DRI MICRONUTRIENT FALLBACK LOGIC
=============================================================================

NutritionService menggunakan strategy "Guideline Override with DRI Fallback":

1. For NORMAL disease:
   - Gunakan DRI micronutrient lengkap sebagai constraint

2. For SICK patients (dm2, hypertension, etc):
   - Load guideline specifik untuk disease tersebut (atau merged jika multiple)
   - Jika nutrient ada di guideline → gunakan guideline value
   - Jika nutrient TIDAK ada di guideline → fallback ke DRI micronutrient
   - Result: Merged constraints = disease guideline + DRI fallback

Example hasil merge untuk DM2:
{
    'energy_kcal': {
        'min': 1800.0,
        'max': 2200.0,
        'basis': '1',
        'constraint_type': 'absolute',
        'source': 'guideline',  # ← dari DM2 guideline
        'diseases': ['dm2']
    },
    'vitamin_d_mg': {
        'min': 15.0,
        'max': 15.0,
        'basis': 'DRI',
        'constraint_type': 'dri_micronutrient',
        'source': 'DRI fallback'  # ← tidak ada di DM2 guideline, ambil DRI
    }
}

=============================================================================
QUICK START
=============================================================================

# Step 1: Import service
from nutrition_service import NutritionService

# Step 2: Initialize service
service = NutritionService()

# Step 3: Get user data (disease dapat string ATAU list)
user_input = {
    'gender': 'M',
    'age': 25,
    'weight': 70,
    'height': 175,
    'activity_factor': 1.55,
    'disease': ['dm2', 'hypertension'],  # ← Multiple diseases! (atau string 'dm2' untuk single)
    'food_preferences': ['Western', 'Asian', 'Mediterranean', 'Generic']  # ← Multiple preferences!
}

# Step 4: Calculate nutrition needs (include DRI fallback + multi-disease merge!)
result = service.calculate_nutrition_needs(user_input)

# Step 5: Extract data untuk algorithm
if result['success']:
    guidelines = result['guidelines']['nutrients']       # Dicampur guideline + DRI
    food_data = result['food_data']['dataframe']         # Candidate items
    user_params = result['user_params']                  # User parameters
    
    # Now pass ke GA atau Greedy
    # solution = genetic_algorithm(food_data, guidelines, user_params)
    # solution = greedy_algorithm(food_data, guidelines, user_params)
else:
    print(f"Error: {result['error']}")

=============================================================================
DATA STRUCTURE
=============================================================================

Result['guidelines']['nutrients']:
{
    'energy_kcal': {
        'min': 1800.0,                  # Minimum daily energy
        'max': 2205.0,                  # Maximum daily energy (merged from multiple diseases)
        'basis': '1',                   # Basis type (1=absolute, TDEE, BB, BBI, DRI)
        'constraint_type': 'absolute',  # How to interpret the value
        'unit': 'kcal',
        'source': 'guideline',          # ← Indicator dari mana constraint: 'guideline' atau 'DRI fallback'
        'diseases': ['dm2', 'hypertension']  # ← NEW: Track which diseases contributed (untuk multiple diseases)
    },
    'carbohydrate_g': {
        'min': 998.75,                  # Merged: min dari DM2 vs Hypertension
        'max': 1445.56,                 # Merged: max dari DM2 vs Hypertension
        'basis': 'TDEE',
        'constraint_type': 'tdee_based',
        'unit': 'g',
        'source': 'guideline',
        'diseases': ['dm2', 'hypertension']
    },
    'vitamin_d_mg': {
        'min': 15.0,
        'max': 15.0,
        'basis': 'DRI',
        'constraint_type': 'dri_micronutrient',
        'unit': 'mg',
        'source': 'DRI fallback'  # ← Dari DRI fallback karena tidak ada di disease guideline
    },
    ...
}

Result['food_data']:
{
    'total_items': 4425,                        # Total food items in database
    'filtered_items': 1200,                     # Items sesuai user preference
    'by_cuisine': {'Western': 2000, ...},       # Distribution by cuisine
    'preferences': ['Western', 'Asian'],        # User-selected food preferences (now multiple!)
    'dataframe': <pd.DataFrame>                 # Food data dengan nutrients
}

Result['user_params']:
{
    'tdee': 2672.28,                # Daily energy expenditure
    'weight': 70,                   # Body weight
    'bbi': 67.5,                    # Ideal body weight
    'energy_target': 2672.28,       # Target energy
    'age': 25,
    'gender': 'M',
    'disease': ['dm2', 'hypertension']  # ← Now LIST untuk support multiple diseases!
}

=============================================================================
EXAMPLE: GENETIC ALGORITHM INTEGRATION
=============================================================================

from nutrition_service import NutritionService
from genetic_algorithm import GeneticAlgorithm  # Your GA implementation

def optimize_menu_with_ga(user_input, ga_params=None):
    # Step 1: Get nutrition needs (with DRI fallback!)
    service = NutritionService()
    result = service.calculate_nutrition_needs(user_input)
    
    if not result['success']:
        return None
    
    # Step 2: Extract constraints & data (sudah merged)
    guidelines = result['guidelines']['nutrients']
    food_data = result['food_data']['dataframe']
    user_params = result['user_params']
    
    # Step 3: Initialize GA with default params
    if ga_params is None:
        ga_params = {
            'population_size': 100,
            'generations': 500,
            'mutation_rate': 0.1,
            'crossover_rate': 0.8,
            'meals_per_day': 3  # Breakfast, lunch, dinner
        }
    
    # Step 4: Run GA
    ga = GeneticAlgorithm(
        food_data=food_data,
        guidelines=guidelines,      # Sudah include DRI fallback!
        user_params=user_params,
        **ga_params
    )
    
    best_menu, fitness_history = ga.optimize()
    
    # Step 5: Return solution
    return {
        'user_input': user_input,
        'best_menu': best_menu,
        'guidelines_met': validate_menu(best_menu, guidelines),
        'fitness_history': fitness_history
    }


def validate_menu(menu_items, guidelines):
    \"\"\"Validate menu terhadap guidelines\"\"\"
    # Sum nutrisi dari menu items
    # Compare dengan guidelines min-max
    # Return validation result
    pass

=============================================================================
EXAMPLE: GREEDY ALGORITHM INTEGRATION
=============================================================================

from nutrition_service import NutritionService
from greedy_algorithm import GreedyAlgorithm

def optimize_menu_with_greedy(user_input):
    # Step 1: Get nutrition needs (with DRI fallback!)
    service = NutritionService()
    result = service.calculate_nutrition_needs(user_input)
    
    if not result['success']:
        return None
    
    # Step 2: Extract constraints & data (sudah merged)
    guidelines = result['guidelines']['nutrients']
    food_data = result['food_data']['dataframe']
    user_params = result['user_params']
    
    # Step 3: Run Greedy
    greedy = GreedyAlgorithm(
        food_data=food_data,
        guidelines=guidelines,      # Sudah include DRI fallback!
        user_params=user_params
    )
    
    menu = greedy.build_menu()
    
    # Step 4: Return solution
    return {
        'user_input': user_input,
        'menu': menu,
        'guidelines_met': validate_menu(menu, guidelines)
    }

=============================================================================
KEY POINTS FOR ALGORITHM IMPLEMENTATION
=============================================================================

1. FOOD DATA FORMAT
   - Each row represents one food item
   - Columns: fdc_id, food_name, energy, protein_g, carb_g, fat_g, ...
   - Nutrient columns must match guideline keys
   - Example: 
     - Guideline uses 'carbohydrate_g', food_df must have 'Carbohydrate, by difference'
     - Need mapping function to normalize column names

2. GUIDELINES CONSTRAINTS (now with DRI)
   - Min-max constraints harus di-check
   - Check 'source' key: 'guideline' vs 'DRI fallback'
   - Some constraints punya basis (TDEE-based sudah di-convert)
   - 'unlimited' constraints ignore
   - DRI constraints: min==max (fixed value, bukan range)

3. DRI vs GUIDELINE CONSTRAINTS
   - Guideline constraints: punya min dan max range (flexible)
   - DRI constraints: min == max (fixed target)
   - Both types ada di guidelines dictionary
   - Treat DRI as "target ≈ min = max"

4. MEAL STRUCTURE
   - Typical: 1 day = 3 meals (breakfast, lunch, dinner) OR 3-6 meals
   - Each meal = 1+ food items
   - Calculate total nutrisi per day
   - Compare dengan daily guidelines (merged constraints)

5. FITNESS/OBJECTIVE FUNCTION
   - Minimize deviation dari guideline range
   - For DRI constraints: exact match atau minimal deviation
   - Maximize food variety/preference
   - Consider cuisine preference
   - Consider sensibility (realistic meals)

6. CONSTRAINTS
   - Energy target: energy_kcal min-max
   - Macro nutrients: carb, protein, fat
   - Micro nutrients: from merged constraints (guideline + DRI)
   - Optional: Cost, availability

=============================================================================
COMMON ISSUES & SOLUTIONS
=============================================================================

Issue 1: Column name mismatch
Solution: Normalize food_df columns dengan guideline keys
          Create mapping dict: 'protein_g' -> 'Protein' atau 'protein, total' dll

Issue 2: Missing nutrient values
Solution: Handle NaN dengan default (0) atau exclude from constraint

Issue 3: Guidelines impossible to meet
Solution: Relax constraints, use weighted objective function

Issue 4: DRI vs Guideline priority
Solution: Check 'source' key - prioritize guideline over DRI if conflicts
          Usually guideline > DRI karena lebih specific untuk disease

Issue 5: Too many constraints
Solution: Create constraint priority levels
          - Critical: energy, macro (must meet)
          - Important: key micros (should meet)
          - Optional: other micros (nice-to-have)

=============================================================================
TESTING YOUR INTEGRATION
=============================================================================

    from nutrition_service import NutritionService
    
    service = NutritionService()
    
    # Test 1: Simple input with DRI
    result = service.calculate_nutrition_needs({
        'gender': 'M',
        'age': 25,
        'weight': 70,
        'height': 175,
        'activity_factor': 1.55,
        'disease': 'dm2',
        'food_preferences': []
    })
    
    assert result['success']
    assert 'guidelines' in result
    assert 'food_data' in result
    
    # Test 2: Verify guideline + DRI merge
    guidelines = result['guidelines']['nutrients']
    food_data = result['food_data']['dataframe']
    
    print(f"Total guidelines: {len(guidelines)} nutrients")
    print(f"Food items: {len(food_data)} items")
    
    # Count by source
    guideline_count = sum(1 for c in guidelines.values() if c.get('source') != 'DRI fallback')
    dri_count = sum(1 for c in guidelines.values() if c.get('source') == 'DRI fallback')
    
    print(f"  - From guideline: {guideline_count}")
    print(f"  - From DRI fallback: {dri_count}")
    
    # Test 3: Check specific constraint
    energy = guidelines['energy_kcal']
    print(f"Energy target: {energy['min']} - {energy['max']} {energy['unit']}")

=============================================================================
"""

Result['food_data']:
{
    'total_items': 4425,                    # Total food items in database
    'filtered_items': 1200,                 # Items sesuai preference
    'by_cuisine': {'Western': 2000, ...},   # Distribution
    'preferences': ['Western', 'Asian'],    # User preferences
    'dataframe': <pd.DataFrame>             # Food data dengan nutrients
}

Result['user_params']:
{
    'tdee': 2672.28,        # Daily energy expenditure
    'weight': 70,           # Body weight
    'bbi': 67.5,           # Ideal body weight
    'energy_target': 2672.28,  # Target energy
    'age': 25,
    'gender': 'M',
    'disease': 'dm2'
}

=============================================================================
EXAMPLE: GENETIC ALGORITHM INTEGRATION
=============================================================================

from nutrition_service import NutritionService
from genetic_algorithm import GeneticAlgorithm  # Your GA implementation

def optimize_menu_with_ga(user_input, ga_params=None):
    # Step 1: Get nutrition needs
    service = NutritionService()
    result = service.calculate_nutrition_needs(user_input)
    
    if not result['success']:
        return None
    
    # Step 2: Extract constraints & data
    guidelines = result['guidelines']['nutrients']
    food_data = result['food_data']['dataframe']
    user_params = result['user_params']
    
    # Step 3: Initialize GA with default params
    if ga_params is None:
        ga_params = {
            'population_size': 100,
            'generations': 500,
            'mutation_rate': 0.1,
            'crossover_rate': 0.8,
            'meals_per_day': 3  # Breakfast, lunch, dinner
        }
    
    # Step 4: Run GA
    ga = GeneticAlgorithm(
        food_data=food_data,
        guidelines=guidelines,
        user_params=user_params,
        **ga_params
    )
    
    best_menu, fitness_history = ga.optimize()
    
    # Step 5: Return solution
    return {
        'user_input': user_input,
        'best_menu': best_menu,
        'guidelines_met': validate_menu(best_menu, guidelines),
        'fitness_history': fitness_history
    }


def validate_menu(menu_items, guidelines):
    \"\"\"Validate menu terhadap guidelines\"\"\"
    # Sum nutrisi dari menu items
    # Compare dengan guidelines min-max
    # Return validation result
    pass

=============================================================================
EXAMPLE: GREEDY ALGORITHM INTEGRATION
=============================================================================

from nutrition_service import NutritionService
from greedy_algorithm import GreedyAlgorithm

def optimize_menu_with_greedy(user_input):
    # Step 1: Get nutrition needs
    service = NutritionService()
    result = service.calculate_nutrition_needs(user_input)
    
    if not result['success']:
        return None
    
    # Step 2: Extract constraints & data
    guidelines = result['guidelines']['nutrients']
    food_data = result['food_data']['dataframe']
    user_params = result['user_params']
    
    # Step 3: Run Greedy
    greedy = GreedyAlgorithm(
        food_data=food_data,
        guidelines=guidelines,
        user_params=user_params
    )
    
    menu = greedy.build_menu()
    
    # Step 4: Return solution
    return {
        'user_input': user_input,
        'menu': menu,
        'guidelines_met': validate_menu(menu, guidelines)
    }

=============================================================================
KEY POINTS FOR ALGORITHM IMPLEMENTATION
=============================================================================

1. FOOD DATA FORMAT
   - Each row represents one food item
   - Columns: fdc_id, food_name, energy, protein_g, carb_g, fat_g, ...
   - Nutrient columns must match guideline keys
   - Example: 
     - Guideline uses 'carbohydrate_g', food_df must have 'Carbohydrate, by difference'
     - Need mapping function to normalize column names

2. GUIDELINES CONSTRAINTS
   - Min-max constraints harus di-check
   - Some constraints punya basis (TDEE-based sudah di-convert)
   - 'unlimited' constraints ignore
   - Some nutrient penting (energy_kcal), some optional

3. MEAL STRUCTURE
   - Typical: 1 day = 3 meals (breakfast, lunch, dinner) OR 3-6 meals
   - Each meal = 1+ food items
   - Calculate total nutrisi per day
   - Compare dengan daily guidelines

4. FITNESS/OBJECTIVE FUNCTION
   - Minimize deviation dari guideline range
   - Maximize food variety/preference
   - Consider cuisine preference
   - Consider sensibility (realistic meals)

5. CONSTRAINTS
   - Energy target: energy_kcal min-max
   - Macro nutrients: carb, protein, fat
   - Micro nutrients: Ca, Fe, Vit C, etc.
   - Optional: Cost, availability

=============================================================================
COMMON ISSUES & SOLUTIONS
=============================================================================

Issue 1: Column name mismatch
Solution: Normalize food_df columns dengan guideline keys
          Create mapping dict: 'protein_g' -> 'Protein' atau 'protein, total' dll

Issue 2: Missing nutrient values
Solution: Handle NaN dengan default (0) atau exclude from constraint

Issue 3: Guidelines impossible to meet
Solution: Relax constraints, use weighted objective function

Issue 4: Female vs Male guidelines
Solution: NutritionService handles via gender parameter
          Some nutrients punya different requirements

=============================================================================
TESTING YOUR INTEGRATION
=============================================================================

    from nutrition_service import NutritionService
    
    service = NutritionService()
    
    # Test 1: Simple input
    result = service.calculate_nutrition_needs({
        'gender': 'M',
        'age': 25,
        'weight': 70,
        'height': 175,
        'activity_factor': 1.55,
        'disease': 'normal',
        'food_preferences': []
    })
    
    assert result['success']
    assert 'guidelines' in result
    assert 'food_data' in result
    
    # Test 2: Verify structure
    guidelines = result['guidelines']['nutrients']
    food_data = result['food_data']['dataframe']
    
    print(f"Guidelines: {len(guidelines)} nutrients")
    print(f"Food items: {len(food_data)} items")
    
    # Test 3: Check specific constraint
    energy = guidelines['energy_kcal']
    print(f"Energy target: {energy['min']} - {energy['max']} {energy['unit']}")

=============================================================================
"""

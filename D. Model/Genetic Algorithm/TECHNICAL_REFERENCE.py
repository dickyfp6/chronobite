"""
TECHNICAL REFERENCE: Category-Constrained GA System
Comprehensive technical documentation and architecture reference
"""

# ============================================================================
# SECTION 1: ARCHITECTURAL COMPARISON
# ============================================================================

OLD_SYSTEM_ARCHITECTURE = """
╔════════════════════════════════════════════════════════════════════════════╗
║                        OLD GA SYSTEM (BEFORE)                             ║
╚════════════════════════════════════════════════════════════════════════════╝

Chromosome Structure:
    {
        'breakfast': {food_id_1: portion, food_id_2: portion, ...},
        'lunch': {food_id_3: portion, food_id_4: portion, ...},
        ...
    }
    
Problem:
    ✗ No category info stored
    ✗ food_id_1 could be jam, fruit, or anything
    ✗ Mutation picks random food from ENTIRE database
    ✗ Result: Unrealistic menus despite high fitness

GA Population:
    [Chromosome1, Chromosome2, ..., Chromosome50]
    ↓ (arbitrary selection)
    Any food_id could be picked from database ~3920 foods

Fitness:
    ImprovedFitnessCalculator
    - 12 nutrients checked
    - Soft penalties
    - Doesn't validate category structure
    ✗ Result: "Optimal fitness" but unrealistic meal

Output:
    {
        'breakfast': {'Jam': portion, 'Banana': portion, ...},  ← WRONG!
        'lunch': {'Fruit': portion, ...},  ← WRONG!
    }
"""

NEW_SYSTEM_ARCHITECTURE = """
╔════════════════════════════════════════════════════════════════════════════╗
║                      NEW GA SYSTEM (AFTER)                                ║
╚════════════════════════════════════════════════════════════════════════════╝

Chromosome Structure (STRICT):
    {
        'breakfast': {
            'main_course': fdc_id_1,      ← Only main course here
            'side_dish': fdc_id_2,        ← Only side dish here
            'drink': fdc_id_3             ← Only drink here
        },
        'lunch': {
            'main_course': fdc_id_4,
            'side_dish': fdc_id_5,
            'drink': fdc_id_6
        },
        'dinner': {...},
        'snack': fdc_id_7                 ← Single snack
    }
    
Advantage:
    ✓ Category explicitly stored
    ✓ Each slot can only hold specific category
    ✓ fdc_id_1 MUST be in main_course pool
    ✓ Result: Structure enforces realism

Food Pools (Pre-filtered by Category):
    FoodCategoryManager creates:
    {
        'main_course': [fdc_id_101, fdc_id_401, ...],  ← ~500 items
        'side_dish': [fdc_id_201, fdc_id_501, ...],    ← ~600 items
        'drink': [fdc_id_301, fdc_id_304, ...],        ← ~50 items
        'snack': [fdc_id_601, fdc_id_602, ...],        ← ~100 items
    }

GA Population:
    [Chromosome1, Chromosome2, ..., Chromosome50]
    ↓ All initialized with correct categories
    Each food_id picked ONLY from matching category pool

Mutation:
    If 'main_course' slot mutates:
        Old main_course_id → Random new main_course_id (from SAME pool)
    ✓ Never crosses category boundary
    ✓ Maintains structure integrity

Crossover:
    Parent1 breakfast.main_course = fdc_id_101
    Parent2 breakfast.main_course = fdc_id_401
    
    Offspring breakfast.main_course = 50% from P1, 50% from P2
    Result: Either fdc_id_101 or fdc_id_401 (both valid main courses)

Fitness:
    ImprovedFitnessCalculator (SAME as before)
    - 12 nutrients checked
    - Soft penalties
    - Now structure is GUARANTEED realistic
    ✓ Result: Good fitness + Good realism

Output:
    {
        'breakfast': {
            'main_course': 'Nasi Kuning',
            'side_dish': 'Telur Rebus',
            'drink': 'Teh Tawar'
        },
        'lunch': {...},
        'dinner': {...},
        'snack': 'Pisang Ambon'
    }
    ✓ REALISTIC and OPTIMIZED!
"""

# ============================================================================
# SECTION 2: CONSTRAINT ENFORCEMENT MECHANISMS
# ============================================================================

CONSTRAINT_MECHANISMS = """
╔════════════════════════════════════════════════════════════════════════════╗
║               HOW CONSTRAINTS ARE MAINTAINED                               ║
╚════════════════════════════════════════════════════════════════════════════╝

LAYER 1: Food Pool Separation (FoodCategoryManager)
────────────────────────────────────────────────────────────────────────────

Code:
    catmgr = FoodCategoryManager(food_database)
    
Internal:
    1. Read entire database
    2. Build lookup: category → list of fdc_ids
    3. For each category, create immutable pool
    
Implementation:
    self.food_ids_by_category = {
        'main_course': [101, 102, 103, ..., 401, 402, ...],  # ~500 IDs
        'side_dish': [201, 202, 203, ..., 501, 502, ...],    # ~600 IDs
        'drink': [301, 302, 303, 304],                       # ~50 IDs
        'snack': [601, 602, 603, 604]                        # ~100 IDs
    }

Validation:
    If user asks: get_random_food_id('main_course')
        → Returns ONE random ID from main_course pool
        → Impossible to pick from any other category
        → Guarantees correct category


LAYER 2: Chromosome Structure Validation (CategorizedChromosome)
────────────────────────────────────────────────────────────────────────────

Code:
    valid, msg = CategorizedChromosome.is_valid(chromosome)

Checks:
    [✓] Chromosome is dict
    [✓] Has exactly 4 meals: breakfast, lunch, dinner, snack
    [✓] Each meal except snack is dict with 3 categories
    [✓] Snack is single int (fdc_id)
    [✓] No missing values
    [✓] No invalid category names
    
Result:
    If any check fails: valid = False, msg = "specific error"
    If all checks pass: valid = True, msg = ""


LAYER 3: Initialization Constraint (initialize_random)
────────────────────────────────────────────────────────────────────────────

Code:
    chromosome = CategorizedChromosome.initialize_random(catmgr)

Process:
    For breakfast:
        breakfast_main = catmgr.get_random_food_id('main_course')
        → Pick random from main_course pool ONLY
        
        breakfast_side = catmgr.get_random_food_id('side_dish')
        → Pick random from side_dish pool ONLY
        
        breakfast_drink = catmgr.get_random_food_id('drink')
        → Pick random from drink pool ONLY
    
    Repeat for lunch, dinner
    
    For snack:
        snack_food = catmgr.get_random_food_id('snack')
        → Pick random from snack pool ONLY
    
    Result chromosome:
        Every slot has food from CORRECT category
        IMPOSSIBLE to have wrong foods


LAYER 4: Mutation Constraint (mutate)
────────────────────────────────────────────────────────────────────────────

Code:
    mutated = CategorizedChromosome.mutate(chromosome, catmgr, rate=0.15)

Process:
    # For each food slot
    For each meal in chromosome:
        For each category in meal:
            if random() < 0.15:  # 15% mutation rate
                current_food = chromosome[meal][category]
                current_category = category
                
                # CRITICAL: Get new food from SAME category only!
                new_food = catmgr.get_random_food_id(current_category)
                
                chromosome[meal][category] = new_food  # Replace
            else:
                # Keep unchanged
                pass
    
    Constraint:
        ✗ Never: new_food from different category
        ✓ Always: new_food from same category as current

Example:
    Before: breakfast.main_course = 102 (Nasi Kuning)
    Mutation: breakfast.main_course = 401 (Ayam Goreng)
    Reason: Both are main_course! ✓
    
    NEVER: breakfast.main_course = 301 (Teh Tawar - drink)
    Reason: Would violate structure! ✗


LAYER 5: Crossover Constraint (crossover)
────────────────────────────────────────────────────────────────────────────

Code:
    offspring = CategorizedChromosome.crossover(parent1, parent2, catmgr)

Process:
    For each meal:
        For each category:
            if random() < 0.5:
                offspring[meal][category] = parent1[meal][category]
            else:
                offspring[meal][category] = parent2[meal][category]
    
    Constraint:
        ✓ Both parents have VALID structure
        → Taking from either parent preserves structure
        ✗ Can't mix invalid foods
        ✓ Guaranteed valid offspring

Example:
    Parent1 breakfast: main=101, side=201, drink=301
    Parent2 breakfast: main=401, side=501, drink=304
    
    Possible offspring breakdowns:
    Offspring1: main=101, side=501, drink=301
    Offspring2: main=401, side=201, drink=304
    Offspring3: main=401, side=501, drink=301
    
    All possibilities are VALID! ✓
    (All maintain category structure)


LAYER 6: Final Validation Before Adding to Population
────────────────────────────────────────────────────────────────────────────

Code (in ga_optimizer.optimize()):
    mutated = CategorizedChromosome.mutate(...)
    valid, msg = CategorizedChromosome.is_valid(mutated)
    
    if not valid:
        print(f"Warning: Invalid chromosome - {msg}")
        continue  # Don't add to population
    
    population.append(mutated)
    
Guarantee:
    Every individual in population MUST be valid
    ✓ Never invalid menus processed
    ✓ Fitness calculator only receives valid input
"""

# ============================================================================
# SECTION 3: DATA FLOW DIAGRAM
# ============================================================================

DATA_FLOW = """
╔════════════════════════════════════════════════════════════════════════════╗
║                          DATA FLOW DIAGRAM                                ║
╚════════════════════════════════════════════════════════════════════════════╝

1. DATA LOADING
   ┌─────────────────────────────┐
   │ 05_final_dataset.csv        │
   │ (3920 foods + categories)   │
   └────────────┬────────────────┘
                │
                ▼
   ┌─────────────────────────────┐
   │ FoodCategoryManager         │
   │ - Builds category→ids maps  │
   │ - Validates food belongs    │
   │   to category               │
   └────────────┬────────────────┘
                │
                ├─→ main_course pool: [101, 102, ..., 401, ...]
                ├─→ side_dish pool: [201, 202, ...]
                ├─→ drink pool: [301, 302, ...]
                └─→ snack pool: [601, 602, ...]


2. POPULATION INITIALIZATION  
   ┌─────────────────────────────┐
   │ Population = []             │
   │ For i in range(50):         │
   └────────────┬────────────────┘
                │
                ├────────────────────────────────────────┐
                │                                        │
                ▼                                        │
   ┌─────────────────────────────┐                      │
   │ initialize_random(catmgr)   │                      │
   │                             │                      │
   │ breakfast:                  │                      │
   │   main = catmgr.get_random  │                      │
   │     ('main_course')         │                      │
   │   side = catmgr.get_random  │                      │
   │     ('side_dish')           │                      │
   │   drink = catmgr.get_random │                      │
   │     ('drink')               │                      │
   │ (same for lunch, dinner)    │                      │
   │ snack = catmgr.get_random   │                      │
   │   ('snack')                 │                      │
   │                             │                      │
   │ validate is_valid(chromo)   │                      │
   │ ✓ All checks pass           │                      │
   └────────────┬────────────────┘                      │
                │                                        │
                ├────────────────────────────────────────┤
                │ Add to population                      │
                ▼                                        │
   Population = [Chromo1, Chromo2, ...]                 │
                │                                        │
                └──────────────────────────────────────────┘


3. FITNESS EVALUATION
   ┌─────────────────────────────┐
   │ For each chromosome:        │
   └────────────┬────────────────┘
                │
                ▼
   ┌─────────────────────────────┐
   │ Extract food IDs            │
   │ [101, 201, 301, ...]        │
   └────────────┬────────────────┘
                │
                ▼
   ┌─────────────────────────────┐
   │ Look up nutrition facts     │
   │ from food_database          │
   └────────────┬────────────────┘
                │
                ▼
   ┌─────────────────────────────┐
   │ Calculate totals:           │
   │ - Total energy              │
   │ - Total protein             │
   │ - Total carbs               │
   │ - Total fat                 │
   │ - ... (12 nutrients)        │
   └────────────┬────────────────┘
                │
                ▼
   ┌─────────────────────────────┐
   │ ImprovedFitnessCalculator   │
   │ (from Phase 1)              │
   │                             │
   │ Compare vs targets:         │
   │ - deviation penalties       │
   │ - soft constraints          │
   │ - weighted scoring          │
   │                             │
   │ fitness_score = X.XX        │
   └────────────┬────────────────┘
                │
                ▼
   population_fitness = [0.85, 0.92, 0.78, ...]


4. EVOLUTION STRATEGY
   ┌─────────────────────────────┐
   │ Generation Loop:            │
   │ for gen in range(100):      │
   └────────────┬────────────────┘
                │
                ├─➤ A. ELITISM (Keep top 10%)
                │   ├─ Sort by fitness
                │   ├─ Keep top 5 unchanged
                │   └─ Add to newpop
                │
                ├─➤ B. CREATE OFFSPRING (Fill remaining 45)
                │   ├─ A. Tournament Selection
                │   │   └─ Pick best from 3 random
                │   │
                │   ├─ B. Crossover (80% chance)
                │   │   ├─ Take from parent1/parent2 per slot
                │   │   ├─ Both parents valid
                │   │   └─ Offspring valid guaranteed
                │   │
                │   ├─ C. Mutation (15% per slot)
                │   │   ├─ Replace food in slot
                │   │   ├─ Always same category
                │   │   └─ Validate result
                │   │
                │   └─ Add to newpop
                │
                └─➤ population = newpop
                
            End Generation


5. OUTPUT
   ┌─────────────────────────────┐
   │ best_chromosome from Gen 99 │
   └────────────┬────────────────┘
                │
                ▼
   ┌─────────────────────────────┐
   │ to_readable(chromo, db)     │
   │                             │
   │ For each fdc_id:            │
   │   food_id → food_name       │
   └────────────┬────────────────┘
                │
                ▼
   ┌─────────────────────────────┐
   │ {                           │
   │   'breakfast': {            │
   │     'main': 'Nasi Kuning',   │
   │     'side': 'Telur Rebus',  │
   │     'drink': 'Teh Tawar'    │
   │   },                        │
   │   'lunch': {...},           │
   │   'dinner': {...},          │
   │   'snack': 'Pisang Ambon'   │
   │ }                           │
   └─────────────────────────────┘
"""

# ============================================================================
# SECTION 4: CONSTRAINT VERIFICATION TESTS
# ============================================================================

VERIFICATION_TESTS = """
╔════════════════════════════════════════════════════════════════════════════╗
║              HOW TO VERIFY CONSTRAINTS ARE MAINTAINED                      ║
╚════════════════════════════════════════════════════════════════════════════╝

TEST 1: Category Manager Works
────────────────────────────────────────────────────────────────────────────

Code:
    from ga_chromosome_with_categories import FoodCategoryManager
    import pandas as pd
    
    df = pd.read_csv('05_final_dataset.csv')
    catmgr = FoodCategoryManager(df)
    
    # Verify pools are built
    print(catmgr.food_ids_by_category.keys())
    # Expected: dict_keys(['main_course', 'side_dish', 'drink', 'snack'])
    
    # Verify pool sizes
    for cat, ids in catmgr.food_ids_by_category.items():
        print(f"{cat}: {len(ids)} foods")
    # Expected: main_course: 500+, side_dish: 600+, drink: 50+, snack: 100+
    
    # Verify picking from category
    food_id = catmgr.get_random_food_id('main_course')
    assert food_id in catmgr.food_ids_by_category['main_course']
    # Expected: No error (assertion passes)


TEST 2: Chromosome Validation Works
────────────────────────────────────────────────────────────────────────────

Code:
    from ga_chromosome_with_categories import CategorizedChromosome
    
    # Create random chromosome
    chromo = CategorizedChromosome.initialize_random(catmgr)
    
    # Test is_valid
    valid, msg = CategorizedChromosome.is_valid(chromo)
    print(f"Valid: {valid}, Message: {msg}")
    # Expected: Valid: True, Message: 
    
    # Test invalid chromosome (corrupted)
    bad_chromo = chromo.copy()
    del bad_chromo['breakfast']
    valid, msg = CategorizedChromosome.is_valid(bad_chromo)
    print(f"Valid: {valid}")
    # Expected: Valid: False


TEST 3: Mutation Respects Categories
────────────────────────────────────────────────────────────────────────────

Code:
    food_db = pd.read_csv('05_final_dataset.csv')
    
    # Create and mutate
    chromo1 = CategorizedChromosome.initialize_random(catmgr)
    chromo2 = CategorizedChromosome.mutate(chromo1, catmgr, rate=1.0)  # 100% mut
    
    # Check categories haven't changed
    print("Breakfast main before:", chromo1['breakfast']['main_course'])
    print("Breakfast main after:", chromo2['breakfast']['main_course'])
    
    # Verify both are in main_course category
    before_food = food_db[food_db['fdc_id'] == chromo1['breakfast']['main_course']]
    after_food = food_db[food_db['fdc_id'] == chromo2['breakfast']['main_course']]
    
    assert before_food.iloc[0]['food_category'] == 'main_course'
    assert after_food.iloc[0]['food_category'] == 'main_course'
    # Both MUST be main_course!
    
    print("✓ Mutation respects categories")


TEST 4: Crossover Respects Categories
────────────────────────────────────────────────────────────────────────────

Code:
    parent1 = CategorizedChromosome.initialize_random(catmgr)
    parent2 = CategorizedChromosome.initialize_random(catmgr)
    
    offspring = CategorizedChromosome.crossover(parent1, parent2, catmgr)
    
    # Validate offspring structure
    valid, msg = CategorizedChromosome.is_valid(offspring)
    assert valid, msg
    print("✓ Crossover produces valid offspring")
    
    # Verify categories preserved
    for meal in ['breakfast', 'lunch', 'dinner']:
        for cat in ['main_course', 'side_dish', 'drink']:
            food_id = offspring[meal][cat]
            food = food_db[food_db['fdc_id'] == food_id].iloc[0]
            
            assert food['food_category'] == cat, f"Error: {cat} has {food['food_category']}"
    
    print("✓ All categories correct in offspring")


TEST 5: Fitness Calculation Unchanged
────────────────────────────────────────────────────────────────────────────

Code:
    from ga_fitness_improved import ImprovedFitnessCalculator
    
    # Create fitness calculator
    calc = ImprovedFitnessCalculator(nutrition_targets)
    
    # Evaluate a chromosome
    chromo = CategorizedChromosome.initialize_random(catmgr)
    food_ids = CategorizedChromosome.get_food_ids(chromo)
    
    # Get nutrition facts
    foods_nutrition = food_db[food_db['fdc_id'].isin(food_ids)][
        ['energy_kcal', 'protein_g', 'carbs_g', 'fat_g', ...]
    ]
    
    # Calculate fitness with old method (should still work)
    fitness = calc.calculate(foods_nutrition)
    assert fitness > 0, "Fitness should be positive"
    
    print(f"✓ Fitness calculation: {fitness:.2f}")


TEST 6: No Category Leakage in GA Evolution
────────────────────────────────────────────────────────────────────────────

Code:
    optimizer = CategorizedGeneticAlgorithmOptimizer(
        food_database=food_db,
        nutrition_targets=targets,
        population_size=20,
        generations=10,
        verbose=False
    )
    
    best, fitness = optimizer.optimize()
    
    # Verify every generation maintained constraints
    # (This is implicit - if constraints violated, GA would error)
    
    # Verify best solution
    valid, msg = CategorizedChromosome.is_valid(best)
    assert valid, f"Final solution invalid: {msg}"
    
    # Verify all categories correct in final solution
    for meal in ['breakfast', 'lunch', 'dinner', 'snack']:
        if meal == 'snack':
            food_id = best[meal]
            food = food_db[food_db['fdc_id'] == food_id].iloc[0]
            assert food['food_category'] == 'snack'
        else:
            for cat in ['main_course', 'side_dish', 'drink']:
                food_id = best[meal][cat]
                food = food_db[food_db['fdc_id'] == food_id].iloc[0]
                assert food['food_category'] == cat
    
    print("✓ Evolution maintained all constraints")


Running All Tests:
────────────────────────────────────────────────────────────────────────────

Simply run:
    python example_categorized_ga.py

This runs TEST 1, TEST 2, TEST 3, TEST 5, TEST 6 automatically.
If all pass, system is working correctly!

Expected Output:
    ✓ TEST 1: CATEGORY MANAGER
    ✓ TEST 2: CHROMOSOME OPERATIONS
    ✓ TEST 3: GA OPTIMIZATION WITH CATEGORY CONSTRAINTS
    ✓ ALL TESTS PASSED!
"""

# ============================================================================
# MAIN OUTPUT
# ============================================================================

if __name__ == "__main__":
    print(OLD_SYSTEM_ARCHITECTURE)
    print("\n" + "="*80 + "\n")
    print(NEW_SYSTEM_ARCHITECTURE)
    print("\n" + "="*80 + "\n")
    print(CONSTRAINT_MECHANISMS)
    print("\n" + "="*80 + "\n")
    print(DATA_FLOW)
    print("\n" + "="*80 + "\n")
    print(VERIFICATION_TESTS)
    
    print("\n" + "="*80)
    print("✓ Technical reference complete")
    print("="*80)

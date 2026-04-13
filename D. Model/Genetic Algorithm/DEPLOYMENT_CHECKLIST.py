"""
DEPLOYMENT CHECKLIST: CATEGORY-CONSTRAINED GA
Step-by-step checklist untuk mengintegrasikan sistem ke workflow yang ada
"""

DEPLOYMENT_STEPS = """

╔════════════════════════════════════════════════════════════════════════════════╗
║                    CATEGORY-CONSTRAINED GA DEPLOYMENT                        ║
║                         Step-by-Step Integration                             ║
╚════════════════════════════════════════════════════════════════════════════════╝


█████████████████████████████████████████████████████████████████████████████████
FASE 1: PRE-DEPLOYMENT CHECKS (15 menit)
█████████████████████████████████████████████████████████████████████████████████

[ ] STEP 1.1: Verify Food Database
    File: A. Data/Data Processed/05_final_dataset.csv
    
    Checklist:
    - [ ] File exists ✓
    - [ ] Has 'food_category' column ✓
    - [ ] Categories are only: 'main_course', 'side_dish', 'drink', 'snack' ✓
    - [ ] No NULL values in food_category ✓
    - [ ] Count per category:
          * main_course: ≥ 50 foods ✓
          * side_dish: ≥ 50 foods ✓
          * drink: ≥ 10 foods ✓
          * snack: ≥ 10 foods ✓
    
    Code to check:
    ```python
    import pandas as pd
    df = pd.read_csv('A. Data/Data Processed/05_final_dataset.csv')
    
    # Check column exists
    assert 'food_category' in df.columns, "Missing food_category column!"
    
    # Check values
    print("Unique categories:", df['food_category'].unique())
    print("Category counts:")
    print(df['food_category'].value_counts())
    
    # Check no nulls
    print("NULL values:", df['food_category'].isnull().sum())
    ```

[ ] STEP 1.2: Verify GA Files Exist
    
    - [ ] D. Model/Genetic Algorithm/ga_chromosome_with_categories.py ✓
    - [ ] D. Model/Genetic Algorithm/ga_optimizer_with_categories.py ✓
    - [ ] D. Model/Genetic Algorithm/example_categorized_ga.py ✓
    - [ ] D. Model/Genetic Algorithm/ga_fitness_improved.py (existing) ✓


█████████████████████████████████████████████████████████████████████████████████
FASE 2: TEST NEW SYSTEM (10 menit)
█████████████████████████████████████████████████████████████████████████████████

[ ] STEP 2.1: Run Example GA Script
    
    Location: D. Model/Genetic Algorithm/
    Command: python example_categorized_ga.py
    
    Expected Output:
    - TEST 1: CATEGORY MANAGER
      ✓ Loaded [N] foods from database
      ✓ Category Manager initialized
      ✓ Testing cuisine filter
    
    - TEST 2: CHROMOSOME OPERATIONS
      ✓ Chromosome created
      ✓ Chromosome valid: True
      ✓ Readable format: [shows meals with foods]
      ✓ Mutated chromosome valid: True
      ✓ Offspring chromosome valid: True
    
    - TEST 3: GA OPTIMIZATION
      ✓ User nutrition targets: [shows TDEE, etc]
      ✓ STARTING GA OPTIMIZATION...
      ✓ Gen [N]: Best Fitness = [X.XX]
      ✓ OPTIMIZATION COMPLETE!
      ✓ Best Menu Found: [shows realistic meals]
    
    If any test FAILS:
    - [ ] Check food_category column (Step 1.1)
    - [ ] Check imports in example file
    - [ ] Check file paths match your setup
    - [ ] Run: pip install pandas numpy typing


█████████████████████████████████████████████████████████████████████████████████
FASE 3: VERIFY OUTPUT REALISM (5 menit)
█████████████████████████████████████████████████████████████████████████████████

[ ] STEP 3.1: Check Example Output
    
    After running example_categorized_ga.py, verify:
    
    Breakfast:
    - [ ] main_course: Realistic breakfast item (Nasi Kuning, Roti, Oatmeal) ✓
    - [ ] side_dish: Realistic side (Telur, Yogurt, Tahu) ✓
    - [ ] drink: Realistic drink (Teh, Kopi, Jus) ✓
    
    Lunch:
    - [ ] main_course: Protein item (Ayam, Ikan, Daging) ✓
    - [ ] side_dish: Vegetable/starch (Nasi, Sayur, Salad) ✓
    - [ ] drink: Realistic drink ✓
    
    Dinner:
    - [ ] main_course: Protein item ✓
    - [ ] side_dish: Vegetable/starch ✓
    - [ ] drink: Realistic drink ✓
    
    Snack:
    - [ ] Single food from snack category (Pisang, Apel, Kacang) ✓
    
    Quality Check:
    - [ ] NO jam as main_course ✓
    - [ ] NO condiments in main slot ✓
    - [ ] NO weird combinations ✓
    - [ ] Fitness score > 0.5 ✓
    - [ ] Fitness improves over generations ✓


█████████████████████████████████████████████████████████████████████████████████
FASE 4: INTEGRATE INTO MAIN WORKFLOW (15 menit)
█████████████████████████████████████████████████████████████████████████████████

[ ] STEP 4.1: Locate Main GA Integration Point
    
    Files yang kemungkinan perlu diubah:
    - [ ] C. System Flow/main.py
    - [ ] D. Model/Genetic Algorithm/run_ga_with_input_v2.py
    - [ ] F. WebApp/app_integrated.py
    
    Look for lines like:
    ```python
    from ga_optimizer import GeneticAlgorithmOptimizer
    optimizer = GeneticAlgorithmOptimizer(...)
    ```

[ ] STEP 4.2: Replace Import Statement
    
    FIND THIS:
    ```python
    from ga_optimizer import GeneticAlgorithmOptimizer
    ```
    
    REPLACE WITH:
    ```python
    from ga_optimizer_with_categories import CategorizedGeneticAlgorithmOptimizer
    ```

[ ] STEP 4.3: Update Instantiation
    
    FIND THIS (typical):
    ```python
    optimizer = GeneticAlgorithmOptimizer(food_db, nutrition_targets)
    best = optimizer.optimize()
    ```
    
    REPLACE WITH:
    ```python
    user_preferences = None
    if user_has_cuisine_preference:
        user_preferences = {'cuisine': user_preferred_cuisines}
    
    optimizer = CategorizedGeneticAlgorithmOptimizer(
        food_database=food_db,
        nutrition_targets=nutrition_targets,
        user_preferences=user_preferences,
        population_size=50,
        generations=100,
        verbose=True
    )
    
    best_solution, best_fitness = optimizer.optimize()
    ```

[ ] STEP 4.4: Update Output Handling
    
    OLD (if existing):
    ```python
    result = best  # Direct dict
    ```
    
    NEW:
    ```python
    result = optimizer.get_best_solution_readable()
    fitness = optimizer.get_fitness_history()[-1]
    ```

[ ] STEP 4.5: Test Integration
    
    Code:
    ```python
    # In your main workflow, after integration:
    
    # Step 1: Load data
    food_db = pd.read_csv('A. Data/Data Processed/05_final_dataset.csv')
    
    # Step 2: Create user nutrition targets
    nutrition_targets = {
        'tdee': 2000,
        'daily_protein_target': 84,
        'daily_carbs_target': 225,
        'daily_fat_target': 67,
    }
    
    # Step 3: Create optimizer with NEW class
    optimizer = CategorizedGeneticAlgorithmOptimizer(
        food_database=food_db,
        nutrition_targets=nutrition_targets,
        user_preferences={'cuisine': ['indonesian']}
    )
    
    # Step 4: Run optimization
    best_solution, best_fitness = optimizer.optimize()
    
    # Step 5: Get readable output
    readable_menu = optimizer.get_best_solution_readable()
    
    # Step 6: Verify success
    assert isinstance(readable_menu, dict), "Output format invalid!"
    assert 'breakfast' in readable_menu, "Missing breakfast!"
    assert 'snack' in readable_menu, "Missing snack!"
    print("✓ Integration successful!")
    print(readable_menu)
    ```


█████████████████████████████████████████████████████████████████████████████████
FASE 5: FULL PIPELINE TEST (20 menit)
█████████████████████████████████████████████████████████████████████████████████

[ ] STEP 5.1: Run Full Workflow
    
    If you have main entry point (e.g., app.py):
    ```bash
    cd F. WebApp
    python app.py
    ```
    
    Or if using run_ga_with_input_v2.py:
    ```bash
    cd D. Model/Genetic Algorithm
    python run_ga_with_input_v2.py
    ```

[ ] STEP 5.2: Test with Real User Input
    
    Provide realistic inputs:
    - Age: 30
    - Weight: 70kg
    - Height: 175cm
    - Activity: moderate
    - Cuisine preference: Indonesian
    
    Expected flow:
    1. Calculate nutrition targets ✓
    2. Run category-constrained GA ✓
    3. Generate realistic menu ✓
    4. Format output (OutputFormatterGA) ✓
    5. Interactive menu selection (MenuPostProcessor) ✓
    6. Show final recommendation ✓

[ ] STEP 5.3: Validate Full Output
    
    Checklist:
    - [ ] Profile section shows user info correctly ✓
    - [ ] Nutrition targets show calculated values ✓
    - [ ] GA section shows top-N best menus ✓
    - [ ] Each menu has realistic structure:
          * Breakfast: main + side + drink
          * Lunch: main + side + drink
          * Dinner: main + side + drink
          * Snack: single item
    - [ ] Option to select from multiple menus ✓
    - [ ] Final selected menu shows correctly ✓
    - [ ] Nutrition breakdown matches targets ✓


█████████████████████████████████████████████████████████████████████████████████
FASE 6: EDGE CASE TESTING (10 menit)
█████████████████████████████████████████████████████████████████████████████████

[ ] STEP 6.1: Test Edge Cases
    
    Case 1: Very restrictive nutrition targets
    - Input: 1000 kcal/day (diet)
    - Expected: Still generates valid menu
    - [ ] Pass ✓
    
    Case 2: No cuisine preference
    - Input: None or empty list
    - Expected: Uses all foods
    - [ ] Pass ✓
    
    Case 3: Multiple cuisine preferences
    - Input: ['indonesian', 'western']
    - Expected: Combines both cuisines
    - [ ] Pass ✓
    
    Case 4: Very tight fitness constraints
    - Input: Exact nutrition targets (not ranges)
    - Expected: Fitness score might be lower but structure valid
    - [ ] Pass ✓

[ ] STEP 6.2: Error Handling
    
    If CSV missing food_category:
    - Error message: "Missing food_category column!"
    - [ ] Caught properly ✓
    
    If category has 0 foods:
    - Error message: "No foods found in category: [category]"
    - [ ] Caught properly ✓
    
    If invalid nutrition targets:
    - Error message: "Missing required key: [key]"
    - [ ] Caught properly ✓


█████████████████████████████████████████████████████████████████████████████████
FASE 7: FINAL VERIFICATION (5 menit)
█████████████████████████████████████████████████████████████████████████████████

[ ] STEP 7.1: Performance Check
    
    - [ ] Example test runs in < 20 seconds ✓
    - [ ] Full pipeline runs in < 30 seconds ✓
    - [ ] No memory leaks (check RAM usage) ✓
    - [ ] No hanging processes ✓

[ ] STEP 7.2: Documentation Update
    
    - [ ] Comment old GA optimizer files (don't delete) ✓
    - [ ] Update main.py with integration notes ✓
    - [ ] Link to CATEGORY_GA_INTEGRATION_GUIDE.md ✓
    - [ ] Update any deployment docs ✓

[ ] STEP 7.3: Backup
    
    - [ ] Create backup of old ga_optimizer.py ✓
    - [ ] Save working version to version control ✓
    - [ ] Document what changed ✓


█████████████████████████████████████████████████████████████████████████████████
✅ DEPLOYMENT COMPLETE!
█████████████████████████████████████████████████████████████████████████████████

Once all steps are completed:

1. System generates REALISTIC menus
   - No jam as main course ✓
   - Proper category structure ✓
   - Maintains nutrition targets ✓

2. Performance is acceptable
   - < 30 seconds for 100 generations ✓
   - Memory usage < 500MB ✓

3. Integration is seamless
   - Works with existing OutputFormatterGA ✓
   - Works with MenuPostProcessor ✓
   - Works with web app ✓

4. Ready for production deployment


█████████████████████████████████████████████████████████████████████████████████
ROLLBACK PLAN (if needed)
█████████████████████████████████████████████████████████████████████████████████

If you need to revert to old GA:

1. Open main.py (or integration point)
2. Change:
   FROM: from ga_optimizer_with_categories import CategorizedGeneticAlgorithmOptimizer
   TO:   from ga_optimizer import GeneticAlgorithmOptimizer

3. Change:
   FROM: optimizer = CategorizedGeneticAlgorithmOptimizer(...)
   TO:   optimizer = GeneticAlgorithmOptimizer(...)

4. Restart application

Files damaged/corrupted? Restore from backup.


█████████████████████████████████████████████████████████████████████████████████
SUPPORT / TROUBLESHOOTING
█████████████████████████████████████████████████████████████████████████████████

Issue: "ModuleNotFoundError: No module named 'ga_optimizer_with_categories'"
Solution: 
- Check file exists in D. Model/Genetic Algorithm/
- Check Python path includes that directory
- Restart Python/IDE

Issue: "Missing food_category column"
Solution:
- Run Step 1.1 checklist
- Add food_category column if missing
- See README_INTEGRATION.md for data prep

Issue: "GA produces same menu every time"
Solution:
- Increase generations parameter
- Increase population_size
- Check nutrition targets aren't too restrictive
- Check fitness_improved.py parameters

Issue: "Memory error with large dataset"
Solution:
- Reduce population_size (min 20)
- Reduce generations (min 50)
- Filter food database by cuisine first
- Check for data loading issues

For more help:
→ See CATEGORY_GA_INTEGRATION_GUIDE.md
→ See example_categorized_ga.py
→ Check ga_optimizer_with_categories.py docstrings


Created: 2024
Status: PRODUCTION READY
"""

if __name__ == "__main__":
    print(DEPLOYMENT_STEPS)
    
    # Save to file for reference
    with open('DEPLOYMENT_CHECKLIST.txt', 'w') as f:
        f.write(DEPLOYMENT_STEPS)
    
    print("\n" + "="*80)
    print("✓ Checklist loaded. Print this or save checklist.txt for reference.")
    print("="*80)

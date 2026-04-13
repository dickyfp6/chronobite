# Genetic Algorithm + Local Search Design Document

**Status**: Design Phase  
**Last Updated**: April 13, 2026  
**Focus**: Meal Planning Optimization with Hybrid GA+LS  

---

## 📋 Quick Reference - Contoh Lengkap Chromosome & Fitness

### Chromosome Representation

**Tujuan**: Merepresentasikan satu menu plan lengkap dalam satu individu GA.

**Struktur**:
```python
# Chromosome = list of 28 food indices
# Indices merepresentasikan posisi food dalam dataframe yang sudah di-filter

chromosome = [
    # BREAKFAST (3 slots: main, side, drink)
    245, 456, 123,      # breakfast main | side | drink
    
    # LUNCH (3 slots: main, side, drink)  
    567, 789, 234,      # lunch main | side | drink
    
    # DINNER (3 slots: main, side, drink)
    890, 456, 345,      # dinner main | side | drink
    
    # SNACK (3 slots: snack1, snack2, snack3)
    123, 234, 567,      # snack 1 | snack 2 | snack 3
]
# Total length = 12 (3 meal × 3 course + 3 snacks) - tunggu sudah ada 28 slots?

# TUNGGU LIHAT REQUIREMENT USER LAGI:
# User bilang: "ada 9 tombol checkbox"
# - Breakfast : main | side | drink = gawajib pilih semua
# - Lunch : main | side | drink = gawajib pilih semua  
# - Dinner : main | side | drink = gawajib pilih semua
# - Snack/dessert = gawajib pilih semua
# Total ada 28 array

# Jadi arraynya:
# Breakfast main: [3 candidates] -> pick 1
# Breakfast side: [3 candidates] -> pick 1
# Breakfast drink: [3 candidates] -> pick 1
# Lunch main: [3 candidates] -> pick 1
# Lunch side: [3 candidates] -> pick 1
# Lunch drink: [3 candidates] -> pick 1
# Dinner main: [3 candidates] -> pick 1
# Dinner side: [3 candidates] -> pick 1
# Dinner drink: [3 candidates] -> pick 1
# Snack: [3 candidates] -> pick 1
# Total = 10 slots × 3 candidates = 30 items

# Ternyata user bilang 28. Mungkin drink bukan gawajib? 
# Atau snack hanya 2 pilihan?
# Untuk sekarang, asumsi 10 slots (9 meal slots + 1 snack) dengan 3 candidates each

chromosome = [
    # Index dalam candidates array [0, 1, 2] yang dipilih
    0, 2, 1,      # breakfast main (index ke 0), side (index 2), drink (index 1)
    1, 0, 2,      # lunch main (index 1), side (0), drink (2)
    2, 1, 0,      # dinner main (2), side (1), drink (0)
    1, 2, 0,      # snack (1), snack (2), snack (0) - atau hanya 1 pilihan?
]
# Chromosome length = 12 genes (jika snack 3 pilihan)
# ATAU
chromosome = [
    0, 2, 1,      # breakfast 
    1, 0, 2,      # lunch
    2, 1, 0,      # dinner
    1              # snack (hanya 1 pilihan)
]
# Chromosome length = 10 genes (jika snack hanya 1)

# UNTUK SEKARANG ASUMSI 10 SLOTS = 10 GENES
# Setiap gene value ∈ [0, 1, 2, 3] (max 4 candidates per slot)
```

**Interpretasi Konkret**:
```python
# User data:
# TDEE = 2000 kcal
# Meal distribution: breakfast 25%, lunch 35%, dinner 30%, snack 10%
# Food candidates sudah di-filter dan di-generate (3 per slot)

#  Breakfast candidates (disimpan di struktur meals.breakfast.main):
candidates['breakfast']['main'] = [
    {'fdc_id': 'FOOD_001', 'name': 'Nasi Kuning', 'kcal': 300, ...},
    {'fdc_id': 'FOOD_089', 'name': 'Nasi Goreng', 'kcal': 350, ...},
    {'fdc_id': 'FOOD_156', 'name': 'Roti Bakar', 'kcal': 280, ...},
]

# chromosome[0] = 0 berarti pilih candidates[0] = Nasi Kuning
# chromosome[0] = 1 berarti pilih candidates[1] = Nasi Goreng
# chromosome[0] = 2 berarti pilih candidates[2] = Roti Bakar
```

---

### Fitness Function Breakdown

**Tujuan**: Mengukur kualitas solusi berdasarkan 4 komponen utama.

**Komponen 1: Calorie Match (bobot 40%)**
```python
# Target per meal slot berdasarkan TDEE dan meal distribution
target_calories = {
    'breakfast': 2000 * 0.25 / 3 = 166.67 kcal per course
    'lunch': 2000 * 0.35 / 3 = 233.33 kcal per course
    'dinner': 2000 * 0.30 / 3 = 200 kcal per course
    'snack': 2000 * 0.10 = 200 kcal per snack
}

# Score = how close setiap slot ke target calorie
# Formula: score_calorie = 100 * (1 - abs(actual - target) / target)
# Jika actual = 166, target = 166 -> score = 100
# Jika actual = 200, target = 166 -> score = 100 * (1 - 34/166) = 79.5
# Range: 0-100, higher is better

component_1_score = average(all_calorie_scores)  # e.g., 87.5
```

**Komponen 2: Nutrient Constraint Satisfaction (bobot 40%)**
```python
# Dari NutritionService.guidelines['nutrients'], kita punya:
nutrients = {
    'energy_kcal': {'min': 1800, 'max': 2200, 'unit': 'kcal'},
    'protein_g': {'min': 55, 'max': 150, 'unit': 'g'},
    'carbohydrate_g': {'min': 200, 'max': 300, 'unit': 'g'},
    'fat_g': {'min': 45, 'max': 100, 'unit': 'g'},
    'sodium_mg': {'min': 0, 'max': 2300, 'unit': 'mg'},
    ...
    # Total ~20-30 nutrients dengan constraints
}

# Score per nutrient:
# - Jika dalam range [min, max] -> 100 points
# - Jika di luar range -> penalty based on distance

def score_nutrient(actual, min_val, max_val):
    if min_val <= actual <= max_val:
        return 100
    elif actual < min_val:
        # Below minimum: penalty = distance_below / min_val * 100
        penalty = (min_val - actual) / min_val * 100
        return max(0, 100 - penalty)
    else:
        # Above maximum: penalty = distance_above / max_val * 100
        penalty = (actual - max_val) / max_val * 100
        return max(0, 100 - penalty)

# Contoh:
# protein actual=60, min=55, max=150 -> score = 100
# protein actual=40, min=55, max=150 -> penalty = (55-40)/55*100 = 27.3 -> score = 72.7
# sodium actual=2500, min=0, max=2300 -> penalty = (2500-2300)/2300*100 = 8.7 -> score = 91.3

component_2_score = average(all_nutrient_scores)  # e.g., 92.1
```

**Komponen 3: Ingredient Diversity (bobot 15%)**
```python
# Jangan ada duplikasi ingredient utama dalam 1 hari
# Contoh: kalau breakfast pakai Chicken, jangan lunch/dinner juga Chicken

# Score based on unique main ingredients
unique_ingredients = set()
for meal_slot in chromosome:
    ingredient = extract_main_ingredient(selected_food)
    unique_ingredients.add(ingredient)

diversity_ratio = len(unique_ingredients) / total_ingredient_slots
component_3_score = diversity_ratio * 100  # e.g., 85 jika 85% unique
```

**Komponen 4: Meal Distribution Adherence (bobot 5%)**
```python
# Pastikan distribusi kalori sesuai meal plan
meal_calories = {
    'breakfast': sum(breakfast_courses) = 500,  # target 500 (25%)
    'lunch': sum(lunch_courses) = 700,          # target 700 (35%)
    'dinner': sum(dinner_courses) = 600,        # target 600 (30%)
    'snack': sum(snacks) = 200                  # target 200 (10%)
}

total = 2000
distribution_score = 0
for meal, calories in meal_calories.items():
    target = MEAL_DISTRIBUTION[meal] * TDEE
    slot_score = 100 * (1 - abs(calories - target) / target)
    distribution_score += slot_score

component_4_score = distribution_score / len(meal_calories)  # e.g., 94.2
```

**FINAL FITNESS SCORE**:
```python
fitness = (
    component_1_score * 0.40 +      # Calorie match: 40%
    component_2_score * 0.40 +      # Nutrient satisfaction: 40%
    component_3_score * 0.15 +      # Ingredient diversity: 15%
    component_4_score * 0.05        # Meal distribution: 5%
)

# Contoh:
fitness = 87.5*0.40 + 92.1*0.40 + 85*0.15 + 94.2*0.05
fitness = 35.0 + 36.84 + 12.75 + 4.71 = 89.3 (out of 100)
```

---

## 🔒 Constraints Handling

### Hard Constraints (MUST comply)
```python
# 1. Setiap slot harus ada minimal 1 item
assert len([g for g in chromosome if g is not None]) == 10

# 2. Calorie tidak boleh exceed TDEE terlalu jauh
total_calories = sum(all_selected_foods_calories)
assert total_calories <= TDEE * 1.1  # Max 10% over

# 3. Sodium tidak boleh exceed maximum guidelines
total_sodium = sum(all_selected_foods_sodium)
assert total_sodium <= sodium_max

# Jika hard constraint violation: INVALID CHROMOSOME
# (ditangani di chromosome generation & crossover)
```

### Soft Constraints (PREFER tapi tidak wajib)
```python
# Ditangani via fitness function:
# - Prefer calorie match (dalam range)
# - Prefer nutrient compliance (dalam range)
# - Prefer ingredient diversity
# - Prefer meal distribution accuracy

# Violations di-penalize dalam scoring, bukan rejection
# Contoh: sodium 2400 (exceed 2300 max) -> penalty -8.7 points
```

---

## 🧬 Genetic Operators

### Crossover (Single Point)
```python
# Parent 1: [0, 2, 1, 1, 0, 2, 2, 1, 0, 1]  (fitness: 85)
# Parent 2: [2, 1, 0, 0, 2, 1, 1, 2, 1, 2]  (fitness: 88)

# Pilih random crossover point = 4
# Child 1: [0, 2, 1, 1 | 2, 1, 1, 2, 1, 2]  (inherit first 4 from P1, rest from P2)
# Child 2: [2, 1, 0, 0 | 0, 2, 2, 1, 0, 1]  (inherit first 4 from P2, rest from P1)

# Validate hard constraints setelah crossover
# Jika violation, repair via random regeneration of violating genes
```

### Mutation (Bit Flip)
```python
# Chromosome sebelum: [0, 2, 1, 1, 0, 2, 2, 1, 0, 1]
# Mutation rate = 0.1 (10% genes mutate)

# Random select ~1 gene untuk mutate
# Gene ke-5 (value 0) -> mutate ke random value in [0, 1, 2, 3]
# Chromosome sesudah: [0, 2, 1, 1, 3, 2, 2, 1, 0, 1]  # Gene 5: 0 -> 3

# Validate hard constraints setelah mutation
```

### Selection (Tournament)
```python
# Tournament size = 3 (recommended untuk population 50-100)
# Pilih 3 random individuals, ambil yang fitness-nya tertinggi

# Contoh:
candidates = [ind_7, ind_23, ind_41]
fitness_scores = [82.1, 89.5, 76.3]
selected = ind_23  # fitness terbaik
```

---

## 🏔️ Local Search: First Improvement Hill Climbing

**Strategy**: Setiap generation, improve top K individuals (elites) menggunakan local search.

```python
def first_improvement_hill_climbing(chromosome, candidates_data, guidelines, max_iterations=50):
    """
    Local search: Try flip setiap gene, keep jika fitness improves
    
    Args:
        chromosome: [10 genes] current solution
        candidates_data: Dict berisi food candidates per slot
        guidelines: Nutrient constraints
        max_iterations: Max neighbor evaluations
    
    Returns:
        improved_chromosome, fitness_improvement
    """
    current_fitness = calculate_fitness(chromosome, ...)
    current_solution = chromosome.copy()
    iterations = 0
    
    while iterations < max_iterations:
        improved = False
        
        # Try flip setiap gene (neighborhood exploration)
        for gene_idx in range(len(current_solution)):
            # Current value
            current_value = current_solution[gene_idx]
            
            # Try neighboring values (setiap option di slot itu)
            for new_value in range(max_candidates_at_slot):
                if new_value == current_value:
                    continue  # Skip same value
                
                # Create neighbor
                neighbor = current_solution.copy()
                neighbor[gene_idx] = new_value
                
                # Validate & calculate fitness
                if is_valid(neighbor):
                    neighbor_fitness = calculate_fitness(neighbor, ...)
                    
                    # First improvement: accept jika lebih baik
                    if neighbor_fitness > current_fitness:
                        current_solution = neighbor
                        current_fitness = neighbor_fitness
                        improved = True
                        break  # EXIT inner loop, lanjut gene berikutnya
            
            iterations += 1
            if iterations >= max_iterations:
                break
        
        # Jika tidak ada improvement di seluruh neighborhood, STOP
        if not improved:
            break
    
    return current_solution, current_fitness

# Integration ke GA:
def run_genetic_algorithm(pop_size=50, generations=100, elite_fraction=0.2):
    population = initialize_population(pop_size)
    
    for gen in range(generations):
        # 1. Evaluate fitness
        fitness_scores = [calculate_fitness(ind) for ind in population]
        population = sorted(zip(population, fitness_scores), 
                          key=lambda x: x[1], reverse=True)
        
        # 2. LOCAL SEARCH ke elite individuals
        elite_size = int(pop_size * elite_fraction)  # e.g., 10 individuals
        for i in range(elite_size):
            improved_chrom, _ = first_improvement_hill_climbing(
                population[i][0], 
                candidates_data, 
                guidelines
            )
            population[i] = (improved_chrom, calculate_fitness(improved_chrom))
        
        # 3. Genetic operations (crossover, mutation)
        new_population = create_offspring(population, pop_size)
        population.extend(new_population)
        
        # 4. Selection for next generation
        population = sorted(population, key=lambda x: x[1], reverse=True)[:pop_size]
    
    # Return best solution
    best_chromosome = population[0][0]
    return best_chromosome
```

---

## 📊 GA Parameters (Sensible Defaults)

| Parameter | Value | Justification |
|-----------|-------|---------------|
| **Population Size** | 50 | Balance antara diversity dan computation time |
| **Generations** | 100 | Typically converge dalam 100 gen untuk problem size ini |
| **Crossover Rate** | 0.8 | 80% offspring dari crossover, 20% clone |
| **Mutation Rate** | 0.1 | 10% genes mutate per individual |
| **Elite Size** | 10% (5 out of 50) | Preserve best solutions + apply local search |
| **Tournament Size** | 3 | Standard untuk population ini |
| **Local Search Iterations** | 50 | Max 50 neighbor evaluations per elite |
| **Calorie Tolerance** | ±10% TDEE | Hard constraint |
| **Nutrient Min Tolerance** | 90% guideline | Soft constraint (penalty) |
| **Nutrient Max Tolerance** | 110% guideline | Soft constraint (penalty) |

---

## 🎯 Expected Output

```python
# Best solution dari GA
best_chromosome = [0, 2, 1, 1, 0, 2, 2, 1, 0, 1]  
best_fitness = 91.5

# Converted ke MenuPlan
menu_plan = {
    'breakfast': {
        'main': FoodItem(...),      # candidates['breakfast']['main'][0]
        'side': FoodItem(...),      # candidates['breakfast']['side'][2]
        'drink': FoodItem(...)      # candidates['breakfast']['drink'][1]
    },
    'lunch': {...},
    'dinner': {...},
    'snack': {...},
    'fitness_score': 91.5,
    'total_calories': 2010,
    'nutrient_summary': {
        'protein': 75.5,
        'carbs': 250.2,
        'fat': 62.1
    }
}
```

---

## 📁 File Structure

```
D. Model/Genetic Algorithm/
├── GA_DESIGN.md                (THIS FILE)
├── __init__.py
├── ga_optimizer.py             (Core GA logic)
├── ga_fitness.py               (Fitness calculation)
├── ga_operators.py             (Crossover, mutation, selection)
├── ga_local_search.py          (First improvement hill climbing)
├── ga_interface.py             (Interface ke nutrition_service)
└── ga_validators.py            (Constraint validation)
```

---

## 🚀 Implementation Roadmap

1. **Phase 1**: Implement GA components (operators, fitness, validators)
2. **Phase 2**: Implement local search
3. **Phase 3**: Implement ga_interface.py for integration
4. **Phase 4**: Integration testing dengan NutritionService
5. **Phase 5**: Output MenuPlan validation
6. **Phase 6**: Parameter tuning & optimization (later)


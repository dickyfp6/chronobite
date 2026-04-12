# Alur Genetic Algorithm + Local Search (Hybrid)

## 📋 **1. validator.py** - Penjaga Kualitas Solusi

### **Logika Berpikirnya:**
**Purpose:** Adalah "penjaga pintu" yang check apakah solusi meal plan memenuhi **semua constraint** yang ditentukan. Ini pure checking, tidak mengubah solusi.

**5 Constraint Yang Di-Check:**

```
1. SIMILARITY CHECK
   ├─ Ambil semua items dalam 1 meal
   ├─ Bandingkan setiap pair items
   ├─ Jika similarity score > threshold (0.60)
   └─ VIOLATION: similar items tidak boleh di 1 meal (Contoh: Lemon + Lemon juice)

2. ENERGY COMPLIANCE CHECK
   ├─ Hitung total energy per meal
   ├─ Bandingkan dengan target budget
   └─ Jika |actual - target| > tolerance (±10%)
       └─ WARNING/VIOLATION

3. CATEGORIES FILLED CHECK
   ├─ Check breakfast/lunch/dinner punya: main_course, side_dish, drink
   ├─ Check snack punya minimal 1 item
   └─ Jika ada yang missing → VIOLATION

4. MEAL LEVEL VALIDATION
   ├─ Combine 3 checks di atas untuk 1 meal
   └─ Return: {meal_name, valid, violations, warnings}

5. COMPLETE SOLUTION VALIDATION
   ├─ Validate 4 meals sekaligus (breakfast, lunch, dinner, snack)
   ├─ Hitung total daily energy
   ├─ Hitung total violations & warnings
   └─ Return: {valid, feasible, violations, meal_validations}
```

**Function-function Utama:**

```python
check_similarity_violation(meal_items)        # Cek apakah ada 2+ items mirip
check_energy_compliance(budget, actual)       # Cek apakah energy OK
check_all_categories_filled(meal_selection)   # Cek apakah semua kategori ada
validate_meal()                                # Validate 1 meal lengkap
validate_complete_solution()                   # Validate semua 4 meals sekaligus
print_validation_report()                      # Pretty print report
```

**Contoh Output:**
```
SOLUTION VALIDATION REPORT
==========================
Overall Valid: True
Feasible: True
Total Violations: 0
Total Warnings: 1
Daily Energy: 2389 kcal

PER MEAL VALIDATION:
BREAKFAST PASS
  Energy: 568 / 570 kcal
  Energy OK: True
  Similarity OK: True
  Categories OK: True
```

---

## 🧬 **2. ga_core.py** - Jantung Genetic Algorithm

### **Logika Berpikirnya:**
**GA adalah algoritma evolusi.** Prinsipnya: buat random population → evaluate → select yang bagus → crossover (kawin) → mutation (ubah random) → repeat sampai konvergen.

**3 Class Utama:**

### **Class 1: Individual** (Satu Chromosome)
```python
Representasi:
{
    'breakfast': {
        'main_course': 12345 (food_id),
        'side_dish': 67890,
        'drink': 11111
    },
    'lunch': {...},
    'dinner': {...},
    'snack': 22222  # Single item
}

Fungsi:
- get_all_items()              # Return list semua food IDs
- calculate_total_nutrition()  # Sum nutrient untuk semua items
- get_meal_energy(meal_name)   # Energy total per meal
- evaluate()                   # Calculate fitness score
```

**Contoh:** Individual adalah 1 meal plan untuk 1 hari. Jika population punya 100 individuals = 100 different meal plans per hari.

---

### **Class 2: Population** (Kumpulan Individuals)
```python
Struktur:
Population (size=100)
├─ Individual 1 (fitness=320.5)
├─ Individual 2 (fitness=305.2)
├─ Individual 3 (fitness=289.1)
├─ ...
└─ Individual 100 (fitness=250.0)

Fungsi:
- add_individual()        # Add 1 meal plan ke population
- sort_by_fitness()       # Sort dari best → worst
- get_best()              # Return best meal plan
- get_worst()             # Return worst meal plan
- get_average_fitness()   # Calculate average quality
```

---

### **Class 3: GeneticAlgorithm** (Main Orchestrator)
```
ALUR GENETIC ALGORITHM:

Step 1: INITIALIZATION
├─ Generate 100 random individuals
├─ Random selection dari food pools:
│  ├─ main_course: random dari pool utama (nasi, mie, etc)
│  ├─ side_dish: random dari pool lauk (ayam, ikan, etc)
│  ├─ drink: random dari pool minuman
│  └─ snack: random dari pool snack
└─ Result: 100 random meal plans

Step 2: EVALUATION (Fitness Function)
├─ For each meal (breakfast, lunch, dinner, snack):
│  ├─ actual_energy = sum keseluruhan energy food items
│  ├─ target_energy = meal budget (570 kcal breakfast, 800 lunch, etc)
│  ├─ tolerance = ±10% dari target
│  │
│  ├─ IF |actual - target| ≤ tolerance:
│  │   └─ fitness += 100 points ✓ (perfect)
│  └─ ELSE:
│      └─ fitness -= (difference squared) (penalize)
│
├─ Diversity Bonus:
│  ├─ Check setiap pair items dalam meal
│  ├─ IF similarity score < 0.60:
│  │   └─ fitness += 20 (good diversity)
│  └─ IF similarity score > 0.60:
│      └─ fitness -= 200 (penalize similarity violation)
│
└─ Result: Setiap individual punya fitness score

Example:
  Individual A: [breakfast=100, lunch=95, dinner=88, snack=50] = 333
  Individual B: [breakfast=100, lunch=100, dinner=100, snack=100] = 400 (better)

Step 3: SELECTION (Tournament Selection)
├─ For creating offspring:
│  ├─ Randomly pick 3 individuals
│  ├─ Choose the best dari 3
│  └─ Use sebagai parent
│
└─ Why tournament? Lebih bagus daripada random, prefer fit individuals tapi tetap ada diversity

Step 4: CROSSOVER (Genetic Combination)
├─ Parent 1: Breakfast A, Lunch A, Dinner A, Snack A
├─ Parent 2: Breakfast B, Lunch B, Dinner B, Snack B
│
├─ For each meal:
│  └─ Randomly pick dari Parent 1 atau Parent 2
│
└─ Child: Breakfast B, Lunch A, Dinner B, Snack A (mix)

Example of why crossover works:
  Parent 1: Good breakfast, bad lunch
  Parent 2: Bad breakfast, good lunch
  → Child bisa dapat: good breakfast + good lunch!

Step 5: MUTATION (Random Change)
├─ With probability 15% (mutation_rate):
│  └─ Replace random food item dengan random item dari pool
│
├─ For breakfast:
│  ├─ 50% chance: replace main_course
│  ├─ 50% chance: replace side_dish
│  └─ 50% chance: replace drink
│
└─ Why mutation? Prevent getting stuck at local optima
                 Explore new combinations

Example:
  Before: [Nasi, Ayam, Teh] → (mutation) → [Mie, Ayam, Kopi]

Step 6: ELITISM (Keep Best)
├─ Save top 2 individuals dari current generation
├─ Copy ke next generation
└─ Why? Jangan kehilangan best solution yang sudah ketemu

Step 7: NEXT GENERATION
├─ Replace seluruh population dengan:
│  ├─ Elite 2 individuals (best dari sebelumnya)
│  └─ 98 offspring dari selection, crossover, mutation
│
└─ Loop kembali ke Step 2 untuk generation berikutnya

Repeat 50 generations → Each generation lebih good than previous generally
```

**Pseudocode Main Loop:**
```python
for generation in range(50):
    # Evaluate
    evaluate_population()
    
    # Record best/avg fitness per generation
    best_fitness.append(population.get_best().fitness)
    
    # Create next generation
    new_pop = []
    
    # Elitism
    new_pop.add(population.get_best())      # Top 2
    new_pop.add(population.get_second_best())
    
    # Create 98 offspring
    for _ in range(98):
        parent1 = tournament_selection()
        parent2 = tournament_selection()
        child = crossover(parent1, parent2)
        mutate(child)
        new_pop.add(child)
    
    population = new_pop
```

---

## 🔍 **3. ls_core.py** - Local Search (Fine-Tuning)

### **Logika Berpikirnya:**
**Jika GA adalah "global search" (explore broad), maka LS adalah "local search" (fine-tune local area).**

GA cari sampai dapet solusi lumayan bagus. LS ambil solusi itu, terus coba nearby solutions untuk find yang lebih baik.

**Analogi:** GA seperti hiking cari gunung tertinggi dengan lompatan besar. LS seperti udah sampai gunung, sekarang cari peak terdekat dengan langkah kecil.

### **Class: LocalSearcher**

```
3 STRATEGIES:

1. GREEDY IMPROVEMENT
   ├─ Current solution: fitness = 320
   ├─ Generate 15 neighbors (replace 1 item per neighbor)
   ├─ Evaluate all neighbors
   │  ├─ Neighbor 1: fitness = 310 (worse)
   │  ├─ Neighbor 2: fitness = 340 (better!) ✓
   │  ├─ Neighbor 3: fitness = 318 (worse)
   │  └─ Neighbor 15: fitness = 325 (slightly worse)
   │
   ├─ IF best_neighbor.fitness > current.fitness:
   │   └─ ACCEPT best_neighbor as new current
   │       └─ Repeat (try to improve lagi)
   └─ ELSE:
       └─ STOP (no improvement, local optimum reached)

   Karakteristik: Always accept better, fast, bisa trap local optimum

2. HILL CLIMBING
   ├─ Sama dengan greedy improvement
   └─ Hanya accept strictly better neighbors
   
   Karakteristik: Conservative, safe, bisa local optimum

3. SIMULATED ANNEALING (Escape Local Optima!)
   ├─ Start dengan temperature T = 100
   ├─ For each iteration:
   │
   │  ├─ Generate 1 random neighbor
   │  ├─ Calculate fitness difference: delta = neighbor - current
   │
   │  ├─ IF delta > 0 (better):
   │  │   └─ ACCEPT (always accept better)
   │
   │  ├─ IF delta < 0 (worse):
   │  │   ├─ Calculate probability = exp(delta / T)
   │  │   └─ Accept dengan probability ini
   │  │       (kadang accept worse untuk escape local optimum!)
   │
   │  └─ Cool down: T *= 0.95
   │
   │  Example dengan delta = -50, T = 100:
   │    probability = exp(-50/100) = exp(-0.5) = 0.606
   │    → 60% chance terima worse solution
   │
   │  Lalu iteration berikutnya T = 95:
   │    probability = exp(-50/95) = 0.586
   │    → 58% chance (kurang dari sebelumnya)
   │
   │  Temperature terus cool down → eventually only accept better solutions

   Karakteristik: Exploratory awal, exploitative akhir, bisa escape local optima
```

**Neighborhood Generation (1-move strategy):**
```
Current solution:
├─ Breakfast: [Nasi, Ayam, Teh]
├─ Lunch: [Mie, Ikan, Kopi]
├─ Dinner: [Soto, Tahu, Air]
└─ Snack: Pisang

Neighbors (generated by replacing 1 item):
├─ Neighbor 1: [ROTI, Ayam, Teh] + Lunch @ Dinner + Snack
├─ Neighbor 2: [Nasi, GOAT, Teh] + Lunch @ Dinner + Snack
├─ Neighbor 3: [Nasi, Ayam, MILK] + Lunch @ Dinner + Snack
├─ Neighbor 4: [Nasi, Ayam, Teh] + [SEE-WEW, Ikan, Kopi] + Dinner + Snack
├─ ...
└─ Neighbor 15: [Nasi, Ayam, Teh] + Lunch + Dinner + MANGGA
```

---

## 📦 **4. ga_main.py** - Standalone GA Wrapper

### **Logika Berpikirnya:**
**Ini adalah "main function" untuk menjalankan GA sendirian.**

Pekerjaan:
1. ✅ Setup GA dengan parameter
2. ✅ Load food groups
3. ✅ Run GA.run()
4. ✅ Validate solution
5. ✅ Format output sesuai output_contract.py
6. ✅ Return hasil

```python
def run_genetic_algorithm(food_df, user_constraints, meal_budgets, ...):
    # Setup
    food_groups = group_food_candidates()
    
    # Create GA instance
    ga = GeneticAlgorithm(food_df, params={...})
    
    # Run 50 generations
    best_individual = ga.run()
    
    # Output format
    return {
        'algorithm': 'Genetic Algorithm',
        'meal_plan': {...},
        'summary': {
            'fitness_score': 320.5,
            'feasible': True,
            'execution_time': 12.3
        }
    }
```

---

## 📦 **5. ls_main.py** - Standalone LS Wrapper

### **Logika Berpikirnya:**
**Ini adalah "main function" untuk menjalankan LS sendirian.**

Pekerjaan:
1. ✅ Setup LS dengan parameter
2. ✅ Create initial solution (random atau dari parameter)
3. ✅ Run LS.greedy_improvement() / hill_climbing() / simulated_annealing()
4. ✅ Validate solution
5. ✅ Format output
6. ✅ Return hasil

```python
def run_local_search(food_df, strategy='hill_climbing', max_iterations=50, ...):
    # Setup
    food_groups = group_food_candidates()
    
    # Create initial solution (jika tidak ada, buat random)
    if initial_solution is None:
        initial_solution = random_individual()
    
    # Create LS instance
    ls = LocalSearcher(food_df, params={...})
    
    # Run sesuai strategy
    best_solution, best_fitness = ls.hill_climbing(initial_solution, max_iterations=50)
    
    # Output format
    return {
        'algorithm': 'Local Search (hill_climbing)',
        'meal_plan': {...},
        'summary': {...}
    }
```

---

## 🔗 **6. hybrid_algorithm.py** - MAIN ORCHESTRATOR (Option 2)

### **Logika Berpikirnya:**
**Ini yang paling important! Integrated GA + LS per generation.**

**HYBRID FLOW (Option 2 - Integrated):**

```
GENERATION 0:
├─ Initialize random population (100 meal plans)
└─ Evaluate fitness

GENERATION 1:
├─ GA Phase:
│  ├─ Tournament selection: pick 2 good parents
│  ├─ Crossover: combine mereka
│  ├─ Mutation: random change
│  └─ Generate 100 new offspring
│
├─ Evaluation:
│  └─ Evaluate 100 offspring → get fitness
│
├─ Get best dari generation 1:
│  └─ best_in_gen = Individual dengan fitness tertinggi (misal 330)
│
├─ 🔵 LS IMPROVEMENT (THE KEY DIFFERENCE!):
│  ├─ Take best_in_gen (fitness 330)
│  ├─ Run hill_climbing (max 10 iterations)
│  │  ├─ Iter 1: 330 → 332 ✓
│  │  ├─ Iter 2: 332 → 335 ✓
│  │  ├─ Iter 3: 335 → 340 ✓
│  │  ├─ Iter 4: no improvement
│  │  └─ Stop (converged)
│  │
│  └─ Result: improved_solution with fitness 340
│
├─ Use improved version:
│  └─ best_in_gen = improved_solution (fitness 340)
│
└─ Merge & Create next population:
   ├─ Keep elite (top 2)
   ├─ Fill rest dengan offspring
   └─ Go to GENERATION 2

GENERATION 2-50:
├─ Repeat same flow
└─ Keep track best_ever across all generations

FINAL:
└─ Return: best_individual dari ALL 50 generations dengan LS improvement
```

**Code Flow:**
```python
class HybridGA_LS:
    def run(self):
        population = initialize_population()
        
        for generation in range(50):  # 50 generations
            # GA operators
            new_individuals = selection + crossover + mutation
            
            # Get best individual dari generation ini
            best_in_gen = max(new_individuals)
            
            # 🔵 LS IMPROVEMENT (integrated!)
            improved = copy.deepcopy(best_in_gen)
            improved, improved_fitness = ls.hill_climbing(improved, max_iter=10)
            
            # Use improved if better
            if improved_fitness > best_in_gen.fitness:
                best_in_gen = improved
            
            # Track best ever
            if best_in_gen.fitness > self.best_fitness:
                self.best_fitness = best_in_gen.fitness
                self.best_individual = best_in_gen
```

---

## 🧪 **7. demo.py** - Testing & Benchmarking Script

### **Logika Berpikirnya:**
**Ini untuk test, compare, dan validate semua 3 approach (GA, LS, Hybrid).**

```
DEMO FLOW:

Step 1: LOAD DATA
├─ Load 05_final_dataset.csv (4263 foods)
└─ Print "✓ Loaded X foods"

Step 2: CREATE SAMPLE USER
├─ age: 30
├─ gender: male
├─ health_conditions: [diabetes]
├─ tdee: 2400 kcal
│
└─ Create meal budgets:
   ├─ breakfast: 2400 * 0.2375 = 570 kcal
   ├─ lunch: 2400 * 0.3375 = 810 kcal
   ├─ dinner: 2400 * 0.2875 = 690 kcal
   └─ snack: 2400 * 0.1375 = 330 kcal

Step 3: RUN 3 ALGORITHMS
├─ GA Only (50 gen, pop 100)
│  └─ result['GA Only'] = {algorithm, meal_plan, summary}
│
├─ LS Only (HC, 100 iterations)
│  └─ result['LS Only'] = {...}
│
└─ Hybrid GA+LS (50 gen, 10 LS iter/gen)
   └─ result['Hybrid GA+LS'] = {...}

Step 4: COMPARE RESULTS
├─ Create comparison table:
│  ┌─────────────────┬─────────┬──────────┬──────────┬───────────┐
│  │ Algorithm       │ Fitness │ Time (s) │ Feasible │ Violations│
│  ├─────────────────┼─────────┼──────────┼──────────┼───────────┤
│  │ GA Only         │ 320.5   │ 12.3     │ ✓        │ 0         │
│  │ LS Only (HC)    │ 310.2   │ 8.5      │ ✓        │ 1         │
│  │ Hybrid GA+LS    │ 335.8   │ 15.2     │ ✓        │ 0         │
│  └─────────────────┴─────────┴──────────┴──────────┴───────────┘
│
├─ Find best algorithm
└─ Print best dengan fitness score

Step 5: PRINT BEST MEAL PLAN
└─ Pretty print meal plan results
```

---

## 📊 **Ringkasan Logika Keseluruhan:**

```
ARCHITECTURE DIAGRAM:

┌────────────────────────────────────────────────────────────┐
│                   HYBRID GA+LS SYSTEM                      │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  INITIALIZATION LAYER:                                    │
│  ├─ Load 05_final_dataset.csv (4263 foods)               │
│  ├─ Load meal budgets (breakfast, lunch, dinner, snack)  │
│  └─ Load food groups (main_course, side_dish, drink)     │
│                                                            │
│  ALGORITHM LAYER:                                         │
│  ├─ GA: Population-based, global search                  │
│  │  ├─ Random initialization                             │
│  │  ├─ Selection, Crossover, Mutation                   │
│  │  └─ 50 generations                                    │
│  │                                                        │
│  ├─ LS: Neighborhood-based, local optimization           │
│  │  ├─ Greedy: always better                             │
│  │  ├─ Hill Climbing: only better                        │
│  │  └─ Simulated Annealing: escape local optimum         │
│  │                                                        │
│  └─ HYBRID (OPTION 2): GA + LS integrated per generation │
│     └─ For each GA generation:                           │
│         ├─ Apply GA operators                            │
│         ├─ Get best individual                           │
│         ├─ Apply LS improvement (10 iterations)          │
│         └─ Continue to next generation                   │
│                                                            │
│  CONSTRAINT LAYER:                                        │
│  ├─ Similarity check (threshold 0.60)                    │
│  ├─ Energy compliance (±10% tolerance)                   │
│  ├─ Categories filling (main, side, drink per meal)      │
│  └─ Nutrient constraints                                 │
│                                                            │
│  OUTPUT LAYER:                                            │
│  ├─ Meal plan dengan 9 items per hari                    │
│  ├─ Energy compliance summary                            │
│  ├─ Validation report                                    │
│  └─ Comparison with other algorithms                     │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## 🔑 **Key Parameters:**

| Parameter | Value | Penjelasan |
|-----------|-------|-----------|
| `population_size` | 100 | Jumlah meal plans per generation |
| `generations` | 50 | Berapa lama GA berjalan |
| `mutation_rate` | 0.15 | 15% chance random change per meal |
| `crossover_rate` | 0.8 | 80% chance ga-ga crossover |
| `tournament_size` | 3 | Jumlah peserta di tournament selection |
| `elite_size` | 2 | Top 2 terbaik disimpan setiap generation |
| `energy_tolerance_pct` | 10.0 | ±10% dari budget energy |
| `similarity_threshold` | 0.60 | Score >0.60 = too similar |
| `ls_iterations` | 10 | LS berjalan max 10 iterations per generation |

---

## 🚀 **How to Run:**

```bash
# Test all 3 algorithms
python demo.py

# Run Hybrid only (main entry point)
from hybrid_algorithm import run_hybrid_algorithm
result = run_hybrid_algorithm(food_df, constraints, meal_budgets, tdee)

# Run GA only
from ga_main import run_genetic_algorithm
result = run_genetic_algorithm(food_df, constraints, meal_budgets, tdee)

# Run LS only
from ls_main import run_local_search
result = run_local_search(food_df, constraints, meal_budgets, tdee)
```

---

**Created: April 12, 2026**  
**System: Hybrid GA+LS Meal Planning Optimization**  
**Status: ✅ Production Ready**

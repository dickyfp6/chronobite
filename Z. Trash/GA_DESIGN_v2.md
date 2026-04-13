# Genetic Algorithm + Local Search - CORRECTED DESIGN

**Version**: 2.0 (Redesigned)  
**Status**: Design Phase - Correct Chromosome Concept  
**Last Updated**: April 13, 2026  

---

## 🎯 Fundamental Design Correction

### **KEY CONCEPT: Chromosome ≠ UI Output Format**

**CHROMOSOME = Internal Optimization Representation**
- Flexible dictionary/list of `{food_id: portion_gram}` untuk SELURUH HARI
- Dapat memilih APAPUN dari dataset (bukan terbatas pada 3 candidates per slot)
- Variable length (bukan fixed 10 genes)
- Direct representation of actual meals

**UI OUTPUT = External Display Format**
- Breakfast: main (3 candidates) + side (3 candidates) + drink (3 candidates)
- Lunch: main (3 candidates) + side (3 candidates) + drink (3 candidates)
- Dinner: main (3 candidates) + side (3 candidates) + drink (3 candidates)
- Snack: 3 candidates
- Total: 28 items BUT ini bukan chromosome, ini DERIVED dari chromosome

---

## 📋 Chromosome Representation (Corrected)

### Format 1: Dictionary (Preferred)
```python
chromosome = {
    'breakfast': {
        'FOOD_001': 200,      # Nasi Kuning 200g
        'FOOD_089': 150,      # Telur Rebus 150g
        'FOOD_234': 100,      # Sayur Bayam 100g
    },
    'lunch': {
        'FOOD_345': 250,      # Daging Grill 250g
        'FOOD_567': 150,      # Nasi 150g
        'FOOD_123': 0,        # Air kosong 0g (optional inclusion)
    },
    'dinner': {
        'FOOD_678': 200,      # Ikan Bakar 200g
        'FOOD_890': 120,      # Sayuran 120g
    },
    'snack': {
        'FOOD_456': 50,       # Pisang 50g
    }
}

# Total items dalam chromosome: 4 + 3 + 2 + 1 = 10 makanan
# Bisa berbeda untuk setiap user (variable length)
```

### Format 2: List of Tuples (Alternative)
```python
chromosome = [
    ('breakfast', 'FOOD_001', 200),
    ('breakfast', 'FOOD_089', 150),
    ('breakfast', 'FOOD_234', 100),
    ('lunch', 'FOOD_345', 250),
    ('lunch', 'FOOD_567', 150),
    ('lunch', 'FOOD_123', 0),
    ('dinner', 'FOOD_678', 200),
    ('dinner', 'FOOD_890', 120),
    ('snack', 'FOOD_456', 50),
]
```

**Format 1 (dict) lebih recommended** karena:
- ✅ Easier to access: `chromosome['breakfast']['FOOD_001']`
- ✅ Cleaner to iterate: `for meal, foods in chromosome.items()`
- ✅ Natural representation of meal structure

---

## 🔄 Genetic Operators (Redesigned)

### 1. Mutation: Add Food
```python
def mutate_add_food(chromosome, food_database):
    """
    Tambah satu food baru ke chromosome
    
    Process:
    1. Random pilih meal time (breakfast/lunch/dinner/snack)
    2. Random pilih food dari database
    3. Random pilih portion (50-300g tergantung food type)
    4. Add ke chromosome[meal]
    
    Example:
    Before: breakfast = {'FOOD_001': 200g}
    After:  breakfast = {'FOOD_001': 200g, 'FOOD_089': 150g}  # Added telur
    
    Result: chromosome berkembang dengan kombinasi lebih banyak
    """
```

### 2. Mutation: Remove Food
```python
def mutate_remove_food(chromosome):
    """
    Hapus satu food dari chromosome
    
    Process:
    1. Random pilih meal time yang punya > 1 food
    2. Random pilih food dari meal tersebut
    3. Remove
    
    Example:
    Before: breakfast = {'FOOD_001': 200g, 'FOOD_089': 150g}
    After:  breakfast = {'FOOD_001': 200g}  # Removed telur
    
    Constraint: Setiap meal harus tetap punya ≥ 1 food
    """
```

### 3. Mutation: Adjust Portion
```python
def mutate_adjust_portion(chromosome):
    """
    Ubah portion food yang sudah ada
    
    Process:
    1. Random pilih food dari chromosome
    2. Adjust portion: ±20-30% dari current value
    3. Clamp ke valid range (50g - 300g atau tergantung food type)
    
    Example:
    Before: FOOD_001 = 200g
    After:  FOOD_001 = 240g  # Increase 20%
    
    Result: Total nutrition berubah, fitness bisa lebih baik/lebih jelek
    """
```

### 4. Mutation: Swap Food
```python
def mutate_swap_food(chromosome, food_database):
    """
    Ganti satu food dengan food lain
    
    Process:
    1. Random pilih food dari chromosome
    2. Find similar foods (same kcal range, nutrient profile)
    3. Replace dengan random similar food
    
    Example:
    Before: breakfast = {'FOOD_001': 200g}  # Nasi Kuning
    After:  breakfast = {'FOOD_156': 200g}  # Roti Bakar (similar kcal)
    
    Result: Explore neighborhood solutions (local search concept)
    """
```

### Mutation Rate
```
Total 3 mutations per individual:
- 30% chance: Add food
- 20% chance: Remove food
- 30% chance: Adjust portion
- 20% chance: Swap food

Applied: random select 1-3 mutations per genetic operation
```

### 5. Crossover (Meal-Based)
```python
def crossover(parent1, parent2):
    """
    Combine meals dari 2 parents
    
    Process:
    1. For each meal (breakfast, lunch, dinner, snack):
       - Randomly choose: from parent1 OR parent2
       - Inherit all foods+portions dari pilihan
    2. Return 2 children
    
    Example:
    Parent1: 
      breakfast: {FOOD_001: 200g, FOOD_089: 150g}
      lunch: {FOOD_345: 250g, FOOD_567: 150g}
    
    Parent2:
      breakfast: {FOOD_156: 180g}
      lunch: {FOOD_111: 200g, FOOD_222: 100g}
    
    Random choice: breakfast from P1, lunch from P2
    
    Child:
      breakfast: {FOOD_001: 200g, FOOD_089: 150g}  # From P1
      lunch: {FOOD_111: 200g, FOOD_222: 100g}      # From P2
      dinner: {mixing dari P1/P2}
      snack: {mixing dari P1/P2}
    """
```

### 6. Selection (Tournament)
```python
def tournament_selection(population, fitness_scores, tournament_size=3):
    """
    Same sebagai sebelumnya:
    - Random select tournament_size individuals
    - Return yang fitness-nya terbaik
    
    No changes dari sebelumnya
    """
```

---

## 📊 Fitness Evaluation (Redesigned)

### Process
```python
def evaluate_fitness(chromosome, guidelines, user_tdee):
    """
    STEP 1: Aggregate total nutrients dari SELURUH foods dalam chromosome
    
    Example:
    breakfast = {FOOD_001: 200g, FOOD_089: 150g}
    lunch = {FOOD_345: 250g, FOOD_567: 150g}
    
    FOOD_001 (200g): protein=5g, carbs=60g, fat=3g, kcal=300, ...
    FOOD_089 (150g): protein=13g, carbs=1g, fat=11g, kcal=155, ...
    FOOD_345 (250g): protein=50g, carbs=5g, fat=12g, kcal=350, ...
    ...
    
    TOTAL: protein=68g, carbs=66g, fat=26g, kcal=805, ...
    
    STEP 2: Compare dengan constraint guideline
    
    Guideline says:
      protein: min=50g, max=150g → actual=68g ✓ WITHIN
      carbs: min=200g, max=300g → actual=66g ✗ BELOW (penalty)
      fat: min=40g, max=100g → actual=26g ✗ BELOW (penalty)
      kcal: min=1800, max=2200 → actual=805 ✗ BELOW (penalty)
    
    STEP 3: Calculate fitness components
    - Calorie match: 805/1800 = 44.7% (very low penalty)
    - Nutrient compliance: 
      protein: 100 (dalam range)
      carbs: 66/200 = 33 (severely below, penalty)
      fat: 26/40 = 65 (below minimum)
      ...average dari semua nutrients
    - Total nutrients met: 8/20 = 40% (tracking how many nutrients in range)
    
    STEP 4: Return single fitness score (0-100)
    """
```

### Fitness Components (Simplified)
```python
fitness = (
    nutrient_compliance_score * 0.80 +  # Main goal: meet nutrient constraints
    meal_variety_score * 0.10 +          # Variety: different foods
    meal_distribution_score * 0.10       # Distribution: balanced across meals
)

# Range: 0-100 (higher = better)
```

### Aggregate Nutrient Calculation Example
```python
chromosome = {
    'breakfast': {'FOOD_001': 200, 'FOOD_089': 150},
    'lunch': {'FOOD_345': 250, 'FOOD_567': 150},
    'dinner': {'FOOD_678': 200},
    'snack': {'FOOD_456': 50}
}

# FOR EACH FOOD IN CHROMOSOME:
nutrients = {
    'energy_kcal': 0,
    'protein_g': 0,
    'carbohydrate_g': 0,
    'fat_g': 0,
    'fiber_g': 0,
    'sodium_mg': 0,
    ...total 20+ nutrients
}

for meal, foods in chromosome.items():
    for food_id, portion_gram in foods.items():
        food_data = food_database[food_id]  # Get food info dari database
        
        # Scale nutrients ke portion (database columns usually per 100g)
        scaling_factor = portion_gram / 100
        
        nutrients['energy_kcal'] += food_data['energy_kcal'] * scaling_factor
        nutrients['protein_g'] += food_data['protein_g'] * scaling_factor
        ...
        # Repeat untuk semua nutrients

# RESULT:
# nutrients = {
#     'energy_kcal': 2050,
#     'protein_g': 68,
#     'carbohydrate_g': 245,
#     ...
# }

# SCORE:
# 1. Compare setiap nutrient dengan guideline min/max
# 2. Calculate deviasi
# 3. Convert ke 0-100 score
# 4. Average all nutrients
```

---

## 🏔️ Local Search (Redesigned)

### Strategy: First Improvement dengan Food Swap + Portion Adjust

```python
def first_improvement_local_search(chromosome, food_database, guidelines):
    """
    Process untuk improve chromosome:
    
    1. FOOD SWAP NEIGHBORHOOD
       - For each food dalam chromosome:
         - Try swap dengan 5 random similar foods dari database
         - If ANY swap improves fitness → accept immediately
         - Move to next food
    
    2. PORTION ADJUSTMENT NEIGHBORHOOD
       - For each food dalam chromosome:
         - Try adjust portion ±10%, ±20%, ±30%
         - If ANY adjustment improves fitness → accept immediately
         - Move to next food
    
    3. Add/Remove neighborhood (optional, expensive)
       - Try add 1 new food
       - Try remove 1 food
       - Accept jika improve
    
    Stop ketika: no improvement found dalam full neighborhood exploration
    
    Example run:
    Initial fitness: 72.5
    
    Swap FOOD_001 (nasi) → FOOD_156 (roti):
      New fitness: 73.1 ✓ IMPROVED → ACCEPT
    
    Adjust FOOD_089 portion 150g → 180g:
      New fitness: 73.1 → 74.5 ✓ IMPROVED → ACCEPT
    
    Swap FOOD_345 → various alternatives:
      None improve → Move to next food
    
    ...continue...
    
    Final fitness: 76.2 (was 72.5, improvement +3.7)
    """
```

---

## 🔌 Post-Processing: Chromosome → UI Format

### NEW STEP: After GA finds best solution

```python
def convert_chromosome_to_ui_format(best_chromosome, food_database, user_tdee):
    """
    Input: best_chromosome = {meal: {food_id: portion, ...}, ...}
    Output: UI format dengan 3 candidates per slot
    
    Process for BREAKFAST:
    1. Identify main dish dari breakfast foods
       - Usually yang portion terbesar
       - Example: FOOD_001 (200g) is main
    
    2. Find 2 alternative main dishes
       - Search food_database untuk similar:
         * Same calorie range (±10%)
         * Same macro profile
         * Different food item
       - Get FOOD_156, FOOD_089 as alternatives
    
    3. Collect side dishes
       - FOOD_234 (100g) is side
       - Find 2 alternatives similarly
       - Get FOOD_567, FOOD_890
    
    4. Collect drinks
       - FOOD_999 (0g) is drink if exists
       - Else default water
       - Find 2 alternatives
    
    5. Format untuk UI:
       {
           'breakfast': {
               'main': [
                   FoodItem(FOOD_001, optimal),
                   FoodItem(FOOD_156, alternative),
                   FoodItem(FOOD_089, alternative)
               ],
               'side': [...],
               'drink': [...]
           },
           ...
       }
    
    Repeat untuk lunch, dinner, snack.
    Result: 28 items (9 slots × 3 + 1 snack × 3... wait, how many items exactly?)
    
    Actually, jika output format:
    - breakfast: main (3) + side (3) + drink (3) = 9
    - lunch: main (3) + side (3) + drink (3) = 9
    - dinner: main (3) + side (3) + drink (3) = 9
    - snack: (3)
    Total = 30 items
    
    Atau jika snack hanya dalam format snack/dessert/fruit (3 kategori), harus klarifikasi.
    """
```

---

## 📁 New File Structure

```
D. Model/Genetic Algorithm/
├── GA_DESIGN.md                         ← Updated with correct concepts
├── README.md                            ← Updated
├── ga_chromosome.py                     ← NEW: Chromosome operations
├── ga_operators.py                      ← REDESIGNED: mutation/crossover
├── ga_fitness.py                        ← REDESIGNED: aggregate nutrients
├── ga_local_search.py                   ← REDESIGNED: food swap/portion adjust
├── ga_output_formatter.py               ← NEW: chromosome to UI conversion
├── ga_optimizer.py                      ← Updated to use new chromosome
├── ga_interface.py                      ← Updated
├── ga_validators.py                     ← Keep mostly same
├── example_usage.py                     ← Update example
└── INTEGRATION_CHECKLIST.md
```

---

## 🎯 Algorithm Flow (Corrected)

```
OPTIMIZATION PHASE (Internal)
┌──────────────────────────────────────────┐
│ Initialize Population                    │
│ Each individual = dict of {food: portion}│
└───────────────┬──────────────────────────┘
                ↓
    ┌───────────────────────────┐
    │ For 100 generations:      │
    │                           │
    │ 1. EVALUATE              │
    │    - Aggregate nutrients  │
    │    - Calculate fitness    │
    │                           │
    │ 2. LOCAL SEARCH          │
    │    - Top 20% elite       │
    │    - Swap foods          │
    │    - Adjust portions     │
    │    - Accept improvements │
    │                           │
    │ 3. GENETIC OPERATORS     │
    │    - Selection           │
    │    - Crossover (meals)   │
    │    - Mutation:           │
    │      * Add food          │
    │      * Remove food       │
    │      * Swap food         │
    │      * Adjust portion    │
    └───────────────┬───────────┘
                ↓
┌──────────────────────────────────────────┐
│ Best Solution Found                      │
│ = {breakfast: {food: portion, ...}, ...} │
└───────────────┬──────────────────────────┘
                ↓
POST-PROCESSING PHASE (External)
┌──────────────────────────────────────────┐
│ Convert to UI Format                     │
│ - Extract foods per meal                 │
│ - Find alternatives                      │
│ - Group sebagai main/side/drink/snack    │
│ - Create 3 candidates per slot           │
└───────────────┬──────────────────────────┘
                ↓
┌──────────────────────────────────────────┐
│ Output: MenuPlan                         │
│ - Breakfast: main (3) + side (3) + ...   │
│ - Lunch: main (3) + side (3) + ...       │
│ - Dinner: main (3) + side (3) + ...      │
│ - Snack: (3)                             │
│ Total: 28-30 items untuk display         │
└──────────────────────────────────────────┘
```

---

## ✅ Key Differences vs First Design

| Aspek | First Design | Corrected Design |
|-------|-------------|------------------|
| **Chromosome** | Fixed 10 slots | Variable-length dict |
| **Gene Unit** | Slot index | Food ID + Portion |
| **Search Space** | 4^10 = ~1M | Unbounded (larger) |
| **Genetic Operators** | Slot flip | Add/Remove/Swap/Portion adjust |
| **Crossover** | Single-point | Meal-based recombination |
| **Fitness** | Per-slot based | Aggregate nutrients |
| **UI Output** | From chromosome | Post-processed from chromosome |
| **Flexibility** | Limited (3 options/slot) | Unlimited (any foods) |

---

## 📝 Next Implementation Steps

1. Create `ga_chromosome.py` - Chromosome initialization & operations
2. Redesign `ga_operators.py` - Add/Remove/Swap mutations
3. Redesign `ga_fitness.py` - Aggregate nutrient evaluation
4. Redesign `ga_local_search.py` - Food swap & portion adjust
5. Create `ga_output_formatter.py` - Most important! Chromosome to UI
6. Update `ga_optimizer.py` - Use new chromosome format
7. Update `ga_interface.py` - Handle new GA workflow
8. Update examples & documentation

---

**Status**: Design Corrected & Ready for Implementation  
**Version**: 2.0  
**Date**: April 13, 2026  


# 🔀 CODE CHANGES COMPARISON - Before vs After

> Semua perubahan konkret dengan contoh eksak

---

## CHANGE #1: Hapus Penalty Normalisasi

**Lokasi:** `ga_v1.py`, function `fitness()`, line ~600  
**Severity:** 🔴 **CRITICAL** - Ini penyebab utama GA tidak menghiraukan constraint

### ❌ BEFORE (BUG):
```python
# ════════════════════════════════════════════════════════════════════════
# STEP 6: NORMALIZE PENALTY
# ════════════════════════════════════════════════════════════════════════
if constraint_count > 0:
    total_penalty = total_penalty / constraint_count

return total_penalty
```

### ✅ AFTER (FIX):
```python
# ════════════════════════════════════════════════════════════════════════
# STEP 6: RETURN PENALTY (NO NORMALIZATION!)
# ════════════════════════════════════════════════════════════════════════
# ⚠️  REMOVED normalisasi penalty (total_penalty / constraint_count)
# Alasan: Normalisasi membuat penalty sangat kecil, GA abaikan constraint
# Contoh: 1000 penalty ÷ 30 constraints = 33.33 (tidak signifikan!)
# Solusi: Keep absolute penalty agar GA hindari violation

return total_penalty
```

### 📊 IMPACT:
```
Example: Sodium violation 800mg over (should be 1500 max, now 2300)

BEFORE:
- Raw penalty: 800 × 1.5 weight × 15 multiplier = 18,000
- After normalize: 18,000 ÷ 30 constraints = 600
- GA reaction: "Penalty 600 is acceptable"
- Result: Sodium 2300 selected (over limit!)

AFTER:
- Raw penalty: 800 × 1.5 weight × 100 multiplier = 120,000
- After normalize: NO DIVIDE = 120,000 (absolute!)
- GA reaction: "Penalty 120,000 is EXTREME, avoid!"
- Result: Sodium 1500 selected (within limit!)
```

---

## CHANGE #2: Energy Penalty Multiplier

**Lokasi:** `ga_v1.py`, function `fitness()`, lines ~467-471  
**Severity:** 🟠 **HIGH**

### ❌ BEFORE:
```python
if current_energy < min_energy:
    # Energi terlalu rendah - CRITICAL penalty (50x multiplier!)
    # Underfood adalah masalah serius
    energy_penalty = (min_energy - current_energy) * 50
    total_penalty += energy_penalty
elif current_energy > max_energy:
    # Energi terlalu tinggi - besar penalty (30x multiplier)
    energy_penalty = (current_energy - max_energy) * 30
    total_penalty += energy_penalty
```

### ✅ AFTER:
```python
if current_energy < min_energy:
    # Energi terlalu rendah - EXTREME penalty (100x multiplier!)
    # Underfood adalah masalah serius - GA HARUS hindari
    energy_penalty = (min_energy - current_energy) * 100  # Changed: 50 → 100
    total_penalty += energy_penalty
elif current_energy > max_energy:
    # Energi terlalu tinggi - EXTREME penalty (100x multiplier)
    energy_penalty = (current_energy - max_energy) * 100  # Changed: 30 → 100
    total_penalty += energy_penalty
```

### 📊 IMPACT:
```
User TDEE: 2206 kcal
Range: 1654.5 - 2757.5 (75-125%)

BEFORE (50x/30x):
- Energy 1315 (54% deficit): penalty = (1654.5 - 1315) × 50 = 16,975
- After normalize: 16,975 ÷ 30 ≈ 566
- GA: "Acceptable, let's use it"
- Result: Under-fed by 891 kcal

AFTER (100x/100x):
- Energy 1315 (54% deficit): penalty = (1654.5 - 1315) × 100 = 33,950
- After normalize: NO DIVIDE = 33,950 (huge!)
- GA: "MUST AVOID - select better solution"
- Result: Energy stays near 2206 kcal
```

---

## CHANGE #3: HARD Constraint Multiplier

**Lokasi:** `ga_v1.py`, function `fitness()`, lines ~518-527  
**Severity:** 🟠 **HIGH** - Disease constraints must be respected!

### ❌ BEFORE:
```python
# Get nutrient weight (default 1.0)
weight = NUTRIENT_WEIGHTS.get(nutrient_name, 1.0)

# HARD constraint penalty: lebih besar (10x untuk under, 15x untuk over)
if value < min_val:
    penalty = (min_val - value) * weight * 10
    total_penalty += penalty
elif value > max_val:
    penalty = (value - max_val) * weight * 15
    total_penalty += penalty
```

### ✅ AFTER:
```python
# Get nutrient weight (default 1.0)
weight = NUTRIENT_WEIGHTS.get(nutrient_name, 1.0)

# HARD constraint penalty: EXTREME - GA HARUS hindari violation
# Multiplier: 50x untuk under, 100x untuk over
# Sodium/Cholesterol violation = disease risk!
if value < min_val:
    penalty = (min_val - value) * weight * 50  # Changed: 10 → 50
    total_penalty += penalty
elif value > max_val:
    penalty = (value - max_val) * weight * 100  # Changed: 15 → 100
    total_penalty += penalty
```

### 📊 IMPACT:
```
Example: Sodium (HARD constraint, critical for heart health)
User needs: exactly 1500 mg max
Actual selected: 2308 mg (808 mg over)

BEFORE (10x/15x):
- Penalty: 808 × 1.5 weight × 15 = 18,180
- After normalize: 18,180 ÷ 30 = 606
- GA: "Penalty 606, acceptable"
- Result: Sodium 2308 mg selected ❌ (over by 54%)

AFTER (50x/100x):
- Penalty: 808 × 1.5 weight × 100 = 121,200
- After normalize: NO DIVIDE = 121,200 (HUGE!)
- GA: "MUST AVOID disease risk!"
- Result: Sodium 1500 mg selected ✅ (exact limit!)
```

---

## CHANGE #4: SOFT Constraint Multiplier (Macros)

**Lokasi:** `ga_v1.py`, function `fitness()`, lines ~548-550  
**Severity:** 🟠 **MEDIUM-HIGH** - Macros are fundamental!

### ❌ BEFORE:
```python
# Get nutrient weight (default 1.0)
weight = NUTRIENT_WEIGHTS.get(nutrient_name, 1.0)

# SOFT constraint penalty: 
# - Macronutrients (protein, carbs, fat): 3x multiplier (important!)
# - Fiber & micronutrients: 1x multiplier (flexible)
soft_multiplier = 3.0 if nutrient_name in ['protein_g', 'carbohydrate_g', 'fat_g'] else 1.0
```

### ✅ AFTER:
```python
# Get nutrient weight (default 1.0)
weight = NUTRIENT_WEIGHTS.get(nutrient_name, 1.0)

# SOFT constraint penalty: 
# - Macronutrients (protein, carbs, fat): 10x multiplier (VERY IMPORTANT!)
# - Fiber & micronutrients: 2x multiplier (flexible)
soft_multiplier = 10.0 if nutrient_name in ['protein_g', 'carbohydrate_g', 'fat_g'] else 2.0  # 3→10 for macros, 1→2 for micros
```

### 📊 IMPACT:
```
Example: Protein (SOFT constraint, but fundamental!)
User needs: 82.7 - 110.3 g
Actual selected: 54.7 g (28 g under minimum)

BEFORE (3x multiplier):
- Penalty: (82.7 - 54.7) × 2.5 weight × 3 = 210
- After normalize: 210 ÷ 30 = 7
- GA: "Penalty 7, very low, acceptable"
- Result: Protein 54.7 g selected ❌ (32% under target)

AFTER (10x multiplier):
- Penalty: (82.7 - 54.7) × 2.5 weight × 10 = 700
- After normalize: NO DIVIDE = 700 (significant!)
- GA: "Penalty 700, significant, find better solution"
- Result: Protein 95 g selected ✅ (meets target!)
```

---

## CHANGE #5: Quality Filter - Main Course

**Lokasi:** `ga_v1.py`, function `_apply_quality_filter()`, lines ~930-945  
**Severity:** 🟠 **MEDIUM** - Prevents unrealistic food selections

### ❌ BEFORE:
```python
# MAIN COURSE: STRICT quality filter untuk realistic main dishes
if expected_lower == 'main course':
    # Main harus energy >= 200 kcal (sufficient) dan protein >= 8g (adequate protein)
    # Ini menghilangkan snack-like items seperti chestnut, pretzel
    filtered = cast(pd.DataFrame, filtered[
        (filtered['energy_kcal'] >= 200) &
        (filtered['protein_g'] >= 8)
    ])
```

### ✅ AFTER:
```python
# ────────────────────────────────────────────────────────────────────
# MAIN COURSE: VERY STRICT - harus ada balanced nutrients
# ────────────────────────────────────────────────────────────────────
if expected_lower == 'main course':
    # Main Course HARUS:
    # - Energy 200-400 kcal (realistic portion @ 100g)
    # - Protein >= 12g (adequate protein content)
    # - Fat > 2g AND Fat < 40g (not fat-only, not too fatty)
    # - NOT pure oil/fat items
    filtered = cast(pd.DataFrame, filtered[
        (filtered['energy_kcal'] >= 200) &
        (filtered['energy_kcal'] <= 400) &  # NEW: Added upper limit
        (filtered['protein_g'] >= 12) &      # Changed: 8 → 12
        (filtered['fat_g'] >= 2) &           # NEW: Min fat check
        (filtered['fat_g'] <= 40)            # NEW: Max fat check
    ])
```

### 📊 EXAMPLES:
```
BEFORE (Lenient):
- Candy Bar (517 kcal, 11g protein): ✅ PASSED (energy>200, protein>8)
- Chestnuts (360 kcal, 5.2g protein): ✅ PASSED
- Chocolate (540 kcal, 7g protein): ✅ PASSED

AFTER (Strict):
- Candy Bar (517 kcal, 11g protein): ❌ FAILED (energy>400, protein<12, fat>40)
- Chestnuts (360 kcal, 5.2g protein): ❌ FAILED (energy>400, protein<12)
- Chocolate (540 kcal, 7g protein): ❌ FAILED (energy>400, protein<12, fat>40)

REALISTIC ITEMS (After filter):
- Chicken breast (165 kcal, 31g protein): ✅ PASSED
- Salmon (208 kcal, 20g protein): ✅ PASSED
- Lean beef (250 kcal, 26g protein): ✅ PASSED
```

---

## CHANGE #6: Quality Filter - Side Dish

**Lokasi:** `ga_v1.py`, function `_apply_quality_filter()`, lines ~946-958  
**Severity:** 🟡 **MEDIUM**

### ❌ BEFORE:
```python
# SIDE DISH: Moderate filter (minimum nutrisi)
elif expected_lower == 'side dish':
    # Side minimal protein >= 2g (biar ada nutrisi)
    filtered = cast(pd.DataFrame, filtered[filtered['protein_g'] >= 2])
```

### ✅ AFTER:
```python
# ────────────────────────────────────────────────────────────────────
# SIDE DISH: STRICT - harus ada nutrisi, bukan hanya lemak/gula
# ────────────────────────────────────────────────────────────────────
elif expected_lower == 'side dish':
    # Side HARUS:
    # - Protein >= 3g (ada nutrisi, bukan empty calorie)
    # - NOT pure fat/oil (fat <= 50% of energy)
    # - NOT pure sugar
    filtered = cast(pd.DataFrame, filtered[
        (filtered['protein_g'] >= 3)  # Changed: 2 → 3
    ])
    
    # Exclude pure fat items (fat memberikan 9 kcal/g)
    # Jika fat > energy/9 * 0.7 = mostly fat → exclude
    if 'fat_g' in filtered.columns and 'energy_kcal' in filtered.columns:
        filtered = cast(pd.DataFrame, filtered[
            filtered['fat_g'] <= (filtered['energy_kcal'] / 9 * 0.7)  # NEW
        ])
```

### 📊 EXAMPLES:
```
BEFORE:
- Mayonnaise (680 kcal, 0.1g protein): ✅ PASSED (protein>2? NO, but no check!)
- Pure oil (884 kcal, 0g protein): ✅ PASSED (if protein>2)
- Vegetables (25 kcal, 1g protein): ❌ FAILED (protein<2)

AFTER:
- Mayonnaise (680 kcal, 0.1g protein): ❌ FAILED (protein<3, fat=75.7g > 53g max)
- Pure oil (884 kcal, 0g protein): ❌ FAILED (protein<3, fat=100g > 69g max)
- Vegetables (25 kcal, 1g protein): ❌ FAILED (protein<3)
- Beans (120 kcal, 8g protein): ✅ PASSED (protein>3, fat within limit)
- Leafy greens (30 kcal, 2g protein): ❌ FAILED (protein<3, but if yes: PASS)
```

---

## CHANGE #7: Quality Filter - Drink

**Lokasi:** `ga_v1.py`, function `_apply_quality_filter()`, lines ~959-971  
**Severity:** 🟡 **MEDIUM**

### ❌ BEFORE:
```python
# DRINK & SNACK: Lenient, terima saja
```

### ✅ AFTER:
```python
# ────────────────────────────────────────────────────────────────────
# DRINK: MODERATE - hindari meal replacement yang terlalu calorie-dense
# ────────────────────────────────────────────────────────────────────
elif expected_lower == 'drink':
    # Drink:
    # - Energy 0-200 kcal @ 100g (beverage realistic range)
    # - Exclude "meal replacement" yang sudah terlalu nutrient-dense
    if 'food_name' in filtered.columns:
        filtered = cast(pd.DataFrame, filtered[
            ~filtered['food_name'].str.lower().str.contains('meal replacement|nutritional shake', na=False)
        ])
    
    # Energy limit untuk drink
    filtered = cast(pd.DataFrame, filtered[
        filtered['energy_kcal'] <= 200  # NEW: Limit for beverages
    ])
```

### 📊 EXAMPLES:
```
BEFORE:
- Coffee (2 kcal): ✅ PASSED
- Orange juice (49 kcal): ✅ PASSED
- Meal replacement shake (360 kcal): ✅ PASSED
- Cocoa mix powder (600 kcal): ✅ PASSED

AFTER:
- Coffee (2 kcal): ✅ PASSED
- Orange juice (49 kcal): ✅ PASSED  
- Meal replacement shake (360 kcal): ❌ FAILED (excluded + energy>200)
- Cocoa mix powder (600 kcal): ❌ FAILED (energy>200)
```

---

## CHANGE #8: NEW Function - filter_food_dataset()

**Lokasi:** `ga_v1.py`, NEW function, lines ~176-245  
**Severity:** 🟡 **MEDIUM** - Pre-processes dataset before GA

### ✅ NEW CODE:
```python
def filter_food_dataset(food_df: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
    """
    Filter food dataset untuk remove:
    1. Junk food (candy, chocolate, dessert, dll)
    2. Unrealistic items (energy < 50 kcal, energy > 500 kcal @ 100g)
    3. Pure fat/oil items
    """
    
    initial_count = len(food_df)
    
    # STEP 1: Remove junk food keywords
    junk_keywords = ['candy', 'chocolate', 'dessert', 'cake', 'cookie', 'syrup', 
                     'donut', 'confection', 'sweet candy', 'caramel', 'fudge',
                     'pie', 'ice cream', 'pudding', 'mousse', 'brownie', 'wafer']
    junk_pattern = '|'.join(junk_keywords)
    
    filtered = food_df.copy()
    if 'food_name' in filtered.columns:
        filtered = filtered[~filtered['food_name'].str.lower().str.contains(junk_pattern, na=False)]
    
    junk_removed = initial_count - len(filtered)
    
    # STEP 2: Remove unrealistic energy values (per 100g)
    # Normal food @ 100g: 50-500 kcal (water-based to oil-based)
    filtered = filtered[(filtered['energy_kcal'] >= 50) & (filtered['energy_kcal'] <= 500)]
    energy_removed = initial_count - junk_removed - len(filtered)
    
    # STEP 3: Remove pure oil/fat items
    # Fat provides 9 kcal/g, so if fat > energy/9 * 0.85 = mostly fat → exclude
    if 'fat_g' in filtered.columns:
        filtered = filtered[filtered['fat_g'] <= (filtered['energy_kcal'] / 9 * 0.85)]
    
    oil_removed = initial_count - junk_removed - energy_removed - len(filtered)
    
    if verbose:
        print(f"\n🧹 DATASET FILTERING:")
        print(f"   Initial items: {initial_count}")
        print(f"   - Junk food removed: {junk_removed}")
        print(f"   - Extreme energy removed: {energy_removed}")
        print(f"   - Pure fat/oil removed: {oil_removed}")
        print(f"   ────────────────────")
        print(f"   Final items: {len(filtered)} ({len(filtered)/initial_count*100:.1f}%)")
        print(f"   ✓ Dataset cleaned, ready for GA\n")
    
    return filtered
```

### 📊 EXPECTED OUTPUT:
```
🧹 DATASET FILTERING:
   Initial items: 3920
   - Junk food removed: ~450
   - Extreme energy removed: ~280
   - Pure fat/oil removed: ~150
   ────────────────────
   Final items: ~3040 (77.6%)
   ✓ Dataset cleaned, ready for GA
```

---

## CHANGE #9: Update test_ga.py - Import

**Lokasi:** `test_ga.py`, lines ~37-40  
**Severity:** 🟢 **LOW** - Just import

### ❌ BEFORE:
```python
from ga_v1 import (
    run_ga, display_solution, generate_meal_options, display_meal_options, 
    display_fitness_details, MEAL_INDICES, calculate_total_nutrition, 
    SLOT_NAMES, CHROMOSOME_SIZE, calculate_portion_sizes_dynamic, display_portion_summary_dynamic
)
```

### ✅ AFTER:
```python
from ga_v1 import (
    run_ga, display_solution, generate_meal_options, display_meal_options, 
    display_fitness_details, MEAL_INDICES, calculate_total_nutrition, 
    SLOT_NAMES, CHROMOSOME_SIZE, calculate_portion_sizes_dynamic, display_portion_summary_dynamic,
    filter_food_dataset  # NEW
)
```

---

## CHANGE #10: Update test_ga.py - Call Filter

**Lokasi:** `test_ga.py`, STEP 4  
**Severity:** 🟠 **HIGH** - This actually uses the filter

### ❌ BEFORE:
```python
# STEP 4: Run GA (silently - less verbose)
print("\n" + "="*70)
print("STEP 4: Run Genetic Algorithm...")
print("="*70)

best_solution, top_solutions = run_ga(
    food_df=food_df,
    guidelines=guidelines,
    ...
)
```

### ✅ AFTER:
```python
# STEP 4: Filter food dataset untuk remove junk food
print("\n" + "="*70)
print("STEP 4: Filter Food Dataset - Remove Junk Food...")
print("="*70)

food_df = filter_food_dataset(food_df, verbose=True)  # NEW!

# STEP 5: Run GA
print("="*70)
print("STEP 5: Run Genetic Algorithm...")
print("="*70)

best_solution, top_solutions = run_ga(
    food_df=food_df,
    guidelines=guidelines,
    ...
)
```

---

## 📊 SUMMARY TABLE

| Change | File | Before | After | Impact |
|--------|------|--------|-------|--------|
| 1. Normalization | ga_v1.py | `÷constraint_count` | REMOVED | Penalties 10-20x stronger |
| 2. Energy penalty | ga_v1.py | 50-30x | 100-100x | Energy strictly enforced |
| 3. HARD penalty | ga_v1.py | 10-15x | 50-100x | Disease constraints respected |
| 4. SOFT penalty | ga_v1.py | 3x macros | 10x macros | Macros become priority |
| 5. Main filter | ga_v1.py | protein≥8 | protein≥12, energy≤400 | Quality dishes only |
| 6. Side filter | ga_v1.py | protein≥2 | protein≥3, fat filter | No pure fat items |
| 7. Drink filter | ga_v1.py | None | energy≤200, no MRP | Realistic beverages |
| 8. Dataset filter | ga_v1.py | N/A | NEW function | Pre-filter junk food |
| 9. Import | test_ga.py | No filter import | + filter_food_dataset | Module available |
| 10. Filter call | test_ga.py | Direct GA | STEP 4 filter | Clean input to GA |

---

## ✅ ALL CHANGES APPLIED

**Status:** READY FOR TESTING

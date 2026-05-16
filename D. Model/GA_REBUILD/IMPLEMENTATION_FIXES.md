# 🔧 GA IMPLEMENTATION FIXES - KODE KONKRET

> Semua perubahan fokus pada **implementasi code**, bukan teori

---

## 📋 RINGKASAN PERUBAHAN

| File | Issue | Fix | Impact |
|------|-------|-----|--------|
| `ga_v1.py` | Penalty normalisasi terlalu kecil | Hapus normalisasi | Penalty besar, GA hindari constraint |
| `ga_v1.py` | HARD constraint penalty lemah (10-15x) | Naikkan ke 50-100x | Sodium/Cholesterol benar-benar dipatuhi |
| `ga_v1.py` | Energy penalty terlalu lemah (50-30x) | Naikkan ke 100-100x | Energy tetap dekat TDEE |
| `ga_v1.py` | SOFT macro penalty terlalu kecil (3x) | Naikkan ke 10x | Protein/Carbs/Fat jadi prioritas |
| `ga_v1.py` | Junk food masuk GA (candy, chocolate) | Filter di awal | Hasil realistis |
| `ga_v1.py` | Quality filter terlalu lenien | Ketat untuk Main/Side | Makanan berkualitas |
| `test_ga.py` | Dataset tidak di-filter | Panggil filter_food_dataset | Input GA lebih baik |

---

## 🔴 CRITICAL FIX #1: Hapus Penalty Normalisasi

**File:** `ga_v1.py`, `fitness()` function, **lines ~588-590**

### ❌ CODE LAMA (BUG):
```python
# STEP 6: NORMALIZE PENALTY
if constraint_count > 0:
    total_penalty = total_penalty / constraint_count  # ← BUG!

return total_penalty
```

**Masalah:**
- Misalnya ada 1000 penalty dari 30 constraints
- Dibagi 30 = 33.33
- GA anggap ini penalty kecil, ignorable
- Result: Constraint dilanggar = GA tidak peduli

### ✅ CODE BARU (FIX):
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

**Impact:**
- Penalty tetap besar (1000, bukan 33)
- GA benar-benar hindari constraint violation
- Compliance genuinely dipatuhi

---

## 🔴 CRITICAL FIX #2: Energy Penalty Multiplier

**File:** `ga_v1.py`, `fitness()` function, **lines ~467-471**

### ❌ CODE LAMA:
```python
if current_energy < min_energy:
    energy_penalty = (min_energy - current_energy) * 50  # ← Masih terlalu kecil
    total_penalty += energy_penalty
elif current_energy > max_energy:
    energy_penalty = (current_energy - max_energy) * 30  # ← Over too lenient
    total_penalty += energy_penalty
```

### ✅ CODE BARU:
```python
if current_energy < min_energy:
    # Energi terlalu rendah - EXTREME penalty (100x multiplier!)
    # Underfood adalah masalah serius - GA HARUS hindari
    energy_penalty = (min_energy - current_energy) * 100  # ← 100x!
    total_penalty += energy_penalty
elif current_energy > max_energy:
    # Energi terlalu tinggi - EXTREME penalty (100x multiplier)
    energy_penalty = (current_energy - max_energy) * 100  # ← 100x!
    total_penalty += energy_penalty
```

**Comparison:**
- **Lama:** Under 50x, Over 30x → "boleh pake energy 1315 dari 2206" (40% deficit OK?)
- **Baru:** Under 100x, Over 100x → "WAJIB energy 1654-2757 (75-125% TDEE)"

---

## 🔴 CRITICAL FIX #3: HARD Constraint Penalty

**File:** `ga_v1.py`, `fitness()` function, **lines ~518-527**

### ❌ CODE LAMA:
```python
# HARD constraint penalty: lebih besar (10x untuk under, 15x untuk over)
if value < min_val:
    penalty = (min_val - value) * weight * 10  # ← Terlalu kecil
    total_penalty += penalty
elif value > max_val:
    penalty = (value - max_val) * weight * 15  # ← Terlalu kecil
    total_penalty += penalty
```

### ✅ CODE BARU:
```python
# HARD constraint penalty: EXTREME - GA HARUS hindari violation
# Multiplier: 50x untuk under, 100x untuk over
# Sodium/Cholesterol violation = disease risk!
if value < min_val:
    penalty = (min_val - value) * weight * 50  # ← 50x (5x lebih besar!)
    total_penalty += penalty
elif value > max_val:
    penalty = (value - max_val) * weight * 100  # ← 100x (7x lebih besar!)
    total_penalty += penalty
```

**Comparison (sodium, user needs 1500mg max):**
- **Lama:** 800mg over × 1.5 weight × 15 = 18,000 penalty (tapi dibagi 30 = 600)
- **Baru:** 800mg over × 1.5 weight × 100 = 120,000 penalty (HUGE, GA hindari)

---

## 🔴 CRITICAL FIX #4: SOFT Constraint Penalty (Macros)

**File:** `ga_v1.py`, `fitness()` function, **lines ~548-550**

### ❌ CODE LAMA:
```python
# SOFT constraint penalty: 
# - Macronutrients (protein, carbs, fat): 3x multiplier (important!)
# - Fiber & micronutrients: 1x multiplier (flexible)
soft_multiplier = 3.0 if nutrient_name in ['protein_g', 'carbohydrate_g', 'fat_g'] else 1.0
```

### ✅ CODE BARU:
```python
# SOFT constraint penalty: 
# - Macronutrients (protein, carbs, fat): 10x multiplier (VERY IMPORTANT!)
# - Fiber & micronutrients: 2x multiplier (flexible)
soft_multiplier = 10.0 if nutrient_name in ['protein_g', 'carbohydrate_g', 'fat_g'] else 2.0
```

**Impact:**
- Protein deficit: (82.7 - 54.7) × 2.5 weight × 10 = 700 penalty (vs 66 sebelumnya)
- GA NOW serius patuhi protein minimum

---

## 🟠 FIX #5: Strict Quality Filter untuk Food Items

**File:** `ga_v1.py`, `_apply_quality_filter()` function, **lines ~912-1010**

### ❌ CODE LAMA (TOO LENIENT):
```python
# MAIN COURSE: STRICT quality filter
if expected_lower == 'main course':
    # Main harus energy >= 200 kcal dan protein >= 8g
    filtered = filtered[
        (filtered['energy_kcal'] >= 200) &
        (filtered['protein_g'] >= 8)
    ]

# SIDE DISH: Moderate filter
elif expected_lower == 'side dish':
    # Side minimal protein >= 2g
    filtered = filtered[filtered['protein_g'] >= 2]

# DRINK & SNACK: Lenient, terima saja
```

**Problems:**
- Candy bar (517 kcal, 11g protein) → pass ke Main! (Junk food)
- Mayonnaise as Side (hanya lemak, 0.1g protein) → pass!
- Meal replacement (600 kcal!) as Drink → OK?

### ✅ CODE BARU (STRICT):
```python
def _apply_quality_filter(filtered: pd.DataFrame, expected_label: str) -> pd.DataFrame:
    """Apply STRICT quality filter untuk realistic food"""
    
    # JUNK FOOD BLACKLIST
    junk_keywords = ['candy', 'chocolate', 'dessert', 'cake', 'cookie', 'syrup', 
                     'donut', 'confection', 'sweet candy', 'caramel', 'fudge', 'pie', 'ice cream']
    junk_pattern = '|'.join(junk_keywords)
    
    # Remove junk food dari semua kategori
    if 'food_name' in filtered.columns:
        filtered = filtered[~filtered['food_name'].str.lower().str.contains(junk_pattern, na=False)]
    
    # ════════════════════════════════════════════════════════════════════════
    # MAIN COURSE: VERY STRICT
    # ════════════════════════════════════════════════════════════════════════
    if expected_lower == 'main course':
        # Energy 200-400 (realistic)
        # Protein >= 12 (adequate)
        # Fat 2-40 (not pure oil, not too fatty)
        filtered = filtered[
            (filtered['energy_kcal'] >= 200) &
            (filtered['energy_kcal'] <= 400) &
            (filtered['protein_g'] >= 12) &     # ← UP from 8
            (filtered['fat_g'] >= 2) &
            (filtered['fat_g'] <= 40)            # ← NEW limit
        ]
    
    # ════════════════════════════════════════════════════════════════════════
    # SIDE DISH: STRICT
    # ════════════════════════════════════════════════════════════════════════
    elif expected_lower == 'side dish':
        # Protein >= 3 (actual nutrisi, bukan just oil)
        # Exclude pure fat items
        filtered = filtered[filtered['protein_g'] >= 3]  # ← UP from 2
        
        # Exclude if fat > 70% of energy
        if 'fat_g' in filtered.columns:
            filtered = filtered[filtered['fat_g'] <= (filtered['energy_kcal'] / 9 * 0.7)]
    
    # ════════════════════════════════════════════════════════════════════════
    # DRINK: MODERATE
    # ════════════════════════════════════════════════════════════════════════
    elif expected_lower == 'drink':
        # Exclude meal replacement (too dense)
        filtered = filtered[~filtered['food_name'].str.lower().str.contains('meal replacement', na=False)]
        # Energy <= 200 kcal (beverage range)
        filtered = filtered[filtered['energy_kcal'] <= 200]
    
    # ════════════════════════════════════════════════════════════════════════
    # SNACK: MODERATE
    # ════════════════════════════════════════════════════════════════════════
    elif expected_lower == 'snack':
        # Energy 50-250 (reasonable snack)
        # Protein >= 1 (minimal nutrition)
        filtered = filtered[
            (filtered['energy_kcal'] >= 50) &
            (filtered['energy_kcal'] <= 250) &
            (filtered['protein_g'] >= 1)
        ]
    
    return filtered
```

**Impact:**
- Candy bar eliminated dari Main Course
- Mayonnaise eliminated dari Side Dish
- Meal replacement drinks eliminated
- Hanya makanan berkualitas yang lolos

---

## 🟠 FIX #6: Filter Dataset Sebelum GA

**File:** `ga_v1.py`, NEW FUNCTION, **lines ~176-245**

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
    
    # STEP 1: Remove junk food
    junk_keywords = ['candy', 'chocolate', 'dessert', 'cake', 'cookie', 'syrup', 
                     'donut', 'confection', 'sweet candy', 'caramel', 'fudge',
                     'pie', 'ice cream', 'pudding', 'mousse', 'brownie']
    junk_pattern = '|'.join(junk_keywords)
    
    filtered = food_df.copy()
    if 'food_name' in filtered.columns:
        filtered = filtered[~filtered['food_name'].str.lower().str.contains(junk_pattern, na=False)]
    
    junk_removed = initial_count - len(filtered)
    
    # STEP 2: Remove unrealistic energy (50-500 kcal per 100g)
    filtered = filtered[(filtered['energy_kcal'] >= 50) & (filtered['energy_kcal'] <= 500)]
    energy_removed = initial_count - junk_removed - len(filtered)
    
    # STEP 3: Remove pure oil/fat items
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

**Usage di test_ga.py:**
```python
# STEP 4: Filter food dataset
from ga_v1 import filter_food_dataset

food_df = filter_food_dataset(food_df, verbose=True)  # ← Add this!

# STEP 5: Run GA
best_solution, top_solutions = run_ga(food_df=food_df, ...)
```

---

## 📝 HOW TO APPLY FIXES

### Option A: Manual (Jika ingin paham setiap baris)
1. Open `ga_v1.py`
2. Find `def fitness()` at line ~415
3. Replace section STEP 6 (normalisasi) - hapus `total_penalty / constraint_count`
4. Update multipliers di STEP 1, 2, 3 (energy, HARD, SOFT)
5. Replace `_apply_quality_filter()` function
6. Add `filter_food_dataset()` function
7. Update `test_ga.py` imports & add filter call

### Option B: Auto (Jika sudah di-apply, tinggal verify)
```bash
# Check apakah fixes sudah ada
grep "total_penalty / constraint_count" ga_v1.py  # Should NOT find (sudah dihapus)
grep "energy_penalty = (min_energy - current_energy) \* 100" ga_v1.py  # Should find
grep "soft_multiplier = 10.0" ga_v1.py  # Should find
grep "def filter_food_dataset" ga_v1.py  # Should find
```

---

## ✅ VERIFICATION CHECKLIST

Setelah apply fixes, cek:

- [ ] `ga_v1.py`: No normalisasi `total_penalty / constraint_count`
- [ ] `ga_v1.py`: Energy multiplier 100x (bukan 50x/30x)
- [ ] `ga_v1.py`: HARD multiplier 50-100x (bukan 10-15x)
- [ ] `ga_v1.py`: SOFT macro multiplier 10x (bukan 3x)
- [ ] `ga_v1.py`: `_apply_quality_filter()` has junk food check
- [ ] `ga_v1.py`: `filter_food_dataset()` function exists
- [ ] `test_ga.py`: Imports include `filter_food_dataset`
- [ ] `test_ga.py`: STEP 4 calls `filter_food_dataset()`

---

## 🎯 EXPECTED RESULTS SETELAH FIX

### Before (Output lama):
```
Energy         :   2359.0 kcal  [     0.0-     inf] ✅  (FALSE - constraints wrong)
Sodium         :   2308.0 mg    [     0.0-     inf] ✅  (FALSE - 54% over limit)
Compliance: 100% (5/5)  ← FALSE!
GA Selected: Candy bar, Mayonnaise, Soup 6kcal
```

### After (Output baru, expected):
```
Energy         :   2206.0 kcal  [  1654.5- 2757.5] ✅  (Correct!)
Sodium         :   1200.0 mg    [  1500.0- 1500.0] ✅  (Within limit!)
Protein        :     95.0 g     [    82.7-   110.3] ✅  (Minimum met!)
Compliance: 100% (5/5)  ← CORRECT!
GA Selected: Chicken breast, Vegetables, Orange juice
```

---

## 📊 PENALTY COMPARISON

**Example: Sodium violation of 800mg over limit**

| Metric | Old Code | New Code | Factor |
|--------|----------|----------|--------|
| Base penalty | 800 × 1.5 × 15 | 800 × 1.5 × 100 | 6.7x |
| After constraint | 18,000 | 120,000 | 6.7x |
| After normalize | 18,000 / 30 = 600 | 120,000 (NO divide) | 200x |
| GA Reaction | "Acceptable" | "MUST AVOID" | ✓ |

---

## 🚀 NEXT STEP

Jalankan:
```bash
python test_ga.py
```

Output should show:
1. Dataset filtering stats
2. GA dengan hasil lebih realistis
3. Constraints benar-benar dipatuhi
4. Compliance accuracy nyata (bukan false 100%)

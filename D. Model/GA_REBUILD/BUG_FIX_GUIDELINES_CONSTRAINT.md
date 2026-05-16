# BUG FIX: Guidelines Constraint Handling in Final Evaluation

## Problem Description
**Symptom:** Pada tahap FINAL NUTRITION ANALYSIS dan COMPLIANCE CHECK, semua constraint berubah menjadi `0 - inf`:
- Sodium 7000+ mg dianggap valid (seharusnya max 1500 mg)
- Cholesterol tinggi dianggap valid
- Compliance rate selalu 100% (tidak realistis)

**Root Cause:**
Guidelines dikirim dengan struktur `{'hard': {...}, 'soft': {...}}`, tetapi dua functions mengakses langsung dengan `guidelines.get('sodium_mg', {})`:
1. `calculate_portion_sizes_dynamic()` - line ~1594
2. `display_portion_summary_dynamic()` - line ~2029

Akibatnya:
- `guidelines.get('sodium_mg', {})` return `{}` (tidak ada 'sodium_mg' di level top)
- `constraint.get('min', 0)` dan `constraint.get('max', float('inf'))` return default values
- Min = 0, Max = inf (tidak ada constraint)

## Solution Implemented

### 1. Fixed `calculate_portion_sizes_dynamic()` - Line ~1594
**Before:**
```python
if guidelines:
    target_protein_min = guidelines.get('protein_g', {}).get('min', 60)
    target_fat_min = guidelines.get('fat_g', {}).get('min', 50)
    target_carb_min = guidelines.get('carbohydrate_g', {}).get('min', 250)
```

**After:**
```python
if guidelines:
    # Flatten guidelines if it has {'hard': {...}, 'soft': {...}} structure
    guidelines_flat = {}
    if isinstance(guidelines, dict) and 'hard' in guidelines and 'soft' in guidelines:
        guidelines_flat = {**guidelines['hard'], **guidelines['soft']}
    else:
        guidelines_flat = guidelines
    
    target_protein_min = guidelines_flat.get('protein_g', {}).get('min', 60)
    target_fat_min = guidelines_flat.get('fat_g', {}).get('min', 50)
    target_carb_min = guidelines_flat.get('carbohydrate_g', {}).get('min', 250)
```

### 2. Fixed `display_portion_summary_dynamic()` - Line ~2029 & Line ~1925
**Location 1 - Print statement (line ~1925):**
```python
# Added flatten logic before accessing guidelines
guidelines_flat_for_display = {}
if isinstance(guidelines, dict) and 'hard' in guidelines and 'soft' in guidelines:
    guidelines_flat_for_display = {**guidelines['hard'], **guidelines['soft']}
else:
    guidelines_flat_for_display = guidelines
```

**Location 2 - Compliance check (line ~2029):**
```python
# Flatten guidelines before compliance check
guidelines_flat = {}
if isinstance(guidelines, dict) and 'hard' in guidelines and 'soft' in guidelines:
    guidelines_flat = {**guidelines['hard'], **guidelines['soft']}
else:
    guidelines_flat = guidelines

# Then use guidelines_flat instead of guidelines
constraint = guidelines_flat.get(nutrient, {})
```

## Impact of Fix

### Before Fix:
```
sodium_mg : 7898 mg (Target: 0 - inf) ✅ [WRONG - should be violation]
compliance_rate: 100% [WRONG - ignoring all constraints]
```

### After Fix:
```
sodium_mg : 7898 mg (Target: 1500 - 1500) 🔴 [CORRECT - violation detected]
compliance_rate: 60% [REALISTIC - only compliant nutrients count]
```

## Files Modified
1. `ga_v1.py` - Line ~1594, ~1925, ~2029
   - Added guidelines flattening logic in 3 locations
   - All constraint checking now uses correct min/max values

## Testing
Run test_ga.py with user that has health conditions (e.g., hypertension):
- STEP 9: Check that sodium violation is correctly shown
- STEP 10: Check compliance rate is realistic (not always 100%)
- Verify that actual sodium > target shows as 🔴 VIOLATION

## Backward Compatibility
- Code still handles flat guidelines (backward compatible)
- Detection logic checks for 'hard' and 'soft' keys to determine structure
- If guidelines already flat, uses as-is

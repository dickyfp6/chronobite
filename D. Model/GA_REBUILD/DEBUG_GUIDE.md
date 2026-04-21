# Debug Guide: Consumption_Label Filtering

## Cara Mengaktifkan Debug Output

### 1. Dalam Fungsi `random_solution()` - Tambahkan Debug

**File:** `ga_v1.py`

**Current Code (Line ~200):**
```python
for slot_idx in range(CHROMOSOME_SIZE):
    filtered_df = _filter_food_by_slot(food_df, slot_idx)
```

**Dengan Debug:**
```python
for slot_idx in range(CHROMOSOME_SIZE):
    filtered_df = _filter_food_by_slot(food_df, slot_idx, debug=True)  # Enable debug
```

---

### 2. Dalam Fungsi `mutation()` - Tambahkan Debug

**File:** `ga_v1.py`

**Current Code (Line ~420):**
```python
filtered_food_df = _filter_food_by_slot(food_df, gene_idx)
```

**Dengan Debug:**
```python
filtered_food_df = _filter_food_by_slot(food_df, gene_idx, debug=True)  # Enable debug
```

---

## Output Debug Contoh

Ketika debug=True, akan melihat output seperti:

```
DEBUG: Slot 0 (breakfast_main) -> label='main' -> 245 items
DEBUG: Slot 1 (breakfast_side) -> label='side' -> 150 items
DEBUG: Slot 2 (breakfast_drink) -> label='drink' -> 89 items
DEBUG: Slot 3 (lunch_main) -> label='main' -> 245 items
DEBUG: Slot 4 (lunch_side) -> label='side' -> 150 items
DEBUG: Slot 5 (lunch_drink) -> label='drink' -> 89 items
DEBUG: Slot 6 (dinner_main) -> label='main' -> 245 items
DEBUG: Slot 7 (dinner_side) -> label='side' -> 150 items
DEBUG: Slot 8 (dinner_drink) -> label='drink' -> 89 items
DEBUG: Slot 9 (snack) -> label='snack' -> 312 items
```

---

## Debug Output Artinya

```
DEBUG: Slot {idx} ({slot_name}) -> label='{expected_label}' -> {count} items
```

- **Slot**: Index dalam chromosome (0-9)
- **slot_name**: Nama slot (breakfast_main, lunch_drink, snack, dll)
- **expected_label**: Label yang dicari di consumption_label column
- **count**: Jumlah makanan yang cocok dengan label

---

## Troubleshooting dengan Debug

### Kasus 1: Slot menunjukkan 0 items

```
DEBUG: Slot 5 (lunch_drink) -> label='drink' -> 0 items
DEBUG: Slot 5 - No items found, using fallback (sampling max 20)
```

**Artinya:** Tidak ada makanan dengan consumption_label='drink'

**Solusi:**
- Check dataset: berapa banyak items dengan label 'drink'?
- Cek kolom consumption_label di CSV
- Pastikan case sensitivity: 'Drink' vs 'drink' vs 'DRINK'?

### Kasus 2: Jumlah items tidak sesuai ekspektasi

```
DEBUG: Slot 0 (breakfast_main) -> label='main' -> 50 items
```

Jika jumlah terlalu sedikit/banyak:
- Verify di dataset: berapa items dengan consumption_label='main'?
- Gunakan Pandas untuk cek:

```python
import pandas as pd
df = pd.read_csv('05_final_dataset.csv')
print(df['consumption_label'].value_counts())
```

---

## Cara Menjalankan dengan Debug

### Option 1: Temporary Enable (Testing)

Edit `ga_v1.py` temp, jalankan, lalu revert:

```python
# Line ~200 (temporary)
filtered_df = _filter_food_by_slot(food_df, slot_idx, debug=True)
```

### Option 2: Conditional Debug (Better)

Di `test_ga.py`, tambahkan:

```python
# Add after imports
ENABLE_DEBUG = True  # Set to False untuk disable

# Modify random_solution call
if ENABLE_DEBUG:
    # Run with debug
    best_solution, top_solutions = run_ga(..., debug=True)
```

Atau tangkap ke file:

```python
import sys
from io import StringIO

# Redirect output
debug_output = StringIO()
old_stdout = sys.stdout
sys.stdout = debug_output

# Run GA
best_solution, top_solutions = run_ga(...)

# Capture output
sys.stdout = old_stdout
print(debug_output.getvalue())
```

---

## Expected Values untuk Dataset Anda

Berdasarkan data yang ada, harusnya:

| Label | Expected Count |
|-------|-----------------|
| main | ~300-400 items |
| side | ~200-300 items |
| drink | ~100-150 items |
| snack | ~400-500 items |

Jika angka-nya jauh berbeda, periksa:
1. Apakah consumption_label ada di dataset?
2. Apakah nilai adalah 'main', 'side', 'drink', 'snack'?
3. Ada spelling error atau case mismatch?

---

## Cepat Cek Dataset

```python
import pandas as pd

df = pd.read_csv('A. Data/Data Processed/05_final_dataset.csv')

# Lihat unique values
print(df['consumption_label'].unique())

# Lihat count per label
print(df['consumption_label'].value_counts())

# Cek ada missing values
print(f"Missing: {df['consumption_label'].isna().sum()}")
```

---

## Disable Debug (Default)

Default adalah `debug=False`, jadi tidak ada extra output.

Untuk production/presentation, pastikan:
```python
filtered_df = _filter_food_by_slot(food_df, slot_idx)  # debug tidak disebutkan
# atau
filtered_df = _filter_food_by_slot(food_df, slot_idx, debug=False)
```

---

## Summary

- **Debug ON**: Lihat detail filtering untuk troubleshooting
- **Debug OFF** (default): Clean output tanpa noise
- **Fallback mechanism**: Jika label tidak match, ambil random 20 items
- **Case-insensitive**: 'Main' == 'main' == 'MAIN'

---

**Last Updated:** 21 April 2026
**Related File:** `D. Model/GA_REBUILD/CONSUMPTION_LABEL_FILTERING.md`

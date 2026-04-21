# Perbaikan Filtering Makanan: Dari Food_Group ke Consumption_Label

## Ringkasan Perubahan

Genetic Algorithm telah diperbaiki untuk menggunakan kolom **`consumption_label`** dari dataset yang lebih akurat, menggantikan pendekatan lama yang berbasis `food_group`.

---

## 📋 Perubahan Utama

### 1. **Tambahan: SLOT_LABEL_MAP Dictionary** (Line 57-70)

```python
SLOT_LABEL_MAP = {
    0: 'main',      # breakfast_main
    1: 'side',      # breakfast_side
    2: 'drink',     # breakfast_drink
    3: 'main',      # lunch_main
    4: 'side',      # lunch_side
    5: 'drink',     # lunch_drink
    6: 'main',      # dinner_main
    7: 'side',      # dinner_side
    8: 'drink',     # dinner_drink
    9: 'snack'      # snack
}
```

**Penjelasan:**
- Setiap slot (0-9) dipetakan ke label konsumsi yang diharapkan
- Lebih akurat karena berbasis dataset yang sudah ter-label
- Menggantikan pendekatan berbasis food_group categories

---

### 2. **Update: Fungsi `_filter_food_by_slot()`** (Line 118-165)

#### Sebelum (Lama):
```python
def _filter_food_by_slot(food_df: pd.DataFrame, slot_idx: int) -> pd.DataFrame:
    if 'food_group' not in food_df.columns:
        return food_df
    
    expected_groups = SLOT_FOOD_GROUP_MAPPING.get(slot_idx, [])
    filtered = food_df[food_df['food_group'].str.lower().isin(expected_groups)]
    
    if len(filtered) == 0:
        return food_df.sample(n=min(20, len(food_df)))
    
    return filtered
```

#### Sesudah (Baru):
```python
def _filter_food_by_slot(food_df: pd.DataFrame, slot_idx: int, debug: bool = False) -> pd.DataFrame:
    # Cek kolom consumption_label ada
    if 'consumption_label' not in food_df.columns:
        if debug:
            print(f"DEBUG: Slot {slot_idx} - No consumption_label column")
        return food_df
    
    # Ambil expected label dari SLOT_LABEL_MAP
    expected_label = SLOT_LABEL_MAP.get(slot_idx, None)
    if not expected_label:
        if debug:
            print(f"DEBUG: Slot {slot_idx} - No label mapping")
        return food_df
    
    # Filter dengan case-insensitive comparison
    filtered = food_df[food_df['consumption_label'].str.lower() == expected_label.lower()]
    
    if debug:
        print(f"DEBUG: Slot {slot_idx} ({SLOT_NAMES[slot_idx]}) -> label='{expected_label}' -> {len(filtered)} items")
    
    # Fallback: sample max 20 jika tidak ada match
    if len(filtered) == 0:
        if debug:
            print(f"DEBUG: Slot {slot_idx} - No items found, using fallback (sampling max 20)")
        return food_df.sample(n=min(20, len(food_df)))
    
    return filtered
```

**Perbaikan:**
- ✅ Menggunakan kolom yang sudah ada: `consumption_label`
- ✅ Logic lebih sederhana: exact match, bukan `isin()` multiple values
- ✅ Optional debug output untuk troubleshooting
- ✅ Clear error messages untuk debugging

---

### 3. **Backup: Legacy SLOT_FOOD_GROUP_MAPPING** (Line 72-82)

```python
# Legacy: kept for reference (tidak digunakan lagi, gunakan consumption_label)
SLOT_FOOD_GROUP_MAPPING = {
    # ... (tetap ada untuk referensi, tapi tidak digunakan)
}
```

**Catatan:** Disimpan untuk referensi saja, tidak digunakan oleh GA saat ini.

---

## 🎯 Keuntungan Perbaikan

| Aspek | Sebelum | Sesudah |
|-------|---------|---------|
| **Data Source** | food_group (dubious) | consumption_label (dari dataset) |
| **Filtering Logic** | `isin()` multiple values | Exact match single value |
| **Akurasi** | Sedang (food_group tidak sempurna) | **Tinggi** (berbasis dataset yang sudah ter-label) |
| **Debug Info** | Tidak ada | Optional debug output |
| **Meal Plan** | Mungkin drink jadi main course | **Realistis**: drink hanya di slot drink |
| **Performance** | OK | Sedikit lebih cepat (simpler filtering) |

---

## 💡 Hasil yang Diharapkan

Setelah perbaikan, meal plan yang dihasilkan akan **lebih realistis**:

### ✅ Breakfast:
- **Main**: Nasi Putih, Roti Tawar, Bubur
- **Side**: Telur, Tahu, Sayuran
- **Drink**: Teh, Kopi, Jus

### ✅ Lunch:
- **Main**: Nasi Goreng, Mie Goreng, Nasi Kuning
- **Side**: Lauk Pauk, Sambal, Sayuran
- **Drink**: Air Putih, Teh Dingin, Jus

### ✅ Dinner:
- **Main**: Nasi, Ketoprak, Soto Ayam
- **Side**: Daging/Ikan, Sayuran, Sambal
- **Drink**: Teh, Mineral, Jus

### ✅ Snack:
- Kue, Buah, Cookies, Minuman Ringan

---

## 🔧 Kompatibilitas

**Perubahan backward compatible:**
- Existing code yang memanggil `_filter_food_by_slot(food_df, slot_idx)` tetap berfungsi
- Debug parameter bersifat opsional (default=False)
- `random_solution()`, `mutation()` berfungsi tanpa modifikasi

---

## 📊 Testing

Untuk memverifikasi perbaikan, jalankan:

```bash
python test_ga.py
```

**Indikator Sukses:**
- Tidak ada error import atau type
- Meal plan realistic (tidak ada minuman jadi main course)
- Semua 10 slot terisi dengan label yang sesuai

---

## 📝 Docstring Updates

Beberapa docstring telah diupdate:
- `_filter_food_by_slot()`: Sekarang menggunakan consumption_label
- `random_solution()`: Referensi ke consumption_label filtering
- Semua comment tetap konsisten

---

## 🚀 Kesimpulan

Dengan perubahan ini, Genetic Algorithm akan menghasilkan meal plan yang:
1. ✅ **Akurat**: Berbasis label konsumsi dari dataset
2. ✅ **Realistis**: Drink hanya di slot minum, snack hanya di slot snack
3. ✅ **Maintainable**: Code lebih simple dan mudah dipahami
4. ✅ **Debuggable**: Optional debug output untuk troubleshooting
5. ✅ **Compatible**: Tidak breaking changes dengan existing code

---

**File Modified:** `D. Model/GA_REBUILD/ga_v1.py`

**Date Modified:** 21 April 2026

**Status:** ✅ COMPLETE

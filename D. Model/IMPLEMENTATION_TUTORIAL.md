# Tutorial Implementasi ke Algoritma Manual

Dokumen ini menjelaskan bagaimana algoritma Greedy dan Genetic yang ditulis manual harus memakai layer pendukung di folder `D. Model`.

## Tujuan

Kita tidak menaruh optimasi di file pendukung. Folder ini hanya menyiapkan:
- kontrak output final
- pembagian meal dan slot
- helper mapping role makanan
- helper similarity/diversity
- state untuk refresh rekomendasi

Algoritma manual nanti tinggal mengikuti kontrak ini.

## Struktur Output Final yang Harus Dipenuhi

Output final algoritma harus berbentuk dictionary dengan struktur inti berikut:

```python
{
    "algorithm": "Greedy" or "Genetic",
    "success": True,
    "user_profile": {...},
    "meal_plan": {
        "breakfast": {
            "budget_kcal": ...,
            "selected": {
                "main_course": ...,
                "side_dish": ...,
                "drink": ...
            },
            "candidates": {
                "main_course": [3 kandidat],
                "side_dish": [3 kandidat],
                "drink": [3 kandidat]
            },
            "refresh_state": {...}
        },
        "lunch": {...},
        "dinner": {...},
        "snack": {
            "budget_kcal": ...,
            "selected": ...,
            "candidates": [3 kandidat]
        }
    },
    "summary": {
        "fitness_score": ...,
        "feasible": ...,
        "execution_time": ...,
        "violations": [],
        "notes": []
    },
    "debug": {
        "selected_algorithm_mode": ...,
        "excluded_food_ids": [],
        "seed": None
    }
}
```

## Skema Pembagian Meal

Gunakan helper di [meal_distribution.py](meal_distribution.py).

### Skema 1
- Main Course: 60%
- Side Dish: 25%
- Drink: 15%

### Skema 2
- Main Course: 70%
- Side Dish: 30%
- Drink: 0%

### Aturan pakai
- Breakfast, Lunch, Dinner default memakai Skema 1.
- Jika user tidak memilih drink, gunakan Skema 2.
- Snack tidak wajib dipisah ke main/side/drink.

Contoh helper:

```python
from meal_distribution import build_meal_budget_plan

plan = build_meal_budget_plan(tdee=2200, include_drink=True)
```

## Alur yang Dipakai Algoritma Manual

### 1. Ambil user profile
Algoritma menerima hasil dari `NutritionService.calculate_nutrition_needs()`.

Field penting:
- `guidelines.nutrients`
- `food_data.dataframe`
- `meal_plan.distribution`
- `user_params`

### 2. Bentuk kandidat makanan per slot
Pakai helper di [food_slot_mapping.py](food_slot_mapping.py):
- `infer_food_role(food_row)`
- `group_food_candidates(food_rows)`
- `filter_excluded_items(food_rows, excluded_ids)`

Tujuannya adalah memisahkan makanan ke:
- `main_course`
- `side_dish`
- `drink`
- `snack`

Kalau data belum punya label lengkap, helper ini masih bisa infer dari `food_name`, `food_group`, `consumption_label`, dan `cuisine_label`.

### 3. Hasilkan 3 kandidat per slot
Setiap slot harus punya 3 kandidat.
Contoh:
- Breakfast Main Course: 3 item
- Breakfast Side Dish: 3 item
- Breakfast Drink: 3 item
- Lunch Main Course: 3 item
- Lunch Side Dish: 3 item
- Lunch Drink: 3 item
- Dinner Main Course: 3 item
- Dinner Side Dish: 3 item
- Dinner Drink: 3 item
- Snack: 3 item

### 4. Refresh rekomendasi
Jika user klik refresh pada satu slot:
- simpan ID item yang sudah muncul
- panggil ulang pencarian kandidat dengan `excluded_ids`
- keluarkan 3 kandidat baru

Pattern ini sudah disiapkan di `build_refresh_request()`.

### 5. Handling portion 100 gram
Dataset kamu basisnya per 100 gram. Jadi semua perhitungan nutrisi harus diskalakan:

```python
actual_value = value_per_100g * serving_gram / 100
```

Kalau algoritma memilih menu 150 gram:
- kalori
- protein
- lemak
- karbohidrat

semuanya dihitung dengan formula di atas.

### 6. Similarity / diversity
Gunakan helper di [meal_similarity.py](meal_similarity.py).

Fungsi penting:
- `similarity_score(food_a, food_b)`
- `diversity_penalty(candidate, selected_items)`
- `is_too_similar(candidate, selected_items)`

Tujuan:
- hindari menu terlalu mirip
- contoh: kalau sudah ada ikan kembung, kandidat berikutnya jangan terlalu dekat dengan ikan kembung lagi

### 7. Drink opsional
Kalau drink tidak dipilih:
- slot drink boleh kosong atau `None`
- budget-nya dialihkan ke main course dan side dish
- output tetap valid memakai Skema 2

## Rekomendasi Implementasi Manual

### Greedy
Pola umum:
1. Ambil slot target.
2. Filter kandidat sesuai role.
3. Urutkan berdasarkan skor.
4. Ambil kandidat terbaik.
5. Simpan 3 kandidat terbaik sebagai opsi UI.
6. Simpan item pilihan final kalau user memilih salah satu.

### Genetic
Pola umum:
1. Encode satu individual sebagai kombinasi slot makanan.
2. Fitness menilai kesesuaian nutrisi, diversity, dan constraint.
3. Crossover dan mutation bekerja pada slot, bukan langsung pada list final UI.
4. Setelah best individual didapat, convert ke format kontrak output final.

## File yang Dipakai

- [meal_distribution.py](meal_distribution.py)
- [output_contract.py](output_contract.py)
- [food_slot_mapping.py](food_slot_mapping.py)
- [meal_similarity.py](meal_similarity.py)

## Catatan Penting

- File-file ini bukan algoritma.
- Kamu boleh menulis algoritma manual nanti di folder algoritma.
- Yang penting, hasil akhir harus mengikuti kontrak output ini supaya web dan CLI bisa membaca data dengan format yang sama.

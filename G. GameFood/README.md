# Food Name Comma Analysis

Folder ini khusus untuk analisis pola koma pada nama makanan USDA dari dataset final.

## Isi Folder
- `analyze_food_name_commas.py`: script analisis utama.
- `output/`: hasil analisis otomatis (dibuat saat script dijalankan).

## Cara Jalankan
Gunakan Python environment yang sudah kamu pakai di project, lalu jalankan:

```powershell
python analyze_food_name_commas.py
```

Atau jika ingin pakai path input custom:

```powershell
python analyze_food_name_commas.py --input "C:\path\ke\dataset.csv"
```

## Output yang Dihasilkan
- `summary_report.txt`: ringkasan insight utama.
- `comma_distribution.csv`: distribusi jumlah koma per nama.
- `top_segments_by_position.csv`: segmen populer per posisi koma.
- `top_last2_patterns.csv`: pola 2 segmen terakhir paling sering.
- `top_last3_patterns.csv`: pola 3 segmen terakhir paling sering.
- `comma_count_samples.csv`: contoh nama berdasarkan jumlah koma.
- `food_group_comma_stats.csv`: statistik per food group (jika kolom tersedia).

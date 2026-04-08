# GUI APPLICATION README

## Struktur

```
C. System Flow/
├── GUI/                  ← GUI Application folder (Temporary)
│   ├── main_gui.py       ← Entry point
│   ├── gui_app.py        ← GUI class implementation
│   ├── test_imports.py   ← Test script
│   └── README.md         ← This file
│
├── modules/              ← Core logic (shared)
├── main.py              ← CLI version
└── data_loader.py
```

## Cara Menjalankan GUI

### Option 1: Dari terminal
```bash
cd "C. System Flow/GUI"
python main_gui.py
```

### Option 2: Dari root System Flow
```bash
cd "C. System Flow"
python GUI/main_gui.py
```

## Fitur GUI

✅ **Input Fields:**
- Jenis Kelamin (Dropdown)
- Usia (Spinbox)
- Berat Badan (Entry)
- Tinggi Badan (Entry)
- Tingkat Aktivitas (Radio buttons)
- Kondisi Kesehatan (Radio buttons)
- Preferensi Makanan (Entry)

✅ **Interface:**
- Left Panel: Input form
- Right Panel: Results display
- Scrollable text area untuk hasil lengkap

✅ **Actions:**
- Calculate: Jalankan perhitungan
- Reset: Clear semua input

## Hasil Output

Aplikasi akan menampilkan:
1. Data user yang dimasukkan
2. Antropometri (BMI, BBI)
3. Energi (BMR, TDEE)
4. Kebutuhan Nutrisi (dari guideline)

## Technology

- **GUI Framework**: tkinter (built-in Python)
- **No additional dependencies** (besides pandas, numpy dari main app)
- **Cross-platform**: Windows, macOS, Linux

## Notes

- GUI ini adalah testing/development version
- Data guideline auto-loaded dari `A. Data/Data Raw/guideline.csv`
- Semua logic reuse dari modules yang sudah ada
- Mudah untuk di-extend atau di-styling lebih lanjut

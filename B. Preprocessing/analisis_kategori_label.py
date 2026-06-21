"""
File Analisis: Cek Kategori & Label
Tujuan: Menampilkan daftar unik dari food_group dan menghitung jumlah makanan per consumption_label
pada dataset final (04_super_final.csv). File ini opsional dan murni untuk pengecekan cepat.
"""

import pandas as pd

import os
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.normpath(os.path.join(CURRENT_DIR, "..", "A. Data", "Data Processed", "04_super_final.csv"))

df = pd.read_csv(INPUT_FILE)
print(df['food_group'].unique().tolist())
print()
print(df['consumption_label'].value_counts())

# Panduan Folder F. WebApp (Antarmuka Pengguna)

Folder ini berfungsi sebagai **Antarmuka (Frontend & API)** yang menghubungkan seluruh kecerdasan buatan (Algoritma Greedy & Genetika) dari proyek Anda agar bisa digunakan secara visual oleh pengguna akhir.

## Daftar Isi & Deskripsi File

1. **`app_integrated.py`**
   - **Peran**: Ini adalah otak dari *Backend* Anda (berbasis Flask).
   - **Fungsi**: Bertindak sebagai "Pelayan" yang menerima pesanan (request profil pasien) dari website, kemudian meneruskannya ke `b_nutrition_service.py` untuk dianalisis, lalu diserahkan ke *Greedy* atau *Genetic Algorithm* untuk dibuatkan menu. Setelah menu jadi, ia akan mengirimkannya kembali ke website dalam format JSON.
   - **Fitur Kunci**: Mendukung *multithreading* (proses di latar belakang) sehingga website tidak akan nge-*lag* saat AI sedang berpikir mencari menu.

2. **`requirements.txt`**
   - **Peran**: Daftar belanjaan pustaka Python.
   - **Fungsi**: Berisi *library* apa saja yang wajib di-install agar `app_integrated.py` bisa menyala (seperti `Flask`, `Flask-CORS`, `pandas`, dll).

3. **Folder `Frontend/`**
   - **Peran**: Tampilan visual website (User Interface).
   - **Fungsi**: Dibangun menggunakan teknologi **React, Vite, dan Tailwind CSS**. Ini adalah kode yang akan di- *render* menjadi halaman web interaktif tempat pengguna memasukkan umur, berat badan, tinggi, penyakit bawaan, lalu melihat rekomendasi menu sarapan, makan siang, dan makan malam yang cantik.

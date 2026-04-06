# 🌿 NutriPlan DSS - Web Application

Sistem Rekomendasi Nutrisi & Diet Berbasis Keputusan dengan Interface Responsif dan PWA-Ready.

## ✨ Fitur Utama

### 1. **Slide-Flow Interface** (Multi-Step Stepper)
- **5 Tahap Interaktif**:
  - 🎯 **Slide 0: Hero** - Landing page dengan call-to-action
  - 👤 **Slide 1: Profile** - Input data demografi & aktivitas
  - 🏥 **Slide 2: Health Condition** - Seleksi kondisi kesehatan & preferensi makanan
  - 📊 **Slide 3: Analysis** - Dashboard hasil analisis nutrisi dengan TDEE & target makro
  - 🍽️ **Slide 4: Menu Recommendation** - Grid rekomendasi menu yang disesuaikan

### 2. **Design System Premium**
- **Glassmorphism Effect**: Transparent containers dengan blur effect
- **Color Palette**: 
  - Primary: Emerald-600 (#10b981)
  - Background: Slate-50
  - Accent: Mint Green
- **Typography**: Inter (body) + Montserrat (headlines)
- **Responsive Mobile-First**: Optimal di semua ukuran layar
- **Smooth Animations**: Fade-in, slide-up transitions

### 3. **Progressive Web App (PWA)**
- ✅ Offline Support dengan Service Worker
- ✅ Installable di Home Screen
- ✅ App-like Experience
- ✅ Background Sync capability
- ✅ Web Manifest dengan Icons

### 4. **Fitur Interaktif**
- Real-time form validation
- Gender, Age, Weight, Height, Activity Level selection
- Multi-select health conditions
- Food preference selection
- Dynamic macro calculation
- Results export (JSON download)

## 🏗️ Struktur Project

```
F. WebApp/
├── app.py                    # Flask backend dengan API
├── requirements.txt          # Python dependencies
├── README.md                # Dokumentasi ini
├── templates/
│   └── index.html          # Main UI dengan Slide-Flow (HTML + Alpine.js)
└── static/
    ├── manifest.json       # PWA Manifest
    └── js/
        └── sw.js          # Service Worker
```

## 🚀 Setup & Installation

### Prerequisites
- Python 3.8+
- pip

### Install Dependencies
```bash
cd "F. WebApp"
pip install -r requirements.txt
```

### Run Application
```bash
python app.py
```

Aplikasi akan berjalan di `http://localhost:5000`

## 📱 Penggunaan

1. **Akses dari Browser**: 
   - Desktop: `http://localhost:5000`
   - Mobile: Akses via IP lokal atau deploy

2. **Flow Analisis**:
   - Klik "Mulai Analisis Sekarang"
   - Isi data profil (gender, usia, berat, tinggi, aktivitas)
   - Pilih kondisi kesehatan & preferensi makanan
   - Lihat hasil analisis (BMI, BMR, TDEE, target makro)
   - Lihat rekomendasi menu
   - Unduh hasil dalam format JSON

3. **Install sebagai PWA**:
   - Di Mobile: Tap menu → "Add to Home Screen"
   - Di Desktop (Chrome): Install icon di address bar

## ⚙️ Backend API

### POST `/api/analyze`
**Input:**
```json
{
  "gender": "M|F",
  "age": 25,
  "weight": 70.5,
  "height": 170.5,
  "activity": "1.2|1.375|1.55|1.725|1.9",
  "diseases": ["normal", "dm2", "hypertension", "cvd", "cholesterol", "ckd"],
  "food_preferences": ["Western", "Asian", "Mediterranean", "Generic"]
}
```

**Output:**
```json
{
  "bmi": 24.4,
  "bmi_category": "Normal",
  "bmi_color": "green",
  "bbi": 63.0,
  "bmr": 1650,
  "tdee": 2268,
  "activity_label": "Moderately Active",
  "diseases": ["Normal"],
  "macros": {
    "carbs": {"pct": [45, 65], "gram": 290},
    "protein": {"pct": [10, 35], "gram": 130},
    "fat": {"pct": [20, 35], "gram": 85}
  },
  "menu": {
    "breakfast": [...],
    "lunch": [...],
    "dinner": [...],
    "snack": [...]
  }
}
```

## 🎨 Customization

### Mengubah Warna
Edit di `index.html` > `<style>`:
```css
:root {
    --primary: #10b981;      /* Emerald */
    --secondary: #f0fdfa;    /* Very light cyan */
    --accent: #d1fae5;       /* Light mint */
    --dark: #1e293b;         /* Slate */
}
```

### Menambah/Edit Menu Items
Edit di `app.py` > `SAMPLE_MENU`:
```python
SAMPLE_MENU = {
    "breakfast": [
        {"name": "Nasi Kuning", "calories": 350, "carbs": 50, "protein": 8, "fat": 12, "emoji": "🍚"},
        ...
    ],
    ...
}
```

### Mengubah Penyakit & Target Makro
Edit di `app.py` > `DISEASE_MACROS`:
```python
DISEASE_MACROS = {
    "diabetes_custom": {
        "carbs": (40, 50),
        "protein": (20, 25),
        "fat": (25, 30)
    },
    ...
}
```

## 🔒 Security Notes

- Validasi input di frontend & backend
- Hindari exposing sensitive data
- Untuk production, gunakan environment variables
- Enable HTTPS
- Implementasi rate limiting di API

## 📊 Browser Compatibility

| Browser | Support |
|---------|---------|
| Chrome  | ✅ Full |
| Firefox | ✅ Full |
| Safari  | ✅ Full |
| Edge    | ✅ Full |
| IE 11   | ❌ Not supported |

## 📦 PWA Features

✅ **Offline**: Service Worker meng-cache aset
✅ **Installable**: Manifest + icons
✅ **App-like**: Fullscreen, status bar
✅ **Responsive**: Mobile-first design
✅ **Share Target**: Import/export results
✅ **Shortcuts**: Quick actions dari home screen

## 🐛 Troubleshooting

### Service Worker tidak register
```bash
# Clear browser cache & uninstall app
# Restart Flask server
# Refresh halaman
```

### Styling tidak muncul
- Pastikan Tailwind CDN accessible
- Cek network tab di DevTools

### Form tidak responsive
- Gunakan browser terbaru
- Clear browser cache

## 🔗 Integrasi Backend

Untuk mengintegrasikan dengan Algoritma Genetika/Greedy:

1. **Update `/api/analyze` endpoint** untuk memanggil algoritma
2. **Replace `SAMPLE_MENU`** dengan output dari algoritma
3. **Validasi constraint** kesehatan di backend

```python
# Contoh
from your_algorithm import generate_menu

@app.route("/api/analyze", methods=["POST"])
def analyze():
    # ... existing code ...
    
    # Call your algorithm
    menu = generate_menu(tdee, macros, diseases, preferences)
    
    return jsonify({ menu: menu, ... })
```

## 📝 License

Bagian dari Tugas Akhir DSS Nutrisi

## 👨‍💼 Support

Untuk pertanyaan atau isu, hubungi tim development.

---

**Last Updated**: April 2025
**Version**: 1.0.0 (Beta)

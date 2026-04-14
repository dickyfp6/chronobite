# 🚀 QUICK START GUIDE - Nutrition DSS

> Udah pusing sama setup? Guide ini akan clear semuanya!

---

## 📊 ARCHITECTURE OVERVIEW

Sistem kamu punya 3 komponen utama yang saling terhubung:

```
┌─────────────────────────────────────────────────────────────────┐
│                     FRONTEND (React + Vite)                     │
│                    F. WebApp/Frontend                           │
│  http://localhost:5173 atau https://vercel.app                 │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                 HTTP Request (POST /api/...)
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│                   BACKEND (Flask)                               │
│                F. WebApp/app_integrated.py                      │
│           http://localhost:5000 (dev)                           │
│     https://render.app (production)                             │
└──────┬──────────────────────────────────────┬───────────────────┘
       │                                      │
       ↓                                      ↓
┌──────────────────────────┐    ┌───────────────────────────────┐
│   SYSTEM FLOW             │    │   MODEL/ALGORITHMS            │
│   C. System Flow/         │    │   D. Model/                   │
│   NutritionService        │    │   Greedy Algorithm            │
│   (Nutrition Calc)        │    │   Genetic Algorithm           │
└──────────────────────────┘    └───────────────────────────────┘
```

---

## 🔄 FLOW EXPLANATION

### 1️⃣ User Input (Frontend)
User isi form di React:
- Gender, age, weight, height
- Activity factor
- Diseases (DM2, Hypertension, dll)
- Food preferences
- Algorithm choice (Greedy atau Genetic)

### 2️⃣ Analyze Profile (Backend → System Flow)
Frontend call **`POST /api/analyze`** với form data.

Backend (`app_integrated.py`) akan:
```python
# Import dari C. System Flow
from nutrition_service import NutritionService

# Process user input
service = NutritionService()
result = service.calculate_nutrition_needs(user_data)
# Output: BMI, BMR, TDEE, nutrition guidelines
```

Kembali ke frontend dengan profile analysis.

### 3️⃣ Generate Menu (Backend → System Flow + Algorithms)
Frontend call **`POST /api/generate-menu`** dengan analysis result.

Backend akan:
```python
# Get algorithm interface
from greedy_interface import GreedyAlgorithmInterface

# Run selected algorithm
algorithm = GreedyAlgorithmInterface()
menu = algorithm.generate_menu(
    user_profile=user_data,
    nutrition_constraints=guidelines,
    food_data=food_database
)
```

Kembali dengan menu yang optimized.

### 4️⃣ Display Menu (Frontend)
Frontend display menu dengan:
- Breakfast, lunch, dinner, snack
- Total macros/micros
- Food details

---

## 🏃 QUICK START (Local Setup)

### STEP 1: Prepare Backend

```bash
# Navigate to F. WebApp (backend folder)
cd "F. WebApp"

# Create virtual environment (if not exists)
python -m venv .venv

# Activate venv
# On Windows:
.venv\Scripts\activate
# On Mac/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### STEP 2: Start Backend Server

```bash
# While in F. WebApp and .venv activated
python app_integrated.py

# Should see:
# ✓ NutritionService imported successfully
# ✓ GreedyAlgorithmInterface imported successfully
# ✓ NutritionService initialized
# ✓ GreedyAlgorithmInterface initialized
# * Running on http://localhost:5000
```

### STEP 3: Prepare Frontend

```bash
# In NEW terminal, navigate to frontend
cd "F. WebApp/Frontend"

# Install dependencies (run once)
npm install

# Start dev server
npm run dev

# Should see:
# VITE v... ready in ... ms
# ➜  Local:   http://localhost:5173
```

### STEP 4: Test di Browser

1. Open http://localhost:5173
2. Isi form:
   - Gender: Male
   - Age: 25
   - Weight: 70
   - Height: 175
   - Activity: Moderate
   - Disease: (none atau DM2)
   - Food preferences: (pilih beberapa)
   - Algorithm: Greedy
3. Click **"Analisis Profil"** → check "Profile" tab
   - Should see BMI, BMR, TDEE calculations
4. Click **Menu** tab → Click **"Buat Menu Sekarang"**
   - Should see generated menu dengan meals
5. Done! ✅

---

## 📚 UNDERSTANDING THE SYSTEM FLOW

### What is `C. System Flow`?

**`C. System Flow/`** adalah core logic yang:
- ✅ Calculate nutrition needs (BMI, BMR, TDEE)
- ✅ Load disease guidelines (untuk DM2, Hypertension, dll)
- ✅ Merge guidelines dengan DRI fallback
- ✅ Load food database
- ✅ Prepare constraints untuk algorithms

**Main files:**
- `main.py` - CLI interface untuk testing
- `nutrition_service.py` - Main service class
- `data_loader.py` - Load food & guideline data
- INTEGRATION_GUIDE.md - Detailed documentation

### What is `D. Model`?

**`D. Model/`** punya 2 algorithms:
- **Greedy Algorithm** - Faster, simpler
  - Select foods greedily berdasarkan score
  - Good untuk real-time menu generation
  
- **Genetic Algorithm** - Slower, better quality
  - Evolves population of menus
  - Good untuk optimal solutions

Backend (`app_integrated.py`) currently use **Greedy** via:
```python
from D. Model/Greedy Algorithm/greedy_interface.py
```

### Testing System Flow (CLI)

Kamu bisa test langsung tanpa frontend/backend:

```bash
cd "C. System Flow"
python main.py

# Interactive CLI akan ask:
# - Gender
# - Age
# - Weight
# - Height
# - Activity factor
# - Disease
# - Food preferences

# Output:
# - BMI calculation
# - TDEE calculation
# - Nutrition guidelines
# Ready untuk GA/Greedy!
```

---

## 🔌 API ENDPOINTS

### POST /api/analyze

**Request:**
```json
{
  "gender": "M",
  "age": 25,
  "weight": 70,
  "height": 175,
  "activity": "1.55",
  "diseases": ["dm2"],
  "food_preferences": ["Western", "Asian"],
  "algorithm": "greedy"
}
```

**Response:**
```json
{
  "success": true,
  "energy": {
    "bmi": 22.9,
    "bbr": 67.5,
    "bmr": 1700,
    "tdee": 2635
  },
  "guidelines": {
    "energy_kcal": {"min": 1800, "max": 2200, ...},
    "protein_g": {"min": 63, "max": 99, ...},
    ...
  },
  "food_data": {
    "total_items": 4425,
    "filtered_items": 1200,
    ...
  }
}
```

### POST /api/generate-menu

**Request:**
```json
{
  "algorithm": "greedy",
  "user_profile": {...},
  "analysis_data": {...},
  "user_input": {...}
}
```

**Response:**
```json
{
  "success": true,
  "menu_plan": {
    "meals": {
      "breakfast": {
        "items": [...],
        "calories": 500,
        "protein": 15,
        ...
      },
      "lunch": {...},
      "dinner": {...},
      "snack": {...}
    },
    "total_calories": 2000,
    "total_protein": 75,
    ...
  }
}
```

---

## 🚨 TROUBLESHOOTING

### ❌ "NutritionService not found"

```
Backend shows: ❌ Failed to import NutritionService
```

**Solution:**
- Make sure you're in `F. WebApp` folder
- Check `C. System Flow` folder exists
- Path: `../C. System Flow` should be correct

```bash
# Test path
python -c "import sys; print(sys.path)"
```

### ❌ "CORS error in browser console"

```
Access to XMLHttpRequest at 'http://localhost:5000'
has been blocked by CORS policy
```

**Solution:**
- Make sure `app_integrated.py` punya CORS enabled:
  ```python
  CORS(app, resources={
      r"/api/*": {
          "origins": ["http://localhost:5173", ...],
          ...
      }
  })
  ```
- Restart backend server

### ❌ "Cannot find module 'react'"

```
Frontend shows: Cannot find module 'react'
```

**Solution:**
```bash
cd "F. WebApp/Frontend"
npm install react react-dom
npm run dev
```

### ❌ Menu generation is slow atau error

**Check:**
1. Backend console untuk error messages
2. Food database tersedia di `C. System Flow`
3. Algorithm parameters reasonable

---

## 📦 DEPLOYMENT

### Deploy Frontend (Vercel)

```bash
cd "F. WebApp/Frontend"

# Install Vercel CLI
npm install -g vercel

# Deploy
vercel

# Or via GitHub:
# 1. Push to GitHub
# 2. Go to vercel.com
# 3. Import repository
# 4. Select "F. WebApp/Frontend" as root
# 5. Deploy
```

### Deploy Backend (Render)

```bash
# 1. Push to GitHub
# 2. Go to render.com
# 3. New Web Service
# 4. Connect GitHub repo
# 5. Configuration:
#    - Root: F. WebApp
#    - Build: pip install -r requirements.txt
#    - Start: gunicorn -w 4 -b 0.0.0.0:10000 app_integrated:app
# 6. Deploy
```

### Connect Frontend to Production Backend

After deployment, update Vercel environment:

```bash
# In Vercel dashboard - Settings - Environment Variables
VITE_API_URL = https://your-render-backend.onrender.com
```

Then redeploy frontend.

---

## 📝 PROJECT STRUCTURE

```
TugasAkhirDSS/
├── A. Data/                    # Raw data files
├── B. Preprocessing/           # Data preprocessing scripts
├── C. System Flow/             # ⭐ CORE SYSTEM
│   ├── main.py                 # CLI interface
│   ├── nutrition_service.py    # Main service
│   ├── data_loader.py          # Load food data
│   └── INTEGRATION_GUIDE.md    # Detailed docs
├── D. Model/                   # 🤖 ALGORITHMS
│   ├── Greedy Algorithm/
│   ├── Genetic Algorithm/
│   └── IMPLEMENTATION_GUIDE.md
├── E. Evaluation/              # Testing & evaluation
├── F. WebApp/                  # 🌐 WEB APPLICATION
│   ├── app_integrated.py       # Flask backend
│   ├── requirements.txt        # Python dependencies
│   ├── Backend/
│   └── Frontend/               # React app
│       ├── src/
│       ├── package.json        # npm dependencies
│       └── vite.config.ts
└── Z. Trash/                   # Old/unused files
```

---

## ✅ CHECKLIST

- [ ] System Flow (C.) understand
- [ ] Backend (F. WebApp/app_integrated.py) bisa start
- [ ] Frontend (F. WebApp/Frontend) bisa npm run dev
- [ ] Test locally http://localhost:5173
- [ ] Form submit → get analysis result
- [ ] Generate menu → get menu output
- [ ] Deploy frontend ke Vercel
- [ ] Deploy backend ke Render
- [ ] Connect frontend ke production backend
- [ ] Share URL ke dosen! 🎉

---

## 🤔 NEXT STEPS (What to Do Now)

1. **Test locally:**
   ```bash
   cd "F. WebApp"
   .venv\Scripts\activate
   python app_integrated.py    # Terminal 1
   
   # Terminal 2
   cd "F. WebApp/Frontend"
   npm run dev
   
   # Browser: http://localhost:5173
   ```

2. **Once working locally, deploy:**
   - Push to GitHub
   - Deploy frontend to Vercel
   - Deploy backend to Render
   - Update environment variables

3. **Share:**
   - Frontend URL: `https://your-app.vercel.app`
   - Backend URL: `https://your-api.onrender.com`

---

## 💪 YOU GOT THIS!

Kalau ada error atau stuck, check error message di:
1. Browser Console (F12 → Console)
2. Backend terminal (stdout/stderr)
3. Troubleshooting section di guide ini

Semangat! 🚀

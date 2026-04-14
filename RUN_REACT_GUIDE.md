# ✅ RUN REACT FRONTEND + FLASK BACKEND

## STEP 1: Terminal 1 - Start Backend

```bash
cd "F. WebApp"
.venv\Scripts\activate
python app_integrated.py
```

**Expected Output:**
```
✓ NutritionService imported successfully
✓ GreedyAlgorithmInterface imported successfully
✓ NutritionService initialized
✓ GreedyAlgorithmInterface initialized
 * Running on http://localhost:5000
```

✅ **Keep this terminal running! Don't close!**

---

## STEP 2: Terminal 2 - Start React Frontend

**Open NEW terminal** (don't close Terminal 1!)

```bash
cd "F. WebApp/Frontend"
npm run dev
```

**Expected Output:**
```
  VITE v5.x.x  ready in xxx ms

   ➜  Local:   http://localhost:5173
   ➜  press h + enter to show help
```

✅ **Keep this terminal running too!**

---

## STEP 3: Open Browser

**Go to: http://localhost:5173**

You should see the React Nutrition DSS app with:
- Form for user input
- Profile tab
- Nutrition tab
- Menu tab
- Constraint tab

---

## STEP 4: Test

1. **Fill form:**
   - Gender: Male
   - Age: 25
   - Weight: 70
   - Height: 175
   - Activity: Moderate (1.55)
   - Disease: (leave empty or pick one)
   - Food preferences: Pick a few
   - Algorithm: Greedy

2. **Click: "Analisis Profil"**
   - Should see loading
   - Then see BMI, TDEE on Profile tab
   - ✅ If you see this = connection works!

3. **Click: Menu tab → "Buat Menu Sekarang"**
   - Should generate menu with meals
   - ✅ Done!

---

## 📍 TWO SERVERS RUNNING:

| Server | Port | URL | Purpose |
|--------|------|-----|---------|
| **Backend (Flask)** | 5000 | http://localhost:5000 | API only (hidden) |
| **Frontend (React)** | 5173 | http://localhost:5173 | Website (open this) |

**You only open 5173 in browser!**
The 5000 backend runs in background and handles calculations.

---

## 🐛 If Error

### "Cannot find module 'react'"
```bash
cd "F. WebApp/Frontend"
npm install
npm run dev
```

### "CORS error in console"
- Restart backend (Terminal 1)
- Refresh browser

### "Network error when submit form"
- Check if both terminals running
- Check no other app using port 5000 or 5173

---

## ✅ Success = See This:

**Terminal 1 (Backend):**
```
✓ NutritionService initialized
✓ GreedyAlgorithmInterface initialized
 * Running on http://localhost:5000
```

**Terminal 2 (Frontend):**
```
➜  Local:   http://localhost:5173
```

**Browser (http://localhost:5173):**
```
[Nutrition DSS Website with Form]
Fill form → Click Analisis → See Results
```

---

**NOW YOU'RE GOOD TO GO!** 🚀

Use React, keep backend running, all working! ✅

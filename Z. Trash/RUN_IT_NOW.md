# 🎯 RUN IT NOW - Step by Step

**Target**: Aplikasi jalan di http://localhost:5173 dalam 10 menit ✅

---

## STEP 1: Start Backend (Terminal 1)

```bash
# Copy-paste these exactly:

cd "F. WebApp"
.venv\Scripts\activate
python app_integrated.py
```

**Expected output:**
```
✓ NutritionService imported successfully
✓ GreedyAlgorithmInterface imported successfully
✓ NutritionService initialized
✓ GreedyAlgorithmInterface initialized
 * Running on http://localhost:5000
```

✅ **Don't close this terminal!** Backend must keep running.

---

## STEP 2: Start Frontend (Terminal 2 - NEW)

```bash
# Open NEW terminal (don't close terminal 1!)
# Copy-paste these exactly:

cd "F. WebApp\Frontend"
npm run dev
```

**Expected output:**
```
   VITE v5.x.x  ready in xxx ms

   ➜  Local:   http://localhost:5173
   ➜  press h + enter to show help
```

✅ **Don't close this terminal either!** Frontend server must keep running.

---

## STEP 3: Test di Browser

1. Open browser → go to `http://localhost:5173`
2. You should see the app page with form

---

## STEP 4: Fill Form & Test

**Fill the form:**
- Gender: **Male**
- Age: **25**
- Weight: **70**
- Height: **175**
- Activity: **Moderate Activity (1.55)**
- Disease: **(None selected)**
- Food Preferences: **Check a few** (Western, Asian, etc)
- Algorithm: **Greedy**

**Click: "Analisis Profil"**

Should see loading spinner, then profile data appears on Profile tab with:
- BMI = 22.9
- BBR = 67.5
- BMR = 1700
- TDEE = 2635

✅ **If you see this, connection works!**

---

## STEP 5: Generate Menu

Go to **"Menu"** tab → Click **"Buat Menu Sekarang"**

Should see:
- Breakfast, Lunch, Dinner, Snack cards
- Each with food items
- Macros summary
- Download button

✅ **If you see this, everything works!**

---

## 🐛 STUCK? Check This

### Backend tidak start (Terminal 1)

```
❌ ModuleNotFoundError: No module named 'nutrition_service'
```

**Fix:**
```bash
# Make sure C. System Flow folder exists
# Path should be: TugasAkhirDSS/C. System Flow/nutrition_service.py

# Check exact structure:
ls "../C. System Flow/"
```

---

### Frontend npm error (Terminal 2)

```
❌ npm: command not found
```

**Fix:** Install Node.js from nodejs.org

```bash
❌ Cannot find module 'react'
```

**Fix:**
```bash
cd "F. WebApp/Frontend"
npm install
npm run dev
```

---

### Browser CORS error

**Symptom:**
```
Access to XMLHttpRequest at 'http://localhost:5000'
from origin 'http://localhost:5173' has been blocked by CORS policy
```

**Fix:**
- Restart backend: Kill terminal 1 and restart
- Make sure `app_integrated.py` has CORS enabled

---

### Form submit not working

**Check:**
1. Backend terminal - any error messages?
2. Browser console (F12 → Console) - any red errors?
3. Network tab - is request going to localhost:5000?

**If stuck:**
```bash
# Restart everything:
# Kill both terminals (Ctrl+C)
# Run STEP 1 and STEP 2 again
# Refresh browser (Ctrl+R or F5)
```

---

## 📱 WHAT EACH TAB DOES

| Tab | What It Does |
|-----|-------------|
| **Profile** | Shows your BMI, BMR, TDEE after "Analisis Profil" |
| **Nutrition** | Shows detailed nutrition guidelines (protein, carbs, etc) |
| **Menu** | Shows the generated menu when you click "Buat Menu Sekarang" |
| **Constraints** | Shows nutrition constraints (detailed view) |

---

## ⚡ QUICK TEST COMMANDS

**Check if Node.js installed:**
```bash
node --version
npm --version
```

**Check if Python installed:**
```bash
python --version
```

**Check if virtual env works:**
```bash
cd "F. WebApp"
.venv\Scripts\activate
pip list
```

---

## ✅ SUCCESS CHECKLIST

- [ ] Run `python app_integrated.py` → See ✓ messages
- [ ] Run `npm run dev` → See port 5173
- [ ] Open http://localhost:5173 → See form
- [ ] Fill form → Click "Analisis Profil" → See BMI/TDEE
- [ ] Go Menu tab → Click "Buat Menu" → See breakfast/lunch/dinner
- [ ] All working? **GREAT! You're done!** 🎉

---

## 🎊 NEXT STAGE (After Local Works)

Once everything working locally, you can:

1. **Deploy to production** (Vercel + Render)
2. **Share URL with dosen**
3. **Celebrate!** 🚀

But first, get it working locally using this guide!

---

**Stuck?** Check the Troubleshooting section di QUICK_START.md

Good luck! 💪

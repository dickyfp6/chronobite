# Quick Start Guide - Webapp Integration

## 🚀 Start in 5 Minutes

### Step 1: Navigate to WebApp
```bash
cd "F. WebApp"
```

### Step 2: Run Flask
```bash
python app_integrated.py
```

**Expected Output**:
```
✓ NutritionService imported successfully
✓ NutritionService initialized
✓ GreedyAlgorithmInterface imported successfully
✓ GreedyAlgorithmInterface initialized
 * Running on http://127.0.0.1:5000
```

### Step 3: Open Browser
```
http://localhost:5000/app
```

### Step 4: Complete User Journey

**Form Section (Steps 1-5)**:
1. **Step 1 - Profile**
   - Gender: Select M/F
   - Age: Enter 30 (or any 18-100)
   - Weight: Enter 70 (kg)
   - Height: Enter 170 (cm)
   - → Click "Lanjut"

2. **Step 2 - Activity**
   - Select "Active or Moderately Active" (1.845)
   - → Click "Lanjut ke Konfirmasi"

3. **Step 3 - Diseases**
   - Keep "Normal" selected (or choose 1-3 conditions)
   - → Click "Lanjut"

4. **Step 4 - Food Preferences**
   - Leave empty OR select 1-3 cuisines
   - → Click "Lanjut"

5. **Step 5 - Algorithm**
   - Keep "Greedy" selected
   - → Click "Analisis Profile"

**Results Section**:
6. **Tab 1: Profile & Anthropometrics**
   - See: BMI, BBI, Age Group, Energy (BMR/TDEE), Macros

7. **Tab 2: Nutrition Guidelines**
   - See: Nutrient ranges (Macros + Micros)
   - Filter: All / Makro / Mikro

8. **Tab 3: Menu Generation**
   - Click "Generate Menu"
   - See: 4 meals (Breakfast, Lunch, Dinner, Snack)
   - Click item → see details modal

9. **Tab 4: Constraints**
   - See: Calorie target compliance

### Step 5: Test Interactions

**Menu Operations**:
- Click menu item → Details modal
- "Regenerate" → New menu
- "Print Menu" → Browser print dialog
- "Save Menu" → localStorage
- "Download JSON" → Export
- "Bagikan" → Share (if supported)

**Form Adjustments**:
- Click "<" on any tab (except after generating)
- Change values
- Generate new menu with new parameters

---

## 🧪 Test Cases

### Test 1: Basic Happy Path
**Input**: 30M, 70kg, 170cm, Activity 1.845, Normal, No preferences, Greedy
**Expected**: Complete analysis + menu generation

**Verify**:
- ✓ Analysis shows correct BMI (~24.2)
- ✓ TDEE shown (~3228 kkal)
- ✓ Menu has 4 meals
- ✓ Total calories ≈ TDEE

### Test 2: Multiple Diseases
**Input**: 35F, 65kg, 160cm, Activity 1.545, DM2 + Hypertension, Asian + Mediterranean
**Expected**: Merged disease constraints

**Verify**:
- ✓ Diseases show as badges
- ✓ Food preferences show as list
- ✓ Menu respects constraints

### Test 3: Input Validation
**Input**: Age 15 (invalid) or Height 350 (invalid)
**Expected**: Error message

**Verify**:
- ✓ Form shows validation error
- ✓ "Analisis Profile" button disabled
- ✓ Can't proceed

### Test 4: API Error Handling
**Scenario**: Disconnect internet during menu generation
**Expected**: Error toast notification

**Verify**:
- ✓ Error message displayed
- ✓ Can retry menu generation

---

## 🔍 Troubleshooting

### Issue: "NutritionService not available"
**Solution**:
1. Check `C. System Flow/nutrition_service.py` exists
2. Verify imports in `app_integrated.py`
3. Check Flask logs for import errors

```bash
# Try importing manually
python -c "from nutrition_service import NutritionService; print('OK')"
```

### Issue: "Greedy Algorithm not available"
**Solution**:
1. Check `D. Model/Greedy Algorithm/` folder exists
2. Verify `greedy_interface.py` exists
3. Check Flask logs for import errors

```bash
# Try importing manually
python -c "from Greedy_Algorithm.greedy_interface import GreedyAlgorithmInterface; print('OK')"
```

### Issue: Form doesn't submit
**Solution**:
1. Open DevTools → Console
2. Check for JavaScript errors
3. Check Network tab for POST request failure
4. Verify /api/analyze endpoint responds

```javascript
// Test in browser console
fetch('/api/health-check').then(r => r.json()).then(d => console.log(d))
// Look for: {"status": "ok", "services": {...}}
```

### Issue: Menu doesn't generate
**Solution**:
1. Check /api/analyze worked first
2. Check food database loaded in logs
3. Check Greedy Algorithm initialized
4. Try /api/health-check to see service status

---

## 📊 Sample Data

### Test Profile 1 (Normal)
```
Gender: M
Age: 30
Weight: 70 kg
Height: 170 cm
Activity: 1.845 (Active)
Diseases: Normal
Preferences: None
Expected TDEE: ~3228 kkal
Expected BMI: ~24.2 (Normal)
```

### Test Profile 2 (Diabetic)
```
Gender: F
Age: 45
Weight: 65 kg
Height: 160 cm
Activity: 1.545 (Sedentary)
Diseases: DM2, Hypertension
Preferences: Asian
Expected TDEE: ~2196 kkal
Expected BMI: ~25.4 (Overweight)
Carbs: 45-55% (more restricted for DM2)
Protein: 15-20%
Fat: 25-35%
```

### Test Profile 3 (CVD Risk)
```
Gender: M
Age: 55
Weight: 85 kg
Height: 175 cm
Activity: 1.845 (Active)
Diseases: CVD, Cholesterol, Hypertension
Preferences: Mediterranean, Western
Expected TDEE: ~3650 kkal
Expected BMI: ~27.7 (Overweight)
Fat: 20-30% (lower for CVD)
```

---

## 🎯 Key Features to Test

### Form Validation ✓
- [x] Age must be 18-100
- [x] Height must be 100-300 cm
- [x] Weight must be > 0
- [x] "Next" button disabled if invalid
- [x] "Normal" exclusive (auto-selects alone)
- [x] Max 3 diseases
- [x] Max 3 food preferences

### Real-time Calculations ✓
- [x] BMI updates on weight/height change
- [x] TDEE updates on activity change
- [x] Macros update on disease change

### Analysis ✓
- [x] /api/analyze returns correct structure
- [x] Anthropometrics calculated correctly
- [x] Energy (BMR/TDEE) accurate
- [x] Guidelines 27-30 nutrients
- [x] Meal distribution shown

### Menu ✓
- [x] /api/generate-menu works
- [x] Returns 4 meals (breakfast, lunch, dinner, snack)
- [x] 10 total meal slots
- [x] Each item has: name, calories, macros, score, ingredients
- [x] Total calories ≈ TDEE (±200)

### UI ✓
- [x] All tabs switch properly
- [x] Item modal opens/closes
- [x] Notifications appear & disappear
- [x] Buttons have loading states
- [x] Responsive on mobile

---

## 🔌 API Endpoints Reference

### Health Check
```bash
GET http://localhost:5000/api/health-check

# Response:
{
  "status": "ok",
  "services": {
    "nutrition_service": true,
    "greedy_algorithm": true
  },
  "timestamp": "2024-01-15T10:30:45.123456"
}
```

### Analyze Profile
```bash
POST http://localhost:5000/api/analyze
Content-Type: application/json

{
  "gender": "M",
  "age": 30,
  "weight": 70.0,
  "height": 170.0,
  "activity": "1.845",
  "diseases": ["normal"],
  "food_preferences": []
}

# Response: Complete nutrition analysis (see docs)
```

### Generate Menu
```bash
POST http://localhost:5000/api/generate-menu
Content-Type: application/json

{
  "algorithm": "greedy",
  "user_profile": {...},
  "analysis_data": {...},
  "user_input": {...}
}

# Response: MenuPlan as JSON with 4 meals
```

---

## 🎨 UI Pages

### Landing Page
```
http://localhost:5000/
```
- Simple landing/intro page
- Link to main app

### Main App
```
http://localhost:5000/app
```
- Full nutrition DSS interface
- 5-step form
- Results tabs
- Menu display

---

## 💾 Data Persistence

### LocalStorage
- Saved automatically when "Simpan Menu" clicked
- Key: `lastMenu`
- Contains: formData, analysisResult, menuResult, timestamp
- Persists across page reloads
- Use DevTools → Application → Storage → localStorage

### Accessing Saved Data
```javascript
// In browser console
const saved = JSON.parse(localStorage.getItem('lastMenu'))
console.log(saved)
```

---

## 📱 Device Testing

### Desktop
- [ ] Chrome/Edge/Firefox - test responsive layout
- [ ] DevTools mobile view 375px, 768px, 1024px

### Mobile
- [ ] iOS Safari
- [ ] Android Chrome
- [ ] test touch interactions
- [ ] test input on mobile keyboard

---

## ⏱️ Performance Targets

- [ ] Page load: < 2s
- [ ] /api/analyze response: < 1s
- [ ] /api/generate-menu response: < 500ms
- [ ] Menu display render: < 300ms
- [ ] Form validation: immediate (< 100ms)

---

## 🐛 Common Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| "NutritionService not available" | Import failed | Check path, run manual import test |
| "Greedy Algorithm not available" | Import failed | Check Greedy Algorithm folder exists |
| Menu generation timeout | Processing too slow | Check food database size, Increase timeout |
| Form validation broken | Alpine.js error | Check console, Check syntax |
| API 500 error | Backend exception | Check Flask logs |
| API 400 error | Invalid input | Check input format, Check validation rules |
| No menu items | Insufficient candidates | Check food database loaded |
| Incorrect calories | Calculation error | Check TDEE formula, Check meal distribution |

---

## 📚 Documentation Files

1. **WEBAPP_INTEGRATION_GUIDE.md** - Complete integration documentation
2. **IMPLEMENTATION_CHECKLIST.md** - Feature completion checklist
3. **app_integrated.py** - Backend code with inline comments
4. **templates/index_comprehensive.html** - Frontend code with inline comments
5. **QUICK_START_GUIDE.md** - This file

---

## ✅ Sign-Off

- [ ] Ran `python app_integrated.py` successfully
- [ ] Opened http://localhost:5000/app
- [ ] Completed form all 5 steps
- [ ] Clicked "Analisis Profile"
- [ ] Generated menu
- [ ] All 4 tabs working
- [ ] Item modal works
- [ ] No console errors
- [ ] Ready to test advanced features

---

**Need Help?**
1. Check Flask logs for errors
2. Open Browser DevTools (F12) → Console
3. Check Network tab for failed requests
4. Review WEBAPP_INTEGRATION_GUIDE.md for details
5. Check issue-specific troubleshooting above

**Last Updated**: Now  
**Version**: 1.0 - MVP


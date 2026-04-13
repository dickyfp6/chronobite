# Integration Testing Reference

## Test Environment Setup

### Prerequisites
```bash
# Python 3.8+
python --version

# Flask
pip list | grep Flask

# All required packages installed in System Flow
cd "C. System Flow"
pip install -r requirements.txt  # if exists

# All required packages installed in Model
cd "D. Model/Greedy Algorithm"
pip install -r requirements.txt  # if exists
```

### Verify Dependencies
```bash
# Test NutritionService import
cd "F. WebApp"
python -c "import sys; sys.path.insert(0, '..\\C. System Flow'); from nutrition_service import NutritionService; print('✓ NutritionService OK')"

# Test Greedy Algorithm import
python -c "import sys; sys.path.insert(0, '..\\D. Model'); from Greedy_Algorithm.greedy_interface import GreedyAlgorithmInterface; print('✓ GreedyAlgorithmInterface OK')"
```

---

## Test Scenario 1: Form Validation

### Test 1.1: Age Validation
**Input**: Age 15 (invalid)
**Expected**: Error message, "Next" button disabled
**Result**: ⬜ _____

**Input**: Age 18 (minimum valid)
**Expected**: No error, "Next" button enabled
**Result**: ⬜ _____

**Input**: Age 100 (maximum valid)
**Expected**: No error, "Next" button enabled
**Result**: ⬜ _____

**Input**: Age 101 (invalid)
**Expected**: Error message, "Next" button disabled
**Result**: ⬜ _____

---

### Test 1.2: Height Validation
**Input**: Height 99 (invalid)
**Expected**: Error message, "Next" button disabled
**Result**: ⬜ _____

**Input**: Height 100 (minimum valid)
**Expected**: No error, "Next" button enabled
**Result**: ⬜ _____

**Input**: Height 300 (maximum valid)
**Expected**: No error, "Next" button enabled
**Result**: ⬜ _____

**Input**: Height 301 (invalid)
**Expected**: Error message, "Next" button disabled
**Result**: ⬜ _____

---

### Test 1.3: Weight Validation
**Input**: Weight 0 (invalid)
**Expected**: Error message, "Next" button disabled
**Result**: ⬜ _____

**Input**: Weight 0.1 (valid)
**Expected**: No error, "Next" button enabled
**Result**: ⬜ _____

**Input**: Weight 150 (normal)
**Expected**: No error, "Next" button enabled
**Result**: ⬜ _____

---

### Test 1.4: BMI Real-time Calculation
**Input**: Weight 70, Height 170, Gender M
**Expected**: BMI ≈ 24.2 (Normal)
**Shown**: ⬜ _____

**Change**: Weight to 85
**Expected**: BMI ≈ 29.4 (Overweight)
**Shown**: ⬜ _____

**Change**: Weight to 100
**Expected**: BMI ≈ 34.6 (Obesity)
**Shown**: ⬜ _____

---

## Test Scenario 2: Disease Selection

### Test 2.1: Single Disease
**Input**: Select "Normal"
**Expected**: Only Normal selected, checkbox marked
**Result**: ⬜ _____

### Test 2.2: Multiple Diseases
**Input**: Select DM2
**Expected**: Normal unselected automatically, DM2 selected
**Result**: ⬜ _____

**Input**: Add Hypertension
**Expected**: Both DM2 and Hypertension selected (2/3)
**Result**: ⬜ _____

**Input**: Add CVD
**Expected**: All three selected (3/3)
**Result**: ⬜ _____

**Input**: Try to add Cholesterol
**Expected**: Disabled (max 3 already), tooltip or unable to click
**Result**: ⬜ _____

### Test 2.3: "Normal" Exclusive Behavior
**Input**: Select Normal
**Expected**: All others unselected
**Result**: ⬜ _____

---

## Test Scenario 3: Activity Factor

### Test 3.1: TDEE Calculation
**Profile**: 30M, 70kg, 170cm

**Input**: Activity 1.545 (Sedentary)
**Expected**: TDEE ≈ 2700 kkal (BMR × 1.545)
**Shown**: ⬜ _____

**Input**: Activity 1.845 (Moderate)
**Expected**: TDEE ≈ 3228 kkal (BMR × 1.845)
**Shown**: ⬜ _____

**Input**: Activity 2.2 (Vigorous)
**Expected**: TDEE ≈ 3848 kkal (BMR × 2.2)
**Shown**: ⬜ _____

---

## Test Scenario 4: API Endpoints

### Test 4.1: /api/analyze Endpoint
```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "gender": "M",
    "age": 30,
    "weight": 70,
    "height": 170,
    "activity": "1.845",
    "diseases": ["normal"],
    "food_preferences": []
  }'
```

**Expected Response**: 
```json
{
  "success": true,
  "anthropometrics": {
    "bmi": 24.2,
    "bmi_category": "Normal",
    "..": ".."
  },
  "energy": {
    "bmr": 1750,
    "tdee": 3228
  },
  "guidelines": {
    "nutrients": { "..": ".." }
  }
}
```

**Result**: ⬜ _____

---

### Test 4.2: /api/analyze with Invalid Age
```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "gender": "M",
    "age": 15,
    "weight": 70,
    "height": 170,
    "activity": "1.845",
    "diseases": ["normal"],
    "food_preferences": []
  }'
```

**Expected Response**:
```json
{
  "success": false,
  "error": "Age must be 18-100"
}
```
**Status**: 400

**Result**: ⬜ _____

---

### Test 4.3: /api/generate-menu Endpoint
```bash
curl -X POST http://localhost:5000/api/generate-menu \
  -H "Content-Type: application/json" \
  -d '{
    "algorithm": "greedy",
    "user_profile": { "gender": "M", "age": 30, ... },
    "analysis_data": { "energy": { "tdee": 3228 }, ... },
    "user_input": { ... }
  }'
```

**Expected Response**:
```json
{
  "success": true,
  "menu_plan": {
    "algorithm_used": "Greedy",
    "total_calories": 2150,
    "breakfast": { "items": [...] },
    "lunch": { "items": [...] },
    "dinner": { "items": [...] },
    "snack": { "items": [...] }
  }
}
```

**Result**: ⬜ _____

---

## Test Scenario 5: Menu Generation

### Test 5.1: Basic Menu Generation
**Profile**: 30M, 70kg, 170cm, Normal, Greedy
**Expected**:
- 4 meals displayed (Breakfast, Lunch, Dinner, Snack)
- Total ≈ 3228 kkal (TDEE)
- Calorie distribution correct

**Result**: ⬜ _____

---

### Test 5.2: Menu Item Structure
**Expected for Breakfast**:
- 3 items (e.g., Main + Side + Drink)
- Each item shows:
  - Name
  - Serving size (g)
  - Calories
  - Score (0-100)
  - Main ingredients

**Result**: ⬜ _____

---

### Test 5.3: Regenerate Menu
**Action**: Click "Regenerate"
**Expected**: New menu generated with same TDEE
**Result**: ⬜ _____

---

## Test Scenario 6: UI Interactions

### Test 6.1: Tab Switching
**Action**: Click each tab (Profile | Nutrition | Menu | Constraints)
**Expected**: Tab content switches, bottom border indicator moves
**Result**: ⬜ _____

### Test 6.2: Item Details Modal
**Action**: Click a menu item
**Expected**: 
- Modal opens
- Item details displayed (name, calories, macros, ingredients)
- Micronutrients shown (top 10)
- Halal status shown
**Result**: ⬜ _____

**Action**: Click X button
**Expected**: Modal closes
**Result**: ⬜ _____

### Test 6.3: Notifications
**Action**: Generate menu
**Expected**: Toast notification appears (top right)
**Expected**: Auto-dismiss after ~3 seconds
**Result**: ⬜ _____

---

## Test Scenario 7: Real-time Recalculation

### Test 7.1: Change Form Values
**Current**: 30M, 70kg, 170cm, Activity 1.845
**Action**: Change weight to 80 kg
**Expected**: 
- BMI updates
- TDEE updates
- All calculations reflect new values

**Result**: ⬜ _____

**Action**: Change disease to "DM2"
**Expected**:
- Macro ranges update
- Guidelines update
- If menu was generated, should regenerate

**Result**: ⬜ _____

---

## Test Scenario 8: Download/Share Functions

### Test 8.1: Download JSON
**Action**: Click "Download JSON" button
**Expected**: 
- Menu JSON file downloaded
- Filename: menu.json
- Content valid JSON

**Result**: ⬜ _____

### Test 8.2: Print Menu
**Action**: Click "Print Menu" button
**Expected**: 
- Print dialog appears
- Can preview menu
- Can print to file/printer

**Result**: ⬜ _____

### Test 8.3: Save Menu
**Action**: Click "Save Menu" button
**Expected**: 
- Toast "Menu saved locally"
- Data persisted in localStorage
- Can reload page and menu still there

**Result**: ⬜ _____

### Test 8.4: Share Menu
**Action**: Click "Share" button
**Expected**: 
- Native share dialog (if available)
- Or fallback message

**Result**: ⬜ _____

---

## Test Scenario 9: Performance

### Test 9.1: Page Load Time
**Measure**: Time to fully load http://localhost:5000/app
**Expected**: < 2 seconds
**Actual**: _______ seconds

**Result**: ⬜ _____

---

### Test 9.2: Form Navigation Speed
**Measure**: Time to navigate through all 5 form steps
**Expected**: Immediate (< 200ms each step)
**Actual**: _______ ms

**Result**: ⬜ _____

---

### Test 9.3: API Response Time
**Measure**: Time for /api/analyze to respond
**Expected**: < 1 second
**Actual**: _______ ms

**Result**: ⬜ _____

### Test 9.4: Menu Generation Time
**Measure**: Time for /api/generate-menu to respond
**Expected**: < 500ms (Greedy)
**Actual**: _______ ms

**Result**: ⬜ _____

---

## Test Scenario 10: Error Scenarios

### Test 10.1: Network Error During Analysis
**Simulate**: Disconnect WiFi during analyze click
**Expected**: 
- Error toast displayed
- Can retry
- Form still editable

**Result**: ⬜ _____

---

### Test 10.2: Network Error During Menu Generation
**Simulate**: Disconnect WiFi during generate menu
**Expected**: 
- Error toast displayed
- Can retry
- Previous analysis still visible

**Result**: ⬜ _____

---

### Test 10.3: Invalid Algorithm Choice
**Input**: Genetic algorithm (not available)
**Expected**: 
- Error message: "Only Greedy algorithm available"
- Greedy option re-selected

**Result**: ⬜ _____

---

## Test Scenario 11: Mobile Responsiveness

### Test 11.1: Mobile View (375px width)
**Test**: Open on 375px device/emulation
**Expected**:
- Form visible and usable
- Buttons accessible
- Text readable
- No horizontal scroll

**Result**: ⬜ _____

### Test 11.2: Tablet View (768px width)
**Test**: Open on 768px device/emulation
**Expected**:
- 2-column layout where applicable
- Readable content
- Accessible buttons

**Result**: ⬜ _____

### Test 11.3: Desktop View (1024px+)
**Test**: Open on desktop
**Expected**:
- Proper grid layouts
- Good use of space
- Professional appearance

**Result**: ⬜ _____

---

## Test Scenario 12: Complete User Journey

### Full Journey Test
1. **Step**: Fill complete form
   - Gender: M
   - Age: 35
   - Weight: 75
   - Height: 175
   - Activity: 1.845
   - Diseases: DM2, Hypertension
   - Preferences: Asian
   - Result: ⬜ _____

2. **Step**: Click "Analisis Profile"
   - Expected: Analysis succeeds
   - Result: ⬜ _____

3. **Step**: View Tab 1 (Profile)
   - Check all values correct
   - Result: ⬜ _____

4. **Step**: View Tab 2 (Nutrition)
   - Check nutrients displayed
   - Try filtering
   - Result: ⬜ _____

5. **Step**: View Tab 3 (Menu)
   - Click "Generate Menu"
   - Expected: Menu generated
   - Result: ⬜ _____

6. **Step**: Interact with Menu
   - Click item → modal
   - Click regenerate
   - Click download
   - Result: ⬜ _____

7. **Step**: View Tab 4 (Constraints)
   - Check compliance displayed
   - Result: ⬜ _____

8. **Step**: Edit Form
   - Change one value
   - Verify recalculation
   - Expected: Values update
   - Result: ⬜ _____

---

## Test Summary

### Total Tests: ___ / ___

### Passed: ___
### Failed: ___
### Needs Refinement: ___

### Critical Issues Found:
```
1. ______________________________
2. ______________________________
3. ______________________________
```

### Minor Issues Found:
```
1. ______________________________
2. ______________________________
3. ______________________________
```

### Feedback:
```
_____________________________________________________
_____________________________________________________
_____________________________________________________
```

---

## Sign-Off

**Tester Name**: _______________  
**Date**: _______________  
**Status**: [ ] Pass [ ] Fail [ ] Needs Refinement

**Executive Summary**:
_____________________________________________________
_____________________________________________________

**Recommendations**:
_____________________________________________________
_____________________________________________________

**Next Steps**:
- [ ] Fix critical issues
- [ ] Address minor issues  
- [ ] Deploy to production
- [ ] Gather user feedback
- [ ] Iterate based on feedback


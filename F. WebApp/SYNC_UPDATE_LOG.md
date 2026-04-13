# Website Sync Update Log
**Date**: April 13, 2026  
**Status**: ✅ Synchronized with System Flow updates

## Changes Made

### 1. Input Validation Ranges
| Field | Old | New | Source |
|-------|-----|-----|--------|
| Age | 10-120 | **18-100** | System Flow (input_handler.py) |
| Height | 100-250 cm | **100-300 cm** | System Flow (input_handler.py) |
| Weight | No change | 20-300 kg | Already correct |

### 2. Activity Factor (FAO/WHO/UNU Guidelines)
**Old (5 levels):**
```
1.2 - Sedentary
1.375 - Lightly Active
1.55 - Moderately Active
1.725 - Very Active
1.9 - Extremely Active
```

**New (3 levels based on FAO/WHO/UNU 2004):**
```
1.545 - Sedentary or Light Activity
1.845 - Active or Moderately Active  
2.2 - Vigorous or Vigorously Active
```

**Updated in:**
- ✅ `app.py` - `ACTIVITY_LABELS` dict
- ✅ `app.py` - `/api/analyze` default value
- ✅ `templates/index.html` - Activity select options
- ✅ `templates/index.html` - Alpine.js initial formData (default: 1.845)
- ✅ `templates/index.html` - Reset function defaults

### 3. Food Preferences (Multi-Select Support)
**Old:** Single selection only
```javascript
food_preferences: ['Generic']  // Only one choice
```

**New:** Multi-select support
```javascript
food_preferences: []  // Can select multiple or none (all)
```

**Updated in:**
- ✅ `templates/index.html` - Preference buttons now toggle (can select multiple)
- ✅ `templates/index.html` - Added visual indicator "Dipilih: [selections]"
- ✅ `templates/index.html` - Removed "Generic" option (auto-select all if none chosen)
- ✅ `templates/index.html` - Alpine.js formData default (empty array)
- ✅ `templates/index.html` - Reset function defaults

### 4. Age Default
- Old: 25 years
- New: **30 years** (closer to typical user)

### 5. Backend API Compatibility
- ✅ `app.py` - `/api/analyze` endpoint already handles new activity factors
- ✅ `app.py` - Macro calculation logic unchanged (compatible with 3 or 5 activity levels)
- ✅ Disease handling already supports multi-disease (no changes needed)

## Files Modified
1. `F. WebApp/app.py` 
   - Updated `ACTIVITY_LABELS`
   - Updated default `activity` value in `/api/analyze`

2. `F. WebApp/templates/index.html`
   - Updated age input: min=18, max=100
   - Updated height input: max=300
   - Updated activity select options (3 levels)
   - Updated food preference buttons (multi-select)
   - Updated Alpine.js formData defaults (age: 30, activity: 1.845, food_preferences: [])
   - Updated reset() function defaults

## Testing Checklist
- [ ] Test age input validation (18-100)
- [ ] Test height input validation (100-300 cm)
- [ ] Test activity factor selection (3 options)
- [ ] Test food preference multi-select
- [ ] Test API `/api/analyze` with new activity values
- [ ] Test form reset
- [ ] Test macro calculations with new activity levels
- [ ] Verify no console errors in browser DevTools

## Backward Compatibility
⚠️ **WARNING**: Old saved form data with activity values (1.375, 1.55, 1.725, 1.9) will NOT match new options
- Solution: Browser localStorage should auto-clear on form reset
- Users need to re-select activity level if they had old bookmarks

## Related System Flow Changes (Already in Sync)
- ✅ `C. System Flow/modules/input_handler.py` - Age: 18-100, Height: 100-300
- ✅ `C. System Flow/modules/input_handler.py` - Activity: 1.545, 1.845, 2.2 (FAO/WHO/UNU)
- ✅ `C. System Flow/modules/input_handler.py` - Food preferences: Multi-select support
- ✅ `C. System Flow/nutrition_service.py` - Validated against new ranges

## Next Steps
1. Run test suite for form validation
2. Test API responses with new activity values
3. Update user documentation if activity descriptions changed
4. Clear browser caches if testing on same browser

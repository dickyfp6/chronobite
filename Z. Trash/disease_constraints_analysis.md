# Analysis of Constraints for 5 Diseases + Normal + Combined

## User Profile Input
- **Gender**: F
- **Age**: 58 years old
- **Weight**: 68.0 kg
- **Height**: 155.0 cm
- **Activity Factor**: 1.55

## Base Anthropometrics & Energy
- **BMI**: 28.30 (Overweight)
- **BBI (Ideal Weight)**: 52.9 kg
- **Age Group Classification**: Young People (18-65 years old)
- **BMR**: 1176.1 kcal/day
- **TDEE (Daily Energy Needs)**: 1823.0 kcal/day

## Disease-Specific & Combined Constraints Analysis

### NORMAL
- **Target Energy**: 1823.0 kcal
| Nutrient | Min | Max | Hard/Soft | Source / Disease(s) |
| --- | --- | --- | --- | --- |
| **carbohydrate_g** | 250.7 g | 273.4 g | HARD | guideline (normal) |
| **protein_g** | 68.4 g | 91.2 g | HARD | guideline (normal) |
| **fat_g** | 50.6 g | 60.8 g | HARD | guideline (normal) |
| **sugar_g** | 0.0 g | 91.2 g | HARD | guideline (normal) |
| **saturated_fat_g** | 0.0 g | 20.3 g | HARD | guideline (normal) |
| **cholesterol_mg** | 0.0 mg | 300.0 mg | HARD | guideline (normal) |
| **sodium_mg** | 1500.0 mg | No limit | SOFT | DRI fallback (normal) |
| **potassium_mg** | 2600.0 mg | No limit | SOFT | DRI fallback (normal) |
| **calcium_mg** | 1200.0 mg | No limit | SOFT | DRI fallback (normal) |
| **magnesium_mg** | 320.0 mg | No limit | SOFT | DRI fallback (normal) |
| **phosphorus_mg** | 700.0 mg | No limit | SOFT | DRI fallback (normal) |

### DM2
- **Target Energy**: 1621.8 kcal
| Nutrient | Min | Max | Hard/Soft | Source / Disease(s) |
| --- | --- | --- | --- | --- |
| **energy_kcal** | 1800.0 kcal | 2200.0 kcal | HARD | guideline (dm2) |
| **carbohydrate_g** | 202.7 g | 223.0 g | HARD | guideline (dm2) |
| **protein_g** | 48.7 g | 60.8 g | HARD | guideline (dm2) |
| **fat_g** | 0.0 g | 54.1 g | HARD | guideline (dm2) |
| **cholesterol_mg** | 0.0 mg | 300.0 mg | HARD | guideline (dm2) |
| **sodium_mg** | 0.0 mg | 2300.0 mg | HARD | guideline (dm2) |
| **potassium_mg** | 2600.0 mg | 3400.0 mg | HARD | guideline (dm2) |
| **calcium_mg** | 950.0 mg | 1050.0 mg | HARD | guideline (dm2) |
| **magnesium_mg** | 320.0 mg | No limit | SOFT | DRI fallback (dm2) |
| **phosphorus_mg** | 700.0 mg | No limit | SOFT | DRI fallback (dm2) |
| **fiber_g** | 20.0 g | 35.0 g | HARD | guideline (dm2) |

### HYPERTENSION
- **Target Energy**: 1621.8 kcal
| Nutrient | Min | Max | Hard/Soft | Source / Disease(s) |
| --- | --- | --- | --- | --- |
| **energy_kcal** | 1995.0 kcal | 2205.0 kcal | HARD | guideline (hypertension) |
| **carbohydrate_g** | 154.1 g | 223.0 g | HARD | guideline (hypertension) |
| **protein_g** | 60.8 g | 73.0 g | HARD | guideline (hypertension) |
| **fat_g** | 45.0 g | 48.7 g | HARD | guideline (hypertension) |
| **saturated_fat_g** | 0.0 g | 10.8 g | HARD | guideline (hypertension) |
| **cholesterol_mg** | 0.0 mg | 150.0 mg | HARD | guideline (hypertension) |
| **sodium_mg** | 0.0 mg | 2300.0 mg | HARD | guideline (hypertension) |
| **potassium_mg** | 4465.0 mg | 4935.0 mg | HARD | guideline (hypertension) |
| **calcium_mg** | 800.0 mg | 1250.0 mg | HARD | guideline (hypertension) |
| **magnesium_mg** | 240.0 mg | 500.0 mg | HARD | guideline (hypertension) |
| **phosphorus_mg** | 700.0 mg | No limit | SOFT | DRI fallback (hypertension) |
| **fiber_g** | 30.0 g | 38.0 g | HARD | guideline (hypertension) |

### CVD
- **Target Energy**: 1621.8 kcal
| Nutrient | Min | Max | Hard/Soft | Source / Disease(s) |
| --- | --- | --- | --- | --- |
| **carbohydrate_g** | 154.1 g | 223.0 g | HARD | guideline (cvd) |
| **protein_g** | 60.8 g | 101.4 g | HARD | guideline (cvd) |
| **fat_g** | 45.0 g | 63.1 g | HARD | guideline (cvd) |
| **saturated_fat_g** | 0.0 g | 12.6 g | HARD | guideline (cvd) |
| **trans_fat_g** | 0.0 g | 1.8 g | HARD | guideline (cvd) |
| **cholesterol_mg** | 0.0 mg | 300.0 mg | HARD | guideline (cvd) |
| **sodium_mg** | 0.0 mg | 2300.0 mg | HARD | guideline (cvd) |
| **potassium_mg** | 2600.0 mg | No limit | SOFT | DRI fallback (cvd) |
| **calcium_mg** | 1200.0 mg | No limit | SOFT | DRI fallback (cvd) |
| **magnesium_mg** | 320.0 mg | No limit | SOFT | DRI fallback (cvd) |
| **phosphorus_mg** | 700.0 mg | No limit | SOFT | DRI fallback (cvd) |

### CHOLESTEROL
- **Target Energy**: 1621.8 kcal
| Nutrient | Min | Max | Hard/Soft | Source / Disease(s) |
| --- | --- | --- | --- | --- |
| **energy_kcal** | 1540.8 kcal | 1702.9 kcal | HARD | guideline (cholesterol) |
| **carbohydrate_g** | 0.0 g | 223.0 g | HARD | guideline (cholesterol) |
| **protein_g** | 52.7 g | 68.9 g | HARD | guideline (cholesterol) |
| **fat_g** | 45.0 g | 63.1 g | HARD | guideline (cholesterol) |
| **saturated_fat_g** | 0.0 g | 12.6 g | HARD | guideline (cholesterol) |
| **trans_fat_g** | 0.0 g | 1.8 g | HARD | guideline (cholesterol) |
| **cholesterol_mg** | 0.0 mg | 200.0 mg | HARD | guideline (cholesterol) |
| **sodium_mg** | 0.0 mg | 2300.0 mg | HARD | guideline (cholesterol) |
| **potassium_mg** | 2600.0 mg | No limit | SOFT | DRI fallback (cholesterol) |
| **calcium_mg** | 1200.0 mg | No limit | SOFT | DRI fallback (cholesterol) |
| **magnesium_mg** | 320.0 mg | No limit | SOFT | DRI fallback (cholesterol) |
| **phosphorus_mg** | 700.0 mg | No limit | SOFT | DRI fallback (cholesterol) |

### CKD
- **Target Energy**: 1621.8 kcal
| Nutrient | Min | Max | Hard/Soft | Source / Disease(s) |
| --- | --- | --- | --- | --- |
| **energy_kcal** | 2261.0 kcal | 2499.0 kcal | HARD | guideline (ckd) |
| **carbohydrate_g** | 223.0 g | 243.3 g | HARD | guideline (ckd) |
| **protein_g** | 40.8 g | 54.4 g | HARD | guideline (ckd) |
| **fat_g** | 45.0 g | 63.1 g | HARD | guideline (ckd) |
| **saturated_fat_g** | 0.0 g | 18.0 g | HARD | guideline (ckd) |
| **sodium_mg** | 0.0 mg | 2000.0 mg | HARD | guideline (ckd) |
| **potassium_mg** | 2600.0 mg | No limit | SOFT | DRI fallback (ckd) |
| **calcium_mg** | 800.0 mg | 1000.0 mg | HARD | guideline (ckd) |
| **magnesium_mg** | 320.0 mg | No limit | SOFT | DRI fallback (ckd) |
| **phosphorus_mg** | 800.0 mg | 1000.0 mg | HARD | guideline (ckd) |

### COMBINED (ALL 5)
- **Target Energy**: 1621.8 kcal
| Nutrient | Min | Max | Hard/Soft | Source / Disease(s) |
| --- | --- | --- | --- | --- |
| **energy_kcal** | 1540.8 kcal | 2499.0 kcal | HARD | guideline (ckd, dm2, cholesterol, hypertension) |
| **carbohydrate_g** | 223.0 g | 223.0 g | HARD | guideline (cvd, ckd, dm2, cholesterol, hypertension) |
| **protein_g** | 40.8 g | 101.4 g | HARD | guideline (cvd, ckd, dm2, cholesterol, hypertension) |
| **fat_g** | 45.0 g | 48.7 g | HARD | guideline (cvd, ckd, dm2, cholesterol, hypertension) |
| **saturated_fat_g** | 0.0 g | 10.8 g | HARD | guideline (cvd, ckd, cholesterol, hypertension) |
| **trans_fat_g** | 0.0 g | 1.8 g | HARD | guideline (cvd, cholesterol) |
| **cholesterol_mg** | 0.0 mg | 150.0 mg | HARD | guideline (cvd, dm2, cholesterol, hypertension) |
| **sodium_mg** | 0.0 mg | 2000.0 mg | HARD | guideline (cvd, ckd, dm2, cholesterol, hypertension) |
| **potassium_mg** | 2600.0 mg | 4935.0 mg | HARD | guideline (dm2, hypertension) |
| **calcium_mg** | 950.0 mg | 1000.0 mg | HARD | guideline (ckd, dm2, hypertension) |
| **magnesium_mg** | 240.0 mg | 500.0 mg | HARD | guideline (hypertension) |
| **phosphorus_mg** | 800.0 mg | 1000.0 mg | HARD | guideline (ckd) |
| **fiber_g** | 30.0 g | 35.0 g | HARD | guideline (dm2, hypertension) |

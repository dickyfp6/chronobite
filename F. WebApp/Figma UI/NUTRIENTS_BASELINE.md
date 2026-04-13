# NutriPlan - 34 Nutrients Baseline

Sistem NutriPlan sudah menggunakan **34 nutrients standar** untuk analisis nutrisi lengkap.

## Daftar 34 Nutrients

### Top 3 Macronutrients
1. `carbohydrate_g` - Karbohidrat / Carbohydrates
2. `protein_g` - Protein / Protein
3. `fat_g` - Lemak / Fat

### Minerals (11)
- `calcium_mg` - Kalsium / Calcium
- `iron_mg` - Zat Besi / Iron
- `magnesium_mg` - Magnesium / Magnesium
- `phosphorus_mg` - Fosfor / Phosphorus
- `potassium_mg` - Kalium / Potassium
- `sodium_mg` - Natrium / Sodium
- `zinc_mg` - Seng / Zinc
- `copper_mg` - Tembaga / Copper
- `manganese_mg` - Mangan / Manganese
- `selenium_mg` - Selenium / Selenium
- `fluoride_mg` - Fluorida / Fluoride

### Vitamins (11)
- `vitamin_a_rae_mg` - Vitamin A
- `vitamin_b1_thiamin_mg` - Tiamin (B1) / Thiamin (B1)
- `vitamin_b2_riboflavin_mg` - Riboflavin (B2) / Riboflavin (B2)
- `vitamin_b3_niacin_mg` - Niasin (B3) / Niacin (B3)
- `vitamin_b5_pantothenic_acid_mg` - Asam Pantotenat (B5) / Pantothenic Acid (B5)
- `vitamin_b6_mg` - Vitamin B6
- `vitamin_b12_mg` - Vitamin B12
- `vitamin_c_mg` - Vitamin C
- `vitamin_d_mg` - Vitamin D
- `vitamin_e_mg` - Vitamin E
- `vitamin_k_mg` - Vitamin K

### Other Nutrients (9)
- `energy_kcal` - Energi / Energy
- `fiber_g` - Serat / Fiber
- `sugar_g` - Gula / Sugar
- `saturated_fat_g` - Lemak Jenuh / Saturated Fat
- `trans_fat_g` - Lemak Trans / Trans Fat
- `cholesterol_mg` - Kolesterol / Cholesterol
- `choline_mg` - Kolin / Choline
- `folate_mg` - Folat / Folate
- `water_g` - Air / Water

## Files Updated

### 1. `/src/app/utils/nutrientsList.ts`
- Master list semua 34 nutrients
- Helper functions: `getNutrientUnit()`, `getNutrientDisplayName()`
- Type-safe dengan TypeScript

### 2. `/src/app/utils/translations.ts`
- Translasi lengkap EN & ID untuk semua 34 nutrients
- Accessible via `t.nutrients[nutrientKey]`

### 3. `/src/app/utils/mockData.ts`
- `calculateDailyNeeds()` sekarang return semua 34 nutrients
- Recommended values berdasarkan age, gender, activity level
- Baseline untuk comparison

### 4. `/src/app/pages/Report.tsx`
- Tab "Other Nutrients" sekarang display semua 34 nutrients
- Grouped by category: Vitamins, Minerals, Others
- Show actual vs target dengan percentage

## Recommended Daily Intake Logic

Berdasarkan:
- **Gender**: Male/Female
- **Age**: Different requirements per age group
- **Weight**: Protein, water calculated per kg
- **Activity Level**: Affects calorie multiplier

### Example Calculations:
```typescript
// Protein: 1.2g per kg body weight
protein_g = weight * 1.2

// Water: 35ml per kg
water_g = weight * 35

// Calcium: Gender & age dependent
calcium_mg = gender === 'male' ? 1000 : (age > 50 ? 1200 : 1000)

// Iron: Gender & age dependent
iron_mg = gender === 'male' ? 8 : (age > 50 ? 8 : 18)
```

## Usage

```typescript
import { nutrientsList, getNutrientUnit } from './utils/nutrientsList';
import { calculateDailyNeeds } from './utils/mockData';
import { useI18n } from './contexts/I18nContext';

const { t } = useI18n();
const dailyNeeds = calculateDailyNeeds(weight, height, age, gender, activity);

// Access specific nutrient
const proteinTarget = dailyNeeds.protein_g;
const unit = getNutrientUnit('protein_g'); // "g"
const name = t.nutrients.protein_g; // "Protein" or "Protein"

// Iterate all nutrients
nutrientsList.forEach(nutrientKey => {
  const value = dailyNeeds[nutrientKey];
  const unit = getNutrientUnit(nutrientKey);
  const name = t.nutrients[nutrientKey];
  console.log(`${name}: ${value}${unit}`);
});
```

## Future Integration

Baseline ini siap untuk:
- ✅ API integration untuk meal database dengan 34 nutrients
- ✅ Algorithm optimization berdasarkan semua nutrients
- ✅ Detailed nutrition analysis per health condition
- ✅ Advanced reporting & visualization
- ✅ Export to PDF dengan complete nutrient breakdown

---

**Last Updated:** 2026-04-13  
**Total Nutrients:** 34

// Daftar lengkap 34 nutriens dalam urutan yang benar
// Carbohydrate, Protein, Fat di 3 teratas
import { t } from './translations';

export const nutrientsList = [
  'carbohydrate_g',
  'protein_g',
  'fat_g',
  'calcium_mg',
  'cholesterol_mg',
  'choline_mg',
  'copper_mg',
  'energy_kcal',
  'saturated_fat_g',
  'trans_fat_g',
  'fiber_g',
  'fluoride_mg',
  'folate_mg',
  'iron_mg',
  'magnesium_mg',
  'manganese_mg',
  'vitamin_b3_niacin_mg',
  'vitamin_b5_pantothenic_acid_mg',
  'phosphorus_mg',
  'potassium_mg',
  'vitamin_b2_riboflavin_mg',
  'selenium_mg',
  'sodium_mg',
  'sugar_g',
  'vitamin_b1_thiamin_mg',
  'vitamin_a_rae_mg',
  'vitamin_b12_mg',
  'vitamin_b6_mg',
  'vitamin_c_mg',
  'vitamin_d_mg',
  'vitamin_e_mg',
  'vitamin_k_mg',
  'water_g',
  'zinc_mg',
] as const;

export type NutrientKey = typeof nutrientsList[number];

// Helper function untuk get unit dari nutrient key
export function getNutrientUnit(nutrientKey: NutrientKey): string {
  if (nutrientKey.endsWith('_g')) return 'g';
  if (nutrientKey.endsWith('_mg')) return 'mg';
  if (nutrientKey === 'energy_kcal') return 'kcal';
  return '';
}

// Helper function untuk get nutrient display name
export function getNutrientDisplayName(nutrientKey: NutrientKey): string {
  return (t.nutrients as Record<string, string>)[nutrientKey] || nutrientKey;
}

export interface NutrientDisplay {
  val: number;
  formatted: string;
  unit: string;
}

export function formatNutrient(key: string, rawVal: number | null | undefined): NutrientDisplay {
  if (rawVal === null || rawVal === undefined) {
    return { val: 0, formatted: '0', unit: '' };
  }

  const keyLower = key.toLowerCase();
  let unit = '';
  let scaleFactor = 1;
  let decimals = 1;

  if (keyLower.endsWith('_g')) {
    unit = 'g';
    decimals = rawVal >= 100 ? 0 : 1;
  } else if (keyLower.endsWith('_mg')) {
    unit = 'mg';
    if (keyLower.includes('b12')) {
      unit = 'mcg';
      scaleFactor = 1000;
      decimals = 1;
    } else if (
      keyLower.includes('vitamin_a') ||
      keyLower.includes('folate') ||
      keyLower.includes('selenium') ||
      keyLower.includes('vitamin_k')
    ) {
      unit = 'mcg';
      scaleFactor = 1000;
      decimals = 0;
    } else if (keyLower.includes('vitamin_d')) {
      unit = 'mcg';
      scaleFactor = 1000;
      decimals = 0;
    } else {
      if (rawVal < 1) {
        decimals = 2;
      } else if (rawVal < 10) {
        decimals = 1;
      } else {
        decimals = 0;
      }
    }
  } else if (keyLower === 'energy_kcal') {
    unit = 'kcal';
    decimals = 0;
  }

  const val = rawVal * scaleFactor;
  const formatted = val.toFixed(decimals);
  
  return {
    val: Math.round(val * 100) / 100,
    formatted,
    unit
  };
}


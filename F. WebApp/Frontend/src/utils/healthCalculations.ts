
// Calculate recommended daily intake untuk semua 34 nutrients
export function calculateDailyNeeds(weight: number, height: number, age: number, gender: string, activity: string) {
  let bmr = 0;

  if (gender === 'male') {
    bmr = 10 * weight + 6.25 * height - 5 * age + 5;
  } else {
    bmr = 10 * weight + 6.25 * height - 5 * age - 161;
  }

  const activityMultiplier = activity === 'light' ? 1.375 : activity === 'moderate' ? 1.55 : 1.725;
  const calories = Math.round(bmr * activityMultiplier);
  const proteinG = Math.round(weight * 1.2);
  const carbsG = Math.round(calories * 0.5 / 4);
  const fatG = Math.round(calories * 0.25 / 9);

  // Return object dengan semua 34 nutrients + basic calculations
  return {
    // Legacy fields untuk backward compatibility
    calories,
    protein: proteinG,
    carbs: carbsG,
    fat: fatG,
    fiber: 25,

    // 34 Nutrients sesuai urutan (carbs, protein, fat di 3 teratas)
    carbohydrate_g: carbsG,
    protein_g: proteinG,
    fat_g: fatG,
    calcium_mg: gender === 'male' ? 1000 : age > 50 ? 1200 : 1000,
    cholesterol_mg: 300, // max recommended
    choline_mg: gender === 'male' ? 550 : 425,
    copper_mg: 0.9,
    energy_kcal: calories,
    saturated_fat_g: Math.round(fatG * 0.3), // max 30% of total fat
    trans_fat_g: 0, // avoid
    fiber_g: 25,
    fluoride_mg: gender === 'male' ? 4 : 3,
    folate_mg: 400,
    iron_mg: gender === 'male' ? 8 : age > 50 ? 8 : 18,
    magnesium_mg: gender === 'male' ? 400 : 310,
    manganese_mg: gender === 'male' ? 2.3 : 1.8,
    vitamin_b3_niacin_mg: gender === 'male' ? 16 : 14,
    vitamin_b5_pantothenic_acid_mg: 5,
    phosphorus_mg: 700,
    potassium_mg: 3500,
    vitamin_b2_riboflavin_mg: gender === 'male' ? 1.3 : 1.1,
    selenium_mg: 55,
    sodium_mg: 2300, // max recommended
    sugar_g: Math.round(calories * 0.1 / 4), // max 10% of calories
    vitamin_b1_thiamin_mg: gender === 'male' ? 1.2 : 1.1,
    vitamin_a_rae_mg: gender === 'male' ? 900 : 700,
    vitamin_b12_mg: 2.4,
    vitamin_b6_mg: age > 50 ? 1.7 : 1.3,
    vitamin_c_mg: gender === 'male' ? 90 : 75,
    vitamin_d_mg: age > 70 ? 20 : 15,
    vitamin_e_mg: 15,
    vitamin_k_mg: gender === 'male' ? 120 : 90,
    water_g: gender === 'male' ? (age > 18 ? 3700 : 3300) : (age > 18 ? 2700 : 2300),
    zinc_mg: gender === 'male' ? 11 : 8,
  };
}

import { nutrientsList, type NutrientKey } from './nutrientsList';

export const mealDatabase = {
  breakfast: {
    mainCourse: [
      { id: 'b1', name: 'Oatmeal with Berries', calories: 250, protein: 8, carbs: 45, fat: 5 },
      { id: 'b2', name: 'Scrambled Eggs', calories: 180, protein: 13, carbs: 2, fat: 13 },
      { id: 'b3', name: 'Whole Grain Toast', calories: 150, protein: 6, carbs: 28, fat: 2 },
      { id: 'b4', name: 'Greek Yogurt Bowl', calories: 200, protein: 15, carbs: 20, fat: 6 },
      { id: 'b5', name: 'Avocado Toast', calories: 220, protein: 7, carbs: 25, fat: 12 },
    ],
    sideDish: [
      { id: 'bs1', name: 'Fresh Fruit Salad', calories: 80, protein: 1, carbs: 20, fat: 0 },
      { id: 'bs2', name: 'Almonds (handful)', calories: 100, protein: 4, carbs: 4, fat: 9 },
      { id: 'bs3', name: 'Cottage Cheese', calories: 90, protein: 12, carbs: 5, fat: 2 },
    ],
    drink: [
      { id: 'bd1', name: 'Green Tea', calories: 0, protein: 0, carbs: 0, fat: 0 },
      { id: 'bd2', name: 'Black Coffee', calories: 5, protein: 0, carbs: 1, fat: 0 },
      { id: 'bd3', name: 'Almond Milk', calories: 30, protein: 1, carbs: 1, fat: 2.5 },
    ],
  },
  lunch: {
    mainCourse: [
      { id: 'l1', name: 'Grilled Chicken Breast', calories: 280, protein: 42, carbs: 0, fat: 12 },
      { id: 'l2', name: 'Baked Salmon', calories: 320, protein: 35, carbs: 0, fat: 20 },
      { id: 'l3', name: 'Quinoa Bowl', calories: 240, protein: 9, carbs: 42, fat: 4 },
      { id: 'l4', name: 'Turkey Wrap', calories: 300, protein: 25, carbs: 35, fat: 8 },
      { id: 'l5', name: 'Tofu Stir-fry', calories: 220, protein: 18, carbs: 15, fat: 12 },
    ],
    sideDish: [
      { id: 'ls1', name: 'Steamed Broccoli', calories: 50, protein: 4, carbs: 10, fat: 0 },
      { id: 'ls2', name: 'Mixed Greens Salad', calories: 40, protein: 2, carbs: 8, fat: 0 },
      { id: 'ls3', name: 'Brown Rice', calories: 110, protein: 3, carbs: 23, fat: 1 },
      { id: 'ls4', name: 'Sweet Potato', calories: 130, protein: 2, carbs: 30, fat: 0 },
    ],
    drink: [
      { id: 'ld1', name: 'Water', calories: 0, protein: 0, carbs: 0, fat: 0 },
      { id: 'ld2', name: 'Sparkling Water', calories: 0, protein: 0, carbs: 0, fat: 0 },
      { id: 'ld3', name: 'Herbal Tea', calories: 0, protein: 0, carbs: 0, fat: 0 },
    ],
  },
  dinner: {
    mainCourse: [
      { id: 'd1', name: 'Grilled Fish', calories: 250, protein: 38, carbs: 0, fat: 10 },
      { id: 'd2', name: 'Lean Beef Steak', calories: 310, protein: 40, carbs: 0, fat: 16 },
      { id: 'd3', name: 'Chicken Vegetable Soup', calories: 180, protein: 20, carbs: 15, fat: 5 },
      { id: 'd4', name: 'Lentil Curry', calories: 260, protein: 16, carbs: 40, fat: 4 },
      { id: 'd5', name: 'Shrimp Pasta', calories: 340, protein: 28, carbs: 45, fat: 8 },
    ],
    sideDish: [
      { id: 'ds1', name: 'Roasted Vegetables', calories: 80, protein: 3, carbs: 15, fat: 2 },
      { id: 'ds2', name: 'Cauliflower Rice', calories: 30, protein: 2, carbs: 6, fat: 0 },
      { id: 'ds3', name: 'Green Beans', calories: 40, protein: 2, carbs: 8, fat: 0 },
    ],
    drink: [
      { id: 'dd1', name: 'Water', calories: 0, protein: 0, carbs: 0, fat: 0 },
      { id: 'dd2', name: 'Chamomile Tea', calories: 0, protein: 0, carbs: 0, fat: 0 },
      { id: 'dd3', name: 'Vegetable Broth', calories: 15, protein: 1, carbs: 3, fat: 0 },
    ],
  },
  snack: [
    { id: 's1', name: 'Apple Slices', calories: 95, protein: 0, carbs: 25, fat: 0 },
    { id: 's2', name: 'Carrot Sticks', calories: 50, protein: 1, carbs: 12, fat: 0 },
    { id: 's3', name: 'Rice Cake', calories: 35, protein: 1, carbs: 7, fat: 0 },
    { id: 's4', name: 'Dark Chocolate (1 sq)', calories: 70, protein: 1, carbs: 8, fat: 4 },
    { id: 's5', name: 'Walnuts (handful)', calories: 120, protein: 3, carbs: 4, fat: 12 },
  ],
};

export function generateRandomMealOptions(meal: string, category: string, count: number = 3) {
  const pool = meal === 'snack'
    ? mealDatabase.snack
    : mealDatabase[meal as keyof typeof mealDatabase][category as keyof typeof mealDatabase.breakfast];

  const shuffled = [...pool].sort(() => Math.random() - 0.5);
  return shuffled.slice(0, Math.min(count, pool.length));
}

export function calculateNutrition(selectedMeals: any) {
  let total = { calories: 0, protein: 0, carbs: 0, fat: 0 };

  Object.values(selectedMeals).forEach((meal: any) => {
    if (meal) {
      total.calories += meal.calories || 0;
      total.protein += meal.protein || 0;
      total.carbs += meal.carbs || 0;
      total.fat += meal.fat || 0;
    }
  });

  return total;
}

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
    water_g: Math.round(weight * 35), // 35ml per kg
    zinc_mg: gender === 'male' ? 11 : 8,
  };
}

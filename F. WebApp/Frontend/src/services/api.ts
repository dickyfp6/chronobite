// API Service Layer
// Handles all backend communication

interface FormData {
  gender: string;
  age: number;
  weight: number;
  height: number;
  activity: string;
  diseases: string[];
  food_preferences: string[];
  algorithm: string;
}

interface AnalysisResult {
  success: boolean;
  energy: {
    bmi: number;
    bbr: number;
    bmr: number;
    tdee: number;
  };
  guidelines: Record<string, any>;
  [key: string]: any;
}

interface MenuRequest {
  algorithm: string;
  user_profile: FormData;
  analysis_data: AnalysisResult;
  user_input: AnalysisResult;
}

interface MenuResult {
  success: boolean;
  menu_plan: any;
  [key: string]: any;
}

type RawAnalysisResult = Record<string, any>;

const toNumber = (value: unknown): number | undefined => {
  if (typeof value === 'number' && Number.isFinite(value)) {
    return value;
  }
  if (typeof value === 'string') {
    const parsed = Number(value);
    if (Number.isFinite(parsed)) {
      return parsed;
    }
  }
  return undefined;
};

const pickNumber = (...values: unknown[]): number => {
  for (const value of values) {
    const num = toNumber(value);
    if (num !== undefined) {
      return num;
    }
  }
  return 0;
};

const normalizeAnalysisResult = (raw: RawAnalysisResult): AnalysisResult => {
  const energy = raw.energy && typeof raw.energy === 'object' ? raw.energy : {};
  const anthropometrics =
    raw.anthropometrics && typeof raw.anthropometrics === 'object' ? raw.anthropometrics : {};

  const normalizedEnergy = {
    ...energy,
    bmi: pickNumber(energy.bmi, anthropometrics.bmi, raw.bmi),
    bbr: pickNumber(energy.bbr, energy.bbi, anthropometrics.bbr, anthropometrics.bbi, raw.bbr, raw.bbi),
    bmr: pickNumber(energy.bmr, raw.bmr),
    tdee: pickNumber(energy.tdee, raw.tdee),
  };

  return {
    ...raw,
    success: raw.success ?? true,
    energy: normalizedEnergy,
    guidelines: raw.guidelines ?? raw.macros ?? {},
  } as AnalysisResult;
};

const normalizeMenuResult = (raw: Record<string, any>): MenuResult => {
  const rawMenu = raw.menu_plan && typeof raw.menu_plan === 'object' ? raw.menu_plan : {};
  const mealOrder = ['breakfast', 'lunch', 'dinner', 'snack'];

  const rawMeals = rawMenu.meals && typeof rawMenu.meals === 'object' ? rawMenu.meals : {};

  const meals = mealOrder.reduce<Record<string, any>>((acc, mealName) => {
    const sourceMeal = rawMeals[mealName] ?? rawMenu[mealName];
    if (!sourceMeal || typeof sourceMeal !== 'object') {
      return acc;
    }

    const sourceMacros =
      sourceMeal.macros && typeof sourceMeal.macros === 'object' ? sourceMeal.macros : {};

    const items = Array.isArray(sourceMeal.items)
      ? sourceMeal.items.map((item: Record<string, any>) => {
          const itemMacros = item?.macros && typeof item.macros === 'object' ? item.macros : {};
          return {
            ...item,
            name: item?.name ?? item?.food_name ?? 'Unknown',
            weight: pickNumber(item?.weight, item?.serving_size, item?.portion_gram),
            calories: pickNumber(item?.calories, item?.energy_kcal),
            protein: pickNumber(item?.protein, item?.protein_g, itemMacros?.protein),
            carbs: pickNumber(item?.carbs, item?.carbohydrate_g, itemMacros?.carbs),
            fat: pickNumber(item?.fat, item?.fat_g, itemMacros?.fat),
            fiber: pickNumber(item?.fiber, item?.fiber_g),
          };
        })
      : [];

    acc[mealName] = {
      ...sourceMeal,
      meal_name: sourceMeal.meal_name ?? mealName,
      recommended_calories: pickNumber(
        sourceMeal.recommended_calories,
        sourceMeal.target_calories,
        sourceMeal.total_calories,
        sourceMeal.calories
      ),
      calories: pickNumber(sourceMeal.calories, sourceMeal.total_calories),
      protein: pickNumber(sourceMeal.protein, sourceMeal.total_protein, sourceMacros.protein),
      carbs: pickNumber(sourceMeal.carbs, sourceMeal.total_carbs, sourceMacros.carbs),
      fat: pickNumber(sourceMeal.fat, sourceMeal.total_fat, sourceMacros.fat),
      items,
    };

    return acc;
  }, {});

  const mealList = Object.values(meals) as Array<Record<string, any>>;
  const sumCalories = mealList.reduce((sum, meal) => sum + pickNumber(meal.calories), 0);
  const sumProtein = mealList.reduce((sum, meal) => sum + pickNumber(meal.protein), 0);
  const sumCarbs = mealList.reduce((sum, meal) => sum + pickNumber(meal.carbs), 0);
  const sumFat = mealList.reduce((sum, meal) => sum + pickNumber(meal.fat), 0);

  return {
    ...raw,
    success: raw.success ?? true,
    menu_plan: {
      ...rawMenu,
      meals,
      total_calories: pickNumber(rawMenu.total_calories, sumCalories),
      total_protein: pickNumber(rawMenu.total_protein, rawMenu?.macros?.protein, sumProtein),
      total_carbs: pickNumber(rawMenu.total_carbs, rawMenu?.macros?.carbs, sumCarbs),
      total_fat: pickNumber(rawMenu.total_fat, rawMenu?.macros?.fat, sumFat),
    },
  };
};

// Determine API base URL based on environment
const getAPIBase = (): string => import.meta.env.VITE_API_URL || '';

const getApiUrl = (path: string): string => {
  const base = getAPIBase().replace(/\/$/, '');
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;

  if (!base) {
    return normalizedPath;
  }

  if (base.endsWith('/api') && normalizedPath.startsWith('/api/')) {
    return `${base}${normalizedPath.slice(4)}`;
  }

  return `${base}${normalizedPath}`;
};

export const api = {
  async analyzeProfile(formData: FormData): Promise<AnalysisResult> {
    const response = await fetch(getApiUrl('/api/analyze'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData),
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const rawResult = (await response.json()) as RawAnalysisResult;
    return normalizeAnalysisResult(rawResult);
  },

  async pollMenuJob(jobId: string): Promise<MenuResult> {
    const maxAttempts = 60; // 60 × 3s = 3 minutes max
    
    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      await new Promise(r => setTimeout(r, 3000)); // wait 3s
      
      const response = await fetch(getApiUrl(`/api/job-status/${jobId}`), {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      if (data.status === 'done') {
        return normalizeMenuResult(data);
      } else if (data.status === 'error') {
        throw new Error(data.error || 'Menu generation failed');
      }
      // if 'running', continue polling
    }
    
    throw new Error('Menu generation timed out after 3 minutes');
  },

  async generateMenu(menuRequest: MenuRequest): Promise<MenuResult> {
    const response = await fetch(getApiUrl('/api/generate-menu'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(menuRequest),
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const rawResult = (await response.json()) as Record<string, any>;
    
    // If backend returned job_id (async mode for genetic algorithm)
    if (rawResult.job_id) {
      return await api.pollMenuJob(rawResult.job_id);
    }
    
    // Otherwise synchronous response (greedy)
    return normalizeMenuResult(rawResult);
  },
};

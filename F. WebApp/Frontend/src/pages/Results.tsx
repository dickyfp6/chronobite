import { useState, useEffect, useMemo } from 'react';
import { ArrowRight, RotateCcw } from 'lucide-react';
import { useI18n } from '../contexts/I18nContext';
import type { UserInputData } from './InputWizard';
import { api } from '../services/api';
import { motion, AnimatePresence } from 'motion/react';

const loadingSteps = [
  "Analyzing physical profile & energy needs...",
  "Evaluating medical constraints & health history...",
  "Filtering nutritional food database...",
  "Formulating optimal daily meal combinations...",
  "Balancing macro & micro nutrient distributions...",
  "Finalizing customized recommendations for you..."
];

interface ResultsProps {
  userData: UserInputData;
  algorithm?: 'greedy' | 'genetic';
  analysisResult?: any;
  menuPromise?: Promise<any> | null;
  onViewReport: () => void;
  selectedItems: Record<string, Candidate>;
  onSelectedItemsChange: (items: Record<string, Candidate>) => void;
}

type Candidate = {
  fdc_id: string;
  name: string;
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
  serving_size: number;
  is_selected: boolean;
  cuisine_label?: string;
};

type Course = {
  course_type: string;
  candidates: Candidate[];
};

type Meal = {
  meal_type: string;
  target_calories: number;
  actual_calories: number;
  courses?: Record<string, Course>;
  candidates?: Candidate[];
};

const getRibbonColor = (cuisine?: string) => {
  const c = cuisine?.toLowerCase() || '';
  if (c.includes('asian')) return 'bg-red-500';
  if (c.includes('western')) return 'bg-blue-500';
  if (c.includes('mediteranian') || c.includes('mediterranean')) return 'bg-purple-500';
  return 'bg-green-500'; // Generic
};

const mealThemes: Record<string, {
  color: string;
  glowClass: string;
  glowClass2: string;
  containerBg: string;
  containerBorder: string;
  icon: React.ReactNode;
  badgeBg: string;
  badgeText: string;
  borderColor: string;
  selectedClass: string;
  unselectedClass: string;
}> = {
  breakfast: {
    color: "amber",
    glowClass: "absolute -top-16 -right-16 w-64 h-64 bg-gradient-to-br from-amber-450/40 via-orange-450/20 to-transparent rounded-full blur-3xl pointer-events-none",
    glowClass2: "absolute -bottom-20 -left-20 w-64 h-64 bg-gradient-to-tr from-orange-450/20 via-amber-400/10 to-transparent rounded-full blur-3xl pointer-events-none",
    containerBg: "bg-gradient-to-br from-amber-100/35 via-amber-50/15 to-orange-100/25 dark:from-amber-950/20 dark:via-slate-900/70 dark:to-orange-950/15",
    containerBorder: "border border-amber-200/60 dark:border-amber-900/40 shadow-sm",
    icon: (
      <svg className="w-8 h-8 text-amber-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364-6.364l-.707.707M6.343 17.657l-.707.707m0-12.728l.707.707m12.728 12.728l.707-.707M12 8a4 4 0 100 8 4 4 0 000-8z" />
      </svg>
    ),
    badgeBg: "bg-amber-100/90 dark:bg-amber-950/50 border border-amber-200/30",
    badgeText: "text-amber-800 dark:text-amber-300",
    borderColor: "hover:border-amber-450/50 dark:hover:border-amber-500/50",
    selectedClass: "border-2 border-amber-450 dark:border-amber-400 bg-gradient-to-br from-amber-200 via-amber-100 to-orange-100 dark:from-amber-950/70 dark:via-slate-900/80 dark:to-orange-950/60 shadow-[0_10px_25px_rgba(0,0,0,0.1)] dark:shadow-[0_10px_30px_rgba(0,0,0,0.4)] backdrop-blur-md scale-[1.02] transition-all duration-300",
    unselectedClass: "border border-white/50 dark:border-white/10 bg-white/45 dark:bg-slate-950/20 shadow-[0_4px_15px_rgba(0,0,0,0.03)] dark:shadow-[0_4px_25px_rgba(0,0,0,0.12)] hover:bg-white/70 dark:hover:bg-slate-900/40 hover:border-amber-300/50 dark:hover:border-amber-500/30 hover:shadow-[0_8px_20px_rgba(0,0,0,0.06)] dark:hover:shadow-[0_8px_20px_rgba(0,0,0,0.25)] hover:-translate-y-0.5 backdrop-blur-md transition-all duration-300"
  },
  lunch: {
    color: "sky",
    glowClass: "absolute -top-16 -right-16 w-64 h-64 bg-gradient-to-br from-sky-400/40 via-yellow-450/20 to-transparent rounded-full blur-3xl pointer-events-none",
    glowClass2: "absolute -bottom-20 -left-20 w-64 h-64 bg-gradient-to-tr from-yellow-300/45 via-sky-300/10 to-transparent rounded-full blur-3xl pointer-events-none",
    containerBg: "bg-gradient-to-br from-sky-100/30 via-sky-50/15 to-yellow-100/35 dark:from-sky-950/20 dark:via-slate-900/70 dark:to-yellow-950/25",
    containerBorder: "border border-sky-200/60 dark:border-sky-900/40 shadow-sm",
    icon: (
      <svg className="w-8 h-8 text-sky-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v2m0 14v2m9-9h-2M5 12H3m14.071-7.071l-1.414 1.414M8.343 15.657l-1.414 1.414m0-11.314l1.414 1.414m8.485 8.485l1.414-1.414M12 7a5 5 0 100 10 5 5 0 000-10z" />
      </svg>
    ),
    badgeBg: "bg-sky-100/90 dark:bg-sky-950/50 border border-sky-200/30",
    badgeText: "text-sky-800 dark:text-sky-300",
    borderColor: "hover:border-sky-450/50 dark:hover:border-sky-500/50",
    selectedClass: "border-2 border-sky-450 dark:border-sky-400 bg-gradient-to-br from-sky-200 to-yellow-200 dark:from-sky-900/60 dark:to-yellow-950/60 shadow-[0_10px_25px_rgba(0,0,0,0.1)] dark:shadow-[0_10px_30px_rgba(0,0,0,0.4)] backdrop-blur-md scale-[1.02] transition-all duration-300",
    unselectedClass: "border border-white/50 dark:border-white/10 bg-white/45 dark:bg-slate-950/20 shadow-[0_4px_15px_rgba(0,0,0,0.03)] dark:shadow-[0_4px_25px_rgba(0,0,0,0.12)] hover:bg-white/70 dark:hover:bg-slate-900/40 hover:border-sky-300/50 dark:hover:border-sky-500/30 hover:shadow-[0_8px_20px_rgba(0,0,0,0.06)] dark:hover:shadow-[0_8px_20px_rgba(0,0,0,0.25)] hover:-translate-y-0.5 backdrop-blur-md transition-all duration-300"
  },
  dinner: {
    color: "indigo",
    glowClass: "absolute -top-16 -right-16 w-64 h-64 bg-gradient-to-br from-indigo-500/40 via-purple-450/20 to-transparent rounded-full blur-3xl pointer-events-none",
    glowClass2: "absolute -bottom-20 -left-20 w-64 h-64 bg-gradient-to-tr from-purple-500/20 via-indigo-500/10 to-transparent rounded-full blur-3xl pointer-events-none",
    containerBg: "bg-gradient-to-br from-indigo-100/35 via-indigo-50/15 to-purple-100/30 dark:from-indigo-950/20 dark:via-slate-900/70 dark:to-purple-950/15",
    containerBorder: "border border-indigo-200/60 dark:border-indigo-900/40 shadow-sm",
    icon: (
      <svg className="w-8 h-8 text-indigo-500 dark:text-indigo-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
      </svg>
    ),
    badgeBg: "bg-indigo-100/90 dark:bg-indigo-950/50 border border-indigo-200/30",
    badgeText: "text-indigo-800 dark:text-indigo-300",
    borderColor: "hover:border-indigo-450/50 dark:hover:border-indigo-500/50",
    selectedClass: "border-2 border-indigo-450 dark:border-indigo-400 bg-gradient-to-br from-indigo-200 to-blue-900/30 dark:from-indigo-950/70 dark:to-blue-950/90 shadow-[0_10px_25px_rgba(0,0,0,0.1)] dark:shadow-[0_10px_30px_rgba(0,0,0,0.4)] backdrop-blur-md scale-[1.02] transition-all duration-300",
    unselectedClass: "border border-white/50 dark:border-white/10 bg-white/45 dark:bg-slate-950/20 shadow-[0_4px_15px_rgba(0,0,0,0.03)] dark:shadow-[0_4px_25px_rgba(0,0,0,0.12)] hover:bg-white/70 dark:hover:bg-slate-900/40 hover:border-indigo-300/50 dark:hover:border-indigo-500/30 hover:shadow-[0_8px_20px_rgba(0,0,0,0.06)] dark:hover:shadow-[0_8px_20px_rgba(0,0,0,0.25)] hover:-translate-y-0.5 backdrop-blur-md transition-all duration-300"
  },
  snack: {
    color: "rose",
    glowClass: "absolute -top-16 -right-16 w-64 h-64 bg-gradient-to-br from-rose-500/40 via-pink-450/20 to-transparent rounded-full blur-3xl pointer-events-none",
    glowClass2: "absolute -bottom-20 -left-20 w-64 h-64 bg-gradient-to-tr from-pink-500/20 via-rose-500/10 to-transparent rounded-full blur-3xl pointer-events-none",
    containerBg: "bg-gradient-to-br from-rose-100/35 via-rose-50/15 to-pink-100/30 dark:from-rose-950/20 dark:via-slate-900/70 dark:to-pink-950/15",
    containerBorder: "border border-rose-200/60 dark:border-rose-900/40 shadow-sm",
    icon: (
      <svg className="w-8 h-8 text-rose-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
      </svg>
    ),
    badgeBg: "bg-rose-100/90 dark:bg-rose-950/50 border border-rose-200/30",
    badgeText: "text-rose-800 dark:text-rose-300",
    borderColor: "hover:border-rose-450/50 dark:hover:border-rose-500/50",
    selectedClass: "border-2 border-rose-450 dark:border-rose-400 bg-gradient-to-br from-rose-200 via-rose-100 to-pink-100 dark:from-rose-950/70 dark:via-slate-900/80 dark:to-pink-950/50 shadow-[0_10px_25px_rgba(0,0,0,0.1)] dark:shadow-[0_10px_30px_rgba(0,0,0,0.4)] backdrop-blur-md scale-[1.02] transition-all duration-300",
    unselectedClass: "border border-white/50 dark:border-white/10 bg-white/45 dark:bg-slate-950/20 shadow-[0_4px_15px_rgba(0,0,0,0.03)] dark:shadow-[0_4px_25px_rgba(0,0,0,0.12)] hover:bg-white/70 dark:hover:bg-slate-900/40 hover:border-rose-300/50 dark:hover:border-rose-500/30 hover:shadow-[0_8px_20px_rgba(0,0,0,0.06)] dark:hover:shadow-[0_8px_20px_rgba(0,0,0,0.25)] hover:-translate-y-0.5 backdrop-blur-md transition-all duration-300"
  }
};

const timeLabels: Record<string, string> = {
  breakfast: 'Suggested Time: 07:00 - 09:00',
  lunch: 'Suggested Time: 12:00 - 14:00',
  dinner: 'Suggested Time: 18:00 - 19:00',
  snack: 'Suggested Time: 15:00 - 16:00',
};

export function Results({ userData, algorithm, analysisResult, menuPromise, onViewReport, selectedItems, onSelectedItemsChange }: ResultsProps) {
  const { t } = useI18n();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [menuData, setMenuData] = useState<Record<string, Meal> | null>(null);
  const [statusIndex, setStatusIndex] = useState(0);

  // Rotate status message every 2 seconds
  useEffect(() => {
    if (!loading) return;
    const interval = setInterval(() => {
      setStatusIndex((prev) => (prev + 1) % loadingSteps.length);
    }, 2000);
    return () => clearInterval(interval);
  }, [loading]);

  // Helper function to scale alternative candidates (option 2 & 3) to match option 1's calorie target
  const scaleCandidates = (candidates: Candidate[]): Candidate[] => {
    if (!candidates || candidates.length === 0) return candidates;
    if (candidates.length === 1) return candidates;

    const targetCalories = candidates[0].calories;
    const scaled = [candidates[0]]; // Keep option 1 as-is

    // Scale options 2 and 3
    for (let i = 1; i < Math.min(candidates.length, 3); i++) {
      const candidate = candidates[i];
      if (candidate.calories > 0) {
        // Scale based on actual candidate serving size and calories
        const rawScaleFactor = targetCalories / candidate.calories;
        const rawServingSize = (candidate.serving_size || 100) * rawScaleFactor;
        
        // Round portion size to the nearest whole integer gram
        const roundedServingSize = Math.round(rawServingSize);
        
        // Compute actual scale factor from the rounded portion
        const actualScaleFactor = roundedServingSize / (candidate.serving_size || 100);
        
        scaled.push({
          ...candidate,
          serving_size: roundedServingSize,
          calories: Math.round(candidate.calories * actualScaleFactor * 10) / 10,
          protein: Math.round(candidate.protein * actualScaleFactor * 100) / 100,
          carbs: Math.round(candidate.carbs * actualScaleFactor * 100) / 100,
          fat: Math.round(candidate.fat * actualScaleFactor * 100) / 100,
        });
      } else {
        scaled.push(candidate); // Keep as-is if calories is 0
      }
    }

    return scaled;
  };

  const fetchMenu = async () => {
    setLoading(true);
    setError(null);
    try {
      let result;
      if (menuPromise) {
        result = await menuPromise;
      } else {
        const payload = {
          gender: userData.gender === 'male' ? 'M' : 'F',
          age: userData.age,
          weight: userData.weight,
          height: userData.height,
          activity: userData.activity || '1.845',
          diseases: userData.healthConditions.length > 0 ? userData.healthConditions : ['normal'],
          food_preferences: userData.foodPreferences,
          algorithm: algorithm || 'greedy',
        };

        result = await api.generateMenu({
          algorithm: algorithm || 'greedy',
          user_profile: payload,
          analysis_data: analysisResult || {},
          user_input: analysisResult || {},
        });
      }

      if (!result.success || !result.menu_plan?.meals) {
        throw new Error('Failed to generate valid menu plan from backend');
      }

      const meals = result.menu_plan.meals;
      const formattedMenu = {
        breakfast: meals.breakfast,
        lunch: meals.lunch,
        dinner: meals.dinner,
        snack: meals.snack,
      };

      // Apply scaling to alternative candidates (option 2 & 3)
      ['breakfast', 'lunch', 'dinner'].forEach((mealName) => {
        const meal = formattedMenu[mealName as keyof typeof formattedMenu];
        if (meal?.courses) {
          ['Main', 'Side', 'Drink'].forEach((courseName) => {
            const course = meal.courses![courseName];
            if (course?.candidates) {
              course.candidates = scaleCandidates(course.candidates);
            }
          });
        }
      });

      // Scale snack candidates
      if (formattedMenu.snack?.candidates) {
        formattedMenu.snack.candidates = scaleCandidates(formattedMenu.snack.candidates);
      }
      
      setMenuData(formattedMenu);
      sessionStorage.setItem('dss_menu_data', JSON.stringify(formattedMenu));
      
      // Store actual nutrients directly from the backend payload!
      if (result.menu_plan.total_daily_calories) {
        const actualNutrients = {
          calories: result.menu_plan.total_daily_calories,
          protein: result.menu_plan.total_daily_protein_g,
          carbs: result.menu_plan.total_daily_carb_g,
          fat: result.menu_plan.total_daily_fat_g,
          ...result.menu_plan.daily_micronutrients // include micronutrients!
        };
        sessionStorage.setItem('dss_actual_nutrients', JSON.stringify(actualNutrients));
      }

      // Store the analysis guidelines for the dynamic report
      if (analysisResult?.guidelines) {
        sessionStorage.setItem('dss_analysis_guidelines', JSON.stringify(analysisResult.guidelines));
      }

      // Initialize selected items (the first candidate for each course)
      const initialSelected: Record<string, Candidate> = {};

      ['breakfast', 'lunch', 'dinner'].forEach((mealName) => {
        const meal = formattedMenu[mealName as keyof typeof formattedMenu];
        if (meal?.courses) {
          ['Main', 'Side', 'Drink'].forEach((courseName) => {
            const course = meal.courses[courseName];
            if (course?.candidates?.length > 0) {
              initialSelected[`${mealName}_${courseName}`] = course.candidates[0];
            }
          });
        }
      });

      // Initialize snack
      if (meals.snack?.candidates?.length > 0) {
        initialSelected['snack_snack'] = meals.snack.candidates[0];
      }

      onSelectedItemsChange(initialSelected);
      sessionStorage.setItem('dss_selected_items', JSON.stringify(initialSelected));
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'An error occurred while generating the menu plan.');
    } finally {
      setLoading(false);
    }
  };

  const handleRegenerate = async () => {
    setLoading(true);
    setError(null);
    try {
      const payload = {
        gender: userData.gender === 'male' ? 'M' : 'F',
        age: userData.age,
        weight: userData.weight,
        height: userData.height,
        activity: userData.activity || '1.845',
        diseases: userData.healthConditions.length > 0 ? userData.healthConditions : ['normal'],
        food_preferences: userData.foodPreferences,
        algorithm: algorithm || 'greedy',
      };

      const result = await api.generateMenu({
        algorithm: algorithm || 'greedy',
        user_profile: payload,
        analysis_data: analysisResult || {},
        user_input: analysisResult || {},
      });

      if (!result.success || !result.menu_plan?.meals) {
        throw new Error('Failed to generate valid menu plan from backend');
      }

      const meals = result.menu_plan.meals;
      const formattedMenu = {
        breakfast: meals.breakfast,
        lunch: meals.lunch,
        dinner: meals.dinner,
        snack: meals.snack,
      };

      // Apply scaling to alternative candidates (option 2 & 3)
      ['breakfast', 'lunch', 'dinner'].forEach((mealName) => {
        const meal = formattedMenu[mealName as keyof typeof formattedMenu];
        if (meal?.courses) {
          ['Main', 'Side', 'Drink'].forEach((courseName) => {
            const course = meal.courses![courseName];
            if (course?.candidates) {
              course.candidates = scaleCandidates(course.candidates);
            }
          });
        }
      });

      // Scale snack candidates
      if (formattedMenu.snack?.candidates) {
        formattedMenu.snack.candidates = scaleCandidates(formattedMenu.snack.candidates);
      }
      
      setMenuData(formattedMenu);
      sessionStorage.setItem('dss_menu_data', JSON.stringify(formattedMenu));
      
      // Store actual nutrients directly from the backend payload!
      if (result.menu_plan.total_daily_calories) {
        const actualNutrients = {
          calories: result.menu_plan.total_daily_calories,
          protein: result.menu_plan.total_daily_protein_g,
          carbs: result.menu_plan.total_daily_carb_g,
          fat: result.menu_plan.total_daily_fat_g,
          ...result.menu_plan.daily_micronutrients // include micronutrients!
        };
        sessionStorage.setItem('dss_actual_nutrients', JSON.stringify(actualNutrients));
      }

      // Initialize selected items (the first candidate for each course)
      const initialSelected: Record<string, Candidate> = {};

      ['breakfast', 'lunch', 'dinner'].forEach((mealName) => {
        const meal = formattedMenu[mealName as keyof typeof formattedMenu];
        if (meal?.courses) {
          ['Main', 'Side', 'Drink'].forEach((courseName) => {
            const course = meal.courses[courseName];
            if (course?.candidates?.length > 0) {
              initialSelected[`${mealName}_${courseName}`] = course.candidates[0];
            }
          });
        }
      });

      if (meals.snack?.candidates?.length > 0) {
        initialSelected['snack_snack'] = meals.snack.candidates[0];
      }

      onSelectedItemsChange(initialSelected);
      sessionStorage.setItem('dss_selected_items', JSON.stringify(initialSelected));
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'An error occurred while generating the menu plan.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMenu();
  }, []);

  const handleSelect = (meal: string, category: string, candidate: Candidate) => {
    const key = `${meal}_${category}`;
    const newSelected = {
      ...selectedItems,
      [key]: candidate,
    };
    // Let the useEffect handle propagating the changes
    onSelectedItemsChange(newSelected);
  };

  // Dynamically rebalance portions of Main Course and Side Dish if Drink is Mineral Water
  const rebalancedSelectedItems = useMemo(() => {
    const rebalanced = { ...selectedItems };
    if (!menuData) return rebalanced;

    ['breakfast', 'lunch', 'dinner'].forEach((mealName) => {
      const mainKey = `${mealName}_Main`;
      const sideKey = `${mealName}_Side`;
      const drinkKey = `${mealName}_Drink`;

      const main = selectedItems[mainKey];
      const side = selectedItems[sideKey];
      const drink = selectedItems[drinkKey];

      if (!main || !side || !drink) return;

      // Check if the selected drink is Mineral Water (0 kcal)
      if (drink.name === 'Mineral Water') {
        const mealTarget = menuData[mealName as keyof typeof menuData]?.target_calories || 0;
        
        // Find default candidate values from the original menuData
        const defaultMain = menuData[mealName as keyof typeof menuData]?.courses?.Main?.candidates?.find((c: any) => c.name === main.name) || main;
        const defaultSide = menuData[mealName as keyof typeof menuData]?.courses?.Side?.candidates?.find((c: any) => c.name === side.name) || side;

        const currentCalories = defaultMain.calories + defaultSide.calories;
        const deficit = mealTarget - currentCalories;

        if (deficit > 0) {
          // Distribute deficit: 65% to Main, 35% to Side
          const mainDeficitShare = deficit * 0.65;
          const sideDeficitShare = deficit * 0.35;

          // Scale Main Course
          if (defaultMain.calories > 0) {
            const mainKcalPerGram = defaultMain.calories / defaultMain.serving_size;
            let newMainPortion = defaultMain.serving_size + (mainDeficitShare / mainKcalPerGram);
            newMainPortion = Math.min(newMainPortion, 400); // Clamp to max portion limit (400g)
            
            const scale = newMainPortion / defaultMain.serving_size;
            rebalanced[mainKey] = {
              ...defaultMain,
              serving_size: Math.round(newMainPortion),
              calories: Math.round(defaultMain.calories * scale * 10) / 10,
              protein: Math.round(defaultMain.protein * scale * 100) / 100,
              carbs: Math.round(defaultMain.carbs * scale * 100) / 100,
              fat: Math.round(defaultMain.fat * scale * 100) / 100,
            };
          }

          // Scale Side Dish
          if (defaultSide.calories > 0) {
            const sideKcalPerGram = defaultSide.calories / defaultSide.serving_size;
            let newSidePortion = defaultSide.serving_size + (sideDeficitShare / sideKcalPerGram);
            newSidePortion = Math.min(newSidePortion, 250); // Clamp to max portion limit (250g)
            
            const scale = newSidePortion / defaultSide.serving_size;
            rebalanced[sideKey] = {
              ...defaultSide,
              serving_size: Math.round(newSidePortion),
              calories: Math.round(defaultSide.calories * scale * 10) / 10,
              protein: Math.round(defaultSide.protein * scale * 100) / 100,
              carbs: Math.round(defaultSide.carbs * scale * 100) / 100,
              fat: Math.round(defaultSide.fat * scale * 100) / 100,
            };
          }
        }
      } else {
        // Restore standard portion values if they switched back to a caloric drink
        const defaultMain = menuData[mealName as keyof typeof menuData]?.courses?.Main?.candidates?.find((c: any) => c.name === main.name) || main;
        const defaultSide = menuData[mealName as keyof typeof menuData]?.courses?.Side?.candidates?.find((c: any) => c.name === side.name) || side;
        rebalanced[mainKey] = defaultMain;
        rebalanced[sideKey] = defaultSide;
      }
    });

    return rebalanced;
  }, [selectedItems, menuData]);

  // Sync rebalanced items back to parent and session storage safely
  useEffect(() => {
    if (Object.keys(rebalancedSelectedItems).length > 0) {
      const prevString = sessionStorage.getItem('dss_selected_items');
      const newString = JSON.stringify(rebalancedSelectedItems);
      if (prevString !== newString) {
        sessionStorage.setItem('dss_selected_items', newString);
        onSelectedItemsChange(rebalancedSelectedItems);
      }
    }
  }, [rebalancedSelectedItems, onSelectedItemsChange]);

  // Calculate totals from currently selected (rebalanced) items
  const totalCalories = Object.values(rebalancedSelectedItems).reduce((sum: number, item: any) => sum + (item.calories || 0), 0);
  const totalProtein = Object.values(rebalancedSelectedItems).reduce((sum: number, item: any) => sum + (item.protein || 0), 0);
  const totalCarbs = Object.values(rebalancedSelectedItems).reduce((sum: number, item: any) => sum + (item.carbs || 0), 0);
  const totalFat = Object.values(rebalancedSelectedItems).reduce((sum: number, item: any) => sum + (item.fat || 0), 0);

  // Use the calculated TDEE from analysisResult if available
  const targetCalories = analysisResult?.energy?.tdee
    ? Math.round(analysisResult.energy.tdee)
    : 2000;

  if (loading) {
    const currentStepText = loadingSteps[statusIndex];

    const foods = [
      { emoji: '🍎', start: 0.0, targetX: -24, targetY: 132, rotate: 15 },
      { emoji: '🥦', start: 0.7, targetX: 22, targetY: 132, rotate: -25 },
      { emoji: '🥕', start: 1.4, targetX: -10, targetY: 120, rotate: 35 },
      { emoji: '🐟', start: 2.1, targetX: 10, targetY: 110, rotate: -45 },
      { emoji: '🥩', start: 2.8, targetX: -18, targetY: 96, rotate: 55 },
      { emoji: '🥚', start: 3.5, targetX: 16, targetY: 86, rotate: -30 },
      { emoji: '🥑', start: 4.2, targetX: 0, targetY: 74, rotate: 12 },
    ];

    const getFoodAnimation = (food: typeof foods[0]) => {
      const duration = 8.0;
      const start = food.start;
      const fallDuration = 0.45;
      const bounceDuration = 0.15;
      const rollDuration = 0.25;

      const landTime = start + fallDuration;
      const bounceTime = landTime + bounceDuration;
      const settleTime = bounceTime + rollDuration;

      const pStart = start / duration;
      const pLand = landTime / duration;
      const pBounce = bounceTime / duration;
      const pSettle = settleTime / duration;
      const pFadeStart = 7.0 / duration;
      const pFadeEnd = 7.6 / duration;

      const times = [0, pStart, pLand, pBounce, pSettle, pFadeStart, pFadeEnd, 1];

      return {
        times,
        y: [-60, -60, food.targetY, food.targetY - 12, food.targetY, food.targetY, food.targetY + 40, food.targetY + 40],
        x: [0, 0, 0, food.targetX * 0.5, food.targetX, food.targetX, food.targetX, food.targetX],
        opacity: [0, 0, 1, 1, 1, 1, 0, 0],
        rotate: [0, 0, food.rotate * 0.7, food.rotate * 0.9, food.rotate, food.rotate, food.rotate, food.rotate]
      };
    };

    return (
      <div className="min-h-[calc(100vh-4rem)] bg-gradient-to-br from-background via-background to-secondary/30 flex flex-col items-center justify-center p-4 text-center">
        <div className="flex flex-col items-center">
          {/* Animated Bowl & Falling Foods container */}
          <motion.div
            animate={{
              y: [0, -4, 0],
              rotate: [0, -1.2, 1.2, 0],
            }}
            transition={{
              duration: 2.4,
              repeat: Infinity,
              ease: "easeInOut",
            }}
            className="relative w-48 h-56 flex flex-col items-center justify-end overflow-visible select-none"
          >
            {/* Gentle Steam Lines */}
            <div className="absolute bottom-20 flex gap-3 z-0">
              {[0, 1, 2].map((j) => (
                <motion.div
                  key={j}
                  initial={{ y: 5, opacity: 0, scaleY: 0.5 }}
                  animate={{
                    y: [-5, -25],
                    opacity: [0, 0.4, 0],
                    scaleY: [0.5, 1.2, 0.5],
                  }}
                  transition={{
                    duration: 1.8,
                    repeat: Infinity,
                    delay: j * 0.6,
                    ease: "easeInOut",
                  }}
                  className="w-1.5 h-6 bg-emerald-500/20 dark:bg-emerald-400/15 rounded-full filter blur-[1px]"
                />
              ))}
            </div>

            {/* Mask Container for clipping bottom & sides */}
            <div className="absolute bottom-0 w-32 h-44 overflow-hidden rounded-b-[48px] z-10">
              {/* Inner Bowl Base behind items (simulates inner ceramic bottom) */}
              <div className="absolute inset-x-0 bottom-0 h-16 bg-slate-100 dark:bg-slate-950 z-0" />

              {/* Falling & Accumulating Foods */}
              {foods.map((food, i) => {
                const anim = getFoodAnimation(food);
                return (
                  <motion.div
                    key={i}
                    animate={{
                      y: anim.y,
                      x: anim.x,
                      opacity: anim.opacity,
                      rotate: anim.rotate,
                    }}
                    transition={{
                      duration: 8.0,
                      repeat: Infinity,
                      times: anim.times,
                      ease: "linear",
                    }}
                    className="absolute text-3xl z-10"
                    style={{
                      top: 0,
                      left: 'calc(50% - 18px)',
                    }}
                  >
                    {food.emoji}
                  </motion.div>
                );
              })}
            </div>

            {/* Physical Bowl Front Overlay */}
            <div className="absolute bottom-0 w-32 h-16 pointer-events-none z-20">
              {/* Semi-transparent Ceramic Wall of the Bowl (emerald accents) */}
              <div className="w-full h-full rounded-b-[48px] border-4 border-t-0 border-emerald-600 dark:border-emerald-500 bg-gradient-to-b from-white/50 to-slate-100/60 dark:from-slate-900/50 dark:to-slate-850/60 backdrop-blur-[3px] shadow-lg z-20" />
            </div>
          </motion.div>

          {/* Dynamic Ground Shadow */}
          <motion.div
            animate={{
              scaleX: [1, 0.92, 1],
              opacity: [0.35, 0.2, 0.35]
            }}
            transition={{
              duration: 2.4,
              repeat: Infinity,
              ease: "easeInOut",
            }}
            className="w-28 h-2 bg-black/10 dark:bg-black/35 rounded-full filter blur-[2.5px] mb-8"
          />
        </div>

        {/* Text Container with smooth fade-in-out transition */}
        <div className="max-w-lg w-full h-16 flex items-center justify-center px-4 text-center">
          <AnimatePresence mode="wait">
            <motion.p
              key={statusIndex}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.3 }}
              className="text-gray-700 dark:text-gray-300 font-semibold text-lg font-sans tracking-wide"
            >
              {currentStepText}
            </motion.p>
          </AnimatePresence>
        </div>

        {/* Subtitle/Algorithm badge */}
        <p className="text-xs text-gray-500 dark:text-gray-500 font-medium font-sans mt-2">
          Engine: {algorithm === 'genetic' ? 'Genetic Algorithm v1' : 'Greedy Optimizer v1'}
        </p>
      </div>
    );
  }

  if (error || !menuData) {
    return (
      <div className="min-h-[calc(100vh-4rem)] bg-gradient-to-br from-background via-background to-secondary/30 flex flex-col items-center justify-center p-4">
        <div className="bg-white/70 dark:bg-slate-800/40 backdrop-blur-md p-8 rounded-3xl border border-destructive/30 dark:border-destructive/20 max-w-lg text-center shadow-xl shadow-primary/5 dark:shadow-none">
          <p className="text-destructive font-bold text-xl mb-3 font-serif">Oops, something went wrong</p>
          <p className="text-gray-600 dark:text-gray-400 mb-6 font-sans">{error}</p>
          <button
            onClick={fetchMenu}
            className="px-6 py-3 bg-destructive/10 text-destructive rounded-2xl font-semibold hover:bg-destructive/15 transition-all inline-flex items-center gap-2 border border-destructive/20 cursor-pointer text-sm"
          >
            <RotateCcw className="w-5 h-5" />
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <>
      <div className="w-full pb-12 sm:pb-8">
        <div className="space-y-8">
          {['breakfast', 'lunch', 'dinner'].map((mealName) => {
            const meal = menuData[mealName];
            if (!meal || !meal.courses) return null;

            const theme = mealThemes[mealName] || mealThemes.breakfast;
            const timeText = timeLabels[mealName];

            return (
              <div key={mealName} className={`relative overflow-hidden backdrop-blur-md rounded-3xl p-6 border shadow-xl dark:shadow-none transition-all duration-300 ${theme.containerBg} ${theme.containerBorder}`}>
                {/* Sun/Sunset art glow effects */}
                <div className={theme.glowClass} />
                <div className={theme.glowClass2} />

                <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6 border-b border-border/50 dark:border-slate-800/60 pb-4 relative z-10">
                  <div className="flex items-center gap-3">
                    <div className="p-2.5 bg-white/80 dark:bg-slate-900/80 rounded-2xl shadow-sm border border-border/40">
                      {theme.icon}
                    </div>
                    <div>
                      <h2 className="text-xl font-bold text-gray-900 dark:text-white capitalize font-serif leading-none mb-1.5 flex items-center gap-2">
                        {mealName}
                      </h2>
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold ${theme.badgeBg} ${theme.badgeText}`}>
                        <svg className="w-3.5 h-3.5 mr-1 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                        {timeText}
                      </span>
                    </div>
                  </div>
                  <div className="text-right sm:text-right shrink-0">
                    <div className="text-sm font-bold text-primary dark:text-emerald-450 font-serif">
                      Target: {meal.target_calories} cal
                    </div>
                    <div className="text-[11px] text-gray-500 dark:text-gray-400 font-sans mt-0.5">
                      Actual: {meal.actual_calories} cal
                    </div>
                  </div>
                </div>

                <div className="space-y-6 relative z-10">
                  {['Main', 'Side', 'Drink'].map((courseName) => {
                    const course = meal.courses![courseName];
                    const key = `${mealName}_${courseName}`;

                    return (
                      <div key={courseName}>
                        <div className="mb-3">
                          <h3 className="font-serif font-semibold text-gray-950 dark:text-white capitalize text-sm tracking-wide">
                            {courseName === 'Main' ? 'Main Course' : courseName === 'Side' ? 'Side Dish' : 'Drink'}
                          </h3>
                        </div>

                        {!course || course.candidates.length === 0 ? (
                          <div className="p-4 rounded-2xl border border-dashed border-border dark:border-slate-800 bg-secondary/20 dark:bg-slate-900/20 text-center">
                            <p className="text-xs text-gray-500 dark:text-gray-400 font-sans">No foods found matching your constraints.</p>
                          </div>
                        ) : (
                          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                            {course.candidates.map((option) => {
                              const isSelected = selectedItems[key]?.name === option.name;
                              const displayOption = isSelected ? rebalancedSelectedItems[key] : option;
                              return (
                                <button
                                  key={option.fdc_id || option.name}
                                  onClick={() => handleSelect(mealName, courseName, option)}
                                  className={`relative overflow-hidden p-3.5 rounded-2xl text-left transition-all cursor-pointer ${
                                    isSelected
                                      ? theme.selectedClass
                                      : theme.unselectedClass
                                  }`}
                                >
                                  <div className="flex justify-between items-start gap-2 mb-1.5">
                                    <p className="font-bold text-sm text-gray-900 dark:text-white leading-snug line-clamp-2 flex-1 font-sans">
                                      {displayOption.name}
                                    </p>
                                    <span className={`px-2 py-0.5 rounded-full text-[9px] font-bold text-white uppercase tracking-wider shrink-0 ${getRibbonColor(displayOption.cuisine_label)} shadow-sm bg-opacity-90`}>
                                      {displayOption.cuisine_label || 'Generic'}
                                    </span>
                                  </div>
                                  <p className="text-xs font-semibold text-primary dark:text-emerald-450 mb-1 font-serif">
                                    {displayOption.calories} kcal
                                  </p>
                                  <div className="flex items-center justify-between text-[10px] text-gray-500 dark:text-gray-400 font-sans">
                                    <span>Carb: {displayOption.carbs}g • Pro: {displayOption.protein}g • Fat: {displayOption.fat}g</span>
                                    <span className="font-medium shrink-0">{displayOption.serving_size}g</span>
                                  </div>
                                </button>
                              );
                            })}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })}

          {menuData.snack && (() => {
            const mealName = 'snack';
            const theme = mealThemes[mealName];
            const timeText = timeLabels[mealName];

            return (
              <div key={mealName} className={`relative overflow-hidden backdrop-blur-md rounded-3xl p-6 border shadow-xl dark:shadow-none transition-all duration-300 ${theme.containerBg} ${theme.containerBorder}`}>
                {/* Snack art glow effects */}
                <div className={theme.glowClass} />
                <div className={theme.glowClass2} />

                <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6 border-b border-border/50 dark:border-slate-800/60 pb-4 relative z-10">
                  <div className="flex items-center gap-3">
                    <div className="p-2.5 bg-white/80 dark:bg-slate-900/80 rounded-2xl shadow-sm border border-border/40">
                      {theme.icon}
                    </div>
                    <div>
                      <h2 className="text-xl font-bold text-gray-900 dark:text-white capitalize font-serif leading-none mb-1.5 flex items-center gap-2">
                        Snack
                      </h2>
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold ${theme.badgeBg} ${theme.badgeText}`}>
                        <svg className="w-3.5 h-3.5 mr-1 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                        {timeText}
                      </span>
                    </div>
                  </div>
                  <div className="text-right sm:text-right shrink-0">
                    <div className="text-sm font-bold text-primary dark:text-emerald-450 font-serif">
                      Target: {menuData.snack.target_calories} cal
                    </div>
                    <div className="text-[11px] text-gray-500 dark:text-gray-400 font-sans mt-0.5">
                      Actual: {menuData.snack.actual_calories} cal
                    </div>
                  </div>
                </div>

                <div className="mb-3 relative z-10">
                  <h3 className="font-serif font-semibold text-gray-950 dark:text-white text-sm tracking-wide">Options</h3>
                </div>

                {!menuData.snack.candidates || menuData.snack.candidates.length === 0 ? (
                  <div className="p-4 rounded-2xl border border-dashed border-border dark:border-slate-800 bg-secondary/20 dark:bg-slate-900/20 text-center relative z-10">
                    <p className="text-xs text-gray-500 dark:text-gray-400 font-sans">No snack found matching your constraints.</p>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 relative z-10">
                    {menuData.snack.candidates.map((option) => (
                      <button
                        key={option.fdc_id || option.name}
                        onClick={() => handleSelect('snack', 'snack', option)}
                        className={`relative overflow-hidden p-3.5 rounded-2xl text-left transition-all cursor-pointer ${
                          selectedItems['snack_snack']?.name === option.name
                            ? theme.selectedClass
                            : theme.unselectedClass
                        }`}
                      >
                        <div className="flex justify-between items-start gap-2 mb-1.5">
                          <p className="font-bold text-sm text-gray-900 dark:text-white leading-snug line-clamp-2 flex-1 font-sans">
                            {option.name}
                          </p>
                          <span className={`px-2 py-0.5 rounded-full text-[9px] font-bold text-white uppercase tracking-wider shrink-0 ${getRibbonColor(option.cuisine_label)} shadow-sm bg-opacity-90`}>
                            {option.cuisine_label || 'Generic'}
                          </span>
                        </div>
                        <p className="text-xs font-semibold text-primary dark:text-emerald-450 mb-1 font-serif">
                          {option.calories} kcal
                        </p>
                        <div className="flex items-center justify-between text-[10px] text-gray-500 dark:text-gray-400 font-sans">
                          <span>Carb: {option.carbs}g • Pro: {option.protein}g • Fat: {option.fat}g</span>
                          <span className="font-medium shrink-0">{option.serving_size}g</span>
                        </div>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            );
          })()}
        </div>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mt-12 mb-2">
          <button
            onClick={handleRegenerate}
            className="px-8 py-3.5 text-base bg-white dark:bg-slate-800 text-foreground rounded-2xl font-semibold hover:bg-gray-50 dark:hover:bg-slate-700 transition-all inline-flex items-center justify-center gap-2 border border-border shadow-sm cursor-pointer transform hover:-translate-y-0.5"
          >
            <RotateCcw className="w-4 h-4 sm:w-5 sm:h-5 text-primary" />
            Regenerate Menu
          </button>
          <button
            onClick={onViewReport}
            className="px-8 py-3.5 text-base bg-primary text-primary-foreground rounded-2xl font-semibold hover:bg-primary/95 transition-all inline-flex items-center justify-center gap-2 shadow-md hover:shadow-lg hover:shadow-primary/10 cursor-pointer transform hover:-translate-y-0.5"
          >
            {t.results.viewReport}
            <ArrowRight className="w-4 h-4 sm:w-5 sm:h-5" />
          </button>
        </div>
      </div>

      {/* Sticky Nutrition Summary (Mobile only) */}
      <div className="lg:hidden fixed bottom-0 left-0 right-0 bg-white/80 dark:bg-slate-900/70 backdrop-blur-md border-t border-border/80 dark:border-slate-800/60 shadow-[0_-8px_30px_rgba(0,0,0,0.06)] z-40">
        <div className="max-w-4xl mx-auto px-3 sm:px-4 py-3 sm:py-4">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 sm:gap-4">
            <div className="text-center">
              <p className="text-[10px] sm:text-xs text-gray-600 dark:text-gray-400 mb-0.5 sm:mb-1 font-sans">{t.results.dailyCalories}</p>
              <p className="text-sm sm:text-lg md:text-xl font-bold text-primary dark:text-emerald-400 font-serif">
                {Math.round(totalCalories)} / {targetCalories}
              </p>
            </div>
            <div className="text-center">
              <p className="text-[10px] sm:text-xs text-gray-600 dark:text-gray-400 mb-0.5 sm:mb-1 font-sans">{t.results.carbs}</p>
              <p className="text-sm sm:text-lg md:text-xl font-bold text-primary dark:text-emerald-400 font-serif">
                {Math.round(totalCarbs)}g
              </p>
            </div>
            <div className="text-center">
              <p className="text-[10px] sm:text-xs text-gray-600 dark:text-gray-400 mb-0.5 sm:mb-1 font-sans">{t.results.protein}</p>
              <p className="text-sm sm:text-lg md:text-xl font-bold text-primary dark:text-emerald-400 font-serif">
                {Math.round(totalProtein)}g
              </p>
            </div>
            <div className="text-center">
              <p className="text-[10px] sm:text-xs text-gray-600 dark:text-gray-400 mb-0.5 sm:mb-1 font-sans">{t.results.fat}</p>
              <p className="text-sm sm:text-lg md:text-xl font-bold text-primary dark:text-emerald-400 font-serif">
                {Math.round(totalFat)}g
              </p>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

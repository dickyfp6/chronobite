import { useState, useEffect } from 'react';
import { motion } from 'motion/react';
import { ArrowRight, Loader2, RotateCcw } from 'lucide-react';
import { useI18n } from '../contexts/I18nContext';
import type { UserInputData } from './InputWizard';
import { api } from '../services/api';

interface ResultsProps {
  userData: UserInputData;
  algorithm?: 'greedy' | 'genetic';
  analysisResult?: any;
  onViewReport: () => void;
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

export function Results({ userData, algorithm, analysisResult, onViewReport }: ResultsProps) {
  const { t } = useI18n();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [menuData, setMenuData] = useState<Record<string, Meal> | null>(null);

  // Track selected candidate for each meal+course. e.g. "breakfast_Main" -> Candidate
  const [selected, setSelected] = useState<Record<string, Candidate>>({});

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
        const scaleFactor = targetCalories / candidate.calories;
        scaled.push({
          ...candidate,
          serving_size: Math.round(100 * scaleFactor * 10) / 10,
          calories: Math.round(targetCalories * 10) / 10,
          protein: Math.round(candidate.protein * scaleFactor * 10) / 10,
          carbs: Math.round(candidate.carbs * scaleFactor * 10) / 10,
          fat: Math.round(candidate.fat * scaleFactor * 10) / 10,
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

      setSelected(initialSelected);
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
    setSelected((prev) => {
      const newSelected = {
        ...prev,
        [key]: candidate,
      };
      sessionStorage.setItem('dss_selected_items', JSON.stringify(newSelected));
      return newSelected;
    });
  };

  // Calculate totals from currently selected items
  const totalCalories = Object.values(selected).reduce((sum, item) => sum + item.calories, 0);
  const totalProtein = Object.values(selected).reduce((sum, item) => sum + item.protein, 0);
  const totalCarbs = Object.values(selected).reduce((sum, item) => sum + item.carbs, 0);
  const totalFat = Object.values(selected).reduce((sum, item) => sum + item.fat, 0);

  // Use the calculated TDEE from analysisResult if available
  const targetCalories = analysisResult?.energy?.tdee
    ? Math.round(analysisResult.energy.tdee)
    : 2000;

  if (loading) {
    return (
      <div className="min-h-[calc(100vh-4rem)] bg-gradient-to-br from-emerald-50 via-green-50 to-teal-50 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900 flex flex-col items-center justify-center p-4">
        <Loader2 className="w-12 h-12 text-emerald-500 animate-spin mb-4" />
        <p className="text-gray-600 dark:text-gray-400 font-medium">Generating optimal meal plan with {algorithm === 'genetic' ? 'Genetic' : 'Greedy'} algorithm...</p>
      </div>
    );
  }

  if (error || !menuData) {
    return (
      <div className="min-h-[calc(100vh-4rem)] bg-gradient-to-br from-emerald-50 via-green-50 to-teal-50 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900 flex flex-col items-center justify-center p-4">
        <div className="bg-white dark:bg-slate-800 p-8 rounded-2xl border-2 border-red-200 dark:border-red-800 max-w-lg text-center shadow-sm">
          <p className="text-red-600 dark:text-red-400 font-bold text-xl mb-3">Oops, something went wrong</p>
          <p className="text-gray-600 dark:text-gray-400 mb-6">{error}</p>
          <button
            onClick={fetchMenu}
            className="px-6 py-3 bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300 rounded-xl font-medium hover:bg-red-100 dark:hover:bg-red-900/40 transition-all inline-flex items-center gap-2 border border-red-200 dark:border-red-800"
          >
            <RotateCcw className="w-5 h-5" />
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-[calc(100vh-4rem)] bg-gradient-to-br from-emerald-50 via-green-50 to-teal-50 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900 px-4 py-8 pb-48 sm:pb-40">
      <div className="max-w-4xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-3xl sm:text-4xl font-bold mb-2 text-gray-900 dark:text-white">{t.results.title}</h1>
          <p className="text-gray-600 dark:text-gray-400">Select your meals from the AI-generated options below</p>
        </motion.div>

        <div className="space-y-8">
          {['breakfast', 'lunch', 'dinner'].map((mealName) => {
            const meal = menuData[mealName];
            if (!meal || !meal.courses) return null;

            return (
              <div key={mealName} className="bg-white dark:bg-slate-800 rounded-xl p-6 border border-gray-200/80 dark:border-slate-700/80 shadow-sm">
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-xl font-bold text-emerald-700 dark:text-emerald-400 capitalize">
                    {mealName}
                  </h2>
                  <div className="text-sm font-medium text-gray-500 dark:text-gray-400">
                    Target: {meal.target_calories} cal
                  </div>
                </div>

                <div className="space-y-6">
                  {['Main', 'Side', 'Drink'].map((courseName) => {
                    const course = meal.courses![courseName];
                    const key = `${mealName}_${courseName}`;

                    return (
                      <div key={courseName}>
                        <div className="mb-3">
                          <h3 className="font-semibold text-gray-900 dark:text-white capitalize text-sm">
                            {courseName === 'Main' ? 'Main Course' : courseName === 'Side' ? 'Side Dish' : 'Drink'}
                          </h3>
                        </div>

                        {!course || course.candidates.length === 0 ? (
                          <div className="p-4 rounded-lg border border-dashed border-gray-200 dark:border-slate-700 bg-gray-50/50 dark:bg-slate-800/50 text-center">
                            <p className="text-xs text-gray-500 dark:text-gray-400">No foods found matching your constraints.</p>
                          </div>
                        ) : (
                          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                            {course.candidates.map((option) => (
                              <button
                                key={option.fdc_id || option.name}
                                onClick={() => handleSelect(mealName, courseName, option)}
                                className={`relative overflow-hidden p-3.5 rounded-lg border text-left transition-all ${
                                  selected[key]?.name === option.name
                                    ? 'border-emerald-500 dark:border-emerald-400 bg-emerald-500/5 dark:bg-emerald-400/5 shadow-sm ring-1 ring-emerald-500/30'
                                    : 'border-gray-200/80 dark:border-slate-700 hover:border-emerald-300 dark:hover:border-slate-600 hover:bg-slate-50 dark:hover:bg-slate-800/50'
                                }`}
                              >
                                <div className="flex justify-between items-start gap-2 mb-1.5">
                                  <p className="font-bold text-sm text-gray-900 dark:text-white leading-snug line-clamp-2 flex-1">
                                    {option.name}
                                  </p>
                                  <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold text-white uppercase tracking-wider shrink-0 ${getRibbonColor(option.cuisine_label)}`}>
                                    {option.cuisine_label || 'Generic'}
                                  </span>
                                </div>
                                <p className="text-xs font-semibold text-emerald-600 dark:text-emerald-400 mb-1">
                                  {option.calories} kcal
                                </p>
                                <div className="flex items-center justify-between text-[10px] text-gray-500 dark:text-gray-400">
                                  <span>P: {option.protein}g • C: {option.carbs}g • F: {option.fat}g</span>
                                  <span className="font-medium shrink-0">{option.serving_size}g</span>
                                </div>
                              </button>
                            ))}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })}

          {menuData.snack && (
            <div className="bg-white dark:bg-slate-800 rounded-xl p-6 border border-gray-200/80 dark:border-slate-700/80 shadow-sm">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-bold text-emerald-700 dark:text-emerald-400 capitalize">
                  Snack
                </h2>
                <div className="text-sm font-medium text-gray-500 dark:text-gray-400">
                  Target: {menuData.snack.target_calories} cal
                </div>
              </div>

              <div className="mb-3">
                <h3 className="font-semibold text-gray-900 dark:text-white text-sm">Options</h3>
              </div>

              {!menuData.snack.candidates || menuData.snack.candidates.length === 0 ? (
                <div className="p-4 rounded-lg border border-dashed border-gray-200 dark:border-slate-700 bg-gray-50/50 dark:bg-slate-800/50 text-center">
                  <p className="text-xs text-gray-500 dark:text-gray-400">No snack found matching your constraints.</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  {menuData.snack.candidates.map((option) => (
                    <button
                      key={option.fdc_id || option.name}
                      onClick={() => handleSelect('snack', 'snack', option)}
                      className={`relative overflow-hidden p-3.5 rounded-lg border text-left transition-all ${
                        selected['snack_snack']?.name === option.name
                          ? 'border-emerald-500 dark:border-emerald-400 bg-emerald-500/5 dark:bg-emerald-400/5 shadow-sm ring-1 ring-emerald-500/30'
                          : 'border-gray-200/80 dark:border-slate-700 hover:border-emerald-300 dark:hover:border-slate-600 hover:bg-slate-50 dark:hover:bg-slate-800/50'
                      }`}
                    >
                      <div className="flex justify-between items-start gap-2 mb-1.5">
                        <p className="font-bold text-sm text-gray-900 dark:text-white leading-snug line-clamp-2 flex-1">
                          {option.name}
                        </p>
                        <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold text-white uppercase tracking-wider shrink-0 ${getRibbonColor(option.cuisine_label)}`}>
                          {option.cuisine_label || 'Generic'}
                        </span>
                      </div>
                      <p className="text-xs font-semibold text-emerald-600 dark:text-emerald-400 mb-1">
                        {option.calories} kcal
                      </p>
                      <div className="flex items-center justify-between text-[10px] text-gray-500 dark:text-gray-400">
                        <span>P: {option.protein}g • C: {option.carbs}g • F: {option.fat}g</span>
                        <span className="font-medium shrink-0">{option.serving_size}g</span>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        <div className="text-center mt-12 mb-2">
          <button
            onClick={onViewReport}
            className="px-6 sm:px-8 py-3 sm:py-4 text-base sm:text-lg bg-gradient-to-r from-emerald-500 to-teal-500 text-white rounded-xl font-medium hover:from-emerald-600 hover:to-teal-600 transition-all inline-flex items-center gap-2 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
          >
            {t.results.viewReport}
            <ArrowRight className="w-4 h-4 sm:w-5 sm:h-5" />
          </button>
        </div>
      </div>

      {/* Sticky Nutrition Summary */}
      <div className="fixed bottom-0 left-0 right-0 bg-white/95 dark:bg-slate-800/95 backdrop-blur-md border-t border-gray-200 dark:border-slate-700 shadow-[0_-8px_30px_rgba(0,0,0,0.06)] z-40">
        <div className="max-w-4xl mx-auto px-3 sm:px-4 py-3 sm:py-4">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 sm:gap-4">
            <div className="text-center">
              <p className="text-[10px] sm:text-xs text-gray-600 dark:text-gray-400 mb-0.5 sm:mb-1">{t.results.dailyCalories}</p>
              <p className="text-sm sm:text-lg md:text-xl font-bold text-emerald-600 dark:text-emerald-400">
                {Math.round(totalCalories)} / {targetCalories}
              </p>
            </div>
            <div className="text-center">
              <p className="text-[10px] sm:text-xs text-gray-600 dark:text-gray-400 mb-0.5 sm:mb-1">{t.results.protein}</p>
              <p className="text-sm sm:text-lg md:text-xl font-bold text-emerald-600 dark:text-emerald-400">
                {Math.round(totalProtein)}g
              </p>
            </div>
            <div className="text-center">
              <p className="text-[10px] sm:text-xs text-gray-600 dark:text-gray-400 mb-0.5 sm:mb-1">{t.results.carbs}</p>
              <p className="text-sm sm:text-lg md:text-xl font-bold text-emerald-600 dark:text-emerald-400">
                {Math.round(totalCarbs)}g
              </p>
            </div>
            <div className="text-center">
              <p className="text-[10px] sm:text-xs text-gray-600 dark:text-gray-400 mb-0.5 sm:mb-1">{t.results.fat}</p>
              <p className="text-sm sm:text-lg md:text-xl font-bold text-emerald-600 dark:text-emerald-400">
                {Math.round(totalFat)}g
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

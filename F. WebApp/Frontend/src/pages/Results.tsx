import { useState, useEffect } from 'react';
import { ArrowRight, Loader2, RotateCcw } from 'lucide-react';
import { useI18n } from '../contexts/I18nContext';
import type { UserInputData } from './InputWizard';
import { api } from '../services/api';
import { motion, AnimatePresence } from 'motion/react';

const loadingSteps = {
  id: [
    "Menganalisis profil fisik & kebutuhan energi...",
    "Mengevaluasi batasan medis & riwayat kesehatan...",
    "Menyaring database bahan makanan bernutrisi...",
    "Menyusun kombinasi menu makanan harian optimal...",
    "Menyeimbangkan porsi makro & mikro nutrisi...",
    "Menyempurnakan hasil rekomendasi untuk Anda..."
  ],
  en: [
    "Analyzing physical profile & energy needs...",
    "Evaluating medical constraints & health history...",
    "Filtering nutritional food database...",
    "Formulating optimal daily meal combinations...",
    "Balancing macro & micro nutrient distributions...",
    "Finalizing customized recommendations for you..."
  ]
};

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
      setStatusIndex((prev) => (prev + 1) % loadingSteps.en.length);
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

  useEffect(() => {
    fetchMenu();
  }, []);

  const handleSelect = (meal: string, category: string, candidate: Candidate) => {
    const key = `${meal}_${category}`;
    const newSelected = {
      ...selectedItems,
      [key]: candidate,
    };
    sessionStorage.setItem('dss_selected_items', JSON.stringify(newSelected));
    onSelectedItemsChange(newSelected);
  };

  // Calculate totals from currently selected items
  const totalCalories = Object.values(selectedItems).reduce((sum, item) => sum + (item.calories || 0), 0);
  const totalProtein = Object.values(selectedItems).reduce((sum, item) => sum + (item.protein || 0), 0);
  const totalCarbs = Object.values(selectedItems).reduce((sum, item) => sum + (item.carbs || 0), 0);
  const totalFat = Object.values(selectedItems).reduce((sum, item) => sum + (item.fat || 0), 0);

  // Use the calculated TDEE from analysisResult if available
  const targetCalories = analysisResult?.energy?.tdee
    ? Math.round(analysisResult.energy.tdee)
    : 2000;

  if (loading) {
    const language = (useI18n().language as string) || 'en';
    const steps = language === 'id' ? loadingSteps.id : loadingSteps.en;
    const currentStepText = steps[statusIndex];

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

            return (
              <div key={mealName} className="bg-white/70 dark:bg-slate-800/40 backdrop-blur-md rounded-3xl p-6 border border-border/80 dark:border-slate-850/30 shadow-xl shadow-primary/5 dark:shadow-none">
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-xl font-bold text-primary dark:text-emerald-450 font-serif capitalize">
                    {mealName}
                  </h2>
                  <div className="text-sm font-medium text-gray-500 dark:text-gray-400 font-sans">
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
                          <h3 className="font-serif font-semibold text-gray-900 dark:text-white capitalize text-sm tracking-wide">
                            {courseName === 'Main' ? 'Main Course' : courseName === 'Side' ? 'Side Dish' : 'Drink'}
                          </h3>
                        </div>

                        {!course || course.candidates.length === 0 ? (
                          <div className="p-4 rounded-2xl border border-dashed border-border dark:border-slate-800 bg-secondary/20 dark:bg-slate-900/20 text-center">
                            <p className="text-xs text-gray-500 dark:text-gray-400 font-sans">No foods found matching your constraints.</p>
                          </div>
                        ) : (
                          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                            {course.candidates.map((option) => (
                              <button
                                key={option.fdc_id || option.name}
                                onClick={() => handleSelect(mealName, courseName, option)}
                                className={`relative overflow-hidden p-3.5 rounded-2xl border text-left transition-all cursor-pointer bg-white/40 dark:bg-slate-950/20 ${
                                  selectedItems[key]?.name === option.name
                                    ? 'border-primary dark:border-primary bg-primary/5 dark:bg-primary/10 shadow-sm ring-1 ring-primary/20'
                                    : 'border-border/80 dark:border-slate-800 hover:border-primary/50 dark:hover:border-slate-700 hover:bg-secondary/40 dark:hover:bg-slate-800/50'
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
                  })}
                </div>
              </div>
            );
          })}

          {menuData.snack && (
            <div className="bg-white/70 dark:bg-slate-800/40 backdrop-blur-md rounded-3xl p-6 border border-border/80 dark:border-slate-850/30 shadow-xl shadow-primary/5 dark:shadow-none">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-bold text-primary dark:text-emerald-450 font-serif capitalize">
                  Snack
                </h2>
                <div className="text-sm font-medium text-gray-500 dark:text-gray-400 font-sans">
                  Target: {menuData.snack.target_calories} cal
                </div>
              </div>

              <div className="mb-3">
                <h3 className="font-serif font-semibold text-gray-900 dark:text-white text-sm tracking-wide">Options</h3>
              </div>

              {!menuData.snack.candidates || menuData.snack.candidates.length === 0 ? (
                <div className="p-4 rounded-2xl border border-dashed border-border dark:border-slate-800 bg-secondary/20 dark:bg-slate-900/20 text-center">
                  <p className="text-xs text-gray-500 dark:text-gray-400 font-sans">No snack found matching your constraints.</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  {menuData.snack.candidates.map((option) => (
                    <button
                      key={option.fdc_id || option.name}
                      onClick={() => handleSelect('snack', 'snack', option)}
                      className={`relative overflow-hidden p-3.5 rounded-2xl border text-left transition-all cursor-pointer bg-white/40 dark:bg-slate-950/20 ${
                        selectedItems['snack_snack']?.name === option.name
                          ? 'border-primary dark:border-primary bg-primary/5 dark:bg-primary/10 shadow-sm ring-1 ring-primary/20'
                          : 'border-border/80 dark:border-slate-800 hover:border-primary/50 dark:hover:border-slate-700 hover:bg-secondary/40 dark:hover:bg-slate-800/50'
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
          )}
        </div>

        <div className="text-center mt-12 mb-2">
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

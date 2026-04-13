import { useState } from 'react';
import { motion } from 'motion/react';
import { ArrowRight, RefreshCw } from 'lucide-react';
import { useI18n } from '../contexts/I18nContext';
import { generateRandomMealOptions, calculateNutrition, calculateDailyNeeds } from '../utils/mockData';
import type { UserInputData } from './InputWizard';

interface ResultsProps {
  userData: UserInputData;
  onViewReport: () => void;
}

export function Results({ userData, onViewReport }: ResultsProps) {
  const { t } = useI18n();

  const dailyNeeds = calculateDailyNeeds(
    userData.weight!,
    userData.height!,
    userData.age!,
    userData.gender!,
    userData.activity!
  );

  const [mealOptions, setMealOptions] = useState({
    breakfast: {
      mainCourse: generateRandomMealOptions('breakfast', 'mainCourse'),
      sideDish: generateRandomMealOptions('breakfast', 'sideDish'),
      drink: generateRandomMealOptions('breakfast', 'drink'),
    },
    lunch: {
      mainCourse: generateRandomMealOptions('lunch', 'mainCourse'),
      sideDish: generateRandomMealOptions('lunch', 'sideDish'),
      drink: generateRandomMealOptions('lunch', 'drink'),
    },
    dinner: {
      mainCourse: generateRandomMealOptions('dinner', 'mainCourse'),
      sideDish: generateRandomMealOptions('dinner', 'sideDish'),
      drink: generateRandomMealOptions('dinner', 'drink'),
    },
    snack: generateRandomMealOptions('snack', 'snack'),
  });

  const [selected, setSelected] = useState<any>({});
  const [refreshing, setRefreshing] = useState<string>('');

  const refreshMeal = (meal: string, category: string) => {
    const key = `${meal}_${category}`;
    setRefreshing(key);
    setMealOptions((prev) => ({
      ...prev,
      [meal]: {
        ...prev[meal as keyof typeof prev],
        [category]: generateRandomMealOptions(meal, category),
      },
    }));
    setTimeout(() => setRefreshing(''), 500);
  };

  const refreshSnack = () => {
    setRefreshing('snack');
    setMealOptions((prev) => ({
      ...prev,
      snack: generateRandomMealOptions('snack', 'snack'),
    }));
    setTimeout(() => setRefreshing(''), 500);
  };

  const handleSelect = (meal: string, category: string, id: string) => {
    const key = `${meal}_${category}`;
    const options = meal === 'snack'
      ? mealOptions.snack
      : (mealOptions[meal as keyof typeof mealOptions] as any)[category];
    const item = options.find((opt: any) => opt.id === id);

    setSelected((prev: any) => ({
      ...prev,
      [key]: item,
    }));
  };

  const nutrition = calculateNutrition(selected);

  return (
    <div className="min-h-[calc(100vh-4rem)] bg-gradient-to-br from-emerald-50 via-green-50 to-teal-50 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900 px-4 py-8 pb-48 sm:pb-40">
      <div className="max-w-4xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-3xl sm:text-4xl font-bold mb-2 text-gray-900 dark:text-white">{t.results.title}</h1>
          <p className="text-gray-600 dark:text-gray-400">Select your meals from the options below</p>
        </motion.div>

        <div className="space-y-8">
          {['breakfast', 'lunch', 'dinner'].map((meal) => (
            <div key={meal} className="bg-white dark:bg-slate-800 rounded-xl p-6 border-2 border-emerald-200 dark:border-emerald-700 shadow-sm">
              <h2 className="text-2xl font-bold mb-6 text-emerald-700 dark:text-emerald-400">
                {t.results.meals[meal as keyof typeof t.results.meals]}
              </h2>

              <div className="space-y-6">
                {['mainCourse', 'sideDish', 'drink'].map((category) => {
                  const key = `${meal}_${category}`;
                  const options = (mealOptions[meal as keyof typeof mealOptions] as any)[category];

                  return (
                    <div key={category}>
                      <div className="flex items-center justify-between mb-3">
                        <h3 className="font-medium text-gray-900 dark:text-white">
                          {t.results.meals[category as keyof typeof t.results.meals]}
                          {category === 'drink' && <span className="text-xs text-gray-500 dark:text-gray-400 ml-2">(Optional)</span>}
                        </h3>
                        <button
                          onClick={() => refreshMeal(meal, category)}
                          className="p-2 hover:bg-emerald-100 dark:hover:bg-emerald-900 rounded-lg transition-all text-emerald-600 dark:text-emerald-400"
                        >
                          <RefreshCw className={`w-4 h-4 ${refreshing === key ? 'animate-spin' : ''}`} />
                        </button>
                      </div>

                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                        {options.map((option: any) => (
                          <button
                            key={option.id}
                            onClick={() => handleSelect(meal, category, option.id)}
                            className={`p-4 rounded-lg border-2 text-left transition-all ${
                              selected[key]?.id === option.id
                                ? 'border-emerald-500 dark:border-emerald-400 bg-gradient-to-br from-emerald-100 to-teal-100 dark:from-emerald-900/50 dark:to-teal-900/50 shadow-lg ring-2 ring-emerald-400/50 dark:ring-emerald-400/30'
                                : 'border-emerald-200 dark:border-emerald-700 hover:border-emerald-400 dark:hover:border-emerald-500 hover:shadow-md hover:bg-emerald-50/50 dark:hover:bg-emerald-900/20'
                            }`}
                          >
                            <p className="font-medium text-sm text-emerald-900 dark:text-white mb-1">{option.name}</p>
                            <p className="text-xs text-emerald-600 dark:text-emerald-400">
                              {option.calories} cal • P: {option.protein}g • C: {option.carbs}g • F: {option.fat}g
                            </p>
                          </button>
                        ))}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          ))}

          <div className="bg-white dark:bg-slate-800 rounded-xl p-6 border-2 border-emerald-200 dark:border-emerald-700 shadow-sm">
            <h2 className="text-2xl font-bold mb-6 text-emerald-700 dark:text-emerald-400">{t.results.meals.snack}</h2>

            <div className="flex items-center justify-between mb-3">
              <h3 className="font-medium text-gray-900 dark:text-white">Options</h3>
              <button
                onClick={refreshSnack}
                className="p-2 hover:bg-emerald-100 dark:hover:bg-emerald-900 rounded-lg transition-all text-emerald-600 dark:text-emerald-400"
              >
                <RefreshCw className={`w-4 h-4 ${refreshing === 'snack' ? 'animate-spin' : ''}`} />
              </button>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {mealOptions.snack.map((option: any) => (
                <button
                  key={option.id}
                  onClick={() => handleSelect('snack', 'snack', option.id)}
                  className={`p-4 rounded-lg border-2 text-left transition-all ${
                    selected['snack_snack']?.id === option.id
                      ? 'border-emerald-500 dark:border-emerald-400 bg-gradient-to-br from-emerald-100 to-teal-100 dark:from-emerald-900/50 dark:to-teal-900/50 shadow-lg ring-2 ring-emerald-400/50 dark:ring-emerald-400/30'
                      : 'border-emerald-200 dark:border-emerald-700 hover:border-emerald-400 dark:hover:border-emerald-500 hover:shadow-md hover:bg-emerald-50/50 dark:hover:bg-emerald-900/20'
                  }`}
                >
                  <p className="font-medium text-sm text-emerald-900 dark:text-white mb-1">{option.name}</p>
                  <p className="text-xs text-emerald-600 dark:text-emerald-400">
                    {option.calories} cal • P: {option.protein}g • C: {option.carbs}g • F: {option.fat}g
                  </p>
                </button>
              ))}
            </div>
          </div>
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
      <div className="fixed bottom-0 left-0 right-0 bg-white/95 dark:bg-slate-800/95 backdrop-blur-md border-t-2 border-emerald-200 dark:border-emerald-700 shadow-lg z-40">
        <div className="max-w-4xl mx-auto px-3 sm:px-4 py-3 sm:py-4">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 sm:gap-4">
            <div className="text-center">
              <p className="text-[10px] sm:text-xs text-gray-600 dark:text-gray-400 mb-0.5 sm:mb-1">{t.results.dailyCalories}</p>
              <p className="text-sm sm:text-lg md:text-xl font-bold text-emerald-600 dark:text-emerald-400">
                {Math.round(nutrition.calories)} / {dailyNeeds.calories}
              </p>
            </div>
            <div className="text-center">
              <p className="text-[10px] sm:text-xs text-gray-600 dark:text-gray-400 mb-0.5 sm:mb-1">{t.results.protein}</p>
              <p className="text-sm sm:text-lg md:text-xl font-bold text-emerald-600 dark:text-emerald-400">
                {Math.round(nutrition.protein)}g / {dailyNeeds.protein}g
              </p>
            </div>
            <div className="text-center">
              <p className="text-[10px] sm:text-xs text-gray-600 dark:text-gray-400 mb-0.5 sm:mb-1">{t.results.carbs}</p>
              <p className="text-sm sm:text-lg md:text-xl font-bold text-emerald-600 dark:text-emerald-400">
                {Math.round(nutrition.carbs)}g / {dailyNeeds.carbs}g
              </p>
            </div>
            <div className="text-center">
              <p className="text-[10px] sm:text-xs text-gray-600 dark:text-gray-400 mb-0.5 sm:mb-1">{t.results.fat}</p>
              <p className="text-sm sm:text-lg md:text-xl font-bold text-emerald-600 dark:text-emerald-400">
                {Math.round(nutrition.fat)}g / {dailyNeeds.fat}g
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

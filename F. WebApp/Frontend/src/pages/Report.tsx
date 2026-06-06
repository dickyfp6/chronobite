import { useState, useMemo } from 'react';
import { motion } from 'motion/react';
import { Download, FileText, BarChart3, List, Lightbulb, User } from 'lucide-react';
import { useI18n } from '../contexts/I18nContext';
import type { UserInputData } from './InputWizard';
import { calculateDailyNeeds } from '../utils/mockData';
import { NutritionChart } from '../components/figma/NutritionChart';
import { getNutrientUnit } from '../utils/nutrientsList';
import { generateNutritionPDF } from '../utils/pdfGenerator';
import html2canvas from 'html2canvas';
import { translations } from '../utils/translations';

interface ReportProps {
  userData: UserInputData;
}

const dietTips = {
  dm2: [
    'Monitor carbohydrate intake and choose complex carbs over simple sugars',
    'Eat regular meals to maintain stable blood sugar levels',
    'Include high-fiber foods to slow glucose absorption',
  ],
  hypertension: [
    'Limit sodium intake to less than 2,300mg per day',
    'Increase potassium-rich foods like bananas and leafy greens',
    'Reduce caffeine and alcohol consumption',
  ],
  cvd: [
    'Choose lean proteins and limit red meat consumption',
    'Include omega-3 fatty acids from fish or supplements',
    'Avoid trans fats and limit saturated fats',
  ],
  cholesterol: [
    'Increase soluble fiber intake through oats, beans, and fruits',
    'Choose healthy fats like olive oil and avocados',
    'Limit dietary cholesterol from animal products',
  ],
  ckd: [
    'Monitor protein intake and choose high-quality protein sources',
    'Limit phosphorus and potassium based on lab results',
    'Control fluid intake as recommended by your healthcare provider',
  ],
};

export function Report({ userData }: ReportProps) {
  const [activeTab, setActiveTab] = useState<number | string>('profile');
  const { t, language } = useI18n();

  const [selectedItems] = useState<Record<string, any>>(() => {
    const saved = sessionStorage.getItem('dss_selected_items');
    return saved ? JSON.parse(saved) : {};
  });

  const [actualNutrients] = useState<any>(() => {
    const saved = sessionStorage.getItem('dss_actual_nutrients');
    return saved ? JSON.parse(saved) : null;
  });

  const getMealItems = (mealName: string) => {
    return Object.keys(selectedItems)
      .filter(key => key.startsWith(`${mealName}_`))
      .map(key => {
        const item = selectedItems[key];
        const category = key.split('_')[1];
        return {
          type: category.toLowerCase(),
          item: item.name || item.food_name,
          portion: `${item.serving_size || item.portion_gram}g`,
        };
      });
  };

  const dailyNeeds = useMemo(
    () =>
      calculateDailyNeeds(
        userData.weight!,
        userData.height!,
        userData.age!,
        userData.gender!,
        userData.activity!
      ),
    [userData]
  );

  const [analysisGuidelines] = useState<any>(() => {
    const saved = sessionStorage.getItem('dss_analysis_guidelines');
    return saved ? JSON.parse(saved) : null;
  });

  const { macroData, microData } = useMemo(() => {
    // 1. Setup base macros
    const macros = [
      {
        nutrient: t.results.protein,
        actual: Math.round(actualNutrients?.protein || dailyNeeds.protein * 0.85),
        min: Math.round(dailyNeeds.protein * 0.8),
        max: Math.round(dailyNeeds.protein * 1.2),
      },
      {
        nutrient: t.results.carbs,
        actual: Math.round(actualNutrients?.carbs || dailyNeeds.carbs * 0.92),
        min: Math.round(dailyNeeds.carbs * 0.85),
        max: Math.round(dailyNeeds.carbs * 1.15),
      },
      {
        nutrient: t.results.fat,
        actual: Math.round(actualNutrients?.fat || dailyNeeds.fat * 0.78),
        min: Math.round(dailyNeeds.fat * 0.7),
        max: Math.round(dailyNeeds.fat * 1.0),
      },
    ];

    const micros: any[] = [];

    if (analysisGuidelines?.nutrients) {
      // 2. Map and inject HARD constraints only (Priority guidelines)
      Object.entries(analysisGuidelines.nutrients).forEach(([key, rule]: [string, any]) => {
        if (rule.hard_soft_type === 'HARD') {
          // If it's a base nutrient, override the min/max accurately from guidelines
          const baseMap: any = {
            'energy_kcal': 'Calories',
            'protein_g': t.results.protein,
            'carbohydrate_g': t.results.carbs,
            'fat_g': t.results.fat
          };
          
          if (baseMap[key]) {
            const mappedName = baseMap[key];
            const existing = macros.find(b => b.nutrient === mappedName);
            if (existing) {
              existing.min = rule.min != null ? Math.round(rule.min) : existing.min;
              existing.max = rule.max != null ? Math.round(rule.max) : Infinity;
            }
          } else {
            // It's a Micronutrient Constraint! (e.g. fiber_g, zinc_mg, sodium_mg)
            const friendlyName = t.nutrients[key as keyof typeof t.nutrients] || key.split('_')[0].toUpperCase();
            const dataPoint = {
              nutrient: friendlyName,
              actual: Math.round(actualNutrients?.[key] || 0),
              min: rule.min != null ? Math.round(rule.min) : 0,
              max: rule.max != null ? Math.round(rule.max) : Infinity,
            };

            // Separate into Macro (g) or Micro (mg/mcg)
            if (key.endsWith('_g')) {
              macros.push(dataPoint);
            } else {
              micros.push(dataPoint);
            }
          }
        }
      });
    } else {
      // Fallback for fiber if no guidelines found
      macros.push({
        nutrient: t.results.fiber,
        actual: Math.round(actualNutrients?.fiber_g || 22),
        min: Math.round(dailyNeeds.fiber * 0.8),
        max: Math.round(dailyNeeds.fiber * 1.2),
      });
    }

    return { macroData: macros, microData: micros };
  }, [dailyNeeds, t, actualNutrients, analysisGuidelines]);

  // Group nutrients by category
  const vitaminNutrients = [
    'vitamin_a_rae_mg',
    'vitamin_b1_thiamin_mg',
    'vitamin_b2_riboflavin_mg',
    'vitamin_b3_niacin_mg',
    'vitamin_b5_pantothenic_acid_mg',
    'vitamin_b6_mg',
    'vitamin_b12_mg',
    'vitamin_c_mg',
    'vitamin_d_mg',
    'vitamin_e_mg',
    'vitamin_k_mg',
  ];

  const mineralNutrients = [
    'calcium_mg',
    'iron_mg',
    'magnesium_mg',
    'phosphorus_mg',
    'potassium_mg',
    'sodium_mg',
    'zinc_mg',
    'copper_mg',
    'manganese_mg',
    'selenium_mg',
    'fluoride_mg',
  ];

  const otherNutrients = [
    'fiber_g',
    'sugar_g',
    'saturated_fat_g',
    'trans_fat_g',
    'cholesterol_mg',
    'choline_mg',
    'folate_mg',
    'water_g',
  ];

  const tabs = [
    { id: 'profile', label: 'Profil', icon: User },
    { id: 0, label: t.report.tabs.menu, icon: FileText },
    { id: 1, label: t.report.tabs.nutrition, icon: BarChart3 },
    { id: 2, label: t.report.tabs.other, icon: List },
    { id: 3, label: t.report.tabs.tips, icon: Lightbulb },
  ];

  const userConditions = userData.healthConditions.filter(c => c !== 'normal');

  const handleDownloadPDF = async () => {
    // Transform meals data for PDF
    const mealsData = [
      {
        meal: t.results.meals.breakfast,
        items: getMealItems('breakfast').map(item => ({
          type: item.type === 'main' ? t.results.meals.mainCourse : item.type === 'drink' ? 'Drink' : t.results.meals.sideDish,
          item: item.item,
          portion: item.portion,
        }))
      },
      {
        meal: t.results.meals.lunch,
        items: getMealItems('lunch').map(item => ({
          type: item.type === 'main' ? t.results.meals.mainCourse : item.type === 'drink' ? 'Drink' : t.results.meals.sideDish,
          item: item.item,
          portion: item.portion,
        }))
      },
      {
        meal: t.results.meals.dinner,
        items: getMealItems('dinner').map(item => ({
          type: item.type === 'main' ? t.results.meals.mainCourse : item.type === 'drink' ? 'Drink' : t.results.meals.sideDish,
          item: item.item,
          portion: item.portion,
        }))
      },
      {
        meal: t.results.meals.snack,
        items: getMealItems('snack').map(item => ({
          type: item.type,
          item: item.item,
          portion: item.portion,
        }))
      }
    ];

    // Calculate actual nutrients
    const actualPDFNutrients = {
      calories: actualNutrients?.calories || Math.round(dailyNeeds.calories * 0.85),
      protein: actualNutrients?.protein || Math.round(dailyNeeds.protein * 0.85),
      carbs: actualNutrients?.carbs || Math.round(dailyNeeds.carbs * 0.92),
      fat: actualNutrients?.fat || Math.round(dailyNeeds.fat * 0.78),
    };

    // Capture charts
    const captureChart = async (id: string) => {
      const el = document.getElementById(id);
      if (!el) return null;
      try {
        const canvas = await html2canvas(el, { scale: 2, logging: false, useCORS: true });
        return canvas.toDataURL('image/png');
      } catch (err) {
        console.error('Error capturing chart', err);
        return null;
      }
    };

    const macroChart = await captureChart('pdf-macro-chart');
    const microChart = microData.length > 0 ? await captureChart('pdf-micro-chart') : null;

    await generateNutritionPDF({
      userName: userData.gender === 'male' ? 'User' : 'User',
      meals: mealsData,
      dailyNeeds,
      nutrients: actualPDFNutrients,
      healthConditions: userConditions,
      dietTips,
      language,
      translations: translations[language],
      charts: {
        macro: macroChart,
        micro: microChart
      }
    });
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] bg-gradient-to-br from-emerald-50 via-green-50 to-teal-50 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900 px-4 py-8">
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8 flex items-center justify-between"
        >
          <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white">{t.report.title}</h1>
          <button
            onClick={handleDownloadPDF}
            className="px-4 py-2 bg-gradient-to-r from-emerald-500 to-teal-500 text-white rounded-lg font-medium hover:from-emerald-600 hover:to-teal-600 transition-all flex items-center gap-2 shadow-md hover:shadow-lg"
          >
            <Download className="w-4 h-4" />
            {t.report.download}
          </button>
        </motion.div>

        <div className="mb-6 bg-white dark:bg-slate-800 rounded-xl border border-gray-200/80 dark:border-slate-700 overflow-hidden shadow-sm">
          <div className="flex overflow-x-auto">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex-1 min-w-[120px] px-6 py-4 font-bold transition-all border-b-4 flex items-center justify-center gap-2 ${
                    activeTab === tab.id
                      ? 'border-emerald-500 text-emerald-700 dark:text-emerald-400 bg-emerald-50/5 dark:bg-emerald-400/5'
                      : 'border-transparent text-gray-600 dark:text-gray-400 hover:text-emerald-700 dark:hover:text-emerald-400 hover:bg-emerald-50/30 dark:hover:bg-emerald-900/10'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span className="hidden sm:inline">{tab.label}</span>
                </button>
              );
            })}
          </div>
        </div>

        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white dark:bg-slate-800 rounded-2xl p-6 sm:p-8 border border-gray-200/80 dark:border-slate-700 shadow-xl shadow-emerald-500/5 dark:shadow-none min-h-[500px]"
        >
          
          {/* Profile Summary Section */}
          {activeTab === 'profile' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-8"
            >
              <div className="flex flex-col md:flex-row md:items-center justify-between pb-6 border-b border-gray-100 dark:border-slate-700 gap-6">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-full bg-emerald-500/10 dark:bg-emerald-400/10 flex items-center justify-center text-emerald-600 dark:text-emerald-400">
                    <User className="w-6 h-6" />
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Profile Summary</h2>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Summary of your personal data and health constraints</p>
                  </div>
                </div>
              </div>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6 py-2">
                <div className="space-y-1">
                  <span className="text-xs font-semibold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider">Gender & Age</span>
                  <p className="text-base font-bold text-gray-900 dark:text-white capitalize">
                    {userData.gender === 'male' ? 'Male' : 'Female'}, {userData.age} yrs
                  </p>
                </div>
                <div className="space-y-1 border-l border-gray-100 dark:border-slate-700 pl-6">
                  <span className="text-xs font-semibold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider">Weight & Height</span>
                  <p className="text-base font-bold text-gray-900 dark:text-white">
                    {userData.weight} kg • {userData.height} cm
                  </p>
                </div>
                <div className="space-y-1 border-l border-gray-100 dark:border-slate-700 pl-6">
                  <span className="text-xs font-semibold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider">Physical Activity</span>
                  <p className="text-base font-bold text-gray-900 dark:text-white capitalize">
                    {userData.activity || 'Moderate'}
                  </p>
                </div>
                <div className="space-y-1 border-l border-gray-100 dark:border-slate-700 pl-6">
                  <span className="text-xs font-semibold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider">Estimated Calories</span>
                  <p className="text-base font-bold text-gray-900 dark:text-white">
                    {Math.round(dailyNeeds.calories)} kcal
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-8 pt-6 border-t border-gray-100 dark:border-slate-700">
                <div className="space-y-3">
                  <h4 className="text-sm font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                    Health Conditions
                  </h4>
                  <div className="flex flex-wrap gap-1.5">
                    {userData.healthConditions.map(c => (
                      <span key={c} className="px-2.5 py-1 bg-emerald-500/10 dark:bg-emerald-400/10 text-emerald-700 dark:text-emerald-300 rounded text-xs font-medium capitalize">
                        {t.input.health[c as keyof typeof t.input.health] || c}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="space-y-3">
                  <h4 className="text-sm font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-teal-500"></span>
                    Food Preferences
                  </h4>
                  <div className="flex flex-wrap gap-1.5">
                    {userData.foodPreferences.length > 0 ? userData.foodPreferences.map(p => (
                      <span key={p} className="px-2.5 py-1 bg-teal-500/10 dark:bg-teal-400/10 text-teal-700 dark:text-teal-300 rounded text-xs font-medium capitalize">
                        {p}
                      </span>
                    )) : (
                      <span className="text-xs text-gray-500 italic">All Cuisines / None</span>
                    )}
                  </div>
                </div>
              </div>

              <div className="pt-6 border-t border-gray-100 dark:border-slate-700">
                <h3 className="text-base font-bold mb-4 text-emerald-800 dark:text-emerald-400 flex items-center gap-2">
                  <span>Hard Constraints</span>
                  <span className="text-xs font-normal text-gray-500 dark:text-gray-400">(Required Nutrient Limits)</span>
                </h3>
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
                  {analysisGuidelines?.nutrients ? (() => {
                    const priorityKeys = ['energy_kcal', 'carbohydrate_g', 'protein_g', 'fat_g'];
                    return Object.entries(analysisGuidelines.nutrients)
                      .filter(([_, rule]: [string, any]) => rule.hard_soft_type === 'HARD')
                      .sort(([keyA], [keyB]) => {
                        const idxA = priorityKeys.indexOf(keyA);
                        const idxB = priorityKeys.indexOf(keyB);
                        if (idxA !== -1 && idxB !== -1) return idxA - idxB;
                        if (idxA !== -1) return -1;
                        if (idxB !== -1) return 1;
                        const nameA = t.nutrients[keyA as keyof typeof t.nutrients] || keyA;
                        const nameB = t.nutrients[keyB as keyof typeof t.nutrients] || keyB;
                        return nameA.localeCompare(nameB);
                      })
                      .map(([key, rule]: [string, any]) => {
                        const friendlyName = t.nutrients[key as keyof typeof t.nutrients] || key.split('_')[0].toUpperCase();
                        const unit = rule.unit || getNutrientUnit(key as any);
                        
                        let rangeText = '';
                        const minVal = rule.min != null ? Math.round(rule.min) : null;
                        const maxVal = rule.max != null && Number.isFinite(rule.max) ? Math.round(rule.max) : null;
                        
                        if (minVal !== null && maxVal !== null) {
                          if (minVal === maxVal) {
                            rangeText = `± ${minVal} ${unit}`;
                          } else {
                            rangeText = `${minVal}-${maxVal} ${unit}`;
                          }
                        } else if (minVal !== null) {
                          rangeText = `min. ${minVal} ${unit}`;
                        } else if (maxVal !== null) {
                          rangeText = `max. ${maxVal} ${unit}`;
                        } else {
                          rangeText = 'No limits';
                        }

                        let cardStyle = 'bg-red-50/70 dark:bg-red-950/20 border-red-150 dark:border-red-900/40';
                        let titleColor = 'text-red-900 dark:text-red-200';
                        let rangeColor = 'text-red-700/80 dark:text-red-300/80';

                        if (key === 'energy_kcal') {
                          cardStyle = 'bg-emerald-600 dark:bg-emerald-700 border-emerald-500 dark:border-emerald-600 text-white';
                          titleColor = 'text-white';
                          rangeColor = 'text-white/90';
                        } else if (['carbohydrate_g', 'protein_g', 'fat_g'].includes(key)) {
                          cardStyle = 'bg-red-600 dark:bg-red-700 border-red-500 dark:border-red-600 text-white';
                          titleColor = 'text-white';
                          rangeColor = 'text-white/90';
                        }

                        return (
                          <div key={key} className={`p-2.5 rounded border shadow-sm flex flex-col justify-center transition-all hover:opacity-95 ${cardStyle}`}>
                            <p className={`font-bold text-xs mb-1 truncate ${titleColor}`} title={friendlyName}>{friendlyName}</p>
                            <p className={`text-[10px] font-medium ${rangeColor}`}>{rangeText}</p>
                          </div>
                        );
                      });
                  })() : (
                    <p className="text-xs text-gray-500 col-span-full italic">No specific hard constraints.</p>
                  )}
                </div>
              </div>
            </motion.div>
          )}

          {/* Meal Menu Section */}
          {activeTab === 0 && (
            <div>
              <h2 className="text-2xl font-bold mb-6 text-gray-900 dark:text-white">{t.report.tabs.menu}</h2>
              <div className="space-y-6">
                {/* Breakfast */}
                <div>
                  <h3 className="text-base font-bold mb-2.5 text-emerald-700 dark:text-emerald-400">Breakfast</h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                    {getMealItems('breakfast').map((item, i) => (
                      <div
                        key={i}
                        className="p-3 bg-slate-50 dark:bg-slate-800/40 hover:bg-slate-100/50 dark:hover:bg-slate-800/80 transition-colors border border-gray-100 dark:border-slate-700/60 rounded-lg flex items-center justify-between shadow-sm"
                      >
                        <div className="flex-1 min-w-0">
                          <p className="text-[10px] text-emerald-600 dark:text-emerald-400 font-bold uppercase tracking-wider mb-0.5">
                            {item.type === 'main' ? 'Main Course' : item.type === 'side' ? 'Side Dish' : item.type}
                          </p>
                          <p className="font-bold text-gray-900 dark:text-white text-sm truncate">{item.item}</p>
                          <p className="text-xs text-gray-500 dark:text-gray-400">{item.portion}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Lunch */}
                <div>
                  <h3 className="text-base font-bold mb-2.5 text-emerald-700 dark:text-emerald-400">Lunch</h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                    {getMealItems('lunch').map((item, i) => (
                      <div
                        key={i}
                        className="p-3 bg-slate-50 dark:bg-slate-800/40 hover:bg-slate-100/50 dark:hover:bg-slate-800/80 transition-colors border border-gray-100 dark:border-slate-700/60 rounded-lg flex items-center justify-between shadow-sm"
                      >
                        <div className="flex-1 min-w-0">
                          <p className="text-[10px] text-emerald-600 dark:text-emerald-400 font-bold uppercase tracking-wider mb-0.5">
                            {item.type === 'main' ? 'Main Course' : item.type === 'side' ? 'Side Dish' : item.type}
                          </p>
                          <p className="font-bold text-gray-900 dark:text-white text-sm truncate">{item.item}</p>
                          <p className="text-xs text-gray-500 dark:text-gray-400">{item.portion}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Dinner */}
                <div>
                  <h3 className="text-base font-bold mb-2.5 text-emerald-700 dark:text-emerald-400">Dinner</h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                    {getMealItems('dinner').map((item, i) => (
                      <div
                        key={i}
                        className="p-3 bg-slate-50 dark:bg-slate-800/40 hover:bg-slate-100/50 dark:hover:bg-slate-800/80 transition-colors border border-gray-100 dark:border-slate-700/60 rounded-lg flex items-center justify-between shadow-sm"
                      >
                        <div className="flex-1 min-w-0">
                          <p className="text-[10px] text-emerald-600 dark:text-emerald-400 font-bold uppercase tracking-wider mb-0.5">
                            {item.type === 'main' ? 'Main Course' : item.type === 'side' ? 'Side Dish' : item.type}
                          </p>
                          <p className="font-bold text-gray-900 dark:text-white text-sm truncate">{item.item}</p>
                          <p className="text-xs text-gray-500 dark:text-gray-400">{item.portion}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Snack */}
                <div>
                  <h3 className="text-base font-bold mb-2.5 text-emerald-700 dark:text-emerald-400">Snack</h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {getMealItems('snack').map((item, i) => (
                      <div
                        key={i}
                        className="p-3 bg-slate-50 dark:bg-slate-800/40 hover:bg-slate-100/50 dark:hover:bg-slate-800/80 transition-colors border border-gray-100 dark:border-slate-700/60 rounded-lg flex items-center justify-between shadow-sm"
                      >
                        <div className="flex-1 min-w-0">
                          <p className="text-[10px] text-emerald-600 dark:text-emerald-400 font-bold uppercase tracking-wider mb-0.5">
                            {item.type === 'main' ? 'Main Course' : item.type === 'side' ? 'Side Dish' : item.type}
                          </p>
                          <p className="font-bold text-gray-900 dark:text-white text-sm truncate">{item.item}</p>
                          <p className="text-xs text-gray-500 dark:text-gray-400">{item.portion}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 1 && (
            <div key={`chart-${language}`}>
              <h2 className="text-2xl font-bold mb-6 text-gray-900 dark:text-white">{t.report.tabs.nutrition}</h2>
              <div className="mb-4 flex flex-wrap items-center gap-6 text-sm">
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 bg-emerald-600 rounded"></div>
                  <span className="text-gray-700 dark:text-gray-300">Actual Value</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-8 h-3 bg-gradient-to-b from-emerald-300/40 to-emerald-200/20 rounded-sm"></div>
                  <span className="text-gray-700 dark:text-gray-300">Safe Range</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-8 h-0.5 border-t-2 border-dashed border-emerald-500"></div>
                  <span className="text-gray-700 dark:text-gray-300">Min/Max Boundary</span>
                </div>
              </div>
              <div className="mb-4">
                <h3 className="text-lg font-bold mb-2 text-emerald-700 dark:text-emerald-400">Macronutrient Balance (g)</h3>
                <NutritionChart data={macroData} />
              </div>
              
              {microData.length > 0 && (
                <div className="mt-8">
                  <h3 className="text-lg font-bold mb-2 text-emerald-700 dark:text-emerald-400">Micronutrient Analysis (mg)</h3>
                  <NutritionChart data={microData} unit="mg" />
                </div>
              )}
            </div>
          )}

          {activeTab === 2 && (
            <div>
              <h2 className="text-2xl font-bold mb-6 text-gray-900 dark:text-white">{t.report.tabs.other}</h2>

              {/* Vitamins Section */}
              <div className="mb-8">
                <h3 className="text-base font-bold mb-3.5 text-emerald-700 dark:text-emerald-400">Vitamins</h3>
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
                  {vitaminNutrients.map((nutrientKey, i) => {
                    const value = dailyNeeds[nutrientKey as keyof typeof dailyNeeds];
                    const unit = getNutrientUnit(nutrientKey as any);
                    const name = t.nutrients[nutrientKey as keyof typeof t.nutrients];
                    const targetVal = Number(value) || 0;
                    const actual = actualNutrients && actualNutrients[nutrientKey] !== undefined
                      ? Math.round(actualNutrients[nutrientKey])
                      : Math.round(targetVal * (0.7 + Math.random() * 0.4));
                    const percentage = targetVal === 0 
                      ? (actual === 0 ? 100 : 0) 
                      : Math.round((actual / targetVal) * 100);

                    return (
                      <div key={i} className="p-3 bg-slate-50 dark:bg-slate-800/40 rounded-lg border border-gray-100 dark:border-slate-700/60 flex flex-col justify-between hover:bg-slate-100/50 dark:hover:bg-slate-800/80 transition-colors shadow-sm">
                        <h4 className="font-semibold text-gray-700 dark:text-gray-300 text-xs mb-1.5 truncate">{name}</h4>
                        <div className="flex items-baseline justify-between gap-1">
                          <span className="text-lg font-extrabold text-emerald-600 dark:text-emerald-400 whitespace-nowrap">
                            {actual}{unit}
                          </span>
                          <span className="text-[10px] text-emerald-600 dark:text-emerald-400 font-bold bg-emerald-500/10 dark:bg-emerald-400/10 px-1.5 py-0.5 rounded shrink-0">{percentage}%</span>
                        </div>
                        <div className="text-[10px] text-gray-400 dark:text-gray-505 mt-1">
                          Target: {value}{unit}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Minerals Section */}
              <div className="mb-8">
                <h3 className="text-base font-bold mb-3.5 text-emerald-700 dark:text-emerald-400">Minerals</h3>
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
                  {mineralNutrients.map((nutrientKey, i) => {
                    const value = dailyNeeds[nutrientKey as keyof typeof dailyNeeds];
                    const unit = getNutrientUnit(nutrientKey as any);
                    const name = t.nutrients[nutrientKey as keyof typeof t.nutrients];
                    const targetVal = Number(value) || 0;
                    const actual = actualNutrients && actualNutrients[nutrientKey] !== undefined
                      ? Math.round(actualNutrients[nutrientKey])
                      : Math.round(targetVal * (0.7 + Math.random() * 0.4));
                    const percentage = targetVal === 0 
                      ? (actual === 0 ? 100 : 0) 
                      : Math.round((actual / targetVal) * 100);

                    return (
                      <div key={i} className="p-3 bg-slate-50 dark:bg-slate-800/40 rounded-lg border border-gray-100 dark:border-slate-700/60 flex flex-col justify-between hover:bg-slate-100/50 dark:hover:bg-slate-800/80 transition-colors shadow-sm">
                        <h4 className="font-semibold text-gray-700 dark:text-gray-300 text-xs mb-1.5 truncate">{name}</h4>
                        <div className="flex items-baseline justify-between gap-1">
                          <span className="text-lg font-extrabold text-emerald-600 dark:text-emerald-400 whitespace-nowrap">
                            {actual}{unit}
                          </span>
                          <span className="text-[10px] text-emerald-600 dark:text-emerald-400 font-bold bg-emerald-500/10 dark:bg-emerald-400/10 px-1.5 py-0.5 rounded shrink-0">{percentage}%</span>
                        </div>
                        <div className="text-[10px] text-gray-400 dark:text-gray-505 mt-1">
                          Target: {value}{unit}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Other Nutrients Section */}
              <div>
                <h3 className="text-base font-bold mb-3.5 text-emerald-700 dark:text-emerald-400">Other Nutrients</h3>
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
                  {otherNutrients.map((nutrientKey, i) => {
                    const value = dailyNeeds[nutrientKey as keyof typeof dailyNeeds];
                    const unit = getNutrientUnit(nutrientKey as any);
                    const name = t.nutrients[nutrientKey as keyof typeof t.nutrients];
                    const targetVal = Number(value) || 0;
                    const actual = actualNutrients && actualNutrients[nutrientKey] !== undefined
                      ? Math.round(actualNutrients[nutrientKey])
                      : Math.round(targetVal * (0.7 + Math.random() * 0.4));
                    const percentage = targetVal === 0 
                      ? (actual === 0 ? 100 : 0) 
                      : Math.round((actual / targetVal) * 100);

                    return (
                      <div key={i} className="p-3 bg-slate-50 dark:bg-slate-800/40 rounded-lg border border-gray-100 dark:border-slate-700/60 flex flex-col justify-between hover:bg-slate-100/50 dark:hover:bg-slate-800/80 transition-colors shadow-sm">
                        <h4 className="font-semibold text-gray-700 dark:text-gray-300 text-xs mb-1.5 truncate">{name}</h4>
                        <div className="flex items-baseline justify-between gap-1">
                          <span className="text-lg font-extrabold text-emerald-600 dark:text-emerald-400 whitespace-nowrap">
                            {actual}{unit}
                          </span>
                          <span className="text-[10px] text-emerald-600 dark:text-emerald-400 font-bold bg-emerald-500/10 dark:bg-emerald-400/10 px-1.5 py-0.5 rounded shrink-0">{percentage}%</span>
                        </div>
                        <div className="text-[10px] text-gray-400 dark:text-gray-505 mt-1">
                          Target: {value}{unit}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          )}

          {activeTab === 3 && (
            <div>
              <h2 className="text-2xl font-bold mb-6 text-gray-900 dark:text-white">{t.report.tabs.tips}</h2>
              <div className="space-y-4">
                {userConditions.length > 0 ? (
                  userConditions.map((condition) => (
                    <div key={condition} className="p-5 bg-slate-50 dark:bg-slate-800/40 rounded-lg border border-gray-100 dark:border-slate-700/60">
                      <h3 className="font-bold text-base mb-2.5 text-emerald-700 dark:text-emerald-300">
                        {t.input.health[condition as keyof typeof t.input.health]}
                      </h3>
                      <ul className="space-y-2">
                        {dietTips[condition as keyof typeof dietTips].map((tip, i) => (
                          <li key={i} className="flex items-start gap-2 text-sm text-gray-700 dark:text-gray-300">
                            <span className="text-emerald-600 dark:text-emerald-400 font-bold">•</span>
                            <span className="flex-1">{tip}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  ))
                ) : (
                  <div className="p-6 bg-slate-50 dark:bg-slate-800/40 rounded-lg text-center text-sm text-emerald-700 dark:text-emerald-300 border border-gray-100 dark:border-slate-700/60">
                    No specific health conditions selected. Maintain a balanced diet with variety.
                  </div>
                )}
              </div>
            </div>
          )}
        </motion.div>
      </div>

      {/* Hidden charts for PDF export */}
      <div style={{ position: 'absolute', top: '-9999px', left: '-9999px', pointerEvents: 'none', opacity: 0 }}>
        <div id="pdf-export-container" style={{ width: '800px', backgroundColor: 'white', padding: '20px' }}>
          <div id="pdf-macro-chart" style={{ width: '800px', height: '400px' }}>
            <NutritionChart data={macroData} />
          </div>
          {microData.length > 0 && (
            <div id="pdf-micro-chart" style={{ width: '800px', height: '400px' }}>
              <NutritionChart data={microData} unit="mg" />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

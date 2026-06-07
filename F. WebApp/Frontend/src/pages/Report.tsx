import { useState, useMemo, useEffect } from 'react';
import { motion } from 'motion/react';
import { FileText, BarChart3, List, Lightbulb, User } from 'lucide-react';
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
  onRegisterDownloadPDF?: (fn: (() => void) | null) => void;
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

export function Report({ userData, onRegisterDownloadPDF }: ReportProps) {
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
    { id: 'profile', label: 'Profile', icon: User },
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
      userData: {
        gender: userData.gender,
        age: userData.age,
        weight: userData.weight,
        height: userData.height,
        activity: userData.activity,
        foodPreferences: userData.foodPreferences,
      },
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

  useEffect(() => {
    if (onRegisterDownloadPDF) {
      onRegisterDownloadPDF(() => handleDownloadPDF);
    }
    return () => {
      if (onRegisterDownloadPDF) onRegisterDownloadPDF(null);
    };
  }, [onRegisterDownloadPDF, handleDownloadPDF]);

  return (
    <div className="w-full font-sans">
        <div className="mb-6 bg-white/70 dark:bg-slate-800/40 backdrop-blur-md rounded-3xl border border-border/80 dark:border-slate-850/30 overflow-hidden shadow-xl shadow-primary/5 dark:shadow-none">
          <div className="flex overflow-x-auto">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex-1 min-w-[120px] px-6 py-4 font-semibold text-sm transition-all border-b-4 flex items-center justify-center gap-2 cursor-pointer font-sans ${
                    activeTab === tab.id
                      ? 'border-primary text-primary dark:text-emerald-450 bg-primary/5 dark:bg-primary/10'
                      : 'border-transparent text-gray-600 dark:text-gray-400 hover:text-primary dark:hover:text-emerald-450 hover:bg-secondary/30 dark:hover:bg-slate-800/20'
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
          className="bg-white/70 dark:bg-slate-800/40 backdrop-blur-md rounded-3xl p-6 sm:p-8 border border-border/80 dark:border-slate-850/30 shadow-xl shadow-primary/5 dark:shadow-none min-h-[500px]"
        >
          
          {/* Profile Summary Section */}
          {activeTab === 'profile' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-8"
            >
              <div className="flex flex-col md:flex-row md:items-center justify-between pb-6 border-b border-border dark:border-slate-800 gap-6">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-full bg-primary/10 text-primary dark:bg-emerald-950/40 dark:text-emerald-450 flex items-center justify-center">
                    <User className="w-6 h-6" />
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900 dark:text-white font-serif tracking-tight">Profile Summary</h2>
                    <p className="text-sm text-gray-500 dark:text-gray-400 font-sans">Summary of your personal data and health constraints</p>
                  </div>
                </div>
              </div>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6 py-2 font-sans">
                <div className="space-y-1">
                  <span className="text-xs font-bold text-primary dark:text-emerald-450 uppercase tracking-wider">Gender & Age</span>
                  <p className="text-base font-bold text-gray-900 dark:text-white capitalize font-serif">
                    {userData.gender === 'male' ? 'Male' : 'Female'}, {userData.age} yrs
                  </p>
                </div>
                <div className="space-y-1 border-l border-border dark:border-slate-800 pl-6">
                  <span className="text-xs font-bold text-primary dark:text-emerald-450 uppercase tracking-wider">Weight & Height</span>
                  <p className="text-base font-bold text-gray-900 dark:text-white font-serif">
                    {userData.weight} kg • {userData.height} cm
                  </p>
                </div>
                <div className="space-y-1 border-l border-border dark:border-slate-800 pl-6">
                  <span className="text-xs font-bold text-primary dark:text-emerald-450 uppercase tracking-wider">Physical Activity</span>
                  <p className="text-base font-bold text-gray-900 dark:text-white capitalize font-serif">
                    {userData.activity || 'Moderate'}
                  </p>
                </div>
                <div className="space-y-1 border-l border-border dark:border-slate-800 pl-6">
                  <span className="text-xs font-bold text-primary dark:text-emerald-450 uppercase tracking-wider">Estimated Calories</span>
                  <p className="text-base font-bold text-gray-900 dark:text-white font-serif">
                    {Math.round(dailyNeeds.calories)} kcal
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-8 pt-6 border-t border-border dark:border-slate-800 font-sans">
                <div className="space-y-3">
                  <h4 className="text-sm font-bold text-gray-900 dark:text-white flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-primary"></span>
                    Health Conditions
                  </h4>
                  <div className="flex flex-wrap gap-1.5">
                    {userData.healthConditions.map(c => (
                      <span key={c} className="px-3 py-1 bg-primary/10 text-primary dark:text-emerald-350 border border-primary/20 dark:border-primary/10 rounded-xl text-xs font-semibold capitalize font-sans">
                        {t.input.health[c as keyof typeof t.input.health] || c}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="space-y-3">
                  <h4 className="text-sm font-bold text-gray-900 dark:text-white flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-accent"></span>
                    Food Preferences
                  </h4>
                  <div className="flex flex-wrap gap-1.5">
                    {userData.foodPreferences.length > 0 ? userData.foodPreferences.map(p => (
                      <span key={p} className="px-3 py-1 bg-accent/15 text-accent dark:text-emerald-300 border border-accent/20 dark:border-accent/10 rounded-xl text-xs font-semibold capitalize font-sans">
                        {p}
                      </span>
                    )) : (
                      <span className="text-xs text-gray-500 italic">All Cuisines / None</span>
                    )}
                  </div>
                </div>
              </div>

              <div className="pt-6 border-t border-border dark:border-slate-800">
                <h3 className="text-base font-bold mb-4 text-primary dark:text-emerald-450 flex items-center gap-2 font-serif">
                  <span>Hard Constraints</span>
                  <span className="text-xs font-normal text-gray-500 dark:text-gray-400 font-sans">(Required Nutrient Limits)</span>
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

                        let cardStyle = 'rounded-2xl p-3 border bg-white/40 dark:bg-slate-950/20 border-border/85 dark:border-slate-800/80 shadow-sm';
                        let titleColor = 'text-gray-900 dark:text-white';
                        let rangeColor = 'text-gray-500 dark:text-gray-400';

                        if (key === 'energy_kcal') {
                          cardStyle = 'rounded-2xl p-3 border bg-primary text-primary-foreground border-primary/20 shadow-sm';
                          titleColor = 'text-primary-foreground';
                          rangeColor = 'text-primary-foreground/90';
                        } else if (['carbohydrate_g', 'protein_g', 'fat_g'].includes(key)) {
                          cardStyle = 'rounded-2xl p-3 border bg-secondary dark:bg-slate-900/60 text-secondary-foreground dark:text-emerald-350 border-border/80 dark:border-slate-800';
                          titleColor = 'text-secondary-foreground dark:text-emerald-350';
                          rangeColor = 'text-secondary-foreground/80 dark:text-emerald-400/80';
                        } else {
                          cardStyle = 'rounded-2xl p-3 border bg-red-500/10 dark:bg-red-950/25 border-red-500/20 dark:border-red-900/30';
                          titleColor = 'text-red-950 dark:text-red-300';
                          rangeColor = 'text-red-800/80 dark:text-red-450/80';
                        }

                        return (
                          <div key={key} className={`flex flex-col justify-center transition-all hover:opacity-95 font-sans ${cardStyle}`}>
                            <p className={`font-bold text-xs mb-1 truncate ${titleColor}`} title={friendlyName}>{friendlyName}</p>
                            <p className={`text-[10px] font-medium font-serif ${rangeColor}`}>{rangeText}</p>
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
              <h2 className="text-2xl font-bold mb-6 text-gray-900 dark:text-white font-serif tracking-tight">{t.report.tabs.menu}</h2>
              <div className="space-y-6">
                {/* Breakfast */}
                <div>
                  <h3 className="text-base font-bold mb-2.5 text-primary dark:text-emerald-450 font-serif">Breakfast</h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                    {getMealItems('breakfast').map((item, i) => (
                      <div
                        key={i}
                        className="p-4 bg-white/50 dark:bg-slate-900/40 hover:bg-secondary/40 dark:hover:bg-slate-800/60 transition-colors border border-border/80 dark:border-slate-800/60 rounded-2xl flex items-center justify-between shadow-sm shadow-primary/5 dark:shadow-none font-sans"
                      >
                        <div className="flex-1 min-w-0">
                          <p className="text-[10px] text-primary dark:text-emerald-450 font-bold uppercase tracking-wider mb-0.5">
                            {item.type === 'main' ? 'Main Course' : item.type === 'side' ? 'Side Dish' : item.type}
                          </p>
                          <p className="font-bold text-gray-900 dark:text-white text-sm truncate">{item.item}</p>
                          <p className="text-xs text-gray-500 dark:text-gray-400 font-medium">{item.portion}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Lunch */}
                <div>
                  <h3 className="text-base font-bold mb-2.5 text-primary dark:text-emerald-450 font-serif">Lunch</h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                    {getMealItems('lunch').map((item, i) => (
                      <div
                        key={i}
                        className="p-4 bg-white/50 dark:bg-slate-900/40 hover:bg-secondary/40 dark:hover:bg-slate-800/60 transition-colors border border-border/80 dark:border-slate-800/60 rounded-2xl flex items-center justify-between shadow-sm shadow-primary/5 dark:shadow-none font-sans"
                      >
                        <div className="flex-1 min-w-0">
                          <p className="text-[10px] text-primary dark:text-emerald-450 font-bold uppercase tracking-wider mb-0.5">
                            {item.type === 'main' ? 'Main Course' : item.type === 'side' ? 'Side Dish' : item.type}
                          </p>
                          <p className="font-bold text-gray-900 dark:text-white text-sm truncate">{item.item}</p>
                          <p className="text-xs text-gray-500 dark:text-gray-400 font-medium">{item.portion}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Dinner */}
                <div>
                  <h3 className="text-base font-bold mb-2.5 text-primary dark:text-emerald-450 font-serif">Dinner</h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                    {getMealItems('dinner').map((item, i) => (
                      <div
                        key={i}
                        className="p-4 bg-white/50 dark:bg-slate-900/40 hover:bg-secondary/40 dark:hover:bg-slate-800/60 transition-colors border border-border/80 dark:border-slate-800/60 rounded-2xl flex items-center justify-between shadow-sm shadow-primary/5 dark:shadow-none font-sans"
                      >
                        <div className="flex-1 min-w-0">
                          <p className="text-[10px] text-primary dark:text-emerald-450 font-bold uppercase tracking-wider mb-0.5">
                            {item.type === 'main' ? 'Main Course' : item.type === 'side' ? 'Side Dish' : item.type}
                          </p>
                          <p className="font-bold text-gray-900 dark:text-white text-sm truncate">{item.item}</p>
                          <p className="text-xs text-gray-500 dark:text-gray-400 font-medium">{item.portion}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Snack */}
                <div>
                  <h3 className="text-base font-bold mb-2.5 text-primary dark:text-emerald-450 font-serif">Snack</h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {getMealItems('snack').map((item, i) => (
                      <div
                        key={i}
                        className="p-4 bg-white/50 dark:bg-slate-900/40 hover:bg-secondary/40 dark:hover:bg-slate-800/60 transition-colors border border-border/80 dark:border-slate-800/60 rounded-2xl flex items-center justify-between shadow-sm shadow-primary/5 dark:shadow-none font-sans"
                      >
                        <div className="flex-1 min-w-0">
                          <p className="text-[10px] text-primary dark:text-emerald-450 font-bold uppercase tracking-wider mb-0.5">
                            {item.type === 'main' ? 'Main Course' : item.type === 'side' ? 'Side Dish' : item.type}
                          </p>
                          <p className="font-bold text-gray-900 dark:text-white text-sm truncate">{item.item}</p>
                          <p className="text-xs text-gray-500 dark:text-gray-400 font-medium">{item.portion}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 1 && (
            <div key={`chart-${language}`} className="font-sans">
              <h2 className="text-2xl font-bold mb-6 text-gray-900 dark:text-white font-serif tracking-tight">{t.report.tabs.nutrition}</h2>
              <div className="mb-4 flex flex-wrap items-center gap-6 text-sm">
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 bg-primary rounded"></div>
                  <span className="text-gray-700 dark:text-gray-300">Actual Value</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-8 h-3 bg-gradient-to-b from-primary/40 to-secondary/20 rounded-sm"></div>
                  <span className="text-gray-700 dark:text-gray-300">Safe Range</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-8 h-0.5 border-t-2 border-dashed border-primary"></div>
                  <span className="text-gray-700 dark:text-gray-300">Min/Max Boundary</span>
                </div>
              </div>
              <div className="mb-4">
                <h3 className="text-lg font-bold mb-2 text-primary dark:text-emerald-450 font-serif">Macronutrient Balance (g)</h3>
                <NutritionChart data={macroData} />
              </div>
              
              {microData.length > 0 && (
                <div className="mt-8">
                  <h3 className="text-lg font-bold mb-2 text-primary dark:text-emerald-450 font-serif">Micronutrient Analysis (mg)</h3>
                  <NutritionChart data={microData} unit="mg" />
                </div>
              )}
            </div>
          )}
          {activeTab === 2 && (
            <div>
              <h2 className="text-2xl font-bold mb-6 text-gray-900 dark:text-white font-serif tracking-tight">{t.report.tabs.other}</h2>

              {/* Helper for nutrient coloring/status */}
              {(() => {
                const getNutrientStatus = (percentage: number) => {
                  const isId = (language as string) === 'id';
                  if (percentage < 100) {
                    return {
                      label: isId ? 'Kurang Asupan' : 'Deficient',
                      showBadge: true,
                      priority: 1, // Red
                      cardBg: 'bg-red-50/70 dark:bg-red-950/20 border-red-200/50 dark:border-red-900/40',
                      badgeBg: 'bg-red-500/10 text-red-600 dark:text-red-400',
                      textColor: 'text-red-700 dark:text-red-400',
                      titleColor: 'text-red-900 dark:text-red-200'
                    };
                  } else if (percentage <= 200) {
                    return {
                      label: isId ? 'Cukup' : 'Optimal',
                      showBadge: false, // Green styling/badge not needed
                      priority: 3, // Green (neutral style)
                      cardBg: 'bg-white/40 dark:bg-slate-950/20 border-border/80 dark:border-slate-800/80',
                      badgeBg: '',
                      textColor: 'text-gray-800 dark:text-gray-200',
                      titleColor: 'text-gray-900 dark:text-white'
                    };
                  } else {
                    return {
                      label: isId ? 'Berlebih' : 'Excessive',
                      showBadge: true,
                      priority: 2, // Yellow
                      cardBg: 'bg-amber-50/60 dark:bg-amber-950/20 border-amber-200/50 dark:border-amber-900/40',
                      badgeBg: 'bg-amber-500/10 text-amber-600 dark:text-amber-450',
                      textColor: 'text-amber-700 dark:text-amber-400',
                      titleColor: 'text-amber-900 dark:text-amber-200'
                    };
                  }
                };

                return (
                  <>
                    {/* Vitamins Section */}
                    <div className="mb-8">
                      <h3 className="text-base font-bold mb-3.5 text-primary dark:text-emerald-450 font-serif">Vitamins</h3>
                      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
                        {(() => {
                          const mapped = vitaminNutrients.map((nutrientKey) => {
                            const value = dailyNeeds[nutrientKey as keyof typeof dailyNeeds];
                            const unit = getNutrientUnit(nutrientKey as any);
                            const name = t.nutrients[nutrientKey as keyof typeof t.nutrients];
                            const targetVal = Number(value) || 0;
                            const actual = actualNutrients && actualNutrients[nutrientKey] !== undefined
                              ? Math.round(actualNutrients[nutrientKey])
                              : Math.round(targetVal * (0.7 + Math.random() * 0.4));
                            const percentage = targetVal === 0 
                              ? (actual === 0 ? 100 : 999) 
                              : Math.round((actual / targetVal) * 100);
                            const status = getNutrientStatus(percentage);
                            return { nutrientKey, value, unit, name, actual, percentage, status };
                          });

                          mapped.sort((a, b) => a.status.priority - b.status.priority);

                          return mapped.map((item, index) => (
                            <div key={index} className={`p-3.5 rounded-2xl border flex flex-col justify-between hover:opacity-95 transition-all shadow-sm font-sans ${item.status.cardBg}`}>
                              <div>
                                <div className="flex justify-between items-start gap-1.5 mb-2.5">
                                  <h4 className={`font-semibold text-xs truncate ${item.status.titleColor}`} title={item.name}>{item.name}</h4>
                                  {item.status.showBadge && (
                                    <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded shrink-0 ${item.status.badgeBg}`}>
                                      {item.status.label}
                                    </span>
                                  )}
                                </div>
                                <div className="flex items-end justify-between">
                                  <div className="flex items-baseline">
                                    <span className={`text-sm font-bold ${item.status.textColor}`}>
                                      {item.actual}{item.unit}
                                    </span>
                                    <span className="text-[10px] font-light text-gray-400 dark:text-gray-500 ml-1">
                                      / {item.value}{item.unit}
                                    </span>
                                  </div>
                                  <span className="text-[10px] text-gray-400 dark:text-gray-500 font-bold">{item.percentage}%</span>
                                </div>
                              </div>
                            </div>
                          ));
                        })()}
                      </div>
                    </div>

                    {/* Minerals Section */}
                    <div className="mb-8">
                      <h3 className="text-base font-bold mb-3.5 text-primary dark:text-emerald-450 font-serif">Minerals</h3>
                      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
                        {(() => {
                          const mapped = mineralNutrients.map((nutrientKey) => {
                            const value = dailyNeeds[nutrientKey as keyof typeof dailyNeeds];
                            const unit = getNutrientUnit(nutrientKey as any);
                            const name = t.nutrients[nutrientKey as keyof typeof t.nutrients];
                            const targetVal = Number(value) || 0;
                            const actual = actualNutrients && actualNutrients[nutrientKey] !== undefined
                              ? Math.round(actualNutrients[nutrientKey])
                              : Math.round(targetVal * (0.7 + Math.random() * 0.4));
                            const percentage = targetVal === 0 
                              ? (actual === 0 ? 100 : 999) 
                              : Math.round((actual / targetVal) * 100);
                            const status = getNutrientStatus(percentage);
                            return { nutrientKey, value, unit, name, actual, percentage, status };
                          });

                          mapped.sort((a, b) => a.status.priority - b.status.priority);

                          return mapped.map((item, index) => (
                            <div key={index} className={`p-3.5 rounded-2xl border flex flex-col justify-between hover:opacity-95 transition-all shadow-sm font-sans ${item.status.cardBg}`}>
                              <div>
                                <div className="flex justify-between items-start gap-1.5 mb-2.5">
                                  <h4 className={`font-semibold text-xs truncate ${item.status.titleColor}`} title={item.name}>{item.name}</h4>
                                  {item.status.showBadge && (
                                    <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded shrink-0 ${item.status.badgeBg}`}>
                                      {item.status.label}
                                    </span>
                                  )}
                                </div>
                                <div className="flex items-end justify-between">
                                  <div className="flex items-baseline">
                                    <span className={`text-sm font-bold ${item.status.textColor}`}>
                                      {item.actual}{item.unit}
                                    </span>
                                    <span className="text-[10px] font-light text-gray-400 dark:text-gray-500 ml-1">
                                      / {item.value}{item.unit}
                                    </span>
                                  </div>
                                  <span className="text-[10px] text-gray-400 dark:text-gray-500 font-bold">{item.percentage}%</span>
                                </div>
                              </div>
                            </div>
                          ));
                        })()}
                      </div>
                    </div>

                    {/* Other Nutrients Section */}
                    <div>
                      <h3 className="text-base font-bold mb-3.5 text-primary dark:text-emerald-450 font-serif">Other Nutrients</h3>
                      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
                        {(() => {
                          const mapped = otherNutrients.map((nutrientKey) => {
                            const value = dailyNeeds[nutrientKey as keyof typeof dailyNeeds];
                            const unit = getNutrientUnit(nutrientKey as any);
                            const name = t.nutrients[nutrientKey as keyof typeof t.nutrients];
                            const targetVal = Number(value) || 0;
                            const actual = actualNutrients && actualNutrients[nutrientKey] !== undefined
                              ? Math.round(actualNutrients[nutrientKey])
                              : Math.round(targetVal * (0.7 + Math.random() * 0.4));
                            const percentage = targetVal === 0 
                              ? (actual === 0 ? 100 : 999) 
                              : Math.round((actual / targetVal) * 100);
                            const status = getNutrientStatus(percentage);
                            return { nutrientKey, value, unit, name, actual, percentage, status };
                          });

                          mapped.sort((a, b) => a.status.priority - b.status.priority);

                          return mapped.map((item, index) => (
                            <div key={index} className={`p-3.5 rounded-2xl border flex flex-col justify-between hover:opacity-95 transition-all shadow-sm font-sans ${item.status.cardBg}`}>
                              <div>
                                <div className="flex justify-between items-start gap-1.5 mb-2.5">
                                  <h4 className={`font-semibold text-xs truncate ${item.status.titleColor}`} title={item.name}>{item.name}</h4>
                                  {item.status.showBadge && (
                                    <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded shrink-0 ${item.status.badgeBg}`}>
                                      {item.status.label}
                                    </span>
                                  )}
                                </div>
                                <div className="flex items-end justify-between">
                                  <div className="flex items-baseline">
                                    <span className={`text-sm font-bold ${item.status.textColor}`}>
                                      {item.actual}{item.unit}
                                    </span>
                                    <span className="text-[10px] font-light text-gray-400 dark:text-gray-500 ml-1">
                                      / {item.value}{item.unit}
                                    </span>
                                  </div>
                                  <span className="text-[10px] text-gray-400 dark:text-gray-500 font-bold">{item.percentage}%</span>
                                </div>
                              </div>
                            </div>
                          ));
                        })()}
                      </div>
                    </div>
                  </>
                );
              })()}
            </div>
          )}

          {activeTab === 3 && (
            <div>
              <h2 className="text-2xl font-bold mb-6 text-gray-900 dark:text-white font-serif tracking-tight">{t.report.tabs.tips}</h2>
              <div className="space-y-4 font-sans">
                {userConditions.length > 0 ? (
                  userConditions.map((condition) => (
                    <div key={condition} className="p-5 bg-white/50 dark:bg-slate-900/40 rounded-2xl border border-border/80 dark:border-slate-800/60 shadow-sm shadow-primary/5 dark:shadow-none">
                      <h3 className="font-bold text-base mb-2.5 text-primary dark:text-emerald-350 font-serif">
                        {t.input.health[condition as keyof typeof t.input.health]}
                      </h3>
                      <ul className="space-y-2">
                        {dietTips[condition as keyof typeof dietTips].map((tip, i) => (
                          <li key={i} className="flex items-start gap-2 text-sm text-gray-700 dark:text-gray-300">
                            <span className="text-primary dark:text-emerald-450 font-bold">•</span>
                            <span className="flex-1">{tip}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  ))
                ) : (
                  <div className="p-6 bg-white/50 dark:bg-slate-900/40 rounded-2xl text-center text-sm text-primary dark:text-emerald-350 border border-border/80 dark:border-slate-800/60 shadow-sm">
                    No specific health conditions selected. Maintain a balanced diet with variety.
                  </div>
                )}
              </div>
            </div>
          )}
        </motion.div>

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

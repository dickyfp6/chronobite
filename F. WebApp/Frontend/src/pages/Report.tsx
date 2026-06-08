import { useState, useMemo, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
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
    'Consume at least 400 g of fruits and vegetables daily.',
    'Choose foods rich in fiber to support blood sugar control.',
    'Avoid sugary beverages and limit added sugar intake.',
    'Select lean protein sources such as fish, beans, and legumes.',
    'Prefer grilled, steamed, or boiled foods instead of fried foods.',
    'Drink sufficient water and choose unsweetened beverages.',
  ],
  hypertension: [
    'Limit sodium intake to less than 2,300mg per day.',
    'Include potassium-rich foods such as fruits, vegetables, and legumes.',
    'Choose fat-free or low-fat milk and dairy products.',
    'Limit processed, smoked, cured, and canned foods that are high in sodium.',
    'Choose whole grain foods for most grain servings.',
  ],
  cvd: [
    'Consume a diet rich in vegetables and fruits.',
    'Choose whole-grain, high-fiber foods.',
    'Consume fish, especially oily fish, at least twice a week.',
    'Choose lean meats and plant-based protein alternatives.',
    'Minimize foods with added sugars and excessive salt.',
  ],
  cholesterol: [
    'Reduce foods high in saturated fat such as fatty meats and full-fat dairy products.',
    'Limit dietary cholesterol intake.',
    'Eat more soluble fiber from oats, fruits, and legumes.',
    'Include plant sterols and stanols in your daily diet.',
    'Replace saturated fats with healthier unsaturated fats.',
  ],
  ckd: [
    'Avoid excessive protein intake.',
    'Limit sodium and processed foods.',
    'Maintain fluid intake of approximately 30–35 mL/kg body weight per day.',
    'If edema is present, fluid intake may need to be restricted.',
    'Monitor potassium and phosphorus intake as recommended.',

  ],
};

// Group nutrients by category statically to optimize renders
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

export function Report({ userData, onRegisterDownloadPDF }: ReportProps) {
  const [activeTab, setActiveTab] = useState<number | string>('profile');
  const { t, language } = useI18n();

  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isPreviewModalOpen, setIsPreviewModalOpen] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);

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
    const items = Object.values(selectedItems);
    const totalProtein = items.reduce((sum, item) => sum + (item.protein || 0), 0);
    const totalCarbs = items.reduce((sum, item) => sum + (item.carbs || 0), 0);
    const totalFat = items.reduce((sum, item) => sum + (item.fat || 0), 0);

    // 1. Setup base macros
    const macros = [
      {
        nutrient: t.results.carbs,
        actual: Math.round(totalCarbs),
        min: Math.round(dailyNeeds.carbs * 0.85),
        max: Math.round(dailyNeeds.carbs * 1.15),
        diseases: [] as string[],
        basis: 'DRI',
        source: 'DRI fallback'
      },
      {
        nutrient: t.results.protein,
        actual: Math.round(totalProtein),
        min: Math.round(dailyNeeds.protein * 0.8),
        max: Math.round(dailyNeeds.protein * 1.2),
        diseases: [] as string[],
        basis: 'DRI',
        source: 'DRI fallback'
      },
      {
        nutrient: t.results.fat,
        actual: Math.round(totalFat),
        min: Math.round(dailyNeeds.fat * 0.7),
        max: Math.round(dailyNeeds.fat * 1.0),
        diseases: [] as string[],
        basis: 'DRI',
        source: 'DRI fallback'
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
              existing.diseases = rule.diseases || [];
              existing.basis = rule.basis || '1';
              existing.source = rule.source || 'guideline';
            }
          } else {
            // It's a Micronutrient Constraint! (e.g. fiber_g, zinc_mg, sodium_mg)
            const friendlyName = t.nutrients[key as keyof typeof t.nutrients] || key.split('_')[0].toUpperCase();
            
            let unit = rule.unit || 'mg';
            const keyLower = key.toLowerCase();
            const isMicro = keyLower.includes('b12') || keyLower.includes('mcg') || keyLower.includes('ug') || keyLower.includes('μg');
            if (isMicro) {
              unit = 'mcg';
            }

            const scaleAndRound = (val: any) => {
              if (val === null || val === undefined || typeof val !== 'number' || !Number.isFinite(val)) return val;
              const factor = isMicro ? 1000 : 1;
              return Math.round(val * factor * 10) / 10;
            };

            const dataPoint = {
              nutrient: friendlyName,
              actual: scaleAndRound(actualNutrients?.[key] || 0),
              min: rule.min != null ? scaleAndRound(rule.min) : 0,
              max: rule.max != null ? scaleAndRound(rule.max) : Infinity,
              diseases: rule.diseases || [],
              basis: rule.basis || '1',
              source: rule.source || 'guideline',
              unit: unit
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
        diseases: [] as string[],
        basis: 'DRI',
        source: 'DRI fallback'
      });
    }

    return { macroData: macros, microData: micros };
  }, [dailyNeeds, t, actualNutrients, analysisGuidelines, selectedItems]);

  // Collect nutrient deficiency/excess warnings dynamically
  const nutritionalWarnings = useMemo(() => {
    const warnings: { message: string; type: 'deficient' | 'excessive'; nutrient: string }[] = [];
    const isId = (language as string) === 'id';

    const checkNutrient = (key: string, name: string, actualValue: number, minVal: number | null, maxVal: number | null, unit: string) => {
      if (minVal !== null && actualValue < minVal) {
        const diff = Math.round(minVal - actualValue);
        const msg = isId
          ? `Asupan ${name} kurang dari rentang rekomendasi. Anda membutuhkan tambahan ${diff}${unit} untuk mencapai target minimum ${Math.round(minVal)}${unit}.`
          : `${name} intake is below the recommended range. You need an additional ${diff}${unit} to reach the minimum target of ${Math.round(minVal)}${unit}.`;
        warnings.push({ message: msg, type: 'deficient', nutrient: key });
      } else if (maxVal !== null && maxVal !== Infinity && actualValue > maxVal) {
        const diff = Math.round(actualValue - maxVal);
        const msg = isId
          ? `Asupan ${name} melebihi rentang rekomendasi. Batasi/kurangi ${name} sebesar ${diff}${unit} agar berada di bawah batas maksimum ${Math.round(maxVal)}${unit}.`
          : `${name} intake is above the recommended range. Try to reduce ${name} by ${diff}${unit} to stay below the maximum target of ${Math.round(maxVal)}${unit}.`;
        warnings.push({ message: msg, type: 'excessive', nutrient: key });
      }
    };

    const items = Object.values(selectedItems);
    const totalProtein = items.reduce((sum: number, item: any) => sum + (item.protein || 0), 0);
    const totalCarbs = items.reduce((sum: number, item: any) => sum + (item.carbs || 0), 0);
    const totalFat = items.reduce((sum: number, item: any) => sum + (item.fat || 0), 0);

    let carbMin = dailyNeeds.carbs * 0.85;
    let carbMax = dailyNeeds.carbs * 1.15;
    let proteinMin = dailyNeeds.protein * 0.8;
    let proteinMax = dailyNeeds.protein * 1.2;
    let fatMin = dailyNeeds.fat * 0.7;
    let fatMax = dailyNeeds.fat * 1.0;

    if (analysisGuidelines?.nutrients) {
      const g = analysisGuidelines.nutrients;
      if (g.carbohydrate_g) {
        carbMin = g.carbohydrate_g.min != null ? g.carbohydrate_g.min : carbMin;
        carbMax = g.carbohydrate_g.max != null ? g.carbohydrate_g.max : carbMax;
      }
      if (g.protein_g) {
        proteinMin = g.protein_g.min != null ? g.protein_g.min : proteinMin;
        proteinMax = g.protein_g.max != null ? g.protein_g.max : proteinMax;
      }
      if (g.fat_g) {
        fatMin = g.fat_g.min != null ? g.fat_g.min : fatMin;
        fatMax = g.fat_g.max != null ? g.fat_g.max : fatMax;
      }
    }

    checkNutrient('carbohydrate_g', t.results.carbs, totalCarbs, carbMin, carbMax, 'g');
    checkNutrient('protein_g', t.results.protein, totalProtein, proteinMin, proteinMax, 'g');
    checkNutrient('fat_g', t.results.fat, totalFat, fatMin, fatMax, 'g');

    const allCheckKeys = [...vitaminNutrients, ...mineralNutrients, ...otherNutrients];
    allCheckKeys.forEach(key => {
      const rule = analysisGuidelines?.nutrients?.[key];
      const unit = getNutrientUnit(key as any);
      const name = t.nutrients[key as keyof typeof t.nutrients] || key.split('_')[0].toUpperCase();

      const staticVal = Number(dailyNeeds[key as keyof typeof dailyNeeds]) || 0;
      const actual = actualNutrients && actualNutrients[key] !== undefined
        ? actualNutrients[key]
        : staticVal * 0.9;

      if (rule) {
        const minVal = rule.min != null ? Number(rule.min) : null;
        const maxVal = rule.max != null && Number.isFinite(rule.max) ? Number(rule.max) : null;
        checkNutrient(key, name, actual, minVal, maxVal, unit);
      } else {
        const isLimitNutrient = ['sodium_mg', 'cholesterol_mg', 'sugar_g', 'saturated_fat_g', 'trans_fat_g'].includes(key);
        if (isLimitNutrient) {
          checkNutrient(key, name, actual, null, staticVal, unit);
        } else {
          checkNutrient(key, name, actual, staticVal * 0.8, null, unit);
        }
      }
    });

    return warnings;
  }, [selectedItems, dailyNeeds, actualNutrients, analysisGuidelines, language, t]);

  const tabs = [
    { id: 'profile', label: 'Profile', icon: User },
    { id: 0, label: t.report.tabs.menu, icon: FileText },
    { id: 1, label: t.report.tabs.nutrition, icon: BarChart3 },
    { id: 2, label: t.report.tabs.other, icon: List },
    { id: 3, label: t.report.tabs.tips, icon: Lightbulb },
  ];

  const userConditions = userData.healthConditions.filter(c => c !== 'normal');

  const handleDownloadPDF = async () => {
    setIsGenerating(true);

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

    try {
      const url = await generateNutritionPDF({
        userName: userData.gender === 'male' ? 'User' : 'User',
        userData: {
          gender: userData.gender || 'male',
          age: userData.age,
          weight: userData.weight,
          height: userData.height,
          activity: userData.activity || 'moderate',
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
      }, true); // Pass true to get Blob URL

      if (url) {
        setPreviewUrl(url);
        setIsPreviewModalOpen(true);
      }
    } catch (error) {
      console.error('Failed to generate PDF preview', error);
    } finally {
      setIsGenerating(false);
    }
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
                  className={`flex-1 min-w-[100px] px-3 py-3 font-semibold text-sm transition-all border-b-4 flex items-center justify-center gap-2 cursor-pointer font-sans ${
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
                    <span className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]"></span>
                    Health Conditions
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {userData.healthConditions.map(c => (
                      <span key={c} className="px-3.5 py-1.5 bg-emerald-500/10 dark:bg-emerald-500/15 text-emerald-800 dark:text-emerald-300 border border-emerald-500/20 dark:border-emerald-500/10 rounded-full text-xs font-semibold capitalize font-sans shadow-sm hover:bg-emerald-500/15 transition-all duration-200">
                        {t.input.health[c as keyof typeof t.input.health] || c}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="space-y-3">
                  <h4 className="text-sm font-bold text-gray-900 dark:text-white flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-amber-500 shadow-[0_0_8px_rgba(245,158,11,0.5)]"></span>
                    Food Preferences
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {userData.foodPreferences.length > 0 ? userData.foodPreferences.map(p => (
                      <span key={p} className="px-3.5 py-1.5 bg-amber-500/10 dark:bg-amber-500/15 text-amber-800 dark:text-amber-300 border border-amber-500/20 dark:border-amber-500/10 rounded-full text-xs font-semibold capitalize font-sans shadow-sm hover:bg-amber-500/15 transition-all duration-200">
                        {p}
                      </span>
                    )) : (
                      <span className="text-xs text-gray-500 italic pl-1">All Cuisines / None</span>
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

                        let cardStyle = '';
                        let titleColor = '';
                        let rangeColor = '';

                        if (key === 'energy_kcal') {
                          cardStyle = 'bg-primary text-primary-foreground border-primary/20 shadow-md hover:shadow-lg hover:-translate-y-0.5 transition-all duration-300';
                          titleColor = 'text-primary-foreground font-bold';
                          rangeColor = 'text-primary-foreground/90 font-medium';
                        } else if (['carbohydrate_g', 'protein_g', 'fat_g'].includes(key)) {
                          cardStyle = 'bg-destructive text-destructive-foreground border-destructive/20 shadow-md hover:shadow-lg hover:-translate-y-0.5 transition-all duration-300';
                          titleColor = 'text-destructive-foreground font-bold';
                          rangeColor = 'text-destructive-foreground/90 font-medium';
                        } else {
                          cardStyle = 'bg-red-500/10 dark:bg-red-950/25 border-red-500/15 shadow-sm hover:shadow-md hover:-translate-y-0.5 transition-all duration-300';
                          titleColor = 'text-gray-900 dark:text-red-300 font-semibold';
                          rangeColor = 'text-gray-600 dark:text-red-400';
                        }

                        return (
                          <div key={key} className={`rounded-2xl p-3 border text-left flex flex-col justify-center font-sans ${cardStyle}`}>
                            <p className={`font-bold text-xs mb-1 truncate ${titleColor}`} title={friendlyName}>{friendlyName}</p>
                            <p className={`text-[10px] font-semibold font-serif ${rangeColor}`}>{rangeText}</p>
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
                  <h3 className="text-lg font-bold mb-2 text-primary dark:text-emerald-450 font-serif">
                    Micronutrient Analysis
                  </h3>
                  <NutritionChart data={microData} unit="mg" />
                </div>
              )}

              {nutritionalWarnings.length > 0 && (
                <div className="mt-8 p-5 rounded-2xl border bg-amber-500/5 dark:bg-amber-500/10 border-amber-500/20 dark:border-amber-500/10 shadow-sm">
                  <div className="flex items-center gap-2 mb-3">
                    <span className="text-amber-500 text-lg font-bold">⚠️</span>
                    <h3 className="font-bold text-sm text-amber-950 dark:text-amber-300 font-serif">
                      Nutritional Adjustments & Notes
                    </h3>
                  </div>
                  <ul className="space-y-2">
                    {nutritionalWarnings.map((warning, index) => (
                      <li key={index} className="flex items-start gap-2.5 text-xs text-amber-900 dark:text-amber-400 font-medium">
                        <span className="text-amber-500">•</span>
                        <span className="flex-1 leading-relaxed">{warning.message}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
          {activeTab === 2 && (
            <div>
              <h2 className="text-2xl font-bold mb-6 text-gray-900 dark:text-white font-serif tracking-tight">{t.report.tabs.other}</h2>

              {nutritionalWarnings.length > 0 && (
                <div className="mb-8 p-5 rounded-2xl border bg-amber-500/5 dark:bg-amber-500/10 border-amber-500/20 dark:border-amber-500/10 shadow-sm">
                  <div className="flex items-center gap-2 mb-3">
                    <span className="text-amber-500 text-lg font-bold">⚠️</span>
                    <h3 className="font-bold text-sm text-amber-950 dark:text-amber-300 font-serif">
                      Nutritional Adjustments & Notes
                    </h3>
                  </div>
                  <ul className="space-y-2">
                    {nutritionalWarnings.map((warning, index) => (
                      <li key={index} className="flex items-start gap-2.5 text-xs text-amber-900 dark:text-amber-400 font-medium">
                        <span className="text-amber-500">•</span>
                        <span className="flex-1 leading-relaxed">{warning.message}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {(() => {
                const getNutrientCardData = (nutrientKey: string) => {
                  const rule = analysisGuidelines?.nutrients?.[nutrientKey];
                  const unit = getNutrientUnit(nutrientKey as any);
                  const name = t.nutrients[nutrientKey as keyof typeof t.nutrients] || nutrientKey.split('_')[0].toUpperCase();
                  
                  // Get actual value
                  const staticVal = Number(dailyNeeds[nutrientKey as keyof typeof dailyNeeds]) || 0;
                  const actual = actualNutrients && actualNutrients[nutrientKey] !== undefined
                    ? Math.round(actualNutrients[nutrientKey])
                    : Math.round(staticVal * (0.7 + Math.random() * 0.4));

                  let targetValText = '';
                  let percentage = 0;
                  let isDeficient = false;
                  let isExcessive = false;

                  if (rule) {
                    const minVal = rule.min != null ? Number(rule.min) : null;
                    const maxVal = rule.max != null && Number.isFinite(rule.max) ? Number(rule.max) : null;

                    // 1. Format Target Text
                    if (minVal !== null && maxVal !== null) {
                      if (minVal === maxVal) {
                        targetValText = `${Math.round(minVal)}`;
                      } else {
                        targetValText = `${Math.round(minVal)}-${Math.round(maxVal)}`;
                      }
                    } else if (minVal !== null) {
                      targetValText = `min. ${Math.round(minVal)}`;
                    } else if (maxVal !== null) {
                      targetValText = `max. ${Math.round(maxVal)}`;
                    } else {
                      targetValText = 'No limit';
                    }

                    // 2. Status & Percentage
                    if (minVal !== null && maxVal !== null) {
                      if (actual < minVal) {
                        isDeficient = true;
                        percentage = minVal > 0 ? Math.round((actual / minVal) * 100) : 100;
                      } else if (actual > maxVal) {
                        isExcessive = true;
                        percentage = maxVal > 0 ? Math.round((actual / maxVal) * 100) : 100;
                      } else {
                        percentage = minVal > 0 ? Math.round((actual / minVal) * 100) : 100;
                      }
                    } else if (minVal !== null) {
                      if (actual < minVal) {
                        isDeficient = true;
                      }
                      percentage = minVal > 0 ? Math.round((actual / minVal) * 100) : 100;
                    } else if (maxVal !== null) {
                      if (actual > maxVal) {
                        isExcessive = true;
                      }
                      percentage = maxVal > 0 ? Math.round((actual / maxVal) * 100) : 100;
                    } else {
                      percentage = 100;
                    }
                  } else {
                    targetValText = `${staticVal}`;
                    percentage = staticVal > 0 ? Math.round((actual / staticVal) * 100) : 100;

                    const isLimitNutrient = [
                      'sodium_mg',
                      'cholesterol_mg',
                      'sugar_g',
                      'saturated_fat_g',
                      'trans_fat_g'
                    ].includes(nutrientKey);

                    if (isLimitNutrient) {
                      if (actual > staticVal) {
                        isExcessive = true;
                      }
                    } else {
                      if (percentage < 100) {
                        isDeficient = true;
                      } else if (percentage > 200) {
                        isExcessive = true;
                      }
                    }
                  }

                  let statusLabel = 'Optimal';
                  let showBadge = false;
                  let cardBg = 'bg-white/40 dark:bg-slate-950/20 border-border/80 dark:border-slate-800/80';
                  let badgeBg = '';
                  let textColor = 'text-gray-800 dark:text-gray-200';
                  let titleColor = 'text-gray-900 dark:text-white';
                  let priority = 3;

                  if (isDeficient) {
                    statusLabel = 'Deficient';
                    showBadge = true;
                    priority = 1;
                    cardBg = 'bg-red-50/70 dark:bg-red-950/20 border-red-200/50 dark:border-red-900/40';
                    badgeBg = 'bg-red-500/10 text-red-600 dark:text-red-400';
                    textColor = 'text-red-700 dark:text-red-400';
                    titleColor = 'text-red-900 dark:text-red-200';
                  } else if (isExcessive) {
                    statusLabel = 'Excessive';
                    showBadge = true;
                    priority = 2;
                    cardBg = 'bg-amber-50/60 dark:bg-amber-950/20 border-amber-200/50 dark:border-amber-900/40';
                    badgeBg = 'bg-amber-500/10 text-amber-600 dark:text-amber-450';
                    textColor = 'text-amber-700 dark:text-amber-400';
                    titleColor = 'text-amber-900 dark:text-amber-200';
                  }

                  return {
                    nutrientKey,
                    name,
                    actual,
                    unit,
                    targetValText,
                    percentage,
                    status: {
                      label: statusLabel,
                      showBadge,
                      priority,
                      cardBg,
                      badgeBg,
                      textColor,
                      titleColor
                    }
                  };
                };

                return (
                  <>
                    {/* Vitamins Section */}
                    <div className="mb-8">
                      <h3 className="text-base font-bold mb-3.5 text-primary dark:text-emerald-450 font-serif">Vitamins</h3>
                      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
                        {(() => {
                          const mapped = vitaminNutrients.map(getNutrientCardData);
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
                                      / {item.targetValText}{item.unit}
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
                          const mapped = mineralNutrients.map(getNutrientCardData);
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
                                      / {item.targetValText}{item.unit}
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
                          const mapped = otherNutrients.map(getNutrientCardData);
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
                                      / {item.targetValText}{item.unit}
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

      {/* PDF Preview Modal */}
      <AnimatePresence>
        {isPreviewModalOpen && previewUrl && (
          <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="bg-white dark:bg-slate-900 w-full max-w-5xl h-[85vh] rounded-3xl overflow-hidden shadow-2xl flex flex-col border border-slate-200 dark:border-slate-800"
            >
              {/* Header */}
              <div className="flex items-center justify-between p-5 border-b border-slate-200 dark:border-slate-850">
                <div>
                  <h3 className="font-serif font-bold text-xl text-slate-900 dark:text-white">
                    PDF Report Preview
                  </h3>
                  <p className="text-xs text-slate-500 dark:text-slate-400 font-sans">
                    Review your report before downloading
                  </p>
                </div>
                <button
                  onClick={() => {
                    setIsPreviewModalOpen(false);
                    setPreviewUrl(null);
                  }}
                  className="p-2 text-slate-500 hover:text-slate-850 dark:text-slate-400 dark:hover:text-white rounded-full hover:bg-slate-100 dark:hover:bg-slate-800 cursor-pointer"
                >
                  <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              {/* Iframe Preview */}
              <div className="flex-1 bg-slate-100 dark:bg-slate-950 p-4 flex items-center justify-center">
                <iframe
                  src={previewUrl}
                  className="w-full h-full rounded-2xl border border-slate-200/80 dark:border-slate-800/80 shadow-sm bg-white"
                  title="PDF Preview"
                />
              </div>

              {/* Footer Actions */}
              <div className="flex items-center justify-end gap-3 p-4 border-t border-slate-200 dark:border-slate-850 bg-slate-50 dark:bg-slate-900/50">
                <button
                  onClick={() => {
                    setIsPreviewModalOpen(false);
                    setPreviewUrl(null);
                  }}
                  className="px-5 py-2.5 text-sm font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-800 rounded-xl cursor-pointer transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={() => {
                    const link = document.createElement('a');
                    link.href = previewUrl;
                    link.download = `NutriPlan_Report_${new Date().toISOString().split('T')[0]}.pdf`;
                    link.click();
                  }}
                  className="px-6 py-2.5 text-sm font-semibold bg-primary text-white hover:bg-primary-hover dark:bg-emerald-600 dark:hover:bg-emerald-500 rounded-xl shadow-lg cursor-pointer transition-colors flex items-center gap-2"
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                  Download PDF
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Generating Overlay */}
      {isGenerating && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-[2px] z-50 flex flex-col items-center justify-center gap-4">
          <div className="bg-white dark:bg-slate-900 p-6 rounded-3xl shadow-xl flex flex-col items-center gap-3 border border-slate-200 dark:border-slate-800">
            <div className="w-10 h-10 border-4 border-primary dark:border-emerald-500 border-t-transparent rounded-full animate-spin" />
            <p className="text-sm font-semibold text-slate-800 dark:text-slate-200">
              Preparing PDF preview...
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

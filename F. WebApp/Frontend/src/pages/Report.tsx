import { useState, useMemo, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { FileText, BarChart3, List, Lightbulb, User } from 'lucide-react';
import { t } from '../utils/translations';
import type { UserInputData } from './InputWizard';
import { calculateDailyNeeds } from '../utils/healthCalculations';
import { NutritionChart } from '../components/figma/NutritionChart';
import { getNutrientUnit } from '../utils/nutrientsList';
import { generateNutritionPDF, preFetchFonts } from '../utils/pdfGenerator';
import html2canvas from 'html2canvas';

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

const mealThemes = {
 breakfast: {
 title: 'Breakfast',
 time: '07:00 - 09:00',
 themeClass: "bg-gradient-to-br from-amber-100/35 via-amber-50/15 to-orange-100/25 ",
 borderClass: "border border-amber-200/60 ",
 tagBg: "bg-amber-100/90 text-amber-800 border border-amber-200/30",
 glowClass: "absolute -top-16 -right-16 w-64 h-64 bg-gradient-to-br from-amber-450/40 via-orange-450/20 to-transparent rounded-full blur-3xl pointer-events-none",
 glowClass2: "absolute -bottom-20 -left-20 w-64 h-64 bg-gradient-to-tr from-orange-450/20 via-amber-400/10 to-transparent rounded-full blur-3xl pointer-events-none",
 cardClass: "border border-amber-300/40 bg-gradient-to-br from-amber-200/40 via-amber-100/20 to-orange-100/30 shadow-[0_4px_12px_rgba(0,0,0,0.02)]"
 },
 lunch: {
 title: 'Lunch',
 time: '12:00 - 14:00',
 themeClass: "bg-gradient-to-br from-sky-100/30 via-sky-50/15 to-yellow-100/35 ",
 borderClass: "border border-sky-200/60 ",
 tagBg: "bg-sky-100/90 text-sky-800 border border-sky-200/30",
 glowClass: "absolute -top-16 -right-16 w-64 h-64 bg-gradient-to-br from-sky-400/40 via-yellow-450/20 to-transparent rounded-full blur-3xl pointer-events-none",
 glowClass2: "absolute -bottom-20 -left-20 w-64 h-64 bg-gradient-to-tr from-yellow-300/45 via-sky-300/10 to-transparent rounded-full blur-3xl pointer-events-none",
 cardClass: "border border-sky-300/40 bg-gradient-to-br from-sky-200/40 to-yellow-250/30 shadow-[0_4px_12px_rgba(0,0,0,0.02)]"
 },
 dinner: {
 title: 'Dinner',
 time: '18:00 - 19:00',
 themeClass: "bg-gradient-to-br from-indigo-100/35 via-indigo-50/15 to-purple-100/30 ",
 borderClass: "border border-indigo-200/60 ",
 tagBg: "bg-indigo-100/90 text-indigo-800 border border-indigo-200/30",
 glowClass: "absolute -top-16 -right-16 w-64 h-64 bg-gradient-to-br from-indigo-500/40 via-purple-450/20 to-transparent rounded-full blur-3xl pointer-events-none",
 glowClass2: "absolute -bottom-20 -left-20 w-64 h-64 bg-gradient-to-tr from-purple-500/20 via-indigo-500/10 to-transparent rounded-full blur-3xl pointer-events-none",
 cardClass: "border border-indigo-300/40 bg-gradient-to-br from-indigo-200/40 to-blue-900/20 shadow-[0_4px_12px_rgba(0,0,0,0.02)]"
 },
 snack: {
 title: 'Snack',
 time: '15:00 - 16:00',
 themeClass: "bg-gradient-to-br from-rose-100/35 via-rose-50/15 to-pink-100/30 ",
 borderClass: "border border-rose-200/60 ",
 tagBg: "bg-rose-100/90 text-rose-800 border border-rose-200/30",
 glowClass: "absolute -top-16 -right-16 w-64 h-64 bg-gradient-to-br from-rose-500/40 via-pink-450/20 to-transparent rounded-full blur-3xl pointer-events-none",
 glowClass2: "absolute -bottom-20 -left-20 w-64 h-64 bg-gradient-to-tr from-pink-500/20 via-rose-500/10 to-transparent rounded-full blur-3xl pointer-events-none",
 cardClass: "border border-rose-300/40 bg-gradient-to-br from-rose-200/40 via-rose-100 to-pink-100/30 shadow-[0_4px_12px_rgba(0,0,0,0.02)]"
 }
};

export function Report({ userData, onRegisterDownloadPDF }: ReportProps) {
 const [activeTab, setActiveTab] = useState<number | string>('profile');

 const [previewUrl, setPreviewUrl] = useState<string | null>(null);
 const [isPreviewModalOpen, setIsPreviewModalOpen] = useState(false);
 const [isGenerating, setIsGenerating] = useState(false);
 const pdfDataRef = useRef<any>(null);

 useEffect(() => {
 preFetchFonts();
 }, []);

 useEffect(() => {
    if (isPreviewModalOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [isPreviewModalOpen]);

 const [selectedItems] = useState<Record<string, any>>(() => {
 const saved = sessionStorage.getItem('dss_selected_items');
 return saved ? JSON.parse(saved) : {};
 });

 const [actualNutrients] = useState<any>(() => {
 const saved = sessionStorage.getItem('dss_actual_nutrients');
 return saved ? JSON.parse(saved) : null;
 });

 const [analysisGuidelines] = useState<any>(() => {
 const saved = sessionStorage.getItem('dss_analysis_guidelines');
 return saved ? JSON.parse(saved) : null;
 });

 const [analysisResult] = useState<any>(() => {
 const saved = sessionStorage.getItem('dss_analysis_result_full');
 return saved ? JSON.parse(saved) : null;
 });

  const waterTargetLiters = useMemo(() => {
    const weight = userData.weight || 70;
    const gender = userData.gender || 'male';
    const age = userData.age || 25;
    const hasCKD = userData.healthConditions.includes('ckd');

    if (hasCKD) {
      const rule = analysisGuidelines?.nutrients?.['water_g'];
      if (rule && rule.max && rule.max !== Infinity) {
        return {
          min: rule.min ? rule.min / 1000 : (weight * 30) / 1000,
          max: rule.max / 1000,
          basis: 'CKD Guideline'
        };
      }
      // CKD fluid target range: 30 - 35 mL/kg body weight per day
      return {
        min: (weight * 30) / 1000,
        max: (weight * 35) / 1000,
        basis: 'CKD Fallback'
      };
    }

    // Normal or other diseases (DM2, Hypertension, CVD, Cholesterol) -> DRI
    const rule = analysisGuidelines?.nutrients?.['water_g'];
    if (rule && rule.min && rule.min !== 0) {
      return {
        min: rule.min / 1000,
        max: (rule.min * 1.1) / 1000,
        basis: 'DRI'
      };
    }

    // Fallback if guideline is not loaded yet
    const driMl = gender === 'male' ? (age > 18 ? 3700 : 3300) : (age > 18 ? 2700 : 2300);
    return {
      min: driMl / 1000,
      max: (driMl * 1.1) / 1000,
      basis: 'DRI Fallback'
    };
  }, [analysisGuidelines, userData]);

 const foodWaterLiters = useMemo(() => {
 return (actualNutrients?.['water_g'] || 0) / 1000;
 }, [actualNutrients]);

 const totalWaterLiters = useMemo(() => {
 return foodWaterLiters;
 }, [foodWaterLiters]);

 const waterPercentage = useMemo(() => {
 const targetVal = waterTargetLiters.max || 2.5;
 return (totalWaterLiters / targetVal) * 100;
 }, [totalWaterLiters, waterTargetLiters]);

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
 calories: item.calories || 0,
 carbs: item.carbs || 0,
 protein: item.protein || 0,
 fat: item.fat || 0,
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

 // Collect nutrient deficiency/excess warnings dynamically (strictly for HARD constraints only)
 const nutritionalWarnings = useMemo(() => {
 const warnings: { message: string; type: 'deficient' | 'excessive'; nutrient: string }[] = [];

 const checkNutrient = (key: string, name: string, actualValue: number, minVal: number | null, maxVal: number | null, unit: string) => {
    if (minVal !== null && actualValue < minVal) {
      const diff = Math.round(minVal - actualValue);
      const msg = `${name}: ↓ ${diff}${unit}`;
      warnings.push({ message: msg, type: 'deficient', nutrient: key });
    } else if (maxVal !== null && maxVal !== Infinity && actualValue > maxVal) {
      const diff = Math.round(actualValue - maxVal);
      const msg = `${name}: ↑ ${diff}${unit}`;
      warnings.push({ message: msg, type: 'excessive', nutrient: key });
    }
  };

 const items = Object.values(selectedItems);
 const totalProtein = items.reduce((sum: number, item: any) => sum + (item.protein || 0), 0);
 const totalCarbs = items.reduce((sum: number, item: any) => sum + (item.carbs || 0), 0);
 const totalFat = items.reduce((sum: number, item: any) => sum + (item.fat || 0), 0);

 const allCheckKeys = [
 'energy_kcal',
 'protein_g',
 'carbohydrate_g',
 'fat_g',
 ...vitaminNutrients,
 ...mineralNutrients,
 ...otherNutrients
];

 allCheckKeys.forEach(key => {
 const rule = analysisGuidelines?.nutrients?.[key];
 // ONLY check if it is configured as a HARD constraint
 if (rule && rule.hard_soft_type === 'HARD') {
 const unit = rule.unit || getNutrientUnit(key as any);
 const name = t.nutrients[key as keyof typeof t.nutrients] || key.split('_')[0].toUpperCase();

 let actual = 0;
 if (key === 'energy_kcal') {
 actual = items.reduce((sum: number, item: any) => sum + (item.calories || 0), 0);
 } else if (key === 'protein_g') {
 actual = totalProtein;
 } else if (key === 'carbohydrate_g') {
 actual = totalCarbs;
 } else if (key === 'fat_g') {
 actual = totalFat;
 } else {
 actual = actualNutrients && actualNutrients[key] !== undefined
 ? actualNutrients[key]
 : (Number(dailyNeeds[key as keyof typeof dailyNeeds]) || 0) * 0.9;
 }

 const minVal = rule.min != null ? Number(rule.min) : null;
 const maxVal = rule.max != null && Number.isFinite(rule.max) ? Number(rule.max) : null;
 checkNutrient(key, name, actual, minVal, maxVal, unit);
 }
 });

 return warnings;
 }, [selectedItems, dailyNeeds, actualNutrients, analysisGuidelines, t]);

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
 ...actualNutrients,
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
 const canvas = await html2canvas(el, { scale: 1.5, logging: false, useCORS: true });
 return canvas.toDataURL('image/png');
 } catch (err) {
 console.error('Error capturing chart', err);
 return null;
 }
 };

 const macroChart = await captureChart('pdf-macro-chart');
 const microChart = microData.length > 0 ? await captureChart('pdf-micro-chart') : null;

 try {
 const pdfPayload = {
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
 language: 'en' as const,
 analysisGuidelines,
 charts: {
 macro: macroChart,
 micro: microChart
 }
 };

 pdfDataRef.current = pdfPayload;

 const url = await generateNutritionPDF(pdfPayload, true); // Pass true to get Blob URL

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

 const handleDownloadPDFRef = useRef(handleDownloadPDF);
 useEffect(() => {
 handleDownloadPDFRef.current = handleDownloadPDF;
 });

 useEffect(() => {
 if (onRegisterDownloadPDF) {
 onRegisterDownloadPDF(handleDownloadPDFRef.current);
 }
 return () => {
 if (onRegisterDownloadPDF) onRegisterDownloadPDF(null);
 };
 }, [onRegisterDownloadPDF]);

 const displayCalories = useMemo(() => {
 const tdee = (analysisResult && analysisResult.energy && typeof analysisResult.energy.tdee === 'number') 
 ? Math.round(analysisResult.energy.tdee) 
 : Math.round(dailyNeeds.calories);

 const hasDiseaseGuidelines = userConditions.length > 0;
 if (!hasDiseaseGuidelines) return tdee;

 const rule = analysisGuidelines?.nutrients?.['energy_kcal'];
 if (rule && rule.hard_soft_type === 'HARD') {
 const minVal = rule.min != null ? Math.round(rule.min) : 0;
 const maxVal = rule.max != null && Number.isFinite(rule.max) ? Math.round(rule.max) : Infinity;

 if (tdee > maxVal) return maxVal;
 if (tdee < minVal) return minVal;
 }
 return tdee;
 }, [analysisResult, dailyNeeds.calories, userConditions.length, analysisGuidelines]);

 return (
 <div className="w-full font-sans">
 <div className="mb-6 bg-white/70 backdrop-blur-md rounded-3xl border border-border/80 overflow-hidden shadow-xl shadow-primary/5 ">
 <div className="flex overflow-x-auto">
 {tabs.map((tab) => {
 const Icon = tab.icon;
 return (
 <button
 key={tab.id}
 onClick={() => setActiveTab(tab.id)}
 className={`flex-1 min-w-[100px] px-3 py-3 font-semibold text-sm transition-all border-b-4 flex items-center justify-center gap-2 cursor-pointer font-sans ${
 activeTab === tab.id
 ? 'border-primary text-primary bg-primary/5 '
 : 'border-transparent text-gray-600 hover:text-primary :text-emerald-450 hover:bg-secondary/30 :bg-slate-800/20'
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
 className="bg-white/70 backdrop-blur-md rounded-3xl p-6 sm:p-8 border border-border/80 shadow-xl shadow-primary/5 min-h-[500px]"
 >
 
 {/* Profile Summary Section */}
 {activeTab === 'profile' && (
 <motion.div
 initial={{ opacity: 0, y: 20 }}
 animate={{ opacity: 1, y: 0 }}
 className="space-y-8"
 >
 <div className="flex flex-col md:flex-row md:items-center justify-between pb-6 border-b border-border gap-6">
 <div className="flex items-center gap-4">
 <div className="w-12 h-12 rounded-full bg-primary/10 text-primary flex items-center justify-center">
 <User className="w-6 h-6" />
 </div>
 <div>
 <h2 className="text-2xl font-bold text-gray-900 font-serif tracking-tight">Profile Summary</h2>
 <p className="text-sm text-gray-500 font-sans">Summary of your personal data and health constraints</p>
 </div>
 </div>
 </div>
 
 <div className="grid grid-cols-2 md:grid-cols-4 gap-x-4 gap-y-6 py-2 font-sans">
  <div className="space-y-1">
  <span className="text-[10px] sm:text-xs font-bold text-primary uppercase tracking-wider">Gender & Age</span>
  <p className="text-sm sm:text-base font-bold text-gray-900 capitalize font-serif">
  {userData.gender === 'male' ? 'Male' : 'Female'}, {userData.age} yrs
  </p>
  </div>
  <div className="space-y-1 border-l border-border pl-4 sm:pl-6">
  <span className="text-[10px] sm:text-xs font-bold text-primary uppercase tracking-wider">Weight & Height</span>
  <p className="text-sm sm:text-base font-bold text-gray-900 font-serif whitespace-nowrap">
  {userData.weight} kg • {userData.height} cm
  </p>
  </div>
  <div className="space-y-1 sm:border-l sm:border-border sm:pl-6">
  <span className="text-[10px] sm:text-xs font-bold text-primary uppercase tracking-wider">Physical Activity</span>
  <p className="text-sm sm:text-base font-bold text-gray-900 capitalize font-serif">
  {userData.activity || 'Moderate'}
  </p>
  </div>
  <div className="space-y-1 border-l border-border pl-4 sm:pl-6">
  <span className="text-[10px] sm:text-xs font-bold text-primary uppercase tracking-wider">Estimated Calories</span>
  <p className="text-sm sm:text-base font-bold text-gray-900 font-serif">
  {displayCalories} kcal
  </p>
  </div>
  </div>

 <div className="grid grid-cols-1 md:grid-cols-2 gap-8 pt-6 border-t border-border font-sans">
 <div className="space-y-3">
 <h4 className="text-sm font-bold text-gray-900 flex items-center gap-2">
 <span className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]"></span>
 Health Conditions
 </h4>
 <div className="flex flex-wrap gap-2">
 {userData.healthConditions.map(c => (
 <span key={c} className="px-3.5 py-1.5 bg-emerald-500/10 text-emerald-800 border border-emerald-500/20 rounded-full text-xs font-semibold capitalize font-sans shadow-sm hover:bg-emerald-500/15 transition-all duration-200">
 {t.input.health[c as keyof typeof t.input.health] || c}
 </span>
 ))}
 </div>
 </div>

 <div className="space-y-3">
 <h4 className="text-sm font-bold text-gray-900 flex items-center gap-2">
 <span className="w-2 h-2 rounded-full bg-amber-500 shadow-[0_0_8px_rgba(245,158,11,0.5)]"></span>
 Food Preferences
 </h4>
 <div className="flex flex-wrap gap-2">
 {userData.foodPreferences.length > 0 ? userData.foodPreferences.map(p => (
 <span key={p} className="px-3.5 py-1.5 bg-amber-500/10 text-amber-800 border border-amber-500/20 rounded-full text-xs font-semibold capitalize font-sans shadow-sm hover:bg-amber-500/15 transition-all duration-200">
 {p}
 </span>
 )) : (
 <span className="text-xs text-gray-500 italic pl-1">All Cuisines / None</span>
 )}
 </div>
 </div>
 </div>

 <div className="pt-6 border-t border-border ">
 <h3 className="text-base font-bold mb-4 text-primary flex items-center gap-2 font-serif">
 <span>Required Nutrient Limits</span>
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
 cardStyle = 'bg-red-500/10 border-red-500/15 shadow-sm hover:shadow-md hover:-translate-y-0.5 transition-all duration-300';
 titleColor = 'text-gray-900 font-semibold';
 rangeColor = 'text-gray-600 ';
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
 <div className="flex flex-col md:flex-row md:items-center justify-between pb-6 border-b border-border gap-6 mb-8">
 <div>
 <h2 className="text-2xl font-bold text-gray-900 font-serif tracking-tight">{t.report.tabs.menu}</h2>
 <p className="text-sm text-gray-500 font-sans mt-0.5">Overview of your generated daily meal plan</p>
 </div>
 </div>

 <div className="space-y-8">
 {Object.entries(mealThemes).map(([mealKey, theme]) => {
 const items = getMealItems(mealKey);
 if (items.length === 0) return null;
 
 if (mealKey === 'snack') {
 return (
 <div key={mealKey} className="grid grid-cols-1 md:grid-cols-3 gap-6 relative z-10">
 {/* Snack Container (1/3 width on desktop) */}
 <div 
 className={`md:col-span-1 relative overflow-hidden rounded-3xl p-6 sm:p-7 ${theme.borderClass} ${theme.themeClass} shadow-xl transition-all duration-300`}
 >
 {/* Sun/Sunset art glow effects */}
 <div className={theme.glowClass} />
 <div className={theme.glowClass2} />

 <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-4 relative z-10">
 <div className="flex items-center gap-3">
 <div>
 <h3 className="text-lg font-bold text-gray-955 font-serif leading-none mb-1.5 capitalize">
 {theme.title}
 </h3>
 <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-bold ${theme.tagBg} shadow-sm bg-opacity-90`}>
 <svg className="w-3.5 h-3.5 mr-1 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
 <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
 </svg>
 {theme.time}
 </span>
 </div>
 </div>
 </div>

 <div className="grid grid-cols-1 gap-4 relative z-10">
 {items.map((item, i) => {
 const isMain = item.type === 'main';
 const isSide = item.type === 'side';
 const isDrink = item.type === 'drink';

 let courseLabel = item.type;
 if (isMain) courseLabel = 'Main Course';
 else if (isSide) courseLabel = 'Side Dish';
 else if (isDrink) courseLabel = 'Drink';

 const tagColorClass = 'bg-white/40 text-gray-800 border border-black/5 ';

 return (
 <div
 key={i}
 className={`p-4.5 ${theme.cardClass} backdrop-blur-md rounded-2xl flex flex-col shadow-md hover:shadow-lg hover:-translate-y-0.5 transition-all duration-300 font-sans`}
 >
 <div className="mb-3">
 <div className="flex items-center justify-between gap-2 mb-2">
 <span className={`inline-flex px-2 py-0.5 rounded-md text-[9px] font-bold uppercase tracking-wider ${tagColorClass}`}>
 {courseLabel}
 </span>
 <span className="text-[10px] text-gray-600 font-medium font-serif">{item.portion}</span>
 </div>
 <h4 className="font-sans font-bold text-gray-900 text-[14px] leading-snug line-clamp-2">
 {item.item}
 </h4>
 </div>

 <div className="mt-auto pt-3 border-t border-black/5 ">
 <p className="text-xs font-semibold text-primary mb-1 font-serif">
 {item.calories} kcal
 </p>
 <div className="flex items-center justify-between text-[10px] text-gray-700 font-sans">
 <span>Carb: {item.carbs}g &bull; Pro: {item.protein}g &bull; Fat: {item.fat}g</span>
 </div>
 </div>
 </div>
 );
 })}
 </div>
 </div>

 {/* Animated Water Level Container (2/3 width on desktop) */}
 <div className="md:col-span-2 bg-gradient-to-br from-sky-100/35 via-sky-50/15 to-blue-100/30 border border-sky-200/60 rounded-3xl pt-6 pb-4 px-6 flex flex-col justify-between shadow-xl transition-all duration-300 relative overflow-hidden min-h-[200px]">
 {/* Water glow circles */}
 <div className="absolute -top-16 -right-16 w-64 h-64 bg-gradient-to-br from-sky-400/30 via-blue-400/10 to-transparent rounded-full blur-3xl pointer-events-none" />
 <div className="absolute -bottom-20 -left-20 w-64 h-64 bg-gradient-to-tr from-blue-300/20 via-sky-300/10 to-transparent rounded-full blur-3xl pointer-events-none" />
 <div className="relative z-10 flex flex-col sm:flex-row gap-6 sm:gap-8 items-center sm:items-start justify-between h-full w-full">
 {/* Left Column: Title + Badge + Poster text */}
 <div className="flex-1 flex flex-col justify-start min-w-0 w-full text-center sm:text-left items-center sm:items-start">
 <div>
 <h3 className="text-lg font-bold text-gray-955 font-serif leading-none mb-1.5 capitalize">
 Hydration Tracker
 </h3>
 <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-sky-100/90 text-sky-800 border border-sky-200/30 shadow-sm bg-opacity-90">
 Daily Target: {userData.healthConditions.includes('ckd') ? `${waterTargetLiters.min.toFixed(2)} - ${waterTargetLiters.max.toFixed(2)} L` : `min. ${waterTargetLiters.min.toFixed(2)} L`}
 </span>
 </div>

 <div className="mt-5 space-y-5 w-full">
 {/* Secured Block */}
 <div className="space-y-1">
 <span className="text-[10px] font-bold text-sky-600/90 uppercase tracking-widest block">
 Secured From Meals
 </span>
 <div className="flex items-baseline gap-1 justify-center sm:justify-start">
 <span className="text-xl font-extrabold text-sky-600 font-serif leading-none">
 {foodWaterLiters.toFixed(2)}
 </span>
 <span className="text-xs font-bold text-sky-600/70 ">Liters</span>
 </div>
 <p className="text-[11px] text-gray-500 font-medium">
 of water is already provided by your recommended dishes.
 </p>
 </div>

 {/* Needed Block */}
 <div className="space-y-1">
 <span className="text-[10px] font-bold text-amber-600/90 uppercase tracking-widest block">
 Additional Needed
 </span>
 <div className="flex items-baseline gap-1 justify-center sm:justify-start">
 <span className="text-3xl font-extrabold text-amber-500 font-serif leading-none">
 {Math.max(0, waterTargetLiters.min - foodWaterLiters).toFixed(2)}
 </span>
 <span className="text-base font-bold text-amber-500/70 ">Liters</span>
 </div>
 <p className="text-[11px] text-gray-500 font-medium">
 more to drink to meet your daily hydration goal! 💧
 </p>
 </div>
 </div>
 </div>

 {/* Right Column: Glass animation */}
 <div className="relative w-40 h-56 flex flex-col items-center justify-start shrink-0 pt-0 filter drop-shadow-[0_10px_20px_rgba(0,0,0,0.25)] (0,0,0,0.6)]">
 {/* Glass Top Rim */}
 <div className="absolute top-0 w-36 h-5 bg-sky-200/20 border border-sky-350/50 rounded-full z-30 pointer-events-none" />
 
 {/* Thin Tapered Glass Border Outline */}
 <svg 
 viewBox="0 0 100 100" 
 preserveAspectRatio="none" 
 className="absolute top-[10px] w-36 h-52 text-sky-300/60 pointer-events-none z-20"
 >
 <polygon 
 points="0.5,0.5 99.5,0.5 81.8,99.5 18.2,99.5" 
 fill="none" 
 stroke="currentColor" 
 strokeWidth="1.5" 
 />
 </svg>

 {/* Tapered Glass Body */}
 <div 
 className="relative w-36 h-52 bg-sky-100/15 border border-sky-300/20 rounded-b-2xl overflow-hidden shadow-inner flex items-center justify-center mt-2.5"
 style={{ clipPath: 'polygon(0% 0%, 100% 0%, 82% 100%, 18% 100%)' }}
 >
 <div 
 className="absolute bottom-0 left-0 w-full bg-gradient-to-t from-sky-600/85 to-sky-400/85 transition-all duration-1000 ease-out"
 style={{ height: `${Math.min(100, Math.max(0, waterPercentage))}%` }}
 >
 <style>{`
 @keyframes wave-motion {
 0% { transform: translateX(0); }
 100% { transform: translateX(-50%); }
 }
 `}</style>
 {/* Wave 1 (Back wave, lighter color) */}
 <svg 
 viewBox="0 0 240 28" 
 preserveAspectRatio="none"
 className="absolute left-0 w-[200%] text-sky-300/40 " 
 style={{ top: '-16px', height: '18px', animation: 'wave-motion 4s linear infinite' }}
 >
 <path 
 d="M 0 15 C 30 25, 30 5, 60 15 C 90 25, 90 5, 120 15 C 150 25, 150 5, 180 15 C 210 25, 210 5, 240 15 L 240 28 L 0 28 Z" 
 fill="currentColor" 
 />
 </svg>

 {/* Wave 2 (Front wave, matching water color) */}
 <svg 
 viewBox="0 0 240 28" 
 preserveAspectRatio="none"
 className="absolute left-0 w-[200%] text-sky-400/85 " 
 style={{ top: '-16px', height: '18px', animation: 'wave-motion 2.5s linear infinite', animationDirection: 'reverse' }}
 >
 <path 
 d="M 0 15 C 30 25, 30 5, 60 15 C 90 25, 90 5, 120 15 C 150 25, 150 5, 180 15 C 210 25, 210 5, 240 15 L 240 28 L 0 28 Z" 
 fill="currentColor" 
 />
 </svg>
 </div>

 <div className="relative z-20 flex flex-col items-center select-none pointer-events-none">
 <span className="font-extrabold text-[18px] text-sky-900 drop-shadow-sm font-sans leading-none bg-white/40 px-2 py-1 rounded-lg border border-sky-200/10 backdrop-blur-xs">
 {totalWaterLiters.toFixed(2)}L
 </span>
 </div>
 </div>
 </div>
 </div>
 </div>
 </div>
 );
 }

 return (
 <div 
 key={mealKey} 
 className={`relative overflow-hidden rounded-3xl p-6 sm:p-7 ${theme.borderClass} ${theme.themeClass} shadow-xl transition-all duration-300`}
 >
 {/* Sun/Sunset art glow effects */}
 <div className={theme.glowClass} />
 <div className={theme.glowClass2} />

 <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-4 relative z-10">
 <div className="flex items-center gap-3">
 <div>
 <h3 className="text-lg font-bold text-gray-955 font-serif leading-none mb-1.5 capitalize">
 {theme.title}
 </h3>
 <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-bold ${theme.tagBg} shadow-sm bg-opacity-90`}>
 <svg className="w-3.5 h-3.5 mr-1 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
 <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
 </svg>
 {theme.time}
 </span>
 </div>
 </div>
 </div>

 <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 relative z-10">
 {items.map((item, i) => {
 const isMain = item.type === 'main';
 const isSide = item.type === 'side';
 const isDrink = item.type === 'drink';

 let courseLabel = item.type;
 if (isMain) courseLabel = 'Main Course';
 else if (isSide) courseLabel = 'Side Dish';
 else if (isDrink) courseLabel = 'Drink';

 const tagColorClass = 'bg-white/40 text-gray-800 border border-black/5 ';

 return (
 <div
 key={i}
 className={`p-4.5 ${theme.cardClass} backdrop-blur-md rounded-2xl flex flex-col shadow-md hover:shadow-lg hover:-translate-y-0.5 transition-all duration-300 font-sans`}
 >
 <div className="mb-3">
 <div className="flex items-center justify-between gap-2 mb-2">
 <span className={`inline-flex px-2 py-0.5 rounded-md text-[9px] font-bold uppercase tracking-wider ${tagColorClass}`}>
 {courseLabel}
 </span>
 <span className="text-[10px] text-gray-600 font-medium font-serif">{item.portion}</span>
 </div>
 <h4 className="font-sans font-bold text-gray-900 text-[14px] leading-snug line-clamp-2">
 {item.item}
 </h4>
 </div>

 <div className="mt-auto pt-3 border-t border-black/5 ">
 <p className="text-xs font-semibold text-primary mb-1 font-serif">
 {item.calories} kcal
 </p>
 <div className="flex items-center justify-between text-[10px] text-gray-700 font-sans">
 <span>Carb: {item.carbs}g &bull; Pro: {item.protein}g &bull; Fat: {item.fat}g</span>
 </div>
 </div>
 </div>
 );
 })}
 </div>
 </div>
 );
 })}
 </div>

 {/* Warnings placed right under the menu plan */}
 {nutritionalWarnings.length > 0 && (() => {
 const deficientWarnings = nutritionalWarnings.filter(w => w.type === 'deficient');
 const excessiveWarnings = nutritionalWarnings.filter(w => w.type === 'excessive');

 return (
 <div className="mt-10 space-y-5">
 {/* 1. Excess Warnings Box */}
 {excessiveWarnings.length > 0 && (
 <div className="p-6 rounded-2xl border bg-red-500/5 border-red-500/15 shadow-sm font-sans animate-fade-in">
 <div className="flex items-center gap-2.5 mb-3">
 <span className="text-red-500 text-lg font-bold">⚠️</span>
 <h3 className="font-bold text-sm text-red-950 font-serif">
 Nutritional Excess Alerts
 </h3>
 </div>
 <p className="text-xs text-gray-650 mb-4 font-sans leading-relaxed">
 The following nutrient levels in your generated meal plan exceed the recommended safe maximum limits (hard constraints). You may want to reduce portion sizes or replace some items:
 </p>
 <ul className="space-y-2.5">
 {excessiveWarnings.map((warning, index) => (
 <li key={index} className="flex items-start gap-2.5 text-xs text-red-900 font-medium font-sans">
 <span className="text-red-500 mt-0.5">•</span>
 <span className="flex-1 leading-relaxed">{warning.message}</span>
 </li>
 ))}
 </ul>
 </div>
 )}

 {/* 2. Deficiency Warnings Box */}
 {deficientWarnings.length > 0 && (
 <div className="p-6 rounded-2xl border bg-amber-500/5 border-amber-500/15 shadow-sm font-sans animate-fade-in">
 <div className="flex items-center gap-2.5 mb-3">
 <span className="text-amber-500 text-lg font-bold">⚠️</span>
 <h3 className="font-bold text-sm text-amber-950 font-serif">
 Nutritional Deficiency Warnings
 </h3>
 </div>
 <p className="text-xs text-gray-650 mb-4 font-sans leading-relaxed">
 Your recommended meal plan is currently below the minimum targets for the following nutrients. Consider adding healthy side dishes, snacks, or supplements:
 </p>
 <ul className="space-y-2.5">
 {deficientWarnings.map((warning, index) => (
 <li key={index} className="flex items-start gap-2.5 text-xs text-amber-900 font-medium font-sans">
 <span className="text-amber-500 mt-0.5">•</span>
 <span className="flex-1 leading-relaxed">{warning.message}</span>
 </li>
 ))}
 </ul>
 </div>
 )}
 </div>
 );
 })()}
 </div>
 )}

 {activeTab === 1 && (
 <div key="chart-en" className="font-sans">
 <h2 className="text-2xl font-bold mb-6 text-gray-900 font-serif tracking-tight">{t.report.tabs.nutrition}</h2>
 <div className="mb-4 flex flex-wrap items-center gap-6 text-sm">
 <div className="flex items-center gap-2">
 <div className="w-4 h-4 bg-primary rounded"></div>
 <span className="text-gray-700 ">Actual Value</span>
 </div>
 <div className="flex items-center gap-2">
 <div className="w-8 h-3 bg-gradient-to-b from-primary/40 to-secondary/20 rounded-sm"></div>
 <span className="text-gray-700 ">Safe Range</span>
 </div>
 <div className="flex items-center gap-2">
 <div className="w-8 h-0.5 border-t-2 border-dashed border-primary"></div>
 <span className="text-gray-700 ">Min/Max Boundary</span>
 </div>
 </div>
 <div className="mb-4">
 <h3 className="text-lg font-bold mb-2 text-primary font-serif">Macronutrient Balance (g)</h3>
 <NutritionChart data={macroData} />
 </div>
 
 {microData.length > 0 && (
 <div className="mt-8">
 <h3 className="text-lg font-bold mb-2 text-primary font-serif">
 Micronutrient Analysis
 </h3>
 <NutritionChart data={microData} unit="mg" />
 </div>
 )}

 </div>
 )}
 {activeTab === 2 && (
 <div>
 <h2 className="text-2xl font-bold mb-6 text-gray-900 font-serif tracking-tight">{t.report.tabs.other}</h2>


 {(() => {
 const getNutrientCardData = (nutrientKey: string) => {
 const rule = analysisGuidelines?.nutrients?.[nutrientKey];
 const unit = getNutrientUnit(nutrientKey as any);
 const name = t.nutrients[nutrientKey as keyof typeof t.nutrients] || nutrientKey.split('_')[0].toUpperCase();
 
 // Get actual value
 const staticVal = Number(dailyNeeds[nutrientKey as keyof typeof dailyNeeds]) || 0;
 let actual = actualNutrients && actualNutrients[nutrientKey] !== undefined
 ? Math.round(actualNutrients[nutrientKey])
 : Math.round(staticVal * (0.7 + Math.random() * 0.4));

 let targetValText = '';
 let percentage = 0;
 let isDeficient = false;
 let isExcessive = false;

 if (nutrientKey === 'water_g') {
 const minGram = Math.round(waterTargetLiters.min * 1000);
 const maxGram = Math.round(waterTargetLiters.max * 1000);
 
 targetValText = `${minGram}-${maxGram}`;
 percentage = maxGram > 0 ? Math.round((actual / maxGram) * 100) : 100;
 
 if (actual < minGram) {
 isDeficient = true;
 } else if (actual > maxGram) {
 isExcessive = true;
 }
 } else if (rule) {
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
 let showBadge = true;
 let cardBg = 'bg-green-50/90 border-green-300 ';
 let badgeBg = 'bg-green-100 text-green-700 ';
 let textColor = 'text-green-700 ';
 let titleColor = 'text-green-900 ';
 let priority = 3;

 if (isDeficient) {
 statusLabel = 'Deficient';
 showBadge = true;
 priority = 1;
 cardBg = 'bg-red-50/90 border-red-300 ';
 badgeBg = 'bg-red-100 text-red-700 ';
 textColor = 'text-red-700 ';
 titleColor = 'text-red-900 ';
 } else if (isExcessive) {
 statusLabel = 'Excessive';
 showBadge = true;
 priority = 2;
 cardBg = 'bg-amber-50/90 border-amber-300 ';
 badgeBg = 'bg-amber-100 text-amber-700 ';
 textColor = 'text-amber-700 ';
 titleColor = 'text-amber-900 ';
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
 <h3 className="text-base font-bold mb-3.5 text-primary font-serif">Vitamins</h3>
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
 <span className="text-[10px] font-light text-gray-400 ml-1">
 / {item.targetValText}{item.unit}
 </span>
 </div>
 <span className="text-[10px] text-gray-400 font-bold">{item.percentage}%</span>
 </div>
 </div>
 </div>
 ));
 })()}
 </div>
 </div>

 {/* Minerals Section */}
 <div className="mb-8">
 <h3 className="text-base font-bold mb-3.5 text-primary font-serif">Minerals</h3>
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
 <span className="text-[10px] font-light text-gray-400 ml-1">
 / {item.targetValText}{item.unit}
 </span>
 </div>
 <span className="text-[10px] text-gray-400 font-bold">{item.percentage}%</span>
 </div>
 </div>
 </div>
 ));
 })()}
 </div>
 </div>

 {/* Other Nutrients Section */}
 <div>
 <h3 className="text-base font-bold mb-3.5 text-primary font-serif">Other Nutrients</h3>
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
 <span className="text-[10px] font-light text-gray-400 ml-1">
 / {item.targetValText}{item.unit}
 </span>
 </div>
 <span className="text-[10px] text-gray-400 font-bold">{item.percentage}%</span>
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
 <h2 className="text-2xl font-bold mb-6 text-gray-900 font-serif tracking-tight">{t.report.tabs.tips}</h2>
 <div className="space-y-4 font-sans">
 {userConditions.length > 0 ? (
 userConditions.map((condition) => (
 <div key={condition} className="p-5 bg-white/50 rounded-2xl border border-border/80 shadow-sm shadow-primary/5 ">
 <h3 className="font-bold text-base mb-2.5 text-primary font-serif">
 {t.input.health[condition as keyof typeof t.input.health]}
 </h3>
 <ul className="space-y-2">
 {dietTips[condition as keyof typeof dietTips].map((tip, i) => (
 <li key={i} className="flex items-start gap-2 text-sm text-gray-700 ">
 <span className="text-primary font-bold">•</span>
 <span className="flex-1">{tip}</span>
 </li>
 ))}
 </ul>
 </div>
 ))
 ) : (
 <div className="p-6 bg-white/50 rounded-2xl text-center text-sm text-primary border border-border/80 shadow-sm">
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
 className="bg-white w-full max-w-2xl h-[85vh] rounded-3xl overflow-hidden shadow-2xl flex flex-col border border-slate-200 "
 >
 {/* Header */}
 <div className="flex items-center justify-between p-5 border-b border-slate-200 ">
 <div>
 <h3 className="font-serif font-bold text-xl text-slate-900 ">
 PDF Report Preview
 </h3>
 <p className="text-xs text-slate-500 font-sans">
 Review your report before downloading
 </p>
 </div>
 <button
 onClick={() => {
 setIsPreviewModalOpen(false);
 setPreviewUrl(null);
 }}
 className="p-2 text-slate-500 hover:text-slate-850 :text-white rounded-full hover:bg-slate-100 :bg-slate-800 cursor-pointer"
 >
 <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
 <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
 </svg>
 </button>
 </div>

 {/* Iframe Preview */}
 <div className="flex-1 bg-slate-100 p-4 flex items-center justify-center">
 <iframe
 src={previewUrl}
 className="h-full aspect-[1/1.414] max-w-full rounded-2xl border border-slate-200/80 shadow-sm bg-white"
 title="PDF Preview"
 />
 </div>

 {/* Footer Actions */}
 <div className="flex items-center justify-end gap-3 p-4 border-t border-slate-200 bg-slate-50 ">
 <button
 onClick={() => {
 setIsPreviewModalOpen(false);
 setPreviewUrl(null);
 }}
 className="px-5 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-200 :bg-slate-800 rounded-xl cursor-pointer transition-colors"
 >
 Cancel
 </button>
 <button
 onClick={async () => {
 if (pdfDataRef.current) {
 await generateNutritionPDF(pdfDataRef.current, false);
 }
 }}
 className="px-6 py-2.5 text-sm font-semibold bg-primary text-white hover:bg-primary-hover :bg-emerald-500 rounded-xl shadow-lg cursor-pointer transition-colors flex items-center gap-2"
 >
 <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
 <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
 </svg>
 Download Report
 </button>
 </div>
 </motion.div>
 </div>
 )}
 </AnimatePresence>

 {/* Generating Overlay */}
 {isGenerating && (
 <div className="fixed inset-0 bg-black/40 backdrop-blur-[2px] z-50 flex flex-col items-center justify-center gap-4">
 <div className="bg-white p-6 rounded-3xl shadow-xl flex flex-col items-center gap-3 border border-slate-200 ">
 <div className="w-10 h-10 border-4 border-primary border-t-transparent rounded-full animate-spin" />
 <p className="text-sm font-semibold text-slate-800 ">
 Preparing Document...
 </p>
 </div>
 </div>
 )}
 </div>
 );
}

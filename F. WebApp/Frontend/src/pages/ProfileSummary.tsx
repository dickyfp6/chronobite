import { useEffect, useState, useMemo } from 'react';
import { motion } from 'motion/react';
import { ArrowRight, ArrowLeft, HeartPulse, Scale, FileText, Loader2, ChevronDown } from 'lucide-react';
import type { UserInputData } from './InputWizard';
import { calculateDailyNeeds } from '../utils/healthCalculations';
import { api } from '../services/api';

interface ProfileSummaryProps {
 userData: UserInputData;
 onBack: () => void;
 onContinue: () => void;
 onAnalysisComplete?: (result: any) => void;
}

type BmiInfo = {
 label: string;
 badge: string;
 text: string;
 note: string;
};

type GuidelineItem = {
 key: string;
 label: string;
 min: number | string | null;
 max: number | string | null;
 unit: string;
 source?: string;
 hard_soft_type?: string; // 'HARD' | 'SOFT'
 diseases?: string[];
};

const priorityMacroKeys = ['energy_kcal', 'carbohydrate_g', 'protein_g', 'fat_g'];

const isEnergyOrMacroKey = (key: string) => priorityMacroKeys.includes(key);

const conditionLabels: Record<string, string> = {
 normal: 'General / No Condition',
 dm2: 'Diabetes Mellitus Type 2',
 hypertension: 'Hypertension',
 cvd: 'Cardiovascular Disease',
 cholesterol: 'High Cholesterol',
 ckd: 'Chronic Kidney Disease',
};

function getBmiInfo(weight: number, height: number): BmiInfo {
 const bmi = weight / ((height / 100) ** 2);
 if (bmi < 18.5) {
 return {
 label: 'Underweight',
 badge: 'bg-yellow-100 text-yellow-800',
 text: 'text-yellow-700',
 note: 'Your ideal weight range for this height is in the normal BMI band.',
 };
 }
 if (bmi < 25) {
 return {
 label: 'Normal weight',
 badge: 'bg-green-100 text-green-800',
 text: 'text-green-700',
 note: 'Your current weight is within the recommended healthy range.',
 };
 }
 if (bmi < 30) {
 return {
 label: 'Overweight',
 badge: 'bg-yellow-100 text-yellow-800',
 text: 'text-yellow-700',
 note: 'A healthier weight range for your height is shown below.',
 };
 }
 return {
 label: 'Obesity',
 badge: 'bg-red-100 text-red-800',
 text: 'text-red-700',
 note: 'A healthier weight range for your height is shown below.',
 };
}

const conditionGuidelines: Record<string, string> = {
 normal: 'No disease restriction selected. Your needs are based on standard nutrition targets.',
 dm2: 'Carbohydrates and added sugars should be controlled. Higher-fiber foods are preferred.',
 hypertension: 'Sodium should be limited and potassium-rich foods are encouraged when appropriate.',
 cvd: 'Saturated fat and trans fat should be limited. Lean proteins and healthy fats are preferred.',
 cholesterol: 'Soluble fiber should be increased and cholesterol-dense foods should be limited.',
 ckd: 'Protein, sodium, potassium, and phosphorus may need tighter limits depending on your condition.',
};

const guidelineLabels: Record<string, string> = {
 carbohydrate_g: 'Carbohydrates',
 protein_g: 'Protein',
 fat_g: 'Fat',
 energy_kcal: 'Energy',
 fiber_g: 'Fiber',
 sugar_g: 'Sugar',
 saturated_fat_g: 'Saturated Fat',
 trans_fat_g: 'Trans Fat',
 cholesterol_mg: 'Cholesterol',
 choline_mg: 'Choline',
 folate_mg: 'Folate',
 water_g: 'Water',
 calcium_mg: 'Calcium',
 iron_mg: 'Iron',
 magnesium_mg: 'Magnesium',
 phosphorus_mg: 'Phosphorus',
 potassium_mg: 'Potassium',
 sodium_mg: 'Sodium',
 zinc_mg: 'Zinc',
 copper_mg: 'Copper',
 manganese_mg: 'Manganese',
 selenium_mg: 'Selenium',
 fluoride_mg: 'Fluoride',
 vitamin_a_rae_mg: 'Vitamin A',
 vitamin_b1_thiamin_mg: 'Vitamin B1',
 vitamin_b2_riboflavin_mg: 'Vitamin B2',
 vitamin_b3_niacin_mg: 'Vitamin B3',
 vitamin_b5_pantothenic_acid_mg: 'Vitamin B5',
 vitamin_b6_mg: 'Vitamin B6',
 vitamin_b12_mg: 'Vitamin B12',
 vitamin_c_mg: 'Vitamin C',
 vitamin_d_mg: 'Vitamin D',
 vitamin_e_mg: 'Vitamin E',
 vitamin_k_mg: 'Vitamin K',
};

function formatGuidelineLabel(key: string) {
 if (guidelineLabels[key]) {
 return guidelineLabels[key];
 }
 return key
 .replace(/_/g, ' ')
 .replace(/\b\w/g, (char) => char.toUpperCase());
}

function getGuidelineItems(guidelines: any): GuidelineItem[] {
 if (!guidelines?.nutrients) {
 return [];
 }

 return Object.entries(guidelines.nutrients).map(([key, value]: [string, any]) => ({
 key,
 label: formatGuidelineLabel(key),
 min: value.min,
 max: value.max,
 unit: value.unit || '',
 source: value.source || null,
 hard_soft_type: value.hard_soft_type || (value.tipe && ['range', 'max'].includes(value.tipe) ? 'HARD' : 'SOFT'),
 diseases: value.diseases || [],
 }));
}

function formatGuidelineBound(value: number | string | null | undefined) {
 if (value === null || value === undefined) {
 return 'No limit';
 }
 if (typeof value === 'number' && !Number.isFinite(value)) {
 return 'No limit';
 }
 // Format angka dengan 2 decimal places jika perlu, otherwise integer
 if (typeof value === 'number') {
 return value % 1 === 0 ? value.toString() : value.toFixed(2);
 }
 return value;
}

function formatGuidelineDisplay(item: GuidelineItem) {
 const minText = formatGuidelineBound(item.min);
 const maxText = formatGuidelineBound(item.max);

 if (item.min !== null && item.max !== null) {
 const minNumeric = typeof item.min === 'number' ? item.min : Number(item.min);
 const maxNumeric = typeof item.max === 'number' ? item.max : Number(item.max);

 // Exact value (min === max)
 if (Number.isFinite(minNumeric) && Number.isFinite(maxNumeric) && minNumeric === maxNumeric) {
 return `± ${minText} ${item.unit}`.trim();
 }

 // Both min and max are finite (range)
 if (Number.isFinite(minNumeric) && Number.isFinite(maxNumeric)) {
 return `${minText}-${maxText} ${item.unit}`.trim();
 }
 }

 // Only max is unlimited (min only)
 if (maxText === 'No limit' && minText !== 'No limit') {
 return `min. ${minText} ${item.unit}`.trim();
 }

 // Only min is unlimited (max only - rare case)
 if (minText === 'No limit' && maxText !== 'No limit') {
 return `max. ${maxText} ${item.unit}`.trim();
 }

 return `${minText}-${maxText} ${item.unit}`.trim();
}

// Fallback logic representing Python's DISEASE_MACROS logic if API fails
const DISEASE_MACROS: Record<string, { carbs: [number, number], protein: [number, number], fat: [number, number] }> = {
 normal: { carbs: [45, 65], protein: [10, 35], fat: [20, 35] },
 dm2: { carbs: [45, 55], protein: [15, 20], fat: [25, 35] },
 hypertension: { carbs: [50, 60], protein: [15, 20], fat: [25, 30] },
 cvd: { carbs: [45, 55], protein: [15, 25], fat: [20, 30] },
 cholesterol: { carbs: [45, 55], protein: [15, 20], fat: [20, 30] },
 ckd: { carbs: [50, 60], protein: [5, 10], fat: [25, 35] },
};

function calculateFallbackMacros(tdee: number, diseases: string[]) {
 const macros = { carbs: [0, 100], protein: [0, 100], fat: [0, 100] };
 const activeDiseases = diseases.length > 0 ? diseases : ['normal'];

 for (const d of activeDiseases) {
 const limits = DISEASE_MACROS[d] || DISEASE_MACROS.normal;
 macros.carbs[0] = Math.max(macros.carbs[0], limits.carbs[0]);
 macros.carbs[1] = Math.min(macros.carbs[1], limits.carbs[1]);
 macros.protein[0] = Math.max(macros.protein[0], limits.protein[0]);
 macros.protein[1] = Math.min(macros.protein[1], limits.protein[1]);
 macros.fat[0] = Math.max(macros.fat[0], limits.fat[0]);
 macros.fat[1] = Math.min(macros.fat[1], limits.fat[1]);
 }

 return {
 carbs: { pct: macros.carbs, gram: Math.round(tdee * ((macros.carbs[0] + macros.carbs[1]) / 2) / 100 / 4) },
 protein: { pct: macros.protein, gram: Math.round(tdee * ((macros.protein[0] + macros.protein[1]) / 2) / 100 / 4) },
 fat: { pct: macros.fat, gram: Math.round(tdee * ((macros.fat[0] + macros.fat[1]) / 2) / 100 / 9) }
 };
}

export function ProfileSummary({ userData, onBack, onContinue, onAnalysisComplete }: ProfileSummaryProps) {
 const [analysis, setAnalysis] = useState<any>(null);
 const [loading, setLoading] = useState(true);
 const [showOtherNutrients, setShowOtherNutrients] = useState(false);

 const dailyNeeds = calculateDailyNeeds(
 userData.weight!,
 userData.height!,
 userData.age!,
 userData.gender!,
 userData.activity!
 );

 const bmi = userData.weight / ((userData.height / 100) ** 2);
 const bmiInfo = getBmiInfo(userData.weight, userData.height);
 const isNormalBmi = bmi >= 18.5 && bmi < 25;
 const idealMin = (18.5 * (userData.height / 100) ** 2).toFixed(1);
 const idealMax = (24.9 * (userData.height / 100) ** 2).toFixed(1);
 const healthConditions = userData.healthConditions.filter((condition) => condition !== 'normal');
 const hasDiseaseGuidelines = healthConditions.length > 0;

 // Prepare guideline items and prioritize disease-specific HARD constraints
 const allGuidelineItems = getGuidelineItems(analysis?.guidelines);
 const guidelineByKey = new Map(allGuidelineItems.map((item) => [item.key, item]));
 const priorityMacroItems = priorityMacroKeys
 .map((key) => guidelineByKey.get(key))
 .filter((item): item is GuidelineItem => Boolean(item));

 const _allGuidelineItems = allGuidelineItems.filter((item) => !priorityMacroKeys.includes(item.key));
 const diseaseSpecificHardItems = hasDiseaseGuidelines
 ? _allGuidelineItems.filter((it) => it.hard_soft_type === 'HARD' && it.diseases && it.diseases.some((d: string) => healthConditions.includes(d)))
 : [];

 const priorityGuidelineItems = [...priorityMacroItems, ...diseaseSpecificHardItems];

 const remainingGuidelineItems = _allGuidelineItems.filter((it) => !priorityGuidelineItems.includes(it));
 remainingGuidelineItems.sort((a, b) => {
 const aHard = a.hard_soft_type === 'HARD' ? 0 : 1;
 const bHard = b.hard_soft_type === 'HARD' ? 0 : 1;
 if (aHard !== bHard) return aHard - bHard;
 return a.label.localeCompare(b.label);
 });
 useEffect(() => {
 async function fetchAnalysis() {
 try {
 const result = await api.analyzeProfile({
 gender: userData.gender === 'male' ? 'M' : 'F',
 age: userData.age,
 weight: userData.weight,
 height: userData.height,
 activity: userData.activity || '1.845',
 diseases: userData.healthConditions.length > 0 ? userData.healthConditions : ['normal'],
 food_preferences: userData.foodPreferences,
 algorithm: 'greedy'
 });
 setAnalysis(result);
 if (onAnalysisComplete) onAnalysisComplete(result);
 } catch (err) {
 console.error("Failed to fetch from API, using fallback logic", err);
 setAnalysis({
 macros: calculateFallbackMacros(dailyNeeds.calories, userData.healthConditions)
 });
 } finally {
 setLoading(false);
 }
 }
 fetchAnalysis();
 }, [userData, dailyNeeds.calories]);

 const displayCalories = useMemo(() => {
 const tdee = (analysis && analysis.energy && typeof analysis.energy.tdee === 'number') 
 ? Math.round(analysis.energy.tdee) 
 : Math.round(dailyNeeds.calories);

 if (!hasDiseaseGuidelines) return tdee;

 const rule = analysis?.guidelines?.nutrients?.['energy_kcal'];
 if (rule && rule.hard_soft_type === 'HARD') {
 const minVal = rule.min != null ? Math.round(rule.min) : 0;
 const maxVal = rule.max != null && Number.isFinite(rule.max) ? Math.round(rule.max) : Infinity;

 if (tdee > maxVal) return maxVal;
 if (tdee < minVal) return minVal;
 }
 return tdee;
 }, [analysis, dailyNeeds.calories, hasDiseaseGuidelines]);

 return (
 <div className="w-full">


 {loading ? (
 <div className="flex flex-col items-center justify-center py-20">
 <Loader2 className="w-12 h-12 text-primary animate-spin mb-4" />
 <p className="text-gray-600 font-medium">Calculating optimal health constraints...</p>
 </div>
 ) : (
 <div className="space-y-6">


 <div className="grid gap-6 lg:grid-cols-2">

 {/* ROW 1: Daily Energy & BMI */}
 <motion.section
 initial={{ opacity: 0, y: 10 }}
 animate={{ opacity: 1, y: 0 }}
 transition={{ delay: 0.1 }}
 className="bg-white/70 backdrop-blur-md rounded-3xl p-6 border border-border/80 shadow-xl shadow-primary/5 "
 >
 <div className="flex items-center gap-3 mb-5">
 <div className="w-11 h-11 rounded-full bg-secondary flex items-center justify-center text-primary ">
 <Scale className="w-5 h-5" />
 </div>
 <div>
 <h2 className="text-xl font-bold text-gray-900 tracking-tight">Daily Energy Needs</h2>
 <p className="text-xs text-gray-500 font-normal">Adjusted with your profile and health constraints</p>
 </div>
 </div>

 <div className="space-y-4">
 <div className="rounded-2xl bg-primary/5 p-4 border border-primary/20 ">
 <p className="text-xs text-primary font-semibold tracking-wide uppercase">Estimated daily calories</p>
 <p className="text-3xl font-bold text-primary font-serif mt-1">{displayCalories} kcal/day</p>
 <p className="text-xs text-gray-600 mt-2.5 font-normal leading-relaxed">
 Your calorie needs are derived from BMI, BMR, TDEE, activity level, and aligned with your selected health conditions.
 </p>
 </div>
 </div>
 </motion.section>

 <motion.section
 initial={{ opacity: 0, y: 10 }}
 animate={{ opacity: 1, y: 0 }}
 transition={{ delay: 0.15 }}
 className="bg-white/70 backdrop-blur-md rounded-3xl p-6 border border-border/80 shadow-xl shadow-primary/5 flex flex-col"
 >
 <div className="flex items-center gap-3 mb-5">
 <div className="w-11 h-11 rounded-full bg-secondary flex items-center justify-center text-primary ">
 <HeartPulse className="w-5 h-5" />
 </div>
 <div>
 <h2 className="text-xl font-bold text-gray-900 tracking-tight">BMI Status</h2>
 <p className="text-xs text-gray-500 font-normal">Your current BMI and ideal weight range</p>
 </div>
 </div>

 <div className="flex flex-col gap-3 sm:flex-row">
 <div
 className="rounded-2xl p-4 border flex-1"
 style={{
 borderColor: isNormalBmi ? '#2d5a27' : bmi < 18.5 || bmi >= 25 ? '#c98a0c' : '#cb2d2d',
 }}
 >
 <p className={`text-xs font-semibold uppercase tracking-wider ${bmiInfo.text}`}>{bmiInfo.label}</p>
 <p className={`text-4xl font-bold mt-1 font-serif ${bmiInfo.text}`}>{bmi.toFixed(1)}</p>
 <span className={`inline-block mt-3 px-3 py-1 rounded-full text-xs font-semibold bg-primary/10 text-primary `}>
 Body Mass Index
 </span>
 </div>

 {!isNormalBmi && (
 <div className="rounded-2xl bg-secondary/35 border border-border/70 p-4 sm:w-[220px] flex-shrink-0">
 <p className="text-xs text-gray-500 font-semibold uppercase tracking-wide">Ideal Range</p>
 <p className="text-base font-bold text-gray-900 mt-1 font-serif">{idealMin} kg - {idealMax} kg</p>
 <p className="text-xs text-gray-500 mt-2 font-normal leading-relaxed">{bmiInfo.note}</p>
 </div>
 )}
 </div>
 </motion.section>

 {/* ROW 2: Health Guidelines & Nutrition Constraints */}
 <motion.section
 initial={{ opacity: 0, y: 10 }}
 animate={{ opacity: 1, y: 0 }}
 transition={{ delay: 0.2 }}
 className="bg-white/70 backdrop-blur-md rounded-3xl p-6 border border-border/80 shadow-xl shadow-primary/5 lg:col-span-2"
 >
 <div className="flex items-center gap-3 mb-5">
 <div className="w-11 h-11 rounded-full bg-secondary flex items-center justify-center text-primary ">
 <FileText className="w-5 h-5" />
 </div>
 <div>
 <h2 className="text-xl font-bold text-gray-900 tracking-tight">Health Guidelines</h2>
 <p className="text-xs text-gray-500 font-normal">Carbs, protein, fat, and all other nutrient boundaries</p>
 </div>
 </div>

 <div className="space-y-5">
 {priorityGuidelineItems.length > 0 && (
 <div className="rounded-2xl bg-transparent p-4 border border-red-550/20 mb-4">
 <p className="text-xs font-bold text-destructive/80 uppercase tracking-wider mb-3">Priority guidelines for your condition</p>
 <div className="grid gap-3 grid-cols-2 sm:grid-cols-3 lg:grid-cols-6">
 {priorityGuidelineItems.map((item) => (
 <div
 key={item.key}
 className={
 item.key === 'energy_kcal'
 ? 'rounded-xl bg-primary text-primary-foreground p-2.5 border border-primary/20 shadow-md hover:shadow-lg hover:-translate-y-0.5 transition-all duration-300'
 : isEnergyOrMacroKey(item.key)
 ? 'rounded-xl bg-destructive text-destructive-foreground p-2.5 border border-destructive/20 shadow-md hover:shadow-lg hover:-translate-y-0.5 transition-all duration-300'
 : 'rounded-xl bg-red-500/10 p-2.5 border border-red-500/15 shadow-sm hover:shadow-md hover:-translate-y-0.5 transition-all duration-300'
 }
 >
 <div className="flex items-center justify-between">
 <p className="text-xs font-bold truncate">{item.label}</p>
 </div>
 <p className="text-[11px] font-semibold mt-1 font-serif">{formatGuidelineDisplay(item)}</p>
 </div>
 ))}
 </div>
 </div>
 )}

 <div className="rounded-2xl bg-secondary/35 border border-border/70 overflow-hidden">
 <button
 type="button"
 onClick={() => setShowOtherNutrients(!showOtherNutrients)}
 className="w-full flex items-center justify-between p-4 hover:bg-secondary/50 :bg-slate-900/60 transition-colors text-left focus:outline-none cursor-pointer"
 >
 <div>
 <p className="text-xs font-bold text-gray-500 uppercase tracking-wider">Other nutrient limits</p>
 <p className="text-[10px] text-gray-450 mt-0.5">Click to view additional nutrient limits and guidelines</p>
 </div>
 <ChevronDown className={`w-4 h-4 text-gray-500 transition-transform duration-350 ${showOtherNutrients ? 'transform rotate-180' : ''}`} />
 </button>

 {showOtherNutrients && (
 <div className="px-4 pb-4 pt-1 border-t border-border/40 ">
 {remainingGuidelineItems.length > 0 ? (
 <div className="grid gap-3 grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 mt-3">
 {remainingGuidelineItems.map((item) => (
 <div key={item.key} className="rounded-xl bg-white p-2.5 border border-border shadow-sm hover:shadow-md transition-shadow">
 <div className="flex items-center justify-between">
 <p className="text-xs font-bold text-gray-800 truncate">{item.label}</p>
 </div>
 <p className="text-[11px] text-gray-500 mt-1 font-semibold font-serif">{formatGuidelineDisplay(item)}</p>
 </div>
 ))}
 </div>
 ) : (
 <p className="text-sm text-gray-600 font-normal mt-2">No additional nutrient limits available.</p>
 )}
 </div>
 )}
 </div>

 {hasDiseaseGuidelines && (
 <div className="rounded-2xl border border-primary/20 bg-primary/5 p-5 space-y-4">
 <div className="flex items-start gap-2.5">
 <div className="w-1.5 h-5 rounded bg-primary shrink-0 mt-0.5" />
 <div>
 <h3 className="text-sm font-bold text-primary tracking-wide uppercase">
 Adjusted Health Guidelines
 </h3>
 <p className="text-xs text-gray-600 mt-0.5">
 Your nutritional targets have been customized based on your medical conditions:
 </p>
 </div>
 </div>

 <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
 {healthConditions.map((condition) => {
 const label = conditionLabels[condition] || condition;
 const guideline = conditionGuidelines[condition] || '';
 if (!guideline) return null;

 return (
 <div
 key={condition}
 className="bg-white/60 rounded-xl p-4 border border-primary/10 flex flex-col justify-between"
 >
 <div>
 <span className="inline-block px-2.5 py-0.5 text-[10px] font-bold tracking-wide uppercase rounded-full bg-primary/10 text-primary mb-2">
 {label}
 </span>
 <p className="text-xs text-gray-750 font-normal leading-relaxed">
 {guideline}
 </p>
 </div>
 </div>
 );
 })}
 </div>
 </div>
 )}
 </div>
 </motion.section>

 </div>
 </div>
 )}

  <div className="flex flex-col-reverse sm:flex-row gap-3 justify-between mt-8">
  <button
  onClick={onBack}
  className="w-full sm:w-auto px-6 py-3 rounded-2xl font-semibold transition-all hover:bg-secondary :bg-slate-800 border border-border text-gray-900 flex items-center justify-center gap-2 cursor-pointer text-sm"
  >
  <ArrowLeft className="w-5 h-5" />
  Back to Profile Input
  </button>

  <button
  onClick={onContinue}
  disabled={loading}
  className="w-full sm:w-auto px-6 py-3 bg-primary text-primary-foreground rounded-2xl font-semibold hover:bg-primary/95 transition-all flex items-center justify-center gap-2 shadow-md hover:shadow-lg hover:shadow-primary/10 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer text-sm"
  >
  Next
  <ArrowRight className="w-5 h-5" />
  </button>
  </div>
 </div>
 );
}
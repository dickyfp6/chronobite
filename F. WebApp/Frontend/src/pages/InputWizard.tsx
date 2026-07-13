/**
 * ==============================================================================
 * InputWizard.tsx - Formulir Input Data Pasien
 * ==============================================================================
 * Komponen berbentuk "Wizard" (formulir bertahap) untuk mengambil data vital 
 * pengguna seperti jenis kelamin, usia, berat badan, tinggi, tingkat aktivitas,
 * preferensi makanan, dan riwayat penyakit bawaan (komorbid).
 * Data yang diisi divalidasi sebelum dilanjutkan ke halaman berikutnya.
 * ==============================================================================
 */
import { useState, useEffect } from 'react';
import { motion } from 'motion/react';
import { User, Activity, Heart, UtensilsCrossed, ClipboardList, FileText, ChevronRight, ChevronLeft, Calendar, Scale, Ruler, Footprints, Flame, Leaf, Droplet, TrendingDown, Shield, Plus, Minus } from 'lucide-react';
import { t } from '../utils/translations';
import { IconCard } from '../components/figma/IconCard';

export interface UserInputData {
 gender?: 'male' | 'female';
 age: number;
 weight: number;
 height: number;
 activity?: 'light' | 'moderate' | 'heavy';
 healthConditions: string[];
 foodPreferences: string[];
}

interface InputWizardProps {
 data: UserInputData;
 onUpdate: (data: Partial<UserInputData>) => void;
 onComplete: () => void;
}

export function InputWizard({ data, onUpdate, onComplete }: InputWizardProps) {
 const [step, setStep] = useState(() => {
 const saved = sessionStorage.getItem('dss_wizard_step');
 const parsed = saved ? parseInt(saved, 10) : 0;
 return parsed >= 0 && parsed <= 3 ? parsed : 0;
 });

 const [editing, setEditing] = useState<null | 'age' | 'weight' | 'height'>(null);
 const [tempValue, setTempValue] = useState<string>('');


 // Persist step to sessionStorage so refresh keeps the current wizard step in this tab only
 useEffect(() => {
 sessionStorage.setItem('dss_wizard_step', step.toString());
 }, [step]);

 const steps = t.input.steps;

 const canProceed = () => {
 switch (step) {
 case 0: return !!(data.gender && data.activity);
 case 1: return !!(data.age >= 18 && data.weight >= 30 && data.height >= 100);
 case 2: return data.healthConditions.length > 0;
 case 3: return true;
 default: return false;
 }
 };

 const next = () => {
 if (step < 3) setStep(step + 1);
 else onComplete();
 };

 const back = () => {
 if (step > 0) setStep(step - 1);
 };

 const selectGender = (gender: 'male' | 'female') => {
 onUpdate({ gender });
 };

 const selectActivity = (activity: 'light' | 'moderate' | 'heavy') => {
 onUpdate({ activity });
 };

 const isStepAccessible = (targetStep: number) => {
 if (targetStep === 0) return true;
 for (let i = 0; i < targetStep; i++) {
 if (i === 0 && !(data.gender && data.activity)) return false;
 if (i === 1 && !(data.age >= 18 && data.weight >= 30 && data.height >= 100)) return false;
 if (i === 2 && data.healthConditions.length === 0) return false;
 }
 return true;
 };

 const handleStepClick = (targetStep: number) => {
 if (isStepAccessible(targetStep)) {
 setStep(targetStep);
 }
 };

 const getStepSummary = (stepIndex: number) => {
 switch (stepIndex) {
 case 0:
 if (!data.gender) return '';
 const genLabel = data.gender === 'male' ? t.input.gender.male : t.input.gender.female;
 const actLabel = data.activity ? (t.input.activity[data.activity] || data.activity) : '';
 return actLabel ? `${genLabel} • ${actLabel}` : genLabel;
 case 1:
 const hasMetrics = data.age >= 18 && data.weight >= 30 && data.height >= 100;
 return hasMetrics ? `${data.age} yrs • ${data.weight} kg • ${data.height} cm` : '';
 case 2:
 if (data.healthConditions.length === 0) return '';
 return data.healthConditions.map(c => t.input.health[c as keyof typeof t.input.health] || c).join(', ');
 case 3:
 if (data.foodPreferences.length === 0) return 'All Cuisines';
 return data.foodPreferences.map(p => t.input.preferences[p as keyof typeof t.input.preferences] || p).join(', ');
 default:
 return '';
 }
 };

 const toggleHealthCondition = (condition: string) => {
 const isNormal = condition === 'normal';
 const isSelected = data.healthConditions.includes(condition);

 if (isNormal) {
 if (isSelected) {
 onUpdate({ healthConditions: [] });
 } else {
 onUpdate({ healthConditions: ['normal'] });
 }
 } else {
 let conditions = data.healthConditions.filter(c => c !== 'normal');
 if (conditions.includes(condition)) {
 conditions = conditions.filter(c => c !== condition);
 } else if (conditions.length < 3) {
 conditions.push(condition);
 }
 onUpdate({ healthConditions: conditions });
 }
 };

 const toggleFoodPreference = (pref: string) => {
 const prefs = data.foodPreferences.includes(pref)
 ? data.foodPreferences.filter(p => p !== pref)
 : [...data.foodPreferences, pref];
 onUpdate({ foodPreferences: prefs });
 };

  return (
  <div className="min-h-[calc(100vh-4rem)] relative bg-background px-4 sm:px-6 lg:px-8 pb-8 pt-0 lg:pt-8 flex items-start justify-center overflow-clip">
  {/* Mature Background Texture */}
  <div className="absolute inset-0 z-0 pointer-events-none overflow-hidden">
    {/* Base: soft warm-green gradient wash */}
    <div className="absolute inset-0 bg-gradient-to-br from-[#f4f8f4] via-[#f8faf5] to-[#eef5ee]" />

    {/* Fine crosshatch / linen grid */}
    <div
      className="absolute inset-0 opacity-[0.045]"
      style={{
        backgroundImage: `
          linear-gradient(rgba(45,90,39,0.8) 1px, transparent 1px),
          linear-gradient(90deg, rgba(45,90,39,0.8) 1px, transparent 1px)
        `,
        backgroundSize: '32px 32px'
      }}
    />

    {/* Diagonal accent lines (like luxury paper) */}
    <div
      className="absolute inset-0 opacity-[0.025]"
      style={{
        backgroundImage: `repeating-linear-gradient(
          -45deg,
          rgba(45,90,39,1) 0px,
          rgba(45,90,39,1) 1px,
          transparent 1px,
          transparent 18px
        )`
      }}
    />

    {/* SVG noise grain overlay for paper/canvas texture */}
    <svg className="absolute inset-0 w-full h-full opacity-[0.08]" xmlns="http://www.w3.org/2000/svg">
      <filter id="wizard-noise">
        <feTurbulence type="fractalNoise" baseFrequency="0.72" numOctaves="4" stitchTiles="stitch"/>
        <feColorMatrix type="saturate" values="0"/>
      </filter>
      <rect width="100%" height="100%" filter="url(#wizard-noise)" />
    </svg>

    {/* Soft edge vignette */}
    <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_transparent_50%,_rgba(0,0,0,0.04)_100%)]" />
  </div>

  <div className="w-full max-w-[1600px] relative z-10">
 <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
 {/* Left Side: Interactive Vertical Stepper (sticky sub-navbar on mobile) */}
 <div className="sticky top-16 z-30 lg:col-span-3 flex flex-row lg:flex-col overflow-x-auto lg:overflow-x-visible scrollbar-none gap-3 lg:gap-0 -mx-4 px-4 sm:-mx-6 sm:px-6 lg:mx-0 lg:px-5 py-3 lg:py-5 bg-white/95 lg:bg-white/50 lg:backdrop-blur-md border-b border-border/50 lg:border lg:border-border/80 rounded-none lg:rounded-3xl shadow-sm lg:shadow-lg lg:shadow-primary/5">
 {(() => {
 const allSteps = [
 { id: 'profile-input-0', label: steps[0], summary: getStepSummary(0), isFuture: false, index: 0 },
 { id: 'profile-input-1', label: steps[1], summary: getStepSummary(1), isFuture: false, index: 1 },
 { id: 'profile-input-2', label: steps[2], summary: getStepSummary(2), isFuture: false, index: 2 },
 { id: 'profile-input-3', label: steps[3], summary: getStepSummary(3), isFuture: false, index: 3 },
 { id: 'summary-peek', label: t.input.sidebar?.summary || 'Summary', summary: 'Nutrition constraints', isFuture: true, icon: FileText },
 { id: 'meals-peek', label: t.results?.title || 'Meal Plan', summary: 'Recommended menus', isFuture: true, icon: UtensilsCrossed },
 { id: 'report-peek', label: t.report?.title || 'Complete Report', summary: 'Detailed analysis', isFuture: true, icon: ClipboardList },
];

 return allSteps.map((item, index) => {
 if (!item.isFuture) {
 const idx = item.index!;
 const active = idx === step;
 const accessible = isStepAccessible(idx);
 const summary = item.summary;
 const isCompleted = (() => {
 if (idx === step) return false;
 if (idx === 0) return !!data.gender;
 if (idx === 1) return !!(data.age >= 18 && data.weight >= 30 && data.height >= 100);
 if (idx === 2) return !!data.activity;
 if (idx === 3) return data.healthConditions.length > 0;
 return false;
 })();

 return (
 <button
 key={item.id}
 disabled={!accessible}
 onClick={() => handleStepClick(idx)}
 className={`relative flex flex-row items-center lg:items-start text-left gap-2.5 lg:gap-3 p-2 lg:p-3 rounded-xl lg:rounded-2xl transition-all min-w-max lg:min-w-0 flex-1 lg:flex-none border border-transparent ${
 active
 ? 'bg-primary/10 text-primary border-primary/25 font-bold shadow-sm'
 : accessible
 ? 'hover:bg-white/80 text-gray-700 cursor-pointer'
 : 'opacity-40 text-gray-400 cursor-not-allowed'
 }`}
 >
 {/* Vertical Connection Line on Desktop */}
 {index < allSteps.length - 1 && (
 <div className="hidden lg:block absolute left-8 top-12 bottom-0 w-0.5 bg-border -mb-6 z-0" />
 )}

 {/* Icon Indicator */}
 <div
 className={`w-8 h-8 lg:w-10 lg:h-10 rounded-full flex items-center justify-center text-xs lg:text-sm font-bold shadow-sm z-10 shrink-0 transition-all ${
 isCompleted
 ? 'bg-primary text-primary-foreground'
 : active
 ? 'bg-primary text-primary-foreground ring-4 ring-primary/25 scale-105'
 : 'bg-secondary text-muted-foreground '
 }`}
 >
 {isCompleted ? <span className="text-xs font-extrabold">✓</span> : idx + 1}
 </div>

 <div className="flex-1 min-w-0 text-left z-10">
 <p className={`text-xs lg:text-sm tracking-tight ${active ? 'font-bold text-primary ' : 'font-semibold'}`}>
 {item.label}
 </p>
 {summary && (
 <p className="text-[10px] lg:text-xs text-gray-500 font-normal truncate max-w-[100px] lg:max-w-[200px] mt-0.5 hidden lg:block">
 {summary}
 </p>
 )}
 </div>
 </button>
 );
 } else {
 const Icon = item.icon!;
 return (
 <div
 key={item.id}
 className="relative flex flex-row items-center lg:items-start text-left gap-2.5 lg:gap-3 p-2 lg:p-3 rounded-xl lg:rounded-2xl transition-all min-w-max lg:min-w-0 flex-1 lg:flex-none border border-transparent opacity-25 text-gray-400 cursor-not-allowed"
 >
 {/* Vertical Connection Line on Desktop */}
 {index < allSteps.length - 1 && (
 <div className="hidden lg:block absolute left-8 top-12 bottom-0 w-0.5 bg-border -mb-6 z-0" />
 )}

 {/* Icon Indicator */}
 <div className="w-8 h-8 lg:w-10 lg:h-10 rounded-full flex items-center justify-center bg-secondary text-muted-foreground shadow-sm z-10 shrink-0">
 <Icon className="w-4 h-4 lg:w-5 h-5" />
 </div>

 <div className="flex-1 min-w-0 text-left z-10">
 <p className="text-xs lg:text-sm tracking-tight font-semibold">
 {item.label}
 </p>
 <p className="text-[10px] lg:text-xs text-gray-500 font-normal truncate max-w-[100px] lg:max-w-[200px] mt-0.5 hidden lg:block">
 {item.summary}
 </p>
 </div>
 </div>
 );
 }
 });
 })()}
 </div>

 {/* Right Side: Active Step Card Container */}
 <div className="lg:col-span-9 flex flex-col gap-6">
  <motion.div
  key={step}
  initial={{ opacity: 0, x: 15 }}
  animate={{ opacity: 1, x: 0 }}
  exit={{ opacity: 0, x: -15 }}
  className="relative bg-white/70 backdrop-blur-xl rounded-3xl p-6 sm:p-10 lg:p-12 border border-white/60 shadow-[0_8px_30px_rgb(0,0,0,0.04)] min-h-[360px] flex flex-col justify-between overflow-clip group"
  >
  {/* Card Aesthetic Textures */}
  <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-primary/10 to-transparent rounded-bl-full pointer-events-none opacity-60 transition-opacity duration-700 group-hover:opacity-100"></div>
  <div className="absolute bottom-0 left-0 w-48 h-48 bg-gradient-to-tr from-emerald-500/10 to-transparent rounded-tr-full pointer-events-none opacity-60 transition-opacity duration-700 group-hover:opacity-100"></div>
  <div className="absolute inset-0 bg-gradient-to-b from-white/40 via-transparent to-white/20 pointer-events-none z-0"></div>

  {/* Form Contents */}
  <div className="flex-1 relative z-10">
 {step === 0 && (
 <div className="w-full grid grid-cols-1 xl:grid-cols-2 gap-8 xl:gap-12">
 {/* Gender Selection Section */}
 <div className="space-y-4 h-full flex flex-col">
 <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
 <User className="w-5 h-5 text-primary" />
 {t.input.gender.title}
 </h3>
 <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-1 gap-4 sm:gap-6 w-full flex-1">
 <IconCard
 icon={(props: any) => (
 <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" {...props}>
 <path d="M12 12a5 5 0 1 0 0-10 5 5 0 0 0 0 10Z" />
 <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
 {/* Subtle tie/collar to distinguish male */}
 <path d="m9 15 3 4 3-4" /> 
 </svg>
 )}
 title={t.input.gender.male}
 selected={data.gender === 'male'}
 onClick={() => selectGender('male')}
 backgroundImage="https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?auto=format&fit=crop&w=600&q=80"
 />
 <IconCard
 icon={(props: any) => (
 <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" {...props}>
 <path d="M12 12a5 5 0 1 0 0-10 5 5 0 0 0 0 10Z" />
 <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
 {/* Subtle hair lines to distinguish female */}
 <path d="M8.5 12c-1.5 1.5-2.5 4-2.5 9" />
 <path d="M15.5 12c1.5 1.5 2.5 4 2.5 9" />
 </svg>
 )}
 title={t.input.gender.female}
 selected={data.gender === 'female'}
 onClick={() => selectGender('female')}
 backgroundImage="https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=600&q=80"
 />
 </div>
 </div>

 {/* Divider - Mobile only */}
 <div className="xl:hidden border-t border-border/70 " />

 {/* Activity Selection Section */}
 <div className="space-y-4 h-full flex flex-col">
 <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
 <Activity className="w-5 h-5 text-primary" />
 {t.input.activity.title}
 </h3>
 <div className="grid grid-cols-1 sm:grid-cols-3 xl:grid-cols-1 gap-4 sm:gap-6 w-full flex-1">
 <IconCard
 icon={Footprints}
 title={t.input.activity.light}
 description={t.input.activity.lightDesc}
 selected={data.activity === 'light'}
 onClick={() => selectActivity('light')}
 backgroundImage="https://images.unsplash.com/photo-1506126613408-eca07ce68773?auto=format&fit=crop&w=600&q=80"
 />
 <IconCard
 icon={Activity}
 title={t.input.activity.moderate}
 description={t.input.activity.moderateDesc}
 selected={data.activity === 'moderate'}
 onClick={() => selectActivity('moderate')}
 backgroundImage="https://images.unsplash.com/photo-1476480862126-209bfaa8edc8?auto=format&fit=crop&w=600&q=80"
 />
 <IconCard
 icon={Flame}
 title={t.input.activity.heavy}
 description={t.input.activity.heavyDesc}
 selected={data.activity === 'heavy'}
 onClick={() => selectActivity('heavy')}
 backgroundImage="https://images.unsplash.com/photo-1517838277536-f5f99be501cd?auto=format&fit=crop&w=600&q=80"
 />
 </div>
 </div>
 </div>
 )}

 {step === 1 && (
 <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12 items-center w-full">
 {/* Left Column: Sliders */}
 <div className="lg:col-span-8 space-y-10 w-full">
        {/* Age Slider */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <label className="text-sm font-medium flex items-center gap-2 text-gray-900">
              <div className="w-10 h-10 rounded-full bg-secondary flex items-center justify-center shrink-0">
                <Calendar className="w-5 h-5 text-primary" />
              </div>
              <span className="whitespace-nowrap">{t.input.metrics.age}</span>
            </label>
            <span className="text-2xl font-bold text-primary min-w-[60px] text-center font-serif select-none">
              {editing === 'age' ? (
                <input
                  autoFocus
                  className="w-[60px] text-center bg-transparent outline-none border-b border-primary"
                  type="number"
                  min={18}
                  max={100}
                  value={tempValue}
                  onChange={(e) => setTempValue(e.target.value)}
                  onBlur={() => {
                    const v = Math.max(18, Math.min(100, parseInt(tempValue || '18')));
                    onUpdate({ age: Number.isFinite(v) ? v : 18 });
                    setEditing(null);
                  }}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      (e.target as HTMLInputElement).blur();
                    } else if (e.key === 'Escape') {
                      setEditing(null);
                    }
                  }}
                />
              ) : (
                <button
                  onClick={() => {
                    setEditing('age');
                    setTempValue(String(data.age));
                  }}
                  className="w-full cursor-pointer hover:opacity-80 font-serif"
                >
                  {data.age}
                </button>
              )}
            </span>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => onUpdate({ age: Math.max(18, data.age - 1) })}
              className="w-8 h-8 rounded-full bg-secondary hover:bg-muted :bg-slate-700 text-primary transition-all flex items-center justify-center shadow-sm hover:shadow cursor-pointer select-none shrink-0"
            >
              <Minus className="w-3.5 h-3.5" />
            </button>
            <div className="relative flex-1 flex items-center group">
              <input
                type="range"
                min="18"
                max="100"
                value={data.age}
                onChange={(e) => onUpdate({ age: parseInt(e.target.value) })}
                className="w-full cursor-pointer dss-slider peer"
                style={{
                  background: `linear-gradient(to right, #2d5a27 0%, #558550 ${((data.age - 18) / (100 - 18)) * 100}%, #d2dfd5 ${((data.age - 18) / (100 - 18)) * 100}%, #d2dfd5 100%)`,
                  borderRadius: '9999px'
                }}
              />
              <div 
                className="absolute -top-11 flex flex-col items-center opacity-0 peer-hover:opacity-100 peer-active:opacity-100 transition-opacity duration-200 pointer-events-none z-10 drop-shadow-md"
                style={{
                  left: `calc(${((data.age - 18) / (100 - 18)) * 100}% + ${13 - (((data.age - 18) / (100 - 18)) * 26)}px)`,
                  transform: 'translateX(-50%)'
                }}
              >
                <div className="bg-white px-3 py-1 rounded-full text-xs font-bold text-primary shadow-sm border border-gray-100">
                  {data.age}
                </div>
                <div className="w-2 h-2 bg-white rotate-45 -mt-1.5 border-r border-b border-gray-100"></div>
              </div>
            </div>
            <button
              onClick={() => onUpdate({ age: Math.min(100, data.age + 1) })}
              className="w-8 h-8 rounded-full bg-secondary hover:bg-muted :bg-slate-700 text-primary transition-all flex items-center justify-center shadow-sm hover:shadow cursor-pointer select-none shrink-0"
            >
              <Plus className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* Weight Slider */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <label className="text-sm font-medium flex items-center gap-2 text-gray-900">
              <div className="w-10 h-10 rounded-full bg-secondary flex items-center justify-center shrink-0">
                <Scale className="w-5 h-5 text-primary" />
              </div>
              <span className="whitespace-nowrap">{t.input.metrics.weight}</span>
            </label>
            <span className="text-2xl font-bold text-primary min-w-[60px] text-center font-serif select-none">
              {editing === 'weight' ? (
                <input
                  autoFocus
                  className="w-[60px] text-center bg-transparent outline-none border-b border-primary"
                  type="number"
                  min={30}
                  max={200}
                  value={tempValue}
                  onChange={(e) => setTempValue(e.target.value)}
                  onBlur={() => {
                    const v = Math.max(30, Math.min(200, parseFloat(tempValue || '30')));
                    onUpdate({ weight: Number.isFinite(v) ? v : 30 });
                    setEditing(null);
                  }}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') (e.target as HTMLInputElement).blur();
                    if (e.key === 'Escape') setEditing(null);
                  }}
                />
              ) : (
                <button
                  onClick={() => {
                    setEditing('weight');
                    setTempValue(String(data.weight));
                  }}
                  className="w-full cursor-pointer hover:opacity-80 font-serif"
                >
                  {data.weight}
                </button>
              )}
            </span>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => onUpdate({ weight: Math.max(30, data.weight - 1) })}
              className="w-8 h-8 rounded-full bg-secondary hover:bg-muted :bg-slate-700 text-primary transition-all flex items-center justify-center shadow-sm hover:shadow cursor-pointer select-none shrink-0"
            >
              <Minus className="w-3.5 h-3.5" />
            </button>
            <div className="relative flex-1 flex items-center group">
              <input
                type="range"
                min="30"
                max="200"
                value={data.weight}
                onChange={(e) => onUpdate({ weight: parseFloat(e.target.value) })}
                className="w-full cursor-pointer dss-slider peer"
                style={{
                  background: `linear-gradient(to right, #2d5a27 0%, #558550 ${((data.weight - 30) / (200 - 30)) * 100}%, #d2dfd5 ${((data.weight - 30) / (200 - 30)) * 100}%, #d2dfd5 100%)`,
                  borderRadius: '9999px'
                }}
              />
              <div 
                className="absolute -top-11 flex flex-col items-center opacity-0 peer-hover:opacity-100 peer-active:opacity-100 transition-opacity duration-200 pointer-events-none z-10 drop-shadow-md"
                style={{
                  left: `calc(${((data.weight - 30) / (200 - 30)) * 100}% + ${13 - (((data.weight - 30) / (200 - 30)) * 26)}px)`,
                  transform: 'translateX(-50%)'
                }}
              >
                <div className="bg-white px-3 py-1 rounded-full text-xs font-bold text-primary shadow-sm border border-gray-100">
                  {data.weight}
                </div>
                <div className="w-2 h-2 bg-white rotate-45 -mt-1.5 border-r border-b border-gray-100"></div>
              </div>
            </div>
            <button
              onClick={() => onUpdate({ weight: Math.min(200, data.weight + 1) })}
              className="w-8 h-8 rounded-full bg-secondary hover:bg-muted :bg-slate-700 text-primary transition-all flex items-center justify-center shadow-sm hover:shadow cursor-pointer select-none shrink-0"
            >
              <Plus className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* Height Slider */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <label className="text-sm font-medium flex items-center gap-2 text-gray-900">
              <div className="w-10 h-10 rounded-full bg-secondary flex items-center justify-center shrink-0">
                <Ruler className="w-5 h-5 text-primary" />
              </div>
              <span className="whitespace-nowrap">{t.input.metrics.height}</span>
            </label>
            <span className="text-2xl font-bold text-primary min-w-[60px] text-center font-serif select-none">
              {editing === 'height' ? (
                <input
                  autoFocus
                  className="w-[60px] text-center bg-transparent outline-none border-b border-primary"
                  type="number"
                  min={100}
                  max={300}
                  value={tempValue}
                  onChange={(e) => setTempValue(e.target.value)}
                  onBlur={() => {
                    const v = Math.max(100, Math.min(300, parseFloat(tempValue || '100')));
                    onUpdate({ height: Number.isFinite(v) ? v : 100 });
                    setEditing(null);
                  }}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') (e.target as HTMLInputElement).blur();
                    if (e.key === 'Escape') setEditing(null);
                  }}
                />
              ) : (
                <button
                  onClick={() => {
                    setEditing('height');
                    setTempValue(String(data.height));
                  }}
                  className="w-full cursor-pointer hover:opacity-80 font-serif"
                >
                  {data.height}
                </button>
              )}
            </span>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => onUpdate({ height: Math.max(100, data.height - 1) })}
              className="w-8 h-8 rounded-full bg-secondary hover:bg-muted :bg-slate-700 text-primary transition-all flex items-center justify-center shadow-sm hover:shadow cursor-pointer select-none shrink-0"
            >
              <Minus className="w-3.5 h-3.5" />
            </button>
            <div className="relative flex-1 flex items-center group">
              <input
                type="range"
                min="100"
                max="300"
                value={data.height}
                onChange={(e) => onUpdate({ height: parseFloat(e.target.value) })}
                className="w-full cursor-pointer dss-slider peer"
                style={{
                  background: `linear-gradient(to right, #2d5a27 0%, #558550 ${((data.height - 100) / (300 - 100)) * 100}%, #d2dfd5 ${((data.height - 100) / (300 - 100)) * 100}%, #d2dfd5 100%)`,
                  borderRadius: '9999px'
                }}
              />
              <div 
                className="absolute -top-11 flex flex-col items-center opacity-0 peer-hover:opacity-100 peer-active:opacity-100 transition-opacity duration-200 pointer-events-none z-10 drop-shadow-md"
                style={{
                  left: `calc(${((data.height - 100) / (300 - 100)) * 100}% + ${13 - (((data.height - 100) / (300 - 100)) * 26)}px)`,
                  transform: 'translateX(-50%)'
                }}
              >
                <div className="bg-white px-3 py-1 rounded-full text-xs font-bold text-primary shadow-sm border border-gray-100">
                  {data.height}
                </div>
                <div className="w-2 h-2 bg-white rotate-45 -mt-1.5 border-r border-b border-gray-100"></div>
              </div>
            </div>
            <button
              onClick={() => onUpdate({ height: Math.min(300, data.height + 1) })}
              className="w-8 h-8 rounded-full bg-secondary hover:bg-muted :bg-slate-700 text-primary transition-all flex items-center justify-center shadow-sm hover:shadow cursor-pointer select-none shrink-0"
            >
              <Plus className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
 </div>

 {/* Right Column: BMI Visual Indicator */}
 <div className="lg:col-span-4 w-full flex flex-col justify-center h-full">
 {data.weight > 0 && data.height > 0 && (
 <motion.div
 initial={{ opacity: 0, scale: 0.95 }}
 animate={{ opacity: 1, scale: 1 }}
 className="p-6 sm:p-8 rounded-2xl text-center shadow-lg transition-all duration-500 flex flex-col justify-center min-h-[180px] lg:min-h-[260px] w-full text-white"
 style={{
 backgroundColor: (() => {
 const bmi = data.weight / ((data.height / 100) ** 2);
 if (bmi >= 30) return '#991b1b'; // Dark Red
 if (bmi >= 25) return '#b45309'; // Dark Orange
 if (bmi >= 18.5) return '#2d5a27'; // Primary Green (Website Color)
 return '#b45309'; // Dark Orange for Underweight
 })(),
 }}
 >
 <p className="text-xs mb-1 font-medium tracking-wider uppercase text-white/90">
 Body Mass Index
 </p>
 <p className="text-5xl lg:text-[64px] font-bold font-serif leading-none my-2 lg:my-4 text-white drop-shadow-sm">
 {(data.weight / ((data.height / 100) ** 2)).toFixed(1)}
 </p>
 <p className="mt-2 text-sm lg:text-lg font-semibold text-white/95">
 {(() => {
 const bmi = data.weight / ((data.height / 100) ** 2);
 if (bmi < 18.5) return 'Underweight (<18.5)';
 if (bmi <= 24.9) return 'Normal (18.5–24.9)';
 if (bmi <= 29.9) return 'Overweight (25.0–29.9)';
 if (bmi <= 34.9) return 'Obesity Class I (30.0–34.9)';
 if (bmi <= 39.9) return 'Obesity Class II (35.0–39.9)';
 return 'Obesity Class III (≥40.0)';
 })()}
 </p>
 </motion.div>
 )}
 </div>
 </div>
 )}

 {step === 2 && (
 <div>
 <p className="text-base text-gray-500 text-center mb-8 font-normal">{t.input.health.subtitle}</p>
 <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 sm:gap-5">
 {['normal', 'dm2', 'hypertension', 'cvd', 'cholesterol', 'ckd'].map((condition) => {
 const getHealthIcon = (c: string) => {
  switch (c) {
 case 'normal': return Leaf;
 case 'dm2': return Droplet;
 case 'hypertension': return Activity;
 case 'cvd': return Heart;
 case 'cholesterol': return TrendingDown;
 case 'ckd': return Shield;
 default: return Heart;
 }
 };
 const getHealthDescription = (c: string) => {
 switch (c) {
 case 'normal': return 'Healthy eating guidelines for general well-being';
 case 'dm2': return 'Manage blood glucose levels and carbohydrate intake';
 case 'hypertension': return 'Lower blood pressure with sodium-restricted meals';
 case 'cvd': return 'Support cardiovascular health and lower saturated fats';
 case 'cholesterol': return 'Reduce cholesterol levels with fiber-rich options';
 case 'ckd': return 'Specifically for non-hemodialysis patients';
 default: return undefined;
 }
 };
 return (
 <IconCard
 key={condition}
 icon={getHealthIcon(condition)}
 title={t.input.health[condition as keyof typeof t.input.health] as string}
 description={getHealthDescription(condition)}
 className="h-full"
 iconBgSelectedClass={condition === 'normal' ? 'bg-blue-900' : undefined}
 iconBgUnselectedClass={condition === 'normal' ? 'bg-blue-900/80' : undefined}
 selected={data.healthConditions.includes(condition)}
 disabled={
 (condition === 'normal' && data.healthConditions.some(c => c !== 'normal')) ||
 (condition !== 'normal' && data.healthConditions.includes('normal')) ||
 (condition !== 'normal' && !data.healthConditions.includes(condition) &&
 data.healthConditions.filter(c => c !== 'normal').length >= 3)
 }
 onClick={() => toggleHealthCondition(condition)}
 backgroundImage={
    condition === 'normal' ? 'https://images.unsplash.com/photo-1506126613408-eca07ce68773?auto=format&fit=crop&w=600&q=80' : 
    condition === 'dm2' ? 'https://images.unsplash.com/photo-1490645935967-10de6ba17061?auto=format&fit=crop&w=600&q=80' : 
    condition === 'hypertension' ? 'https://images.unsplash.com/photo-1518611012118-696072aa579a?auto=format&fit=crop&w=600&q=80' : 
    condition === 'cvd' ? 'https://images.unsplash.com/photo-1476480862126-209bfaa8edc8?auto=format&fit=crop&w=600&q=80' : 
    condition === 'cholesterol' ? 'https://images.unsplash.com/photo-1498837167922-ddd27525d352?auto=format&fit=crop&w=600&q=80' : 
    condition === 'ckd' ? 'https://images.unsplash.com/photo-1505576399279-565b52d4ac71?auto=format&fit=crop&w=600&q=80' : 
    undefined
  }
 />
 );
 })}
 </div>
 </div>
 )}

 {step === 3 && (
 <div className="w-full">
 <p className="text-base text-gray-500 text-center mb-10 font-normal">{t.input.preferences.subtitle}</p>
 <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
 {[
 {
 id: 'western',
 image: 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=600&q=80',
 activeBorder: 'border-blue-500 ring-2 ring-blue-500/20',
 activeBg: 'bg-blue-50/30 ',
 accentColor: 'text-blue-600 ',
 badgeBg: 'bg-blue-100/80 text-blue-800 ',
 tag: 'Classic & Hearty',
 description: 'High-protein meals inspired by modern European and American culinary arts.'
 },
 {
 id: 'asian',
 image: 'https://images.unsplash.com/photo-1569718212165-3a8278d5f624?auto=format&fit=crop&w=600&q=80',
 activeBorder: 'border-red-500 ring-2 ring-red-500/20',
 activeBg: 'bg-red-50/30 ',
 accentColor: 'text-red-600 ',
 badgeBg: 'bg-red-100/80 text-red-800 ',
 tag: 'Savory & Spice',
 description: 'Healthy meals rich in fresh vegetables and flavors inspired by Eastern and South East Asian cooking.'
 },
 {
 id: 'mediterranean',
 image: 'https://images.unsplash.com/photo-1540189549336-e6e99c3679fe?auto=format&fit=crop&w=600&q=80',
 activeBorder: 'border-purple-500 ring-2 ring-purple-500/20',
 activeBg: 'bg-purple-50/30 ',
 accentColor: 'text-purple-600 ',
 badgeBg: 'bg-purple-100/80 text-purple-800 ',
 tag: 'Fresh & Olive-rich',
 description: 'Nutritious meals featuring plant foods, healthy fats like olive oil, fresh seafood, and whole grains.'
 }
].map((item) => {
 const isSelected = data.foodPreferences.includes(item.id);
 const title = t.input.preferences[item.id as keyof typeof t.input.preferences] as string;

 return (
 <button
 key={item.id}
 onClick={() => toggleFoodPreference(item.id)}
 className={`group relative flex flex-col w-full text-left overflow-hidden rounded-3xl border transition-all duration-300 hover:shadow-lg cursor-pointer ${
 isSelected
 ? `${item.activeBorder} ${item.activeBg} shadow-md scale-[1.01]`
 : 'border-border/80 bg-white/50 '
 }`}
 >
 {/* Image Header */}
 <div className="relative h-44 w-full overflow-hidden">
 <img
 src={item.image}
 alt={title}
 className={`h-full w-full object-cover transition-all duration-500 group-hover:scale-105 ${
 isSelected ? 'scale-100 filter-none opacity-100' : 'filter grayscale contrast-[1.1] opacity-75'
 }`}
 />
 {/* Dark Overlay */}
 <div className="absolute inset-0 bg-gradient-to-t from-slate-950/70 via-slate-950/20 to-transparent" />
 
 {/* Selection Badge */}
 <div className="absolute top-4 right-4">
 <span className={`flex h-7 w-7 items-center justify-center rounded-full text-sm font-bold shadow-md transition-all ${
 isSelected
 ? 'bg-white text-gray-900 scale-110 ring-2 ring-white/20'
 : 'bg-slate-900/60 text-white border border-white/20'
 }`}>
 {isSelected ? '✓' : ''}
 </span>
 </div>

 {/* Cuisine Tag */}
 <div className="absolute bottom-4 left-4">
 <span className="px-2.5 py-1 rounded-lg text-[10px] font-bold tracking-wide uppercase backdrop-blur-md bg-white/10 text-white border border-white/10">
 {item.tag}
 </span>
 </div>
 </div>

 {/* Details */}
 <div className="p-5 flex-1 flex flex-col justify-between">
 <div>
 <h4 className={`text-base font-bold tracking-tight transition-colors ${
 isSelected ? item.accentColor : 'text-gray-900 '
 }`}>
 {title}
 </h4>
 <p className="text-xs text-gray-500 mt-1.5 leading-relaxed font-normal">
 {item.description}
 </p>
 </div>
 </div>
 </button>
 );
 })}
 </div>
 </div>
 )}
 </div>

 {/* Bottom Navigation Buttons */}
 <div className="flex flex-row gap-2.5 sm:gap-3 justify-between mt-8 pt-6 border-t border-border/70">
 <button
 onClick={back}
 disabled={step === 0}
 className={`group/back flex-1 sm:flex-none px-5 py-3 justify-center rounded-2xl font-bold transition-all duration-300 flex items-center justify-center gap-2 text-xs sm:text-sm ${
   step === 0
     ? 'bg-gray-50 text-gray-300 border border-gray-200/40 cursor-not-allowed shadow-none'
     : 'bg-white hover:bg-gray-50 text-gray-700 border border-gray-200 shadow-sm hover:shadow active:scale-98 cursor-pointer'
 }`}
 >
 <ChevronLeft className="w-4 h-4 sm:w-5 sm:h-5 transition-transform duration-300 group-hover/back:-translate-x-1" />
 {t.input.back}
 </button>

 <button
  onClick={next}
  disabled={!canProceed()}
  className={`group/next flex-1 sm:flex-none px-6 py-3 justify-center rounded-2xl font-bold transition-all duration-300 flex items-center justify-center gap-2 text-xs sm:text-sm ${
    canProceed()
      ? 'bg-primary text-white border border-primary/20 shadow-md hover:shadow-lg hover:shadow-primary/20 hover:-translate-y-0.5 active:translate-y-0 active:scale-98 cursor-pointer'
      : 'bg-gray-150 text-gray-400 border border-gray-200/50 cursor-not-allowed shadow-none'
  }`}
  >
  {step === 3 ? t.input.generate : t.input.next}
  {step < 3 && <ChevronRight className="w-4 h-4 sm:w-5 sm:h-5 transition-transform duration-300 group-hover/next:translate-x-1" />}
  </button>
  </div>
  </motion.div>
  </div>
  </div>
  </div>
  </div>
  );
}

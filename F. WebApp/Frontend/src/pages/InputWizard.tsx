import { useState, useEffect } from 'react';
import { motion } from 'motion/react';
import { User, Activity, Heart, UtensilsCrossed, ChevronRight, ChevronLeft, Calendar, Scale, Ruler, Footprints, Flame, Leaf, Droplet, TrendingDown, Shield } from 'lucide-react';
import { useI18n } from '../contexts/I18nContext';
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
  const [activeTimeout, setActiveTimeout] = useState<any>(null);
  const { t } = useI18n();

  // Persist step to sessionStorage so refresh keeps the current wizard step in this tab only
  useEffect(() => {
    sessionStorage.setItem('dss_wizard_step', step.toString());
  }, [step]);

  // Clean up timeouts on unmount
  useEffect(() => {
    return () => {
      if (activeTimeout) clearTimeout(activeTimeout);
    };
  }, [activeTimeout]);

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
    if (activeTimeout) clearTimeout(activeTimeout);
    if (step < 3) setStep(step + 1);
    else onComplete();
  };

  const back = () => {
    if (activeTimeout) clearTimeout(activeTimeout);
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
      if (activeTimeout) clearTimeout(activeTimeout);
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
    <div className="min-h-[calc(100vh-4rem)] bg-gradient-to-br from-background via-background to-secondary/30 px-4 sm:px-6 lg:px-8 pb-8 pt-0 lg:pt-8 flex items-start justify-center">
      <div className="w-full max-w-[1600px]">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Left Side: Interactive Vertical Stepper (sticky sub-navbar on mobile) */}
          <div className="sticky top-16 lg:top-24 z-30 lg:col-span-3 flex flex-row lg:flex-col overflow-x-auto lg:overflow-x-visible scrollbar-none gap-3 lg:gap-0 -mx-4 px-4 sm:-mx-6 sm:px-6 lg:mx-0 lg:px-5 py-3 lg:py-5 bg-white/95 dark:bg-slate-900/95 lg:bg-white/50 lg:dark:bg-slate-900/40 backdrop-blur-md border-b border-border/50 lg:border lg:border-border/80 lg:dark:border-slate-800/80 rounded-none lg:rounded-3xl shadow-sm lg:shadow-lg lg:shadow-primary/5 dark:shadow-none">
            {steps.map((stepLabel, index) => {
              const active = index === step;
              const accessible = isStepAccessible(index);
              const summary = getStepSummary(index);
              const isCompleted = (() => {
                if (index === step) return false;
                if (index === 0) return !!data.gender;
                if (index === 1) return !!(data.age >= 18 && data.weight >= 30 && data.height >= 100);
                if (index === 2) return !!data.activity;
                if (index === 3) return data.healthConditions.length > 0;
                if (index === 4) return !!summary;
                return false;
              })();

              return (
                <button
                  key={index}
                  disabled={!accessible}
                  onClick={() => handleStepClick(index)}
                  className={`relative flex flex-row items-center lg:items-start text-left gap-2.5 lg:gap-3 p-2 lg:p-3 rounded-xl lg:rounded-2xl transition-all min-w-max lg:min-w-0 flex-1 lg:flex-none border border-transparent ${
                    active
                      ? 'bg-primary/10 dark:bg-primary/20 text-primary dark:text-emerald-300 border-primary/25 font-bold shadow-sm'
                      : accessible
                      ? 'hover:bg-white/80 dark:hover:bg-slate-800/60 text-gray-700 dark:text-gray-300 cursor-pointer'
                      : 'opacity-40 text-gray-400 dark:text-gray-650 cursor-not-allowed'
                  }`}
                >
                  {/* Vertical Connection Line on Desktop */}
                  {index < steps.length - 1 && (
                    <div className="hidden lg:block absolute left-8 top-12 bottom-0 w-0.5 bg-border dark:bg-slate-800 -mb-6 z-0" />
                  )}

                  {/* Icon Indicator */}
                  <div
                    className={`w-8 h-8 lg:w-10 lg:h-10 rounded-full flex items-center justify-center text-xs lg:text-sm font-bold shadow-sm z-10 shrink-0 transition-all ${
                      isCompleted
                        ? 'bg-primary text-primary-foreground'
                        : active
                        ? 'bg-primary text-primary-foreground ring-4 ring-primary/25 scale-105'
                        : 'bg-secondary dark:bg-slate-800 text-muted-foreground dark:text-gray-400'
                    }`}
                  >
                    {isCompleted ? <span className="text-xs font-extrabold">✓</span> : index + 1}
                  </div>

                  <div className="flex-1 min-w-0 text-left z-10">
                    <p className={`text-xs lg:text-sm tracking-tight ${active ? 'font-bold text-primary dark:text-emerald-300' : 'font-semibold'}`}>
                      {stepLabel}
                    </p>
                    {summary && (
                      <p className="text-[10px] lg:text-xs text-gray-500 dark:text-gray-400 font-normal truncate max-w-[100px] lg:max-w-[200px] mt-0.5">
                        {summary}
                      </p>
                    )}
                  </div>
                </button>
              );
            })}
          </div>

          {/* Right Side: Active Step Card Container */}
          <div className="lg:col-span-9 flex flex-col gap-6">
            <motion.div
              key={step}
              initial={{ opacity: 0, x: 15 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -15 }}
              className="bg-white/70 dark:bg-slate-800/40 backdrop-blur-md rounded-3xl p-6 sm:p-10 lg:p-12 border border-border/80 dark:border-border/20 shadow-xl shadow-primary/5 dark:shadow-none min-h-[360px] flex flex-col justify-between"
            >
              {/* Form Contents */}
              <div className="flex-1">
                {step === 0 && (
                  <div className="w-full space-y-10">
                    {/* Gender Selection Section */}
                    <div className="space-y-4">
                      <h3 className="text-lg font-bold text-gray-900 dark:text-white flex items-center gap-2">
                        <User className="w-5 h-5 text-primary" />
                        {t.input.gender.title}
                      </h3>
                      <div className="grid grid-cols-2 gap-6 w-full">
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
                        />
                      </div>
                    </div>

                    {/* Divider */}
                    <div className="border-t border-border/70 dark:border-slate-800/80" />

                    {/* Activity Selection Section */}
                    <div className="space-y-4">
                      <h3 className="text-lg font-bold text-gray-900 dark:text-white flex items-center gap-2">
                        <Activity className="w-5 h-5 text-primary" />
                        {t.input.activity.title}
                      </h3>
                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
                        <IconCard
                          icon={Footprints}
                          title={t.input.activity.light}
                          description={t.input.activity.lightDesc}
                          selected={data.activity === 'light'}
                          onClick={() => selectActivity('light')}
                        />
                        <IconCard
                          icon={Activity}
                          title={t.input.activity.moderate}
                          description={t.input.activity.moderateDesc}
                          selected={data.activity === 'moderate'}
                          onClick={() => selectActivity('moderate')}
                        />
                        <IconCard
                          icon={Flame}
                          title={t.input.activity.heavy}
                          description={t.input.activity.heavyDesc}
                          selected={data.activity === 'heavy'}
                          onClick={() => selectActivity('heavy')}
                        />
                      </div>
                    </div>
                  </div>
                )}

                {step === 1 && (
                  <div className="w-full">
                    <div className="w-full space-y-12">
                      {/* Age Slider */}
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <label className="text-sm font-medium flex items-center gap-2 text-gray-900 dark:text-white">
                            <div className="w-10 h-10 rounded-full bg-secondary dark:bg-slate-800 flex items-center justify-center">
                              <Calendar className="w-5 h-5 text-primary dark:text-emerald-400" />
                            </div>
                            {t.input.metrics.age}
                          </label>
                          <div className="flex items-center gap-3">
                            <button
                              onClick={() => onUpdate({ age: Math.max(18, data.age - 1) })}
                              className="w-9 h-9 rounded-xl bg-secondary hover:bg-muted dark:bg-slate-800 dark:hover:bg-slate-700 text-primary dark:text-emerald-400 transition-all flex items-center justify-center font-extrabold shadow-sm hover:shadow cursor-pointer"
                            >
                              -
                            </button>
                            <span className="text-3xl font-bold text-primary dark:text-emerald-450 min-w-[80px] text-center font-serif">
                              {editing === 'age' ? (
                                <input
                                  autoFocus
                                  className="w-[80px] text-center bg-transparent outline-none border-b border-primary"
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
                                  className="w-full cursor-pointer hover:opacity-80"
                                >
                                  {data.age}
                                </button>
                              )}
                            </span>
                            <button
                              onClick={() => onUpdate({ age: Math.min(100, data.age + 1) })}
                              className="w-9 h-9 rounded-xl bg-secondary hover:bg-muted dark:bg-slate-800 dark:hover:bg-slate-700 text-primary dark:text-emerald-400 transition-all flex items-center justify-center font-extrabold shadow-sm hover:shadow cursor-pointer"
                            >
                              +
                            </button>
                          </div>
                        </div>
                        <input
                          type="range"
                          min="18"
                          max="100"
                          value={data.age}
                          onChange={(e) => onUpdate({ age: parseInt(e.target.value) })}
                          className="w-full cursor-pointer"
                          style={{
                            background: `linear-gradient(to right, #2d5a27 0%, #558550 ${((data.age - 18) / (100 - 18)) * 100}%, #d2dfd5 ${((data.age - 18) / (100 - 18)) * 100}%, #d2dfd5 100%)`,
                            borderRadius: '9999px'
                          }}
                        />
                      </div>

                      {/* Weight Slider */}
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <label className="text-sm font-medium flex items-center gap-2 text-gray-900 dark:text-white">
                            <div className="w-10 h-10 rounded-full bg-secondary dark:bg-slate-800 flex items-center justify-center">
                              <Scale className="w-5 h-5 text-primary dark:text-emerald-400" />
                            </div>
                            {t.input.metrics.weight}
                          </label>
                          <div className="flex items-center gap-3">
                            <button
                              onClick={() => onUpdate({ weight: Math.max(30, data.weight - 1) })}
                              className="w-9 h-9 rounded-xl bg-secondary hover:bg-muted dark:bg-slate-800 dark:hover:bg-slate-700 text-primary dark:text-emerald-400 transition-all flex items-center justify-center font-extrabold shadow-sm hover:shadow cursor-pointer"
                            >
                              -
                            </button>
                            <span className="text-3xl font-bold text-primary dark:text-emerald-455 min-w-[80px] text-center font-serif">
                              {editing === 'weight' ? (
                                <input
                                  autoFocus
                                  className="w-[80px] text-center bg-transparent outline-none border-b border-primary"
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
                                  className="w-full cursor-pointer hover:opacity-80"
                                >
                                  {data.weight}
                                </button>
                              )}
                            </span>
                            <button
                              onClick={() => onUpdate({ weight: Math.min(200, data.weight + 1) })}
                              className="w-9 h-9 rounded-xl bg-secondary hover:bg-muted dark:bg-slate-800 dark:hover:bg-slate-700 text-primary dark:text-emerald-400 transition-all flex items-center justify-center font-extrabold shadow-sm hover:shadow cursor-pointer"
                            >
                              +
                            </button>
                          </div>
                        </div>
                        <input
                          type="range"
                          min="30"
                          max="200"
                          value={data.weight}
                          onChange={(e) => onUpdate({ weight: parseFloat(e.target.value) })}
                          className="w-full cursor-pointer"
                          style={{
                            background: `linear-gradient(to right, #2d5a27 0%, #558550 ${((data.weight - 30) / (200 - 30)) * 100}%, #d2dfd5 ${((data.weight - 30) / (200 - 30)) * 100}%, #d2dfd5 100%)`,
                            borderRadius: '9999px'
                          }}
                        />
                      </div>

                      {/* Height Slider */}
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <label className="text-sm font-medium flex items-center gap-2 text-gray-900 dark:text-white">
                            <div className="w-10 h-10 rounded-full bg-secondary dark:bg-slate-800 flex items-center justify-center">
                              <Ruler className="w-5 h-5 text-primary dark:text-emerald-400" />
                            </div>
                            {t.input.metrics.height}
                          </label>
                          <div className="flex items-center gap-3">
                            <button
                              onClick={() => onUpdate({ height: Math.max(100, data.height - 1) })}
                              className="w-9 h-9 rounded-xl bg-secondary hover:bg-muted dark:bg-slate-800 dark:hover:bg-slate-700 text-primary dark:text-emerald-400 transition-all flex items-center justify-center font-extrabold shadow-sm hover:shadow cursor-pointer"
                            >
                              -
                            </button>
                            <span className="text-3xl font-bold text-primary dark:text-emerald-455 min-w-[80px] text-center font-serif">
                              {editing === 'height' ? (
                                <input
                                  autoFocus
                                  className="w-[80px] text-center bg-transparent outline-none border-b border-primary"
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
                                  className="w-full cursor-pointer hover:opacity-80"
                                >
                                  {data.height}
                                </button>
                              )}
                            </span>
                            <button
                              onClick={() => onUpdate({ height: Math.min(300, data.height + 1) })}
                              className="w-9 h-9 rounded-xl bg-secondary hover:bg-muted dark:bg-slate-800 dark:hover:bg-slate-700 text-primary dark:text-emerald-400 transition-all flex items-center justify-center font-extrabold shadow-sm hover:shadow cursor-pointer"
                            >
                              +
                            </button>
                          </div>
                        </div>
                        <input
                          type="range"
                          min="100"
                          max="300"
                          value={data.height}
                          onChange={(e) => onUpdate({ height: parseFloat(e.target.value) })}
                          className="w-full"
                          style={{
                            background: `linear-gradient(to right, #2d5a27 0%, #558550 ${((data.height - 100) / (300 - 100)) * 100}%, #d2dfd5 ${((data.height - 100) / (300 - 100)) * 100}%, #d2dfd5 100%)`,
                            borderRadius: '9999px'
                          }}
                        />
                      </div>

                      {/* BMI Visual Indicator */}
                      {data.weight > 0 && data.height > 0 && (
                        <motion.div
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          className="mt-6 p-6 rounded-2xl text-center border"
                          style={{
                            borderColor: (() => {
                              const bmi = data.weight / ((data.height / 100) ** 2);
                              if (bmi >= 30) return '#cb2d2d';
                              if (bmi >= 25) return '#c98a0c';
                              if (bmi >= 18.5) return '#2d5a27';
                              return '#c98a0c';
                            })(),
                            background: 'linear-gradient(to right, rgba(45,90,39,0.04), rgba(45,90,39,0.01))'
                          }}
                        >
                          <p className="text-xs mb-1 font-semibold tracking-wider uppercase" style={{
                            color: (() => {
                              const bmi = data.weight / ((data.height / 100) ** 2);
                              if (bmi >= 30) return '#a62424';
                              if (bmi >= 25) return '#8c5f0a';
                              if (bmi >= 18.5) return '#2d5a27';
                              return '#8c5f0a';
                            })()
                          }}>
                            Body Mass Index
                          </p>
                          <p className="text-4xl font-bold font-serif" style={{
                            color: (() => {
                              const bmi = data.weight / ((data.height / 100) ** 2);
                              if (bmi >= 30) return '#a62424';
                              if (bmi >= 25) return '#8c5f0a';
                              if (bmi >= 18.5) return '#2d5a27';
                              return '#8c5f0a';
                            })()
                          }}>
                            {(data.weight / ((data.height / 100) ** 2)).toFixed(1)}
                          </p>
                          <p className="mt-2 text-sm font-semibold" style={{
                            color: (() => {
                              const bmi = data.weight / ((data.height / 100) ** 2);
                              if (bmi >= 30) return '#a62424';
                              if (bmi >= 25) return '#8c5f0a';
                              if (bmi >= 18.5) return '#2d5a27';
                              return '#8c5f0a';
                            })()
                          }}>
                            {(() => {
                              const bmi = data.weight / ((data.height / 100) ** 2);
                              if (bmi < 18.5) return 'Underweight (<18.5)';
                              if (bmi < 25) return 'Normal weight (18.5–24.9)';
                              if (bmi < 30) return 'Overweight (25–29.9)';
                              if (bmi < 35) return 'Obesity Class I (30–34.9)';
                              if (bmi < 40) return 'Obesity Class II (35–39.9)';
                              return 'Obesity Class III (≥40)';
                            })()}
                          </p>
                        </motion.div>
                      )}
                    </div>
                  </div>
                )}

                {step === 2 && (
                  <div>
                    <p className="text-base text-gray-500 dark:text-gray-400 text-center mb-8 font-normal">{t.input.health.subtitle}</p>
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-5">
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
                        return (
                          <IconCard
                            key={condition}
                            icon={getHealthIcon(condition)}
                            title={t.input.health[condition as keyof typeof t.input.health] as string}
                            selected={data.healthConditions.includes(condition)}
                            disabled={
                              (condition === 'normal' && data.healthConditions.some(c => c !== 'normal')) ||
                              (condition !== 'normal' && data.healthConditions.includes('normal')) ||
                              (condition !== 'normal' && !data.healthConditions.includes(condition) &&
                                data.healthConditions.filter(c => c !== 'normal').length >= 3)
                            }
                            onClick={() => toggleHealthCondition(condition)}
                          />
                        );
                      })}
                    </div>
                  </div>
                )}

                {step === 3 && (
                  <div className="w-full">
                    <p className="text-base text-gray-500 dark:text-gray-400 text-center mb-10 font-normal">{t.input.preferences.subtitle}</p>
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
                      {[
                        {
                          id: 'western',
                          image: 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=600&q=80',
                          activeBorder: 'border-blue-500 dark:border-blue-400 ring-2 ring-blue-500/20',
                          activeBg: 'bg-blue-50/30 dark:bg-blue-950/10',
                          accentColor: 'text-blue-600 dark:text-blue-400',
                          badgeBg: 'bg-blue-100/80 dark:bg-blue-900/40 text-blue-800 dark:text-blue-300',
                          tag: 'Classic & Hearty',
                          description: 'High-protein meals inspired by modern European and American culinary arts.'
                        },
                        {
                          id: 'asian',
                          image: 'https://images.unsplash.com/photo-1569718212165-3a8278d5f624?auto=format&fit=crop&w=600&q=80',
                          activeBorder: 'border-red-500 dark:border-red-400 ring-2 ring-red-500/20',
                          activeBg: 'bg-red-50/30 dark:bg-red-950/10',
                          accentColor: 'text-red-600 dark:text-red-400',
                          badgeBg: 'bg-red-100/80 dark:bg-red-900/40 text-red-800 dark:text-red-300',
                          tag: 'Savory & Spice',
                          description: 'Healthy meals rich in fresh vegetables and flavors inspired by Eastern and South East Asian cooking.'
                        },
                        {
                          id: 'mediterranean',
                          image: 'https://images.unsplash.com/photo-1540189549336-e6e99c3679fe?auto=format&fit=crop&w=600&q=80',
                          activeBorder: 'border-purple-500 dark:border-purple-400 ring-2 ring-purple-500/20',
                          activeBg: 'bg-purple-50/30 dark:bg-purple-950/10',
                          accentColor: 'text-purple-600 dark:text-purple-400',
                          badgeBg: 'bg-purple-100/80 dark:bg-purple-900/40 text-purple-800 dark:text-purple-300',
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
                                : 'border-border/80 dark:border-slate-800/80 bg-white/50 dark:bg-slate-900/40'
                            }`}
                          >
                            {/* Image Header */}
                            <div className="relative h-44 w-full overflow-hidden">
                              <img
                                src={item.image}
                                alt={title}
                                className={`h-full w-full object-cover transition-all duration-500 group-hover:scale-105 ${
                                  isSelected ? 'scale-100 filter-none opacity-100' : 'filter grayscale contrast-[1.1] opacity-75 group-hover:filter-none group-hover:opacity-100'
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
                                  isSelected ? item.accentColor : 'text-gray-900 dark:text-white'
                                }`}>
                                  {title}
                                </h4>
                                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1.5 leading-relaxed font-normal">
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
              <div className="flex justify-between mt-8 pt-6 border-t border-border/70 dark:border-slate-800/80">
                <button
                  onClick={back}
                  disabled={step === 0}
                  className="px-5 py-2.5 rounded-2xl font-semibold transition-all disabled:opacity-30 disabled:cursor-not-allowed hover:bg-secondary dark:hover:bg-slate-800 border border-border dark:border-slate-700 text-gray-700 dark:text-gray-300 flex items-center gap-2 cursor-pointer text-sm"
                >
                  <ChevronLeft className="w-5 h-5" />
                  {t.input.back}
                </button>

                <button
                  onClick={next}
                  disabled={!canProceed()}
                  className="px-6 py-2.5 bg-primary text-primary-foreground rounded-2xl font-semibold hover:bg-primary/95 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:bg-slate-200 dark:disabled:bg-slate-800 disabled:text-gray-400 flex items-center gap-2 shadow-sm hover:shadow-md hover:shadow-primary/10 cursor-pointer text-sm"
                >
                  {step === 3 ? t.input.generate : t.input.next}
                  {step < 3 && <ChevronRight className="w-5 h-5" />}
                </button>
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
}

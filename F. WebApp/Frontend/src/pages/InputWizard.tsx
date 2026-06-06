import { useState, useEffect } from 'react';
import { motion } from 'motion/react';
import { User, Activity, Heart, UtensilsCrossed, ChevronRight, ChevronLeft } from 'lucide-react';
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
    return saved ? parseInt(saved, 10) : 0;
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
      case 0: return !!data.gender;
      case 1: return !!(data.age >= 18 && data.weight >= 30 && data.height >= 100);
      case 2: return !!data.activity;
      case 3: return data.healthConditions.length > 0;
      case 4: return true;
      default: return false;
    }
  };

  const next = () => {
    if (activeTimeout) clearTimeout(activeTimeout);
    if (step < 4) setStep(step + 1);
    else onComplete();
  };

  const back = () => {
    if (activeTimeout) clearTimeout(activeTimeout);
    if (step > 0) setStep(step - 1);
  };

  const selectGender = (gender: 'male' | 'female') => {
    if (activeTimeout) clearTimeout(activeTimeout);
    onUpdate({ gender });
    const to = setTimeout(() => {
      setStep(1);
    }, 450);
    setActiveTimeout(to);
  };

  const selectActivity = (activity: 'light' | 'moderate' | 'heavy') => {
    if (activeTimeout) clearTimeout(activeTimeout);
    onUpdate({ activity });
    const to = setTimeout(() => {
      setStep(3);
    }, 450);
    setActiveTimeout(to);
  };

  const isStepAccessible = (targetStep: number) => {
    if (targetStep === 0) return true;
    for (let i = 0; i < targetStep; i++) {
      if (i === 0 && !data.gender) return false;
      if (i === 1 && !(data.age >= 18 && data.weight >= 30 && data.height >= 100)) return false;
      if (i === 2 && !data.activity) return false;
      if (i === 3 && data.healthConditions.length === 0) return false;
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
        return data.gender ? (data.gender === 'male' ? 'Male' : 'Female') : '';
      case 1:
        const hasMetrics = data.age >= 18 && data.weight >= 30 && data.height >= 100;
        return hasMetrics ? `${data.age} yrs • ${data.weight} kg • ${data.height} cm` : '';
      case 2:
        return data.activity ? (data.activity === 'light' ? 'Light' : data.activity === 'moderate' ? 'Moderate' : 'Heavy') : '';
      case 3:
        if (data.healthConditions.length === 0) return '';
        return data.healthConditions.map(c => t.input.health[c as keyof typeof t.input.health] || c).join(', ');
      case 4:
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
    <div className="min-h-[calc(100vh-4rem)] bg-gradient-to-br from-background via-background to-secondary/30 px-4 py-8 flex items-center justify-center">
      <div className="w-full max-w-5xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8 text-center"
        >
          <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white tracking-tight">{t.input.title}</h1>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Left Side: Interactive Vertical Stepper */}
          <div className="lg:col-span-4 bg-white/50 dark:bg-slate-900/40 backdrop-blur-md rounded-3xl p-5 border border-border/80 dark:border-slate-800/80 shadow-lg shadow-primary/5 dark:shadow-none flex flex-row lg:flex-col overflow-x-auto lg:overflow-x-visible gap-4 lg:gap-0">
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
                  className={`relative flex flex-col lg:flex-row items-center lg:items-start text-left gap-3 p-3 rounded-2xl transition-all min-w-[120px] lg:min-w-0 flex-1 lg:flex-none border border-transparent ${
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
                    className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold shadow-sm z-10 shrink-0 transition-all ${
                      isCompleted
                        ? 'bg-primary text-primary-foreground'
                        : active
                        ? 'bg-primary text-primary-foreground ring-4 ring-primary/25 scale-105'
                        : 'bg-secondary dark:bg-slate-800 text-muted-foreground dark:text-gray-400'
                    }`}
                  >
                    {isCompleted ? <span className="text-xs font-extrabold">✓</span> : index + 1}
                  </div>

                  <div className="flex-1 min-w-0 text-center lg:text-left z-10">
                    <p className={`text-sm tracking-tight ${active ? 'font-bold text-primary dark:text-emerald-300' : 'font-semibold'}`}>
                      {stepLabel}
                    </p>
                    {summary && (
                      <p className="text-xs text-gray-500 dark:text-gray-400 font-normal truncate max-w-[150px] lg:max-w-[200px] mt-0.5">
                        {summary}
                      </p>
                    )}
                  </div>
                </button>
              );
            })}
          </div>

          {/* Right Side: Active Step Card Container */}
          <div className="lg:col-span-8 flex flex-col gap-6">
            <motion.div
              key={step}
              initial={{ opacity: 0, x: 15 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -15 }}
              className="bg-white/70 dark:bg-slate-800/40 backdrop-blur-md rounded-3xl p-6 sm:p-8 border border-border/80 dark:border-border/20 shadow-xl shadow-primary/5 dark:shadow-none min-h-[360px] flex flex-col justify-between"
            >
              {/* Form Contents */}
              <div className="flex-1">
                {step === 0 && (
                  <div>
                    <h2 className="text-2xl font-bold mb-6 text-center text-gray-900 dark:text-white">{t.input.gender.title}</h2>
                    <div className="grid grid-cols-2 gap-4 max-w-lg mx-auto">
                      <IconCard
                        icon={User}
                        title={t.input.gender.male}
                        selected={data.gender === 'male'}
                        onClick={() => selectGender('male')}
                      />
                      <IconCard
                        icon={User}
                        title={t.input.gender.female}
                        selected={data.gender === 'female'}
                        onClick={() => selectGender('female')}
                      />
                    </div>
                  </div>
                )}

                {step === 1 && (
                  <div>
                    <h2 className="text-2xl font-bold mb-8 text-center text-gray-900 dark:text-white tracking-tight">{t.input.metrics.title}</h2>
                    <div className="max-w-2xl mx-auto space-y-8">
                      {/* Age Slider */}
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <label className="text-sm font-medium flex items-center gap-2 text-gray-900 dark:text-white">
                            <div className="w-10 h-10 rounded-full bg-secondary dark:bg-slate-800 flex items-center justify-center">
                              <span className="text-xl">🎂</span>
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
                              <span className="text-xl">⚖️</span>
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
                            <span className="text-3xl font-bold text-primary dark:text-emerald-450 min-w-[80px] text-center font-serif">
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
                              <span className="text-xl">📏</span>
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
                            <span className="text-3xl font-bold text-primary dark:text-emerald-450 min-w-[80px] text-center font-serif">
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
                    <h2 className="text-2xl font-bold mb-6 text-center text-gray-900 dark:text-white tracking-tight">{t.input.activity.title}</h2>
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                      <IconCard
                        icon={Activity}
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
                        icon={Activity}
                        title={t.input.activity.heavy}
                        description={t.input.activity.heavyDesc}
                        selected={data.activity === 'heavy'}
                        onClick={() => selectActivity('heavy')}
                      />
                    </div>
                  </div>
                )}

                {step === 3 && (
                  <div>
                    <h2 className="text-2xl font-bold mb-2 text-center text-gray-900 dark:text-white tracking-tight">{t.input.health.title}</h2>
                    <p className="text-sm text-gray-500 dark:text-gray-400 text-center mb-6 font-normal">{t.input.health.subtitle}</p>
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                      {['normal', 'dm2', 'hypertension', 'cvd', 'cholesterol', 'ckd'].map((condition) => (
                        <IconCard
                          key={condition}
                          icon={Heart}
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
                      ))}
                    </div>
                  </div>
                )}

                {step === 4 && (
                  <div>
                    <h2 className="text-2xl font-bold mb-2 text-center text-gray-900 dark:text-white tracking-tight">{t.input.preferences.title}</h2>
                    <p className="text-sm text-gray-500 dark:text-gray-400 text-center mb-6 font-normal">{t.input.preferences.subtitle}</p>
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 max-w-2xl mx-auto">
                      {['western', 'asian', 'mediterranean'].map((pref) => (
                        <IconCard
                          key={pref}
                          icon={UtensilsCrossed}
                          title={t.input.preferences[pref as keyof typeof t.input.preferences] as string}
                          selected={data.foodPreferences.includes(pref)}
                          onClick={() => toggleFoodPreference(pref)}
                        />
                      ))}
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
                  {step === 4 ? t.input.generate : t.input.next}
                  {step < 4 && <ChevronRight className="w-5 h-5" />}
                </button>
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
}

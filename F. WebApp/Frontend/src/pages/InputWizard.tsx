import { useState, useEffect } from 'react';
import { motion } from 'motion/react';
import { User, Activity, Heart, UtensilsCrossed, ChevronRight, ChevronLeft } from 'lucide-react';
import { useI18n } from '../contexts/I18nContext';
import { ProgressIndicator } from '../components/figma/ProgressIndicator';
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
    const saved = localStorage.getItem('dss_wizard_step');
    return saved ? parseInt(saved, 10) : 0;
  });

  const [editing, setEditing] = useState<null | 'age' | 'weight' | 'height'>(null);
  const [tempValue, setTempValue] = useState<string>('');
  const { t } = useI18n();

  // Persist step to localStorage
  useEffect(() => {
    localStorage.setItem('dss_wizard_step', step.toString());
  }, [step]);

  const steps = t.input.steps;

  const canProceed = () => {
    switch (step) {
      case 0: return !!data.gender;
      case 1: return !!(data.age > 0 && data.weight > 0 && data.height > 0);
      case 2: return !!data.activity;
      case 3: return data.healthConditions.length > 0;
      case 4: return true;
      default: return false;
    }
  };

  const next = () => {
    if (step < 4) setStep(step + 1);
    else onComplete();
  };

  const back = () => {
    if (step > 0) setStep(step - 1);
  };

  const toggleHealthCondition = (condition: string) => {
    const isNormal = condition === 'normal';
    const isSelected = data.healthConditions.includes(condition);

    if (isNormal) {
      // Toggle normal on/off
      if (isSelected) {
        onUpdate({ healthConditions: [] });
      } else {
        onUpdate({ healthConditions: ['normal'] });
      }
    } else {
      let conditions = data.healthConditions.filter(c => c !== 'normal');
      if (conditions.includes(condition)) {
        // Deselect if already selected
        conditions = conditions.filter(c => c !== condition);
      } else if (conditions.length < 3) {
        // Add if under limit
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
    <div className="min-h-[calc(100vh-4rem)] bg-gradient-to-br from-emerald-50 via-green-50 to-teal-50 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900 px-4 py-8 flex items-center justify-center">
      <div className="w-full max-w-4xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-3xl sm:text-4xl font-bold text-center mb-8 text-gray-900 dark:text-white">{t.input.title}</h1>
          <ProgressIndicator steps={steps} currentStep={step} />
        </motion.div>

        <motion.div
          key={step}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          className="bg-white dark:bg-slate-800 rounded-2xl p-6 sm:p-8 border-2 border-emerald-200 dark:border-emerald-700"
        >
          {step === 0 && (
            <div>
              <h2 className="text-2xl font-bold mb-6 text-center text-gray-900 dark:text-white">{t.input.gender.title}</h2>
              <div className="grid grid-cols-2 gap-4 max-w-lg mx-auto">
                <IconCard
                  icon={User}
                  title={t.input.gender.male}
                  selected={data.gender === 'male'}
                  onClick={() => onUpdate({ gender: data.gender === 'male' ? undefined : 'male' })}
                />
                <IconCard
                  icon={User}
                  title={t.input.gender.female}
                  selected={data.gender === 'female'}
                  onClick={() => onUpdate({ gender: data.gender === 'female' ? undefined : 'female' })}
                />
              </div>
            </div>
          )}

          {step === 1 && (
            <div>
              <h2 className="text-2xl font-bold mb-8 text-center text-gray-900 dark:text-white">{t.input.metrics.title}</h2>
              <div className="max-w-2xl mx-auto space-y-8">
                {/* Age Slider */}
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <label className="text-sm font-medium flex items-center gap-2 text-gray-900 dark:text-white">
                      <div className="w-10 h-10 rounded-full bg-emerald-100 dark:bg-emerald-900 flex items-center justify-center">
                        <span className="text-xl">🎂</span>
                      </div>
                      {t.input.metrics.age}
                    </label>
                      <div className="flex items-center gap-3">
                      <button
                        onClick={() => onUpdate({ age: Math.max(18, data.age - 1) })}
                        className="w-9 h-9 rounded-lg bg-gradient-to-br from-emerald-500 to-teal-500 text-white hover:from-emerald-600 hover:to-teal-600 transition-all flex items-center justify-center font-bold shadow-md hover:shadow-lg"
                      >
                        -
                      </button>
                      <span className="text-3xl font-bold text-emerald-600 dark:text-emerald-400 min-w-[80px] text-center">
                        {editing === 'age' ? (
                          <input
                            autoFocus
                            className="w-[80px] text-center bg-transparent outline-none"
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
                            className="w-full"
                          >
                            {data.age}
                          </button>
                        )}
                      </span>
                      <button
                        onClick={() => onUpdate({ age: Math.min(100, data.age + 1) })}
                        className="w-9 h-9 rounded-lg bg-gradient-to-br from-emerald-500 to-teal-500 text-white hover:from-emerald-600 hover:to-teal-600 transition-all flex items-center justify-center font-bold shadow-md hover:shadow-lg"
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
                    className="w-full"
                    style={{
                      background: `linear-gradient(to right, #10b981 0%, #14b8a6 ${((data.age - 18) / (100 - 18)) * 100}%, #d1d5db ${((data.age - 18) / (100 - 18)) * 100}%, #d1d5db 100%)`,
                      borderRadius: '9999px'
                    }}
                  />
                </div>

                {/* Weight Slider */}
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <label className="text-sm font-medium flex items-center gap-2 text-gray-900 dark:text-white">
                      <div className="w-10 h-10 rounded-full bg-emerald-100 dark:bg-emerald-900 flex items-center justify-center">
                        <span className="text-xl">⚖️</span>
                      </div>
                      {t.input.metrics.weight}
                    </label>
                      <div className="flex items-center gap-3">
                      <button
                        onClick={() => onUpdate({ weight: Math.max(30, data.weight - 1) })}
                        className="w-9 h-9 rounded-lg bg-gradient-to-br from-emerald-500 to-teal-500 text-white hover:from-emerald-600 hover:to-teal-600 transition-all flex items-center justify-center font-bold shadow-md hover:shadow-lg"
                      >
                        -
                      </button>
                      <span className="text-3xl font-bold text-emerald-600 dark:text-emerald-400 min-w-[80px] text-center">
                        {editing === 'weight' ? (
                          <input
                            autoFocus
                            className="w-[80px] text-center bg-transparent outline-none"
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
                            className="w-full"
                          >
                            {data.weight}
                          </button>
                        )}
                      </span>
                      <button
                        onClick={() => onUpdate({ weight: Math.min(200, data.weight + 1) })}
                        className="w-9 h-9 rounded-lg bg-gradient-to-br from-emerald-500 to-teal-500 text-white hover:from-emerald-600 hover:to-teal-600 transition-all flex items-center justify-center font-bold shadow-md hover:shadow-lg"
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
                    className="w-full"
                    style={{
                      background: `linear-gradient(to right, #10b981 0%, #14b8a6 ${((data.weight - 30) / (200 - 30)) * 100}%, #d1d5db ${((data.weight - 30) / (200 - 30)) * 100}%, #d1d5db 100%)`,
                      borderRadius: '9999px'
                    }}
                  />
                </div>

                {/* Height Slider */}
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <label className="text-sm font-medium flex items-center gap-2 text-gray-900 dark:text-white">
                      <div className="w-10 h-10 rounded-full bg-emerald-100 dark:bg-emerald-900 flex items-center justify-center">
                        <span className="text-xl">📏</span>
                      </div>
                      {t.input.metrics.height}
                    </label>
                      <div className="flex items-center gap-3">
                      <button
                        onClick={() => onUpdate({ height: Math.max(100, data.height - 1) })}
                        className="w-9 h-9 rounded-lg bg-gradient-to-br from-emerald-500 to-teal-500 text-white hover:from-emerald-600 hover:to-teal-600 transition-all flex items-center justify-center font-bold shadow-md hover:shadow-lg"
                      >
                        -
                      </button>
                      <span className="text-3xl font-bold text-emerald-600 dark:text-emerald-400 min-w-[80px] text-center">
                        {editing === 'height' ? (
                          <input
                            autoFocus
                            className="w-[80px] text-center bg-transparent outline-none"
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
                            className="w-full"
                          >
                            {data.height}
                          </button>
                        )}
                      </span>
                      <button
                        onClick={() => onUpdate({ height: Math.min(300, data.height + 1) })}
                        className="w-9 h-9 rounded-lg bg-gradient-to-br from-emerald-500 to-teal-500 text-white hover:from-emerald-600 hover:to-teal-600 transition-all flex items-center justify-center font-bold shadow-md hover:shadow-lg"
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
                      background: `linear-gradient(to right, #10b981 0%, #14b8a6 ${((data.height - 100) / (300 - 100)) * 100}%, #d1d5db ${((data.height - 100) / (300 - 100)) * 100}%, #d1d5db 100%)`,
                      borderRadius: '9999px'
                    }}
                  />
                </div>

                {/* BMI Visual Indicator */}
                {data.weight > 0 && data.height > 0 && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mt-6 p-6 rounded-xl text-center border-2"
                    style={{
                      borderColor: (() => {
                        const bmi = data.weight / ((data.height / 100) ** 2);
                        if (bmi >= 30) return '#ef4444'; // red
                        if (bmi >= 25) return '#f59e0b'; // yellow
                        if (bmi >= 18.5) return '#10b981'; // green
                        return '#f59e0b'; // yellow for underweight
                      })(),
                      background: 'linear-gradient(to right, rgba(16,185,129,0.05), rgba(16,185,129,0.02))'
                    }}
                  >
                    <p className="text-sm mb-2 font-medium" style={{ color: (() => {
                      const bmi = data.weight / ((data.height / 100) ** 2);
                      if (bmi >= 30) return '#b91c1c';
                      if (bmi >= 25) return '#92400e';
                      if (bmi >= 18.5) return '#047857';
                      return '#92400e';
                    })() }}>
                      Body Mass Index
                    </p>
                    <p className="text-4xl font-bold" style={{ color: (() => {
                      const bmi = data.weight / ((data.height / 100) ** 2);
                      if (bmi >= 30) return '#b91c1c';
                      if (bmi >= 25) return '#92400e';
                      if (bmi >= 18.5) return '#047857';
                      return '#92400e';
                    })() }}>
                      {(data.weight / ((data.height / 100) ** 2)).toFixed(1)}
                    </p>
                    <p className="mt-2 text-sm font-semibold" style={{ color: (() => {
                      const bmi = data.weight / ((data.height / 100) ** 2);
                      if (bmi >= 40) return '#b91c1c';
                      if (bmi >= 35) return '#b91c1c';
                      if (bmi >= 30) return '#b91c1c';
                      if (bmi >= 25) return '#92400e';
                      if (bmi >= 18.5) return '#047857';
                      return '#92400e';
                    })() }}>
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
              <h2 className="text-2xl font-bold mb-6 text-center text-gray-900 dark:text-white">{t.input.activity.title}</h2>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <IconCard
                  icon={Activity}
                  title={t.input.activity.light}
                  description={t.input.activity.lightDesc}
                  selected={data.activity === 'light'}
                  onClick={() => onUpdate({ activity: data.activity === 'light' ? undefined : 'light' })}
                />
                <IconCard
                  icon={Activity}
                  title={t.input.activity.moderate}
                  description={t.input.activity.moderateDesc}
                  selected={data.activity === 'moderate'}
                  onClick={() => onUpdate({ activity: data.activity === 'moderate' ? undefined : 'moderate' })}
                />
                <IconCard
                  icon={Activity}
                  title={t.input.activity.heavy}
                  description={t.input.activity.heavyDesc}
                  selected={data.activity === 'heavy'}
                  onClick={() => onUpdate({ activity: data.activity === 'heavy' ? undefined : 'heavy' })}
                />
              </div>
            </div>
          )}

          {step === 3 && (
            <div>
              <h2 className="text-2xl font-bold mb-2 text-center text-gray-900 dark:text-white">{t.input.health.title}</h2>
              <p className="text-sm text-gray-600 dark:text-gray-400 text-center mb-6">{t.input.health.subtitle}</p>
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
              <h2 className="text-2xl font-bold mb-2 text-center text-gray-900 dark:text-white">{t.input.preferences.title}</h2>
              <p className="text-sm text-gray-600 dark:text-gray-400 text-center mb-6">{t.input.preferences.subtitle}</p>
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
        </motion.div>

        <div className="flex justify-between mt-8 max-w-4xl mx-auto">
          <button
            onClick={back}
            disabled={step === 0}
            className="px-6 py-3 rounded-xl font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed hover:bg-emerald-100 dark:hover:bg-emerald-900 border-2 border-emerald-200 dark:border-emerald-700 text-gray-900 dark:text-white flex items-center gap-2"
          >
            <ChevronLeft className="w-5 h-5" />
            {t.input.back}
          </button>

          <button
            onClick={next}
            disabled={!canProceed()}
            className="px-6 py-3 bg-gradient-to-r from-emerald-500 to-teal-500 text-white rounded-xl font-medium hover:from-emerald-600 hover:to-teal-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:from-gray-300 disabled:to-gray-400 flex items-center gap-2 shadow-md hover:shadow-lg"
          >
            {step === 4 ? t.input.generate : t.input.next}
            {step < 4 && <ChevronRight className="w-5 h-5" />}
          </button>
        </div>
      </div>
    </div>
  );
}

import { useState } from 'react';
import { X, Heart, Activity, Flame, Zap } from 'lucide-react';

interface BmiCalculatorModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function BmiCalculatorModal({ isOpen, onClose }: BmiCalculatorModalProps) {
  // Input states
  const [gender, setGender] = useState<'male' | 'female'>('male');
  const [age, setAge] = useState<number>(30);
  const [weight, setWeight] = useState<number>(70);
  const [height, setHeight] = useState<number>(170);
  const [healthStatus, setHealthStatus] = useState<'sehat' | 'sakit'>('sehat');
  const [activity, setActivity] = useState<'light' | 'moderate' | 'heavy'>('moderate');

  if (!isOpen) return null;

  // 1. BMI Calculation
  const heightInMeters = height / 100;
  const bmi = heightInMeters > 0 ? weight / (heightInMeters * heightInMeters) : 0;

  // BMI Category & Styling
  let bmiCategory = 'Healthy Weight';
  let bmiColor = 'text-green-600 bg-green-50 border-green-200';
  let bmiBarColor = 'bg-green-500';
  let bmiPercent = 0;

  if (bmi < 18.5) {
    bmiCategory = 'Underweight';
    bmiColor = 'text-amber-600 bg-amber-50 border-amber-200';
    bmiBarColor = 'bg-amber-500';
    bmiPercent = Math.min((bmi / 18.5) * 30, 30);
  } else if (bmi < 25) {
    bmiCategory = 'Healthy Weight';
    bmiColor = 'text-green-600 bg-green-50 border-green-200';
    bmiBarColor = 'bg-primary';
    bmiPercent = 30 + ((bmi - 18.5) / 6.5) * 30;
  } else if (bmi < 30) {
    bmiCategory = 'Overweight';
    bmiColor = 'text-orange-600 bg-orange-50 border-orange-200';
    bmiBarColor = 'bg-orange-500';
    bmiPercent = 60 + ((bmi - 25) / 5) * 20;
  } else {
    bmiCategory = 'Obesity';
    bmiColor = 'text-red-600 bg-red-50 border-red-200';
    bmiBarColor = 'bg-red-500';
    bmiPercent = Math.min(80 + ((bmi - 30) / 10) * 20, 100);
  }

  // 2. BBI (Ideal Body Weight)
  const bbi = 22 * (heightInMeters * heightInMeters);

  // 3. BMR Calculations
  const bmrHarrisBenedict = gender === 'male'
    ? 66.4730 + (13.7516 * weight) + (5.0033 * height) - (6.7550 * age)
    : 655.0955 + (9.5634 * weight) + (1.8496 * height) - (4.6756 * age);

  const bmrMifflin = gender === 'male'
    ? (10 * weight) + (6.25 * height) - (5 * age) + 5
    : (10 * weight) + (6.25 * height) - (5 * age) - 161;

  const selectedBmr = healthStatus === 'sehat' ? bmrHarrisBenedict : bmrMifflin;

  // 4. TDEE Calculations
  const activityMultipliers = {
    light: 1.545,
    moderate: 1.845,
    heavy: 2.2,
  };
  const multiplier = activityMultipliers[activity];
  const tdee = selectedBmr * multiplier;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-md transition-all">
      <div className="bg-white rounded-3xl w-full max-w-4xl shadow-2xl overflow-hidden border border-border flex flex-col md:flex-row max-h-[90vh] md:max-h-[85vh] relative">
        
        {/* Absolute positioned close button for all screen sizes */}
        <button 
          onClick={onClose}
          className="absolute right-4 top-4 z-20 p-2 text-gray-400 hover:text-gray-600 hover:bg-secondary rounded-full transition-all cursor-pointer"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Left Side: Inputs */}
        <div className="flex-1 p-6 overflow-y-auto border-r border-border scrollbar-none">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-gray-900 font-serif">BMI & Calorie Calculator</h2>
          </div>

          <div className="space-y-5">
            {/* Gender */}
            <div>
              <label className="text-xs font-bold text-gray-500 uppercase tracking-wider block mb-2">Gender</label>
              <div className="grid grid-cols-2 gap-3">
                <button
                  type="button"
                  onClick={() => setGender('male')}
                  className={`py-2.5 px-4 rounded-2xl border text-sm font-semibold transition-all flex items-center justify-center gap-2 cursor-pointer ${
                    gender === 'male'
                      ? 'bg-primary/10 border-primary text-primary shadow-sm'
                      : 'border-border text-gray-700 hover:bg-secondary'
                  }`}
                >
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4 shrink-0">
                    <path d="M12 12a5 5 0 1 0 0-10 5 5 0 0 0 0 10Z" />
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                    <path d="m9 15 3 4 3-4" /> 
                  </svg>
                  <span>Male</span>
                </button>
                <button
                  type="button"
                  onClick={() => setGender('female')}
                  className={`py-2.5 px-4 rounded-2xl border text-sm font-semibold transition-all flex items-center justify-center gap-2 cursor-pointer ${
                    gender === 'female'
                      ? 'bg-primary/10 border-primary text-primary shadow-sm'
                      : 'border-border text-gray-700 hover:bg-secondary'
                  }`}
                >
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4 shrink-0">
                    <path d="M12 12a5 5 0 1 0 0-10 5 5 0 0 0 0 10Z" />
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                    <path d="M8.5 12c-1.5 1.5-2.5 4-2.5 9" />
                    <path d="M15.5 12c1.5 1.5 2.5 4 2.5 9" />
                  </svg>
                  <span>Female</span>
                </button>
              </div>
            </div>

            {/* Age, Weight, Height Grid */}
            <div className="grid grid-cols-3 gap-3">
              <div>
                <label className="text-xs font-bold text-gray-500 uppercase tracking-wider block mb-1.5">Age</label>
                <input
                  type="number"
                  min="1"
                  max="120"
                  value={age}
                  onChange={(e) => setAge(Math.max(1, parseInt(e.target.value) || 0))}
                  className="w-full px-4 py-2 rounded-2xl border border-border text-sm font-medium focus:outline-primary bg-secondary/30 focus:bg-white transition-all text-center"
                />
              </div>
              <div>
                <label className="text-xs font-bold text-gray-500 uppercase tracking-wider block mb-1.5">Weight (kg)</label>
                <input
                  type="number"
                  min="1"
                  max="300"
                  value={weight}
                  onChange={(e) => setWeight(Math.max(1, parseFloat(e.target.value) || 0))}
                  className="w-full px-4 py-2 rounded-2xl border border-border text-sm font-medium focus:outline-primary bg-secondary/30 focus:bg-white transition-all text-center"
                />
              </div>
              <div>
                <label className="text-xs font-bold text-gray-500 uppercase tracking-wider block mb-1.5">Height (cm)</label>
                <input
                  type="number"
                  min="1"
                  max="300"
                  value={height}
                  onChange={(e) => setHeight(Math.max(1, parseFloat(e.target.value) || 0))}
                  className="w-full px-4 py-2 rounded-2xl border border-border text-sm font-medium focus:outline-primary bg-secondary/30 focus:bg-white transition-all text-center"
                />
              </div>
            </div>

            {/* Condition Select (Healthy vs Chronic) */}
            <div>
              <label className="text-xs font-bold text-gray-500 uppercase tracking-wider block mb-2">Health Condition</label>
              <div className="grid grid-cols-2 gap-3">
                <button
                  type="button"
                  onClick={() => setHealthStatus('sehat')}
                  className={`py-2.5 px-4 rounded-2xl border text-sm font-semibold transition-all flex items-center justify-center gap-2 cursor-pointer ${
                    healthStatus === 'sehat'
                      ? 'bg-green-500/10 border-green-500 text-green-700 shadow-sm'
                      : 'border-border text-gray-700 hover:bg-secondary'
                  }`}
                >
                  <Heart className="w-4 h-4 shrink-0" />
                  <span>Healthy</span>
                </button>
                <button
                  type="button"
                  onClick={() => setHealthStatus('sakit')}
                  className={`py-2.5 px-4 rounded-2xl border text-sm font-semibold transition-all flex items-center justify-center gap-2 cursor-pointer ${
                    healthStatus === 'sakit'
                      ? 'bg-red-500/10 border-red-500 text-red-700 shadow-sm'
                      : 'border-border text-gray-700 hover:bg-secondary'
                  }`}
                >
                  <Activity className="w-4 h-4 shrink-0" />
                  <span>Chronic</span>
                </button>
              </div>
            </div>

            {/* Activity Level Selector */}
            <div>
              <label className="text-xs font-bold text-gray-500 uppercase tracking-wider block mb-2">Activity Level</label>
              <select
                value={activity}
                onChange={(e: any) => setActivity(e.target.value as any)}
                className="w-full px-4 py-2.5 rounded-2xl border border-border text-sm font-medium focus:outline-primary bg-secondary/35 cursor-pointer"
              >
                <option value="light">Light / Sedentary (1.545)</option>
                <option value="moderate">Moderate / Active (1.845)</option>
                <option value="heavy">Heavy / Vigorous (2.20)</option>
              </select>
            </div>
          </div>
        </div>

        {/* Right Side: Results */}
        <div className="flex-1 bg-gradient-to-b from-secondary/40 to-secondary/15 p-6 overflow-y-auto flex flex-col justify-center max-h-[50vh] md:max-h-none scrollbar-none">
          <div className="space-y-6">
            {/* BMI Display */}
            <div>
              <div className="flex justify-between items-baseline mb-2 pr-8">
                <span className="text-sm font-semibold text-gray-600">BMI</span>
                <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold border ${bmiColor}`}>
                  {bmiCategory}
                </span>
              </div>
              <div className="flex items-baseline gap-2 mb-3">
                <span className="text-4xl font-extrabold text-gray-900 font-serif">{bmi.toFixed(1)}</span>
                <span className="text-xs text-gray-400">kg/m²</span>
              </div>

              {/* Slider Gauge */}
              <div className="space-y-1">
                <div className="h-2 w-full bg-gray-200 rounded-full relative overflow-hidden">
                  <div className={`h-full rounded-full ${bmiBarColor}`} style={{ width: `${bmiPercent}%` }} />
                </div>
                <div className="flex justify-between text-[9px] text-gray-400 font-bold px-0.5">
                  <span>Under (18.5)</span>
                  <span>Normal (22.0)</span>
                  <span>Over (25.0)</span>
                  <span>Obese (30.0)</span>
                </div>
              </div>
            </div>

            {/* Weight summary cards */}
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-white p-3 rounded-2xl border border-border/80 shadow-sm">
                <span className="text-[10px] font-bold text-gray-450 uppercase tracking-wider block mb-0.5">Actual Weight</span>
                <span className="text-xl font-bold text-gray-800 font-serif">{weight} kg</span>
              </div>
              <div className="bg-white p-3 rounded-2xl border border-border/80 shadow-sm">
                <span className="text-[10px] font-bold text-gray-450 uppercase tracking-wider block mb-0.5">Ideal Weight (BBI)</span>
                <span className="text-xl font-bold text-gray-800 font-serif">{bbi.toFixed(1)} kg</span>
              </div>
            </div>

            {/* BMR and TDEE results */}
            <div className="space-y-3">
              <div className="bg-white p-4 rounded-2xl border border-border/80 shadow-sm relative overflow-hidden flex items-center justify-between">
                <div>
                  <span className="text-[10px] font-bold text-orange-600 uppercase tracking-wider block mb-0.5">Basal Metabolic Rate (BMR)</span>
                  <div className="flex items-baseline gap-1.5">
                    <span className="text-2xl font-extrabold text-gray-800 font-serif">{Math.round(selectedBmr)}</span>
                    <span className="text-xs text-gray-500 font-medium">kcal/day</span>
                  </div>
                </div>
                <div className="w-8 h-8 rounded-full bg-orange-100 flex items-center justify-center text-orange-600 shrink-0">
                  <Flame className="w-4 h-4" />
                </div>
              </div>

              <div className="bg-primary text-primary-foreground p-4 rounded-2xl shadow-md relative overflow-hidden flex items-center justify-between">
                <div>
                  <span className="text-[10px] font-bold text-white/80 uppercase tracking-wider block mb-0.5">Total Daily Energy (TDEE)</span>
                  <div className="flex items-baseline gap-1.5">
                    <span className="text-3xl font-extrabold font-serif">{Math.round(tdee)}</span>
                    <span className="text-xs text-white/85">kcal/day</span>
                  </div>
                  <div className="text-[10px] text-white/80 mt-0.5 font-semibold">
                    Multiplier: x{multiplier}
                  </div>
                </div>
                <div className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center text-white shrink-0">
                  <Zap className="w-4 h-4" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

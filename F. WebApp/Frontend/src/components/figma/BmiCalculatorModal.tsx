import { useState } from 'react';
import { X, Heart, Activity, Flame, Zap } from 'lucide-react';

interface BmiCalculatorModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function BmiCalculatorModal({ isOpen, onClose }: BmiCalculatorModalProps) {
  // Input states
  const [gender, setGender] = useState<'male' | 'female'>('male');
  const [age, setAge] = useState<number | string>(30);
  const [weight, setWeight] = useState<number | string>(70);
  const [height, setHeight] = useState<number | string>(170);
  const [healthStatus, setHealthStatus] = useState<'sehat' | 'sakit'>('sehat');
  const [activity, setActivity] = useState<'light' | 'moderate' | 'heavy'>('moderate');

  if (!isOpen) return null;

  // Parse strings to numbers for calculations
  const numAge = Number(age) || 0;
  const numWeight = Number(weight) || 0;
  const numHeight = Number(height) || 0;

  // 1. BMI Calculation
  const heightInMeters = numHeight / 100;
  const bmi = heightInMeters > 0 ? numWeight / (heightInMeters * heightInMeters) : 0;

  // BMI Category & Styling
  let bmiCategory = 'Healthy Weight';
  let bmiColor = 'text-green-600 bg-green-50 border-green-200';
  let bmiBarColor = 'bg-green-500';
  let bmiPercent = 0;

  if (bmi < 18.5) {
    bmiCategory = 'Underweight';
    bmiColor = 'text-amber-600 bg-amber-50 border-amber-200';
    bmiBarColor = 'bg-amber-500';
    bmiPercent = Math.min((bmi / 18.5) * 20, 20);
  } else if (bmi <= 24.9) {
    bmiCategory = 'Normal';
    bmiColor = 'text-green-600 bg-green-50 border-green-200';
    bmiBarColor = 'bg-primary';
    bmiPercent = 20 + ((bmi - 18.5) / 6.5) * 30;
  } else if (bmi <= 29.9) {
    bmiCategory = 'Overweight';
    bmiColor = 'text-orange-600 bg-orange-50 border-orange-200';
    bmiBarColor = 'bg-orange-500';
    bmiPercent = 50 + ((bmi - 25) / 5) * 25;
  } else if (bmi <= 34.9) {
    bmiCategory = 'Obesity Class I';
    bmiColor = 'text-red-600 bg-red-50 border-red-200';
    bmiBarColor = 'bg-red-500';
    bmiPercent = Math.min(75 + ((bmi - 30) / 10) * 15, 90);
  } else if (bmi <= 39.9) {
    bmiCategory = 'Obesity Class II';
    bmiColor = 'text-red-700 bg-red-100 border-red-300';
    bmiBarColor = 'bg-red-600';
    bmiPercent = Math.min(90 + ((bmi - 35) / 5) * 5, 95);
  } else {
    bmiCategory = 'Obesity Class III';
    bmiColor = 'text-red-800 bg-red-200 border-red-400';
    bmiBarColor = 'bg-red-700';
    bmiPercent = 100;
  }

  // 2. BBI (Ideal Body Weight) using Broca's Formula
  const baseWeight = numHeight - 100;
  const bbi = gender === 'male'
    ? (numHeight < 160 ? baseWeight : baseWeight - (baseWeight * 0.10))
    : (numHeight < 150 ? baseWeight : baseWeight - (baseWeight * 0.15));

  const idealMin = (18.5 * (numHeight / 100) ** 2).toFixed(1);
  const idealMax = (24.9 * (numHeight / 100) ** 2).toFixed(1);

  // 3. BMR Calculations
  const bmrHarrisBenedict = gender === 'male'
    ? 66.4730 + (13.7516 * numWeight) + (5.0033 * numHeight) - (6.7550 * numAge)
    : 655.0955 + (9.5634 * numWeight) + (1.8496 * numHeight) - (4.6756 * numAge);

  const bmrMifflin = gender === 'male'
    ? (10 * numWeight) + (6.25 * numHeight) - (5 * numAge) + 5
    : (10 * numWeight) + (6.25 * numHeight) - (5 * numAge) - 161;

  const selectedBmr = healthStatus === 'sehat' ? bmrHarrisBenedict : bmrMifflin;

  // 4. TDEE Calculations
  const activityMultipliers = {
    light: 1.4,
    moderate: 1.7,
    heavy: 2.0,
  };
  const multiplier = activityMultipliers[activity];
  const tdee = selectedBmr * multiplier;

  return (
    <div className="fixed inset-0 z-50 flex items-start md:items-center justify-center p-4 bg-black/50 backdrop-blur-md transition-all overflow-y-auto">
      <div className="bg-white rounded-3xl w-full max-w-4xl shadow-2xl overflow-hidden border border-border flex flex-col md:flex-row my-4 md:my-0 md:max-h-[85vh] relative">
        
        {/* Absolute positioned close button for all screen sizes */}
        <button 
          onClick={onClose}
          className="absolute right-4 top-4 z-20 p-2 text-gray-400 hover:text-gray-600 hover:bg-secondary rounded-full transition-all cursor-pointer"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Left Side: Inputs */}
        <div className="flex-none md:flex-1 p-6 md:overflow-y-auto border-b md:border-b-0 md:border-r border-border scrollbar-none">
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
                <label className="text-[10px] sm:text-xs font-bold text-gray-500 uppercase tracking-wider block mb-1.5 whitespace-nowrap text-center">Age</label>
                <input
                  type="number"
                  value={age}
                  onChange={(e) => setAge(e.target.value === '' ? '' : parseInt(e.target.value))}
                  onBlur={() => setAge(Math.max(1, Math.min(120, Number(age) || 1)))}
                  className="w-full px-4 py-2 rounded-2xl border border-border text-sm font-medium focus:outline-primary bg-secondary/30 focus:bg-white transition-all text-center"
                />
              </div>
              <div>
                <label className="text-[10px] sm:text-xs font-bold text-gray-500 uppercase tracking-wider block mb-1.5 whitespace-nowrap text-center">Weight (kg)</label>
                <input
                  type="number"
                  value={weight}
                  onChange={(e) => setWeight(e.target.value === '' ? '' : parseFloat(e.target.value))}
                  onBlur={() => setWeight(Math.max(1, Math.min(300, Number(weight) || 1)))}
                  className="w-full px-4 py-2 rounded-2xl border border-border text-sm font-medium focus:outline-primary bg-secondary/30 focus:bg-white transition-all text-center"
                />
              </div>
              <div>
                <label className="text-[10px] sm:text-xs font-bold text-gray-500 uppercase tracking-wider block mb-1.5 whitespace-nowrap text-center">Height (cm)</label>
                <input
                  type="number"
                  value={height}
                  onChange={(e) => setHeight(e.target.value === '' ? '' : parseFloat(e.target.value))}
                  onBlur={() => setHeight(Math.max(1, Math.min(300, Number(height) || 1)))}
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
              <div className="relative group/select">
                <select
                  value={activity}
                  onChange={(e: any) => setActivity(e.target.value as any)}
                  className="w-full px-4 py-2.5 pr-10 rounded-2xl border border-border text-sm font-semibold focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 bg-secondary/35 hover:bg-secondary/60 cursor-pointer appearance-none transition-all text-gray-800"
                >
                  <option value="light">Light</option>
                  <option value="moderate">Moderate</option>
                  <option value="heavy">Heavy</option>
                </select>
                <div className="absolute inset-y-0 right-0 flex items-center pr-4 pointer-events-none text-gray-400 group-hover/select:text-primary transition-colors">
                  <div className="w-6 h-6 rounded-full bg-white shadow-sm flex items-center justify-center border border-border group-hover/select:border-primary/30 group-hover/select:animate-pulse">
                    <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M19 9l-7 7-7-7"></path>
                    </svg>
                  </div>
                </div>
              </div>
              
              {/* Activity Description */}
              <p className="text-xs text-gray-500 mt-2 ml-1 leading-relaxed transition-all duration-200 min-h-[32px]">
                {activity === 'light' && 'Mostly sitting, minimal exercise'}
                {activity === 'moderate' && 'Active lifestyle, regular exercise'}
                {activity === 'heavy' && 'Very active, intense physical work'}
              </p>
            </div>
          </div>
        </div>

        {/* Right Side: Results */}
        <div className="flex-none md:flex-1 bg-gradient-to-b from-secondary/40 to-secondary/15 p-6 pb-10 md:pb-6 md:overflow-y-auto flex flex-col justify-start md:justify-center scrollbar-none">
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
                  <div className={`h-full rounded-full ${bmiBarColor} transition-all duration-500`} style={{ width: `${bmiPercent}%` }} />
                </div>
                <div className="flex justify-between text-[9px] text-gray-400 font-bold px-0.5">
                  <span>Under (18.5)</span>
                  <span>Normal (25.0)</span>
                  <span>Over (30.0)</span>
                  <span>Obese (35.0+)</span>
                </div>
              </div>
            </div>

            {/* Weight summary cards */}
            <div className="flex flex-row gap-2 sm:gap-3 w-full">
              <div className="w-[35%] sm:flex-1 bg-white p-2.5 sm:p-3 rounded-2xl border border-border/80 shadow-sm flex flex-col justify-center items-center text-center">
                <span className="text-[9px] sm:text-[10px] font-bold text-gray-450 uppercase tracking-wider block mb-0.5">Actual</span>
                <span className="text-base sm:text-xl font-bold text-gray-800 font-serif">{numWeight} <span className="text-[10px] sm:text-sm font-sans font-normal text-gray-500">kg</span></span>
              </div>
              <div className="w-[65%] sm:flex-[1.2] bg-white p-2.5 sm:p-3 rounded-2xl border border-border/80 shadow-sm relative group hover:z-50 cursor-pointer transition-all hover:border-primary/50 flex flex-col justify-center items-center text-center">
                <span className="text-[9px] sm:text-[10px] font-bold text-gray-450 uppercase tracking-wider block mb-0.5">Ideal Weight</span>
                <span className="text-[13px] sm:text-xl font-bold font-serif whitespace-nowrap flex items-baseline justify-center gap-1 sm:gap-1.5 w-full">
                  <span className="text-gray-400 text-[10px] sm:text-sm font-semibold">{idealMin}</span>
                  <span className="text-gray-300 text-[10px] sm:text-sm">-</span>
                  <span className="text-primary">{bbi.toFixed(1)}</span>
                  <span className="text-gray-300 text-[10px] sm:text-sm">-</span>
                  <span className="text-gray-400 text-[10px] sm:text-sm font-semibold">{idealMax}</span>
                  <span className="text-[9px] sm:text-xs font-sans font-normal text-gray-500 ml-0.5">kg</span>
                </span>
                
                {/* Tooltip Hover */}
                <div className="absolute top-full left-1/2 -translate-x-1/2 mt-3 w-[220px] p-3 bg-white text-gray-800 text-xs rounded-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300 pointer-events-none shadow-xl border border-gray-100">
                  <div className="font-bold text-gray-800 mb-2 border-b border-gray-100 pb-1.5 text-center uppercase tracking-wider text-[10px]">Healthy Weight Zone</div>
                  <div className="flex justify-between items-center mb-1 text-[11px]">
                    <span className="text-gray-500 font-medium">Lower Bound</span>
                    <span className="font-semibold text-gray-800">{idealMin} kg</span>
                  </div>
                  <div className="flex justify-between items-center mb-1 text-[11px] bg-primary/5 rounded px-1 -mx-1 py-0.5">
                    <span className="text-primary font-bold">Ideal Weight</span>
                    <span className="font-bold text-primary">{bbi.toFixed(1)} kg</span>
                  </div>
                  <div className="flex justify-between items-center mb-1 text-[11px]">
                    <span className="text-gray-500 font-medium">Upper Bound</span>
                    <span className="font-semibold text-gray-800">{idealMax} kg</span>
                  </div>
                  <div className="text-[9px] text-gray-400 leading-relaxed mt-2 text-center border-t border-gray-50 pt-2">
                    Values based on Broca's formula (Ideal) and normal BMI tolerance range (18.5 - 24.9).
                  </div>
                  <div className="absolute bottom-full left-1/2 -translate-x-1/2 border-6 border-transparent border-b-white drop-shadow-sm"></div>
                </div>
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

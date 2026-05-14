import React, { useMemo, useState } from 'react';

interface AnalysisResult {
  energy?: {
    bmi?: number;
    bbr?: number;
    bbi?: number;
    bmr?: number;
    tdee?: number;
  };
  anthropometrics?: {
    bmi?: number;
    bbr?: number;
    bbi?: number;
  };
  bmi?: number;
  bbr?: number;
  bbi?: number;
  bmr?: number;
  tdee?: number;
  guidelines: {
    [key: string]: {
      [key: string]: any;
    };
  };
  [key: string]: any;
}

interface ProfileResultsProps {
  analysisResult: AnalysisResult;
  formData: {
    gender: string;
    age: number;
    weight: number;
    height: number;
  };
  onFormUpdate?: (data: Partial<{ gender: string; age: number; weight: number; height: number }>) => void;
}

export const ProfileResults: React.FC<ProfileResultsProps> = ({ analysisResult, formData, onFormUpdate }) => {
  const [editing, setEditing] = useState<null | 'age' | 'weight' | 'height'>(null);
  const [tempValue, setTempValue] = useState<string>('');
  const firstValidNumber = (...values: unknown[]): number | undefined => {
    for (const value of values) {
      if (typeof value === 'number' && Number.isFinite(value)) {
        return value;
      }
    }
    return undefined;
  };

  const bmiValue = firstValidNumber(
    analysisResult.energy?.bmi,
    analysisResult.anthropometrics?.bmi,
    analysisResult.bmi
  );
  const bbrValue = firstValidNumber(
    analysisResult.energy?.bbr,
    analysisResult.energy?.bbi,
    analysisResult.anthropometrics?.bbr,
    analysisResult.anthropometrics?.bbi,
    analysisResult.bbr,
    analysisResult.bbi
  );
  const bmrValue = firstValidNumber(analysisResult.energy?.bmr, analysisResult.bmr);
  const tdeeValue = firstValidNumber(analysisResult.energy?.tdee, analysisResult.tdee);

  const getBMICategory = (bmi: number) => {
    if (bmi < 18.5) return { label: 'Underweight (<18.5)', color: 'bg-yellow-100 text-yellow-800', severity: 'yellow' };
    if (bmi < 25) return { label: 'Normal weight (18.5–24.9)', color: 'bg-green-100 text-green-800', severity: 'green' };
    if (bmi < 30) return { label: 'Overweight (25–29.9)', color: 'bg-yellow-100 text-yellow-800', severity: 'yellow' };
    if (bmi < 35) return { label: 'Obesity Class I (30–34.9)', color: 'bg-red-100 text-red-800', severity: 'red' };
    if (bmi < 40) return { label: 'Obesity Class II (35–39.9)', color: 'bg-red-100 text-red-800', severity: 'red' };
    return { label: 'Obesity Class III (≥40)', color: 'bg-red-100 text-red-800', severity: 'red' };
  };

  const bmiCategory = useMemo(() => {
    if (bmiValue === undefined) {
      return null;
    }
    return getBMICategory(bmiValue);
  }, [bmiValue]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <h3 className="text-2xl font-bold text-gray-800 flex items-center">
        <i className="fas fa-chart-bar text-blue-500 mr-3"></i>
        Analysis Results
      </h3>

      {/* Energy Metrics Grid */}
      <div className="grid md:grid-cols-2 gap-4">
        {/* BMI Card */}
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4 border-l-4 border-blue-500">
          <p className="text-sm text-gray-600 font-semibold mb-2">
            <i className="fas fa-chart-pie text-blue-500 mr-2"></i>
            Body Mass Index (BMI)
          </p>
          <p className="text-3xl font-bold mb-2" style={{ color: (() => {
            if (!bmiCategory) return '#374151';
            return bmiCategory.severity === 'green' ? '#059669' : bmiCategory.severity === 'yellow' ? '#b45309' : '#b91c1c';
          })() }}>
            {bmiValue !== undefined ? bmiValue.toFixed(1) : 'N/A'}
          </p>
          <span
            className={`inline-block px-3 py-1 rounded-full text-sm font-semibold ${
              bmiCategory ? bmiCategory.color : 'bg-gray-100 text-gray-700'
            }`}
          >
            {bmiCategory ? bmiCategory.label : 'N/A'}
          </span>
        </div>

        {/* BBR Card */}
        <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-4 border-l-4 border-green-500">
          <p className="text-sm text-gray-600 font-semibold mb-2">
            <i className="fas fa-weight text-green-500 mr-2"></i>
            Recommended Body Weight (RBW)
          </p>
          <p className="text-3xl font-bold text-green-600 mb-2">
            {bbrValue !== undefined ? `${bbrValue.toFixed(1)} kg` : 'N/A'}
          </p>
          <p className="text-xs text-gray-600">
            Delta: {bbrValue !== undefined ? `${(formData.weight - bbrValue).toFixed(1)} kg` : 'N/A'}
          </p>
        </div>

        {/* BMR Card */}
        <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-lg p-4 border-l-4 border-orange-500">
          <p className="text-sm text-gray-600 font-semibold mb-2">
            <i className="fas fa-fire text-orange-500 mr-2"></i>
            Basal Metabolic Rate (BMR)
          </p>
          <p className="text-3xl font-bold text-orange-600">
            {bmrValue !== undefined ? `${bmrValue.toFixed(0)} kcal/day` : 'N/A'}
          </p>
        </div>

        {/* TDEE Card */}
        <div className="bg-gradient-to-br from-red-50 to-red-100 rounded-lg p-4 border-l-4 border-red-500">
          <p className="text-sm text-gray-600 font-semibold mb-2">
            <i className="fas fa-bolt text-red-500 mr-2"></i>
            Total Daily Energy Expenditure (TDEE)
          </p>
          <p className="text-3xl font-bold text-red-600">
            {tdeeValue !== undefined ? `${tdeeValue.toFixed(0)} kcal/day` : 'N/A'}
          </p>
        </div>
      </div>

      {/* Personal Info */}
      <div className="bg-gray-50 rounded-lg p-4">
        <p className="text-sm font-semibold text-gray-700 mb-3">
          <i className="fas fa-user text-gray-500 mr-2"></i>
          Personal Data
        </p>
        <div className="grid md:grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-600">Gender:</span>
            <span className="font-semibold ml-2">{formData.gender === 'M' ? 'Male' : 'Female'}</span>
          </div>
          <div>
            <span className="text-gray-600">Age:</span>
            <span className="font-semibold ml-2">
              {editing === 'age' ? (
                <input
                  autoFocus
                  className="w-[80px] text-center bg-transparent outline-none"
                  type="number"
                  min={0}
                  max={120}
                  value={tempValue}
                  onChange={(e) => setTempValue(e.target.value)}
                  onBlur={() => {
                    const v = Math.max(0, Math.min(120, parseInt(tempValue || '0')));
                    setEditing(null);
                    if (v !== formData.age && typeof v === 'number' && onFormUpdate) {
                      onFormUpdate({ age: v });
                    }
                  }}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') (e.target as HTMLInputElement).blur();
                    if (e.key === 'Escape') setEditing(null);
                  }}
                />
              ) : (
                <button
                  onClick={() => {
                    setEditing('age');
                    setTempValue(String(formData.age));
                  }}
                  className="ml-2"
                >
                  {formData.age} years
                </button>
              )}
            </span>
          </div>
          <div>
            <span className="text-gray-600">Height:</span>
            <span className="font-semibold ml-2">
              {editing === 'height' ? (
                <input
                  autoFocus
                  className="w-[80px] text-center bg-transparent outline-none"
                  type="number"
                  min={50}
                  max={300}
                  value={tempValue}
                  onChange={(e) => setTempValue(e.target.value)}
                  onBlur={() => {
                    const v = Math.max(50, Math.min(300, parseFloat(tempValue || '0')));
                    setEditing(null);
                    if (v !== formData.height && typeof v === 'number' && onFormUpdate) {
                      onFormUpdate({ height: v });
                    }
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
                    setTempValue(String(formData.height));
                  }}
                  className="ml-2"
                >
                  {formData.height} cm
                </button>
              )}
            </span>
          </div>
          <div>
            <span className="text-gray-600">Weight:</span>
            <span className="font-semibold ml-2">
              {editing === 'weight' ? (
                <input
                  autoFocus
                  className="w-[80px] text-center bg-transparent outline-none"
                  type="number"
                  min={10}
                  max={500}
                  value={tempValue}
                  onChange={(e) => setTempValue(e.target.value)}
                  onBlur={() => {
                    const v = Math.max(10, Math.min(500, parseFloat(tempValue || '0')));
                    setEditing(null);
                    if (v !== formData.weight && typeof v === 'number' && onFormUpdate) {
                      onFormUpdate({ weight: v });
                    }
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
                    setTempValue(String(formData.weight));
                  }}
                  className="ml-2"
                >
                  {formData.weight} kg
                </button>
              )}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

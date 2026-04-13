import React, { useMemo } from 'react';

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
}

export const ProfileResults: React.FC<ProfileResultsProps> = ({ analysisResult, formData }) => {
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
    if (bmi < 18.5) return { label: 'Underweight', color: 'bg-blue-100 text-blue-800' };
    if (bmi < 25) return { label: 'Normal', color: 'bg-green-100 text-green-800' };
    if (bmi < 30) return { label: 'Overweight', color: 'bg-yellow-100 text-yellow-800' };
    return { label: 'Obese', color: 'bg-red-100 text-red-800' };
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
        Hasil Analisis
      </h3>

      {/* Energy Metrics Grid */}
      <div className="grid md:grid-cols-2 gap-4">
        {/* BMI Card */}
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4 border-l-4 border-blue-500">
          <p className="text-sm text-gray-600 font-semibold mb-2">
            <i className="fas fa-chart-pie text-blue-500 mr-2"></i>
            Index Massa Tubuh (BMI)
          </p>
          <p className="text-3xl font-bold text-blue-600 mb-2">
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
            Berat Badan Rekomendasi (BBR)
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
            {bmrValue !== undefined ? `${bmrValue.toFixed(0)} kkal/hari` : 'N/A'}
          </p>
        </div>

        {/* TDEE Card */}
        <div className="bg-gradient-to-br from-red-50 to-red-100 rounded-lg p-4 border-l-4 border-red-500">
          <p className="text-sm text-gray-600 font-semibold mb-2">
            <i className="fas fa-bolt text-red-500 mr-2"></i>
            Total Daily Energy Expenditure (TDEE)
          </p>
          <p className="text-3xl font-bold text-red-600">
            {tdeeValue !== undefined ? `${tdeeValue.toFixed(0)} kkal/hari` : 'N/A'}
          </p>
        </div>
      </div>

      {/* Personal Info */}
      <div className="bg-gray-50 rounded-lg p-4">
        <p className="text-sm font-semibold text-gray-700 mb-3">
          <i className="fas fa-user text-gray-500 mr-2"></i>
          Data Pribadi
        </p>
        <div className="grid md:grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-600">Jenis Kelamin:</span>
            <span className="font-semibold ml-2">{formData.gender === 'M' ? 'Pria' : 'Wanita'}</span>
          </div>
          <div>
            <span className="text-gray-600">Usia:</span>
            <span className="font-semibold ml-2">{formData.age} tahun</span>
          </div>
          <div>
            <span className="text-gray-600">Tinggi:</span>
            <span className="font-semibold ml-2">{formData.height} cm</span>
          </div>
          <div>
            <span className="text-gray-600">Berat:</span>
            <span className="font-semibold ml-2">{formData.weight} kg</span>
          </div>
        </div>
      </div>
    </div>
  );
};

import React from 'react';

interface FormData {
  gender: string;
  age: number;
  weight: number;
  height: number;
  activity: string;
  diseases: string[];
  food_preferences: string[];
  algorithm: string;
}

interface UserFormProps {
  formData: FormData;
  onFormChange: (newFormData: FormData) => void;
  onSubmit: () => void;
  isLoading: boolean;
}

const DISEASES = {
  normal: 'Normal',
  dm2: 'Diabetes Tipe 2',
  hypertension: 'Hipertensi',
  cvd: 'Penyakit Kardiovaskular',
  cholesterol: 'Kolesterol Tinggi',
  ckd: 'Penyakit Ginjal Kronis',
};

const ACTIVITIES = {
  '1.545': 'Sedentary (Jarang Aktivitas)',
  '1.845': 'Active (Aktivitas Normal)',
  '2.2': 'Vigorous (Aktivitas Intens)',
};

export const UserForm: React.FC<UserFormProps> = ({
  formData,
  onFormChange,
  onSubmit,
  isLoading,
}) => {
  const handleGenderChange = (value: string) => {
    onFormChange({ ...formData, gender: value });
  };

  const handleInputChange = (field: keyof Omit<FormData, 'diseases' | 'food_preferences'>) => (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    onFormChange({
      ...formData,
      [field]: field === 'age' || field === 'weight' || field === 'height'
        ? parseFloat(e.target.value)
        : e.target.value,
    });
  };

  const handleDiseaseToggle = (disease: string) => {
    let newDiseases: string[];

    if (disease === 'normal') {
      newDiseases = formData.diseases.includes('normal') ? [] : ['normal'];
    } else {
      if (formData.diseases.includes('normal')) {
        newDiseases = formData.diseases.filter((d) => d !== 'normal');
      } else {
        newDiseases = formData.diseases;
      }

      if (newDiseases.includes(disease)) {
        newDiseases = newDiseases.filter((d) => d !== disease);
      } else {
        newDiseases = [...newDiseases, disease];
      }

      if (newDiseases.length === 0) {
        newDiseases = ['normal'];
      }
    }

    onFormChange({ ...formData, diseases: newDiseases });
  };

  const handleAlgorithmChange = (value: string) => {
    onFormChange({ ...formData, algorithm: value });
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <h2 className="text-3xl font-bold text-gray-800 flex items-center">
        <i className="fas fa-user-circle text-blue-500 mr-3 text-4xl"></i>
        Profil Pengguna
      </h2>

      {/* Form Grid */}
      <div className="space-y-8">
        {/* Row 1: Gender & Age & Weight */}
        <div className="grid md:grid-cols-3 gap-6">
          {/* Gender */}
          <div>
            <label className="block text-sm font-bold text-gray-700 mb-3">
              <i className="fas fa-venus-mars text-pink-500 mr-2"></i>
              Jenis Kelamin
            </label>
            <div className="flex gap-3">
              <label className="flex-1 cursor-pointer">
                <input
                  type="radio"
                  name="gender"
                  value="M"
                  checked={formData.gender === 'M'}
                  onChange={(e) => handleGenderChange(e.target.value)}
                  className="sr-only peer"
                />
                <div className="p-4 border-2 rounded-xl text-center font-semibold transition-all peer-checked:border-blue-500 peer-checked:bg-blue-50 border-gray-300 hover:border-gray-400">
                  <i className="fas fa-mars text-2xl text-blue-600 mb-2 block"></i>
                  <span className="text-sm text-gray-700">Pria</span>
                </div>
              </label>
              <label className="flex-1 cursor-pointer">
                <input
                  type="radio"
                  name="gender"
                  value="F"
                  checked={formData.gender === 'F'}
                  onChange={(e) => handleGenderChange(e.target.value)}
                  className="sr-only peer"
                />
                <div className="p-4 border-2 rounded-xl text-center font-semibold transition-all peer-checked:border-pink-500 peer-checked:bg-pink-50 border-gray-300 hover:border-gray-400">
                  <i className="fas fa-venus text-2xl text-pink-600 mb-2 block"></i>
                  <span className="text-sm text-gray-700">Wanita</span>
                </div>
              </label>
            </div>
          </div>

          {/* Age */}
          <div>
            <label className="block text-sm font-bold text-gray-700 mb-3">
              <i className="fas fa-calendar-alt text-green-500 mr-2"></i>
              Usia (tahun)
            </label>
            <input
              type="number"
              value={formData.age}
              onChange={handleInputChange('age')}
              min="18"
              max="100"
              className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 font-semibold"
              placeholder="30"
            />
          </div>

          {/* Weight */}
          <div>
            <label className="block text-sm font-bold text-gray-700 mb-3">
              <i className="fas fa-weight text-orange-500 mr-2"></i>
              Berat Badan (kg)
            </label>
            <input
              type="number"
              value={formData.weight}
              onChange={handleInputChange('weight')}
              min="30"
              max="300"
              className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 font-semibold"
              placeholder="70"
            />
          </div>
        </div>

        {/* Row 2: Height & Activity */}
        <div className="grid md:grid-cols-2 gap-6">
          {/* Height */}
          <div>
            <label className="block text-sm font-bold text-gray-700 mb-3">
              <i className="fas fa-ruler-vertical text-purple-500 mr-2"></i>
              Tinggi Badan (cm)
            </label>
            <input
              type="number"
              value={formData.height}
              onChange={handleInputChange('height')}
              min="140"
              max="220"
              className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 font-semibold"
              placeholder="170"
            />
          </div>

          {/* Activity Factor */}
          <div>
            <label className="block text-sm font-bold text-gray-700 mb-3">
              <i className="fas fa-dumbbell text-red-500 mr-2"></i>
              Tingkat Aktivitas
            </label>
            <select
              value={formData.activity}
              onChange={handleInputChange('activity')}
              className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 font-semibold"
            >
              {Object.entries(ACTIVITIES).map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Row 3: Health Conditions */}
        <div>
          <label className="block text-sm font-bold text-gray-700 mb-4">
            <i className="fas fa-heart text-red-500 mr-2"></i>
            Kondisi Kesehatan
          </label>
          <div className="grid md:grid-cols-3 gap-3">
            {Object.entries(DISEASES).map(([key, label]) => (
              <label key={key} className="flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.diseases.includes(key)}
                  onChange={() => handleDiseaseToggle(key)}
                  className="w-4 h-4 text-blue-600 rounded"
                />
                <span className="ml-2 text-sm text-gray-700">{label}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Row 4: Algorithm Selection */}
        <div>
          <label className="block text-sm font-bold text-gray-700 mb-4">
            <i className="fas fa-cogs text-gray-500 mr-2"></i>
            Algoritma Optimasi
          </label>
          <div className="grid md:grid-cols-2 gap-4">
            <label className="cursor-pointer">
              <input
                type="radio"
                name="algorithm"
                value="greedy"
                checked={formData.algorithm === 'greedy'}
                onChange={(e) => handleAlgorithmChange(e.target.value)}
                className="sr-only peer"
              />
              <div className="p-4 border-2 rounded-lg transition-all peer-checked:border-blue-500 peer-checked:bg-blue-50 border-gray-300 hover:border-gray-400">
                <p className="font-semibold text-gray-700">Greedy Algorithm</p>
                <p className="text-xs text-gray-500">Cepat dan efisien</p>
              </div>
            </label>
            <label className="cursor-pointer">
              <input
                type="radio"
                name="algorithm"
                value="genetic"
                checked={formData.algorithm === 'genetic'}
                onChange={(e) => handleAlgorithmChange(e.target.value)}
                className="sr-only peer"
              />
              <div className="p-4 border-2 rounded-lg transition-all peer-checked:border-blue-500 peer-checked:bg-blue-50 border-gray-300 hover:border-gray-400">
                <p className="font-semibold text-gray-700">Genetic Algorithm</p>
                <p className="text-xs text-gray-500">Optimal tapi lambat</p>
              </div>
            </label>
          </div>
        </div>

        {/* Submit Button */}
        <button
          onClick={onSubmit}
          disabled={isLoading}
          className="w-full bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 disabled:from-gray-400 disabled:to-gray-400 text-white font-bold py-3 px-4 rounded-lg transition-all duration-300 flex items-center justify-center gap-2"
        >
          {isLoading ? (
            <>
              <i className="fas fa-spinner fa-spin"></i>
              Menganalisis...
            </>
          ) : (
            <>
              <i className="fas fa-check"></i>
              Analisis Profil
            </>
          )}
        </button>
      </div>
    </div>
  );
};

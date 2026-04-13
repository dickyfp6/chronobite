import React, { useState } from 'react';
import './App.css';
import { UserForm } from './components/UserForm';
import { ProfileResults } from './components/ProfileResults';
import { MenuDisplay } from './components/MenuDisplay';
import { Notifications } from './components/Notifications';
import { useNotifications } from './hooks/useNotifications';
import { useLocalStorage } from './hooks/useLocalStorage';
import { api } from './services/api';

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

interface AnalysisResult {
  success: boolean;
  energy: {
    bmi: number;
    bbr: number;
    bmr: number;
    tdee: number;
  };
  guidelines: Record<string, any>;
  [key: string]: any;
}

interface MenuResult {
  success: boolean;
  menu_plan: {
    meals: Record<string, any>;
    total_calories: number;
    total_protein: number;
    total_carbs: number;
    total_fat: number;
  };
}

function App() {
  // State
  const { notifications, showNotification } = useNotifications();
  const [formData, setFormData] = useLocalStorage<FormData>('formData', {
    gender: 'M',
    age: 30,
    weight: 70,
    height: 170,
    activity: '1.845',
    diseases: ['normal'],
    food_preferences: [],
    algorithm: 'greedy',
  });

  const [analysisResult, setAnalysisResult] = useLocalStorage<AnalysisResult | null>('analysisResult', null);
  const [menuResult, setMenuResult] = useLocalStorage<MenuResult['menu_plan'] | null>('menuResult', null);
  const [activeTab, setActiveTab] = useState<'profile' | 'nutrition' | 'menu' | 'constraints'>('profile');
  const [isLoading, setIsLoading] = useState(false);

  // Handlers
  const handleFormChange = (newFormData: FormData) => {
    setFormData(newFormData);
  };

  const handleSubmitForm = async () => {
    if (!formData.age || !formData.weight || !formData.height) {
      showNotification('Mohon lengkapi semua data', 'error');
      return;
    }

    setIsLoading(true);
    try {
      const result = await api.analyzeProfile(formData);
      setAnalysisResult(result);
      setMenuResult(null);
      setActiveTab('profile');
      showNotification('✓ Analisis profil selesai!', 'success');
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Gagal menganalisis profil';
      showNotification('❌ ' + errorMessage, 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateMenu = async () => {
    if (!analysisResult) {
      showNotification('Silakan analisis profil terlebih dahulu', 'error');
      return;
    }

    setIsLoading(true);
    try {
      const menuRequest = {
        algorithm: formData.algorithm,
        user_profile: formData,
        analysis_data: analysisResult,
        user_input: analysisResult,
      };

      const result = await api.generateMenu(menuRequest);
      setMenuResult(result.menu_plan);
      setActiveTab('menu');
      showNotification('✓ Menu berhasil dibuat!', 'success');
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Gagal membuat menu';
      showNotification('❌ ' + errorMessage, 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleBackToForm = () => {
    setAnalysisResult(null);
    setMenuResult(null);
    setActiveTab('profile');
    setFormData({
      gender: 'M',
      age: 30,
      weight: 70,
      height: 170,
      activity: '1.845',
      diseases: ['normal'],
      food_preferences: [],
      algorithm: 'greedy',
    });
    showNotification('Form direset', 'info');
  };

  const handleDownloadMenu = () => {
    if (menuResult) {
      const data = JSON.stringify(menuResult, null, 2);
      const blob = new Blob([data], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `menu-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      showNotification('✓ Menu berhasil diunduh', 'success');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-md">
        <div className="max-w-6xl mx-auto px-4 py-6">
          <h1 className="text-4xl font-bold text-gray-800 flex items-center">
            <i className="fas fa-leaf text-green-500 mr-3"></i>
            Nutrition DSS
          </h1>
          <p className="text-gray-600 mt-1">Sistem Rekomendasi Menu Nutrisi yang Dipersonalisasi</p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto p-4 py-8">
        <div className="bg-white rounded-lg shadow-xl overflow-hidden">
          <div className="p-6 md:p-8">
            {/* Form Section */}
            {!analysisResult ? (
              <div style={{ animation: 'slideIn 0.3s ease-out' }}>
                <UserForm
                  formData={formData}
                  onFormChange={handleFormChange}
                  onSubmit={handleSubmitForm}
                  isLoading={isLoading}
                />
              </div>
            ) : (
              <>
                {/* Results Header */}
                <div className="mb-6 pb-6 border-b-2 border-gray-200 flex items-center justify-between">
                  <h2 className="text-2xl font-bold text-gray-800">
                    <i className="fas fa-chart-line text-blue-500 mr-3"></i>
                    Hasil Analisis
                  </h2>
                  <button
                    onClick={handleBackToForm}
                    className="px-4 py-2 bg-gray-500 hover:bg-gray-600 text-white rounded-lg transition-colors flex items-center gap-2"
                  >
                    <i className="fas fa-arrow-left"></i>
                    Kembali ke Form
                  </button>
                </div>

                {/* Tabs */}
                <div className="mb-6 flex gap-2 border-b-2 border-gray-200 overflow-x-auto">
                  <button
                    onClick={() => setActiveTab('profile')}
                    className={`px-4 py-3 font-semibold transition-colors whitespace-nowrap ${
                      activeTab === 'profile'
                        ? 'text-blue-600 border-b-2 border-blue-600'
                        : 'text-gray-600 hover:text-gray-800'
                    }`}
                  >
                    <i className="fas fa-user-circle mr-2"></i>
                    Profil
                  </button>
                  <button
                    onClick={() => setActiveTab('nutrition')}
                    className={`px-4 py-3 font-semibold transition-colors whitespace-nowrap ${
                      activeTab === 'nutrition'
                        ? 'text-blue-600 border-b-2 border-blue-600'
                        : 'text-gray-600 hover:text-gray-800'
                    }`}
                  >
                    <i className="fas fa-apple-alt mr-2"></i>
                    Nutrisi
                  </button>
                  <button
                    onClick={() => handleGenerateMenu()}
                    disabled={isLoading}
                    className={`px-4 py-3 font-semibold transition-colors whitespace-nowrap ${
                      activeTab === 'menu'
                        ? 'text-blue-600 border-b-2 border-blue-600'
                        : 'text-gray-600 hover:text-gray-800'
                    } ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
                  >
                    <i className="fas fa-book-open mr-2"></i>
                    Menu {!menuResult && '(Klik untuk buat)'}
                  </button>
                </div>

                {/* Tab Content */}
                <div style={{ animation: 'slideIn 0.3s ease-out' }}>
                  {activeTab === 'profile' && analysisResult && (
                    <ProfileResults analysisResult={analysisResult} formData={formData} />
                  )}

                  {activeTab === 'nutrition' && analysisResult && (
                    <div className="space-y-6">
                      <h3 className="text-2xl font-bold text-gray-800">
                        <i className="fas fa-chart-pie text-purple-500 mr-3"></i>
                        Panduan Nutrisi
                      </h3>
                      <div className="bg-gray-50 rounded-lg p-6">
                        <pre className="text-xs overflow-auto">
                          {JSON.stringify(analysisResult.guidelines, null, 2)}
                        </pre>
                      </div>
                    </div>
                  )}

                  {activeTab === 'menu' && menuResult ? (
                    <MenuDisplay
                      menu={menuResult}
                      onDownload={handleDownloadMenu}
                      onRegenerate={handleGenerateMenu}
                      isLoading={isLoading}
                    />
                  ) : activeTab === 'menu' ? (
                    <div className="text-center py-12">
                      <p className="text-gray-600 mb-4">Menu belum dibuat</p>
                      <button
                        onClick={handleGenerateMenu}
                        disabled={isLoading}
                        className="px-6 py-3 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-400 text-white rounded-lg transition-colors"
                      >
                        {isLoading ? 'Membuat Menu...' : 'Buat Menu Sekarang'}
                      </button>
                    </div>
                  ) : null}
                </div>
              </>
            )}
          </div>
        </div>
      </main>

      {/* Notifications */}
      <Notifications notifications={notifications} />
    </div>
  );
}

export default App;

      {/* Notifications */}
      <Notifications notifications={notifications} />

      {/* CSS for animations */}
      <style>{`
        @keyframes slideIn {
          from {
            transform: translateX(20px);
            opacity: 0;
          }
          to {
            transform: translateX(0);
            opacity: 1;
          }
        }
      `}</style>
    </div>
  );
}

export default App;

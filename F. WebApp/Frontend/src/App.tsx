import { useState, useEffect } from 'react';
import { ThemeProvider } from 'next-themes';
import { I18nProvider } from './contexts/I18nContext';
import { Navbar } from './components/figma/Navbar';
import { Landing } from './pages/Landing';
import { AlgorithmSelect } from './pages/AlgorithmSelect';
import { InputWizard } from './pages/InputWizard';
import type { UserInputData } from './pages/InputWizard';
import { ProfileSummary } from './pages/ProfileSummary';
import { Results } from './pages/Results';
import { Report } from './pages/Report';

type Page = 'landing' | 'algorithm' | 'input' | 'profile' | 'results' | 'report';

export default function App() {
  const [currentPage, setCurrentPage] = useState<Page>(() => {
    const saved = sessionStorage.getItem('dss_current_page');
    return (saved as Page) || 'landing';
  });

  const [algorithm, setAlgorithm] = useState<'greedy' | 'genetic' | undefined>(() => {
    const saved = sessionStorage.getItem('dss_algorithm');
    return (saved as 'greedy' | 'genetic') || undefined;
  });

  const [userData, setUserData] = useState<UserInputData>(() => {
    const saved = sessionStorage.getItem('dss_user_data');
    return saved ? JSON.parse(saved) : {
      age: 18,
      weight: 30,
      height: 100,
      healthConditions: [],
      foodPreferences: [],
    };
  });

  const [showRestartConfirm, setShowRestartConfirm] = useState(false);

  // Check if there's active progress (not on landing page)
  const hasActiveProgress = () => {
    return currentPage !== 'landing';
  };

  // Handle home/logo click with confirmation if needed
  const handleHomeClick = () => {
    if (hasActiveProgress()) {
      setShowRestartConfirm(true);
    } else {
      setCurrentPage('landing');
    }
  };

  // Confirm restart and go to landing
  const handleRestartConfirm = () => {
    setShowRestartConfirm(false);
    setCurrentPage('landing');
    setAlgorithm(undefined);
    setUserData({
      age: 18,
      weight: 30,
      height: 100,
      healthConditions: [],
      foodPreferences: [],
    });
    sessionStorage.removeItem('dss_current_page');
    sessionStorage.removeItem('dss_algorithm');
    sessionStorage.removeItem('dss_user_data');
    sessionStorage.removeItem('dss_wizard_step');
    localStorage.clear();
  };

  useEffect(() => {
    if (algorithm) sessionStorage.setItem('dss_algorithm', algorithm);
    else sessionStorage.removeItem('dss_algorithm');
  }, [algorithm]);

  useEffect(() => {
    sessionStorage.setItem('dss_user_data', JSON.stringify(userData));
  }, [userData]);

  return (
    <ThemeProvider attribute="class" defaultTheme="light">
      <I18nProvider>
        <div className="min-h-screen bg-background text-foreground">
          <Navbar onHomeClick={handleHomeClick} />

          <main className="pt-16">
            {currentPage === 'landing' && (
              <Landing onStart={() => setCurrentPage('algorithm')} />
            )}

            {currentPage === 'algorithm' && (
              <AlgorithmSelect
                selected={algorithm}
                onSelect={setAlgorithm}
                onContinue={() => setCurrentPage('input')}
              />
            )}

            {currentPage === 'input' && (
              <InputWizard
                data={userData}
                onUpdate={(data) => setUserData({ ...userData, ...data })}
                onComplete={() => setCurrentPage('profile')}
              />
            )}

            {currentPage === 'profile' && (
              <ProfileSummary
                userData={userData}
                onBack={() => setCurrentPage('input')}
                onContinue={() => setCurrentPage('results')}
              />
            )}

            {currentPage === 'results' && (
              <Results
                userData={userData}
                onViewReport={() => setCurrentPage('report')}
              />
            )}

            {currentPage === 'report' && <Report userData={userData} />}
          </main>

          {/* Restart Confirmation Modal */}
          {showRestartConfirm && (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm px-4">
              <div className="w-full max-w-md rounded-2xl bg-white dark:bg-slate-800 p-6 shadow-2xl border border-emerald-200 dark:border-emerald-700">
                <h3 className="text-xl font-bold text-gray-900 dark:text-white">Mulai ulang halaman?</h3>
                <p className="mt-3 text-sm text-gray-600 dark:text-gray-300">
                  Progress saat ini akan dihapus dan form dimulai dari awal.
                </p>
                <div className="mt-6 flex flex-col sm:flex-row gap-3 sm:justify-end">
                  <button
                    onClick={() => setShowRestartConfirm(false)}
                    className="px-5 py-2.5 rounded-xl border border-gray-300 dark:border-slate-600 text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-slate-700 transition-all"
                  >
                    Batal
                  </button>
                  <button
                    onClick={handleRestartConfirm}
                    className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 text-white font-medium hover:from-emerald-600 hover:to-teal-600 transition-all"
                  >
                    Ya, mulai ulang
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </I18nProvider>
    </ThemeProvider>
  );
}

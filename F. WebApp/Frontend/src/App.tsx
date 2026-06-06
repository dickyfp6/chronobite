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
import { api } from './services/api';

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
  const [analysisResult, _setAnalysisResult] = useState<any>(() => {
    const saved = sessionStorage.getItem('dss_analysis_result_full');
    return saved ? JSON.parse(saved) : null;
  });

  const [menuPromise, setMenuPromise] = useState<Promise<any> | null>(null);

  const startMenuPrefetch = (analysis: any) => {
    if (menuPromise) return; // already prefetching

    const payload = {
      gender: userData.gender === 'male' ? 'M' : 'F',
      age: userData.age,
      weight: userData.weight,
      height: userData.height,
      activity: userData.activity || '1.845',
      diseases: userData.healthConditions.length > 0 ? userData.healthConditions : ['normal'],
      food_preferences: userData.foodPreferences,
      algorithm: algorithm || 'greedy',
    };

    const promise = api.generateMenu({
      algorithm: algorithm || 'greedy',
      user_profile: payload,
      analysis_data: analysis || {},
      user_input: analysis || {},
    });
    setMenuPromise(promise);
  };

  const setAnalysisResult = (result: any) => {
    _setAnalysisResult(result);
    if (result) {
      sessionStorage.setItem('dss_analysis_result_full', JSON.stringify(result));
      if (result.guidelines) {
        sessionStorage.setItem('dss_analysis_guidelines', JSON.stringify(result.guidelines));
      }
    } else {
      sessionStorage.removeItem('dss_analysis_result_full');
      sessionStorage.removeItem('dss_analysis_guidelines');
    }
  };

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
    <ThemeProvider attribute="class" defaultTheme="light" forcedTheme="light">
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
                onSelect={(algo) => {
                  setMenuPromise(null);
                  setAlgorithm(algo);
                }}
                onContinue={() => setCurrentPage('input')}
              />
            )}

            {currentPage === 'input' && (
              <InputWizard
                data={userData}
                onUpdate={(data) => {
                  setMenuPromise(null);
                  setUserData({ ...userData, ...data });
                }}
                onComplete={() => setCurrentPage('profile')}
              />
            )}

            {currentPage === 'profile' && (
              <ProfileSummary
                userData={userData}
                onBack={() => {
                  setMenuPromise(null);
                  setCurrentPage('input');
                }}
                onContinue={() => setCurrentPage('results')}
                onAnalysisComplete={(res) => {
                  setAnalysisResult(res);
                  startMenuPrefetch(res);
                }}
              />
            )}

            {currentPage === 'results' && (
              <Results
                userData={userData}
                algorithm={algorithm}
                analysisResult={analysisResult}
                menuPromise={menuPromise}
                onViewReport={() => setCurrentPage('report')}
              />
            )}

            {currentPage === 'report' && <Report userData={userData} />}
          </main>

          {/* Restart Confirmation Modal */}
          {showRestartConfirm && (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm px-4">
              <div className="w-full max-w-md rounded-2xl bg-white dark:bg-slate-800 p-6 shadow-2xl border border-border/80 dark:border-slate-700">
                <h3 className="text-xl font-bold text-gray-900 dark:text-white">Restart application?</h3>
                <p className="mt-3 text-sm text-gray-600 dark:text-gray-300">
                  Current progress will be cleared and the form will start from the beginning.
                </p>
                <div className="mt-6 flex flex-col sm:flex-row gap-3 sm:justify-end">
                  <button
                    onClick={() => setShowRestartConfirm(false)}
                    className="px-5 py-2.5 rounded-xl border border-gray-300 dark:border-slate-600 text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-slate-700 transition-all"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleRestartConfirm}
                    className="px-5 py-2.5 rounded-xl bg-primary text-white font-medium hover:bg-primary/95 transition-all cursor-pointer text-sm"
                  >
                    Yes, restart
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

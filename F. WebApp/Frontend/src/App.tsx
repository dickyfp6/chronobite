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
    const saved = localStorage.getItem('dss_current_page');
    return (saved as Page) || 'landing';
  });

  const [algorithm, setAlgorithm] = useState<'greedy' | 'genetic' | undefined>(() => {
    const saved = localStorage.getItem('dss_algorithm');
    return (saved as 'greedy' | 'genetic') || undefined;
  });

  const [userData, setUserData] = useState<UserInputData>(() => {
    const saved = localStorage.getItem('dss_user_data');
    return saved ? JSON.parse(saved) : {
      age: 0,
      weight: 0,
      height: 0,
      healthConditions: [],
      foodPreferences: [],
    };
  });

  // Persist state to localStorage
  useEffect(() => {
    localStorage.setItem('dss_current_page', currentPage);
  }, [currentPage]);

  useEffect(() => {
    if (algorithm) localStorage.setItem('dss_algorithm', algorithm);
    else localStorage.removeItem('dss_algorithm');
  }, [algorithm]);

  useEffect(() => {
    localStorage.setItem('dss_user_data', JSON.stringify(userData));
  }, [userData]);

  return (
    <ThemeProvider attribute="class" defaultTheme="light">
      <I18nProvider>
        <div className="min-h-screen bg-background text-foreground">
          <Navbar onHomeClick={() => setCurrentPage('landing')} />

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
        </div>
      </I18nProvider>
    </ThemeProvider>
  );
}

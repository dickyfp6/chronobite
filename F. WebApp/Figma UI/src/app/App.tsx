import { useState } from 'react';
import { ThemeProvider } from 'next-themes';
import { I18nProvider } from './contexts/I18nContext';
import { Navbar } from './components/Navbar';
import { Landing } from './pages/Landing';
import { AlgorithmSelect } from './pages/AlgorithmSelect';
import { InputWizard, UserInputData } from './pages/InputWizard';
import { Results } from './pages/Results';
import { Report } from './pages/Report';

type Page = 'landing' | 'algorithm' | 'input' | 'results' | 'report';

export default function App() {
  const [currentPage, setCurrentPage] = useState<Page>('landing');
  const [algorithm, setAlgorithm] = useState<'greedy' | 'genetic' | undefined>();
  const [userData, setUserData] = useState<UserInputData>({
    age: 0,
    weight: 0,
    height: 0,
    healthConditions: [],
    foodPreferences: [],
  });

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
                onComplete={() => setCurrentPage('results')}
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
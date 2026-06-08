import { useState, useEffect, useRef } from 'react';
import { ThemeProvider } from 'next-themes';
import { I18nProvider, useI18n } from './contexts/I18nContext';
import { Navbar } from './components/figma/Navbar';
import { motion, AnimatePresence } from 'motion/react';
import { Landing } from './pages/Landing';
import { AlgorithmSelect } from './pages/AlgorithmSelect';
import { InputWizard } from './pages/InputWizard';
import type { UserInputData } from './pages/InputWizard';
import { ProfileSummary } from './pages/ProfileSummary';
import { Results } from './pages/Results';
import { Report } from './pages/Report';
import { api } from './services/api';
import { User, FileText, UtensilsCrossed, ClipboardList, Flame, Beef, Wheat, Droplet } from 'lucide-react';

type Page = 'landing' | 'algorithm' | 'input' | 'profile' | 'results' | 'report';

function SidebarNutritionSummary({ selectedItems, analysisResult }: { selectedItems: Record<string, any>, analysisResult: any }) {
  const { t } = useI18n();
  const totalCalories = Object.values(selectedItems).reduce((sum, item) => sum + (item.calories || 0), 0);
  const totalProtein = Object.values(selectedItems).reduce((sum, item) => sum + (item.protein || 0), 0);
  const totalCarbs = Object.values(selectedItems).reduce((sum, item) => sum + (item.carbs || 0), 0);
  const totalFat = Object.values(selectedItems).reduce((sum, item) => sum + (item.fat || 0), 0);
  const targetCalories = (analysisResult?.guidelines?.nutrients?.energy_kcal?.max && analysisResult.guidelines.nutrients.energy_kcal.max !== Infinity)
    ? Math.round(analysisResult.guidelines.nutrients.energy_kcal.max)
    : (analysisResult?.energy?.tdee ? Math.round(analysisResult.energy.tdee) : 2000);

  const getRange = (macroKey: string, keyG: string, fallbackMin: number, fallbackMax: number, factor: number) => {
    const guide = analysisResult?.guidelines?.nutrients?.[keyG];
    if (guide && (guide.min !== undefined || guide.max !== undefined)) {
      return { 
        min: guide.min ?? 0, 
        max: (guide.max !== null && Number.isFinite(guide.max)) ? guide.max : Infinity 
      };
    }
    const minPct = analysisResult?.macros?.[macroKey]?.pct?.[0];
    const maxPct = analysisResult?.macros?.[macroKey]?.pct?.[1];
    if (minPct !== undefined && maxPct !== undefined) {
      return {
        min: (targetCalories * minPct / 100) / factor,
        max: (targetCalories * maxPct / 100) / factor
      };
    }
    return {
      min: (targetCalories * fallbackMin / 100) / factor,
      max: (targetCalories * fallbackMax / 100) / factor
    };
  };

  const proteinRange = getRange('protein', 'protein_g', 10, 35, 4);
  const carbsRange = getRange('carbs', 'carbohydrate_g', 45, 65, 4);
  const fatRange = getRange('fat', 'fat_g', 20, 35, 9);
  const calorieRange = getRange('energy', 'energy_kcal', 90, 110, 1);

  const targetProtein = analysisResult?.guidelines?.nutrients?.protein_g?.max || analysisResult?.macros?.protein?.gram || Math.round((targetCalories * 0.15) / 4);
  const targetCarbs = analysisResult?.guidelines?.nutrients?.carbohydrate_g?.max || analysisResult?.macros?.carbs?.gram || Math.round((targetCalories * 0.55) / 4);
  const targetFat = analysisResult?.guidelines?.nutrients?.fat_g?.max || analysisResult?.macros?.fat?.gram || Math.round((targetCalories * 0.3) / 9);

  const getMacroColor = (actual: number, range: { min: number, max: number }) => {
    if (actual < range.min) return 'bg-orange-500 dark:bg-orange-400';
    if (actual > range.max) return 'bg-[#a63a3a] dark:bg-[#c94f4f]'; // classy brick red for over limit
    return 'bg-primary dark:bg-emerald-450'; // forest green to match calorie target
  };

  return (
    <div className="hidden lg:block mt-6 pt-6 border-t border-border/80 dark:border-slate-800">
      <h3 className="font-bold text-sm text-gray-900 dark:text-white mb-4 font-serif">Ketercapaian Target</h3>
      <div className="space-y-4">
        {/* Calories */}
        <div>
          <div className="flex justify-between items-center text-xs mb-1.5">
            <span className="flex items-center gap-1.5 text-gray-600 dark:text-gray-400 font-sans">
              <Flame className="w-3.5 h-3.5 text-orange-500" />
              {t.results.dailyCalories}
            </span>
            <span className="font-bold text-gray-900 dark:text-white">{Math.round(totalCalories)} / {targetCalories}</span>
          </div>
          <div className="w-full bg-secondary dark:bg-slate-800 h-2 rounded-full overflow-hidden">
            <div className={`h-full rounded-full transition-all ${getMacroColor(totalCalories, calorieRange)}`} style={{ width: `${Math.min((totalCalories / targetCalories) * 100, 100)}%` }} />
          </div>
        </div>

        {/* Carbs */}
        <div>
          <div className="flex justify-between items-center text-[11px] mb-1">
            <span className="flex items-center gap-1.5 text-gray-600 dark:text-gray-400 font-sans">
              <Wheat className="w-3.5 h-3.5 text-blue-500 dark:text-blue-450" />
              {t.results.carbs}
            </span>
            <span className="font-bold text-gray-900 dark:text-white">{Math.round(totalCarbs)} / {Math.round(targetCarbs)}g</span>
          </div>
          <div className="w-full bg-secondary dark:bg-slate-800 h-1.5 rounded-full overflow-hidden">
            <div className={`h-full rounded-full transition-all ${getMacroColor(totalCarbs, carbsRange)}`} style={{ width: `${Math.min((totalCarbs / Math.max(targetCarbs, carbsRange.max)) * 100, 100)}%` }} />
          </div>
        </div>
        
        {/* Protein */}
        <div>
          <div className="flex justify-between items-center text-[11px] mb-1">
            <span className="flex items-center gap-1.5 text-gray-600 dark:text-gray-400 font-sans">
              <Beef className="w-3.5 h-3.5 text-amber-500 dark:text-amber-400" />
              {t.results.protein}
            </span>
            <span className="font-bold text-gray-900 dark:text-white">{Math.round(totalProtein)} / {Math.round(targetProtein)}g</span>
          </div>
          <div className="w-full bg-secondary dark:bg-slate-800 h-1.5 rounded-full overflow-hidden">
            <div className={`h-full rounded-full transition-all ${getMacroColor(totalProtein, proteinRange)}`} style={{ width: `${Math.min((totalProtein / Math.max(targetProtein, proteinRange.max)) * 100, 100)}%` }} />
          </div>
        </div>

        {/* Fat */}
        <div>
          <div className="flex justify-between items-center text-[11px] mb-1">
            <span className="flex items-center gap-1.5 text-gray-600 dark:text-gray-400 font-sans">
              <Droplet className="w-3.5 h-3.5 text-red-500 dark:text-red-400" />
              {t.results.fat}
            </span>
            <span className="font-bold text-gray-900 dark:text-white">{Math.round(totalFat)} / {Math.round(targetFat)}g</span>
          </div>
          <div className="w-full bg-secondary dark:bg-slate-800 h-1.5 rounded-full overflow-hidden">
            <div className={`h-full rounded-full transition-all ${getMacroColor(totalFat, fatRange)}`} style={{ width: `${Math.min((totalFat / Math.max(targetFat, fatRange.max)) * 100, 100)}%` }} />
          </div>
        </div>
      </div>
    </div>
  );
}

function SidebarDemographics({ userData }: { userData: UserInputData }) {
  return (
    <div className="hidden lg:block mt-6 pt-6 border-t border-border/80 dark:border-slate-800 space-y-4">
      <h3 className="font-bold text-sm text-gray-900 dark:text-white mb-4 font-serif">Demographics</h3>
      
      <div>
        <span className="text-[10px] font-bold text-primary dark:text-emerald-450 uppercase tracking-wider block mb-0.5">Gender & Age</span>
        <p className="text-sm font-bold text-gray-900 dark:text-white capitalize font-sans">
          {userData.gender === 'male' ? 'Male' : 'Female'}, {userData.age} yrs
        </p>
      </div>

      <div>
        <span className="text-[10px] font-bold text-primary dark:text-emerald-450 uppercase tracking-wider block mb-0.5">Weight & Height</span>
        <p className="text-sm font-bold text-gray-900 dark:text-white font-sans">
          {userData.weight} kg • {userData.height} cm
        </p>
      </div>

      <div>
        <span className="text-[10px] font-bold text-primary dark:text-emerald-450 uppercase tracking-wider block mb-0.5">Activity Level</span>
        <p className="text-sm font-bold text-gray-900 dark:text-white capitalize font-sans">
          {userData.activity || 'Moderate'}
        </p>
      </div>

      <div>
        <span className="text-[10px] font-bold text-primary dark:text-emerald-450 uppercase tracking-wider block mb-0.5">Food Preferences</span>
        <p className="text-sm font-bold text-gray-900 dark:text-white capitalize font-sans line-clamp-2" title={userData.foodPreferences.join(', ')}>
          {userData.foodPreferences.length > 0 ? userData.foodPreferences.join(', ') : 'All Cuisines'}
        </p>
      </div>
    </div>
  );
}

export default function App() {
  const [currentPage, setCurrentPage] = useState<Page>('landing');

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

  const [selectedItems, setSelectedItems] = useState<Record<string, any>>(() => {
    const saved = sessionStorage.getItem('dss_selected_items');
    return saved ? JSON.parse(saved) : {};
  });

  const [menuPromise, setMenuPromise] = useState<Promise<any> | null>(null);
  const [downloadPDFTrigger, setDownloadPDFTrigger] = useState<(() => void) | null>(null);

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
    setSelectedItems({});
    sessionStorage.removeItem('dss_current_page');
    sessionStorage.removeItem('dss_algorithm');
    sessionStorage.removeItem('dss_user_data');
    sessionStorage.removeItem('dss_wizard_step');
    sessionStorage.removeItem('dss_selected_items');
    sessionStorage.removeItem('dss_analysis_result_full');
    sessionStorage.removeItem('dss_analysis_guidelines');
    sessionStorage.removeItem('dss_menu_data');
    localStorage.clear();
  };

  // Reset all progress state and cache if landing page is loaded/reloaded
  useEffect(() => {
    if (currentPage === 'landing') {
      sessionStorage.removeItem('dss_wizard_step');
      sessionStorage.removeItem('dss_user_data');
      sessionStorage.removeItem('dss_algorithm');
      sessionStorage.removeItem('dss_selected_items');
      sessionStorage.removeItem('dss_current_page');
      sessionStorage.removeItem('dss_analysis_result_full');
      sessionStorage.removeItem('dss_analysis_guidelines');
      sessionStorage.removeItem('dss_menu_data');
      setAlgorithm(undefined);
      setUserData({
        age: 18,
        weight: 30,
        height: 100,
        healthConditions: [],
        foodPreferences: [],
      });
      setSelectedItems({});
    }
  }, [currentPage]);

  // Enable beforeunload confirmation for browser reload
  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (currentPage !== 'landing') {
        e.preventDefault();
        e.returnValue = '';
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, [currentPage]);

  useEffect(() => {
    if (algorithm) sessionStorage.setItem('dss_algorithm', algorithm);
    else sessionStorage.removeItem('dss_algorithm');
  }, [algorithm]);

  useEffect(() => {
    sessionStorage.setItem('dss_user_data', JSON.stringify(userData));
  }, [userData]);

  // Modern autohiding scrollbar logic
  useEffect(() => {
    let lastMouseMoveTime = 0;

    const handleScroll = (e: Event) => {
      let target = e.target as any;
      if (!target) return;
      if (target === document) {
        target = document.documentElement;
      }
      if (target.classList) {
        target.classList.add('is-scrolling');
        clearTimeout(target.__scrollTimeout);
        target.__scrollTimeout = setTimeout(() => {
          target.classList.remove('is-scrolling');
        }, 1000);
      }
    };

    const handleMouseMove = (e: MouseEvent) => {
      const now = Date.now();
      if (now - lastMouseMoveTime < 100) return; // Throttle to 100ms
      lastMouseMoveTime = now;

      let parent = e.target as any;
      while (parent && parent !== document.body && parent !== document.documentElement) {
        if (parent.classList) {
          const style = window.getComputedStyle(parent);
          const isScrollableY = (style.overflowY === 'auto' || style.overflowY === 'scroll') && parent.scrollHeight > parent.clientHeight;
          const isScrollableX = (style.overflowX === 'auto' || style.overflowX === 'scroll') && parent.scrollWidth > parent.clientWidth;
          
          if (isScrollableY || isScrollableX) {
            parent.classList.add('is-scrolling');
            clearTimeout(parent.__scrollTimeout);
            parent.__scrollTimeout = setTimeout(() => {
              parent.classList.remove('is-scrolling');
            }, 1000);
            break;
          }
        }
        parent = parent.parentElement;
      }
      
      // Also apply to html document element
      const docEl = document.documentElement;
      const docScrollableY = docEl.scrollHeight > docEl.clientHeight;
      const docScrollableX = docEl.scrollWidth > docEl.clientWidth;
      if (docScrollableY || docScrollableX) {
        docEl.classList.add('is-scrolling');
        clearTimeout((docEl as any).__scrollTimeout);
        (docEl as any).__scrollTimeout = setTimeout(() => {
          docEl.classList.remove('is-scrolling');
        }, 1000);
      }
    };

    window.addEventListener('scroll', handleScroll, true);
    window.addEventListener('mousemove', handleMouseMove, true);

    return () => {
      window.removeEventListener('scroll', handleScroll, true);
      window.removeEventListener('mousemove', handleMouseMove, true);
    };
  }, []);

  return (
    <ThemeProvider attribute="class" defaultTheme="light" forcedTheme="light">
      <I18nProvider>
        <div className="min-h-screen bg-background text-foreground">
          <Navbar 
            onHomeClick={handleHomeClick} 
            currentPage={currentPage} 
            onDownloadPDF={downloadPDFTrigger}
          />

          <main className="pt-16">


            {['profile', 'results', 'report'].includes(currentPage) ? (
              <div className="min-h-[calc(100vh-4rem)] bg-gradient-to-br from-background via-background to-secondary/30 px-4 sm:px-6 lg:px-8 pb-8 pt-0 lg:pt-8 flex items-start justify-center">
                <div className="w-full max-w-[1600px]">
                  <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
                    {/* Collapsed 4-point Sidebar */}
                    <div className="sticky top-16 lg:top-24 z-30 lg:col-span-3 flex flex-row lg:flex-col overflow-x-auto lg:overflow-x-visible scrollbar-none gap-3 lg:gap-0 -mx-4 px-4 sm:-mx-6 sm:px-6 lg:mx-0 lg:px-5 py-3 lg:py-5 bg-white/95 dark:bg-slate-900/95 lg:bg-white/50 lg:dark:bg-slate-900/40 backdrop-blur-md border-b border-border/50 lg:border lg:border-border/80 lg:dark:border-slate-800/80 rounded-none lg:rounded-3xl shadow-sm lg:shadow-lg lg:shadow-primary/5 dark:shadow-none">
                      {[
                        { id: 'input', label: 'Profil Input', summary: 'Edit measurements', icon: User },
                        { id: 'profile', label: 'Summary', summary: 'Nutrition constraints', icon: FileText },
                        { id: 'results', label: 'Meal Plan', summary: 'Recommended menus', icon: UtensilsCrossed },
                        { id: 'report', label: 'Complete Report', summary: 'Detailed analysis', icon: ClipboardList },
                      ].map((item) => {
                        const active = item.id === currentPage;
                        const Icon = item.icon;

                        return (
                          <button
                            key={item.id}
                            onClick={() => {
                              if (item.id === 'input') {
                                setMenuPromise(null);
                                setCurrentPage('input');
                              } else if (item.id === 'profile') {
                                setCurrentPage('profile');
                              } else if (item.id === 'results') {
                                setCurrentPage('results');
                              } else if (item.id === 'report') {
                                setCurrentPage('report');
                              }
                            }}
                            className={`relative flex flex-row items-center lg:items-start text-left gap-2.5 lg:gap-3 p-2 lg:p-3 rounded-xl lg:rounded-2xl transition-all min-w-max lg:min-w-0 flex-1 lg:flex-none border border-transparent ${
                              active
                                ? 'bg-primary/10 dark:bg-primary/20 text-primary dark:text-emerald-300 border-primary/25 font-bold shadow-sm'
                                : 'hover:bg-white/80 dark:hover:bg-slate-800/60 text-gray-700 dark:text-gray-300 cursor-pointer'
                            }`}
                          >
                            {/* Icon Indicator */}
                            <div
                              className={`w-8 h-8 lg:w-10 lg:h-10 rounded-full flex items-center justify-center text-xs lg:text-sm font-bold shadow-sm z-10 shrink-0 transition-all ${
                                active
                                  ? 'bg-primary text-primary-foreground ring-4 ring-primary/25 scale-105'
                                  : 'bg-secondary dark:bg-slate-800 text-muted-foreground dark:text-gray-400'
                              }`}
                            >
                              <Icon className="w-4 h-4 lg:w-5 h-5" />
                            </div>

                            <div className="flex-1 min-w-0 text-left z-10">
                              <p className={`text-xs lg:text-sm tracking-tight ${active ? 'font-bold text-primary dark:text-emerald-300' : 'font-semibold'}`}>
                                {item.label}
                              </p>
                              <p className="text-[10px] lg:text-xs text-gray-500 dark:text-gray-400 font-normal truncate max-w-[100px] lg:max-w-[200px] mt-0.5">
                                {item.summary}
                              </p>
                            </div>
                          </button>
                        );
                      })}
                      {currentPage === 'profile' && (
                        <SidebarDemographics userData={userData} />
                      )}
                      {['results', 'report'].includes(currentPage) && (
                        <SidebarNutritionSummary selectedItems={selectedItems} analysisResult={analysisResult} />
                      )}
                    </div>

                    {/* Right Content */}
                    <div className="lg:col-span-9 flex flex-col gap-6 w-full">
                      <AnimatePresence mode="wait">
                        {currentPage === 'profile' && (
                          <motion.div
                            key="profile"
                            initial={{ opacity: 0, x: 15 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -15 }}
                            transition={{ duration: 0.25, ease: 'easeInOut' }}
                            className="w-full"
                          >
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
                          </motion.div>
                        )}

                        {currentPage === 'results' && (
                          <motion.div
                            key="results"
                            initial={{ opacity: 0, x: 15 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -15 }}
                            transition={{ duration: 0.25, ease: 'easeInOut' }}
                            className="w-full"
                          >
                            <Results
                              userData={userData}
                              algorithm={algorithm}
                              analysisResult={analysisResult}
                              menuPromise={menuPromise}
                              onViewReport={() => setCurrentPage('report')}
                              selectedItems={selectedItems}
                              onSelectedItemsChange={setSelectedItems}
                            />
                          </motion.div>
                        )}

                        {currentPage === 'report' && (
                          <motion.div
                            key="report"
                            initial={{ opacity: 0, x: 15 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -15 }}
                            transition={{ duration: 0.25, ease: 'easeInOut' }}
                            className="w-full"
                          >
                            <Report 
                              userData={userData} 
                              onRegisterDownloadPDF={setDownloadPDFTrigger}
                            />
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <AnimatePresence mode="wait">
                {currentPage === 'landing' && (
                  <motion.div
                    key="landing"
                    initial={{ opacity: 0, y: 15 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -15 }}
                    transition={{ duration: 0.25, ease: 'easeInOut' }}
                    className="w-full"
                  >
                    <Landing onStart={() => {
                      sessionStorage.removeItem('dss_wizard_step');
                      sessionStorage.removeItem('dss_user_data');
                      setUserData({
                        age: 18,
                        weight: 30,
                        height: 100,
                        healthConditions: [],
                        foodPreferences: [],
                      });
                      setCurrentPage('algorithm');
                    }} />
                  </motion.div>
                )}

                {currentPage === 'algorithm' && (
                  <motion.div
                    key="algorithm"
                    initial={{ opacity: 0, y: 15 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -15 }}
                    transition={{ duration: 0.25, ease: 'easeInOut' }}
                    className="w-full"
                  >
                    <AlgorithmSelect
                      selected={algorithm}
                      onSelect={(algo) => {
                        setMenuPromise(null);
                        setAlgorithm(algo);
                      }}
                      onContinue={() => setCurrentPage('input')}
                    />
                  </motion.div>
                )}

                {currentPage === 'input' && (
                  <motion.div
                    key="input"
                    initial={{ opacity: 0, y: 15 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -15 }}
                    transition={{ duration: 0.25, ease: 'easeInOut' }}
                    className="w-full"
                  >
                    <InputWizard
                      data={userData}
                      onUpdate={(data) => {
                        setMenuPromise(null);
                        setUserData({ ...userData, ...data });
                      }}
                      onComplete={() => setCurrentPage('profile')}
                    />
                  </motion.div>
                )}
              </AnimatePresence>
            )}
          </main>

          {/* Restart Confirmation Modal */}
          {showRestartConfirm && (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm px-4">
              <div className="w-full max-w-md rounded-3xl bg-white dark:bg-slate-800 p-8 shadow-2xl border border-border/80 dark:border-slate-700">
                <h3 className="text-2xl font-bold text-foreground font-serif leading-tight">Restart application?</h3>
                <p className="mt-3 text-sm text-gray-600 dark:text-gray-300 font-sans leading-relaxed">
                  Current progress will be cleared and the form will start from the beginning.
                </p>
                <div className="mt-6 flex flex-row gap-3 justify-end">
                  <button
                    onClick={() => setShowRestartConfirm(false)}
                    className="px-6 py-2.5 rounded-2xl border border-gray-200 dark:border-slate-600 text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-slate-700 transition-all font-sans font-medium text-sm cursor-pointer"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleRestartConfirm}
                    className="px-6 py-2.5 rounded-2xl bg-primary text-white font-semibold hover:bg-primary/95 transition-all cursor-pointer text-sm shadow-sm"
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

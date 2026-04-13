import { Moon, Sun } from 'lucide-react';
import { useTheme } from 'next-themes';
import { useI18n } from '../../contexts/I18nContext';

interface NavbarProps {
  onHomeClick: () => void;
}

export function Navbar({ onHomeClick }: NavbarProps) {
  const { theme, setTheme } = useTheme();
  const { language, setLanguage } = useI18n();

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-white/90 dark:bg-slate-900/90 backdrop-blur-md border-b-2 border-emerald-200 dark:border-emerald-700 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <button
          onClick={onHomeClick}
          className="text-lg font-bold text-emerald-600 dark:text-emerald-400 hover:text-emerald-700 dark:hover:text-emerald-300 transition-all"
        >
          NutriPlan
        </button>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1 bg-emerald-100 dark:bg-slate-700 rounded-full p-1 shadow-sm">
            <button
              onClick={() => setTheme('light')}
              className={`px-3 py-1.5 rounded-full text-sm font-medium transition-all ${
                theme === 'light'
                  ? 'bg-gradient-to-r from-emerald-500 to-teal-500 text-white shadow-md'
                  : 'text-emerald-700 dark:text-emerald-400 hover:text-emerald-900 dark:hover:text-emerald-300'
              }`}
            >
              <Sun className="w-4 h-4" />
            </button>
            <button
              onClick={() => setTheme('dark')}
              className={`px-3 py-1.5 rounded-full text-sm font-medium transition-all ${
                theme === 'dark'
                  ? 'bg-gradient-to-r from-emerald-500 to-teal-500 text-white shadow-md'
                  : 'text-emerald-700 dark:text-emerald-400 hover:text-emerald-900 dark:hover:text-emerald-300'
              }`}
            >
              <Moon className="w-4 h-4" />
            </button>
          </div>

          <div className="flex items-center gap-1 bg-emerald-100 dark:bg-slate-700 rounded-full p-1 shadow-sm">
            <button
              onClick={() => setLanguage('en')}
              className={`px-3 py-1.5 rounded-full text-sm font-medium transition-all ${
                language === 'en'
                  ? 'bg-gradient-to-r from-emerald-500 to-teal-500 text-white shadow-md'
                  : 'text-emerald-700 dark:text-emerald-400 hover:text-emerald-900 dark:hover:text-emerald-300'
              }`}
            >
              EN
            </button>
            <button
              onClick={() => setLanguage('id')}
              className={`px-3 py-1.5 rounded-full text-sm font-medium transition-all ${
                language === 'id'
                  ? 'bg-gradient-to-r from-emerald-500 to-teal-500 text-white shadow-md'
                  : 'text-emerald-700 dark:text-emerald-400 hover:text-emerald-900 dark:hover:text-emerald-300'
              }`}
            >
              ID
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}

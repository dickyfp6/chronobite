import { createContext, useContext, useState } from 'react';
import type { ReactNode } from 'react';
import { translations } from '../utils/translations';

type Language = 'en';

interface I18nContextType {
  language: Language;
  setLanguage: () => void;
  t: typeof translations.en;
}

const I18nContext = createContext<I18nContextType | undefined>(undefined);

export function I18nProvider({ children }: { children: ReactNode }) {
  const [language] = useState<Language>('en');

  return (
    <I18nContext.Provider value={{ language, setLanguage: () => {}, t: translations.en }}>
      {children}
    </I18nContext.Provider>
  );
}

export function useI18n() {
  const context = useContext(I18nContext);
  if (!context) throw new Error('useI18n must be used within I18nProvider');
  return context;
}

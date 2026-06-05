import { useLanguageStore } from '@/store/language.store';
import { useTranslation } from 'react-i18next';

export function useLanguage() {
  const { currentLang, setLanguage, toggleLanguage } = useLanguageStore();
  const { i18n } = useTranslation();

  const isRTL = currentLang === 'ar';

  return {
    currentLang,
    isRTL,
    setLanguage,
    toggleLanguage,
    dir: isRTL ? 'rtl' : 'ltr',
    fontFamily: isRTL ? "'Noto Sans Arabic', 'Sora', sans-serif" : "'Sora', system-ui, sans-serif",
    // Direction-aware CSS class helpers
    flexDir: isRTL ? 'flex-row-reverse' : 'flex-row',
    textAlign: isRTL ? 'text-right' : 'text-left',
    ml: isRTL ? 'mr' : 'ml',
    mr: isRTL ? 'ml' : 'mr',
    pl: isRTL ? 'pr' : 'pl',
    pr: isRTL ? 'pl' : 'pr',
  };
}

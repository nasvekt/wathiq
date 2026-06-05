import { create } from 'zustand';
import i18n from '@/i18n';

interface LanguageState {
  currentLang: 'en' | 'ar';
  setLanguage: (lang: 'en' | 'ar') => void;
  toggleLanguage: () => void;
}

export const useLanguageStore = create<LanguageState>((set) => ({
  currentLang: (localStorage.getItem('i18nextLng') as 'en' | 'ar') || 'en',
  setLanguage: (lang) => {
    i18n.changeLanguage(lang);
    document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr';
    document.documentElement.lang = lang;
    localStorage.setItem('i18nextLng', lang);
    set({ currentLang: lang });
  },
  toggleLanguage: () => {
    set((state) => {
      const newLang = state.currentLang === 'en' ? 'ar' : 'en';
      i18n.changeLanguage(newLang);
      document.documentElement.dir = newLang === 'ar' ? 'rtl' : 'ltr';
      document.documentElement.lang = newLang;
      localStorage.setItem('i18nextLng', newLang);
      return { currentLang: newLang as 'en' | 'ar' };
    });
  },
}));

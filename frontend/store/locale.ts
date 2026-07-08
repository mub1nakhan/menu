import { create } from 'zustand'
import { normalizeLocale, type Locale } from '@/lib/i18n'

interface LocaleState {
  locale: Locale
  setLocale: (locale: Locale) => void
}

const initialLocale = normalizeLocale(typeof window !== 'undefined' ? window.localStorage.getItem('locale') : null)

export const useLocaleStore = create<LocaleState>((set) => ({
  locale: initialLocale,
  setLocale: (locale) => {
    if (typeof window !== 'undefined') {
      window.localStorage.setItem('locale', locale)
      document.documentElement.lang = locale
    }
    set({ locale })
  },
}))

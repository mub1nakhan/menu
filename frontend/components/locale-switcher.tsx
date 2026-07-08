'use client'

import { useLocaleStore } from '@/store/locale'
import { translate, type Locale } from '@/lib/i18n'

export function LocaleSwitcher() {
  const locale = useLocaleStore((state) => state.locale)
  const setLocale = useLocaleStore((state) => state.setLocale)

  return (
    <label className="flex items-center gap-2 rounded-full border border-slate-200 bg-white/80 px-3 py-2 text-sm text-slate-600 shadow-sm">
      <span className="text-xs uppercase tracking-[0.2em]">{translate('common.live', locale)}</span>
      <select
        aria-label="Select language"
        value={locale}
        onChange={(event) => setLocale(event.target.value as Locale)}
        className="bg-transparent text-sm font-medium text-slate-700 outline-none"
      >
        <option value="uz">O‘zbek</option>
        <option value="en">English</option>
      </select>
    </label>
  )
}

import { useEffect } from 'react';
import type { ReactNode } from 'react';
import i18n from '../src/i18n';

const RTL_LANGUAGES = ['ar', 'he', 'fa', 'ur'];

export function I18nWrapper({ locale, children }: { locale: string; children: ReactNode }) {
  useEffect(() => {
    i18n.changeLanguage(locale);
    document.dir = RTL_LANGUAGES.includes(locale) ? 'rtl' : 'ltr';
  }, [locale]);

  return <>{children}</>;
}

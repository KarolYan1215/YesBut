'use client';

import { useI18n } from '@/i18n';

export function LanguageSwitcher() {
  const { locale, setLocale, t } = useI18n();

  return (
    <div className="flex items-center gap-2">
      <button
        onClick={() => setLocale('en')}
        className={`px-3 py-1.5 text-sm rounded-md transition-colors ${
          locale === 'en'
            ? 'bg-primary text-white'
            : 'text-muted hover:text-foreground hover:bg-background'
        }`}
      >
        EN
      </button>
      <button
        onClick={() => setLocale('zh')}
        className={`px-3 py-1.5 text-sm rounded-md transition-colors ${
          locale === 'zh'
            ? 'bg-primary text-white'
            : 'text-muted hover:text-foreground hover:bg-background'
        }`}
      >
        中文
      </button>
    </div>
  );
}

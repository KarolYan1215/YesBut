'use client';

import { useTranslation } from '@/i18n';

export type SessionMode = 'sync' | 'async';

interface ModeSwitcherProps {
  mode: SessionMode;
  onModeChange: (mode: SessionMode) => void;
  disabled?: boolean;
}

export function ModeSwitcher({ mode, onModeChange, disabled }: ModeSwitcherProps) {
  const t = useTranslation();

  return (
    <div className="flex items-center gap-1 bg-ink-5 rounded-lg p-1">
      <button
        onClick={() => onModeChange('async')}
        disabled={disabled}
        className={`px-3 py-1 text-xs font-medium rounded transition-colors ${
          mode === 'async'
            ? 'bg-white text-ink-100 shadow-sm'
            : 'text-ink-60 hover:text-ink-80'
        } disabled:opacity-50`}
      >
        {t.sessions.async}
      </button>
      <button
        onClick={() => onModeChange('sync')}
        disabled={disabled}
        className={`px-3 py-1 text-xs font-medium rounded transition-colors ${
          mode === 'sync'
            ? 'bg-white text-ink-100 shadow-sm'
            : 'text-ink-60 hover:text-ink-80'
        } disabled:opacity-50`}
      >
        {t.sessions.sync}
      </button>
    </div>
  );
}

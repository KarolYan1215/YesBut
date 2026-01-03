'use client';

import { useState } from 'react';

type ViewMode = 'causal' | 'conflict';

interface ViewToggleProps {
  value?: ViewMode;
  onChange?: (mode: ViewMode) => void;
  className?: string;
}

export function ViewToggle({ value = 'causal', onChange, className = '' }: ViewToggleProps) {
  const [mode, setMode] = useState<ViewMode>(value);

  const handleChange = (newMode: ViewMode) => {
    setMode(newMode);
    onChange?.(newMode);
  };

  return (
    <div className={`inline-flex rounded-lg border border-border p-0.5 bg-surface ${className}`}>
      <button
        onClick={() => handleChange('causal')}
        className={`px-3 py-1 text-xs font-medium rounded-md transition-colors ${
          mode === 'causal'
            ? 'bg-primary text-white'
            : 'text-muted hover:text-foreground'
        }`}
      >
        Causal
      </button>
      <button
        onClick={() => handleChange('conflict')}
        className={`px-3 py-1 text-xs font-medium rounded-md transition-colors ${
          mode === 'conflict'
            ? 'bg-primary text-white'
            : 'text-muted hover:text-foreground'
        }`}
      >
        Conflict
      </button>
    </div>
  );
}

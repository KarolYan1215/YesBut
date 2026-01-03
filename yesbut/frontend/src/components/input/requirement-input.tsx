'use client';

import { useState } from 'react';
import { Textarea } from '../ui/textarea';

interface RequirementInputProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit?: () => void;
  placeholder?: string;
  disabled?: boolean;
}

export function RequirementInput({
  value,
  onChange,
  onSubmit,
  placeholder = 'Describe your idea or requirement...',
  disabled = false,
}: RequirementInputProps) {
  const [focused, setFocused] = useState(false);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && e.metaKey && onSubmit) {
      e.preventDefault();
      onSubmit();
    }
  };

  return (
    <div className={`relative transition-all ${focused ? 'ring-2 ring-primary rounded-lg' : ''}`}>
      <Textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onFocus={() => setFocused(true)}
        onBlur={() => setFocused(false)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        disabled={disabled}
        rows={6}
        className="text-base leading-relaxed"
      />
      <div className="absolute bottom-3 right-3 flex items-center gap-2">
        <span className="text-xs text-muted">{value.length} chars</span>
        {onSubmit && (
          <button
            onClick={onSubmit}
            disabled={disabled || !value.trim()}
            className="px-3 py-1 text-xs bg-primary text-white rounded-md hover:bg-primary-hover disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Continue
          </button>
        )}
      </div>
    </div>
  );
}

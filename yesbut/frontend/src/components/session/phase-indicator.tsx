'use client';

type Phase = 'divergence' | 'filtering' | 'convergence' | 'completed';

interface PhaseIndicatorProps {
  currentPhase: Phase;
  className?: string;
}

const phases: { key: Phase; label: string; color: string }[] = [
  { key: 'divergence', label: 'Diverge', color: 'bg-phase-diverge' },
  { key: 'filtering', label: 'Filter', color: 'bg-phase-filter' },
  { key: 'convergence', label: 'Converge', color: 'bg-phase-converge' },
];

export function PhaseIndicator({ currentPhase, className = '' }: PhaseIndicatorProps) {
  const currentIndex = currentPhase === 'completed'
    ? phases.length
    : phases.findIndex((p) => p.key === currentPhase);

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      {phases.map((phase, index) => {
        const isActive = index === currentIndex;
        const isCompleted = index < currentIndex || currentPhase === 'completed';

        return (
          <div key={phase.key} className="flex items-center gap-2">
            {index > 0 && (
              <div className={`w-6 h-px ${isCompleted ? 'bg-foreground' : 'bg-border'}`} />
            )}
            <div className="flex items-center gap-1.5">
              <div
                className={`w-2.5 h-2.5 rounded-full transition-colors ${
                  isActive || isCompleted ? phase.color : 'bg-border'
                } ${isActive ? 'ring-2 ring-offset-2 ring-offset-background' : ''}`}
              />
              <span className={`text-xs ${isActive ? 'text-foreground font-medium' : 'text-muted'}`}>
                {phase.label}
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
}

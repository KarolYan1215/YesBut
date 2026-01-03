'use client';

import { memo } from 'react';

type HeatmapMode = 'conflict' | 'confidence' | 'sensitivity';

interface GraphHeatmapProps {
  mode: HeatmapMode;
  visible: boolean;
  onModeChange: (mode: HeatmapMode) => void;
  onToggleVisibility: () => void;
}

const modeLabels: Record<HeatmapMode, string> = {
  conflict: 'Conflict Intensity',
  confidence: 'Confidence Distribution',
  sensitivity: 'Sensitivity Analysis',
};

const modeColors: Record<HeatmapMode, { low: string; high: string }> = {
  conflict: { low: 'bg-signal-warning/20', high: 'bg-signal-critical/60' },
  confidence: { low: 'bg-signal-critical/40', high: 'bg-signal-success/40' },
  sensitivity: { low: 'bg-signal-info/20', high: 'bg-node-synthesis/60' },
};

function GraphHeatmapComponent({
  mode,
  visible,
  onModeChange,
  onToggleVisibility,
}: GraphHeatmapProps): JSX.Element {
  return (
    <div className="absolute top-4 right-4 z-10">
      <div className="bg-white border border-ink-20 rounded-md shadow-sm">
        <div className="flex items-center gap-2 px-3 py-2 border-b border-ink-10">
          <button
            onClick={onToggleVisibility}
            className={`w-4 h-4 rounded border transition-colors ${
              visible ? 'bg-ink-100 border-ink-100' : 'border-ink-40'
            }`}
          >
            {visible && (
              <svg className="w-full h-full text-white" viewBox="0 0 24 24" fill="currentColor">
                <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z" />
              </svg>
            )}
          </button>
          <span className="text-xs font-medium text-ink-80">Heatmap</span>
        </div>

        {visible && (
          <div className="p-2 space-y-2">
            {(['conflict', 'confidence', 'sensitivity'] as HeatmapMode[]).map((m) => (
              <button
                key={m}
                onClick={() => onModeChange(m)}
                className={`w-full px-2 py-1.5 text-left text-xs rounded transition-colors ${
                  mode === m ? 'bg-ink-05 text-ink-100' : 'text-ink-60 hover:bg-ink-05/50'
                }`}
              >
                {modeLabels[m]}
              </button>
            ))}

            <div className="pt-2 border-t border-ink-10">
              <div className="text-[10px] text-ink-40 mb-1">Legend</div>
              <div className="flex items-center gap-1">
                <div className={`w-4 h-2 rounded-sm ${modeColors[mode].low}`} />
                <div className="flex-1 h-2 rounded-sm bg-gradient-to-r from-transparent to-transparent"
                  style={{
                    background: mode === 'conflict'
                      ? 'linear-gradient(to right, rgba(245,158,11,0.2), rgba(239,68,68,0.6))'
                      : mode === 'confidence'
                      ? 'linear-gradient(to right, rgba(239,68,68,0.4), rgba(16,185,129,0.4))'
                      : 'linear-gradient(to right, rgba(59,130,246,0.2), rgba(124,58,237,0.6))'
                  }}
                />
                <div className={`w-4 h-2 rounded-sm ${modeColors[mode].high}`} />
              </div>
              <div className="flex justify-between text-[10px] text-ink-40 mt-0.5">
                <span>Low</span>
                <span>High</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export const GraphHeatmap = memo(GraphHeatmapComponent);

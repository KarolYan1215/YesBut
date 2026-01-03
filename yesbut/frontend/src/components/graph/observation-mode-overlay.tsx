'use client';

import { memo } from 'react';

interface ObservationModeOverlayProps {
  visible: boolean;
  agentName: string;
  agentType: string;
  onGlobalInterrupt: () => void;
  isInterrupting: boolean;
}

const agentTypeColors: Record<string, string> = {
  GEN: 'bg-signal-info',
  RPA: 'bg-node-goal',
  ISA: 'bg-node-fact',
  ACA: 'bg-signal-warning',
  BM: 'bg-node-claim',
  GA: 'bg-node-synthesis',
  UOA: 'bg-node-constraint',
  REC: 'bg-ink-60',
};

function ObservationModeOverlayComponent({
  visible,
  agentName,
  agentType,
  onGlobalInterrupt,
  isInterrupting,
}: ObservationModeOverlayProps): JSX.Element | null {
  if (!visible) return null;

  return (
    <div className="absolute inset-0 bg-ink-100/20 backdrop-blur-[1px] flex items-center justify-center z-50">
      <div className="bg-white border border-ink-20 rounded-md shadow-lg max-w-sm w-full mx-4">
        <div className="px-4 py-3 border-b border-ink-10">
          <div className="flex items-center gap-2">
            <svg className="w-5 h-5 text-ink-60" viewBox="0 0 24 24" fill="currentColor">
              <path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm3.1-9H8.9V6c0-1.71 1.39-3.1 3.1-3.1 1.71 0 3.1 1.39 3.1 3.1v2z" />
            </svg>
            <span className="text-sm font-medium text-ink-100">Branch Locked</span>
          </div>
        </div>

        <div className="p-4 space-y-3">
          <div className="flex items-center gap-2">
            <div className={`w-2 h-6 rounded-full ${agentTypeColors[agentType] || 'bg-ink-40'}`} />
            <div>
              <div className="text-sm font-medium text-ink-80">{agentName}</div>
              <div className="text-xs text-ink-40">{agentType} is working...</div>
            </div>
          </div>

          <div className="text-xs text-ink-60 space-y-1">
            <p>You can:</p>
            <ul className="list-disc list-inside space-y-0.5 text-ink-40">
              <li>View and navigate the graph</li>
              <li>Read node details</li>
              <li>Queue chat messages</li>
            </ul>
          </div>
        </div>

        <div className="px-4 py-3 border-t border-ink-10">
          <button
            onClick={onGlobalInterrupt}
            disabled={isInterrupting}
            className={`w-full px-4 py-2 text-sm font-medium rounded transition-colors ${
              isInterrupting
                ? 'bg-ink-10 text-ink-40 cursor-not-allowed'
                : 'bg-signal-critical text-white hover:bg-signal-critical/90'
            }`}
          >
            {isInterrupting ? 'Interrupting...' : 'Global Interrupt'}
          </button>
          <p className="text-[10px] text-ink-40 text-center mt-2">
            This will pause all agent activity
          </p>
        </div>
      </div>
    </div>
  );
}

export const ObservationModeOverlay = memo(ObservationModeOverlayComponent);

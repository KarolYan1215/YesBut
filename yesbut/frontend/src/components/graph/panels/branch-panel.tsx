'use client';

import { memo } from 'react';

type BranchStatus = 'active' | 'paused' | 'completed' | 'pruned';

interface BranchInfo {
  id: string;
  name: string;
  status: BranchStatus;
  nodeCount: number;
  utilityScore: number;
  agentId: string;
  isLocked: boolean;
  lockingAgent?: string;
}

interface BranchPanelProps {
  branches: BranchInfo[];
  selectedBranchId: string | null;
  onSelectBranch: (branchId: string) => void;
  onForkBranch: (nodeId: string) => void;
  onMergeBranches: (branchId1: string, branchId2: string) => void;
  onPruneBranch: (branchId: string) => void;
  isOpen: boolean;
  onClose: () => void;
}

const statusColors: Record<BranchStatus, string> = {
  active: 'bg-signal-success',
  paused: 'bg-signal-warning',
  completed: 'bg-signal-info',
  pruned: 'bg-ink-40',
};

function BranchPanelComponent({
  branches,
  selectedBranchId,
  onSelectBranch,
  onPruneBranch,
  isOpen,
  onClose,
}: BranchPanelProps): JSX.Element | null {
  if (!isOpen) return null;

  return (
    <div className="w-60 bg-white border-r border-ink-20 h-full flex flex-col">
      <div className="flex items-center justify-between px-4 py-3 border-b border-ink-10">
        <span className="text-sm font-medium text-ink-100">Branches</span>
        <button onClick={onClose} className="text-ink-40 hover:text-ink-80 transition-colors">
          <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
            <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z" />
          </svg>
        </button>
      </div>

      <div className="flex-1 overflow-y-auto">
        {branches.map((branch) => (
          <div
            key={branch.id}
            onClick={() => onSelectBranch(branch.id)}
            className={`px-4 py-3 border-b border-ink-05 cursor-pointer transition-colors ${
              selectedBranchId === branch.id ? 'bg-ink-05' : 'hover:bg-ink-05/50'
            }`}
          >
            <div className="flex items-center justify-between mb-1">
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${statusColors[branch.status]}`} />
                <span className="text-sm font-medium text-ink-80">{branch.name}</span>
              </div>
              {branch.isLocked && (
                <svg className="w-3 h-3 text-ink-40" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2z" />
                </svg>
              )}
            </div>
            <div className="flex items-center justify-between text-xs text-ink-40">
              <span>{branch.nodeCount} nodes</span>
              <span className="font-mono">{(branch.utilityScore * 100).toFixed(0)}%</span>
            </div>
            {branch.status !== 'pruned' && (
              <div className="mt-2 flex gap-1">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onPruneBranch(branch.id);
                  }}
                  className="text-[10px] px-1.5 py-0.5 text-ink-40 hover:text-signal-critical transition-colors"
                >
                  Prune
                </button>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export const BranchPanel = memo(BranchPanelComponent);

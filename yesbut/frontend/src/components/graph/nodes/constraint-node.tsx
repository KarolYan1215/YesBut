'use client';

import { memo } from 'react';
import type { NodeProps } from 'reactflow';
import { BaseNode, MetricsBar } from './base-node';

interface ConstraintNodeData {
  label: string;
  description?: string;
  constraintType?: 'hard' | 'soft';
  weight?: number;
  isSatisfied?: boolean;
  confidence: number;
  selected?: boolean;
  isPreview?: boolean;
  version?: number;
}

function ConstraintNodeComponent({ data, selected }: NodeProps<ConstraintNodeData>): JSX.Element {
  const isHard = data.constraintType === 'hard';
  return (
    <BaseNode
      nodeType="constraint"
      indicatorColor="var(--node-constraint)"
      data={data}
      selected={selected}
    >
      <div className="min-w-[160px] max-w-[260px]">
        <div className="flex items-center gap-1.5 mb-1">
          <svg className="w-3.5 h-3.5 text-[var(--node-constraint)]" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z" />
          </svg>
          <span className="text-xs font-mono text-ink-40 uppercase">
            {isHard ? 'Hard' : 'Soft'} Constraint
          </span>
          {data.isSatisfied !== undefined && (
            <span className={`w-2 h-2 rounded-full ${data.isSatisfied ? 'bg-signal-success' : 'bg-signal-error'}`} />
          )}
        </div>
        <p className="text-sm text-ink-80 leading-tight">{data.label}</p>
        {data.weight !== undefined && !isHard && (
          <div className="text-[10px] text-ink-40 mt-1">Weight: {(data.weight * 100).toFixed(0)}%</div>
        )}
        <MetricsBar confidence={data.confidence} />
      </div>
    </BaseNode>
  );
}

export const ConstraintNode = memo(ConstraintNodeComponent);

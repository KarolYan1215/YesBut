'use client';

import { memo } from 'react';
import type { NodeProps } from 'reactflow';
import { BaseNode, MetricsBar } from './base-node';

interface GoalNodeData {
  label: string;
  description?: string;
  confidence: number;
  selected?: boolean;
  isPreview?: boolean;
  version?: number;
}

function GoalNodeComponent({ data, selected }: NodeProps<GoalNodeData>): JSX.Element {
  return (
    <BaseNode
      nodeType="goal"
      indicatorColor="var(--node-goal)"
      data={data}
      selected={selected}
    >
      <div className="min-w-[180px] max-w-[280px]">
        <div className="flex items-center gap-1.5 mb-1">
          <svg className="w-4 h-4 text-[var(--node-goal)]" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" />
          </svg>
          <span className="text-xs font-mono text-ink-40 uppercase">Goal</span>
        </div>
        <p className="text-sm font-medium text-ink-100 leading-tight">{data.label}</p>
        {data.description && (
          <p className="text-xs text-ink-60 mt-1 line-clamp-2">{data.description}</p>
        )}
        <MetricsBar confidence={data.confidence} />
      </div>
    </BaseNode>
  );
}

export const GoalNode = memo(GoalNodeComponent);

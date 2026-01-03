'use client';

import { memo } from 'react';
import type { NodeProps } from 'reactflow';
import { BaseNode, MetricsBar } from './base-node';

interface ClaimNodeData {
  label: string;
  reasoning?: string;
  confidence: number;
  validity?: number;
  utility?: number;
  novelty?: number;
  agentType?: string;
  selected?: boolean;
  isPreview?: boolean;
  version?: number;
}

function ClaimNodeComponent({ data, selected }: NodeProps<ClaimNodeData>): JSX.Element {
  return (
    <BaseNode
      nodeType="claim"
      indicatorColor="var(--node-claim)"
      data={data}
      selected={selected}
    >
      <div className="min-w-[160px] max-w-[260px]">
        <div className="flex items-center gap-1.5 mb-1">
          <svg className="w-3.5 h-3.5 text-[var(--node-claim)]" viewBox="0 0 24 24" fill="currentColor">
            <path d="M9 21c0 .55.45 1 1 1h4c.55 0 1-.45 1-1v-1H9v1zm3-19C8.14 2 5 5.14 5 9c0 2.38 1.19 4.47 3 5.74V17c0 .55.45 1 1 1h6c.55 0 1-.45 1-1v-2.26c1.81-1.27 3-3.36 3-5.74 0-3.86-3.14-7-7-7z" />
          </svg>
          <span className="text-xs font-mono text-ink-40 uppercase">Claim</span>
          {data.agentType && (
            <span className="text-[10px] font-mono bg-ink-10 text-ink-60 px-1 rounded">{data.agentType}</span>
          )}
        </div>
        <p className="text-sm text-ink-80 leading-tight">{data.label}</p>
        <MetricsBar
          confidence={data.confidence}
          validity={data.validity}
          utility={data.utility}
          novelty={data.novelty}
        />
      </div>
    </BaseNode>
  );
}

export const ClaimNode = memo(ClaimNodeComponent);

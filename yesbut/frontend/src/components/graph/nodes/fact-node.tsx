'use client';

import { memo } from 'react';
import type { NodeProps } from 'reactflow';
import { BaseNode, MetricsBar } from './base-node';

interface FactNodeData {
  label: string;
  content?: string;
  confidence: number;
  sourceCount?: number;
  crossValidated?: boolean;
  selected?: boolean;
  isPreview?: boolean;
  version?: number;
}

function FactNodeComponent({ data, selected }: NodeProps<FactNodeData>): JSX.Element {
  return (
    <BaseNode
      nodeType="fact"
      indicatorColor="var(--node-fact)"
      data={data}
      selected={selected}
    >
      <div className="min-w-[160px] max-w-[260px]">
        <div className="flex items-center gap-1.5 mb-1">
          <svg className="w-3.5 h-3.5 text-[var(--node-fact)]" viewBox="0 0 24 24" fill="currentColor">
            <path d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6zm-1 7V3.5L18.5 9H13z" />
          </svg>
          <span className="text-xs font-mono text-ink-40 uppercase">Fact</span>
          {data.crossValidated && (
            <svg className="w-3 h-3 text-signal-success" viewBox="0 0 24 24" fill="currentColor">
              <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z" />
            </svg>
          )}
          {data.sourceCount && data.sourceCount > 1 && (
            <span className="text-[10px] font-mono bg-ink-10 text-ink-60 px-1 rounded">{data.sourceCount} sources</span>
          )}
        </div>
        <p className="text-sm text-ink-80 leading-tight">{data.label}</p>
        <MetricsBar confidence={data.confidence} />
      </div>
    </BaseNode>
  );
}

export const FactNode = memo(FactNodeComponent);

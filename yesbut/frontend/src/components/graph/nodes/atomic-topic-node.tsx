'use client';

import { memo } from 'react';
import type { NodeProps } from 'reactflow';
import { BaseNode, MetricsBar } from './base-node';

interface AtomicTopicNodeData {
  label: string;
  description?: string;
  importanceWeight?: number;
  confidence: number;
  isExplored?: boolean;
  supportingFactCount?: number;
  selected?: boolean;
  isPreview?: boolean;
  version?: number;
}

function AtomicTopicNodeComponent({ data, selected }: NodeProps<AtomicTopicNodeData>): JSX.Element {
  return (
    <BaseNode
      nodeType="atomic"
      indicatorColor="var(--node-atomic)"
      data={data}
      selected={selected}
    >
      <div className="min-w-[140px] max-w-[220px]">
        <div className="flex items-center gap-1.5 mb-1">
          <svg className="w-3.5 h-3.5 text-[var(--node-atomic)]" viewBox="0 0 24 24" fill="currentColor">
            <circle cx="12" cy="12" r="3" />
            <ellipse cx="12" cy="12" rx="10" ry="4" fill="none" stroke="currentColor" strokeWidth="1.5" />
            <ellipse cx="12" cy="12" rx="10" ry="4" fill="none" stroke="currentColor" strokeWidth="1.5" transform="rotate(60 12 12)" />
            <ellipse cx="12" cy="12" rx="10" ry="4" fill="none" stroke="currentColor" strokeWidth="1.5" transform="rotate(120 12 12)" />
          </svg>
          <span className="text-xs font-mono text-ink-40 uppercase">Atomic</span>
          {data.isExplored && (
            <svg className="w-3 h-3 text-signal-success" viewBox="0 0 24 24" fill="currentColor">
              <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z" />
            </svg>
          )}
        </div>
        <p className="text-sm text-ink-80 leading-tight">{data.label}</p>
        {data.supportingFactCount !== undefined && data.supportingFactCount > 0 && (
          <div className="text-[10px] text-ink-40 mt-1">{data.supportingFactCount} facts</div>
        )}
        <MetricsBar confidence={data.confidence} />
      </div>
    </BaseNode>
  );
}

export const AtomicTopicNode = memo(AtomicTopicNodeComponent);

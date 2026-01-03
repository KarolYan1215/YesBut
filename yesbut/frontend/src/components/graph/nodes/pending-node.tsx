'use client';

import { memo } from 'react';
import type { NodeProps } from 'reactflow';
import { BaseNode } from './base-node';

interface PendingNodeData {
  label: string;
  description?: string;
  expectedType?: string;
  priority?: number;
  confidence: number;
  selected?: boolean;
  isPreview?: boolean;
  version?: number;
}

function PendingNodeComponent({ data, selected }: NodeProps<PendingNodeData>): JSX.Element {
  return (
    <BaseNode
      nodeType="pending"
      indicatorColor="var(--node-pending)"
      data={data}
      selected={selected}
    >
      <div className="min-w-[140px] max-w-[220px] border border-dashed border-ink-20 rounded p-1 -m-1">
        <div className="flex items-center gap-1.5 mb-1">
          <svg className="w-3.5 h-3.5 text-[var(--node-pending)] animate-pulse" viewBox="0 0 24 24" fill="currentColor">
            <path d="M6 2v6h.01L6 8.01 10 12l-4 4 .01.01H6V22h12v-5.99h-.01L18 16l-4-4 4-3.99-.01-.01H18V2H6z" />
          </svg>
          <span className="text-xs font-mono text-ink-40 uppercase">Pending</span>
          {data.expectedType && (
            <span className="text-[10px] font-mono bg-ink-10 text-ink-60 px-1 rounded">{data.expectedType}</span>
          )}
        </div>
        <p className="text-sm text-ink-60 leading-tight italic">{data.label}</p>
        {data.priority !== undefined && data.priority > 0 && (
          <div className="text-[10px] text-ink-40 mt-1">Priority: {data.priority}</div>
        )}
      </div>
    </BaseNode>
  );
}

export const PendingNode = memo(PendingNodeComponent);

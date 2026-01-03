'use client';

import { memo } from 'react';
import type { NodeProps } from 'reactflow';
import { BaseNode, MetricsBar } from './base-node';

interface SynthesisNodeData {
  label: string;
  reasoning?: string;
  resolutionMethod?: 'integration' | 'compromise' | 'transcendence';
  confidence: number;
  selected?: boolean;
  isPreview?: boolean;
  version?: number;
}

function SynthesisNodeComponent({ data, selected }: NodeProps<SynthesisNodeData>): JSX.Element {
  return (
    <BaseNode
      nodeType="synthesis"
      indicatorColor="var(--node-synthesis)"
      data={data}
      selected={selected}
    >
      <div className="min-w-[160px] max-w-[260px]">
        <div className="flex items-center gap-1.5 mb-1">
          <svg className="w-3.5 h-3.5 text-[var(--node-synthesis)]" viewBox="0 0 24 24" fill="currentColor">
            <path d="M17 20.41L18.41 19 15 15.59 13.59 17 17 20.41zM7.5 8H11v5.59L5.59 19 7 20.41l6-6V8h3.5L12 3.5 7.5 8z" />
          </svg>
          <span className="text-xs font-mono text-ink-40 uppercase">Synthesis</span>
          {data.resolutionMethod && (
            <span className="text-[10px] font-mono bg-ink-10 text-ink-60 px-1 rounded capitalize">{data.resolutionMethod}</span>
          )}
        </div>
        <p className="text-sm text-ink-80 leading-tight">{data.label}</p>
        <MetricsBar confidence={data.confidence} />
      </div>
    </BaseNode>
  );
}

export const SynthesisNode = memo(SynthesisNodeComponent);

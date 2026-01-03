'use client';

import { memo } from 'react';
import type { NodeProps } from 'reactflow';
import { BaseNode } from './base-node';

interface PreviewNodeData {
  label: string;
  targetType?: string;
  agentType?: string;
  progress?: number;
  isTyping?: boolean;
  partialReasoning?: string;
  confidence: number;
  selected?: boolean;
  isPreview?: boolean;
}

function PreviewNodeComponent({ data, selected }: NodeProps<PreviewNodeData>): JSX.Element {
  const progress = data.progress ?? 0;
  return (
    <BaseNode
      nodeType="preview"
      indicatorColor="var(--node-preview)"
      data={{ ...data, isPreview: true }}
      selected={selected}
    >
      <div className="min-w-[160px] max-w-[260px] opacity-70">
        <div className="flex items-center gap-1.5 mb-1">
          {data.isTyping && (
            <span className="flex gap-0.5">
              <span className="w-1.5 h-1.5 bg-ink-40 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
              <span className="w-1.5 h-1.5 bg-ink-40 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
              <span className="w-1.5 h-1.5 bg-ink-40 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
            </span>
          )}
          <span className="text-xs font-mono text-ink-40 uppercase">Preview</span>
          {data.agentType && (
            <span className="text-[10px] font-mono bg-ink-10 text-ink-60 px-1 rounded">{data.agentType}</span>
          )}
        </div>
        <p className="text-sm text-ink-60 leading-tight">{data.label || '...'}</p>
        {progress > 0 && (
          <div className="mt-1.5 h-1 bg-ink-10 rounded-full overflow-hidden">
            <div
              className="h-full bg-ink-40 transition-all duration-300"
              style={{ width: `${progress * 100}%` }}
            />
          </div>
        )}
      </div>
    </BaseNode>
  );
}

export const PreviewNode = memo(PreviewNodeComponent);

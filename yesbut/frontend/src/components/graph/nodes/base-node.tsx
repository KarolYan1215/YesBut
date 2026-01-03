/**
 * Base Node Component
 *
 * Base wrapper component for all custom node types in the graph.
 * Provides common styling, selection state, and interaction handlers.
 *
 * @module components/graph/nodes/base-node
 */

'use client';

import { memo, type ReactNode } from 'react';
import { Handle, Position, type NodeProps } from 'reactflow';

interface BaseNodeData {
  label: string;
  confidence: number;
  selected?: boolean;
  isPreview?: boolean;
  version?: number;
}

interface BaseNodeProps {
  nodeType: string;
  indicatorColor: string;
  children: ReactNode;
  data: BaseNodeData;
  selected?: boolean;
}

function BaseNodeComponent({
  nodeType,
  indicatorColor,
  children,
  data,
  selected,
}: BaseNodeProps): JSX.Element {
  const isPreview = data.isPreview ?? false;
  const isSelected = selected ?? data.selected ?? false;

  return (
    <div
      className={`
        graph-node relative
        ${isSelected ? 'graph-node-selected' : ''}
        ${isPreview ? 'graph-node-preview' : ''}
      `}
      data-node-type={nodeType}
    >
      {/* Color indicator bar */}
      <div
        className="graph-node-indicator"
        style={{ backgroundColor: indicatorColor }}
      />

      {/* Target handle (top) */}
      <Handle
        type="target"
        position={Position.Top}
        className="!w-2 !h-2 !bg-ink-40 !border-ink-20"
      />

      {/* Node content */}
      <div className="pl-2">{children}</div>

      {/* Source handle (bottom) */}
      <Handle
        type="source"
        position={Position.Bottom}
        className="!w-2 !h-2 !bg-ink-40 !border-ink-20"
      />
    </div>
  );
}

export const BaseNode = memo(BaseNodeComponent);

interface MetricsBarProps {
  confidence?: number;
  utility?: number;
  novelty?: number;
  validity?: number;
}

export function MetricsBar({
  confidence,
  utility,
  novelty,
  validity,
}: MetricsBarProps): JSX.Element {
  return (
    <div className="metrics-bar">
      {confidence !== undefined && (
        <span className="metric-badge">
          <span className="text-ink-40">C:</span>
          <span>{(confidence * 100).toFixed(0)}%</span>
        </span>
      )}
      {utility !== undefined && (
        <span className="metric-badge">
          <span className="text-ink-40">U:</span>
          <span>{(utility * 100).toFixed(0)}%</span>
        </span>
      )}
      {novelty !== undefined && (
        <span className="metric-badge">
          <span className="text-ink-40">N:</span>
          <span>{(novelty * 100).toFixed(0)}%</span>
        </span>
      )}
      {validity !== undefined && (
        <span className="metric-badge">
          <span className="text-ink-40">V:</span>
          <span>{(validity * 100).toFixed(0)}%</span>
        </span>
      )}
    </div>
  );
}

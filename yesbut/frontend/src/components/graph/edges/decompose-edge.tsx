'use client';

import { memo } from 'react';
import { getBezierPath, type EdgeProps } from 'reactflow';
import type { BaseEdgeData } from './base-edge';

interface DecomposeEdgeData extends BaseEdgeData {
  agentId?: string;
}

function DecomposeEdgeComponent({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  data,
  selected,
  markerEnd,
}: EdgeProps<DecomposeEdgeData>): JSX.Element {
  const [edgePath] = getBezierPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
  });

  const weight = data?.weight ?? 1;
  const isPreview = data?.isPreview ?? false;
  const opacity = 0.4 + weight * 0.4;
  const strokeWidth = 1 + (selected ? 0.5 : 0);

  return (
    <path
      id={id}
      d={edgePath}
      fill="none"
      stroke="var(--ink-40)"
      strokeWidth={strokeWidth}
      strokeDasharray={isPreview ? '4 4' : undefined}
      opacity={opacity}
      markerEnd={markerEnd}
      className="transition-all duration-150"
    />
  );
}

export const DecomposeEdge = memo(DecomposeEdgeComponent);

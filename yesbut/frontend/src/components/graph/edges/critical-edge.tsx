'use client';

import { memo } from 'react';
import { getBezierPath, EdgeLabelRenderer, type EdgeProps } from 'reactflow';
import type { BaseEdgeData } from './base-edge';

type PathCriticality = 'critical' | 'redundant' | 'normal';

interface CriticalEdgeData extends BaseEdgeData {
  criticality?: PathCriticality;
  criticalityScore?: number;
  isMinimalCutSet?: boolean;
  sourceConfidence?: number;
}

function CriticalEdgeComponent({
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
}: EdgeProps<CriticalEdgeData>): JSX.Element {
  const [edgePath, labelX, labelY] = getBezierPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
  });

  const criticality = data?.criticality ?? 'normal';
  const criticalityScore = data?.criticalityScore ?? 0.5;
  const isMinimalCutSet = data?.isMinimalCutSet ?? false;
  const sourceConfidence = data?.sourceConfidence ?? 1;
  const isPreview = data?.isPreview ?? false;

  const strokeWidth = 1 + criticalityScore * 3 + (selected ? 0.5 : 0);

  let strokeColor = 'var(--ink-60)';
  let dashArray: string | undefined;

  if (criticality === 'critical') {
    strokeColor = sourceConfidence < 0.6 ? 'var(--signal-critical)' : 'var(--ink-100)';
  } else if (criticality === 'redundant') {
    strokeColor = 'var(--signal-success)';
    dashArray = '4 2';
  }

  if (isPreview) {
    dashArray = '5 5';
  }

  return (
    <>
      <path
        id={id}
        d={edgePath}
        fill="none"
        stroke={strokeColor}
        strokeWidth={strokeWidth}
        strokeDasharray={dashArray}
        opacity={0.8}
        markerEnd={markerEnd}
        className="transition-all duration-150"
      />
      {isMinimalCutSet && (
        <EdgeLabelRenderer>
          <div
            style={{
              position: 'absolute',
              transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px)`,
              pointerEvents: 'none',
            }}
            className="text-signal-warning"
          >
            <svg className="w-3 h-3" viewBox="0 0 24 24" fill="currentColor">
              <path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z" />
            </svg>
          </div>
        </EdgeLabelRenderer>
      )}
    </>
  );
}

export const CriticalEdge = memo(CriticalEdgeComponent);

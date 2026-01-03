'use client';

import { memo } from 'react';
import { getBezierPath, EdgeLabelRenderer, type EdgeProps } from 'reactflow';
import type { BaseEdgeData } from './base-edge';

interface ConflictEdgeData extends BaseEdgeData {
  agentId?: string;
  resolved?: boolean;
  resolutionNodeId?: string;
}

function ConflictEdgeComponent({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  data,
  selected,
}: EdgeProps<ConflictEdgeData>): JSX.Element {
  const [edgePath, labelX, labelY] = getBezierPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
  });

  const isPreview = data?.isPreview ?? false;
  const resolved = data?.resolved ?? false;
  const strokeWidth = 2 + (selected ? 0.5 : 0);

  return (
    <>
      <path
        id={id}
        d={edgePath}
        fill="none"
        stroke="var(--signal-warning)"
        strokeWidth={strokeWidth}
        strokeDasharray="6 4"
        opacity={resolved ? 0.4 : 0.8}
        className={`transition-all duration-150 ${!resolved && !isPreview ? 'animate-pulse' : ''}`}
      />
      <EdgeLabelRenderer>
        <div
          style={{
            position: 'absolute',
            transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px)`,
            pointerEvents: 'none',
          }}
          className={`${resolved ? 'text-ink-40' : 'text-signal-warning'}`}
        >
          <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
            <path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z" />
          </svg>
        </div>
      </EdgeLabelRenderer>
    </>
  );
}

export const ConflictEdge = memo(ConflictEdgeComponent);

'use client';

import { memo } from 'react';
import { getBezierPath, EdgeLabelRenderer, type EdgeProps } from 'reactflow';
import type { BaseEdgeData } from './base-edge';

interface AttackEdgeData extends BaseEdgeData {
  agentId?: string;
  validated?: boolean;
}

function AttackEdgeComponent({
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
}: EdgeProps<AttackEdgeData>): JSX.Element {
  const [edgePath, labelX, labelY] = getBezierPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
  });

  const weight = data?.weight ?? 1;
  const isPreview = data?.isPreview ?? false;
  const validated = data?.validated ?? false;
  const opacity = 0.5 + weight * 0.5;
  const strokeWidth = 2 + weight * 1 + (selected ? 0.5 : 0);

  return (
    <>
      <path
        id={id}
        d={edgePath}
        fill="none"
        stroke="var(--signal-critical)"
        strokeWidth={strokeWidth}
        strokeDasharray={isPreview ? '5 5' : undefined}
        opacity={opacity}
        markerEnd={markerEnd}
        className="transition-all duration-150"
      />
      <EdgeLabelRenderer>
        <div
          style={{
            position: 'absolute',
            transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px)`,
            pointerEvents: 'none',
          }}
          className={`${validated ? 'text-signal-critical' : 'text-signal-warning'}`}
        >
          <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="currentColor">
            <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z" />
          </svg>
        </div>
      </EdgeLabelRenderer>
    </>
  );
}

export const AttackEdge = memo(AttackEdgeComponent);

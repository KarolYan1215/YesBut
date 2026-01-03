'use client';

import { memo } from 'react';
import { getBezierPath, EdgeLabelRenderer, type EdgeProps } from 'reactflow';
import type { BaseEdgeData } from './base-edge';

interface SupportEdgeData extends BaseEdgeData {
  agentId?: string;
}

function SupportEdgeComponent({
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
}: EdgeProps<SupportEdgeData>): JSX.Element {
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
  const opacity = 0.5 + weight * 0.5;
  const strokeWidth = 1.5 + weight * 1 + (selected ? 0.5 : 0);

  return (
    <>
      <path
        id={id}
        d={edgePath}
        fill="none"
        stroke="var(--signal-success)"
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
          className="text-signal-success"
        >
          <svg className="w-3 h-3" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 4l-1.41 1.41L16.17 11H4v2h12.17l-5.58 5.59L12 20l8-8z" />
          </svg>
        </div>
      </EdgeLabelRenderer>
    </>
  );
}

export const SupportEdge = memo(SupportEdgeComponent);

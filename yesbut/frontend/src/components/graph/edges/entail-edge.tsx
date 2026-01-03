'use client';

import { memo } from 'react';
import { getBezierPath, EdgeLabelRenderer, type EdgeProps } from 'reactflow';
import type { BaseEdgeData } from './base-edge';

interface EntailEdgeData extends BaseEdgeData {
  agentId?: string;
}

function EntailEdgeComponent({
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
}: EdgeProps<EntailEdgeData>): JSX.Element {
  const [edgePath, labelX, labelY] = getBezierPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
  });

  const isPreview = data?.isPreview ?? false;
  const strokeWidth = 1 + (selected ? 0.5 : 0);

  return (
    <>
      <path
        id={id}
        d={edgePath}
        fill="none"
        stroke="var(--signal-info)"
        strokeWidth={strokeWidth}
        strokeDasharray={isPreview ? '4 4' : undefined}
        opacity={0.8}
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
          className="text-signal-info text-[10px] font-mono"
        >
          =&gt;
        </div>
      </EdgeLabelRenderer>
    </>
  );
}

export const EntailEdge = memo(EntailEdgeComponent);

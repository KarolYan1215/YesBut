'use client';

import { memo } from 'react';
import { BaseEdge as RFBaseEdge, EdgeLabelRenderer, getBezierPath, type EdgeProps } from 'reactflow';

export interface BaseEdgeData {
  weight: number;
  selected?: boolean;
  isPreview?: boolean;
  label?: string;
  explanation?: string;
}

interface CustomEdgeProps extends EdgeProps<BaseEdgeData> {
  edgeType: string;
  strokeColor: string;
  strokeWidth?: number;
  strokeDasharray?: string;
  animated?: boolean;
  markerEnd?: string;
}

function BaseEdgeComponent({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  data,
  selected,
  edgeType,
  strokeColor,
  strokeWidth = 1.5,
  strokeDasharray,
  animated = false,
  markerEnd,
}: CustomEdgeProps): JSX.Element {
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
  const opacity = 0.4 + weight * 0.6;
  const finalWidth = strokeWidth + (selected ? 1 : 0);
  const finalDasharray = isPreview ? '5 5' : strokeDasharray;

  return (
    <>
      <RFBaseEdge
        id={id}
        path={edgePath}
        style={{
          stroke: strokeColor,
          strokeWidth: finalWidth,
          strokeDasharray: finalDasharray,
          opacity,
          transition: 'stroke-width 150ms, opacity 150ms',
        }}
        markerEnd={markerEnd}
      />
      {data?.label && (
        <EdgeLabelRenderer>
          <div
            style={{
              position: 'absolute',
              transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px)`,
              pointerEvents: 'all',
            }}
            className="text-[10px] font-mono bg-white px-1 py-0.5 rounded border border-ink-10 text-ink-60"
          >
            {data.label}
          </div>
        </EdgeLabelRenderer>
      )}
    </>
  );
}

export const BaseEdge = memo(BaseEdgeComponent);
export type { CustomEdgeProps };

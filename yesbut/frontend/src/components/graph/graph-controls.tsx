'use client';

import { memo } from 'react';

interface GraphControlsProps {
  onZoomIn: () => void;
  onZoomOut: () => void;
  onFitView: () => void;
  onReset: () => void;
  zoomLevel: number;
}

function GraphControlsComponent({
  onZoomIn,
  onZoomOut,
  onFitView,
  onReset,
  zoomLevel,
}: GraphControlsProps): JSX.Element {
  return (
    <div className="absolute bottom-4 left-4 flex flex-col gap-1 bg-white border border-ink-20 rounded-md shadow-sm">
      <button
        onClick={onZoomIn}
        className="p-2 text-ink-60 hover:text-ink-100 hover:bg-ink-05 transition-colors"
        title="Zoom In"
      >
        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
          <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z" />
        </svg>
      </button>
      <div className="px-2 py-1 text-[10px] font-mono text-ink-40 text-center border-y border-ink-10">
        {(zoomLevel * 100).toFixed(0)}%
      </div>
      <button
        onClick={onZoomOut}
        className="p-2 text-ink-60 hover:text-ink-100 hover:bg-ink-05 transition-colors"
        title="Zoom Out"
      >
        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
          <path d="M19 13H5v-2h14v2z" />
        </svg>
      </button>
      <div className="border-t border-ink-10" />
      <button
        onClick={onFitView}
        className="p-2 text-ink-60 hover:text-ink-100 hover:bg-ink-05 transition-colors"
        title="Fit View"
      >
        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
          <path d="M3 5v4h2V5h4V3H5c-1.1 0-2 .9-2 2zm2 10H3v4c0 1.1.9 2 2 2h4v-2H5v-4zm14 4h-4v2h4c1.1 0 2-.9 2-2v-4h-2v4zm0-16h-4v2h4v4h2V5c0-1.1-.9-2-2-2z" />
        </svg>
      </button>
      <button
        onClick={onReset}
        className="p-2 text-ink-60 hover:text-ink-100 hover:bg-ink-05 transition-colors"
        title="Reset View"
      >
        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 5V1L7 6l5 5V7c3.31 0 6 2.69 6 6s-2.69 6-6 6-6-2.69-6-6H4c0 4.42 3.58 8 8 8s8-3.58 8-8-3.58-8-8-8z" />
        </svg>
      </button>
    </div>
  );
}

export const GraphControls = memo(GraphControlsComponent);

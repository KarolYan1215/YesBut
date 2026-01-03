'use client';

import { useState, useCallback } from 'react';
import { useNodesState, useEdgesState, addEdge, type Connection } from 'reactflow';
import { GraphCanvas } from '@/components/graph/graph-canvas';
import { GraphHeatmap } from '@/components/graph/graph-heatmap';
import { SensitivityPanel } from '@/components/graph/panels/sensitivity-panel';
import { useGraph } from '@/hooks/use-graph';

interface GraphViewPageProps {
  params: { id: string };
}

type HeatmapMode = 'conflict' | 'confidence' | 'sensitivity';
type LayoutAlgorithm = 'hierarchical' | 'force' | 'radial';

export default function GraphViewPage({ params }: GraphViewPageProps): JSX.Element {
  const { nodes: initialNodes, edges: initialEdges, isLoading, applyLayout } = useGraph(params.id);

  const [nodes, , onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [heatmapMode, setHeatmapMode] = useState<HeatmapMode>('confidence');
  const [heatmapVisible, setHeatmapVisible] = useState(false);
  const [showSensitivity, setShowSensitivity] = useState(false);
  const [layout, setLayout] = useState<LayoutAlgorithm>('hierarchical');

  const onConnect = useCallback((connection: Connection) => {
    setEdges((eds) => addEdge(connection, eds));
  }, [setEdges]);

  const handleLayoutChange = (algo: LayoutAlgorithm) => {
    setLayout(algo);
    applyLayout(algo);
  };

  if (isLoading) {
    return (
      <div className="h-screen flex items-center justify-center bg-paper">
        <div className="text-sm text-ink-60">Loading graph...</div>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col bg-paper">
      <div className="h-12 border-b border-ink-20 flex items-center justify-between px-4 bg-white">
        <div className="flex items-center gap-4">
          <a href={`/dashboard/sessions/${params.id}`} className="text-sm text-ink-60 hover:text-ink-100">
            Back to Session
          </a>
          <span className="text-ink-20">|</span>
          <span className="text-sm font-medium text-ink-100">Full Graph View</span>
        </div>
        <div className="flex items-center gap-2">
          <select
            value={layout}
            onChange={(e) => handleLayoutChange(e.target.value as LayoutAlgorithm)}
            className="px-2 py-1 text-xs border border-ink-20 rounded"
          >
            <option value="hierarchical">Hierarchical</option>
            <option value="force">Force-Directed</option>
            <option value="radial">Radial</option>
          </select>
          <button
            onClick={() => setShowSensitivity(!showSensitivity)}
            className={`px-3 py-1.5 text-xs rounded transition-colors ${
              showSensitivity ? 'bg-ink-100 text-white' : 'text-ink-60 hover:text-ink-100'
            }`}
          >
            Sensitivity
          </button>
        </div>
      </div>

      <div className="flex-1 flex overflow-hidden relative">
        <div className="flex-1">
          <GraphCanvas
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            isCurrentBranchLocked={false}
          />
          <GraphHeatmap
            mode={heatmapMode}
            visible={heatmapVisible}
            onModeChange={setHeatmapMode}
            onToggleVisibility={() => setHeatmapVisible(!heatmapVisible)}
          />
        </div>

        {showSensitivity && (
          <SensitivityPanel
            sessionId={params.id}
            criticalNodes={[]}
            pathAnalysis={[]}
            stabilityScore={0.75}
            isOpen={showSensitivity}
            onClose={() => setShowSensitivity(false)}
            onHighlightNode={() => {}}
            onRunSimulation={() => {}}
          />
        )}
      </div>
    </div>
  );
}

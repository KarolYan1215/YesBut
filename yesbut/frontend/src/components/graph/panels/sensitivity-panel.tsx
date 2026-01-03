'use client';

import { memo, useState } from 'react';

interface CriticalNodeInfo {
  nodeId: string;
  nodeLabel: string;
  sensitivityScore: number;
  collapseThreshold: number;
  isMinimalCutSet: boolean;
}

interface PathAnalysisResult {
  pathId: string;
  pathType: 'critical' | 'redundant';
  nodeIds: string[];
  redundancyRatio: number;
}

interface SensitivityPanelProps {
  sessionId: string;
  criticalNodes: CriticalNodeInfo[];
  pathAnalysis: PathAnalysisResult[];
  stabilityScore: number;
  isOpen: boolean;
  onClose: () => void;
  onHighlightNode: (nodeId: string | null) => void;
  onRunSimulation: (nodeId: string, newConfidence: number) => void;
}

function SensitivityPanelComponent({
  criticalNodes,
  pathAnalysis,
  stabilityScore,
  isOpen,
  onClose,
  onHighlightNode,
  onRunSimulation,
}: SensitivityPanelProps): JSX.Element | null {
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [simulatedConfidence, setSimulatedConfidence] = useState(0.5);

  if (!isOpen) return null;

  const criticalPaths = pathAnalysis.filter((p) => p.pathType === 'critical');
  const redundantPaths = pathAnalysis.filter((p) => p.pathType === 'redundant');

  return (
    <div className="w-80 bg-white border-l border-ink-20 h-full flex flex-col">
      <div className="flex items-center justify-between px-4 py-3 border-b border-ink-10">
        <span className="text-sm font-medium text-ink-100">Sensitivity Analysis</span>
        <button onClick={onClose} className="text-ink-40 hover:text-ink-80 transition-colors">
          <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
            <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z" />
          </svg>
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <div className="bg-ink-05 rounded-md p-3">
          <div className="text-xs font-mono text-ink-40 uppercase mb-2">Stability Score</div>
          <div className="flex items-center gap-3">
            <div className="flex-1 h-2 bg-ink-10 rounded-full overflow-hidden">
              <div
                className={`h-full transition-all ${
                  stabilityScore > 0.7 ? 'bg-signal-success' : stabilityScore > 0.4 ? 'bg-signal-warning' : 'bg-signal-critical'
                }`}
                style={{ width: `${stabilityScore * 100}%` }}
              />
            </div>
            <span className="text-sm font-mono text-ink-80">{(stabilityScore * 100).toFixed(0)}%</span>
          </div>
        </div>

        <div>
          <h4 className="text-xs font-mono text-ink-40 uppercase mb-2">Critical Nodes</h4>
          <div className="space-y-2">
            {criticalNodes.map((node) => (
              <div
                key={node.nodeId}
                className="bg-ink-05 rounded px-3 py-2 cursor-pointer hover:bg-ink-10 transition-colors"
                onMouseEnter={() => onHighlightNode(node.nodeId)}
                onMouseLeave={() => onHighlightNode(null)}
                onClick={() => setSelectedNodeId(node.nodeId)}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm text-ink-80 truncate">{node.nodeLabel}</span>
                  {node.isMinimalCutSet && (
                    <svg className="w-3 h-3 text-signal-warning" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z" />
                    </svg>
                  )}
                </div>
                <div className="flex items-center justify-between text-[10px] text-ink-40">
                  <span>Sensitivity: {(node.sensitivityScore * 100).toFixed(0)}%</span>
                  <span>Threshold: {(node.collapseThreshold * 100).toFixed(0)}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div>
          <h4 className="text-xs font-mono text-ink-40 uppercase mb-2">Path Analysis</h4>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div className="bg-ink-05 rounded px-2 py-1.5">
              <div className="text-ink-40">Critical</div>
              <div className="text-sm font-mono text-ink-80">{criticalPaths.length}</div>
            </div>
            <div className="bg-ink-05 rounded px-2 py-1.5">
              <div className="text-ink-40">Redundant</div>
              <div className="text-sm font-mono text-signal-success">{redundantPaths.length}</div>
            </div>
          </div>
        </div>

        {selectedNodeId && (
          <div className="border-t border-ink-10 pt-4">
            <h4 className="text-xs font-mono text-ink-40 uppercase mb-2">What-If Simulation</h4>
            <div className="space-y-2">
              <div className="text-xs text-ink-60">
                Simulating: {criticalNodes.find((n) => n.nodeId === selectedNodeId)?.nodeLabel}
              </div>
              <input
                type="range"
                min="0"
                max="100"
                value={simulatedConfidence * 100}
                onChange={(e) => setSimulatedConfidence(Number(e.target.value) / 100)}
                className="w-full"
              />
              <div className="flex items-center justify-between text-xs text-ink-40">
                <span>0%</span>
                <span className="font-mono">{(simulatedConfidence * 100).toFixed(0)}%</span>
                <span>100%</span>
              </div>
              <button
                onClick={() => onRunSimulation(selectedNodeId, simulatedConfidence)}
                className="w-full px-3 py-1.5 text-xs font-medium bg-ink-100 text-white rounded hover:bg-ink-80 transition-colors"
              >
                Run Simulation
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export const SensitivityPanel = memo(SensitivityPanelComponent);

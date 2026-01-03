'use client';

import { useCallback, useMemo } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  type Node,
  type Edge,
  type OnNodesChange,
  type OnEdgesChange,
  type OnConnect,
  type NodeTypes,
  type EdgeTypes,
} from 'reactflow';
import 'reactflow/dist/style.css';

import { GoalNode } from './nodes/goal-node';
import { ClaimNode } from './nodes/claim-node';
import { FactNode } from './nodes/fact-node';
import { ConstraintNode } from './nodes/constraint-node';
import { AtomicTopicNode } from './nodes/atomic-topic-node';
import { PendingNode } from './nodes/pending-node';
import { PreviewNode } from './nodes/preview-node';
import { SynthesisNode } from './nodes/synthesis-node';

import { SupportEdge } from './edges/support-edge';
import { AttackEdge } from './edges/attack-edge';
import { ConflictEdge } from './edges/conflict-edge';
import { DecomposeEdge } from './edges/decompose-edge';
import { EntailEdge } from './edges/entail-edge';
import { CriticalEdge } from './edges/critical-edge';

interface GraphCanvasProps {
  nodes: Node[];
  edges: Edge[];
  onNodesChange: OnNodesChange;
  onEdgesChange: OnEdgesChange;
  onConnect: OnConnect;
  onNodeClick?: (nodeId: string) => void;
  isCurrentBranchLocked: boolean;
  lockingAgentName?: string;
}

const nodeTypes: NodeTypes = {
  goal: GoalNode,
  claim: ClaimNode,
  fact: FactNode,
  constraint: ConstraintNode,
  atomic: AtomicTopicNode,
  pending: PendingNode,
  preview: PreviewNode,
  synthesis: SynthesisNode,
};

const edgeTypes: EdgeTypes = {
  support: SupportEdge,
  attack: AttackEdge,
  conflict: ConflictEdge,
  decompose: DecomposeEdge,
  entail: EntailEdge,
  critical: CriticalEdge,
};

export function GraphCanvas({
  nodes,
  edges,
  onNodesChange,
  onEdgesChange,
  onConnect,
  onNodeClick,
  isCurrentBranchLocked,
  lockingAgentName,
}: GraphCanvasProps): JSX.Element {
  const handleNodeClick = useCallback(
    (_: React.MouseEvent, node: Node) => {
      onNodeClick?.(node.id);
    },
    [onNodeClick]
  );

  const proOptions = useMemo(() => ({ hideAttribution: true }), []);

  return (
    <div className="w-full h-full relative">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeClick={handleNodeClick}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        nodesDraggable={!isCurrentBranchLocked}
        nodesConnectable={!isCurrentBranchLocked}
        elementsSelectable={!isCurrentBranchLocked}
        fitView
        proOptions={proOptions}
        className="bg-paper"
      >
        <Background color="var(--ink-10)" gap={16} />
        <Controls className="bg-white border border-ink-20 rounded-md" />
        <MiniMap
          nodeColor={(node) => {
            const typeColors: Record<string, string> = {
              goal: 'var(--node-goal)',
              claim: 'var(--node-claim)',
              fact: 'var(--node-fact)',
              constraint: 'var(--node-constraint)',
              atomic: 'var(--node-atomic)',
              pending: 'var(--node-pending)',
              preview: 'var(--ink-40)',
              synthesis: 'var(--node-synthesis)',
            };
            return typeColors[node.type || ''] || 'var(--ink-40)';
          }}
          className="bg-white border border-ink-20 rounded-md"
        />
      </ReactFlow>
      {isCurrentBranchLocked && (
        <div className="absolute inset-0 bg-ink-100/10 flex items-center justify-center pointer-events-none">
          <div className="bg-white border border-ink-20 rounded-md px-4 py-3 shadow-sm pointer-events-auto">
            <div className="flex items-center gap-2 text-ink-80">
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                <path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm3.1-9H8.9V6c0-1.71 1.39-3.1 3.1-3.1 1.71 0 3.1 1.39 3.1 3.1v2z" />
              </svg>
              <span className="text-sm font-medium">
                Branch locked by {lockingAgentName || 'Agent'}
              </span>
            </div>
            <p className="text-xs text-ink-60 mt-1">Observation mode - read only</p>
          </div>
        </div>
      )}
    </div>
  );
}

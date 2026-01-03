'use client';

import { memo, useMemo } from 'react';
import type { Node, Edge } from 'reactflow';
import type {
  NodeType,
  GoalNodeData,
  ClaimNodeData,
  FactNodeData,
  ConstraintNodeData,
  AtomicTopicNodeData,
  PendingNodeData,
  SynthesisNodeData,
  AnyNodeData,
} from '@/types/graph';

interface NodeDetailPanelProps {
  selectedNodeId: string | null;
  nodes: Node[];
  edges: Edge[];
  onClose: () => void;
  isOpen: boolean;
  canEdit: boolean;
  onEditNode?: (nodeId: string) => void;
  onDeleteNode?: (nodeId: string) => void;
}

const NODE_TYPE_COLORS: Record<NodeType, string> = {
  GoalNode: 'var(--node-goal)',
  ClaimNode: 'var(--node-claim)',
  FactNode: 'var(--node-fact)',
  ConstraintNode: 'var(--node-constraint)',
  AtomicTopicNode: 'var(--node-atomic)',
  PendingNode: 'var(--node-pending)',
  SynthesisNode: 'var(--node-synthesis)',
  PreviewNode: 'var(--ink-40)',
};

const NODE_TYPE_LABELS: Record<NodeType, string> = {
  GoalNode: 'Goal',
  ClaimNode: 'Claim',
  FactNode: 'Fact',
  ConstraintNode: 'Constraint',
  AtomicTopicNode: 'Atomic Topic',
  PendingNode: 'Pending',
  SynthesisNode: 'Synthesis',
  PreviewNode: 'Preview',
};

function ScoreBar({ label, value, color = 'bg-signal-info' }: { label: string; value: number; color?: string }) {
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs">
        <span className="text-ink-60">{label}</span>
        <span className="font-mono text-ink-80">{(value * 100).toFixed(0)}%</span>
      </div>
      <div className="h-1.5 bg-ink-10 rounded-full overflow-hidden">
        <div className={`h-full ${color} rounded-full transition-all`} style={{ width: `${value * 100}%` }} />
      </div>
    </div>
  );
}

function GoalNodeDetails({ data }: { data: GoalNodeData }) {
  return (
    <div className="space-y-4">
      <div>
        <h4 className="text-xs font-mono text-ink-40 uppercase mb-2">Description</h4>
        <p className="text-sm text-ink-80">{data.description}</p>
      </div>
      <div>
        <h4 className="text-xs font-mono text-ink-40 uppercase mb-2">Created By</h4>
        <p className="text-sm text-ink-60">{data.createdBy}</p>
      </div>
    </div>
  );
}

function ClaimNodeDetails({ data }: { data: ClaimNodeData }) {
  return (
    <div className="space-y-4">
      <div>
        <h4 className="text-xs font-mono text-ink-40 uppercase mb-2">Reasoning</h4>
        <p className="text-sm text-ink-80 whitespace-pre-wrap">{data.reasoning}</p>
      </div>
      <div>
        <h4 className="text-xs font-mono text-ink-40 uppercase mb-2">Scores</h4>
        <div className="space-y-3">
          <ScoreBar label="Validity" value={data.validity} color="bg-signal-success" />
          <ScoreBar label="Utility" value={data.utility} color="bg-signal-info" />
          <ScoreBar label="Novelty" value={data.novelty} color="bg-node-synthesis" />
          <ScoreBar label="Confidence" value={data.confidence} color="bg-node-claim" />
        </div>
      </div>
      <div>
        <h4 className="text-xs font-mono text-ink-40 uppercase mb-2">Agent</h4>
        <div className="flex items-center gap-2">
          <span className="text-xs px-2 py-0.5 bg-ink-05 rounded text-ink-60">{data.agentType}</span>
          <span className="text-xs text-ink-40 font-mono">{data.agentId}</span>
        </div>
      </div>
    </div>
  );
}

function FactNodeDetails({ data }: { data: FactNodeData }) {
  return (
    <div className="space-y-4">
      <div>
        <h4 className="text-xs font-mono text-ink-40 uppercase mb-2">Content</h4>
        <p className="text-sm text-ink-80 whitespace-pre-wrap">{data.content}</p>
      </div>
      <div>
        <h4 className="text-xs font-mono text-ink-40 uppercase mb-2">Sources ({data.sourceCount})</h4>
        <div className="space-y-1 max-h-32 overflow-y-auto">
          {data.sourceUris.map((uri, idx) => (
            <a
              key={idx}
              href={uri}
              target="_blank"
              rel="noopener noreferrer"
              className="block text-xs text-signal-info hover:underline truncate"
            >
              {uri}
            </a>
          ))}
        </div>
      </div>
      <div className="flex items-center gap-4">
        <div>
          <span className="text-xs text-ink-40">Cross-validated: </span>
          <span className={`text-xs ${data.crossValidated ? 'text-signal-success' : 'text-signal-warning'}`}>
            {data.crossValidated ? 'Yes' : 'No'}
          </span>
        </div>
        <div>
          <span className="text-xs text-ink-40">Retrieved: </span>
          <span className="text-xs text-ink-60">{new Date(data.retrievedAt).toLocaleString()}</span>
        </div>
      </div>
      <div>
        <h4 className="text-xs font-mono text-ink-40 uppercase mb-2">Search Query</h4>
        <p className="text-xs text-ink-60 bg-ink-05 px-2 py-1 rounded font-mono">{data.searchQuery}</p>
      </div>
    </div>
  );
}

function ConstraintNodeDetails({ data }: { data: ConstraintNodeData }) {
  return (
    <div className="space-y-4">
      <div>
        <h4 className="text-xs font-mono text-ink-40 uppercase mb-2">Description</h4>
        <p className="text-sm text-ink-80">{data.description}</p>
      </div>
      <div className="flex items-center gap-4">
        <div>
          <span className="text-xs text-ink-40">Type: </span>
          <span className={`text-xs px-2 py-0.5 rounded ${
            data.constraintType === 'hard' ? 'bg-signal-critical/10 text-signal-critical' : 'bg-signal-warning/10 text-signal-warning'
          }`}>
            {data.constraintType.toUpperCase()}
          </span>
        </div>
        {data.constraintType === 'soft' && (
          <div>
            <span className="text-xs text-ink-40">Weight: </span>
            <span className="text-xs font-mono text-ink-80">{data.weight.toFixed(2)}</span>
          </div>
        )}
      </div>
      <div>
        <span className="text-xs text-ink-40">Status: </span>
        <span className={`text-xs ${data.isSatisfied ? 'text-signal-success' : 'text-signal-critical'}`}>
          {data.isSatisfied ? 'Satisfied' : 'Not Satisfied'}
        </span>
      </div>
    </div>
  );
}

function AtomicTopicNodeDetails({ data }: { data: AtomicTopicNodeData }) {
  return (
    <div className="space-y-4">
      <div>
        <h4 className="text-xs font-mono text-ink-40 uppercase mb-2">Description</h4>
        <p className="text-sm text-ink-80">{data.description}</p>
      </div>
      <div>
        <h4 className="text-xs font-mono text-ink-40 uppercase mb-2">Metrics</h4>
        <div className="grid grid-cols-2 gap-2">
          <div className="bg-ink-05 rounded px-2 py-1.5">
            <div className="text-[10px] text-ink-40">Importance</div>
            <div className="text-sm font-mono text-ink-80">{(data.importanceWeight * 100).toFixed(0)}%</div>
          </div>
          <div className="bg-ink-05 rounded px-2 py-1.5">
            <div className="text-[10px] text-ink-40">Supporting Facts</div>
            <div className="text-sm font-mono text-ink-80">{data.supportingFactCount}</div>
          </div>
        </div>
      </div>
      <div>
        <span className="text-xs text-ink-40">Exploration: </span>
        <span className={`text-xs ${data.isExplored ? 'text-signal-success' : 'text-signal-warning'}`}>
          {data.isExplored ? 'Complete' : 'In Progress'}
        </span>
      </div>
    </div>
  );
}

function PendingNodeDetails({ data }: { data: PendingNodeData }) {
  return (
    <div className="space-y-4">
      <div>
        <h4 className="text-xs font-mono text-ink-40 uppercase mb-2">Description</h4>
        <p className="text-sm text-ink-80">{data.description}</p>
      </div>
      <div className="flex items-center gap-4">
        <div>
          <span className="text-xs text-ink-40">Expected Type: </span>
          <span className="text-xs px-2 py-0.5 bg-ink-05 rounded text-ink-60">{data.expectedType}</span>
        </div>
        <div>
          <span className="text-xs text-ink-40">Priority: </span>
          <span className="text-xs font-mono text-ink-80">{data.priority}</span>
        </div>
      </div>
      <div>
        <span className="text-xs text-ink-40">Timeout: </span>
        <span className="text-xs font-mono text-ink-80">{Math.round(data.timeoutRemaining / 1000)}s remaining</span>
      </div>
    </div>
  );
}

function SynthesisNodeDetails({ data }: { data: SynthesisNodeData }) {
  return (
    <div className="space-y-4">
      <div>
        <h4 className="text-xs font-mono text-ink-40 uppercase mb-2">Synthesis Reasoning</h4>
        <p className="text-sm text-ink-80 whitespace-pre-wrap">{data.reasoning}</p>
      </div>
      <div>
        <h4 className="text-xs font-mono text-ink-40 uppercase mb-2">Resolution Method</h4>
        <span className={`text-xs px-2 py-0.5 rounded ${
          data.resolutionMethod === 'integration' ? 'bg-signal-success/10 text-signal-success' :
          data.resolutionMethod === 'compromise' ? 'bg-signal-warning/10 text-signal-warning' :
          'bg-signal-info/10 text-signal-info'
        }`}>
          {data.resolutionMethod.charAt(0).toUpperCase() + data.resolutionMethod.slice(1)}
        </span>
      </div>
      <div>
        <h4 className="text-xs font-mono text-ink-40 uppercase mb-2">Source Nodes ({data.sourceNodeIds.length})</h4>
        <div className="flex flex-wrap gap-1">
          {data.sourceNodeIds.map((id) => (
            <span key={id} className="text-xs px-2 py-0.5 bg-ink-05 rounded font-mono text-ink-60">
              {id.slice(0, 8)}...
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}

function RelatedEdges({ edges, nodeId }: { edges: Edge[]; nodeId: string }) {
  const relatedEdges = useMemo(() => {
    return edges.filter((e) => e.source === nodeId || e.target === nodeId);
  }, [edges, nodeId]);

  if (relatedEdges.length === 0) return null;

  const incomingEdges = relatedEdges.filter((e) => e.target === nodeId);
  const outgoingEdges = relatedEdges.filter((e) => e.source === nodeId);

  return (
    <div className="space-y-3">
      <h4 className="text-xs font-mono text-ink-40 uppercase">Connections</h4>
      {incomingEdges.length > 0 && (
        <div>
          <div className="text-[10px] text-ink-40 mb-1">Incoming ({incomingEdges.length})</div>
          <div className="space-y-1">
            {incomingEdges.slice(0, 5).map((edge) => (
              <div key={edge.id} className="flex items-center gap-2 text-xs">
                <span className="text-ink-40">{edge.source.slice(0, 8)}...</span>
                <span className={`px-1.5 py-0.5 rounded text-[10px] ${
                  edge.type === 'support' ? 'bg-signal-success/10 text-signal-success' :
                  edge.type === 'attack' ? 'bg-signal-critical/10 text-signal-critical' :
                  'bg-ink-10 text-ink-60'
                }`}>
                  {edge.type}
                </span>
              </div>
            ))}
            {incomingEdges.length > 5 && (
              <div className="text-[10px] text-ink-40">+{incomingEdges.length - 5} more</div>
            )}
          </div>
        </div>
      )}
      {outgoingEdges.length > 0 && (
        <div>
          <div className="text-[10px] text-ink-40 mb-1">Outgoing ({outgoingEdges.length})</div>
          <div className="space-y-1">
            {outgoingEdges.slice(0, 5).map((edge) => (
              <div key={edge.id} className="flex items-center gap-2 text-xs">
                <span className={`px-1.5 py-0.5 rounded text-[10px] ${
                  edge.type === 'support' ? 'bg-signal-success/10 text-signal-success' :
                  edge.type === 'attack' ? 'bg-signal-critical/10 text-signal-critical' :
                  'bg-ink-10 text-ink-60'
                }`}>
                  {edge.type}
                </span>
                <span className="text-ink-40">{edge.target.slice(0, 8)}...</span>
              </div>
            ))}
            {outgoingEdges.length > 5 && (
              <div className="text-[10px] text-ink-40">+{outgoingEdges.length - 5} more</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function NodeDetailPanelComponent({
  selectedNodeId,
  nodes,
  edges,
  onClose,
  isOpen,
  canEdit,
  onEditNode,
  onDeleteNode,
}: NodeDetailPanelProps): JSX.Element | null {
  if (!isOpen || !selectedNodeId) return null;

  const selectedNode = nodes.find((n) => n.id === selectedNodeId);
  if (!selectedNode) return null;

  const nodeData = selectedNode.data as AnyNodeData;
  const nodeType = (nodeData?.type || selectedNode.type || 'ClaimNode') as NodeType;
  const nodeColor = NODE_TYPE_COLORS[nodeType] || 'var(--ink-40)';
  const nodeLabel = NODE_TYPE_LABELS[nodeType] || nodeType;

  const renderNodeDetails = () => {
    switch (nodeType) {
      case 'GoalNode':
        return <GoalNodeDetails data={nodeData as GoalNodeData} />;
      case 'ClaimNode':
        return <ClaimNodeDetails data={nodeData as ClaimNodeData} />;
      case 'FactNode':
        return <FactNodeDetails data={nodeData as FactNodeData} />;
      case 'ConstraintNode':
        return <ConstraintNodeDetails data={nodeData as ConstraintNodeData} />;
      case 'AtomicTopicNode':
        return <AtomicTopicNodeDetails data={nodeData as AtomicTopicNodeData} />;
      case 'PendingNode':
        return <PendingNodeDetails data={nodeData as PendingNodeData} />;
      case 'SynthesisNode':
        return <SynthesisNodeDetails data={nodeData as SynthesisNodeData} />;
      default:
        return (
          <div className="text-sm text-ink-60">
            {nodeData?.label || 'No details available'}
          </div>
        );
    }
  };

  return (
    <div className="w-80 bg-white border-l border-ink-20 h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-ink-10">
        <div className="flex items-center gap-2">
          <div className="w-1 h-5 rounded-full" style={{ backgroundColor: nodeColor }} />
          <span className="text-sm font-medium text-ink-100">{nodeLabel}</span>
          {nodeData?.confidence !== undefined && (
            <span className="text-xs font-mono bg-ink-05 text-ink-60 px-1.5 py-0.5 rounded">
              {(nodeData.confidence * 100).toFixed(0)}%
            </span>
          )}
        </div>
        <button onClick={onClose} className="text-ink-40 hover:text-ink-80 transition-colors">
          <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
            <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z" />
          </svg>
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        {/* Node Label */}
        <div>
          <h3 className="text-sm font-semibold text-ink-100">{nodeData?.label || 'Untitled'}</h3>
        </div>

        {/* Node-specific details */}
        {renderNodeDetails()}

        {/* Related Edges */}
        <RelatedEdges edges={edges} nodeId={selectedNodeId} />

        {/* Metadata */}
        <div className="space-y-2">
          <h4 className="text-xs font-mono text-ink-40 uppercase">Metadata</h4>
          <div className="text-xs text-ink-60 space-y-1">
            <div className="flex justify-between">
              <span>ID:</span>
              <span className="font-mono">{selectedNodeId.slice(0, 12)}...</span>
            </div>
            {nodeData?.layer !== undefined && (
              <div className="flex justify-between">
                <span>Layer:</span>
                <span className="font-mono">{nodeData.layer}</span>
              </div>
            )}
            {nodeData?.branchId && (
              <div className="flex justify-between">
                <span>Branch:</span>
                <span className="font-mono">{nodeData.branchId.slice(0, 8)}...</span>
              </div>
            )}
            {nodeData?.version !== undefined && (
              <div className="flex justify-between">
                <span>Version:</span>
                <span className="font-mono">v{nodeData.version}</span>
              </div>
            )}
            {nodeData?.createdAt && (
              <div className="flex justify-between">
                <span>Created:</span>
                <span>{new Date(nodeData.createdAt).toLocaleString()}</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Actions */}
      {canEdit && (
        <div className="p-4 border-t border-ink-10 flex gap-2">
          <button
            onClick={() => onEditNode?.(selectedNodeId)}
            className="flex-1 px-3 py-1.5 text-xs font-medium bg-ink-05 text-ink-80 rounded hover:bg-ink-10 transition-colors"
          >
            Edit
          </button>
          <button
            onClick={() => onDeleteNode?.(selectedNodeId)}
            className="px-3 py-1.5 text-xs font-medium text-signal-critical hover:bg-signal-critical/10 rounded transition-colors"
          >
            Delete
          </button>
        </div>
      )}
    </div>
  );
}

export const NodeDetailPanel = memo(NodeDetailPanelComponent);

/**
 * Graph Types
 *
 * TypeScript type definitions for graph nodes and edges.
 *
 * @module types/graph
 */

/**
 * Node type enumeration
 */
export type NodeType =
  | 'GoalNode'
  | 'ClaimNode'
  | 'FactNode'
  | 'ConstraintNode'
  | 'AtomicTopicNode'
  | 'PendingNode'
  | 'SynthesisNode'
  | 'PreviewNode';

/**
 * Edge type enumeration
 */
export type EdgeType =
  | 'support'
  | 'attack'
  | 'conflict'
  | 'entail'
  | 'decompose'
  | 'derive';

/**
 * Constraint type enumeration
 */
export type ConstraintType = 'hard' | 'soft';

/**
 * Base node data interface
 * All node types extend this interface
 */
export interface BaseNodeData {
  /** Unique node identifier */
  id: string;
  /** Node type */
  type: NodeType;
  /** Display label */
  label: string;
  /** Confidence score (0-1) */
  confidence: number;
  /** Layer index in the graph */
  layer: number;
  /** Branch ID this node belongs to */
  branchId: string;
  /** Version number for optimistic locking */
  version: number;
  /** Whether this is a preview node (streaming) */
  isPreview: boolean;
  /** Creation timestamp */
  createdAt: string;
  /** Last update timestamp */
  updatedAt: string;
}

/**
 * Goal node data interface
 */
export interface GoalNodeData extends BaseNodeData {
  type: 'GoalNode';
  /** Detailed description of the goal */
  description: string;
  /** ID of the user who created this goal */
  createdBy: string;
}

/**
 * Claim node data interface
 */
export interface ClaimNodeData extends BaseNodeData {
  type: 'ClaimNode';
  /** Detailed reasoning behind the claim */
  reasoning: string;
  /** Validity score (0-1) */
  validity: number;
  /** Utility score (0-1) */
  utility: number;
  /** Novelty score (0-1) */
  novelty: number;
  /** ID of the agent that generated this claim */
  agentId: string;
  /** Type of agent */
  agentType: string;
}

/**
 * Fact node data interface
 */
export interface FactNodeData extends BaseNodeData {
  type: 'FactNode';
  /** Detailed content of the fact */
  content: string;
  /** Array of source URIs */
  sourceUris: string[];
  /** Timestamp when retrieved */
  retrievedAt: string;
  /** Search query used */
  searchQuery: string;
  /** ID of the ISA agent */
  agentId: string;
  /** Whether cross-validated */
  crossValidated: boolean;
  /** Number of confirming sources */
  sourceCount: number;
}

/**
 * Constraint node data interface
 */
export interface ConstraintNodeData extends BaseNodeData {
  type: 'ConstraintNode';
  /** Detailed description */
  description: string;
  /** Hard or soft constraint */
  constraintType: ConstraintType;
  /** Weight for soft constraints */
  weight: number;
  /** Whether currently satisfied */
  isSatisfied: boolean;
  /** ID of the user who created this */
  createdBy: string;
}

/**
 * Atomic topic node data interface
 */
export interface AtomicTopicNodeData extends BaseNodeData {
  type: 'AtomicTopicNode';
  /** Detailed description */
  description: string;
  /** Importance weight */
  importanceWeight: number;
  /** Whether fully explored */
  isExplored: boolean;
  /** Number of supporting facts */
  supportingFactCount: number;
  /** ID of the agent */
  agentId: string;
}

/**
 * Pending node data interface
 */
export interface PendingNodeData extends BaseNodeData {
  type: 'PendingNode';
  /** Description of what needs to be matched */
  description: string;
  /** Expected type to match */
  expectedType: NodeType;
  /** Priority for matching */
  priority: number;
  /** Timeout remaining (ms) */
  timeoutRemaining: number;
  /** ID of the agent */
  agentId: string;
}

/**
 * Synthesis node data interface
 */
export interface SynthesisNodeData extends BaseNodeData {
  type: 'SynthesisNode';
  /** Synthesis reasoning */
  reasoning: string;
  /** IDs of source nodes */
  sourceNodeIds: string[];
  /** Resolution method */
  resolutionMethod: 'integration' | 'compromise' | 'transcendence';
  /** ID of the BM agent */
  agentId: string;
}

/**
 * Union type for all node data types
 */
export type AnyNodeData =
  | GoalNodeData
  | ClaimNodeData
  | FactNodeData
  | ConstraintNodeData
  | AtomicTopicNodeData
  | PendingNodeData
  | SynthesisNodeData;

/**
 * Base edge data interface
 */
export interface BaseEdgeData {
  /** Unique edge identifier */
  id: string;
  /** Edge type */
  type: EdgeType;
  /** Source node ID */
  sourceId: string;
  /** Target node ID */
  targetId: string;
  /** Edge weight (0-1) */
  weight: number;
  /** Explanation of the relationship */
  explanation: string;
  /** ID of the agent that created this edge */
  agentId: string;
  /** Whether this is a preview edge */
  isPreview: boolean;
  /** Creation timestamp */
  createdAt: string;
}

/**
 * Support edge data interface
 */
export interface SupportEdgeData extends BaseEdgeData {
  type: 'support';
}

/**
 * Attack edge data interface
 */
export interface AttackEdgeData extends BaseEdgeData {
  type: 'attack';
  /** Whether validated by ACA */
  validated: boolean;
}

/**
 * Conflict edge data interface
 */
export interface ConflictEdgeData extends BaseEdgeData {
  type: 'conflict';
  /** Whether resolved via synthesis */
  resolved: boolean;
  /** ID of resolution node */
  resolutionNodeId?: string;
}

/**
 * Entail edge data interface
 */
export interface EntailEdgeData extends BaseEdgeData {
  type: 'entail';
}

/**
 * Decompose edge data interface
 */
export interface DecomposeEdgeData extends BaseEdgeData {
  type: 'decompose';
}

/**
 * Union type for all edge data types
 */
export type AnyEdgeData =
  | SupportEdgeData
  | AttackEdgeData
  | ConflictEdgeData
  | EntailEdgeData
  | DecomposeEdgeData;

/**
 * Hyperedge type enumeration
 */
export type HyperedgeType = 'conflict' | 'dependency' | 'aggregation';

/**
 * Hyperedge data interface
 */
export interface HyperedgeData {
  /** Unique hyperedge identifier */
  id: string;
  /** Hyperedge type */
  type: HyperedgeType;
  /** IDs of connected nodes */
  nodeIds: string[];
  /** Explanation */
  explanation: string;
  /** Creation timestamp */
  createdAt: string;
}

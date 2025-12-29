/**
 * Graph Canvas Component
 *
 * Main React Flow canvas for visualizing the layered graph network.
 * This is the core visualization component of the YesBut system.
 *
 * @module components/graph/graph-canvas
 */

import type { Node, Edge, OnNodesChange, OnEdgesChange, OnConnect } from 'reactflow';

/**
 * Props interface for GraphCanvas component
 */
interface GraphCanvasProps {
  /**
   * Array of graph nodes to render
   */
  nodes: Node[];

  /**
   * Array of graph edges to render
   */
  edges: Edge[];

  /**
   * Callback fired when nodes change (position, selection, etc.)
   */
  onNodesChange: OnNodesChange;

  /**
   * Callback fired when edges change
   */
  onEdgesChange: OnEdgesChange;

  /**
   * Callback fired when a new connection is made between nodes
   */
  onConnect: OnConnect;

  /**
   * Callback fired when a node is clicked
   * @param nodeId - The ID of the clicked node
   */
  onNodeClick?: (nodeId: string) => void;

  /**
   * Whether the current branch is locked (OBSERVATION mode)
   * When true, node dragging and editing are disabled
   */
  isCurrentBranchLocked: boolean;

  /**
   * The name of the agent currently holding the lock (if any)
   */
  lockingAgentName?: string;
}

/**
 * Graph canvas component for visualizing the layered graph network
 *
 * Features:
 * - Renders custom node types (Goal, Claim, Fact, Constraint, AtomicTopic, Pending, Preview)
 * - Renders custom edge types (Support, Attack, Conflict, Entail, Decompose, Critical)
 * - Supports zoom, pan, and minimap navigation
 * - Lock-aware: disables editing when branch is locked
 * - Displays observation mode overlay when locked
 *
 * The canvas integrates with the graph store for state management
 * and the lock store for branch locking state.
 *
 * @param props - Component props
 * @returns The graph canvas JSX element
 */
export function GraphCanvas(props: GraphCanvasProps): JSX.Element {
  // TODO: Implement React Flow canvas with custom node/edge types
  // TODO: Bind nodesDraggable and nodesConnectable to lock state
  // TODO: Add observation mode overlay when locked
  throw new Error('Not implemented');
}

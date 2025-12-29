/**
 * Conflict Edge Component
 *
 * Visualizes a conflict relationship where two nodes are mutually exclusive.
 *
 * @module components/graph/edges/conflict-edge
 */

import type { EdgeProps } from 'reactflow';

/**
 * Data interface for ConflictEdge
 */
interface ConflictEdgeData {
  /**
   * Conflict is binary (always 1)
   */
  weight: 1;

  /**
   * Explanation of why nodes are mutually exclusive
   */
  explanation: string;

  /**
   * ID of the agent that detected this conflict
   */
  agentId: string;

  /**
   * Whether this conflict has been resolved via synthesis
   */
  resolved: boolean;

  /**
   * ID of the synthesis node that resolved this conflict (if any)
   */
  resolutionNodeId?: string;

  /**
   * Whether this edge is selected
   */
  selected: boolean;

  /**
   * Whether this is a preview edge (streaming)
   */
  isPreview: boolean;
}

/**
 * Conflict edge component
 *
 * Visual characteristics:
 * - Orange/yellow color
 * - Bidirectional (no arrow, or double arrow)
 * - Dashed line pattern
 * - Warning/conflict icon at midpoint
 * - Pulsing animation if unresolved
 *
 * Represents a horizontal edge indicating that two nodes
 * cannot both be true simultaneously. Used in conflict view
 * for game-theoretic analysis.
 *
 * @param props - React Flow edge props with ConflictEdgeData
 * @returns The conflict edge JSX element
 */
export function ConflictEdge(props: EdgeProps<ConflictEdgeData>): JSX.Element {
  // TODO: Implement conflict edge visualization
  throw new Error('Not implemented');
}

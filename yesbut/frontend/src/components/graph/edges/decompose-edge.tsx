/**
 * Decompose Edge Component
 *
 * Visualizes a decomposition relationship (vertical edge) from parent to child.
 *
 * @module components/graph/edges/decompose-edge
 */

import type { EdgeProps } from 'reactflow';

/**
 * Data interface for DecomposeEdge
 */
interface DecomposeEdgeData {
  /**
   * Decomposition weight (contribution to parent)
   */
  weight: number;

  /**
   * Explanation of the decomposition relationship
   */
  explanation: string;

  /**
   * ID of the agent that performed the decomposition
   */
  agentId: string;

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
 * Decompose edge component
 *
 * Visual characteristics:
 * - Gray/neutral color
 * - Solid line
 * - Arrow pointing from parent to child (downward)
 * - Represents vertical (hierarchical) relationship
 *
 * Represents a vertical edge in the layered graph network,
 * indicating that the parent node is decomposed into child nodes.
 * This is the primary edge type for the tree structure.
 *
 * @param props - React Flow edge props with DecomposeEdgeData
 * @returns The decompose edge JSX element
 */
export function DecomposeEdge(props: EdgeProps<DecomposeEdgeData>): JSX.Element {
  // TODO: Implement decompose edge visualization
  throw new Error('Not implemented');
}

/**
 * Entail Edge Component
 *
 * Visualizes an entailment relationship where source logically implies target.
 *
 * @module components/graph/edges/entail-edge
 */

import type { EdgeProps } from 'reactflow';

/**
 * Data interface for EntailEdge
 */
interface EntailEdgeData {
  /**
   * Entailment is binary (always 1)
   */
  weight: 1;

  /**
   * Logical explanation of the entailment
   */
  explanation: string;

  /**
   * ID of the agent that identified this entailment
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
 * Entail edge component
 *
 * Visual characteristics:
 * - Blue color
 * - Solid line with double arrow
 * - Implies/therefore icon (=>)
 * - Used in causal view for logical chains
 *
 * Represents a horizontal edge indicating that if the source
 * node is true, the target node must also be true (logical implication).
 *
 * @param props - React Flow edge props with EntailEdgeData
 * @returns The entail edge JSX element
 */
export function EntailEdge(props: EdgeProps<EntailEdgeData>): JSX.Element {
  // TODO: Implement entail edge visualization
  throw new Error('Not implemented');
}

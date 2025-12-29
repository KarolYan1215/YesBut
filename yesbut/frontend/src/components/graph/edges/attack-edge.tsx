/**
 * Attack Edge Component
 *
 * Visualizes an attack relationship where source node weakens
 * the credibility of the target node.
 *
 * @module components/graph/edges/attack-edge
 */

import type { EdgeProps } from 'reactflow';

/**
 * Data interface for AttackEdge
 */
interface AttackEdgeData {
  /**
   * Attack strength (0-1)
   */
  weight: number;

  /**
   * Explanation of how source attacks target
   */
  explanation: string;

  /**
   * ID of the agent that created this attack
   */
  agentId: string;

  /**
   * Whether this attack has been validated by ACA
   */
  validated: boolean;

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
 * Attack edge component
 *
 * Visual characteristics:
 * - Red color
 * - Solid line with jagged/lightning pattern
 * - Arrow pointing to target
 * - Thickness based on weight
 * - X icon or warning marker
 *
 * Represents a horizontal edge where the source node
 * weakens or contradicts the target node's credibility.
 * Attacks must be validated by the ACA agent.
 *
 * @param props - React Flow edge props with AttackEdgeData
 * @returns The attack edge JSX element
 */
export function AttackEdge(props: EdgeProps<AttackEdgeData>): JSX.Element {
  // TODO: Implement attack edge visualization
  throw new Error('Not implemented');
}

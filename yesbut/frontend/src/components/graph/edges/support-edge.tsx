/**
 * Support Edge Component
 *
 * Visualizes a support relationship where source node provides
 * positive evidence for the target node.
 *
 * @module components/graph/edges/support-edge
 */

import type { EdgeProps } from 'reactflow';

/**
 * Data interface for SupportEdge
 */
interface SupportEdgeData {
  /**
   * Support strength (0-1)
   */
  weight: number;

  /**
   * Explanation of how source supports target
   */
  explanation: string;

  /**
   * ID of the agent that created this edge
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
 * Support edge component
 *
 * Visual characteristics:
 * - Green color
 * - Solid line
 * - Arrow pointing to target
 * - Thickness based on weight
 * - Plus icon or checkmark marker
 *
 * Represents a horizontal edge where the source node
 * provides positive evidence supporting the target node.
 *
 * @param props - React Flow edge props with SupportEdgeData
 * @returns The support edge JSX element
 */
export function SupportEdge(props: EdgeProps<SupportEdgeData>): JSX.Element {
  // TODO: Implement support edge visualization
  throw new Error('Not implemented');
}

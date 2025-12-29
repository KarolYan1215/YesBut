/**
 * Pending Node Component
 *
 * Visualizes a PendingNode - a top-down generated node awaiting bottom-up matching.
 *
 * @module components/graph/nodes/pending-node
 */

import type { NodeProps } from 'reactflow';

/**
 * Data interface for PendingNode
 */
interface PendingNodeData {
  /**
   * The pending requirement/condition text
   */
  label: string;

  /**
   * Description of what needs to be matched
   */
  description: string;

  /**
   * Expected type of node to match (e.g., 'FactNode', 'ClaimNode')
   */
  expectedType: string;

  /**
   * Priority for matching (higher = more urgent)
   */
  priority: number;

  /**
   * Time remaining before timeout (ms)
   */
  timeoutRemaining: number;

  /**
   * ID of the agent that created this pending node
   */
  agentId: string;

  /**
   * Layer index in the graph
   */
  layer: number;

  /**
   * Whether this node is selected
   */
  selected: boolean;

  /**
   * Whether this is a preview node (streaming)
   */
  isPreview: boolean;

  /**
   * Version number for optimistic locking
   */
  version: number;
}

/**
 * Pending node component
 *
 * Visual characteristics:
 * - Dashed border (incomplete state)
 * - Pulsing animation (awaiting match)
 * - Question mark or hourglass icon
 * - Timeout countdown indicator
 *
 * Interactions:
 * - Click to select and view details
 * - System will attempt to match with bottom-up nodes
 * - Converts to matched node type when fulfilled
 *
 * @param props - React Flow node props with PendingNodeData
 * @returns The pending node JSX element
 */
export function PendingNode(props: NodeProps<PendingNodeData>): JSX.Element {
  // TODO: Implement pending node visualization
  throw new Error('Not implemented');
}

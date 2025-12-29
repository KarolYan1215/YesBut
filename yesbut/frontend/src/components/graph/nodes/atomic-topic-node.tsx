/**
 * Atomic Topic Node Component
 *
 * Visualizes an AtomicTopicNode - an indivisible atomic topic unit.
 *
 * @module components/graph/nodes/atomic-topic-node
 */

import type { NodeProps } from 'reactflow';

/**
 * Data interface for AtomicTopicNode
 */
interface AtomicTopicNodeData {
  /**
   * The atomic topic text
   */
  label: string;

  /**
   * Detailed description of the topic
   */
  description: string;

  /**
   * Importance weight calculated via semantic quantification
   */
  importanceWeight: number;

  /**
   * Confidence score (0-1)
   */
  confidence: number;

  /**
   * Whether this topic has been fully explored
   */
  isExplored: boolean;

  /**
   * Number of facts supporting this topic
   */
  supportingFactCount: number;

  /**
   * ID of the agent that decomposed to this topic
   */
  agentId: string;

  /**
   * Layer index in the graph (typically leaf layer)
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
 * Atomic topic node component
 *
 * Visual characteristics:
 * - Smaller size (leaf node)
 * - Distinct shape (e.g., circle or atom icon)
 * - Color indicates exploration status
 * - Importance weight displayed as size or badge
 *
 * Interactions:
 * - Click to select and view details
 * - Cannot be further decomposed (atomic)
 * - Triggers information retrieval when explored
 *
 * @param props - React Flow node props with AtomicTopicNodeData
 * @returns The atomic topic node JSX element
 */
export function AtomicTopicNode(props: NodeProps<AtomicTopicNodeData>): JSX.Element {
  // TODO: Implement atomic topic node visualization
  throw new Error('Not implemented');
}

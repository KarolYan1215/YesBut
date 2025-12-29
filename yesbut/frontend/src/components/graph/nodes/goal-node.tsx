/**
 * Goal Node Component
 *
 * Visualizes a GoalNode - the root node representing the final decision goal
 * or initial idea/requirement.
 *
 * @module components/graph/nodes/goal-node
 */

import type { NodeProps } from 'reactflow';

/**
 * Data interface for GoalNode
 */
interface GoalNodeData {
  /**
   * The goal/requirement text
   */
  label: string;

  /**
   * Detailed description of the goal
   */
  description: string;

  /**
   * Confidence score (0-1)
   */
  confidence: number;

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

  /**
   * Creation timestamp
   */
  createdAt: string;

  /**
   * ID of the user who created this goal
   */
  createdBy: string;
}

/**
 * Goal node component
 *
 * Visual characteristics:
 * - Larger size than other nodes (prominent root)
 * - Distinct color (e.g., blue/purple gradient)
 * - Star or target icon
 * - Only exists at layer 0 (root layer)
 *
 * Interactions:
 * - Click to select and view details
 * - User can modify (if not locked)
 * - Cannot be deleted (root node)
 *
 * @param props - React Flow node props with GoalNodeData
 * @returns The goal node JSX element
 */
export function GoalNode(props: NodeProps<GoalNodeData>): JSX.Element {
  // TODO: Implement goal node visualization
  throw new Error('Not implemented');
}

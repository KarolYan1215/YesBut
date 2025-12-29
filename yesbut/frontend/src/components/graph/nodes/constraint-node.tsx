/**
 * Constraint Node Component
 *
 * Visualizes a ConstraintNode - a user-defined hard or soft constraint.
 *
 * @module components/graph/nodes/constraint-node
 */

import type { NodeProps } from 'reactflow';

/**
 * Constraint type enumeration
 */
type ConstraintType = 'hard' | 'soft';

/**
 * Data interface for ConstraintNode
 */
interface ConstraintNodeData {
  /**
   * The constraint statement text
   */
  label: string;

  /**
   * Detailed description of the constraint
   */
  description: string;

  /**
   * Type of constraint
   * - 'hard': Must be satisfied, violation results in -infinity utility
   * - 'soft': Preferred but not required, affects utility score
   */
  constraintType: ConstraintType;

  /**
   * Weight/importance of the constraint (for soft constraints)
   */
  weight: number;

  /**
   * Whether this constraint is currently satisfied
   */
  isSatisfied: boolean;

  /**
   * ID of the user who defined this constraint
   */
  createdBy: string;

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
 * Constraint node component
 *
 * Visual characteristics:
 * - Distinct shape (e.g., shield or lock icon)
 * - Hard constraints: Red border, lock icon
 * - Soft constraints: Orange border, preference icon
 * - Satisfaction indicator (checkmark or X)
 *
 * Interactions:
 * - Click to select and view details
 * - User can modify (if not locked)
 * - Can be added at any layer
 *
 * @param props - React Flow node props with ConstraintNodeData
 * @returns The constraint node JSX element
 */
export function ConstraintNode(props: NodeProps<ConstraintNodeData>): JSX.Element {
  // TODO: Implement constraint node visualization
  throw new Error('Not implemented');
}

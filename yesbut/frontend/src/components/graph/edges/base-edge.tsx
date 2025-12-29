/**
 * Base Edge Component
 *
 * Base wrapper component for all custom edge types in the graph.
 *
 * @module components/graph/edges/base-edge
 */

import type { EdgeProps } from 'reactflow';

/**
 * Base data interface for all edge types
 */
interface BaseEdgeData {
  /**
   * Weight/strength of the relationship (0-1)
   */
  weight: number;

  /**
   * Whether this edge is currently selected
   */
  selected: boolean;

  /**
   * Whether this edge is in preview state (streaming)
   */
  isPreview: boolean;

  /**
   * Optional label to display on the edge
   */
  label?: string;
}

/**
 * Props interface for BaseEdge component
 */
interface BaseEdgeProps extends EdgeProps<BaseEdgeData> {
  /**
   * The edge type identifier for styling
   */
  edgeType: string;

  /**
   * Color for the edge stroke
   */
  strokeColor: string;

  /**
   * Whether to show an animated flow effect
   */
  animated: boolean;
}

/**
 * Base edge wrapper component
 *
 * Provides common functionality for all edge types:
 * - Consistent stroke styling
 * - Selection highlight state
 * - Preview state styling (dashed for streaming edges)
 * - Weight-based opacity
 * - Optional label rendering
 * - Animated flow effect
 *
 * All specific edge types (SupportEdge, AttackEdge, etc.) extend this base.
 *
 * @param props - Component props including React Flow edge props
 * @returns The base edge JSX element
 */
export function BaseEdge(props: BaseEdgeProps): JSX.Element {
  // TODO: Implement base edge wrapper with common styling
  throw new Error('Not implemented');
}

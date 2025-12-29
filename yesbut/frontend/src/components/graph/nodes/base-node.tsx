/**
 * Base Node Component
 *
 * Base wrapper component for all custom node types in the graph.
 * Provides common styling, selection state, and interaction handlers.
 *
 * @module components/graph/nodes/base-node
 */

import type { NodeProps } from 'reactflow';

/**
 * Base data interface for all node types
 */
interface BaseNodeData {
  /**
   * Display label for the node
   */
  label: string;

  /**
   * Confidence score (0-1) for the node content
   */
  confidence: number;

  /**
   * Whether this node is currently selected
   */
  selected: boolean;

  /**
   * Whether this node is in preview state (streaming, not yet finalized)
   */
  isPreview: boolean;

  /**
   * Version number for optimistic locking
   */
  version: number;
}

/**
 * Props interface for BaseNode component
 */
interface BaseNodeProps extends NodeProps<BaseNodeData> {
  /**
   * The node type identifier for styling
   */
  nodeType: string;

  /**
   * Child content to render inside the node
   */
  children: React.ReactNode;
}

/**
 * Base node wrapper component
 *
 * Provides common functionality for all node types:
 * - Consistent border and shadow styling
 * - Selection highlight state
 * - Preview state styling (dashed border for streaming nodes)
 * - Confidence indicator (color-coded border)
 * - Connection handles (source/target)
 *
 * All specific node types (GoalNode, ClaimNode, etc.) extend this base.
 *
 * @param props - Component props including React Flow node props
 * @returns The base node JSX element
 */
export function BaseNode(props: BaseNodeProps): JSX.Element {
  // TODO: Implement base node wrapper with common styling
  // TODO: Add selection and preview state handling
  throw new Error('Not implemented');
}

/**
 * Claim Node Component
 *
 * Visualizes a ClaimNode - an agent-generated reasoning conclusion.
 *
 * @module components/graph/nodes/claim-node
 */

import type { NodeProps } from 'reactflow';

/**
 * Data interface for ClaimNode
 */
interface ClaimNodeData {
  /**
   * The claim statement text
   */
  label: string;

  /**
   * Detailed reasoning behind the claim
   */
  reasoning: string;

  /**
   * Confidence score (0-1)
   */
  confidence: number;

  /**
   * Validity score (0-1) - logical soundness
   */
  validity: number;

  /**
   * Utility score (0-1) - value to the goal
   */
  utility: number;

  /**
   * Novelty score (0-1) - non-obviousness
   */
  novelty: number;

  /**
   * ID of the agent that generated this claim
   */
  agentId: string;

  /**
   * Type of agent (e.g., 'BM', 'GEN')
   */
  agentType: string;

  /**
   * ID of the branch this claim belongs to
   */
  branchId: string;

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
 * Claim node component
 *
 * Visual characteristics:
 * - Standard node size
 * - Color varies by confidence (green=high, yellow=medium, red=low)
 * - Lightbulb or speech bubble icon
 * - Shows agent avatar badge
 *
 * Interactions:
 * - Click to select and view details
 * - Can be attacked by other agents
 * - Can be modified by system (not user directly)
 *
 * @param props - React Flow node props with ClaimNodeData
 * @returns The claim node JSX element
 */
export function ClaimNode(props: NodeProps<ClaimNodeData>): JSX.Element {
  // TODO: Implement claim node visualization
  throw new Error('Not implemented');
}

/**
 * Fact Node Component
 *
 * Visualizes a FactNode - an externally verified objective fact.
 *
 * @module components/graph/nodes/fact-node
 */

import type { NodeProps } from 'reactflow';

/**
 * Data interface for FactNode
 */
interface FactNodeData {
  /**
   * The fact statement text
   */
  label: string;

  /**
   * Detailed content of the fact
   */
  content: string;

  /**
   * Confidence score (0-1) based on source reliability
   */
  confidence: number;

  /**
   * Array of source URIs where this fact was retrieved
   */
  sourceUris: string[];

  /**
   * Timestamp when the fact was retrieved
   */
  retrievedAt: string;

  /**
   * The search query used to find this fact
   */
  searchQuery: string;

  /**
   * ID of the ISA agent that retrieved this fact
   */
  agentId: string;

  /**
   * Whether this fact has been cross-validated from multiple sources
   */
  crossValidated: boolean;

  /**
   * Number of independent sources confirming this fact
   */
  sourceCount: number;

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
 * Fact node component
 *
 * Visual characteristics:
 * - Distinct shape (e.g., hexagon or document icon)
 * - Color indicates verification status (green=verified, yellow=pending)
 * - Source count badge
 * - Link icon for external sources
 *
 * Interactions:
 * - Click to select and view details
 * - Click source links to open external URLs
 * - Immutable - cannot be modified after creation
 *
 * @param props - React Flow node props with FactNodeData
 * @returns The fact node JSX element
 */
export function FactNode(props: NodeProps<FactNodeData>): JSX.Element {
  // TODO: Implement fact node visualization
  throw new Error('Not implemented');
}

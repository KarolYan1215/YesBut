/**
 * Streaming Store
 *
 * Zustand store for managing streaming/preview state during agent output.
 *
 * @module store/streaming-store
 */

/**
 * Preview node data
 */
interface PreviewNode {
  id: string;
  targetType: string;
  label: string;
  partialReasoning: string;
  agentId: string;
  agentType: string;
  progress: number;
  isTyping: boolean;
}

/**
 * Preview edge data
 */
interface PreviewEdge {
  id: string;
  sourceId: string;
  targetId: string;
  edgeType: string;
  agentId: string;
}

/**
 * Streaming store state interface
 */
interface StreamingStoreState {
  /**
   * Map of preview node ID to preview data
   */
  previewNodes: Map<string, PreviewNode>;

  /**
   * Map of preview edge ID to preview data
   */
  previewEdges: Map<string, PreviewEdge>;

  /**
   * ID of the currently active (streaming) agent
   */
  activeAgentId: string | null;

  /**
   * Current reasoning step being displayed
   */
  currentReasoningStep: string | null;

  /**
   * Current phase progress (0-1)
   */
  phaseProgress: number;

  /**
   * Current phase name
   */
  currentPhase: 'divergence' | 'filtering' | 'convergence' | null;

  /**
   * Whether streaming is currently active
   */
  isStreaming: boolean;
}

/**
 * Streaming store actions interface
 */
interface StreamingStoreActions {
  /**
   * Add or update a preview node
   * @param node - Preview node data
   */
  upsertPreviewNode: (node: PreviewNode) => void;

  /**
   * Remove a preview node (when finalized)
   * @param nodeId - ID of the preview node
   */
  removePreviewNode: (nodeId: string) => void;

  /**
   * Add or update a preview edge
   * @param edge - Preview edge data
   */
  upsertPreviewEdge: (edge: PreviewEdge) => void;

  /**
   * Remove a preview edge (when finalized)
   * @param edgeId - ID of the preview edge
   */
  removePreviewEdge: (edgeId: string) => void;

  /**
   * Set the active agent
   * @param agentId - ID of the active agent (null if none)
   */
  setActiveAgent: (agentId: string | null) => void;

  /**
   * Update the current reasoning step
   * @param step - Reasoning step text
   */
  setReasoningStep: (step: string | null) => void;

  /**
   * Update phase progress
   * @param phase - Phase name
   * @param progress - Progress value (0-1)
   */
  updatePhaseProgress: (phase: string, progress: number) => void;

  /**
   * Set streaming state
   * @param isStreaming - Whether streaming is active
   */
  setStreaming: (isStreaming: boolean) => void;

  /**
   * Clear all preview state
   */
  clearPreviews: () => void;

  /**
   * Reset the store to initial state
   */
  reset: () => void;
}

/**
 * Combined streaming store type
 */
type StreamingStore = StreamingStoreState & StreamingStoreActions;

/**
 * Create the streaming store
 *
 * This Zustand store manages streaming/preview state:
 * - Preview nodes (dashed border, not yet finalized)
 * - Preview edges (streaming connections)
 * - Active agent tracking
 * - Reasoning step display
 * - Phase progress tracking
 *
 * The store is updated via SSE events:
 * - node_preview -> upsertPreviewNode
 * - node_finalized -> removePreviewNode
 * - agent_thinking -> setActiveAgent, setReasoningStep
 * - phase_progress -> updatePhaseProgress
 *
 * @returns Zustand store hook
 */
export function createStreamingStore(): StreamingStore {
  // TODO: Implement Zustand store
  throw new Error('Not implemented');
}

/**
 * Streaming store hook
 */
export const useStreamingStore = createStreamingStore;

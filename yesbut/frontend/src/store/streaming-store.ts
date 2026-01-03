/**
 * Streaming Store
 *
 * Zustand store for managing streaming/preview state during agent output.
 *
 * @module store/streaming-store
 */

import { create } from 'zustand';

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

interface PreviewEdge {
  id: string;
  sourceId: string;
  targetId: string;
  edgeType: string;
  agentId: string;
}

type Phase = 'divergence' | 'filtering' | 'convergence';

interface StreamingStoreState {
  previewNodes: Map<string, PreviewNode>;
  previewEdges: Map<string, PreviewEdge>;
  activeAgentId: string | null;
  currentReasoningStep: string | null;
  phaseProgress: number;
  currentPhase: Phase | null;
  isStreaming: boolean;
}

interface StreamingStoreActions {
  upsertPreviewNode: (node: PreviewNode) => void;
  removePreviewNode: (nodeId: string) => void;
  upsertPreviewEdge: (edge: PreviewEdge) => void;
  removePreviewEdge: (edgeId: string) => void;
  setActiveAgent: (agentId: string | null) => void;
  setReasoningStep: (step: string | null) => void;
  updatePhaseProgress: (phase: Phase, progress: number) => void;
  setStreaming: (isStreaming: boolean) => void;
  clearPreviews: () => void;
  reset: () => void;
}

type StreamingStore = StreamingStoreState & StreamingStoreActions;

const initialState: StreamingStoreState = {
  previewNodes: new Map(),
  previewEdges: new Map(),
  activeAgentId: null,
  currentReasoningStep: null,
  phaseProgress: 0,
  currentPhase: null,
  isStreaming: false,
};

export const useStreamingStore = create<StreamingStore>((set) => ({
  ...initialState,

  upsertPreviewNode: (node) =>
    set((state) => {
      const newMap = new Map(state.previewNodes);
      newMap.set(node.id, node);
      return { previewNodes: newMap };
    }),

  removePreviewNode: (nodeId) =>
    set((state) => {
      const newMap = new Map(state.previewNodes);
      newMap.delete(nodeId);
      return { previewNodes: newMap };
    }),

  upsertPreviewEdge: (edge) =>
    set((state) => {
      const newMap = new Map(state.previewEdges);
      newMap.set(edge.id, edge);
      return { previewEdges: newMap };
    }),

  removePreviewEdge: (edgeId) =>
    set((state) => {
      const newMap = new Map(state.previewEdges);
      newMap.delete(edgeId);
      return { previewEdges: newMap };
    }),

  setActiveAgent: (agentId) => set({ activeAgentId: agentId }),

  setReasoningStep: (step) => set({ currentReasoningStep: step }),

  updatePhaseProgress: (phase, progress) =>
    set({ currentPhase: phase, phaseProgress: progress }),

  setStreaming: (isStreaming) => set({ isStreaming }),

  clearPreviews: () =>
    set({
      previewNodes: new Map(),
      previewEdges: new Map(),
      activeAgentId: null,
      currentReasoningStep: null,
    }),

  reset: () => set(initialState),
}));

/**
 * Graph Store
 *
 * Zustand store for managing graph nodes and edges state.
 *
 * @module store/graph-store
 */

import { create } from 'zustand';
import type { Node, Edge } from 'reactflow';

interface GraphState {
  nodes: Node[];
  edges: Edge[];
  selectedNodeId: string | null;
  selectedEdgeIds: string[];
  zoomLevel: number;
  viewport: { x: number; y: number };
}

interface GraphActions {
  setNodes: (nodes: Node[]) => void;
  setEdges: (edges: Edge[]) => void;
  addNode: (node: Node) => void;
  updateNode: (nodeId: string, updates: Partial<Node>) => void;
  removeNode: (nodeId: string) => void;
  addEdge: (edge: Edge) => void;
  removeEdge: (edgeId: string) => void;
  setSelectedNode: (nodeId: string | null) => void;
  setSelectedEdges: (edgeIds: string[]) => void;
  setZoomLevel: (level: number) => void;
  setViewport: (viewport: { x: number; y: number }) => void;
  reset: () => void;
}

type GraphStore = GraphState & GraphActions;

const initialState: GraphState = {
  nodes: [],
  edges: [],
  selectedNodeId: null,
  selectedEdgeIds: [],
  zoomLevel: 1,
  viewport: { x: 0, y: 0 },
};

export const useGraphStore = create<GraphStore>((set) => ({
  ...initialState,

  setNodes: (nodes) => set({ nodes }),

  setEdges: (edges) => set({ edges }),

  addNode: (node) => set((state) => ({ nodes: [...state.nodes, node] })),

  updateNode: (nodeId, updates) =>
    set((state) => ({
      nodes: state.nodes.map((n) =>
        n.id === nodeId ? { ...n, ...updates } : n
      ),
    })),

  removeNode: (nodeId) =>
    set((state) => ({
      nodes: state.nodes.filter((n) => n.id !== nodeId),
      edges: state.edges.filter(
        (e) => e.source !== nodeId && e.target !== nodeId
      ),
      selectedNodeId: state.selectedNodeId === nodeId ? null : state.selectedNodeId,
    })),

  addEdge: (edge) => set((state) => ({ edges: [...state.edges, edge] })),

  removeEdge: (edgeId) =>
    set((state) => ({
      edges: state.edges.filter((e) => e.id !== edgeId),
      selectedEdgeIds: state.selectedEdgeIds.filter((id) => id !== edgeId),
    })),

  setSelectedNode: (nodeId) => set({ selectedNodeId: nodeId }),

  setSelectedEdges: (edgeIds) => set({ selectedEdgeIds: edgeIds }),

  setZoomLevel: (level) => set({ zoomLevel: level }),

  setViewport: (viewport) => set({ viewport }),

  reset: () => set(initialState),
}));

'use client';

import { useCallback, useEffect, useState } from 'react';
import type { Node, Edge } from 'reactflow';
import { useGraphStore } from '@/store/graph-store';
import { apiClient } from '@/services/api-client';

interface UseGraphReturn {
  nodes: Node[];
  edges: Edge[];
  isLoading: boolean;
  error: string | null;
  addNode: (node: Node) => void;
  updateNode: (nodeId: string, updates: Partial<Node>) => void;
  removeNode: (nodeId: string) => void;
  addEdge: (edge: Edge) => void;
  removeEdge: (edgeId: string) => void;
  getAncestors: (nodeId: string) => Node[];
  getDescendants: (nodeId: string) => Node[];
  getCausalPath: (fromNodeId: string, toNodeId: string) => Node[];
  applyLayout: (algorithm: 'hierarchical' | 'force' | 'radial') => void;
  fitView: () => void;
}

export function useGraph(sessionId: string): UseGraphReturn {
  const store = useGraphStore();
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!sessionId) return;
    setIsLoading(true);
    apiClient
      .get<{ nodes: Node[]; edges: Edge[] }>(`/sessions/${sessionId}/graph`)
      .then((data) => {
        store.setNodes(data.nodes);
        store.setEdges(data.edges);
        setError(null);
      })
      .catch((err) => {
        setError(err instanceof Error ? err.message : 'Failed to load graph');
      })
      .finally(() => setIsLoading(false));
  }, [sessionId, store]);

  const getAncestors = useCallback((nodeId: string): Node[] => {
    const result: Node[] = [];
    const visited = new Set<string>();
    const findParents = (id: string) => {
      const parentEdges = store.edges.filter((e) => e.target === id);
      for (const edge of parentEdges) {
        if (!visited.has(edge.source)) {
          visited.add(edge.source);
          const parent = store.nodes.find((n) => n.id === edge.source);
          if (parent) {
            result.push(parent);
            findParents(edge.source);
          }
        }
      }
    };
    findParents(nodeId);
    return result;
  }, [store.nodes, store.edges]);

  const getDescendants = useCallback((nodeId: string): Node[] => {
    const result: Node[] = [];
    const visited = new Set<string>();
    const findChildren = (id: string) => {
      const childEdges = store.edges.filter((e) => e.source === id);
      for (const edge of childEdges) {
        if (!visited.has(edge.target)) {
          visited.add(edge.target);
          const child = store.nodes.find((n) => n.id === edge.target);
          if (child) {
            result.push(child);
            findChildren(edge.target);
          }
        }
      }
    };
    findChildren(nodeId);
    return result;
  }, [store.nodes, store.edges]);

  const getCausalPath = useCallback((fromNodeId: string, toNodeId: string): Node[] => {
    const path: Node[] = [];
    const visited = new Set<string>();
    const dfs = (current: string): boolean => {
      if (current === toNodeId) return true;
      visited.add(current);
      const outEdges = store.edges.filter((e) => e.source === current);
      for (const edge of outEdges) {
        if (!visited.has(edge.target) && dfs(edge.target)) {
          const node = store.nodes.find((n) => n.id === edge.target);
          if (node) path.unshift(node);
          return true;
        }
      }
      return false;
    };
    if (dfs(fromNodeId)) {
      const startNode = store.nodes.find((n) => n.id === fromNodeId);
      if (startNode) path.unshift(startNode);
    }
    return path;
  }, [store.nodes, store.edges]);

  const applyLayout = useCallback((_algorithm: 'hierarchical' | 'force' | 'radial') => {
    // Layout algorithms would be implemented here
  }, []);

  const fitView = useCallback(() => {
    // Fit view would be triggered via React Flow ref
  }, []);

  return {
    nodes: store.nodes,
    edges: store.edges,
    isLoading,
    error,
    addNode: store.addNode,
    updateNode: store.updateNode,
    removeNode: store.removeNode,
    addEdge: store.addEdge,
    removeEdge: store.removeEdge,
    getAncestors,
    getDescendants,
    getCausalPath,
    applyLayout,
    fitView,
  };
}

export type { UseGraphReturn };

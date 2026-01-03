/**
 * Graph Store Tests
 *
 * Tests for Zustand graph store state management.
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { useGraphStore } from './graph-store';

describe('GraphStore', () => {
  beforeEach(() => {
    useGraphStore.getState().reset();
  });

  describe('Node Operations', () => {
    it('TC-ST001: should add node', () => {
      const node = {
        id: 'node-1',
        type: 'goal',
        position: { x: 0, y: 0 },
        data: { content: 'Test goal' },
      };

      useGraphStore.getState().addNode(node);

      const state = useGraphStore.getState();
      expect(state.nodes).toHaveLength(1);
      expect(state.nodes[0].id).toBe('node-1');
    });

    it('TC-ST002: should update node', () => {
      const node = {
        id: 'node-1',
        type: 'goal',
        position: { x: 0, y: 0 },
        data: { content: 'Test goal' },
      };

      useGraphStore.getState().addNode(node);
      useGraphStore.getState().updateNode('node-1', {
        data: { content: 'Updated goal' },
      });

      const state = useGraphStore.getState();
      expect(state.nodes[0].data.content).toBe('Updated goal');
    });

    it('TC-ST003: should remove node and cascade edges', () => {
      const node1 = {
        id: 'node-1',
        type: 'goal',
        position: { x: 0, y: 0 },
        data: {},
      };
      const node2 = {
        id: 'node-2',
        type: 'claim',
        position: { x: 100, y: 100 },
        data: {},
      };
      const edge = {
        id: 'edge-1',
        source: 'node-1',
        target: 'node-2',
      };

      useGraphStore.getState().addNode(node1);
      useGraphStore.getState().addNode(node2);
      useGraphStore.getState().addEdge(edge);

      expect(useGraphStore.getState().nodes).toHaveLength(2);
      expect(useGraphStore.getState().edges).toHaveLength(1);

      useGraphStore.getState().removeNode('node-1');

      const state = useGraphStore.getState();
      expect(state.nodes).toHaveLength(1);
      expect(state.edges).toHaveLength(0);
    });
  });

  describe('Edge Operations', () => {
    it('TC-ST004: should add edge', () => {
      const edge = {
        id: 'edge-1',
        source: 'node-1',
        target: 'node-2',
        type: 'support',
      };

      useGraphStore.getState().addEdge(edge);

      const state = useGraphStore.getState();
      expect(state.edges).toHaveLength(1);
      expect(state.edges[0].id).toBe('edge-1');
    });

    it('should remove edge', () => {
      const edge = {
        id: 'edge-1',
        source: 'node-1',
        target: 'node-2',
      };

      useGraphStore.getState().addEdge(edge);
      useGraphStore.getState().removeEdge('edge-1');

      const state = useGraphStore.getState();
      expect(state.edges).toHaveLength(0);
    });
  });

  describe('Selection', () => {
    it('TC-ST005: should set selected node', () => {
      useGraphStore.getState().setSelectedNode('node-1');

      const state = useGraphStore.getState();
      expect(state.selectedNodeId).toBe('node-1');
    });

    it('should clear selected node when node is removed', () => {
      const node = {
        id: 'node-1',
        type: 'goal',
        position: { x: 0, y: 0 },
        data: {},
      };

      useGraphStore.getState().addNode(node);
      useGraphStore.getState().setSelectedNode('node-1');
      useGraphStore.getState().removeNode('node-1');

      const state = useGraphStore.getState();
      expect(state.selectedNodeId).toBeNull();
    });
  });

  describe('Viewport', () => {
    it('should set zoom level', () => {
      useGraphStore.getState().setZoomLevel(1.5);

      const state = useGraphStore.getState();
      expect(state.zoomLevel).toBe(1.5);
    });

    it('should set viewport position', () => {
      useGraphStore.getState().setViewport({ x: 100, y: 200 });

      const state = useGraphStore.getState();
      expect(state.viewport).toEqual({ x: 100, y: 200 });
    });
  });

  describe('Reset', () => {
    it('TC-ST006: should reset state', () => {
      const node = {
        id: 'node-1',
        type: 'goal',
        position: { x: 0, y: 0 },
        data: {},
      };

      useGraphStore.getState().addNode(node);
      useGraphStore.getState().setSelectedNode('node-1');
      useGraphStore.getState().setZoomLevel(2);

      useGraphStore.getState().reset();

      const state = useGraphStore.getState();
      expect(state.nodes).toHaveLength(0);
      expect(state.edges).toHaveLength(0);
      expect(state.selectedNodeId).toBeNull();
      expect(state.zoomLevel).toBe(1);
    });
  });
});

'use client';

import { useEffect, useState, useCallback, useRef } from 'react';
import { SSEService, createSessionSSE, type SSEState } from '@/services/sse-service';

type SSEEventType =
  | 'agent_thinking'
  | 'reasoning_step'
  | 'node_preview'
  | 'node_finalized'
  | 'edge_preview'
  | 'edge_finalized'
  | 'phase_progress'
  | 'debate_round'
  | 'synthesis_started'
  | 'convergence_forced'
  | 'branch_lock_changed'
  | 'version_conflict'
  | 'error';

type SSEEventHandler<T = unknown> = (data: T) => void;
type SSEConnectionState = SSEState;

interface UseSSEReturn {
  connectionState: SSEConnectionState;
  error: string | null;
  subscribe: <T>(eventType: SSEEventType, handler: SSEEventHandler<T>) => () => void;
  reconnect: () => void;
  disconnect: () => void;
  lastEventId: string | null;
}

export function useSSE(
  sessionId: string,
  options?: {
    autoConnect?: boolean;
    reconnectDelay?: number;
    maxReconnectAttempts?: number;
  }
): UseSSEReturn {
  const [connectionState, setConnectionState] = useState<SSEConnectionState>('disconnected');
  const [error, setError] = useState<string | null>(null);
  const [lastEventId, setLastEventId] = useState<string | null>(null);
  const sseRef = useRef<SSEService | null>(null);

  const { autoConnect = true, reconnectDelay = 3000, maxReconnectAttempts = 10 } = options || {};

  useEffect(() => {
    if (!sessionId) return;

    const sse = createSessionSSE(sessionId, { reconnectDelay, maxReconnectAttempts });
    sseRef.current = sse;

    const unsubState = sse.onStateChange((state) => {
      setConnectionState(state);
      if (state === 'error') {
        setError('Connection error');
      } else if (state === 'connected') {
        setError(null);
      }
    });

    sse.subscribe('message', (event: MessageEvent) => {
      setLastEventId(sse.getLastEventId());
    });

    if (autoConnect) {
      sse.connect();
    }

    return () => {
      unsubState();
      sse.disconnect();
      sseRef.current = null;
    };
  }, [sessionId, autoConnect, reconnectDelay, maxReconnectAttempts]);

  const subscribe = useCallback(<T,>(eventType: SSEEventType, handler: SSEEventHandler<T>) => {
    if (!sseRef.current) return () => {};
    return sseRef.current.subscribe(eventType, (event: MessageEvent) => {
      try {
        const data = JSON.parse(event.data) as T;
        handler(data);
      } catch {
        handler(event.data as T);
      }
    });
  }, []);

  const reconnect = useCallback(() => {
    sseRef.current?.connect();
  }, []);

  const disconnect = useCallback(() => {
    sseRef.current?.disconnect();
  }, []);

  return { connectionState, error, subscribe, reconnect, disconnect, lastEventId };
}

export type { SSEEventType, SSEEventHandler, SSEConnectionState, UseSSEReturn };

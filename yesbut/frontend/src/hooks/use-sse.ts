/**
 * SSE Hook
 *
 * Custom React hook for managing Server-Sent Events connections.
 *
 * @module hooks/use-sse
 */

/**
 * SSE event types from the backend
 */
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

/**
 * SSE event handler type
 */
type SSEEventHandler<T = unknown> = (data: T) => void;

/**
 * SSE connection state
 */
type SSEConnectionState = 'connecting' | 'connected' | 'disconnected' | 'error';

/**
 * Return type for useSSE hook
 */
interface UseSSEReturn {
  /**
   * Current connection state
   */
  connectionState: SSEConnectionState;

  /**
   * Error message if connection failed
   */
  error: string | null;

  /**
   * Subscribe to a specific event type
   * @param eventType - The event type to subscribe to
   * @param handler - Callback function for the event
   * @returns Unsubscribe function
   */
  subscribe: <T>(eventType: SSEEventType, handler: SSEEventHandler<T>) => () => void;

  /**
   * Manually reconnect to the SSE stream
   */
  reconnect: () => void;

  /**
   * Disconnect from the SSE stream
   */
  disconnect: () => void;

  /**
   * Last event ID received (for reconnection)
   */
  lastEventId: string | null;
}

/**
 * Custom hook for SSE connection management
 *
 * Provides:
 * - Automatic connection to session SSE stream
 * - Event subscription/unsubscription
 * - Automatic reconnection on disconnect
 * - Connection state tracking
 * - Last event ID for resumption
 *
 * Events are parsed and dispatched to registered handlers.
 * The hook integrates with streaming-store for state updates.
 *
 * @param sessionId - The ID of the session to stream
 * @param options - Optional configuration
 * @returns SSE connection state and operations
 */
export function useSSE(
  sessionId: string,
  options?: {
    autoConnect?: boolean;
    reconnectDelay?: number;
    maxReconnectAttempts?: number;
  }
): UseSSEReturn {
  // TODO: Implement SSE hook with EventSource
  throw new Error('Not implemented');
}

/**
 * SSE Service
 */

interface SSEOptions {
  autoReconnect: boolean;
  reconnectDelay: number;
  maxReconnectAttempts: number;
  lastEventId?: string;
  headers?: Record<string, string>;
}

type SSEEventHandler = (event: MessageEvent) => void;
type SSEState = 'connecting' | 'connected' | 'disconnected' | 'error';

export class SSEService {
  private url: string;
  private options: SSEOptions;
  private eventSource: EventSource | null = null;
  private handlers: Map<string, Set<SSEEventHandler>> = new Map();
  private state: SSEState = 'disconnected';
  private reconnectAttempts: number = 0;
  private lastEventId: string | null = null;
  private stateChangeHandlers: Set<(state: SSEState) => void> = new Set();

  constructor(url: string, options?: Partial<SSEOptions>) {
    this.url = url;
    this.options = {
      autoReconnect: true,
      reconnectDelay: 3000,
      maxReconnectAttempts: 10,
      ...options,
    };
    if (options?.lastEventId) {
      this.lastEventId = options.lastEventId;
    }
  }

  connect(): void {
    if (this.eventSource) {
      this.disconnect();
    }

    this.setState('connecting');
    const url = this.lastEventId ? `${this.url}?lastEventId=${this.lastEventId}` : this.url;
    this.eventSource = new EventSource(url);

    this.eventSource.onopen = () => this.handleOpen();
    this.eventSource.onerror = (e) => this.handleError(e);
    this.eventSource.onmessage = (e) => this.handleMessage(e);
  }

  disconnect(): void {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
    this.setState('disconnected');
    this.reconnectAttempts = 0;
  }

  subscribe(eventType: string, handler: SSEEventHandler): () => void {
    if (!this.handlers.has(eventType)) {
      this.handlers.set(eventType, new Set());
      if (this.eventSource) {
        this.eventSource.addEventListener(eventType, handler as EventListener);
      }
    }
    this.handlers.get(eventType)!.add(handler);

    return () => this.unsubscribe(eventType, handler);
  }

  unsubscribe(eventType: string, handler: SSEEventHandler): void {
    const handlers = this.handlers.get(eventType);
    if (handlers) {
      handlers.delete(handler);
      if (handlers.size === 0) {
        this.handlers.delete(eventType);
      }
    }
  }

  onStateChange(handler: (state: SSEState) => void): () => void {
    this.stateChangeHandlers.add(handler);
    return () => this.stateChangeHandlers.delete(handler);
  }

  getState(): SSEState {
    return this.state;
  }

  getLastEventId(): string | null {
    return this.lastEventId;
  }

  private setState(state: SSEState): void {
    this.state = state;
    this.stateChangeHandlers.forEach((h) => h(state));
  }

  private handleOpen(): void {
    this.setState('connected');
    this.reconnectAttempts = 0;
  }

  private handleError(_error: Event): void {
    this.setState('error');
    if (this.options.autoReconnect && this.reconnectAttempts < this.options.maxReconnectAttempts) {
      this.attemptReconnect();
    }
  }

  private handleMessage(event: MessageEvent): void {
    if (event.lastEventId) {
      this.lastEventId = event.lastEventId;
    }
    const handlers = this.handlers.get('message');
    handlers?.forEach((h) => h(event));
  }

  private attemptReconnect(): void {
    this.reconnectAttempts++;
    setTimeout(() => {
      if (this.state !== 'connected') {
        this.connect();
      }
    }, this.options.reconnectDelay);
  }
}

export function createSessionSSE(sessionId: string, options?: Partial<SSEOptions>): SSEService {
  const url = `/api/v1/sessions/${sessionId}/stream`;
  return new SSEService(url, options);
}

export type { SSEOptions, SSEEventHandler, SSEState };

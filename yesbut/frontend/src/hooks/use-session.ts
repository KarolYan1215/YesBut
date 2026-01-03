'use client';

import { useState, useEffect, useCallback } from 'react';
import { apiClient } from '@/services/api-client';

interface Session {
  id: string;
  title: string;
  status: 'draft' | 'active' | 'paused' | 'completed';
  phase: 'divergence' | 'filtering' | 'convergence';
  mode: 'sync' | 'async';
  createdAt: string;
  updatedAt: string;
}

interface UseSessionReturn {
  session: Session | null;
  isLoading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
  updateSession: (updates: Partial<Session>) => Promise<void>;
  toggleMode: () => Promise<void>;
  pauseSession: () => Promise<void>;
  resumeSession: () => Promise<void>;
}

export function useSession(sessionId: string): UseSessionReturn {
  const [session, setSession] = useState<Session | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refetch = useCallback(async () => {
    if (!sessionId) return;
    setIsLoading(true);
    setError(null);
    try {
      const data = await apiClient.get<Session>(`/sessions/${sessionId}`);
      setSession(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch session');
    } finally {
      setIsLoading(false);
    }
  }, [sessionId]);

  useEffect(() => {
    refetch();
  }, [refetch]);

  const updateSession = useCallback(async (updates: Partial<Session>) => {
    if (!sessionId) return;
    try {
      const data = await apiClient.put<Session>(`/sessions/${sessionId}`, updates);
      setSession(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update session');
      throw err;
    }
  }, [sessionId]);

  const toggleMode = useCallback(async () => {
    if (!session) return;
    const newMode = session.mode === 'sync' ? 'async' : 'sync';
    await updateSession({ mode: newMode });
  }, [session, updateSession]);

  const pauseSession = useCallback(async () => {
    await updateSession({ status: 'paused' });
  }, [updateSession]);

  const resumeSession = useCallback(async () => {
    await updateSession({ status: 'active' });
  }, [updateSession]);

  return {
    session,
    isLoading,
    error,
    refetch,
    updateSession,
    toggleMode,
    pauseSession,
    resumeSession,
  };
}

export type { Session, UseSessionReturn };

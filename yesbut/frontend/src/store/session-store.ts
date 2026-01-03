/**
 * Session Store
 *
 * Zustand store for managing session state.
 *
 * @module store/session-store
 */

import { create } from 'zustand';

type SessionStatus = 'draft' | 'active' | 'paused' | 'completed' | 'failed';
type SessionPhase = 'divergence' | 'filtering' | 'convergence';
type SessionMode = 'sync' | 'async';

interface Session {
  id: string;
  title: string;
  description: string;
  status: SessionStatus;
  phase: SessionPhase;
  mode: SessionMode;
  phaseProgress: number;
  createdAt: string;
  updatedAt: string;
}

interface SessionStoreState {
  currentSession: Session | null;
  sessions: Session[];
  isLoading: boolean;
  error: string | null;
}

interface SessionStoreActions {
  setCurrentSession: (session: Session | null) => void;
  updateCurrentSession: (updates: Partial<Session>) => void;
  setSessions: (sessions: Session[]) => void;
  addSession: (session: Session) => void;
  removeSession: (sessionId: string) => void;
  setLoading: (isLoading: boolean) => void;
  setError: (error: string | null) => void;
  updatePhaseProgress: (progress: number) => void;
  transitionPhase: (phase: SessionPhase) => void;
  toggleMode: () => void;
  reset: () => void;
}

type SessionStore = SessionStoreState & SessionStoreActions;

const initialState: SessionStoreState = {
  currentSession: null,
  sessions: [],
  isLoading: false,
  error: null,
};

export const useSessionStore = create<SessionStore>((set) => ({
  ...initialState,

  setCurrentSession: (session) => set({ currentSession: session }),

  updateCurrentSession: (updates) =>
    set((state) => ({
      currentSession: state.currentSession
        ? { ...state.currentSession, ...updates, updatedAt: new Date().toISOString() }
        : null,
    })),

  setSessions: (sessions) => set({ sessions }),

  addSession: (session) =>
    set((state) => ({ sessions: [...state.sessions, session] })),

  removeSession: (sessionId) =>
    set((state) => ({
      sessions: state.sessions.filter((s) => s.id !== sessionId),
      currentSession:
        state.currentSession?.id === sessionId ? null : state.currentSession,
    })),

  setLoading: (isLoading) => set({ isLoading }),

  setError: (error) => set({ error }),

  updatePhaseProgress: (progress) =>
    set((state) => ({
      currentSession: state.currentSession
        ? { ...state.currentSession, phaseProgress: progress }
        : null,
    })),

  transitionPhase: (phase) =>
    set((state) => ({
      currentSession: state.currentSession
        ? { ...state.currentSession, phase, phaseProgress: 0 }
        : null,
    })),

  toggleMode: () =>
    set((state) => ({
      currentSession: state.currentSession
        ? {
            ...state.currentSession,
            mode: state.currentSession.mode === 'sync' ? 'async' : 'sync',
          }
        : null,
    })),

  reset: () => set(initialState),
}));

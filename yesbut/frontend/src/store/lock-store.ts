/**
 * Lock Store
 *
 * Zustand store for managing branch lock states.
 *
 * @module store/lock-store
 */

import { create } from 'zustand';

type LockState = 'EDITABLE' | 'OBSERVATION' | 'PAUSED';

interface BranchLock {
  branchId: string;
  state: LockState;
  lockingAgentId: string | null;
  lockingAgentName: string | null;
  lockingAgentType: string | null;
  lockedAt: string | null;
}

interface LockStoreState {
  branchLocks: Map<string, BranchLock>;
  currentBranchId: string | null;
  isCurrentBranchLocked: boolean;
  isInterrupting: boolean;
}

interface LockStoreActions {
  updateBranchLock: (branchId: string, lock: BranchLock) => void;
  setCurrentBranch: (branchId: string) => void;
  requestEditLock: (branchId: string) => Promise<boolean>;
  releaseEditLock: (branchId: string) => Promise<void>;
  triggerGlobalInterrupt: (sessionId: string) => Promise<void>;
  canEditBranch: (branchId: string) => boolean;
  reset: () => void;
}

type LockStore = LockStoreState & LockStoreActions;

const initialState: LockStoreState = {
  branchLocks: new Map(),
  currentBranchId: null,
  isCurrentBranchLocked: false,
  isInterrupting: false,
};

export const useLockStore = create<LockStore>((set, get) => ({
  ...initialState,

  updateBranchLock: (branchId, lock) =>
    set((state) => {
      const newMap = new Map(state.branchLocks);
      newMap.set(branchId, lock);
      const isCurrentLocked =
        state.currentBranchId === branchId && lock.state !== 'EDITABLE';
      return { branchLocks: newMap, isCurrentBranchLocked: isCurrentLocked };
    }),

  setCurrentBranch: (branchId) =>
    set((state) => {
      const lock = state.branchLocks.get(branchId);
      return {
        currentBranchId: branchId,
        isCurrentBranchLocked: lock ? lock.state !== 'EDITABLE' : false,
      };
    }),

  requestEditLock: async (branchId) => {
    const state = get();
    const lock = state.branchLocks.get(branchId);
    if (lock && lock.state !== 'EDITABLE') {
      return false;
    }
    set((s) => {
      const newMap = new Map(s.branchLocks);
      newMap.set(branchId, {
        branchId,
        state: 'EDITABLE',
        lockingAgentId: null,
        lockingAgentName: null,
        lockingAgentType: null,
        lockedAt: null,
      });
      return { branchLocks: newMap };
    });
    return true;
  },

  releaseEditLock: async (branchId) => {
    set((state) => {
      const newMap = new Map(state.branchLocks);
      const existing = newMap.get(branchId);
      if (existing) {
        newMap.set(branchId, { ...existing, state: 'EDITABLE' });
      }
      return { branchLocks: newMap };
    });
  },

  triggerGlobalInterrupt: async (sessionId) => {
    set({ isInterrupting: true });
    // API call would go here
    set((state) => {
      const newMap = new Map(state.branchLocks);
      newMap.forEach((lock, id) => {
        newMap.set(id, { ...lock, state: 'PAUSED' });
      });
      return { branchLocks: newMap, isInterrupting: false };
    });
  },

  canEditBranch: (branchId) => {
    const state = get();
    const lock = state.branchLocks.get(branchId);
    return !lock || lock.state === 'EDITABLE';
  },

  reset: () => set(initialState),
}));

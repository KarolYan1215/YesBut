/**
 * Lock Store
 *
 * Zustand store for managing branch lock states.
 *
 * @module store/lock-store
 */

/**
 * Lock state enumeration
 */
type LockState = 'EDITABLE' | 'OBSERVATION' | 'PAUSED';

/**
 * Branch lock information
 */
interface BranchLock {
  branchId: string;
  state: LockState;
  lockingAgentId: string | null;
  lockingAgentName: string | null;
  lockingAgentType: string | null;
  lockedAt: string | null;
}

/**
 * Lock store state interface
 */
interface LockStoreState {
  /**
   * Map of branch ID to lock information
   */
  branchLocks: Map<string, BranchLock>;

  /**
   * ID of the currently focused branch
   */
  currentBranchId: string | null;

  /**
   * Whether the current branch is locked
   */
  isCurrentBranchLocked: boolean;

  /**
   * Whether a global interrupt is in progress
   */
  isInterrupting: boolean;
}

/**
 * Lock store actions interface
 */
interface LockStoreActions {
  /**
   * Update lock state for a branch
   * @param branchId - ID of the branch
   * @param lock - Lock information
   */
  updateBranchLock: (branchId: string, lock: BranchLock) => void;

  /**
   * Set the current branch
   * @param branchId - ID of the branch to focus
   */
  setCurrentBranch: (branchId: string) => void;

  /**
   * Request edit lock for a branch
   * @param branchId - ID of the branch
   */
  requestEditLock: (branchId: string) => Promise<boolean>;

  /**
   * Release edit lock for a branch
   * @param branchId - ID of the branch
   */
  releaseEditLock: (branchId: string) => Promise<void>;

  /**
   * Trigger global interrupt
   * @param sessionId - ID of the session
   */
  triggerGlobalInterrupt: (sessionId: string) => Promise<void>;

  /**
   * Check if user can edit a specific branch
   * @param branchId - ID of the branch
   */
  canEditBranch: (branchId: string) => boolean;

  /**
   * Reset the store to initial state
   */
  reset: () => void;
}

/**
 * Combined lock store type
 */
type LockStore = LockStoreState & LockStoreActions;

/**
 * Create the lock store
 *
 * This Zustand store manages branch locking state:
 * - Tracks lock state for each branch (EDITABLE/OBSERVATION/PAUSED)
 * - Handles lock acquisition and release
 * - Manages global interrupt functionality
 *
 * Lock states:
 * - EDITABLE: User has full control, agents paused on this branch
 * - OBSERVATION: Agent working, user can only view + global interrupt
 * - PAUSED: User triggered pause, awaiting user decision
 *
 * The store is updated via SSE events (branch_lock_changed).
 *
 * @returns Zustand store hook
 */
export function createLockStore(): LockStore {
  // TODO: Implement Zustand store
  throw new Error('Not implemented');
}

/**
 * Lock store hook
 */
export const useLockStore = createLockStore;

/**
 * Observation Mode Overlay Component
 *
 * Semi-transparent overlay displayed when a branch is locked by an agent.
 * Prevents user editing while allowing observation and global interrupt.
 *
 * @module components/graph/observation-mode-overlay
 */

/**
 * Props interface for ObservationModeOverlay component
 */
interface ObservationModeOverlayProps {
  /**
   * Whether the overlay is visible (branch is locked)
   */
  visible: boolean;

  /**
   * Name of the agent currently holding the lock
   */
  agentName: string;

  /**
   * Type of the agent holding the lock
   */
  agentType: string;

  /**
   * Callback to trigger a global interrupt
   * This pauses all agent activity and returns control to the user
   */
  onGlobalInterrupt: () => void;

  /**
   * Whether a global interrupt is currently in progress
   */
  isInterrupting: boolean;
}

/**
 * Observation mode overlay component
 *
 * Displays when an agent has acquired a write lock on the current branch:
 * - Semi-transparent dark overlay
 * - Agent name and type indicator
 * - "Agent is working..." message
 * - Global Interrupt button (red, prominent)
 * - Explanation of what user can do in observation mode
 *
 * User actions allowed in observation mode:
 * - View graph, zoom, pan
 * - Read node details
 * - Send chat messages (queued)
 * - Trigger global interrupt
 *
 * User actions NOT allowed:
 * - Drag nodes
 * - Add/delete nodes or edges
 * - Modify constraints
 *
 * @param props - Component props
 * @returns The observation mode overlay JSX element
 */
export function ObservationModeOverlay(props: ObservationModeOverlayProps): JSX.Element {
  // TODO: Implement observation mode overlay
  // TODO: Add global interrupt button with confirmation
  throw new Error('Not implemented');
}

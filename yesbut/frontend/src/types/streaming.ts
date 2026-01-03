/**
 * Streaming Types
 *
 * TypeScript type definitions for SSE streaming events and agent activity.
 *
 * @module types/streaming
 */

import type { NodeType, EdgeType } from './graph';

/**
 * Agent type enumeration
 */
export type AgentType = 'RPA' | 'GEN' | 'ISA' | 'ACA' | 'BM' | 'GA' | 'UOA' | 'REC';

/**
 * Agent display names
 */
export const AGENT_NAMES: Record<AgentType, string> = {
  RPA: 'Requirement Parser',
  GEN: 'Generator',
  ISA: 'Information Scout',
  ACA: 'Audit & Compliance',
  BM: 'Branch Manager',
  GA: 'Game Arbiter',
  UOA: 'Utility Optimizer',
  REC: 'Reverse Compiler',
};

/**
 * Agent colors for UI
 */
export const AGENT_COLORS: Record<AgentType, string> = {
  RPA: 'bg-node-goal',
  GEN: 'bg-signal-info',
  ISA: 'bg-node-fact',
  ACA: 'bg-signal-warning',
  BM: 'bg-node-claim',
  GA: 'bg-node-synthesis',
  UOA: 'bg-node-constraint',
  REC: 'bg-ink-60',
};

/**
 * SSE event types
 */
export type SSEEventType =
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
 * Agent thinking event payload
 */
export interface AgentThinkingEvent {
  agent: AgentType;
  agentId: string;
  message: string;
}

/**
 * Reasoning step event payload
 */
export interface ReasoningStepEvent {
  agent: AgentType;
  agentId: string;
  step: string;
  reasoning: string;
}

/**
 * Node preview event payload
 */
export interface NodePreviewEvent {
  node: {
    id: string;
    type: NodeType;
    label: string;
    partialReasoning?: string;
  };
  confidence: 'low' | 'medium' | 'high';
  agentId: string;
  agentType: AgentType;
}

/**
 * Node finalized event payload
 */
export interface NodeFinalizedEvent {
  node: {
    id: string;
    type: NodeType;
    label: string;
    confidence: number;
    [key: string]: unknown;
  };
}

/**
 * Edge preview event payload
 */
export interface EdgePreviewEvent {
  edge: {
    id: string;
    sourceId: string;
    targetId: string;
    type: EdgeType;
  };
  agentId: string;
}

/**
 * Edge finalized event payload
 */
export interface EdgeFinalizedEvent {
  edge: {
    id: string;
    sourceId: string;
    targetId: string;
    type: EdgeType;
    weight: number;
    [key: string]: unknown;
  };
}

/**
 * Phase progress event payload
 */
export interface PhaseProgressEvent {
  phase: 'divergence' | 'filtering' | 'convergence';
  progress: number;
}

/**
 * Debate round event payload
 */
export interface DebateRoundEvent {
  round: number;
  branchA: string;
  branchB: string;
}

/**
 * Synthesis started event payload
 */
export interface SynthesisStartedEvent {
  branches: string[];
}

/**
 * Convergence forced event payload
 */
export interface ConvergenceForcedEvent {
  reason: 'max_rounds' | 'oscillation' | 'entropy_stagnation';
}

/**
 * Branch lock changed event payload
 */
export interface BranchLockChangedEvent {
  branchId: string;
  state: 'EDITABLE' | 'OBSERVATION' | 'PAUSED';
  agent: string | null;
}

/**
 * Version conflict event payload
 */
export interface VersionConflictEvent {
  nodeId: string;
  expected: number;
  actual: number;
}

/**
 * Error event payload
 */
export interface ErrorEvent {
  code: string;
  message: string;
}

/**
 * Agent activity entry for activity panel
 */
export interface AgentActivityEntry {
  id: string;
  agentId: string;
  agentType: AgentType;
  agentName: string;
  action: 'thinking' | 'reasoning' | 'creating_node' | 'creating_edge' | 'searching' | 'validating' | 'synthesizing';
  message: string;
  timestamp: string;
  isStreaming: boolean;
  partialContent?: string;
  nodeId?: string;
  edgeId?: string;
}

/**
 * Action display names
 */
export const ACTION_NAMES: Record<AgentActivityEntry['action'], string> = {
  thinking: 'Thinking...',
  reasoning: 'Reasoning',
  creating_node: 'Creating Node',
  creating_edge: 'Creating Edge',
  searching: 'Searching',
  validating: 'Validating',
  synthesizing: 'Synthesizing',
};

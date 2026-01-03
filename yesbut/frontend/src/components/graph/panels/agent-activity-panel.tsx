'use client';

import { memo, useEffect, useRef } from 'react';
import type { AgentActivityEntry, AgentType } from '@/types/streaming';
import { AGENT_NAMES, AGENT_COLORS, ACTION_NAMES } from '@/types/streaming';

interface AgentActivityPanelProps {
  activities: AgentActivityEntry[];
  activeAgentId: string | null;
  isOpen: boolean;
  onClose: () => void;
  onInterruptAgent: (agentId: string) => void;
  onGlobalInterrupt?: () => void;
  maxEntries?: number;
  isStreaming?: boolean;
  currentPhase?: 'divergence' | 'filtering' | 'convergence' | null;
  phaseProgress?: number;
}

function AgentAvatar({ agentType }: { agentType: AgentType }) {
  const colorClass = AGENT_COLORS[agentType] || 'bg-ink-40';
  const initials = agentType.slice(0, 2);

  return (
    <div className={`w-8 h-8 rounded-full ${colorClass} flex items-center justify-center`}>
      <span className="text-[10px] font-bold text-white">{initials}</span>
    </div>
  );
}

function ThinkingIndicator() {
  return (
    <div className="flex items-center gap-1">
      <span className="w-1.5 h-1.5 bg-ink-40 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
      <span className="w-1.5 h-1.5 bg-ink-40 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
      <span className="w-1.5 h-1.5 bg-ink-40 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
    </div>
  );
}

function PhaseProgressBar({ phase, progress }: { phase: string; progress: number }) {
  const phaseColors: Record<string, string> = {
    divergence: 'bg-signal-info',
    filtering: 'bg-signal-warning',
    convergence: 'bg-signal-success',
  };

  const phaseLabels: Record<string, string> = {
    divergence: 'Divergence',
    filtering: 'Filtering',
    convergence: 'Convergence',
  };

  return (
    <div className="px-4 py-2 border-b border-ink-10 bg-ink-05">
      <div className="flex items-center justify-between mb-1">
        <span className="text-xs font-medium text-ink-80">{phaseLabels[phase] || phase}</span>
        <span className="text-xs font-mono text-ink-60">{Math.round(progress * 100)}%</span>
      </div>
      <div className="h-1 bg-ink-10 rounded-full overflow-hidden">
        <div
          className={`h-full ${phaseColors[phase] || 'bg-ink-40'} rounded-full transition-all duration-300`}
          style={{ width: `${progress * 100}%` }}
        />
      </div>
    </div>
  );
}

function ActivityEntry({
  activity,
  isActive,
  onInterrupt,
}: {
  activity: AgentActivityEntry;
  isActive: boolean;
  onInterrupt: () => void;
}) {
  const agentName = AGENT_NAMES[activity.agentType] || activity.agentType;
  const actionLabel = ACTION_NAMES[activity.action] || activity.action;
  const colorClass = AGENT_COLORS[activity.agentType] || 'bg-ink-40';

  return (
    <div className={`px-4 py-3 border-b border-ink-05 ${isActive ? 'bg-ink-05' : ''}`}>
      <div className="flex items-start gap-3">
        <AgentAvatar agentType={activity.agentType} />
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-1">
            <div className="flex items-center gap-2">
              <span className="text-xs font-medium text-ink-100">{agentName}</span>
              <span className={`w-1.5 h-1.5 rounded-full ${colorClass}`} />
            </div>
            <span className="text-[10px] text-ink-40">{activity.timestamp}</span>
          </div>

          <div className="text-xs text-ink-40 mb-1">{actionLabel}</div>

          <p className="text-sm text-ink-80 break-words">{activity.message}</p>

          {activity.isStreaming && (
            <div className="mt-2 space-y-2">
              <div className="flex items-center gap-2">
                <ThinkingIndicator />
                <span className="text-xs text-ink-40">Processing...</span>
              </div>

              {activity.partialContent && (
                <div className="bg-ink-05 rounded p-2">
                  <p className="text-xs text-ink-60 italic line-clamp-3">{activity.partialContent}</p>
                </div>
              )}

              <button
                onClick={onInterrupt}
                className="text-[10px] px-2 py-1 text-signal-critical border border-signal-critical/30 rounded hover:bg-signal-critical/10 transition-colors"
              >
                Interrupt
              </button>
            </div>
          )}

          {activity.nodeId && (
            <div className="mt-1">
              <span className="text-[10px] text-ink-40">Node: </span>
              <span className="text-[10px] font-mono text-ink-60">{activity.nodeId.slice(0, 8)}...</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="flex-1 flex flex-col items-center justify-center p-8 text-center">
      <div className="w-12 h-12 rounded-full bg-ink-05 flex items-center justify-center mb-3">
        <svg className="w-6 h-6 text-ink-40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      <p className="text-sm text-ink-60 mb-1">No agent activity yet</p>
      <p className="text-xs text-ink-40">Agent activities will appear here as they work on your session</p>
    </div>
  );
}

function AgentActivityPanelComponent({
  activities,
  activeAgentId,
  isOpen,
  onClose,
  onInterruptAgent,
  onGlobalInterrupt,
  maxEntries = 50,
  isStreaming = false,
  currentPhase,
  phaseProgress = 0,
}: AgentActivityPanelProps): JSX.Element | null {
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new activities arrive
  useEffect(() => {
    if (scrollRef.current && activities.length > 0) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [activities.length]);

  if (!isOpen) return null;

  const displayedActivities = activities.slice(-maxEntries);
  const hasActiveAgent = activities.some((a) => a.isStreaming);

  return (
    <div className="w-80 bg-white border-l border-ink-20 h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-ink-10">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-ink-100">Agent Activity</span>
          {isStreaming && (
            <span className="w-2 h-2 rounded-full bg-signal-success animate-pulse" />
          )}
        </div>
        <button onClick={onClose} className="text-ink-40 hover:text-ink-80 transition-colors">
          <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
            <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z" />
          </svg>
        </button>
      </div>

      {/* Phase Progress */}
      {currentPhase && (
        <PhaseProgressBar phase={currentPhase} progress={phaseProgress} />
      )}

      {/* Activity List */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto">
        {displayedActivities.length === 0 ? (
          <EmptyState />
        ) : (
          displayedActivities.map((activity) => (
            <ActivityEntry
              key={activity.id}
              activity={activity}
              isActive={activity.agentId === activeAgentId}
              onInterrupt={() => onInterruptAgent(activity.agentId)}
            />
          ))
        )}
      </div>

      {/* Global Interrupt Button */}
      {hasActiveAgent && onGlobalInterrupt && (
        <div className="p-4 border-t border-ink-10">
          <button
            onClick={onGlobalInterrupt}
            className="w-full px-3 py-2 text-xs font-medium text-signal-critical border border-signal-critical/30 rounded hover:bg-signal-critical/10 transition-colors flex items-center justify-center gap-2"
          >
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 15h2v-2h-2v2zm0-4h2V7h-2v6z" />
            </svg>
            Global Interrupt
          </button>
        </div>
      )}

      {/* Activity Count */}
      <div className="px-4 py-2 border-t border-ink-10 bg-ink-05">
        <span className="text-[10px] text-ink-40">
          Showing {displayedActivities.length} of {activities.length} activities
        </span>
      </div>
    </div>
  );
}

export const AgentActivityPanel = memo(AgentActivityPanelComponent);

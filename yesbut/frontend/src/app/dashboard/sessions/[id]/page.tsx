'use client';

import { useState, useCallback, useEffect, useRef } from 'react';
import { useNodesState, useEdgesState, addEdge, type Connection } from 'reactflow';
import { GraphCanvas } from '@/components/graph/graph-canvas';
import { NodeDetailPanel } from '@/components/graph/panels/node-detail-panel';
import { AgentActivityPanel } from '@/components/graph/panels/agent-activity-panel';
import { ChatMessages, ChatInput, type Message, type SessionMode } from '@/components/chat';
import { useSession } from '@/hooks/use-session';
import { useGraph } from '@/hooks/use-graph';
import { useSSE } from '@/hooks/use-sse';
import { useStreamingStore } from '@/store/streaming-store';
import { useTranslation } from '@/i18n';
import type { AgentActivityEntry, AgentType } from '@/types/streaming';
import { AGENT_NAMES } from '@/types/streaming';

const IDLE_TIMEOUT = 30000;
const API_URL = 'http://localhost:8002/api/v1';

interface SessionDetailPageProps {
  params: { id: string };
}

export default function SessionDetailPage({ params }: SessionDetailPageProps): JSX.Element {
  const t = useTranslation();
  const { session, isLoading: sessionLoading } = useSession(params.id);
  const { nodes: initialNodes, edges: initialEdges, isLoading: graphLoading } = useGraph(params.id);
  const { connectionState, subscribe } = useSSE(params.id);

  // Streaming store
  const {
    activeAgentId,
    currentPhase,
    phaseProgress,
    isStreaming,
    setActiveAgent,
    updatePhaseProgress,
    setStreaming,
  } = useStreamingStore();

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [showActivityPanel, setShowActivityPanel] = useState(false);
  const [showGraph, setShowGraph] = useState(false);
  const [isLocked, setIsLocked] = useState(false);

  // Agent activities state
  const [activities, setActivities] = useState<AgentActivityEntry[]>([]);

  const [mode, setMode] = useState<SessionMode>('async');
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'system',
      content: t.sessions.goalPlaceholder,
      timestamp: new Date(),
    },
  ]);
  const [isProcessing, setIsProcessing] = useState(false);
  const idleTimerRef = useRef<NodeJS.Timeout | null>(null);

  // Subscribe to SSE events
  useEffect(() => {
    if (connectionState !== 'connected') return;

    // Agent thinking event
    const unsubThinking = subscribe<{ agent: AgentType; agentId: string; message: string }>(
      'agent_thinking',
      (data) => {
        setActiveAgent(data.agentId);
        setStreaming(true);
        const newActivity: AgentActivityEntry = {
          id: `${Date.now()}-${data.agentId}`,
          agentId: data.agentId,
          agentType: data.agent,
          agentName: AGENT_NAMES[data.agent] || data.agent,
          action: 'thinking',
          message: data.message,
          timestamp: new Date().toLocaleTimeString(),
          isStreaming: true,
        };
        setActivities((prev) => [...prev, newActivity]);
      }
    );

    // Reasoning step event
    const unsubReasoning = subscribe<{ agent: AgentType; agentId: string; step: string; reasoning: string }>(
      'reasoning_step',
      (data) => {
        const newActivity: AgentActivityEntry = {
          id: `${Date.now()}-${data.agentId}-reasoning`,
          agentId: data.agentId,
          agentType: data.agent,
          agentName: AGENT_NAMES[data.agent] || data.agent,
          action: 'reasoning',
          message: data.step,
          timestamp: new Date().toLocaleTimeString(),
          isStreaming: true,
          partialContent: data.reasoning,
        };
        setActivities((prev) => [...prev, newActivity]);
      }
    );

    // Node finalized event
    const unsubNodeFinalized = subscribe<{ node: { id: string; type: string; label: string; confidence: number } }>(
      'node_finalized',
      (data) => {
        // Update activities to mark streaming as complete
        setActivities((prev) =>
          prev.map((a) =>
            a.isStreaming && a.nodeId === data.node.id ? { ...a, isStreaming: false } : a
          )
        );
        // Add node to graph
        setNodes((nds) => [
          ...nds,
          {
            id: data.node.id,
            type: data.node.type,
            position: { x: Math.random() * 400, y: Math.random() * 400 },
            data: { ...data.node },
          },
        ]);
      }
    );

    // Phase progress event
    const unsubPhase = subscribe<{ phase: 'divergence' | 'filtering' | 'convergence'; progress: number }>(
      'phase_progress',
      (data) => {
        updatePhaseProgress(data.phase, data.progress);
      }
    );

    // Branch lock changed event
    const unsubLock = subscribe<{ branchId: string; state: string; agent: string | null }>(
      'branch_lock_changed',
      (data) => {
        setIsLocked(data.state === 'OBSERVATION');
      }
    );

    // Error event
    const unsubError = subscribe<{ code: string; message: string }>('error', (data) => {
      const errorActivity: AgentActivityEntry = {
        id: `${Date.now()}-error`,
        agentId: 'system',
        agentType: 'ACA',
        agentName: 'System',
        action: 'validating',
        message: `Error: ${data.message}`,
        timestamp: new Date().toLocaleTimeString(),
        isStreaming: false,
      };
      setActivities((prev) => [...prev, errorActivity]);
    });

    return () => {
      unsubThinking();
      unsubReasoning();
      unsubNodeFinalized();
      unsubPhase();
      unsubLock();
      unsubError();
    };
  }, [connectionState, subscribe, setActiveAgent, setStreaming, updatePhaseProgress, setNodes]);

  // Idle timer for mode switching
  useEffect(() => {
    const resetIdleTimer = () => {
      if (idleTimerRef.current) clearTimeout(idleTimerRef.current);
      if (mode === 'sync') {
        idleTimerRef.current = setTimeout(() => {
          setMode('async');
        }, IDLE_TIMEOUT);
      }
    };

    window.addEventListener('mousemove', resetIdleTimer);
    window.addEventListener('keydown', resetIdleTimer);

    return () => {
      if (idleTimerRef.current) clearTimeout(idleTimerRef.current);
      window.removeEventListener('mousemove', resetIdleTimer);
      window.removeEventListener('keydown', resetIdleTimer);
    };
  }, [mode]);

  const onConnect = useCallback(
    (connection: Connection) => {
      setEdges((eds) => addEdge(connection, eds));
    },
    [setEdges]
  );

  const handleSendMessage = async (content: string) => {
    setMode('sync');

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: new Date(),
      status: 'sending',
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsProcessing(true);

    try {
      const response = await fetch(`${API_URL}/chat/${params.id}/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: params.id,
          message: content,
          message_type: 'chat',
        }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const result = await response.json();

      if (result.success && result.data) {
        const assistantMessage: Message = {
          id: result.data.id || (Date.now() + 1).toString(),
          role: 'assistant',
          content: result.data.content,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, assistantMessage]);
      } else {
        throw new Error(result.detail || 'Unknown error');
      }
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'system',
        content: `Error: ${error instanceof Error ? error.message : 'Failed to get response'}`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleInterruptAgent = useCallback(async (agentId: string) => {
    try {
      await fetch(`${API_URL}/sessions/${params.id}/interrupt`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ agent_id: agentId }),
      });
      // Mark activity as not streaming
      setActivities((prev) =>
        prev.map((a) => (a.agentId === agentId ? { ...a, isStreaming: false } : a))
      );
    } catch (error) {
      console.error('Failed to interrupt agent:', error);
    }
  }, [params.id]);

  const handleGlobalInterrupt = useCallback(async () => {
    try {
      await fetch(`${API_URL}/sessions/${params.id}/global-interrupt`, {
        method: 'POST',
      });
      // Mark all activities as not streaming
      setActivities((prev) => prev.map((a) => ({ ...a, isStreaming: false })));
      setStreaming(false);
    } catch (error) {
      console.error('Failed to global interrupt:', error);
    }
  }, [params.id, setStreaming]);

  const handleEditNode = useCallback((nodeId: string) => {
    // TODO: Implement node editing dialog
    console.log('Edit node:', nodeId);
  }, []);

  const handleDeleteNode = useCallback(
    (nodeId: string) => {
      setNodes((nds) => nds.filter((n) => n.id !== nodeId));
      setEdges((eds) => eds.filter((e) => e.source !== nodeId && e.target !== nodeId));
      setSelectedNodeId(null);
    },
    [setNodes, setEdges]
  );

  if (sessionLoading || graphLoading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-sm text-ink-60">{t.common.loading}</div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="h-12 border-b border-ink-20 flex items-center justify-between px-4">
        <div className="flex items-center gap-3">
          <h1 className="text-sm font-medium text-ink-100">{session?.title || 'Untitled Session'}</h1>
          <span
            className={`text-xs px-2 py-0.5 rounded ${
              session?.phase === 'divergence'
                ? 'bg-signal-info/10 text-signal-info'
                : session?.phase === 'filtering'
                ? 'bg-signal-warning/10 text-signal-warning'
                : 'bg-signal-success/10 text-signal-success'
            }`}
          >
            {session?.phase}
          </span>
          <span
            className={`w-2 h-2 rounded-full ${
              connectionState === 'connected'
                ? 'bg-signal-success'
                : connectionState === 'connecting'
                ? 'bg-signal-warning animate-pulse'
                : 'bg-ink-40'
            }`}
          />
        </div>
        <div className="flex items-center gap-3">
          <span
            className={`text-xs px-2 py-1 rounded ${
              mode === 'sync' ? 'bg-signal-success/10 text-signal-success' : 'bg-ink-10 text-ink-60'
            }`}
          >
            {mode === 'sync' ? t.sessions.sync : t.sessions.async}
          </span>
          <button
            onClick={() => setShowGraph(!showGraph)}
            className={`px-3 py-1.5 text-xs rounded transition-colors ${
              showGraph ? 'bg-ink-100 text-white' : 'text-ink-60 hover:text-ink-100 hover:bg-ink-5'
            }`}
          >
            {t.graph.nodeDetails}
          </button>
          <button
            onClick={() => setShowActivityPanel(!showActivityPanel)}
            className={`px-3 py-1.5 text-xs rounded transition-colors ${
              showActivityPanel ? 'bg-ink-100 text-white' : 'text-ink-60 hover:text-ink-100 hover:bg-ink-5'
            }`}
          >
            {t.graph.agentActivity}
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Chat Panel */}
        <div className={`flex flex-col ${showGraph ? 'w-1/2 border-r border-ink-10' : 'flex-1'}`}>
          <ChatMessages messages={messages} isLoading={isProcessing} />
          <ChatInput onSend={handleSendMessage} disabled={isProcessing} />
        </div>

        {/* Graph Panel */}
        {showGraph && (
          <div className="w-1/2 flex flex-col">
            <GraphCanvas
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onConnect={onConnect}
              onNodeClick={setSelectedNodeId}
              isCurrentBranchLocked={isLocked}
            />
          </div>
        )}

        {/* Node Detail Panel */}
        {selectedNodeId && showGraph && (
          <NodeDetailPanel
            selectedNodeId={selectedNodeId}
            nodes={nodes}
            edges={edges}
            onClose={() => setSelectedNodeId(null)}
            isOpen={!!selectedNodeId}
            canEdit={!isLocked}
            onEditNode={handleEditNode}
            onDeleteNode={handleDeleteNode}
          />
        )}

        {/* Agent Activity Panel */}
        {showActivityPanel && (
          <AgentActivityPanel
            activities={activities}
            activeAgentId={activeAgentId}
            isOpen={showActivityPanel}
            onClose={() => setShowActivityPanel(false)}
            onInterruptAgent={handleInterruptAgent}
            onGlobalInterrupt={handleGlobalInterrupt}
            isStreaming={isStreaming}
            currentPhase={currentPhase}
            phaseProgress={phaseProgress}
          />
        )}
      </div>
    </div>
  );
}

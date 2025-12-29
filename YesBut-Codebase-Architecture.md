# YesBut MVP Codebase Architecture Design Document
## Multi-Agent Collaborative Brainstorming System - Web MVP

**Version**: 2.1  
**Last Updated**: 2025-12-29  
**Status**: Optimized based on critical review (race conditions, semantic entropy, path analysis)

---

## 1. Document Overview

### 1.1 Purpose
This document defines the complete codebase architecture for the YesBut Web MVP, a multi-agent collaborative brainstorming system based on the technical specification document (YesBut.md v1.0).

### 1.2 Scope
- Web-based MVP implementation
- Core three-phase pipeline (Divergence → Filtering → Convergence)
- 8 agent types orchestration
- Layered graph network visualization
- Synchronous/Asynchronous interaction modes
- MCP protocol integration for external data sources

### 1.3 Design Principles
1. **Separation of Concerns**: Clear boundaries between frontend, backend, and AI orchestration layers
2. **MVP-First Simplicity**: Minimize infrastructure complexity while preserving extensibility
3. **Type Safety**: Full TypeScript/Python type annotations
4. **Real-time with Streaming**: SSE/WebSocket for progressive updates during long-running agent tasks
5. **AI-First**: Optimized for LLM inference and multi-agent coordination
6. **Stability-Aware**: Inspired by structural mechanics, include sensitivity analysis for reasoning chains

### 1.4 Key Architecture Decisions (ADRs)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Graph Storage | PostgreSQL CTE over Neo4j | MVP simplicity; Neo4j deferred to post-MVP |
| Real-time Updates | SSE + WebSocket hybrid | SSE for streaming agent output; WebSocket for bidirectional sync mode |
| Agent Orchestration | LangGraph | Cyclic graphs for dialectical loops (Socratic questioning, synthesis) |
| Quantification | Semantic Anchoring with calibration | LLM scores need variance reduction and external benchmark calibration |
| Convergence Control | Step Counter + Semantic Entropy + Oscillation Detection | Prevent semantic deadlocks; entropy detects "paraphrasing without progress" |
| Race Condition Prevention | Redis Distributed Lock + Optimistic Version | Branch-level locking prevents state conflicts during agent streaming |
| Sensitivity Analysis | Single-node + Path Failure Analysis | Structural mechanics-inspired; identifies critical paths vs. redundant supports |

---

## 2. Technology Stack Selection

### 2.1 Frontend Stack

| Category | Technology | Version | Rationale |
|----------|------------|---------|-----------|
| Framework | Next.js | 14.x | SSR/SSG support, App Router, React Server Components |
| Language | TypeScript | 5.x | Type safety, better IDE support, reduced runtime errors |
| State Management | Zustand | 4.x | Lightweight, TypeScript-first, suitable for complex state |
| Graph Visualization | React Flow | 11.x | Purpose-built for node-based graphs, supports custom nodes |
| UI Components | shadcn/ui | latest | Headless components, Tailwind-based, highly customizable |
| Styling | Tailwind CSS | 3.x | Utility-first, rapid prototyping, consistent design |
| Real-time | Socket.io Client + EventSource | 4.x | WebSocket for sync mode, SSE for streaming agent output |
| HTTP Client | TanStack Query | 5.x | Caching, background sync, optimistic updates |
| Form Handling | React Hook Form + Zod | latest | Type-safe validation, performant |

### 2.2 Backend Stack

| Category | Technology | Version | Rationale |
|----------|------------|---------|-----------|
| Framework | FastAPI | 0.109.x | Async support, automatic OpenAPI docs, SSE native support |
| Language | Python | 3.11+ | AI/ML ecosystem, LangChain/LangGraph compatibility |
| Agent Orchestration | LangGraph | 0.0.x | State machine for multi-agent workflows, cyclic graph support |
| LLM Integration | LangChain | 0.1.x | Unified LLM interface, tool calling, structured output |
| Streaming | sse-starlette | 1.x | Server-Sent Events for progressive agent output |
| Task Queue | Celery | 5.x | Distributed task processing for async mode |
| Message Broker | Redis | 7.x | Pub/Sub for real-time, Celery broker, caching |
| WebSocket | python-socketio | 5.x | Bi-directional real-time communication |
| MCP Client | mcp-python | latest | Model Context Protocol integration |

### 2.3 Database Stack (MVP Simplified)

| Category | Technology | Version | Rationale |
|----------|------------|---------|-----------|
| Primary DB | PostgreSQL | 16.x | ACID compliance, JSONB for flexible schemas, CTE for graph traversal |
| Vector Extension | pgvector | 0.6.x | PostgreSQL extension, semantic search for novelty detection |
| Cache | Redis | 7.x | Session cache, real-time state, rate limiting |
| ORM | SQLAlchemy | 2.x | Async support, type hints, migration support |

> **Note**: Neo4j is deferred to post-MVP phase. PostgreSQL's recursive CTE (WITH RECURSIVE) handles layered graph traversal for depths ≤ 10 layers adequately. Neo4j will be introduced when:
> - Graph depth exceeds 10 layers consistently
> - Complex full-graph path analysis is required
> - Performance bottlenecks emerge in graph queries

### 2.4 Infrastructure & DevOps

| Category | Technology | Rationale |
|----------|------------|-----------|
| Containerization | Docker + Docker Compose | Consistent development environment |
| Reverse Proxy | Nginx | Static file serving, load balancing, SSE support |
| Process Manager | Uvicorn + Gunicorn | ASGI server for FastAPI |
| CI/CD | GitHub Actions | Automated testing and deployment |
| Monitoring | Prometheus + Grafana | Metrics collection and visualization |
| Logging | Structlog | Structured JSON logging |

---

## 3. System Architecture Diagram

### 3.1 Overall Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                        │
│  ┌─────────────────────────────────────────────────────────────────────────────┐│
│  │                         Next.js Frontend (SSR)                               ││
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          ││
│  │  │  Pages   │ │Components│ │  Hooks   │ │  Store   │ │ Services │          ││
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘          ││
│  └─────────────────────────────────────────────────────────────────────────────┘│
└───────────────────────────────────┬─────────────────────────────────────────────┘
                                    │ HTTP/SSE/WebSocket
┌───────────────────────────────────┼─────────────────────────────────────────────┐
│                              API GATEWAY LAYER                                   │
│  ┌────────────────────────────────┴────────────────────────────────────────────┐│
│  │                         FastAPI Application                                  ││
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          ││
│  │  │ Routers  │ │SSE Stream│ │  DTOs    │ │ Services │ │WebSocket │          ││
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘          ││
│  └─────────────────────────────────────────────────────────────────────────────┘│
└───────────────────────────────────┬─────────────────────────────────────────────┘
                                    │
┌───────────────────────────────────┼─────────────────────────────────────────────┐
│                           ORCHESTRATION LAYER                                    │
│  ┌────────────────────────────────┴────────────────────────────────────────────┐│
│  │                      LangGraph Agent Orchestrator                            ││
│  │  ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐    ││
│  │  │  RPA  │ │  GEN  │ │  ISA  │ │  ACA  │ │  BM   │ │  GA   │ │  UOA  │    ││
│  │  └───────┘ └───────┘ └───────┘ └───────┘ └───────┘ └───────┘ └───────┘    ││
│  │                                                              ┌───────┐      ││
│  │  ┌─────────────────────────────────────────────────────────┐ │  REC  │      ││
│  │  │            Convergence Controller (Step Counter)         │ └───────┘      ││
│  │  └─────────────────────────────────────────────────────────┘                ││
│  └─────────────────────────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────────────────────────┐│
│  │                          Celery Task Queue                                   ││
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐       ││
│  │  │ Async Tasks  │ │ Scheduled    │ │  Callbacks   │ │TextGrad Loop │       ││
│  │  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘       ││
│  └─────────────────────────────────────────────────────────────────────────────┘│
└───────────────────────────────────┬─────────────────────────────────────────────┘
                                    │
┌───────────────────────────────────┼─────────────────────────────────────────────┐
│                              DATA LAYER (MVP)                                    │
│  ┌────────────────────────┐ ┌──────────────┐ ┌──────────────┐                  │
│  │      PostgreSQL        │ │    Redis     │ │  MCP Servers │                  │
│  │  (Primary + pgvector)  │ │   (Cache)    │ │  (External)  │                  │
│  └────────────────────────┘ └──────────────┘ └──────────────┘                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Streaming Architecture for Sync Mode

The critical latency issue in synchronous mode (30-60s agent deliberation) is addressed via **progressive streaming**:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    STREAMING ARCHITECTURE (Sync Mode)                            │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  User Action                                                                     │
│       │                                                                          │
│       ▼                                                                          │
│  ┌─────────────┐   SSE Stream   ┌─────────────────────────────────────────────┐ │
│  │   Frontend  │◀──────────────│              FastAPI SSE Endpoint            │ │
│  │             │                │  GET /api/v1/sessions/{id}/stream            │ │
│  └─────────────┘                └─────────────────────────────────────────────┘ │
│       │                                      ▲                                   │
│       │                                      │ yield events                      │
│       │                         ┌────────────┴────────────────┐                 │
│       │                         │    LangGraph Orchestrator   │                 │
│       │                         │    (with streaming=True)    │                 │
│       │                         └────────────┬────────────────┘                 │
│       │                                      │                                   │
│       │              ┌───────────────────────┼───────────────────────┐          │
│       │              ▼                       ▼                       ▼          │
│       │         ┌─────────┐            ┌─────────┐            ┌─────────┐      │
│       │         │ Agent 1 │            │ Agent 2 │            │ Agent N │      │
│       │         │ thinking│────────────│ thinking│────────────│ thinking│      │
│       │         └─────────┘            └─────────┘            └─────────┘      │
│       │              │                       │                       │          │
│       │              └───────────────────────┼───────────────────────┘          │
│       │                                      │                                   │
│       │                                      ▼                                   │
│       │                              Stream Events:                              │
│       │                              - agent_thinking                            │
│       │                              - node_preview                              │
│       │                              - reasoning_step                            │
│       │                              - node_finalized                            │
│       │                              - phase_progress                            │
│       ▼                                                                          │
│  Real-time UI Updates:                                                           │
│  - Typing indicator for active agent                                             │
│  - Preview nodes (dashed border)                                                 │
│  - Reasoning trace in side panel                                                 │
│  - Progress bar for current phase                                                │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 3.3 State Synchronization Architecture

**Three-way state synchronization** between Frontend (Zustand), Backend (PostgreSQL), and Orchestrator (LangGraph), with **distributed locking** to prevent race conditions:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    STATE SYNCHRONIZATION STRATEGY                                │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐           │
│  │     Zustand     │     │   PostgreSQL    │     │    LangGraph    │           │
│  │  (UI State)     │     │ (Persistence)   │     │ (Agent State)   │           │
│  └────────┬────────┘     └────────┬────────┘     └────────┬────────┘           │
│           │                       │                       │                     │
│           │ Optimistic            │ Source of             │ Ephemeral           │
│           │ Updates               │ Truth                 │ Computation         │
│           │                       │                       │ State               │
│           └───────────────────────┼───────────────────────┘                     │
│                                   │                                              │
│                         ┌─────────┴─────────┐                                   │
│                         │   Redis Locks     │                                   │
│                         │ (Branch Control)  │                                   │
│                         └───────────────────┘                                   │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 3.4 Race Condition Prevention (Distributed Locking)

**Problem**: When an Agent is streaming `node_preview`, user modifications to constraints or node positions can cause state conflicts between LangGraph snapshots and PostgreSQL persistence.

**Solution**: Branch-level distributed locks with UI semi-lock mode.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    DISTRIBUTED LOCKING ARCHITECTURE                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  Lock Granularity: BRANCH-LEVEL                                                  │
│  ─────────────────────────────────                                               │
│  - Each branch has an independent lock                                           │
│  - Agents acquire lock before modifying branch                                   │
│  - Users cannot edit locked branches (observation mode only)                     │
│                                                                                  │
│  Lock Types:                                                                     │
│  ───────────                                                                     │
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐           │
│  │  AGENT_WRITE    │     │  USER_WRITE     │     │  GLOBAL_PAUSE   │           │
│  │  (exclusive)    │     │  (exclusive)    │     │  (exclusive)    │           │
│  └─────────────────┘     └─────────────────┘     └─────────────────┘           │
│                                                                                  │
│  UI Lock States:                                                                 │
│  ───────────────                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │ EDITABLE        │ Full user control, agents paused on this branch       │   │
│  │ OBSERVATION     │ Agent working, user can only view + global interrupt  │   │
│  │ PAUSED          │ User triggered pause, awaiting user decision          │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│  Optimistic Lock (Version Number):                                               │
│  ─────────────────────────────────                                               │
│  - Each node/edge has a `version` field                                          │
│  - Updates must include expected version                                         │
│  - Conflict → reject update, notify user                                         │
│                                                                                  │
│  User Actions in OBSERVATION Mode:                                               │
│  ─────────────────────────────────                                               │
│  ✓ View graph, zoom, pan                                                         │
│  ✓ Read node details                                                             │
│  ✓ Send chat messages (queued)                                                   │
│  ✓ Trigger GLOBAL INTERRUPT                                                      │
│  ✗ Drag nodes                                                                    │
│  ✗ Add/delete nodes or edges                                                     │
│  ✗ Modify constraints                                                            │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Directory Structure

```
yesbut/
├── README.md                           # Project overview and setup instructions
├── docker-compose.yml                  # Container orchestration configuration
├── docker-compose.dev.yml              # Development-specific overrides
├── .env.example                        # Environment variables template
├── .gitignore                          # Git ignore rules
├── Makefile                            # Common development commands
│
├── frontend/                           # Next.js Frontend Application
│   ├── package.json                    # Frontend dependencies
│   ├── package-lock.json               # Dependency lock file
│   ├── tsconfig.json                   # TypeScript configuration
│   ├── tailwind.config.ts              # Tailwind CSS configuration
│   ├── postcss.config.js               # PostCSS configuration
│   ├── next.config.js                  # Next.js configuration
│   ├── .eslintrc.json                  # ESLint rules
│   ├── .prettierrc                     # Prettier configuration
│   │
│   ├── public/                         # Static assets
│   │   ├── favicon.ico                 # Site favicon
│   │   ├── logo.svg                    # Application logo
│   │   └── fonts/                      # Custom fonts
│   │       └── inter-var.woff2         # Inter variable font
│   │
│   ├── src/
│   │   ├── app/                        # Next.js App Router
│   │   │   ├── layout.tsx              # Root layout with providers
│   │   │   ├── page.tsx                # Landing page
│   │   │   ├── globals.css             # Global styles
│   │   │   ├── loading.tsx             # Global loading state
│   │   │   ├── error.tsx               # Global error boundary
│   │   │   ├── not-found.tsx           # 404 page
│   │   │   │
│   │   │   ├── (auth)/                 # Auth route group
│   │   │   │   ├── login/
│   │   │   │   │   └── page.tsx        # Login page
│   │   │   │   └── register/
│   │   │   │       └── page.tsx        # Registration page
│   │   │   │
│   │   │   ├── dashboard/              # Main application dashboard
│   │   │   │   ├── layout.tsx          # Dashboard layout with sidebar
│   │   │   │   ├── page.tsx            # Dashboard overview
│   │   │   │   │
│   │   │   │   ├── sessions/           # Brainstorming sessions
│   │   │   │   │   ├── page.tsx        # Sessions list
│   │   │   │   │   ├── new/
│   │   │   │   │   │   └── page.tsx    # Create new session
│   │   │   │   │   └── [id]/
│   │   │   │   │       ├── page.tsx    # Session detail/canvas
│   │   │   │   │       ├── loading.tsx # Session loading state
│   │   │   │   │       └── graph/
│   │   │   │   │           └── page.tsx # Full graph view
│   │   │   │   │
│   │   │   │   └── settings/
│   │   │   │       └── page.tsx        # User settings
│   │   │   │
│   │   │   └── api/                    # API routes (BFF pattern)
│   │   │       └── [...proxy]/
│   │   │           └── route.ts        # Proxy to backend API
│   │   │
│   │   ├── components/                 # React Components
│   │   │   ├── ui/                     # Base UI components (shadcn/ui)
│   │   │   │   ├── button.tsx          # Button component
│   │   │   │   ├── card.tsx            # Card component
│   │   │   │   ├── dialog.tsx          # Dialog/Modal component
│   │   │   │   ├── dropdown-menu.tsx   # Dropdown menu
│   │   │   │   ├── input.tsx           # Input component
│   │   │   │   ├── textarea.tsx        # Textarea component
│   │   │   │   ├── select.tsx          # Select component
│   │   │   │   ├── tabs.tsx            # Tabs component
│   │   │   │   ├── toast.tsx           # Toast notifications
│   │   │   │   ├── tooltip.tsx         # Tooltip component
│   │   │   │   ├── slider.tsx          # Slider component
│   │   │   │   ├── badge.tsx           # Badge component
│   │   │   │   ├── progress.tsx        # Progress bar
│   │   │   │   ├── skeleton.tsx        # Loading skeleton
│   │   │   │   └── scroll-area.tsx     # Scrollable area
│   │   │   │
│   │   │   ├── layout/                 # Layout components
│   │   │   │   ├── header.tsx          # Application header
│   │   │   │   ├── sidebar.tsx         # Navigation sidebar
│   │   │   │   ├── footer.tsx          # Application footer
│   │   │   │   └── mobile-nav.tsx      # Mobile navigation
│   │   │   │
│   │   │   ├── graph/                  # Graph visualization components
│   │   │   │   ├── graph-canvas.tsx    # Main React Flow canvas (with lock-aware drag disable)
│   │   │   │   ├── graph-controls.tsx  # Zoom/pan controls
│   │   │   │   ├── graph-minimap.tsx   # Minimap navigation
│   │   │   │   ├── graph-toolbar.tsx   # Graph action toolbar
│   │   │   │   ├── graph-heatmap.tsx   # [NEW] Conflict/confidence heatmap overlay
│   │   │   │   ├── observation-mode-overlay.tsx # [NEW] Semi-transparent overlay when branch locked
│   │   │   │   │
│   │   │   │   ├── nodes/              # Custom node components
│   │   │   │   │   ├── base-node.tsx   # Base node wrapper
│   │   │   │   │   ├── goal-node.tsx   # GoalNode visualization
│   │   │   │   │   ├── claim-node.tsx  # ClaimNode visualization
│   │   │   │   │   ├── fact-node.tsx   # FactNode visualization
│   │   │   │   │   ├── constraint-node.tsx    # ConstraintNode visualization
│   │   │   │   │   ├── atomic-topic-node.tsx  # AtomicTopicNode visualization
│   │   │   │   │   ├── pending-node.tsx       # PendingNode visualization
│   │   │   │   │   ├── synthesis-node.tsx     # Synthesis node visualization
│   │   │   │   │   └── preview-node.tsx       # [NEW] Streaming preview node (dashed)
│   │   │   │   │
│   │   │   │   ├── edges/              # Custom edge components
│   │   │   │   │   ├── base-edge.tsx   # Base edge wrapper
│   │   │   │   │   ├── support-edge.tsx      # Support relationship
│   │   │   │   │   ├── attack-edge.tsx       # Attack relationship
│   │   │   │   │   ├── conflict-edge.tsx     # Conflict relationship
│   │   │   │   │   ├── entail-edge.tsx       # Entailment relationship
│   │   │   │   │   ├── decompose-edge.tsx    # Decomposition relationship
│   │   │   │   │   └── critical-edge.tsx     # [NEW] Dynamic thickness/style for path criticality
│   │   │   │   │
│   │   │   │   └── panels/             # Side panels for graph
│   │   │   │       ├── node-detail-panel.tsx   # Node details view
│   │   │   │       ├── branch-panel.tsx        # Branch management
│   │   │   │       ├── agent-activity-panel.tsx # Agent activity log with streaming
│   │   │   │       ├── evidence-panel.tsx      # Evidence/source panel
│   │   │   │       └── sensitivity-panel.tsx   # [NEW] Stability/sensitivity analysis
│   │   │   │
│   │   │   ├── session/                # Session-related components
│   │   │   │   ├── session-card.tsx    # Session list card
│   │   │   │   ├── session-header.tsx  # Session page header
│   │   │   │   ├── session-status.tsx  # Session status indicator
│   │   │   │   ├── phase-indicator.tsx # Three-phase progress
│   │   │   │   ├── mode-toggle.tsx     # Sync/Async mode toggle
│   │   │   │   ├── pending-decisions.tsx # Pending decision queue
│   │   │   │   └── streaming-indicator.tsx # [NEW] Agent thinking indicator
│   │   │   │
│   │   │   ├── input/                  # User input components
│   │   │   │   ├── requirement-input.tsx    # Initial requirement input
│   │   │   │   ├── constraint-input.tsx     # Constraint definition
│   │   │   │   ├── preference-wizard.tsx    # Preference elicitation wizard
│   │   │   │   └── chat-input.tsx           # Sync mode chat input
│   │   │   │
│   │   │   ├── agent/                  # Agent visualization
│   │   │   │   ├── agent-avatar.tsx    # Agent icon/avatar
│   │   │   │   ├── agent-message.tsx   # Agent message bubble (streaming)
│   │   │   │   ├── agent-status.tsx    # Agent activity status
│   │   │   │   └── agent-thinking.tsx  # [NEW] Typing/thinking animation
│   │   │   │
│   │   │   └── output/                 # Output components
│   │   │       ├── action-plan.tsx     # Executable plan display
│   │   │       ├── reasoning-trace.tsx # Reasoning chain viewer
│   │   │       ├── confidence-badge.tsx # Confidence indicator
│   │   │       └── export-dialog.tsx   # Export options dialog
│   │   │
│   │   ├── hooks/                      # Custom React hooks
│   │   │   ├── use-session.ts          # Session state management
│   │   │   ├── use-graph.ts            # Graph operations hook
│   │   │   ├── use-socket.ts           # WebSocket connection
│   │   │   ├── use-sse.ts              # [NEW] Server-Sent Events hook
│   │   │   ├── use-agents.ts           # Agent activity subscription
│   │   │   ├── use-streaming.ts        # [NEW] Streaming state management
│   │   │   ├── use-preferences.ts      # User preferences
│   │   │   └── use-debounce.ts         # Debounce utility hook
│   │   │
│   │   ├── store/                      # Zustand state stores
│   │   │   ├── index.ts                # Store exports
│   │   │   ├── session-store.ts        # Session state
│   │   │   ├── graph-store.ts          # Graph nodes/edges state
│   │   │   ├── streaming-store.ts      # [NEW] Streaming/preview state
│   │   │   ├── lock-store.ts           # [NEW] Branch lock state (EDITABLE/OBSERVATION/PAUSED)
│   │   │   ├── ui-store.ts             # UI state (panels, modals)
│   │   │   └── user-store.ts           # User/auth state
│   │   │
│   │   ├── services/                   # API service layer
│   │   │   ├── api-client.ts           # Axios instance configuration
│   │   │   ├── session-service.ts      # Session API calls
│   │   │   ├── graph-service.ts        # Graph API calls
│   │   │   ├── agent-service.ts        # Agent interaction API
│   │   │   ├── auth-service.ts         # Authentication API
│   │   │   ├── socket-service.ts       # WebSocket service
│   │   │   └── sse-service.ts          # [NEW] SSE streaming service
│   │   │
│   │   ├── lib/                        # Utility libraries
│   │   │   ├── utils.ts                # General utilities
│   │   │   ├── cn.ts                   # Class name merger
│   │   │   ├── graph-utils.ts          # Graph manipulation utilities
│   │   │   ├── layout-utils.ts         # Graph layout algorithms
│   │   │   ├── heatmap-utils.ts        # [NEW] Heatmap calculation utilities
│   │   │   ├── path-utils.ts           # [NEW] Path criticality visualization helpers
│   │   │   └── validation.ts           # Zod schemas
│   │   │
│   │   └── types/                      # TypeScript type definitions
│   │       ├── index.ts                # Type exports
│   │       ├── session.ts              # Session types
│   │       ├── graph.ts                # Graph node/edge types
│   │       ├── agent.ts                # Agent types
│   │       ├── streaming.ts            # [NEW] Streaming event types
│   │       ├── api.ts                  # API response types
│   │       └── socket.ts               # WebSocket event types
│   │
│   └── tests/                          # Frontend tests
│       ├── setup.ts                    # Test configuration
│       ├── components/                 # Component tests
│       └── hooks/                      # Hook tests
│
├── backend/                            # FastAPI Backend Application
│   ├── pyproject.toml                  # Python project configuration
│   ├── poetry.lock                     # Dependency lock file
│   ├── alembic.ini                     # Database migration configuration
│   ├── pytest.ini                      # Test configuration
│   ├── .env.example                    # Environment template
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                     # FastAPI application entry point
│   │   ├── config.py                   # Application configuration
│   │   ├── dependencies.py             # Dependency injection
│   │   │
│   │   ├── api/                        # API layer
│   │   │   ├── __init__.py
│   │   │   ├── router.py               # Main API router aggregation
│   │   │   │
│   │   │   ├── v1/                     # API version 1
│   │   │   │   ├── __init__.py
│   │   │   │   ├── sessions.py         # Session CRUD endpoints
│   │   │   │   ├── graph.py            # Graph manipulation endpoints
│   │   │   │   ├── nodes.py            # Node CRUD endpoints
│   │   │   │   ├── edges.py            # Edge CRUD endpoints
│   │   │   │   ├── branches.py         # Branch management endpoints
│   │   │   │   ├── agents.py           # Agent interaction endpoints
│   │   │   │   ├── preferences.py      # Preference elicitation endpoints
│   │   │   │   ├── output.py           # Output compilation endpoints
│   │   │   │   ├── sensitivity.py      # [NEW] Sensitivity analysis endpoints
│   │   │   │   └── auth.py             # Authentication endpoints
│   │   │   │
│   │   │   ├── streaming/              # [NEW] SSE streaming handlers
│   │   │   │   ├── __init__.py
│   │   │   │   ├── session_stream.py   # Session SSE endpoint
│   │   │   │   └── events.py           # SSE event definitions
│   │   │   │
│   │   │   └── websocket/              # WebSocket handlers
│   │   │       ├── __init__.py
│   │   │       ├── manager.py          # Connection manager
│   │   │       ├── session_ws.py       # Session real-time updates
│   │   │       └── events.py           # WebSocket event definitions
│   │   │
│   │   ├── models/                     # Database models (SQLAlchemy)
│   │   │   ├── __init__.py
│   │   │   ├── base.py                 # Base model class
│   │   │   ├── user.py                 # User model
│   │   │   ├── session.py              # Session model
│   │   │   ├── node.py                 # Node model
│   │   │   ├── edge.py                 # Edge model
│   │   │   ├── hyperedge.py            # Hyperedge model
│   │   │   ├── branch.py               # Branch model
│   │   │   ├── utility_function.py     # Utility function model
│   │   │   ├── feature_archive.py      # [NEW] QD feature archive model
│   │   │   ├── pending_decision.py     # Pending decision model
│   │   │   ├── agent_log.py            # Agent activity log model
│   │   │   └── prompt_version.py       # [NEW] TextGrad prompt version model
│   │   │
│   │   ├── schemas/                    # Pydantic schemas (DTOs)
│   │   │   ├── __init__.py
│   │   │   ├── base.py                 # Base schema
│   │   │   ├── user.py                 # User schemas
│   │   │   ├── session.py              # Session schemas
│   │   │   ├── node.py                 # Node schemas
│   │   │   ├── edge.py                 # Edge schemas
│   │   │   ├── branch.py               # Branch schemas
│   │   │   ├── graph.py                # Graph aggregate schemas
│   │   │   ├── preference.py           # Preference schemas
│   │   │   ├── output.py               # Output schemas
│   │   │   ├── agent.py                # Agent activity schemas
│   │   │   ├── feature_space.py        # [NEW] QD feature space schemas
│   │   │   ├── sensitivity.py          # [NEW] Sensitivity analysis schemas
│   │   │   └── streaming.py            # [NEW] SSE event schemas
│   │   │
│   │   ├── services/                   # Business logic services
│   │   │   ├── __init__.py
│   │   │   ├── session_service.py      # Session management
│   │   │   ├── graph_service.py        # Graph operations (PostgreSQL CTE)
│   │   │   ├── node_service.py         # Node CRUD operations
│   │   │   ├── edge_service.py         # Edge CRUD operations
│   │   │   ├── branch_service.py       # Branch management
│   │   │   ├── lock_service.py         # [NEW] Redis-based distributed locking
│   │   │   ├── preference_service.py   # Preference elicitation logic
│   │   │   ├── output_service.py       # Output compilation
│   │   │   ├── auth_service.py         # Authentication logic
│   │   │   ├── sensitivity_service.py  # [NEW] Sensitivity analysis logic
│   │   │   └── feature_archive_service.py # [NEW] QD archive management
│   │   │
│   │   ├── core/                       # Core utilities
│   │   │   ├── __init__.py
│   │   │   ├── security.py             # JWT, password hashing
│   │   │   ├── exceptions.py           # Custom exceptions
│   │   │   └── logging.py              # Structured logging setup
│   │   │
│   │   └── db/                         # Database utilities
│   │       ├── __init__.py
│   │       ├── session.py              # SQLAlchemy session factory
│   │       ├── graph_queries.py        # [NEW] PostgreSQL CTE graph queries
│   │       └── redis.py                # Redis connection
│   │
│   ├── agents/                         # Multi-Agent Orchestration Layer
│   │   ├── __init__.py
│   │   ├── orchestrator.py             # LangGraph main orchestrator
│   │   ├── state.py                    # Agent state definitions
│   │   ├── streaming.py                # [NEW] Streaming callback handlers
│   │   ├── convergence_controller.py   # [NEW] Step counter & oscillation detection
│   │   │
│   │   ├── base/                       # Base agent classes
│   │   │   ├── __init__.py
│   │   │   ├── agent.py                # Base agent class (with streaming)
│   │   │   ├── prompts.py              # Base prompt templates
│   │   │   └── tools.py                # Base tool definitions
│   │   │
│   │   ├── rpa/                        # Requirement Parsing Agent
│   │   │   ├── __init__.py
│   │   │   ├── agent.py                # RPA implementation
│   │   │   ├── prompts.py              # RPA prompts
│   │   │   └── tools.py                # Parsing tools
│   │   │
│   │   ├── gen/                        # Generator Agent (Divergence)
│   │   │   ├── __init__.py
│   │   │   ├── agent.py                # GEN implementation
│   │   │   ├── prompts.py              # Generation prompts
│   │   │   ├── strategies.py           # QD generation strategies
│   │   │   └── feature_space.py        # [NEW] Feature space definition & archiving
│   │   │
│   │   ├── isa/                        # Information Scout Agent
│   │   │   ├── __init__.py
│   │   │   ├── agent.py                # ISA implementation
│   │   │   ├── prompts.py              # Search prompts
│   │   │   ├── tools.py                # MCP tool wrappers
│   │   │   └── semantic_entropy.py     # Semantic entropy calculation
│   │   │
│   │   ├── aca/                        # Audit & Compliance Agent
│   │   │   ├── __init__.py
│   │   │   ├── agent.py                # ACA implementation
│   │   │   ├── prompts.py              # Audit prompts
│   │   │   └── validators.py           # Consistency validators
│   │   │
│   │   ├── bm/                         # Branch Manager Agent
│   │   │   ├── __init__.py
│   │   │   ├── agent.py                # BM implementation
│   │   │   ├── prompts.py              # Reasoning prompts
│   │   │   ├── socratic.py             # Socratic questioning
│   │   │   └── synthesis.py            # Hegelian synthesis
│   │   │
│   │   ├── ga/                         # Game Arbiter Agent
│   │   │   ├── __init__.py
│   │   │   ├── agent.py                # GA implementation
│   │   │   ├── prompts.py              # Arbitration prompts
│   │   │   ├── scheduler.py            # qEHVI resource scheduler
│   │   │   ├── equilibrium.py          # Nash equilibrium solver
│   │   │   └── oscillation_detector.py # [NEW] Semantic oscillation detection
│   │   │
│   │   ├── uoa/                        # Utility Optimization Agent
│   │   │   ├── __init__.py
│   │   │   ├── agent.py                # UOA implementation
│   │   │   ├── prompts.py              # Utility prompts
│   │   │   ├── elicitation.py          # Bayesian preference elicitation
│   │   │   ├── quantification.py       # Semantic anchoring quantification
│   │   │   └── variance_reduction.py   # [NEW] LLM score variance reduction
│   │   │
│   │   └── rec/                        # Reverse Engineering Compiler
│   │       ├── __init__.py
│   │       ├── agent.py                # REC implementation
│   │       ├── prompts.py              # Compilation prompts
│   │       └── templates.py            # Output templates
│   │
│   ├── algorithms/                     # Core algorithms
│   │   ├── __init__.py
│   │   ├── shapley.py                  # Shapley value calculation
│   │   ├── pareto.py                   # Pareto optimization
│   │   ├── qehvi.py                    # qEHVI implementation
│   │   ├── pruning.py                  # Node pruning strategies
│   │   ├── deadlock.py                 # Graph-level deadlock detection
│   │   ├── oscillation.py              # [NEW] Semantic entropy + similarity oscillation detection
│   │   ├── sensitivity.py              # [NEW] Single-node sensitivity analysis
│   │   ├── path_analysis.py            # [NEW] Path failure analysis, minimal cut sets
│   │   └── layout.py                   # Graph layout algorithms
│   │
│   ├── optimization/                   # [NEW] TextGrad optimization module
│   │   ├── __init__.py
│   │   ├── textgrad_loop.py            # TextGrad optimization loop
│   │   ├── loss_functions.py           # Composite loss function
│   │   ├── gradient_aggregator.py      # Batch gradient aggregation
│   │   ├── attribution.py              # Shapley-based attribution routing
│   │   └── version_control.py          # Prompt version management
│   │
│   ├── mcp/                            # MCP Protocol Integration
│   │   ├── __init__.py
│   │   ├── client.py                   # MCP client wrapper
│   │   ├── servers/                    # MCP server configurations
│   │   │   ├── __init__.py
│   │   │   ├── tavily.py               # Tavily search integration
│   │   │   ├── firecrawl.py            # Firecrawl integration
│   │   │   ├── brave.py                # Brave search integration
│   │   │   └── playwright.py           # Playwright integration
│   │   └── tools.py                    # MCP tool definitions
│   │
│   ├── tasks/                          # Celery async tasks
│   │   ├── __init__.py
│   │   ├── celery_app.py               # Celery configuration
│   │   ├── session_tasks.py            # Session processing tasks
│   │   ├── agent_tasks.py              # Agent execution tasks
│   │   ├── search_tasks.py             # Information retrieval tasks
│   │   ├── optimization_tasks.py       # [NEW] TextGrad optimization tasks
│   │   └── cleanup_tasks.py            # Maintenance tasks
│   │
│   ├── migrations/                     # Alembic migrations
│   │   ├── env.py                      # Migration environment
│   │   ├── script.py.mako              # Migration template
│   │   └── versions/                   # Migration files
│   │       └── 001_initial.py          # Initial schema
│   │
│   └── tests/                          # Backend tests
│       ├── __init__.py
│       ├── conftest.py                 # Test fixtures
│       ├── test_api/                   # API endpoint tests
│       ├── test_services/              # Service layer tests
│       ├── test_agents/                # Agent tests
│       └── test_algorithms/            # Algorithm tests
│
├── docker/                             # Docker configurations
│   ├── frontend/
│   │   └── Dockerfile                  # Frontend container
│   ├── backend/
│   │   └── Dockerfile                  # Backend container
│   ├── nginx/
│   │   ├── Dockerfile                  # Nginx container
│   │   └── nginx.conf                  # Nginx configuration (SSE support)
│   └── celery/
│       └── Dockerfile                  # Celery worker container
│
├── scripts/                            # Utility scripts
│   ├── setup-dev.sh                    # Development setup script
│   ├── seed-db.py                      # Database seeding
│   ├── run-migrations.sh               # Run database migrations
│   └── generate-types.ts               # Generate TypeScript types from API
│
└── docs/                               # Documentation
    ├── api/                            # API documentation
    │   └── openapi.yaml                # OpenAPI specification
    ├── architecture/                   # Architecture docs
    │   ├── decisions/                  # Architecture Decision Records
    │   └── streaming-design.md         # [NEW] Streaming architecture details
    └── guides/                         # Developer guides
        ├── setup.md                    # Setup guide
        ├── contributing.md             # Contribution guide
        └── deployment.md               # Deployment guide
```

---

## 5. Critical Design Specifications

### 5.1 QD Feature Space and Archive (Divergence Phase)

The Quality-Diversity (QD) algorithm requires an explicit **feature space** and **archive** mechanism.

**Key Files**:

| File | Function |
|------|----------|
| `backend/agents/gen/feature_space.py` | Defines multi-dimensional feature space (risk_level, innovation_degree, implementation_time, resource_requirement), each dimension with configurable bins. Implements MAP-Elites style archive for storing best solutions per cell. |
| `backend/app/models/feature_archive.py` | SQLAlchemy model storing archive entries with cell_index (ARRAY), solution_node_id, quality_score, and feature_vector (JSONB). Unique constraint per session+cell. |
| `backend/app/services/feature_archive_service.py` | CRUD operations for archive, coverage map generation for visualization, archive pruning strategies. |

### 5.2 Semantic-to-Scalar Quantification (UOA)

The UOA agent must convert LLM semantic assessments to numerical values with variance reduction.

**Key Files**:

| File | Function |
|------|----------|
| `backend/agents/uoa/quantification.py` | SemanticAnchor class for converting LLM descriptions to scalars via pairwise comparison against predefined anchors. Uses Bradley-Terry model for interpolation. |
| `backend/agents/uoa/variance_reduction.py` | VarianceReducer class that applies calibration corrections to raw LLM scores. Fits correction model from calibration dataset. |
| `backend/agents/uoa/elicitation.py` | Bayesian preference elicitation logic for active user preference learning. |

### 5.3 Convergence Control and Oscillation Detection

The GA agent includes a **step counter**, **semantic oscillation detector**, and **semantic entropy monitor** to prevent infinite debate loops.

**Critical Insight**: Simple embedding similarity (threshold 0.85) can be fooled by LLM's "paraphrasing without progress" behavior. We combine two signals:

1. **Embedding Similarity**: Detects surface-level position repetition
2. **Semantic Entropy**: Detects lack of substantive information gain

**Forced Synthesis Triggers**:
- Max debate rounds exceeded (default: 10)
- Position similarity > 0.85 for alternating rounds (A → B → A' where sim(A, A') > threshold)
- Semantic entropy not decreasing for 3 consecutive rounds (stagnation)

**Key Files**:

| File | Function |
|------|----------|
| `backend/agents/convergence_controller.py` | Main controller with round counter, position history tracking, and multi-signal synthesis trigger logic. |
| `backend/agents/ga/oscillation_detector.py` | Embedding-based oscillation detection (similarity threshold configurable). |
| `backend/algorithms/oscillation.py` | Semantic entropy calculation for debate progress measurement. Tracks entropy delta across rounds. If entropy fails to decrease by threshold (default: 0.1) for 3 rounds, triggers forced synthesis. |
| `backend/agents/isa/semantic_entropy.py` | Core semantic entropy calculation using multiple LLM samples to estimate output uncertainty. Reused by oscillation detector. |

### 5.4 Sensitivity Analysis (Stability)

Inspired by structural mechanics, analyze how node and **path** invalidation affects the overall reasoning structure.

**Critical Insight**: In non-linear logic chains, single-node failure may be compensated by redundant branches (analogous to statically indeterminate structures in mechanics). We must identify:

1. **Statically Determinate Core** (必经路径): Paths where every node is critical; any failure collapses the conclusion
2. **Redundant Support** (冗余支撑): Alternative paths that can compensate for localized failures

**Structural Analogy**:
```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  REASONING GRAPH STABILITY CLASSIFICATION                                        │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │ STATICALLY DETERMINATE (Critical Path)                                   │   │
│  │ ─────────────────────────────────────                                    │   │
│  │ - Single path from root to leaf                                          │   │
│  │ - Any node failure → utility collapse                                    │   │
│  │ - UI: Thick, solid edges (RED warning if low confidence)                │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │ STATICALLY INDETERMINATE (Redundant Support)                             │   │
│  │ ─────────────────────────────────────────                                │   │
│  │ - Multiple paths support same conclusion                                  │   │
│  │ - Single node failure → redistributed load to alternatives               │   │
│  │ - UI: Thin, dashed edges (GREEN if healthy redundancy)                   │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │ PATH FAILURE ANALYSIS                                                     │   │
│  │ ─────────────────────                                                     │   │
│  │ - Identify minimal cut sets (smallest set of nodes whose failure         │   │
│  │   disconnects root from goal)                                             │   │
│  │ - Compute path redundancy ratio = |alternative paths| / |critical paths| │   │
│  │ - Flag conclusions with redundancy ratio < 1.0 as structurally fragile   │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

**Key Files**:

| File | Function |
|------|----------|
| `backend/algorithms/sensitivity.py` | Core sensitivity analyzer with Monte Carlo perturbation. Computes single-node sensitivity scores and collapse thresholds. |
| `backend/algorithms/path_analysis.py` | [NEW] Path failure analysis module. Identifies statically determinate cores (critical paths) and redundant supports. Computes minimal cut sets using graph algorithms. |
| `backend/app/services/sensitivity_service.py` | Business logic for sensitivity analysis. Orchestrates node and path analysis, generates stability reports for frontend. |
| `backend/app/schemas/sensitivity.py` | Pydantic schemas for SensitivityReport, PathAnalysisResult, CriticalPath, RedundancyMetrics. |
| `frontend/src/components/graph/panels/sensitivity-panel.tsx` | UI panel showing critical nodes, collapse boundaries, and interactive "what-if" simulator. |
| `frontend/src/lib/heatmap-utils.ts` | Calculates edge thickness/color based on path criticality (thick=critical, thin=redundant). |

### 5.5 PostgreSQL Graph Queries (CTE)

Replace Neo4j with PostgreSQL recursive CTE for MVP. Supports graph traversal for depths ≤ 10 layers.

**Key Files**:

| File | Function |
|------|----------|
| `backend/app/db/graph_queries.py` | GraphQueryService class with PostgreSQL CTE-based traversal: `get_ancestors()` (recursive parent lookup), `get_causal_path()` (path finding between nodes), `detect_cycles()` (cycle detection for deadlock prevention), `get_descendants()` (recursive child lookup). Max depth configurable, default 10. |
| `backend/app/services/graph_service.py` | Higher-level graph operations using GraphQueryService. Handles node/edge CRUD with version conflict detection. |

### 5.6 TextGrad Optimization Loop

Incremental prompt optimization triggered after sessions complete (offline, not real-time).

**Agent Classification**:
- **Frozen** (never optimize): ACA, GA, RPA - critical for system consistency
- **Optimizable** (primary targets): BM, REC - benefit most from prompt tuning
- **Limited** (query strategies only): ISA - only optimize search query formulation

**Optimization Workflow**:
1. Aggregate feedback from completed session batch (min batch size required)
2. Filter for actionable feedback (80%+ agreement on issue type)
3. Compute text gradients for optimizable agents
4. Apply trust-region constrained updates (max 20% change)
5. Validate on gold test set
6. Commit new version or rollback

**Key Files**:

| File | Function |
|------|----------|
| `backend/optimization/textgrad_loop.py` | Main optimization loop orchestrator. Implements batch aggregation, gradient computation, trust-region updates, and rollback logic. |
| `backend/optimization/loss_functions.py` | Composite loss function combining user satisfaction, reasoning quality, and output completeness metrics. |
| `backend/optimization/gradient_aggregator.py` | Aggregates text gradients from multiple sessions, filters noise, identifies consistent improvement directions. |
| `backend/optimization/attribution.py` | Shapley-based attribution routing to identify which agent's prompt contributed to success/failure. |
| `backend/optimization/version_control.py` | Prompt version management with git-like history. Supports rollback to previous versions. |
| `backend/app/models/prompt_version.py` | SQLAlchemy model for storing prompt versions with metadata (agent_type, version_number, content, metrics, created_at). |
| `backend/tasks/optimization_tasks.py` | Celery task for scheduled optimization cycles (e.g., every N sessions or nightly). |

### 5.7 Distributed Locking for Race Condition Prevention

**Problem**: Three-way state synchronization (Zustand ↔ PostgreSQL ↔ LangGraph) creates race conditions when agents stream updates while users attempt edits.

**Solution**: Redis-based branch-level locking with optimistic version numbers.

**Key Files**:

| File | Function |
|------|----------|
| `backend/app/services/lock_service.py` | BranchLockService class with Redis-based distributed locking. Implements `acquire_agent_lock()`, `release_lock()`, `check_user_can_edit()`. Lock TTL with auto-release if agent crashes. Uses Lua scripts for atomic compare-and-delete. |
| `backend/app/models/node.py` | Node model with `version` field for optimistic locking. Updates must include expected version; conflicts trigger rejection and user notification. |
| `frontend/src/store/lock-store.ts` | Zustand store tracking branch lock states (EDITABLE/OBSERVATION/PAUSED). Updates via SSE when lock state changes. |
| `frontend/src/components/graph/observation-mode-overlay.tsx` | Semi-transparent overlay displayed when branch is locked. Shows locking agent name and provides "Global Interrupt" button. |
| `frontend/src/components/graph/graph-canvas.tsx` | React Flow canvas with `nodesDraggable` and `nodesConnectable` bound to lock state. Disables editing when `isCurrentBranchLocked=true`. |

---

## 6. Streaming Event Specifications

### 6.1 SSE Event Types

| Event Type | Payload | Description |
|------------|---------|-------------|
| `agent_thinking` | `{ agent: string, message: string }` | Agent is processing, show typing indicator |
| `reasoning_step` | `{ agent: string, step: string, reasoning: string }` | Intermediate reasoning visible to user |
| `node_preview` | `{ node: PartialNode, confidence: "low" }` | Preview node before finalization |
| `node_finalized` | `{ node: Node }` | Node confirmed and persisted |
| `edge_preview` | `{ edge: PartialEdge }` | Preview edge during reasoning |
| `edge_finalized` | `{ edge: Edge }` | Edge confirmed and persisted |
| `phase_progress` | `{ phase: string, progress: float }` | Current phase completion percentage |
| `debate_round` | `{ round: int, branch_a: string, branch_b: string }` | Debate round notification |
| `synthesis_started` | `{ branches: string[] }` | Hegelian synthesis initiated |
| `convergence_forced` | `{ reason: string }` | Forced convergence (max_rounds/oscillation/entropy_stagnation) |
| `branch_lock_changed` | `{ branch_id: string, state: string, agent: string }` | [NEW] Branch lock state change notification |
| `version_conflict` | `{ node_id: string, expected: int, actual: int }` | [NEW] Optimistic lock conflict detected |
| `error` | `{ code: string, message: string }` | Error during processing |

### 6.2 SSE Endpoint

**Key Files**:

| File | Function |
|------|----------|
| `backend/app/api/streaming/session_stream.py` | SSE endpoint `GET /sessions/{session_id}/stream`. Yields events from LangGraph orchestrator with event type, JSON payload, and event ID. Requires authentication. |
| `backend/app/api/streaming/events.py` | SSE event type definitions and payload schemas. |
| `frontend/src/hooks/use-sse.ts` | React hook for SSE connection management. Handles reconnection, event parsing, and store updates. |
| `frontend/src/services/sse-service.ts` | Low-level SSE service with EventSource wrapper. |

---

## 7. Updated API Specifications

### 7.1 New Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/sessions/{id}/stream` | SSE stream for real-time updates |
| GET | `/api/v1/sessions/{id}/sensitivity` | Get single-node sensitivity analysis |
| GET | `/api/v1/sessions/{id}/path-analysis` | [NEW] Get path failure analysis (critical paths, minimal cut sets) |
| GET | `/api/v1/sessions/{id}/feature-archive` | Get QD feature archive |
| GET | `/api/v1/sessions/{id}/convergence-status` | Get debate round counter, entropy history, oscillation status |
| GET | `/api/v1/branches/{id}/lock-status` | [NEW] Get current lock state for branch |
| POST | `/api/v1/branches/{id}/request-lock` | [NEW] Request edit lock for branch |
| DELETE | `/api/v1/branches/{id}/lock` | [NEW] Release user-held lock |
| POST | `/api/v1/admin/optimization/trigger` | Manually trigger TextGrad optimization |

### 7.2 WebSocket Events (Updated)

| Event | Payload | Description |
|-------|---------|-------------|
| `user_message` | `{ content: string, type: string }` | User input in sync mode (queued if branch locked) |
| `force_synthesis` | `{ branch_ids: string[] }` | User forces synthesis |
| `interrupt_agent` | `{ agent: string }` | User interrupts agent processing |
| `global_interrupt` | `{ session_id: string }` | [NEW] User triggers global interrupt from OBSERVATION mode |
| `request_edit_lock` | `{ branch_id: string }` | [NEW] User requests edit control of branch |

---

## 8. Visualization Enhancements

### 8.1 Conflict Heatmap Layer

**Modes**: conflict (edge attack intensity), confidence (node confidence distribution), sensitivity (node criticality)

**Key Files**:

| File | Function |
|------|----------|
| `frontend/src/components/graph/graph-heatmap.tsx` | HeatmapOverlay component with mode switching. Computes heatmap data based on mode and renders semi-transparent overlay on React Flow canvas. |
| `frontend/src/lib/heatmap-utils.ts` | Utility functions: `computeConflictIntensity()`, `computeConfidenceDistribution()`, `computeSensitivityMap()`, `getColorScale()`. |

### 8.2 Sensitivity Panel

**Features**: Critical nodes list, collapse boundary chart, interactive "what-if" impact simulator

**Key Files**:

| File | Function |
|------|----------|
| `frontend/src/components/graph/panels/sensitivity-panel.tsx` | Panel component displaying stability analysis. Fetches sensitivity report via TanStack Query. Contains CriticalNodesSection, CollapseBoundaryChart, ImpactSimulator sub-components. |
| `frontend/src/components/graph/panels/critical-nodes-section.tsx` | Lists top-k critical nodes with sensitivity scores and visual indicators. |
| `frontend/src/components/graph/panels/impact-simulator.tsx` | Interactive widget to preview utility change when adjusting node confidence. |

### 8.3 Path Criticality Visualization

**Visual Encoding**:
- **Critical paths** (statically determinate): Thick solid edges, RED if low confidence
- **Redundant paths** (statically indeterminate): Thin dashed edges, GREEN if healthy redundancy
- **Minimal cut set nodes**: Highlighted with warning badge

**Key Files**:

| File | Function |
|------|----------|
| `frontend/src/components/graph/edges/critical-edge.tsx` | [NEW] Edge component with dynamic thickness/style based on path criticality. |
| `frontend/src/lib/path-utils.ts` | [NEW] Client-side utilities for path classification data parsing and visual encoding. |

---

## 9. Development Environment Setup (Updated)

### 9.1 Prerequisites

- Node.js 20.x
- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 16 with pgvector (via Docker)
- Redis 7.x (via Docker)

### 9.2 Quick Start

```bash
# Clone repository
git clone https://github.com/your-org/yesbut.git
cd yesbut

# Setup environment
cp .env.example .env
# Edit .env with your API keys (LLM providers, MCP servers)

# Start infrastructure (simplified: no Neo4j in MVP)
docker-compose up -d postgres redis

# Setup backend
cd backend
poetry install
poetry run alembic upgrade head
poetry run uvicorn app.main:app --reload

# Setup frontend (new terminal)
cd frontend
npm install
npm run dev

# Start Celery worker (new terminal)
cd backend
poetry run celery -A tasks.celery_app worker --loglevel=info
```

---

## 10. Post-MVP Roadmap

| Phase | Addition | Trigger Condition |
|-------|----------|-------------------|
| MVP+1 | Neo4j integration | Graph depth > 10 or complex path analysis needed |
| MVP+2 | RFLP-style REC output | User demand for physical constraint mapping |
| MVP+3 | Distributed LangGraph | >1000 concurrent sessions |
| MVP+4 | Fine-tuned embedding model | Novelty detection accuracy < 80% |

---

## 11. References

- [YesBut Technical Specification v1.0](./YesBut.md)
- [Next.js Documentation](https://nextjs.org/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [React Flow Documentation](https://reactflow.dev/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Semantic Entropy Paper](https://arxiv.org/abs/2302.09664)
- [TextGrad Paper](https://arxiv.org/abs/2406.07496)
- [MAP-Elites Paper](https://arxiv.org/abs/1504.04909)

---

**Document Version**: 2.1  
**Last Updated**: 2025-12-29  
**Status**: Optimized based on critical review (race conditions, semantic entropy, path analysis)  
**Author**: YesBut Architecture Team

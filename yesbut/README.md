# YesBut

Multi-Agent Collaborative Brainstorming System based on N-Player Game Theory and Layered Graph Networks.

## Overview

YesBut is a multi-agent collaborative brainstorming system that transforms unstructured ideas into structured, executable solutions through a three-phase pipeline: **Divergence - Filtering - Convergence**.

### Core Concepts

- **Quality-Diversity Exploration**: MAP-Elites inspired approach to explore solution space across multiple feature dimensions
- **Layered Graph Network**: Vertical tree decomposition + horizontal graph associations for deep progressive reasoning
- **N-Player Non-Cooperative Game**: Each branch represents an independent viewpoint with heterogeneous utility functions
- **Bidirectional Derivation**: Top-down deduction + bottom-up induction forming logical closure
- **Semantic Entropy Verification**: NLI-based uncertainty detection for LLM outputs
- **Bayesian Preference Elicitation**: Active learning of user preferences through information gain maximization

### Three-Phase Pipeline

```
Divergence Phase (GEN) --> Filtering Phase (ACA + UOA) --> Convergence Phase (BM + GA)
        |                           |                              |
   50-200 solutions            5-15 candidates              Final executable plan
```

---

## UI Architecture

### Design Philosophy: Scientific Minimalism

YesBut adopts a **Scientific Minimalism** design approach inspired by academic paper typography, laboratory data visualization, and modern code editors.

**Design DNA**:
- **Typography-First**: Information hierarchy through font weight, size, and line height
- **Monochrome Depth**: Grayscale layers create spatial depth
- **Precision Rendering**: Clear boundaries, no blurry decorations
- **Data Density**: Every pixel conveys value
- **Quiet Motion**: Animations only when necessary (150-300ms)

### Session Workspace Layout (Lab Workspace Pattern)

```
+-----------------------------------------------------------------------------+
| HEADER (48px)                                                                |
| [Logo] [Session Title] [o Diverge --*-- Filter --o-- Converge] [Mode] [User]|
+----------+--------------------------------------------------+---------------+
| SIDEBAR  |                                                  |    PANEL      |
| (240px)  |              GRAPH CANVAS                        |    (320px)    |
|          |             (React Flow)                         |               |
| Sessions |                                                  |   [Tabs]      |
| Branches |         +----------+                             |   Node        |
| Agents   |         |   GOAL   |                             |   Evidence    |
|          |         +----+-----+                             |   Trace       |
|          |              |                                   |   Sensitivity |
|          |        +-----+-----+                             |               |
|          |        v           v                             |               |
|          |    +------+    +------+                          |               |
|          |    |Claim |---→|Claim |                          |               |
|          |    +------+    +------+                          |               |
+----------+--------------------------------------------------+---------------+
| FOOTER (40px)                                                                |
| [Chat Input - Sync Mode Only] | Status | Zoom Controls                      |
+-----------------------------------------------------------------------------+
```

### User Flow

```
Landing Page (/)
    |
    v
Dashboard (/dashboard)
    |
    +-- New Session (/dashboard/sessions/new)
    |       |
    |       v
    |   [Step 1: Requirement Input]
    |       |
    |       v
    |   [Step 2: Preference Elicitation]
    |       |
    |       v
    |   [Step 3: Constraint Definition]
    |       |
    |       v
    |   [Step 4: Mode Selection]
    |       |
    |       v
    +-- Session Detail (/dashboard/sessions/[id])
            |
            +-- Divergence View (feature space, solutions)
            |
            +-- Filtering View (Pareto front, candidates)
            |
            +-- Convergence View (graph canvas, debate)
            |
            +-- Output View (action plan, export)
```

### Design Principles

1. **Minimalist**: Clean, no visual clutter
2. **Phase-Aware**: UI adapts to current brainstorming phase
3. **Progressive Disclosure**: Show complexity only when needed
4. **Real-time Feedback**: Streaming updates during agent work
5. **Desktop-First**: Optimized for large screen graph visualization

### Color System

| Category | Color | Usage |
|----------|-------|-------|
| Diverge Phase | `#8B5CF6` (Purple) | Exploration, generation |
| Filter Phase | `#F59E0B` (Orange) | Selection, evaluation |
| Converge Phase | `#10B981` (Green) | Synthesis, consensus |
| Goal Node | `#6366F1` (Indigo) | Root objectives |
| Claim Node | `#8B5CF6` (Purple) | Agent reasoning |
| Fact Node | `#3B82F6` (Blue) | Verified facts |
| Constraint Node | `#EF4444` (Red) | User constraints |
| Support Edge | `#22C55E` (Green) | Positive evidence |
| Attack Edge | `#EF4444` (Red) | Negative evidence |

### Ink Color Palette (Monochrome Depth)

```css
--ink-100: #0A0A0B;  /* Primary text */
--ink-80: #27272A;   /* Secondary text */
--ink-60: #52525B;   /* Auxiliary text */
--ink-40: #A1A1AA;   /* Placeholder */
--ink-20: #D4D4D8;   /* Border */
--ink-10: #E4E4E7;   /* Divider */
--ink-05: #F4F4F5;   /* Light background */
--paper: #FAFAFA;    /* Page background */
```

---

## Frontend Component Architecture

### Component Hierarchy

```
src/components/
+-- ui/                    # Base UI primitives (shadcn/ui style)
|   +-- button.tsx         [IMPLEMENTED] Primary/secondary/ghost buttons
|   +-- card.tsx           [IMPLEMENTED] Content cards
|   +-- badge.tsx          [IMPLEMENTED] Status badges
|   +-- progress.tsx       [IMPLEMENTED] Progress bars
|   +-- tooltip.tsx        [IMPLEMENTED] Tooltips
|   +-- dialog.tsx         [IMPLEMENTED] Modal dialogs
|   +-- input.tsx          [IMPLEMENTED] Text inputs
|   +-- textarea.tsx       [IMPLEMENTED] Text areas
|   +-- tabs.tsx           [STUB] Tab navigation
|   +-- slider.tsx         [STUB] Range slider
|   +-- dropdown.tsx       [NOT IMPLEMENTED] Dropdown menu
|   +-- skeleton.tsx       [NOT IMPLEMENTED] Loading skeleton
|
+-- layout/                # Layout components
|   +-- header.tsx         [STUB] App header with phase indicator
|   +-- sidebar.tsx        [STUB] Navigation sidebar
|   +-- footer.tsx         [NOT IMPLEMENTED] Footer with chat input
|
+-- input/                 # User input components
|   +-- requirement-input.tsx    [STUB] Initial idea input
|   +-- preference-wizard.tsx    [IMPLEMENTED] Preference elicitation
|   +-- constraint-editor.tsx    [STUB] Constraint management
|   +-- chat-input.tsx           [NOT IMPLEMENTED] Sync mode chat
|
+-- session/               # Session components
|   +-- session-card.tsx   [STUB] Session list item
|   +-- phase-indicator.tsx [IMPLEMENTED] Three-phase progress
|   +-- view-toggle.tsx    [STUB] Causal/Conflict toggle
|   +-- mode-toggle.tsx    [NOT IMPLEMENTED] Sync/Async toggle
|
+-- graph/                 # Graph visualization (React Flow)
|   +-- graph-canvas.tsx   [STUB] Main canvas - CRITICAL
|   +-- graph-controls.tsx [STUB] Zoom/pan controls
|   +-- graph-heatmap.tsx  [STUB] Conflict/confidence heatmap
|   +-- observation-mode-overlay.tsx [STUB] Lock overlay
|   |
|   +-- nodes/             # 9 node types
|   |   +-- base-node.tsx        [STUB] Base wrapper (280px width)
|   |   +-- goal-node.tsx        [STUB] GoalNode (#6366F1)
|   |   +-- claim-node.tsx       [STUB] ClaimNode (#8B5CF6)
|   |   +-- fact-node.tsx        [STUB] FactNode (#3B82F6)
|   |   +-- constraint-node.tsx  [STUB] ConstraintNode (#EF4444)
|   |   +-- atomic-topic-node.tsx [STUB] AtomicTopicNode (#14B8A6)
|   |   +-- pending-node.tsx     [STUB] PendingNode (#9CA3AF)
|   |   +-- preview-node.tsx     [STUB] PreviewNode (dashed)
|   |   +-- synthesis-node.tsx   [STUB] SynthesisNode (#F59E0B)
|   |
|   +-- edges/             # 7 edge types
|   |   +-- base-edge.tsx        [STUB] Base edge wrapper
|   |   +-- support-edge.tsx     [STUB] Support (green, 1.5px)
|   |   +-- attack-edge.tsx      [STUB] Attack (red, 2px)
|   |   +-- conflict-edge.tsx    [STUB] Conflict (orange, dashed)
|   |   +-- entail-edge.tsx      [STUB] Entail (gray, 1px)
|   |   +-- decompose-edge.tsx   [STUB] Decompose (purple, 1px)
|   |   +-- critical-edge.tsx    [STUB] Critical (black, 3px)
|   |
|   +-- panels/            # Side panels
|       +-- node-detail-panel.tsx    [STUB] Node details/editing
|       +-- agent-activity-panel.tsx [STUB] Agent activity feed
|       +-- branch-panel.tsx         [STUB] Branch management
|       +-- sensitivity-panel.tsx    [STUB] Stability analysis
|
+-- agent/                 # Agent components
|   +-- agent-avatar.tsx   [NOT IMPLEMENTED] Agent icons
|   +-- agent-status.tsx   [NOT IMPLEMENTED] Activity status
|
+-- output/                # Output components
    +-- action-plan.tsx    [NOT IMPLEMENTED] Plan display
    +-- export-dialog.tsx  [NOT IMPLEMENTED] Export options
```

### State Management (Zustand Stores)

```
src/store/
+-- graph-store.ts         [STUB] Graph state
|   +-- nodes: Node[]
|   +-- edges: Edge[]
|   +-- selectedNodeId: string | null
|   +-- viewport: { x, y, zoom }
|   +-- CRUD operations
|
+-- session-store.ts       [STUB] Session state
|   +-- currentSession: Session | null
|   +-- sessions: Session[]
|   +-- phase: 'divergence' | 'filtering' | 'convergence'
|   +-- mode: 'sync' | 'async'
|   +-- progress: number
|
+-- streaming-store.ts     [STUB] Real-time state
|   +-- previewNodes: PreviewNode[]
|   +-- previewEdges: PreviewEdge[]
|   +-- activeAgentId: string | null
|   +-- phaseProgress: number
|
+-- lock-store.ts          [STUB] Lock state
    +-- branchLocks: Map<string, LockState>
    +-- isCurrentBranchLocked: boolean
    +-- lockingAgentId: string | null
```

### Services Layer

```
src/services/
+-- api-client.ts          [STUB] Axios instance with auth
+-- sse-service.ts         [STUB] Server-Sent Events
+-- socket-service.ts      [NOT IMPLEMENTED] WebSocket for sync mode
```

---

## Implementation Status

### Fully Implemented
- [x] Type definitions (`types/graph.ts`)
- [x] Design tokens (`globals.css`, `tailwind.config.ts`)
- [x] Phase indicator component
- [x] Preference wizard component
- [x] Basic UI components (button, card, badge, progress, input)

### Stub Only (Need Implementation)
- [ ] All 4 Zustand stores
- [ ] GraphCanvas with React Flow
- [ ] All 9 node components
- [ ] All 7 edge components
- [ ] All 4 panel components
- [ ] SSE/WebSocket services
- [ ] Dashboard layout (Lab Workspace)

### Not Started
- [ ] Agent avatar/status components
- [ ] Output components (action-plan, export)
- [ ] Chat input for sync mode
- [ ] Pareto view (filtering phase)
- [ ] Debate view (convergence phase)

---

## Performance Considerations

For 50-200 nodes per session:
- React Flow built-in virtualization
- Node clustering for dense areas
- Lazy load panel content
- Debounce graph updates during streaming
- Web Workers for layout calculations

---

## Architecture

### Technology Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 14, TypeScript, React Flow, Zustand, Tailwind CSS |
| Backend | FastAPI, Python 3.11+, LangGraph, LangChain |
| Database | PostgreSQL 16 (with pgvector), Redis 7.x |
| Real-time | SSE (streaming), WebSocket (sync mode) |
| Task Queue | Celery |

### Agent System (8 Types)

| Agent | Type | Function |
|-------|------|----------|
| RPA | Requirement Parsing | Parse natural language requirements, Bayesian preference elicitation |
| GEN | Generator | MAP-Elites QD algorithm for diverse solution generation |
| ISA | Information Scout | MCP protocol external fact retrieval, semantic entropy verification |
| ACA | Audit & Compliance | First-order logic contradiction detection, constraint validation |
| BM | Branch Manager | Socratic questioning, branch state management |
| GA | Game Arbiter | qEHVI resource scheduling, Nash equilibrium |
| UOA | Utility Optimization | Semantic anchoring quantification, variance reduction |
| REC | Reverse Engineering Compiler | Topological sorting, executable plan generation |

### Core Algorithms

| Algorithm | File | Function |
|-----------|------|----------|
| Pareto Optimization | `pareto.py` | Multi-objective optimization, hypervolume calculation, crowding distance |
| Semantic Entropy | `oscillation.py` | NLI clustering, entropy calculation, oscillation detection |
| Sensitivity Analysis | `sensitivity.py` | Monte Carlo perturbation, critical node identification |
| Path Analysis | `path_analysis.py` | Critical paths, redundant paths, minimal cut sets |

## Project Structure

```
yesbut/
├── backend/
│   ├── agents/                    # Agent modules
│   │   ├── base/agent.py          # Base agent class
│   │   ├── rpa/agent.py           # Requirement Parsing Agent
│   │   ├── gen/agent.py           # Generator Agent
│   │   ├── isa/agent.py           # Information Scout Agent
│   │   ├── aca/agent.py           # Audit & Compliance Agent
│   │   ├── bm/agent.py            # Branch Manager Agent
│   │   ├── ga/agent.py            # Game Arbiter Agent
│   │   ├── uoa/agent.py           # Utility Optimization Agent
│   │   ├── rec/agent.py           # Reverse Engineering Compiler
│   │   ├── orchestrator.py        # LangGraph orchestrator
│   │   ├── state.py               # State definitions
│   │   ├── streaming.py           # Streaming utilities
│   │   └── convergence_controller.py  # Convergence controller
│   │
│   ├── algorithms/                # Core algorithms
│   │   ├── pareto.py              # Pareto optimization
│   │   ├── oscillation.py         # Semantic entropy and oscillation detection
│   │   ├── sensitivity.py         # Sensitivity analysis
│   │   └── path_analysis.py       # Path analysis
│   │
│   ├── app/                       # FastAPI application
│   │   ├── api/v1/
│   │   │   ├── sessions.py        # Session API
│   │   │   ├── nodes.py           # Node API
│   │   │   ├── edges.py           # Edge API
│   │   │   ├── branches.py        # Branch API
│   │   │   └── graph.py           # Graph analysis API
│   │   ├── services/
│   │   │   ├── session_service.py # Session service
│   │   │   ├── graph_service.py   # Graph service
│   │   │   └── lock_service.py    # Distributed lock service
│   │   ├── config.py              # Configuration
│   │   └── main.py                # Application entry
│   │
│   ├── tests/                     # Unit tests
│   │   ├── test_algorithms/       # Algorithm tests
│   │   ├── test_services/         # Service tests
│   │   └── test_agents/           # Agent tests
│   │
│   ├── mcp/                       # MCP client
│   ├── optimization/              # TextGrad optimization
│   └── tasks/                     # Celery tasks
│
├── frontend/                      # Next.js frontend
│   └── src/
│       ├── app/                   # Next.js App Router
│       ├── components/            # React components
│       ├── hooks/                 # Custom hooks
│       ├── store/                 # Zustand stores
│       ├── services/              # API services
│       ├── lib/                   # Utilities
│       └── types/                 # TypeScript types
│
├── docker/                        # Docker configurations
├── scripts/                       # Utility scripts
├── docker-compose.yml             # Container orchestration
└── .env.example                   # Environment template
```

## Quick Start

### Prerequisites

- Node.js 20.x
- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 16 (via Docker)
- Redis 7.x (via Docker)

### Installation

```bash
# Clone repository
git clone https://github.com/your-org/yesbut.git
cd yesbut

# Setup environment
cp .env.example .env
# Edit .env with your configuration

# Start infrastructure
docker-compose up -d postgres redis

# Setup backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install poetry
poetry install

# Run database migrations
poetry run alembic upgrade head

# Start backend server
poetry run uvicorn app.main:app --reload --port 8001

# Setup frontend (new terminal)
cd frontend
npm install
npm run dev
```

### API Configuration

The system uses Anthropic Claude API. Configure in `.env`:

```env
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-5-sonnet-20241022
LLM_API_KEY=your_api_key
LLM_API_BASE=https://api.anthropic.com  # or your proxy URL
```

For local proxy setup:
```bash
# Using LiteLLM as proxy
pip install litellm
litellm --model anthropic/claude-3-5-sonnet-20241022 --port 8000
```

## Key Features

### Convergence Control Mechanism

- Maximum round limit (default: 10 rounds)
- Semantic entropy stagnation detection (3 consecutive rounds without decrease)
- Position similarity oscillation detection (threshold 0.85)

### Structural Stability Analysis

- **Statically Determinate Core**: Critical paths where any node failure collapses the conclusion
- **Redundant Support**: Alternative paths that compensate for localized failures
- **Minimal Cut Sets**: Smallest set of nodes whose failure disconnects root from goal

### Distributed Locking

- Branch-level locking for race condition prevention
- Optimistic version control
- Automatic expiration release

## Testing

```bash
cd backend

# Run all tests
poetry run pytest

# Run specific test modules
poetry run pytest tests/test_algorithms/
poetry run pytest tests/test_services/
poetry run pytest tests/test_agents/

# Run with coverage
poetry run pytest --cov=.
```

### Test Results

| Module | Tests | Status |
|--------|-------|--------|
| Pareto Optimization | 7/7 | Passed |
| Oscillation Detection | 6/6 | Passed |
| Sensitivity Analysis | 5/5 | Passed |
| Path Analysis | 6/6 | Passed |
| SessionService | 10/10 | Passed |
| GraphService | 8/8 | Passed |
| All Agents | 20/20 | Passed |

## API Endpoints

### Sessions
- `GET /api/v1/sessions` - List sessions
- `POST /api/v1/sessions` - Create session
- `GET /api/v1/sessions/{id}` - Get session
- `DELETE /api/v1/sessions/{id}` - Delete session
- `GET /api/v1/sessions/{id}/stream` - SSE stream

### Graph Operations
- `GET /api/v1/sessions/{id}/nodes` - List nodes
- `POST /api/v1/sessions/{id}/nodes` - Create node
- `GET /api/v1/sessions/{id}/edges` - List edges
- `POST /api/v1/sessions/{id}/edges` - Create edge
- `GET /api/v1/sessions/{id}/branches` - List branches
- `GET /api/v1/sessions/{id}/graph/analysis` - Graph analysis

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | - |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379` |
| `LLM_PROVIDER` | LLM provider (anthropic/openai) | `anthropic` |
| `LLM_MODEL` | Model name | `claude-3-5-sonnet-20241022` |
| `LLM_API_KEY` | API key | - |
| `LLM_API_BASE` | API base URL | - |
| `MAX_DEBATE_ROUNDS` | Maximum debate rounds | `10` |
| `ENTROPY_STAGNATION_THRESHOLD` | Entropy stagnation threshold | `3` |
| `SIMILARITY_THRESHOLD` | Oscillation similarity threshold | `0.85` |

## Development Roadmap

### Completed
- [x] 8 agent types implementation
- [x] Core algorithm modules (Pareto, Oscillation, Sensitivity, Path Analysis)
- [x] Service layer (Session, Graph, Lock)
- [x] API endpoints
- [x] Unit test coverage

### In Progress
- [ ] Frontend-backend integration
- [ ] MCP client implementation
- [ ] Database migrations

### Planned
- [ ] Neo4j integration (when graph depth > 10)
- [ ] Distributed LangGraph (>1000 concurrent sessions)
- [ ] Fine-tuned embedding model

## References

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [React Flow Documentation](https://reactflow.dev/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Semantic Entropy Paper](https://arxiv.org/abs/2302.09664)
- [TextGrad Paper](https://arxiv.org/abs/2406.07496)
- [MAP-Elites Paper](https://arxiv.org/abs/1504.04909)

## License

MIT License

---

**Version**: 1.0.0
**Last Updated**: 2025-12-30

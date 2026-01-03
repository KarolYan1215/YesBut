# YesBut Test Plan

## Overview

This document defines a comprehensive test plan for the YesBut multi-agent collaborative brainstorming system, covering backend API tests, frontend component tests, and end-to-end integration tests.

---

## Test Environment Setup

### Prerequisites
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
poetry install
docker-compose up -d postgres redis

# Frontend
cd frontend
npm install
npm install -D vitest @testing-library/react @testing-library/jest-dom jsdom @vitejs/plugin-react playwright
```

### Test Configuration Files

**Backend**: `backend/pytest.ini` (existing)
**Frontend**: `frontend/vitest.config.ts` (to be created)

---

## Part 1: Backend API Integration Tests

### 1.1 Session API Tests (`tests/test_api/test_sessions.py`)

| Test Case | Endpoint | Method | Expected Result |
|-----------|----------|--------|-----------------|
| TC-S001 | `/api/v1/sessions` | POST | Create session with valid data, return 200 |
| TC-S002 | `/api/v1/sessions` | POST | Reject invalid title (empty), return 422 |
| TC-S003 | `/api/v1/sessions` | POST | Reject invalid mode (not sync/async), return 422 |
| TC-S004 | `/api/v1/sessions/{id}` | GET | Return session details |
| TC-S005 | `/api/v1/sessions/{id}` | GET | Return 404 for non-existent session |
| TC-S006 | `/api/v1/sessions` | GET | List sessions with pagination |
| TC-S007 | `/api/v1/sessions/{id}` | PATCH | Update session title |
| TC-S008 | `/api/v1/sessions/{id}` | DELETE | Delete session |
| TC-S009 | `/api/v1/sessions/{id}/start` | POST | Start draft session |
| TC-S010 | `/api/v1/sessions/{id}/pause` | POST | Pause active session |
| TC-S011 | `/api/v1/sessions/{id}/resume` | POST | Resume paused session |
| TC-S012 | `/api/v1/sessions/{id}/complete` | POST | Complete session |
| TC-S013 | `/api/v1/sessions/{id}/toggle-mode` | POST | Toggle sync/async mode |
| TC-S014 | `/api/v1/sessions/{id}/transition-phase` | POST | Transition divergence -> filtering |
| TC-S015 | `/api/v1/sessions/{id}/statistics` | GET | Return session statistics |

### 1.2 Node API Tests (`tests/test_api/test_nodes.py`)

| Test Case | Endpoint | Method | Expected Result |
|-----------|----------|--------|-----------------|
| TC-N001 | `/api/v1/sessions/{sid}/nodes` | POST | Create goal node |
| TC-N002 | `/api/v1/sessions/{sid}/nodes` | POST | Create claim node with parent |
| TC-N003 | `/api/v1/sessions/{sid}/nodes` | POST | Create fact node |
| TC-N004 | `/api/v1/sessions/{sid}/nodes` | POST | Create constraint node |
| TC-N005 | `/api/v1/sessions/{sid}/nodes` | POST | Reject invalid node type |
| TC-N006 | `/api/v1/sessions/{sid}/nodes/{nid}` | GET | Return node details |
| TC-N007 | `/api/v1/sessions/{sid}/nodes` | GET | List nodes with type filter |
| TC-N008 | `/api/v1/sessions/{sid}/nodes` | GET | List nodes with branch filter |
| TC-N009 | `/api/v1/sessions/{sid}/nodes/{nid}` | PATCH | Update node content |
| TC-N010 | `/api/v1/sessions/{sid}/nodes/{nid}` | PATCH | Update node confidence |
| TC-N011 | `/api/v1/sessions/{sid}/nodes/{nid}` | DELETE | Delete node and edges |
| TC-N012 | `/api/v1/sessions/{sid}/nodes/{nid}/ancestors` | GET | Return ancestor nodes |
| TC-N013 | `/api/v1/sessions/{sid}/nodes/{nid}/descendants` | GET | Return descendant nodes |
| TC-N014 | `/api/v1/sessions/{sid}/nodes/{nid}/path-to-root` | GET | Return path to root |

### 1.3 Edge API Tests (`tests/test_api/test_edges.py`)

| Test Case | Endpoint | Method | Expected Result |
|-----------|----------|--------|-----------------|
| TC-E001 | `/api/v1/sessions/{sid}/edges` | POST | Create support edge |
| TC-E002 | `/api/v1/sessions/{sid}/edges` | POST | Create attack edge |
| TC-E003 | `/api/v1/sessions/{sid}/edges` | POST | Create decompose edge |
| TC-E004 | `/api/v1/sessions/{sid}/edges` | POST | Reject self-loop edge |
| TC-E005 | `/api/v1/sessions/{sid}/edges` | POST | Reject duplicate edge |
| TC-E006 | `/api/v1/sessions/{sid}/edges` | GET | List edges with type filter |
| TC-E007 | `/api/v1/sessions/{sid}/edges/{eid}` | DELETE | Delete edge |

### 1.4 Branch API Tests (`tests/test_api/test_branches.py`)

| Test Case | Endpoint | Method | Expected Result |
|-----------|----------|--------|-----------------|
| TC-B001 | `/api/v1/sessions/{sid}/branches` | POST | Create branch |
| TC-B002 | `/api/v1/sessions/{sid}/branches` | GET | List branches |
| TC-B003 | `/api/v1/sessions/{sid}/branches/{bid}` | GET | Return branch details |
| TC-B004 | `/api/v1/sessions/{sid}/branches/{bid}/fork` | POST | Fork branch |

### 1.5 Graph Analysis API Tests (`tests/test_api/test_graph.py`)

| Test Case | Endpoint | Method | Expected Result |
|-----------|----------|--------|-----------------|
| TC-G001 | `/api/v1/sessions/{sid}/graph/analysis` | GET | Return graph statistics |
| TC-G002 | `/api/v1/sessions/{sid}/graph/critical-paths` | GET | Return critical paths |
| TC-G003 | `/api/v1/sessions/{sid}/graph/sensitivity` | GET | Return sensitivity analysis |

---

## Part 2: Frontend Component Tests

### 2.1 UI Component Tests (`frontend/src/components/ui/__tests__/`)

| Test Case | Component | Test Description |
|-----------|-----------|------------------|
| TC-UI001 | Button | Render primary/secondary/ghost variants |
| TC-UI002 | Button | Handle click events |
| TC-UI003 | Button | Show loading state |
| TC-UI004 | Card | Render with/without hover effect |
| TC-UI005 | Badge | Render different variants (default/success/warning/error) |
| TC-UI006 | Progress | Display correct percentage |
| TC-UI007 | Input | Handle value changes |
| TC-UI008 | Textarea | Handle multiline input |
| TC-UI009 | Dialog | Open/close behavior |
| TC-UI010 | Tooltip | Show on hover |

### 2.2 Graph Component Tests (`frontend/src/components/graph/__tests__/`)

| Test Case | Component | Test Description |
|-----------|-----------|------------------|
| TC-GR001 | GraphCanvas | Render empty canvas |
| TC-GR002 | GraphCanvas | Render nodes and edges |
| TC-GR003 | GraphCanvas | Handle node selection |
| TC-GR004 | GoalNode | Render with correct styling (#6366F1) |
| TC-GR005 | ClaimNode | Render with confidence indicator |
| TC-GR006 | FactNode | Render with source citation |
| TC-GR007 | ConstraintNode | Render with red border (#EF4444) |
| TC-GR008 | SupportEdge | Render green edge (1.5px) |
| TC-GR009 | AttackEdge | Render red edge (2px) |
| TC-GR010 | ConflictEdge | Render orange dashed edge |

### 2.3 Session Component Tests (`frontend/src/components/session/__tests__/`)

| Test Case | Component | Test Description |
|-----------|-----------|------------------|
| TC-SE001 | PhaseIndicator | Show divergence phase active |
| TC-SE002 | PhaseIndicator | Show filtering phase active |
| TC-SE003 | PhaseIndicator | Show convergence phase active |
| TC-SE004 | SessionCard | Render session info |
| TC-SE005 | ViewToggle | Toggle causal/conflict view |

### 2.4 Input Component Tests (`frontend/src/components/input/__tests__/`)

| Test Case | Component | Test Description |
|-----------|-----------|------------------|
| TC-IN001 | RequirementInput | Handle text input |
| TC-IN002 | PreferenceWizard | Navigate through steps |
| TC-IN003 | PreferenceWizard | Submit preferences |
| TC-IN004 | ConstraintEditor | Add constraint |
| TC-IN005 | ConstraintEditor | Remove constraint |

### 2.5 Store Tests (`frontend/src/store/__tests__/`)

| Test Case | Store | Test Description |
|-----------|-------|------------------|
| TC-ST001 | graphStore | Add node |
| TC-ST002 | graphStore | Update node |
| TC-ST003 | graphStore | Remove node (cascade edges) |
| TC-ST004 | graphStore | Add edge |
| TC-ST005 | graphStore | Set selected node |
| TC-ST006 | graphStore | Reset state |
| TC-ST007 | sessionStore | Set current session |
| TC-ST008 | sessionStore | Update phase |
| TC-ST009 | streamingStore | Add preview node |
| TC-ST010 | streamingStore | Clear preview |

---

## Part 3: End-to-End Tests (Playwright)

### 3.1 User Flow: New Session Creation

**Test Scenario: TC-E2E001 - Complete Session Creation Flow**

```
Step 1: Navigate to Landing Page (/)
  - Verify page loads
  - Click "Get Started" button

Step 2: Navigate to Dashboard (/dashboard)
  - Verify dashboard loads
  - Click "New Session" button

Step 3: Fill Session Form (/dashboard/sessions/new)
  - Enter title: "Product Strategy Q1 2025"
  - Enter goal: "Develop a comprehensive product roadmap for Q1"
  - Select mode: "Async"
  - Click "Create Session"

Step 4: Verify Session Created
  - Redirect to /dashboard/sessions/{id}
  - Verify session title displayed
  - Verify phase indicator shows "Divergence"
```

### 3.2 User Flow: Divergence Phase

**Test Scenario: TC-E2E002 - Divergence Phase Operations**

```
Step 1: Start Session
  - Click "Start" button
  - Verify status changes to "active"

Step 2: View Generated Solutions
  - Wait for SSE stream updates
  - Verify solution nodes appear on canvas
  - Verify 50-200 solutions generated

Step 3: Explore Feature Space
  - Verify feature dimensions displayed
  - Click on solution to view details
  - Verify solution metadata shown in panel
```

### 3.3 User Flow: Filtering Phase

**Test Scenario: TC-E2E003 - Filtering Phase Operations**

```
Step 1: Transition to Filtering
  - Click "Next Phase" button
  - Verify phase indicator updates

Step 2: View Pareto Front
  - Verify Pareto candidates displayed
  - Verify 5-15 candidates shown

Step 3: Evaluate Candidates
  - Click on candidate node
  - View utility scores
  - View constraint satisfaction
```

### 3.4 User Flow: Convergence Phase

**Test Scenario: TC-E2E004 - Convergence Phase Operations**

```
Step 1: Transition to Convergence
  - Click "Next Phase" button
  - Verify phase indicator updates

Step 2: View Debate Graph
  - Verify graph canvas loads
  - Verify goal node at root
  - Verify claim nodes connected

Step 3: Observe Agent Debate
  - Verify agent activity panel updates
  - Verify support/attack edges appear
  - Wait for convergence (max 10 rounds)

Step 4: View Final Output
  - Click "View Output" button
  - Verify action plan displayed
  - Verify export options available
```

### 3.5 User Flow: Graph Interaction

**Test Scenario: TC-E2E005 - Graph Canvas Interaction**

```
Step 1: Node Selection
  - Click on node
  - Verify node highlighted
  - Verify detail panel opens

Step 2: Pan and Zoom
  - Drag canvas to pan
  - Use scroll to zoom
  - Verify viewport updates

Step 3: View Toggle
  - Click "Causal View" toggle
  - Verify edge display changes
  - Click "Conflict View" toggle
  - Verify conflict edges shown
```

---

## Part 4: Specific Use Case Experiments

### Experiment 1: Product Strategy Brainstorming

**Scenario**: A product manager wants to brainstorm Q1 product strategy

**Input**:
```
Goal: "Develop a comprehensive product roadmap for Q1 2025 that balances
      user growth, revenue targets, and technical debt reduction"

Constraints:
- Budget: $500K
- Team size: 10 engineers
- Timeline: 3 months

Preferences:
- Priority: User growth > Revenue > Tech debt
- Risk tolerance: Medium
```

**Expected Output**:
- Divergence: 50-200 strategy options across feature dimensions
- Filtering: 5-15 Pareto-optimal strategies
- Convergence: Executable action plan with milestones

### Experiment 2: Technical Architecture Decision

**Scenario**: An architect needs to decide on microservices vs monolith

**Input**:
```
Goal: "Determine the optimal architecture for our e-commerce platform
      considering scalability, team expertise, and time-to-market"

Constraints:
- Must support 10K concurrent users
- Team has limited Kubernetes experience
- Launch deadline: 6 months

Preferences:
- Priority: Time-to-market > Scalability > Maintainability
```

**Expected Output**:
- Divergence: Architecture options (monolith, microservices, modular monolith, serverless)
- Filtering: Top 3 architectures with trade-off analysis
- Convergence: Recommended architecture with implementation plan

### Experiment 3: Marketing Campaign Planning

**Scenario**: Marketing team brainstorming campaign ideas

**Input**:
```
Goal: "Design a marketing campaign for product launch targeting
      enterprise customers in the fintech sector"

Constraints:
- Budget: $100K
- Duration: 2 months
- Channels: Digital only

Preferences:
- Priority: Lead quality > Lead quantity > Brand awareness
```

**Expected Output**:
- Divergence: 100+ campaign ideas across channels
- Filtering: 10 high-potential campaigns
- Convergence: Integrated campaign plan with timeline

---

## Part 5: Performance Tests

### 5.1 Load Tests

| Test Case | Scenario | Target |
|-----------|----------|--------|
| TC-P001 | Concurrent session creation | 100 sessions/min |
| TC-P002 | Node creation rate | 1000 nodes/session |
| TC-P003 | SSE stream latency | < 100ms |
| TC-P004 | Graph rendering (200 nodes) | < 500ms |

### 5.2 Stress Tests

| Test Case | Scenario | Target |
|-----------|----------|--------|
| TC-P005 | Max nodes per session | 500 nodes |
| TC-P006 | Max concurrent SSE connections | 100 connections |
| TC-P007 | Database query performance | < 50ms avg |

---

## Test Execution Commands

### Backend Tests
```bash
cd backend

# Run all tests
poetry run pytest -v

# Run API tests only
poetry run pytest tests/test_api/ -v

# Run with coverage
poetry run pytest --cov=app --cov-report=html

# Run specific test file
poetry run pytest tests/test_api/test_sessions.py -v
```

### Frontend Tests
```bash
cd frontend

# Run unit tests
npm run test

# Run with coverage
npm run test:coverage

# Run E2E tests
npm run test:e2e
```

### Full Test Suite
```bash
# From project root
./scripts/run_all_tests.sh
```

---

## Test Data Fixtures

### Session Fixture
```json
{
  "title": "Test Session",
  "description": "Test description",
  "initial_goal": "Test goal for brainstorming",
  "mode": "async",
  "settings": {
    "max_debate_rounds": 10,
    "entropy_threshold": 0.1
  }
}
```

### Node Fixtures
```json
{
  "goal_node": {
    "type": "goal",
    "content": "Develop product strategy",
    "layer": 0,
    "confidence": 1.0
  },
  "claim_node": {
    "type": "claim",
    "content": "Focus on user acquisition",
    "layer": 1,
    "confidence": 0.8,
    "parent_id": "{goal_node_id}"
  },
  "fact_node": {
    "type": "fact",
    "content": "Market research shows 30% growth potential",
    "layer": 2,
    "confidence": 0.95
  },
  "constraint_node": {
    "type": "constraint",
    "content": "Budget limit: $500K",
    "layer": 1,
    "confidence": 1.0
  }
}
```

---

## Acceptance Criteria

### Backend
- [ ] All API endpoints return correct status codes
- [ ] Session lifecycle (create -> start -> pause -> resume -> complete) works
- [ ] Phase transitions (divergence -> filtering -> convergence) work
- [ ] Node CRUD operations work correctly
- [ ] Edge creation validates source/target nodes
- [ ] Branch forking creates independent copies

### Frontend
- [ ] All UI components render correctly
- [ ] Graph canvas displays nodes and edges
- [ ] Phase indicator reflects current phase
- [ ] Real-time updates via SSE work
- [ ] User can navigate through all pages

### Integration
- [ ] Frontend can create sessions via API
- [ ] Frontend receives SSE updates
- [ ] Graph state syncs with backend
- [ ] Export functionality works

---

## Risk Areas

1. **SSE Streaming**: Connection stability, reconnection logic
2. **Graph Performance**: Large graph rendering (200+ nodes)
3. **Concurrent Edits**: Lock contention in sync mode
4. **Phase Transitions**: State consistency during transitions
5. **Agent Coordination**: LangGraph orchestration reliability

---

## Test Schedule

| Phase | Duration | Focus |
|-------|----------|-------|
| Week 1 | 5 days | Backend API tests |
| Week 2 | 5 days | Frontend component tests |
| Week 3 | 5 days | E2E tests + Integration |
| Week 4 | 3 days | Performance tests + Bug fixes |

---

**Document Version**: 1.0
**Created**: 2025-01-03
**Author**: Test Engineering Team

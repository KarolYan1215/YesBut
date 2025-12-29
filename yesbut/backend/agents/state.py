"""
Agent State Definitions Module

Shared state definitions for LangGraph agent orchestration.

@module agents/state
"""

from typing import Optional, List, Dict, Any, TypedDict, Annotated
from datetime import datetime
from enum import Enum
import operator
import uuid


class AgentType(str, Enum):
    """Agent type enumeration."""

    RPA = "rpa"  # Requirement Parsing Agent
    GEN = "gen"  # Generator Agent
    ISA = "isa"  # Information Scout Agent
    ACA = "aca"  # Audit & Compliance Agent
    BM = "bm"    # Branch Manager Agent
    GA = "ga"    # Game Arbiter Agent
    UOA = "uoa"  # Utility Optimization Agent
    REC = "rec"  # Reverse Engineering Compiler


class PhaseType(str, Enum):
    """Session phase enumeration."""

    DIVERGENCE = "divergence"
    FILTERING = "filtering"
    CONVERGENCE = "convergence"


class ActionType(str, Enum):
    """Agent action type enumeration."""

    CREATE_NODE = "create_node"
    UPDATE_NODE = "update_node"
    DELETE_NODE = "delete_node"
    CREATE_EDGE = "create_edge"
    UPDATE_EDGE = "update_edge"
    DELETE_EDGE = "delete_edge"
    FORK_BRANCH = "fork_branch"
    MERGE_BRANCH = "merge_branch"
    PRUNE_BRANCH = "prune_branch"
    VALIDATE = "validate"
    SEARCH = "search"
    SYNTHESIZE = "synthesize"


# =============================================================================
# State Components
# =============================================================================


class NodeState(TypedDict):
    """
    Node state representation.

    Attributes:
        id: Node unique identifier
        type: Node type (goal, claim, fact, etc.)
        content: Node content text
        layer: Layer number
        branch_id: Branch ID
        parent_id: Parent node ID
        confidence: Confidence score (0-1)
        utility: Utility value (0-1)
        sensitivity: Sensitivity score (0-1)
        metadata: Additional metadata
    """

    id: str
    type: str
    content: str
    layer: int
    branch_id: Optional[str]
    parent_id: Optional[str]
    confidence: float
    utility: float
    sensitivity: Optional[float]
    metadata: Dict[str, Any]


class EdgeState(TypedDict):
    """
    Edge state representation.

    Attributes:
        id: Edge unique identifier
        source_id: Source node ID
        target_id: Target node ID
        type: Edge type (support, attack, etc.)
        weight: Edge weight (0-1)
        validated: Validation status
    """

    id: str
    source_id: str
    target_id: str
    type: str
    weight: float
    validated: Optional[bool]


class BranchState(TypedDict):
    """
    Branch state representation.

    Attributes:
        id: Branch unique identifier
        name: Branch name
        status: Branch status
        utility_score: Current utility score
        lock_state: Current lock state
        lock_holder_id: Lock holder ID
    """

    id: str
    name: str
    status: str
    utility_score: float
    lock_state: str
    lock_holder_id: Optional[str]


class AgentAction(TypedDict):
    """
    Agent action representation.

    Attributes:
        agent_type: Type of agent performing action
        agent_id: Agent instance ID
        action_type: Type of action
        target_id: Target resource ID
        payload: Action payload data
        timestamp: Action timestamp
        result: Action result (after execution)
    """

    agent_type: str
    agent_id: str
    action_type: str
    target_id: Optional[str]
    payload: Dict[str, Any]
    timestamp: str
    result: Optional[Dict[str, Any]]


class ConvergenceMetrics(TypedDict):
    """
    Convergence metrics for phase transition detection.

    Attributes:
        step_count: Current step count
        semantic_entropy: Current semantic entropy
        position_history: Recent position history for oscillation detection
        pareto_front_size: Size of Pareto front
        pareto_stability: Pareto front stability score
        nash_distance: Distance to Nash equilibrium
    """

    step_count: int
    semantic_entropy: float
    position_history: List[Dict[str, Any]]
    pareto_front_size: int
    pareto_stability: float
    nash_distance: float


# =============================================================================
# Main Agent State
# =============================================================================


class AgentState(TypedDict):
    """
    Main agent orchestration state for LangGraph.

    This state is shared across all agents in the orchestration graph.
    Uses Annotated types with reducers for proper state merging.

    Attributes:
        session_id: Current session ID
        phase: Current session phase
        phase_progress: Progress within current phase (0-1)

        nodes: Current graph nodes (keyed by ID)
        edges: Current graph edges (keyed by ID)
        branches: Current branches (keyed by ID)

        active_branch_id: Currently active branch ID
        focus_node_id: Currently focused node ID

        pending_actions: Queue of pending agent actions
        completed_actions: History of completed actions

        convergence_metrics: Metrics for convergence detection
        agent_assignments: Agent-to-branch assignments

        messages: LangGraph message history
        errors: Error messages from agents

        metadata: Additional state metadata
    """

    # Session context
    session_id: str
    phase: PhaseType
    phase_progress: float

    # Graph state
    nodes: Dict[str, NodeState]
    edges: Dict[str, EdgeState]
    branches: Dict[str, BranchState]

    # Focus state
    active_branch_id: Optional[str]
    focus_node_id: Optional[str]

    # Action queues
    pending_actions: Annotated[List[AgentAction], operator.add]
    completed_actions: Annotated[List[AgentAction], operator.add]

    # Convergence tracking
    convergence_metrics: ConvergenceMetrics

    # Agent management
    agent_assignments: Dict[str, str]  # agent_id -> branch_id

    # LangGraph messages
    messages: Annotated[List[Dict[str, Any]], operator.add]

    # Error tracking
    errors: Annotated[List[str], operator.add]

    # Metadata
    metadata: Dict[str, Any]


# =============================================================================
# State Factory Functions
# =============================================================================


def create_initial_state(
    session_id: str,
    initial_goal: str,
) -> AgentState:
    """
    Create initial agent state for a new session.

    Args:
        session_id: Session ID
        initial_goal: Initial goal text

    Returns:
        AgentState: Initialized state
    """
    # Create root goal node
    goal_node_id = str(uuid.uuid4())
    goal_node = create_node_state(
        node_id=goal_node_id,
        node_type="goal",
        content=initial_goal,
        layer=0,
    )

    # Create main branch
    main_branch_id = str(uuid.uuid4())
    main_branch = create_branch_state(
        branch_id=main_branch_id,
        name="main",
        status="active",
    )

    # Update goal node with branch
    goal_node["branch_id"] = main_branch_id

    return {
        "session_id": session_id,
        "phase": PhaseType.DIVERGENCE,
        "phase_progress": 0.0,
        "nodes": {goal_node_id: goal_node},
        "edges": {},
        "branches": {main_branch_id: main_branch},
        "active_branch_id": main_branch_id,
        "focus_node_id": goal_node_id,
        "pending_actions": [],
        "completed_actions": [],
        "convergence_metrics": {
            "step_count": 0,
            "semantic_entropy": 1.0,
            "position_history": [],
            "pareto_front_size": 0,
            "pareto_stability": 0.0,
            "nash_distance": 1.0,
        },
        "agent_assignments": {},
        "messages": [],
        "errors": [],
        "metadata": {
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        },
    }


def create_node_state(
    node_id: str,
    node_type: str,
    content: str,
    layer: int = 0,
    branch_id: Optional[str] = None,
    parent_id: Optional[str] = None,
) -> NodeState:
    """
    Create a node state object.

    Args:
        node_id: Node ID
        node_type: Node type
        content: Node content
        layer: Layer number
        branch_id: Branch ID
        parent_id: Parent node ID

    Returns:
        NodeState: Node state object
    """
    return {
        "id": node_id,
        "type": node_type,
        "content": content,
        "layer": layer,
        "branch_id": branch_id,
        "parent_id": parent_id,
        "confidence": 0.8,
        "utility": 0.5,
        "sensitivity": None,
        "metadata": {
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        },
    }


def create_edge_state(
    edge_id: str,
    source_id: str,
    target_id: str,
    edge_type: str,
    weight: float = 1.0,
) -> EdgeState:
    """
    Create an edge state object.

    Args:
        edge_id: Edge ID
        source_id: Source node ID
        target_id: Target node ID
        edge_type: Edge type
        weight: Edge weight

    Returns:
        EdgeState: Edge state object
    """
    return {
        "id": edge_id,
        "source_id": source_id,
        "target_id": target_id,
        "type": edge_type,
        "weight": weight,
        "validated": None,
    }


def create_branch_state(
    branch_id: str,
    name: str,
    status: str = "active",
) -> BranchState:
    """
    Create a branch state object.

    Args:
        branch_id: Branch ID
        name: Branch name
        status: Branch status

    Returns:
        BranchState: Branch state object
    """
    return {
        "id": branch_id,
        "name": name,
        "status": status,
        "utility_score": 0.5,
        "lock_state": "EDITABLE",
        "lock_holder_id": None,
    }


def create_agent_action(
    agent_type: AgentType,
    agent_id: str,
    action_type: ActionType,
    payload: Dict[str, Any],
    target_id: Optional[str] = None,
) -> AgentAction:
    """
    Create an agent action object.

    Args:
        agent_type: Type of agent
        agent_id: Agent instance ID
        action_type: Type of action
        payload: Action payload
        target_id: Target resource ID

    Returns:
        AgentAction: Action object
    """
    return {
        "agent_type": agent_type.value if isinstance(agent_type, AgentType) else agent_type,
        "agent_id": agent_id,
        "action_type": action_type.value if isinstance(action_type, ActionType) else action_type,
        "target_id": target_id,
        "payload": payload,
        "timestamp": datetime.utcnow().isoformat(),
        "result": None,
    }


# =============================================================================
# State Utility Functions
# =============================================================================


def get_node_by_id(state: AgentState, node_id: str) -> Optional[NodeState]:
    """
    Get node from state by ID.

    Args:
        state: Agent state
        node_id: Node ID

    Returns:
        NodeState or None
    """
    return state["nodes"].get(node_id)


def get_branch_nodes(state: AgentState, branch_id: str) -> List[NodeState]:
    """
    Get all nodes in a branch.

    Args:
        state: Agent state
        branch_id: Branch ID

    Returns:
        List of nodes in branch
    """
    return [
        node for node in state["nodes"].values()
        if node.get("branch_id") == branch_id
    ]


def get_node_children(state: AgentState, node_id: str) -> List[NodeState]:
    """
    Get child nodes of a node.

    Args:
        state: Agent state
        node_id: Parent node ID

    Returns:
        List of child nodes
    """
    # Find edges where source is the parent
    child_ids = set()
    for edge in state["edges"].values():
        if edge["source_id"] == node_id and edge["type"] == "decompose":
            child_ids.add(edge["target_id"])

    return [
        state["nodes"][cid] for cid in child_ids
        if cid in state["nodes"]
    ]


def get_incoming_edges(state: AgentState, node_id: str) -> List[EdgeState]:
    """
    Get edges pointing to a node.

    Args:
        state: Agent state
        node_id: Target node ID

    Returns:
        List of incoming edges
    """
    return [
        edge for edge in state["edges"].values()
        if edge["target_id"] == node_id
    ]


def get_outgoing_edges(state: AgentState, node_id: str) -> List[EdgeState]:
    """
    Get edges originating from a node.

    Args:
        state: Agent state
        node_id: Source node ID

    Returns:
        List of outgoing edges
    """
    return [
        edge for edge in state["edges"].values()
        if edge["source_id"] == node_id
    ]


def should_transition_phase(state: AgentState) -> bool:
    """
    Check if phase transition conditions are met.

    Args:
        state: Agent state

    Returns:
        bool: Whether to transition
    """
    metrics = state["convergence_metrics"]
    phase = state["phase"]

    if phase == PhaseType.DIVERGENCE:
        # Transition when enough nodes generated or entropy stabilizes
        node_count = len(state["nodes"])
        return node_count >= 15 or metrics["semantic_entropy"] < 0.3

    elif phase == PhaseType.FILTERING:
        # Transition when Pareto front is stable
        return metrics["pareto_stability"] > 0.8

    elif phase == PhaseType.CONVERGENCE:
        # Transition when Nash equilibrium reached
        return metrics["nash_distance"] < 0.1

    return False


def get_next_phase(current_phase: PhaseType) -> Optional[PhaseType]:
    """
    Get the next phase in sequence.

    Args:
        current_phase: Current phase

    Returns:
        Next phase or None if at end
    """
    phase_sequence = [
        PhaseType.DIVERGENCE,
        PhaseType.FILTERING,
        PhaseType.CONVERGENCE,
    ]

    try:
        current_index = phase_sequence.index(current_phase)
        if current_index < len(phase_sequence) - 1:
            return phase_sequence[current_index + 1]
    except ValueError:
        pass

    return None


def add_node_to_state(
    state: AgentState,
    node: NodeState,
) -> AgentState:
    """
    Add a node to the state.

    Args:
        state: Current state
        node: Node to add

    Returns:
        Updated state
    """
    state["nodes"][node["id"]] = node
    state["metadata"]["updated_at"] = datetime.utcnow().isoformat()
    return state


def add_edge_to_state(
    state: AgentState,
    edge: EdgeState,
) -> AgentState:
    """
    Add an edge to the state.

    Args:
        state: Current state
        edge: Edge to add

    Returns:
        Updated state
    """
    state["edges"][edge["id"]] = edge
    state["metadata"]["updated_at"] = datetime.utcnow().isoformat()
    return state


def update_convergence_metrics(
    state: AgentState,
    entropy: Optional[float] = None,
    pareto_size: Optional[int] = None,
    pareto_stability: Optional[float] = None,
    nash_distance: Optional[float] = None,
) -> AgentState:
    """
    Update convergence metrics.

    Args:
        state: Current state
        entropy: New semantic entropy
        pareto_size: New Pareto front size
        pareto_stability: New Pareto stability
        nash_distance: New Nash distance

    Returns:
        Updated state
    """
    metrics = state["convergence_metrics"]
    metrics["step_count"] += 1

    if entropy is not None:
        metrics["semantic_entropy"] = entropy
    if pareto_size is not None:
        metrics["pareto_front_size"] = pareto_size
    if pareto_stability is not None:
        metrics["pareto_stability"] = pareto_stability
    if nash_distance is not None:
        metrics["nash_distance"] = nash_distance

    return state

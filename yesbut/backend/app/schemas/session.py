"""
Session Pydantic Schemas

Request/response schemas for session operations.

@module app/schemas/session
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class SessionStatus(str, Enum):
    """Session status enumeration."""

    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class SessionPhase(str, Enum):
    """Session phase enumeration."""

    DIVERGENCE = "divergence"
    FILTERING = "filtering"
    CONVERGENCE = "convergence"


class SessionMode(str, Enum):
    """Session mode enumeration."""

    SYNC = "sync"
    ASYNC = "async"


# =============================================================================
# Request Schemas
# =============================================================================


class SessionCreate(BaseModel):
    """
    Session creation request schema.

    Attributes:
        title: Session title
        description: Session description
        initial_goal: Initial goal/requirement text
        mode: Session mode (sync/async)
        settings: Optional session settings
    """

    title: str = Field(..., min_length=1, max_length=200, description="Session title")
    description: Optional[str] = Field(None, max_length=2000, description="Session description")
    initial_goal: str = Field(..., min_length=1, description="Initial goal or requirement")
    mode: SessionMode = Field(default=SessionMode.SYNC, description="Session mode")
    settings: Optional[Dict[str, Any]] = Field(None, description="Session settings")


class SessionUpdate(BaseModel):
    """
    Session update request schema.

    Attributes:
        title: Updated title
        description: Updated description
        status: Updated status
        mode: Updated mode
        settings: Updated settings
    """

    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Updated title")
    description: Optional[str] = Field(None, max_length=2000, description="Updated description")
    status: Optional[SessionStatus] = Field(None, description="Updated status")
    mode: Optional[SessionMode] = Field(None, description="Updated mode")
    settings: Optional[Dict[str, Any]] = Field(None, description="Updated settings")


class SessionPhaseTransition(BaseModel):
    """
    Session phase transition request schema.

    Attributes:
        target_phase: Target phase to transition to
        force: Force transition even if conditions not met
    """

    target_phase: SessionPhase = Field(..., description="Target phase")
    force: bool = Field(default=False, description="Force transition")


# =============================================================================
# Response Schemas
# =============================================================================


class SessionBase(BaseModel):
    """
    Base session schema with common fields.

    Attributes:
        id: Session unique identifier
        title: Session title
        description: Session description
        status: Current session status
        phase: Current session phase
        mode: Session mode
    """

    id: str = Field(..., description="Session ID")
    title: str = Field(..., description="Session title")
    description: Optional[str] = Field(None, description="Session description")
    status: SessionStatus = Field(..., description="Session status")
    phase: SessionPhase = Field(..., description="Current phase")
    mode: SessionMode = Field(..., description="Session mode")


class SessionResponse(SessionBase):
    """
    Session response schema.

    Attributes:
        Inherits all from SessionBase
        owner_id: Session owner user ID
        phase_progress: Progress within current phase (0-1)
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    owner_id: str = Field(..., description="Owner user ID")
    phase_progress: float = Field(..., ge=0, le=1, description="Phase progress")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class SessionDetailResponse(SessionResponse):
    """
    Detailed session response with statistics.

    Attributes:
        Inherits all from SessionResponse
        statistics: Session statistics
        active_agents: Currently active agents
        recent_activity: Recent activity summary
    """

    statistics: Dict[str, Any] = Field(..., description="Session statistics")
    active_agents: List[Dict[str, Any]] = Field(..., description="Active agents")
    recent_activity: List[Dict[str, Any]] = Field(..., description="Recent activity")


class SessionListResponse(BaseModel):
    """
    Session list response schema.

    Attributes:
        items: List of sessions
        total: Total count
        skip: Current offset
        limit: Current limit
    """

    items: List[SessionResponse] = Field(..., description="Session list")
    total: int = Field(..., ge=0, description="Total count")
    skip: int = Field(..., ge=0, description="Current offset")
    limit: int = Field(..., ge=1, description="Current limit")


class SessionStatistics(BaseModel):
    """
    Session statistics schema.

    Attributes:
        node_count: Total number of nodes
        edge_count: Total number of edges
        branch_count: Total number of branches
        active_branch_count: Number of active branches
        depth: Maximum graph depth
        phase_durations: Time spent in each phase
        agent_activity: Agent activity summary
    """

    node_count: int = Field(..., ge=0, description="Total nodes")
    edge_count: int = Field(..., ge=0, description="Total edges")
    branch_count: int = Field(..., ge=0, description="Total branches")
    active_branch_count: int = Field(..., ge=0, description="Active branches")
    depth: int = Field(..., ge=0, description="Max graph depth")
    phase_durations: Dict[str, float] = Field(..., description="Phase durations (seconds)")
    agent_activity: Dict[str, int] = Field(..., description="Agent action counts")


class PhaseTransitionResponse(BaseModel):
    """
    Phase transition response schema.

    Attributes:
        session_id: Session ID
        previous_phase: Previous phase
        current_phase: New current phase
        transition_time: When transition occurred
        triggered_by: What triggered the transition
    """

    session_id: str = Field(..., description="Session ID")
    previous_phase: SessionPhase = Field(..., description="Previous phase")
    current_phase: SessionPhase = Field(..., description="Current phase")
    transition_time: datetime = Field(..., description="Transition timestamp")
    triggered_by: str = Field(..., description="Transition trigger")

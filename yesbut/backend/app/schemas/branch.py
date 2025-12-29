"""
Branch Pydantic Schemas

Request/response schemas for branch operations.

@module app/schemas/branch
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class BranchStatus(str, Enum):
    """Branch status enumeration."""

    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    PRUNED = "pruned"
    MERGED = "merged"


class LockState(str, Enum):
    """Branch lock state enumeration."""

    EDITABLE = "editable"
    OBSERVATION = "observation"
    PAUSED = "paused"


# =============================================================================
# Request Schemas
# =============================================================================


class BranchCreate(BaseModel):
    """
    Branch creation request schema.

    Attributes:
        session_id: Session ID (required)
        name: Branch name (required)
        parent_branch_id: Parent branch ID (for forked branches)
        root_node_id: Root node ID
        description: Branch description
        utility_function: Custom utility function parameters
    """

    session_id: str = Field(..., description="Session ID")
    name: str = Field(..., min_length=1, max_length=100, description="Branch name")
    parent_branch_id: Optional[str] = Field(None, description="Parent branch ID")
    root_node_id: Optional[str] = Field(None, description="Root node ID")
    description: Optional[str] = Field(None, max_length=500, description="Description")
    utility_function: Optional[Dict[str, Any]] = Field(None, description="Utility function")


class BranchUpdate(BaseModel):
    """
    Branch update request schema.

    Attributes:
        name: Updated name
        status: Updated status
        description: Updated description
        utility_function: Updated utility function
        metadata: Updated metadata
    """

    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Updated name")
    status: Optional[BranchStatus] = Field(None, description="Updated status")
    description: Optional[str] = Field(None, max_length=500, description="Updated description")
    utility_function: Optional[Dict[str, Any]] = Field(None, description="Updated utility function")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Updated metadata")


class BranchFork(BaseModel):
    """
    Branch fork request schema.

    Attributes:
        name: Name for new branch (required)
        fork_point_node_id: Node ID to fork from
        copy_nodes: Whether to copy nodes
        reason: Reason for forking
    """

    name: str = Field(..., min_length=1, max_length=100, description="New branch name")
    fork_point_node_id: Optional[str] = Field(None, description="Fork point node ID")
    copy_nodes: bool = Field(default=True, description="Copy nodes to new branch")
    reason: Optional[str] = Field(None, description="Fork reason")


class BranchMerge(BaseModel):
    """
    Branch merge request schema.

    Attributes:
        target_branch_id: Target branch ID (required)
        conflict_resolution: Conflict resolution strategy
        merge_point_node_id: Node to merge at
    """

    target_branch_id: str = Field(..., description="Target branch ID")
    conflict_resolution: str = Field(default="manual", description="Conflict resolution: source, target, manual")
    merge_point_node_id: Optional[str] = Field(None, description="Merge point node ID")


class LockRequest(BaseModel):
    """
    Lock acquisition request schema.

    Attributes:
        lock_type: Lock type (EDITABLE, OBSERVATION)
        timeout: Lock timeout in seconds
    """

    lock_type: LockState = Field(default=LockState.EDITABLE, description="Lock type")
    timeout: Optional[int] = Field(None, ge=1, le=3600, description="Timeout in seconds")


# =============================================================================
# Response Schemas
# =============================================================================


class BranchBase(BaseModel):
    """
    Base branch schema with common fields.

    Attributes:
        id: Branch unique identifier
        session_id: Session ID
        name: Branch name
        status: Branch status
    """

    id: str = Field(..., description="Branch ID")
    session_id: str = Field(..., description="Session ID")
    name: str = Field(..., description="Branch name")
    status: BranchStatus = Field(..., description="Branch status")


class BranchResponse(BranchBase):
    """
    Branch response schema.

    Attributes:
        Inherits all from BranchBase
        parent_branch_id: Parent branch ID
        root_node_id: Root node ID
        description: Branch description
        utility_score: Current utility score
        agent_id: Managing agent ID
        lock_state: Current lock state
        lock_holder_id: Lock holder ID
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    parent_branch_id: Optional[str] = Field(None, description="Parent branch ID")
    root_node_id: Optional[str] = Field(None, description="Root node ID")
    description: Optional[str] = Field(None, description="Description")
    utility_score: float = Field(..., ge=0, le=1, description="Utility score")
    agent_id: Optional[str] = Field(None, description="Managing agent ID")
    lock_state: LockState = Field(default=LockState.EDITABLE, description="Lock state")
    lock_holder_id: Optional[str] = Field(None, description="Lock holder ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class BranchDetailResponse(BranchResponse):
    """
    Detailed branch response with statistics.

    Attributes:
        Inherits all from BranchResponse
        nodes: Nodes in branch
        statistics: Branch statistics
        utility_function: Utility function parameters
        position_history: Position history for oscillation detection
    """

    nodes: Optional[List[Dict[str, Any]]] = Field(None, description="Branch nodes")
    statistics: Optional[Dict[str, Any]] = Field(None, description="Branch statistics")
    utility_function: Optional[Dict[str, Any]] = Field(None, description="Utility function")
    position_history: Optional[List[Dict[str, Any]]] = Field(None, description="Position history")


class BranchListResponse(BaseModel):
    """
    Branch list response schema.

    Attributes:
        items: List of branches
        total: Total count
        skip: Current offset
        limit: Current limit
    """

    items: List[BranchResponse] = Field(..., description="Branch list")
    total: int = Field(..., ge=0, description="Total count")
    skip: int = Field(..., ge=0, description="Current offset")
    limit: int = Field(..., ge=1, description="Current limit")


class BranchStatistics(BaseModel):
    """
    Branch statistics schema.

    Attributes:
        node_count: Number of nodes
        depth: Maximum depth
        utility_score: Current utility
        last_activity: Last modification time
        agent_actions: Agent action counts
    """

    node_count: int = Field(..., ge=0, description="Node count")
    depth: int = Field(..., ge=0, description="Max depth")
    utility_score: float = Field(..., ge=0, le=1, description="Utility score")
    last_activity: datetime = Field(..., description="Last activity")
    agent_actions: Dict[str, int] = Field(..., description="Agent action counts")


class ForkResult(BaseModel):
    """
    Fork result schema.

    Attributes:
        new_branch: Created branch
        copied_nodes: Number of nodes copied
        fork_point: Fork point node
    """

    new_branch: BranchResponse = Field(..., description="New branch")
    copied_nodes: int = Field(..., ge=0, description="Copied node count")
    fork_point: Dict[str, Any] = Field(..., description="Fork point node")


class MergeResult(BaseModel):
    """
    Merge result schema.

    Attributes:
        merged_branch: Updated target branch
        source_branch: Source branch (marked as merged)
        conflicts: Conflicts encountered
        merged_nodes: Number of nodes merged
    """

    merged_branch: BranchResponse = Field(..., description="Merged branch")
    source_branch: BranchResponse = Field(..., description="Source branch")
    conflicts: List[Dict[str, Any]] = Field(..., description="Conflicts")
    merged_nodes: int = Field(..., ge=0, description="Merged node count")


class PruneResult(BaseModel):
    """
    Prune result schema.

    Attributes:
        branch: Updated branch
        pruned_at: Prune timestamp
        reason: Prune reason
    """

    branch: BranchResponse = Field(..., description="Pruned branch")
    pruned_at: datetime = Field(..., description="Prune timestamp")
    reason: str = Field(..., description="Prune reason")


class UtilityResponse(BaseModel):
    """
    Utility response schema.

    Attributes:
        branch_id: Branch ID
        total_utility: Overall utility score
        components: Utility component breakdown
        history: Recent utility history
    """

    branch_id: str = Field(..., description="Branch ID")
    total_utility: float = Field(..., ge=0, le=1, description="Total utility")
    components: Dict[str, float] = Field(..., description="Utility components")
    history: List[Dict[str, Any]] = Field(..., description="Utility history")


class LockStatusResponse(BaseModel):
    """
    Lock status response schema.

    Attributes:
        branch_id: Branch ID
        lock_state: Current lock state
        holder_id: Lock holder ID
        holder_type: Holder type (agent, user)
        acquired_at: Lock acquisition time
        expires_at: Lock expiration time
    """

    branch_id: str = Field(..., description="Branch ID")
    lock_state: LockState = Field(..., description="Lock state")
    holder_id: Optional[str] = Field(None, description="Holder ID")
    holder_type: Optional[str] = Field(None, description="Holder type")
    acquired_at: Optional[datetime] = Field(None, description="Acquisition time")
    expires_at: Optional[datetime] = Field(None, description="Expiration time")


class LockAcquisitionResponse(BaseModel):
    """
    Lock acquisition response schema.

    Attributes:
        success: Whether lock was acquired
        lock_state: New lock state
        holder_id: Lock holder ID
        expires_at: Lock expiration time
    """

    success: bool = Field(..., description="Acquisition success")
    lock_state: LockState = Field(..., description="Lock state")
    holder_id: str = Field(..., description="Holder ID")
    expires_at: datetime = Field(..., description="Expiration time")


class BranchComparisonResponse(BaseModel):
    """
    Branch comparison response schema.

    Attributes:
        branch_a: First branch summary
        branch_b: Second branch summary
        common_ancestor: Common ancestor node
        divergence_point: Divergence point
        unique_to_a: Nodes unique to first branch
        unique_to_b: Nodes unique to second branch
        conflicts: Conflicting nodes
    """

    branch_a: Dict[str, Any] = Field(..., description="First branch")
    branch_b: Dict[str, Any] = Field(..., description="Second branch")
    common_ancestor: Optional[Dict[str, Any]] = Field(None, description="Common ancestor")
    divergence_point: Optional[Dict[str, Any]] = Field(None, description="Divergence point")
    unique_to_a: List[str] = Field(..., description="Unique to A")
    unique_to_b: List[str] = Field(..., description="Unique to B")
    conflicts: List[Dict[str, Any]] = Field(..., description="Conflicts")

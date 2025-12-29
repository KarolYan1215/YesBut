"""
Node Pydantic Schemas

Request/response schemas for node operations.

@module app/schemas/node
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class NodeType(str, Enum):
    """Node type enumeration."""

    GOAL = "goal"
    CLAIM = "claim"
    FACT = "fact"
    CONSTRAINT = "constraint"
    ATOMIC_TOPIC = "atomic_topic"
    SYNTHESIS = "synthesis"


class NodeStatus(str, Enum):
    """Node status enumeration."""

    ACTIVE = "active"
    PENDING = "pending"
    VALIDATED = "validated"
    REJECTED = "rejected"
    PRUNED = "pruned"
    MERGED = "merged"


# =============================================================================
# Request Schemas
# =============================================================================


class NodeCreate(BaseModel):
    """
    Node creation request schema.

    Attributes:
        session_id: Session ID (required)
        type: Node type (required)
        content: Node content text (required)
        parent_id: Parent node ID (optional)
        branch_id: Branch ID (optional)
        position: Visualization position
        confidence: Initial confidence score
        metadata: Additional metadata
    """

    session_id: str = Field(..., description="Session ID")
    type: NodeType = Field(..., description="Node type")
    content: str = Field(..., min_length=1, description="Node content")
    parent_id: Optional[str] = Field(None, description="Parent node ID")
    branch_id: Optional[str] = Field(None, description="Branch ID")
    position: Optional[Dict[str, float]] = Field(None, description="Position {x, y}")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="Confidence score")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class NodeUpdate(BaseModel):
    """
    Node update request schema.

    Attributes:
        content: Updated content
        confidence: Updated confidence
        utility: Updated utility value
        position: Updated position
        status: Updated status
        metadata: Updated metadata
    """

    content: Optional[str] = Field(None, min_length=1, description="Updated content")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="Updated confidence")
    utility: Optional[float] = Field(None, ge=0, le=1, description="Updated utility")
    position: Optional[Dict[str, float]] = Field(None, description="Updated position")
    status: Optional[NodeStatus] = Field(None, description="Updated status")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Updated metadata")


class NodeDecomposition(BaseModel):
    """
    Node decomposition request schema.

    Attributes:
        children: List of child node specifications
        decomposition_type: Type of decomposition (and, or, sequential)
    """

    children: List[Dict[str, Any]] = Field(..., min_items=1, description="Child nodes")
    decomposition_type: str = Field(default="and", description="Decomposition type")


class NodeFork(BaseModel):
    """
    Node fork request schema.

    Attributes:
        branch_name: Name for new branch
        content: Content for forked node (optional)
        reason: Reason for forking
    """

    branch_name: str = Field(..., min_length=1, description="New branch name")
    content: Optional[str] = Field(None, description="Forked node content")
    reason: Optional[str] = Field(None, description="Fork reason")


# =============================================================================
# Response Schemas
# =============================================================================


class NodeBase(BaseModel):
    """
    Base node schema with common fields.

    Attributes:
        id: Node unique identifier
        session_id: Session ID
        type: Node type
        content: Node content
        layer: Layer number (0 = root)
    """

    id: str = Field(..., description="Node ID")
    session_id: str = Field(..., description="Session ID")
    type: NodeType = Field(..., description="Node type")
    content: str = Field(..., description="Node content")
    layer: int = Field(..., ge=0, description="Layer number")


class NodeResponse(NodeBase):
    """
    Node response schema.

    Attributes:
        Inherits all from NodeBase
        branch_id: Branch ID
        parent_id: Parent node ID
        status: Node status
        confidence: Confidence score
        utility: Utility value
        sensitivity: Sensitivity score
        position: Visualization position
        is_preview: Whether this is a preview node
        agent_id: Creating agent ID
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    branch_id: Optional[str] = Field(None, description="Branch ID")
    parent_id: Optional[str] = Field(None, description="Parent node ID")
    status: NodeStatus = Field(..., description="Node status")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score")
    utility: float = Field(..., ge=0, le=1, description="Utility value")
    sensitivity: Optional[float] = Field(None, ge=0, le=1, description="Sensitivity score")
    position: Optional[Dict[str, float]] = Field(None, description="Position {x, y}")
    is_preview: bool = Field(default=False, description="Is preview node")
    agent_id: Optional[str] = Field(None, description="Creating agent ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class NodeDetailResponse(NodeResponse):
    """
    Detailed node response with related data.

    Attributes:
        Inherits all from NodeResponse
        incoming_edges: Edges pointing to this node
        outgoing_edges: Edges from this node
        children: Child nodes
        metadata: Full metadata
    """

    incoming_edges: Optional[List[Dict[str, Any]]] = Field(None, description="Incoming edges")
    outgoing_edges: Optional[List[Dict[str, Any]]] = Field(None, description="Outgoing edges")
    children: Optional[List["NodeResponse"]] = Field(None, description="Child nodes")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Full metadata")


class NodeListResponse(BaseModel):
    """
    Node list response schema.

    Attributes:
        items: List of nodes
        total: Total count
        skip: Current offset
        limit: Current limit
    """

    items: List[NodeResponse] = Field(..., description="Node list")
    total: int = Field(..., ge=0, description="Total count")
    skip: int = Field(..., ge=0, description="Current offset")
    limit: int = Field(..., ge=1, description="Current limit")


class NodeHistoryEntry(BaseModel):
    """
    Node history entry schema.

    Attributes:
        timestamp: When change occurred
        action: Type of change
        changes: What was changed
        agent_id: Agent that made change
        user_id: User that made change
    """

    timestamp: datetime = Field(..., description="Change timestamp")
    action: str = Field(..., description="Action type")
    changes: Dict[str, Any] = Field(..., description="Changes made")
    agent_id: Optional[str] = Field(None, description="Agent ID")
    user_id: Optional[str] = Field(None, description="User ID")


class NodeHistoryResponse(BaseModel):
    """
    Node history response schema.

    Attributes:
        node_id: Node ID
        history: List of history entries
    """

    node_id: str = Field(..., description="Node ID")
    history: List[NodeHistoryEntry] = Field(..., description="History entries")


class DecompositionResult(BaseModel):
    """
    Decomposition result schema.

    Attributes:
        parent_node: Updated parent node
        child_nodes: Created child nodes
        edges: Created decomposition edges
    """

    parent_node: NodeResponse = Field(..., description="Parent node")
    child_nodes: List[NodeResponse] = Field(..., description="Child nodes")
    edges: List[Dict[str, Any]] = Field(..., description="Created edges")


class ForkResult(BaseModel):
    """
    Fork result schema.

    Attributes:
        new_branch: Created branch
        forked_node: New node in forked branch
        original_node: Original node
    """

    new_branch: Dict[str, Any] = Field(..., description="New branch")
    forked_node: NodeResponse = Field(..., description="Forked node")
    original_node: NodeResponse = Field(..., description="Original node")


class RelatedNode(BaseModel):
    """
    Related node schema.

    Attributes:
        node: Related node data
        relationship: Relationship type
        distance: Graph distance
        path: Path from source
    """

    node: NodeResponse = Field(..., description="Related node")
    relationship: str = Field(..., description="Relationship type")
    distance: int = Field(..., ge=1, description="Graph distance")
    path: List[str] = Field(..., description="Path node IDs")


class RelatedNodesResponse(BaseModel):
    """
    Related nodes response schema.

    Attributes:
        node_id: Source node ID
        related: List of related nodes
    """

    node_id: str = Field(..., description="Source node ID")
    related: List[RelatedNode] = Field(..., description="Related nodes")

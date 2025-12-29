"""
Edge Pydantic Schemas

Request/response schemas for edge operations.

@module app/schemas/edge
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class EdgeType(str, Enum):
    """Edge type enumeration."""

    SUPPORT = "support"
    ATTACK = "attack"
    CONFLICT = "conflict"
    ENTAIL = "entail"
    DECOMPOSE = "decompose"
    DERIVE = "derive"


# =============================================================================
# Request Schemas
# =============================================================================


class EdgeCreate(BaseModel):
    """
    Edge creation request schema.

    Attributes:
        session_id: Session ID (required)
        source_id: Source node ID (required)
        target_id: Target node ID (required)
        type: Edge type (required)
        weight: Edge weight/strength (0-1)
        explanation: Explanation of relationship
        metadata: Additional metadata
    """

    session_id: str = Field(..., description="Session ID")
    source_id: str = Field(..., description="Source node ID")
    target_id: str = Field(..., description="Target node ID")
    type: EdgeType = Field(..., description="Edge type")
    weight: float = Field(default=1.0, ge=0, le=1, description="Edge weight")
    explanation: Optional[str] = Field(None, description="Relationship explanation")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class EdgeUpdate(BaseModel):
    """
    Edge update request schema.

    Attributes:
        weight: Updated weight
        explanation: Updated explanation
        validated: Validation status
        metadata: Updated metadata
    """

    weight: Optional[float] = Field(None, ge=0, le=1, description="Updated weight")
    explanation: Optional[str] = Field(None, description="Updated explanation")
    validated: Optional[bool] = Field(None, description="Validation status")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Updated metadata")


# =============================================================================
# Response Schemas
# =============================================================================


class EdgeBase(BaseModel):
    """
    Base edge schema with common fields.

    Attributes:
        id: Edge unique identifier
        session_id: Session ID
        source_id: Source node ID
        target_id: Target node ID
        type: Edge type
    """

    id: str = Field(..., description="Edge ID")
    session_id: str = Field(..., description="Session ID")
    source_id: str = Field(..., description="Source node ID")
    target_id: str = Field(..., description="Target node ID")
    type: EdgeType = Field(..., description="Edge type")


class EdgeResponse(EdgeBase):
    """
    Edge response schema.

    Attributes:
        Inherits all from EdgeBase
        weight: Edge weight
        explanation: Relationship explanation
        is_preview: Whether this is a preview edge
        validated: Validation status (for attack edges)
        agent_id: Creating agent ID
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    weight: float = Field(..., ge=0, le=1, description="Edge weight")
    explanation: Optional[str] = Field(None, description="Explanation")
    is_preview: bool = Field(default=False, description="Is preview edge")
    validated: Optional[bool] = Field(None, description="Validation status")
    agent_id: Optional[str] = Field(None, description="Creating agent ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class EdgeDetailResponse(EdgeResponse):
    """
    Detailed edge response with node data.

    Attributes:
        Inherits all from EdgeResponse
        source_node: Full source node data
        target_node: Full target node data
        metadata: Full metadata
    """

    source_node: Optional[Dict[str, Any]] = Field(None, description="Source node")
    target_node: Optional[Dict[str, Any]] = Field(None, description="Target node")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Full metadata")


class EdgeListResponse(BaseModel):
    """
    Edge list response schema.

    Attributes:
        items: List of edges
        total: Total count
        skip: Current offset
        limit: Current limit
    """

    items: List[EdgeResponse] = Field(..., description="Edge list")
    total: int = Field(..., ge=0, description="Total count")
    skip: int = Field(..., ge=0, description="Current offset")
    limit: int = Field(..., ge=1, description="Current limit")


class ConflictEdge(BaseModel):
    """
    Conflict edge with node context.

    Attributes:
        edge: Edge data
        node_a: First conflicting node
        node_b: Second conflicting node
        resolved: Whether conflict is resolved
        resolution: Resolution details (if resolved)
    """

    edge: EdgeResponse = Field(..., description="Edge data")
    node_a: Dict[str, Any] = Field(..., description="First node")
    node_b: Dict[str, Any] = Field(..., description="Second node")
    resolved: bool = Field(default=False, description="Is resolved")
    resolution: Optional[Dict[str, Any]] = Field(None, description="Resolution details")


class ConflictEdgesResponse(BaseModel):
    """
    Conflict edges response schema.

    Attributes:
        conflicts: List of conflict edges
        unresolved_count: Number of unresolved conflicts
        resolved_count: Number of resolved conflicts
    """

    conflicts: List[ConflictEdge] = Field(..., description="Conflict edges")
    unresolved_count: int = Field(..., ge=0, description="Unresolved count")
    resolved_count: int = Field(..., ge=0, description="Resolved count")


class AttackEdge(BaseModel):
    """
    Attack edge with validation context.

    Attributes:
        edge: Edge data
        attacker: Attacking node
        target: Target node
        validated: Whether attack is validated
        validation_details: Validation details
    """

    edge: EdgeResponse = Field(..., description="Edge data")
    attacker: Dict[str, Any] = Field(..., description="Attacking node")
    target: Dict[str, Any] = Field(..., description="Target node")
    validated: Optional[bool] = Field(None, description="Validation status")
    validation_details: Optional[Dict[str, Any]] = Field(None, description="Validation details")


class AttackEdgesResponse(BaseModel):
    """
    Attack edges response schema.

    Attributes:
        attacks: List of attack edges
        validated_count: Number of validated attacks
        pending_count: Number pending validation
    """

    attacks: List[AttackEdge] = Field(..., description="Attack edges")
    validated_count: int = Field(..., ge=0, description="Validated count")
    pending_count: int = Field(..., ge=0, description="Pending count")

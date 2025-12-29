"""
Node Database Model

SQLAlchemy model for graph nodes in the layered graph network.
Supports all node types: Goal, Claim, Fact, Constraint, AtomicTopic, Pending, Synthesis.
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Enum, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB, UUID, ARRAY
from datetime import datetime
import enum
import uuid

from app.models.base import Base, TimestampMixin


class NodeType(str, enum.Enum):
    """
    Enumeration of all supported node types in the graph.

    Node types:
    - GOAL: Root node representing the final decision goal
    - CLAIM: Agent-generated reasoning conclusion
    - FACT: Externally verified objective fact
    - CONSTRAINT: User-defined hard or soft constraint
    - ATOMIC_TOPIC: Indivisible atomic topic unit
    - PENDING: Top-down generated node awaiting bottom-up matching
    - SYNTHESIS: Node created from Hegelian dialectical synthesis
    """
    GOAL = "GoalNode"
    CLAIM = "ClaimNode"
    FACT = "FactNode"
    CONSTRAINT = "ConstraintNode"
    ATOMIC_TOPIC = "AtomicTopicNode"
    PENDING = "PendingNode"
    SYNTHESIS = "SynthesisNode"


class NodeStatus(str, enum.Enum):
    """
    Node status enumeration.

    Statuses:
    - ACTIVE: Node is active and visible
    - COLLAPSED: Node is hidden but can be expanded
    - SUSPENDED: Node is suspended pending more evidence
    - SOFT_DELETED: Node is soft deleted, summary retained
    - HARD_DELETED: Node is permanently deleted
    """
    ACTIVE = "active"
    COLLAPSED = "collapsed"
    SUSPENDED = "suspended"
    SOFT_DELETED = "soft_deleted"
    HARD_DELETED = "hard_deleted"


class Node(Base, TimestampMixin):
    """
    SQLAlchemy model for graph nodes.

    This model stores all node types in a single table with type-specific
    fields stored in a JSONB column for flexibility.

    Table: nodes

    Columns:
        id (str): Unique node identifier (UUID)
        session_id (str): Foreign key to sessions table
        branch_id (str): Foreign key to branches table
        type (NodeType): Node type enumeration
        label (str): Display label for the node
        layer (int): Layer index in the graph (0 = root)
        confidence (float): Confidence score (0-1)
        version (int): Version number for optimistic locking
        is_preview (bool): Whether this is a streaming preview node
        status (NodeStatus): Node status
        data (JSON): Type-specific data stored as JSONB
        created_by (str): ID of user or agent that created this node
        created_at (datetime): Creation timestamp
        updated_at (datetime): Last update timestamp

    Relationships:
        session: Many-to-one relationship with Session
        branch: Many-to-one relationship with Branch
        outgoing_edges: One-to-many relationship with Edge (as source)
        incoming_edges: One-to-many relationship with Edge (as target)

    Indexes:
        - session_id, layer (for layer-based queries)
        - session_id, branch_id (for branch-based queries)
        - session_id, type (for type filtering)
    """
    __tablename__ = "nodes"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    branch_id = Column(
        UUID(as_uuid=True),
        ForeignKey("branches.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    type = Column(
        Enum(NodeType),
        nullable=False,
        index=True,
    )
    label = Column(
        String(512),
        nullable=False,
    )
    layer = Column(
        Integer,
        default=0,
        nullable=False,
    )
    confidence = Column(
        Float,
        default=1.0,
        nullable=False,
    )
    version = Column(
        Integer,
        default=1,
        nullable=False,
    )
    is_preview = Column(
        Boolean,
        default=False,
        nullable=False,
    )
    status = Column(
        Enum(NodeStatus),
        default=NodeStatus.ACTIVE,
        nullable=False,
    )
    data = Column(
        JSONB,
        default=dict,
        nullable=False,
    )
    created_by = Column(
        String(255),
        nullable=True,
    )
    # Position for visualization
    position_x = Column(
        Float,
        default=0.0,
        nullable=False,
    )
    position_y = Column(
        Float,
        default=0.0,
        nullable=False,
    )

    # Relationships
    session = relationship(
        "Session",
        back_populates="nodes",
    )
    branch = relationship(
        "Branch",
        back_populates="nodes",
    )
    outgoing_edges = relationship(
        "Edge",
        foreign_keys="Edge.source_id",
        back_populates="source",
        cascade="all, delete-orphan",
    )
    incoming_edges = relationship(
        "Edge",
        foreign_keys="Edge.target_id",
        back_populates="target",
        cascade="all, delete-orphan",
    )

    # Indexes
    __table_args__ = (
        Index("ix_nodes_session_layer", "session_id", "layer"),
        Index("ix_nodes_session_branch", "session_id", "branch_id"),
        Index("ix_nodes_session_type", "session_id", "type"),
        Index("ix_nodes_session_status", "session_id", "status"),
    )

    def __repr__(self) -> str:
        return f"<Node(id={self.id}, type={self.type}, label='{self.label[:30]}...')>"

    def to_dict(self) -> dict:
        """
        Convert node to dictionary.

        Returns:
            dict: Node data as dictionary
        """
        return {
            "id": str(self.id),
            "session_id": str(self.session_id),
            "branch_id": str(self.branch_id) if self.branch_id else None,
            "type": self.type.value,
            "label": self.label,
            "layer": self.layer,
            "confidence": self.confidence,
            "version": self.version,
            "is_preview": self.is_preview,
            "status": self.status.value,
            "data": self.data,
            "created_by": self.created_by,
            "position": {"x": self.position_x, "y": self.position_y},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @property
    def validity(self) -> float:
        """Get validity score from data."""
        return self.data.get("validity", 1.0)

    @property
    def utility(self) -> float:
        """Get utility score from data."""
        return self.data.get("utility", 0.0)

    @property
    def novelty(self) -> float:
        """Get novelty score from data."""
        return self.data.get("novelty", 0.0)

    @property
    def evaluation_vector(self) -> tuple:
        """
        Get the four-dimensional evaluation vector.

        Returns:
            tuple: (validity, utility, confidence, novelty)
        """
        return (self.validity, self.utility, self.confidence, self.novelty)

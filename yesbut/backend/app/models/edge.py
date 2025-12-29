"""
Edge Database Model

SQLAlchemy model for graph edges in the layered graph network.
Supports vertical edges (decompose, derive) and horizontal edges (support, attack, conflict, entail).
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Enum, Index, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB, UUID
from datetime import datetime
import enum
import uuid

from app.models.base import Base, TimestampMixin


class EdgeType(str, enum.Enum):
    """
    Enumeration of edge types.

    Vertical edges (hierarchical):
    - DECOMPOSE: Parent decomposes into child
    - DERIVE: Child derives parent (bottom-up)

    Horizontal edges (same layer):
    - SUPPORT: Source supports target (positive evidence)
    - ATTACK: Source attacks target (negative evidence)
    - CONFLICT: Mutual exclusion (cannot both be true)
    - ENTAIL: Source logically implies target
    """
    DECOMPOSE = "decompose"
    DERIVE = "derive"
    SUPPORT = "support"
    ATTACK = "attack"
    CONFLICT = "conflict"
    ENTAIL = "entail"


class EdgeDirection(str, enum.Enum):
    """
    Edge direction classification.

    Directions:
    - VERTICAL: Edge connects nodes in different layers
    - HORIZONTAL: Edge connects nodes in the same layer
    """
    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"


class Edge(Base, TimestampMixin):
    """
    SQLAlchemy model for graph edges.

    Table: edges

    Columns:
        id (str): Unique edge identifier (UUID)
        session_id (str): Foreign key to sessions table
        source_id (str): Foreign key to nodes table (source node)
        target_id (str): Foreign key to nodes table (target node)
        type (EdgeType): Edge type enumeration
        weight (float): Edge weight/strength (0-1)
        explanation (str): Explanation of the relationship
        is_preview (bool): Whether this is a streaming preview edge
        validated (bool): Whether validated by ACA (for attack edges)
        version (int): Version number for optimistic locking
        data (JSONB): Additional edge metadata
        created_by (str): ID of agent that created this edge
        created_at (datetime): Creation timestamp
        updated_at (datetime): Last update timestamp

    Relationships:
        session: Many-to-one relationship with Session
        source: Many-to-one relationship with Node
        target: Many-to-one relationship with Node

    Indexes:
        - session_id, source_id (for outgoing edge lookup)
        - session_id, target_id (for incoming edge lookup)
        - session_id, type (for type filtering)

    Constraints:
        - source_id != target_id (no self-loops)
        - Unique (session_id, source_id, target_id, type)
    """
    __tablename__ = "edges"

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
    source_id = Column(
        UUID(as_uuid=True),
        ForeignKey("nodes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    target_id = Column(
        UUID(as_uuid=True),
        ForeignKey("nodes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    type = Column(
        Enum(EdgeType),
        nullable=False,
        index=True,
    )
    weight = Column(
        Float,
        default=1.0,
        nullable=False,
    )
    explanation = Column(
        String(1024),
        nullable=True,
    )
    is_preview = Column(
        Boolean,
        default=False,
        nullable=False,
    )
    validated = Column(
        Boolean,
        default=False,
        nullable=False,
    )
    version = Column(
        Integer,
        default=1,
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

    # Relationships
    session = relationship(
        "Session",
        back_populates="edges",
    )
    source = relationship(
        "Node",
        foreign_keys=[source_id],
        back_populates="outgoing_edges",
    )
    target = relationship(
        "Node",
        foreign_keys=[target_id],
        back_populates="incoming_edges",
    )

    # Indexes and Constraints
    __table_args__ = (
        Index("ix_edges_session_type", "session_id", "type"),
        Index("ix_edges_source_target", "source_id", "target_id"),
        CheckConstraint("source_id != target_id", name="ck_edges_no_self_loop"),
        UniqueConstraint("session_id", "source_id", "target_id", "type", name="uq_edges_unique_relationship"),
    )

    def __repr__(self) -> str:
        return f"<Edge(id={self.id}, type={self.type}, {self.source_id} -> {self.target_id})>"

    def to_dict(self) -> dict:
        """
        Convert edge to dictionary.

        Returns:
            dict: Edge data as dictionary
        """
        return {
            "id": str(self.id),
            "session_id": str(self.session_id),
            "source_id": str(self.source_id),
            "target_id": str(self.target_id),
            "type": self.type.value,
            "weight": self.weight,
            "explanation": self.explanation,
            "is_preview": self.is_preview,
            "validated": self.validated,
            "version": self.version,
            "data": self.data,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @property
    def direction(self) -> EdgeDirection:
        """
        Get edge direction classification.

        Returns:
            EdgeDirection: VERTICAL for decompose/derive, HORIZONTAL for others
        """
        if self.type in (EdgeType.DECOMPOSE, EdgeType.DERIVE):
            return EdgeDirection.VERTICAL
        return EdgeDirection.HORIZONTAL

    @property
    def is_vertical(self) -> bool:
        """Check if edge is vertical (layer transition)."""
        return self.direction == EdgeDirection.VERTICAL

    @property
    def is_horizontal(self) -> bool:
        """Check if edge is horizontal (same layer)."""
        return self.direction == EdgeDirection.HORIZONTAL

    @property
    def is_positive(self) -> bool:
        """Check if edge represents positive relationship (support, entail)."""
        return self.type in (EdgeType.SUPPORT, EdgeType.ENTAIL, EdgeType.DECOMPOSE, EdgeType.DERIVE)

    @property
    def is_negative(self) -> bool:
        """Check if edge represents negative relationship (attack, conflict)."""
        return self.type in (EdgeType.ATTACK, EdgeType.CONFLICT)

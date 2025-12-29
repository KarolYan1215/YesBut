"""
Branch Database Model

SQLAlchemy model for reasoning branches in the graph.
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Enum, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB, ARRAY, UUID
from datetime import datetime
import enum
import uuid

from app.models.base import Base, TimestampMixin


class BranchStatus(str, enum.Enum):
    """
    Branch status enumeration.

    Statuses:
    - ACTIVE: Branch is actively being developed
    - PAUSED: Branch is paused
    - COMPLETED: Branch has reached conclusion
    - PRUNED: Branch was pruned (low utility)
    - MERGED: Branch was merged into another
    """
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    PRUNED = "pruned"
    MERGED = "merged"


class LockState(str, enum.Enum):
    """
    Branch lock state enumeration.

    States:
    - EDITABLE: Full user control, agents paused
    - OBSERVATION: Agent working, user can only view
    - PAUSED: User triggered pause, awaiting decision
    """
    EDITABLE = "EDITABLE"
    OBSERVATION = "OBSERVATION"
    PAUSED = "PAUSED"


class Branch(Base, TimestampMixin):
    """
    SQLAlchemy model for reasoning branches.

    A branch represents a single reasoning path from root to leaves,
    managed by a Branch Manager (BM) agent.

    Table: branches

    Columns:
        id (str): Unique branch identifier (UUID)
        session_id (str): Foreign key to sessions table
        parent_branch_id (str): Foreign key to branches (for forked branches)
        root_node_id (str): Foreign key to nodes (branch root)
        name (str): Human-readable branch name
        status (BranchStatus): Current branch status
        utility_score (float): Current utility score (0-1)
        agent_id (str): ID of BM agent managing this branch
        utility_function (JSONB): Serialized utility function parameters
        position_history (JSONB): History of positions for oscillation detection
        lock_state (LockState): Current lock state
        lock_holder_id (str): ID of current lock holder (agent or user)
        lock_holder_name (str): Name of current lock holder
        lock_acquired_at (datetime): When lock was acquired
        debate_round (int): Current debate round number
        created_at (datetime): Creation timestamp
        updated_at (datetime): Last update timestamp

    Relationships:
        session: Many-to-one relationship with Session
        parent_branch: Many-to-one self-referential relationship
        child_branches: One-to-many self-referential relationship
        root_node: Many-to-one relationship with Node
        nodes: One-to-many relationship with Node (nodes in this branch)

    Indexes:
        - session_id (for session's branches lookup)
        - session_id, status (for active branches)
        - parent_branch_id (for branch hierarchy)
    """
    __tablename__ = "branches"

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
    parent_branch_id = Column(
        UUID(as_uuid=True),
        ForeignKey("branches.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    root_node_id = Column(
        UUID(as_uuid=True),
        ForeignKey("nodes.id", ondelete="SET NULL"),
        nullable=True,
    )
    name = Column(
        String(255),
        nullable=False,
    )
    status = Column(
        Enum(BranchStatus),
        default=BranchStatus.ACTIVE,
        nullable=False,
        index=True,
    )
    utility_score = Column(
        Float,
        default=0.0,
        nullable=False,
    )
    agent_id = Column(
        String(255),
        nullable=True,
    )
    utility_function = Column(
        JSONB,
        default=dict,
        nullable=False,
    )
    position_history = Column(
        JSONB,
        default=list,
        nullable=False,
    )
    lock_state = Column(
        Enum(LockState),
        default=LockState.EDITABLE,
        nullable=False,
    )
    lock_holder_id = Column(
        String(255),
        nullable=True,
    )
    lock_holder_name = Column(
        String(255),
        nullable=True,
    )
    lock_acquired_at = Column(
        DateTime,
        nullable=True,
    )
    debate_round = Column(
        Integer,
        default=0,
        nullable=False,
    )
    merged_into_id = Column(
        UUID(as_uuid=True),
        ForeignKey("branches.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relationships
    session = relationship(
        "Session",
        back_populates="branches",
    )
    parent_branch = relationship(
        "Branch",
        remote_side=[id],
        foreign_keys=[parent_branch_id],
        backref="child_branches",
    )
    merged_into = relationship(
        "Branch",
        remote_side=[id],
        foreign_keys=[merged_into_id],
    )
    nodes = relationship(
        "Node",
        back_populates="branch",
        lazy="dynamic",
    )

    # Indexes
    __table_args__ = (
        Index("ix_branches_session_status", "session_id", "status"),
    )

    def __repr__(self) -> str:
        return f"<Branch(id={self.id}, name='{self.name}', status={self.status})>"

    def to_dict(self) -> dict:
        """
        Convert branch to dictionary.

        Returns:
            dict: Branch data as dictionary
        """
        return {
            "id": str(self.id),
            "session_id": str(self.session_id),
            "parent_branch_id": str(self.parent_branch_id) if self.parent_branch_id else None,
            "root_node_id": str(self.root_node_id) if self.root_node_id else None,
            "name": self.name,
            "status": self.status.value,
            "utility_score": self.utility_score,
            "agent_id": self.agent_id,
            "utility_function": self.utility_function,
            "lock_state": self.lock_state.value,
            "lock_holder_id": self.lock_holder_id,
            "lock_holder_name": self.lock_holder_name,
            "lock_acquired_at": self.lock_acquired_at.isoformat() if self.lock_acquired_at else None,
            "debate_round": self.debate_round,
            "merged_into_id": str(self.merged_into_id) if self.merged_into_id else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @property
    def is_locked(self) -> bool:
        """Check if branch is currently locked."""
        return self.lock_state == LockState.OBSERVATION

    @property
    def is_editable(self) -> bool:
        """Check if branch is editable by user."""
        return self.lock_state == LockState.EDITABLE

    def add_position_to_history(self, position_embedding: list) -> None:
        """
        Add a position embedding to history for oscillation detection.

        Args:
            position_embedding: Embedding vector of current position
        """
        if self.position_history is None:
            self.position_history = []
        self.position_history.append({
            "round": self.debate_round,
            "embedding": position_embedding,
            "timestamp": datetime.utcnow().isoformat(),
        })

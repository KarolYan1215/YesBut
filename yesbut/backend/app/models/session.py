"""
Session Database Model

SQLAlchemy model for brainstorming sessions.
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Enum, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB, UUID
from datetime import datetime
import enum
import uuid

from app.models.base import Base, TimestampMixin


class SessionStatus(str, enum.Enum):
    """
    Session status enumeration.

    Statuses:
    - DRAFT: Session created but not started
    - ACTIVE: Session is actively processing
    - PAUSED: Session paused by user
    - COMPLETED: Session finished successfully
    - FAILED: Session failed due to error
    """
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class SessionPhase(str, enum.Enum):
    """
    Session phase enumeration (three-phase pipeline).

    Phases:
    - DIVERGENCE: Large-scale idea generation
    - FILTERING: Multi-objective Pareto filtering
    - CONVERGENCE: Multi-agent game-theoretic convergence
    """
    DIVERGENCE = "divergence"
    FILTERING = "filtering"
    CONVERGENCE = "convergence"


class SessionMode(str, enum.Enum):
    """
    Session interaction mode.

    Modes:
    - SYNC: Synchronous, user participates in real-time
    - ASYNC: Asynchronous, background processing
    """
    SYNC = "sync"
    ASYNC = "async"


class Session(Base, TimestampMixin):
    """
    SQLAlchemy model for brainstorming sessions.

    Table: sessions

    Columns:
        id (str): Unique session identifier (UUID)
        user_id (str): Foreign key to users table
        title (str): Session title
        description (str): Initial requirement/goal description
        status (SessionStatus): Current session status
        phase (SessionPhase): Current pipeline phase
        mode (SessionMode): Interaction mode (sync/async)
        phase_progress (float): Progress within current phase (0-1)
        config (JSONB): Session configuration options
        created_at (datetime): Creation timestamp
        updated_at (datetime): Last update timestamp
        completed_at (datetime): Completion timestamp (if completed)

    Relationships:
        nodes: One-to-many relationship with Node
        edges: One-to-many relationship with Edge
        branches: One-to-many relationship with Branch

    Indexes:
        - user_id (for user's sessions lookup)
        - status (for filtering by status)
        - created_at (for sorting)
    """
    __tablename__ = "sessions"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    user_id = Column(
        UUID(as_uuid=True),
        nullable=True,  # Allow anonymous sessions for MVP
        index=True,
    )
    title = Column(
        String(255),
        nullable=False,
    )
    description = Column(
        String(4096),
        nullable=True,
    )
    status = Column(
        Enum(SessionStatus),
        default=SessionStatus.DRAFT,
        nullable=False,
        index=True,
    )
    phase = Column(
        Enum(SessionPhase),
        default=SessionPhase.DIVERGENCE,
        nullable=False,
    )
    mode = Column(
        Enum(SessionMode),
        default=SessionMode.ASYNC,
        nullable=False,
    )
    phase_progress = Column(
        Float,
        default=0.0,
        nullable=False,
    )
    config = Column(
        JSONB,
        default=dict,
        nullable=False,
    )
    completed_at = Column(
        DateTime,
        nullable=True,
    )

    # Relationships
    nodes = relationship(
        "Node",
        back_populates="session",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
    edges = relationship(
        "Edge",
        back_populates="session",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
    branches = relationship(
        "Branch",
        back_populates="session",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    # Indexes
    __table_args__ = (
        Index("ix_sessions_user_status", "user_id", "status"),
        Index("ix_sessions_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Session(id={self.id}, title='{self.title}', status={self.status})>"

    def to_dict(self) -> dict:
        """
        Convert session to dictionary.

        Returns:
            dict: Session data as dictionary
        """
        return {
            "id": str(self.id),
            "user_id": str(self.user_id) if self.user_id else None,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "phase": self.phase.value,
            "mode": self.mode.value,
            "phase_progress": self.phase_progress,
            "config": self.config,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }

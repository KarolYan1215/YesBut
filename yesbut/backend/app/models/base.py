"""
Base Model Class

Provides common functionality for all SQLAlchemy models.
"""

from datetime import datetime
from typing import Any
from sqlalchemy import Column, DateTime, String
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()


class TimestampMixin:
    """
    Mixin providing created_at and updated_at timestamps.
    """
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class UUIDMixin:
    """
    Mixin providing UUID primary key.
    """
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )


def generate_uuid() -> str:
    """
    Generate a new UUID string.

    Returns:
        str: UUID string
    """
    return str(uuid.uuid4())

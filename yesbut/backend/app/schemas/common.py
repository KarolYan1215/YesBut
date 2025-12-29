"""
Common Pydantic Schemas

Shared schemas used across multiple modules.

@module app/schemas/common
"""

from typing import Optional, List, Dict, Any, Generic, TypeVar
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


# Generic type for paginated responses
T = TypeVar("T")


class TimestampMixin(BaseModel):
    """
    Mixin for timestamp fields.

    Attributes:
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class PaginationParams(BaseModel):
    """
    Pagination parameters schema.

    Attributes:
        skip: Number of items to skip (offset)
        limit: Maximum number of items to return
    """

    skip: int = Field(default=0, ge=0, description="Number of items to skip")
    limit: int = Field(default=20, ge=1, le=100, description="Maximum items to return")


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Generic paginated response schema.

    Attributes:
        items: List of items
        total: Total count of items matching query
        skip: Current offset
        limit: Current limit
        has_more: Whether more items exist
    """

    items: List[T] = Field(..., description="List of items")
    total: int = Field(..., ge=0, description="Total count matching query")
    skip: int = Field(..., ge=0, description="Current offset")
    limit: int = Field(..., ge=1, description="Current limit")
    has_more: bool = Field(..., description="Whether more items exist")


class ErrorResponse(BaseModel):
    """
    Standard error response schema.

    Attributes:
        code: Machine-readable error code
        message: Human-readable error message
        details: Additional error details
    """

    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional details")


class SuccessResponse(BaseModel):
    """
    Generic success response schema.

    Attributes:
        success: Always True for success responses
        message: Optional success message
        data: Optional response data
    """

    success: bool = Field(True, description="Success indicator")
    message: Optional[str] = Field(None, description="Success message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")


class DeleteResponse(BaseModel):
    """
    Delete operation response schema.

    Attributes:
        deleted: Whether deletion was successful
        deleted_id: ID of deleted resource
        deleted_count: Number of items deleted (for batch operations)
    """

    deleted: bool = Field(..., description="Whether deletion succeeded")
    deleted_id: Optional[str] = Field(None, description="ID of deleted resource")
    deleted_count: Optional[int] = Field(None, description="Number of items deleted")


class BatchOperationResult(BaseModel):
    """
    Batch operation result schema.

    Attributes:
        successful: List of successfully processed items
        failed: List of failed items with error details
        total_successful: Count of successful operations
        total_failed: Count of failed operations
    """

    successful: List[Dict[str, Any]] = Field(..., description="Successfully processed items")
    failed: List[Dict[str, Any]] = Field(..., description="Failed items with errors")
    total_successful: int = Field(..., ge=0, description="Successful count")
    total_failed: int = Field(..., ge=0, description="Failed count")


class Position(BaseModel):
    """
    2D position schema for graph visualization.

    Attributes:
        x: X coordinate
        y: Y coordinate
    """

    x: float = Field(..., description="X coordinate")
    y: float = Field(..., description="Y coordinate")


class BoundingBox(BaseModel):
    """
    Bounding box schema for graph layout.

    Attributes:
        min_x: Minimum X coordinate
        min_y: Minimum Y coordinate
        max_x: Maximum X coordinate
        max_y: Maximum Y coordinate
    """

    min_x: float = Field(..., description="Minimum X")
    min_y: float = Field(..., description="Minimum Y")
    max_x: float = Field(..., description="Maximum X")
    max_y: float = Field(..., description="Maximum Y")


class HealthStatus(str, Enum):
    """Health check status enumeration."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class HealthCheckResponse(BaseModel):
    """
    Health check response schema.

    Attributes:
        status: Overall health status
        version: Application version
        timestamp: Check timestamp
        components: Individual component health
    """

    status: HealthStatus = Field(..., description="Overall health status")
    version: str = Field(..., description="Application version")
    timestamp: datetime = Field(..., description="Check timestamp")
    components: Dict[str, Dict[str, Any]] = Field(..., description="Component health")


class TaskStatus(str, Enum):
    """Background task status enumeration."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskResponse(BaseModel):
    """
    Background task response schema.

    Attributes:
        task_id: Unique task identifier
        status: Current task status
        progress: Task progress (0-100)
        result: Task result (if completed)
        error: Error message (if failed)
        created_at: Task creation time
        completed_at: Task completion time
    """

    task_id: str = Field(..., description="Task ID")
    status: TaskStatus = Field(..., description="Task status")
    progress: Optional[float] = Field(None, ge=0, le=100, description="Progress percentage")
    result: Optional[Dict[str, Any]] = Field(None, description="Task result")
    error: Optional[str] = Field(None, description="Error message")
    created_at: datetime = Field(..., description="Creation time")
    completed_at: Optional[datetime] = Field(None, description="Completion time")

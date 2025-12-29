"""
Core Package

Core utilities, security, and exception handling.

Modules:
    exceptions: Custom exception classes and handlers
    security: JWT, password hashing, and authentication utilities

@package app.core
"""

from app.core.exceptions import (
    YesButException,
    AuthenticationError,
    AuthorizationError,
    ResourceNotFoundError,
    SessionNotFoundError,
    NodeNotFoundError,
    EdgeNotFoundError,
    BranchNotFoundError,
    LockAcquisitionError,
    ValidationError,
    register_exception_handlers,
)

__all__ = [
    "YesButException",
    "AuthenticationError",
    "AuthorizationError",
    "ResourceNotFoundError",
    "SessionNotFoundError",
    "NodeNotFoundError",
    "EdgeNotFoundError",
    "BranchNotFoundError",
    "LockAcquisitionError",
    "ValidationError",
    "register_exception_handlers",
]

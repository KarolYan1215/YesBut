"""
Unified Exception Handling Module

Custom exception classes and exception handlers for the application.
Provides consistent error responses across all API endpoints.

@module app/core/exceptions
"""

from typing import Optional, Dict, Any, List
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


class YesButException(Exception):
    """
    Base exception class for all YesBut application exceptions.

    All custom exceptions should inherit from this class to ensure
    consistent error handling and response formatting.

    Attributes:
        message: Human-readable error message
        code: Machine-readable error code (e.g., "SESSION_NOT_FOUND")
        status_code: HTTP status code for the response
        details: Additional error details (optional)
        headers: Additional response headers (optional)

    Example:
        raise YesButException(
            message="Session not found",
            code="SESSION_NOT_FOUND",
            status_code=404,
            details={"session_id": "abc123"}
        )
    """

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        """
        Initialize YesButException.

        Args:
            message: Human-readable error message
            code: Machine-readable error code
            status_code: HTTP status code
            details: Additional error details
            headers: Additional response headers
        """
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        self.headers = headers
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert exception to dictionary for JSON response.

        Returns:
            Dict[str, Any]: Error response dictionary with code, message, and details
        """
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details,
        }


# =============================================================================
# Authentication & Authorization Exceptions
# =============================================================================


class AuthenticationError(YesButException):
    """
    Exception raised when authentication fails.

    Used for invalid credentials, expired tokens, or missing authentication.

    Attributes:
        Inherits all attributes from YesButException
        Default status_code: 401 Unauthorized
        Default code: "AUTHENTICATION_FAILED"
    """

    def __init__(
        self,
        message: str = "Authentication failed",
        code: str = "AUTHENTICATION_FAILED",
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize AuthenticationError.

        Args:
            message: Error message (default: "Authentication failed")
            code: Error code (default: "AUTHENTICATION_FAILED")
            details: Additional error details
        """
        super().__init__(
            message=message,
            code=code,
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details,
            headers={"WWW-Authenticate": "Bearer"},
        )


class AuthorizationError(YesButException):
    """
    Exception raised when authorization fails.

    Used when user lacks permission to access a resource or perform an action.

    Attributes:
        Inherits all attributes from YesButException
        Default status_code: 403 Forbidden
        Default code: "AUTHORIZATION_FAILED"
    """

    def __init__(
        self,
        message: str = "You do not have permission to perform this action",
        code: str = "AUTHORIZATION_FAILED",
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize AuthorizationError.

        Args:
            message: Error message
            code: Error code
            details: Additional error details
        """
        super().__init__(
            message=message,
            code=code,
            status_code=status.HTTP_403_FORBIDDEN,
            details=details,
        )


class TokenExpiredError(AuthenticationError):
    """
    Exception raised when JWT token has expired.

    Attributes:
        Default code: "TOKEN_EXPIRED"
    """

    def __init__(self, message: str = "Token has expired"):
        """
        Initialize TokenExpiredError.

        Args:
            message: Error message
        """
        super().__init__(message=message, code="TOKEN_EXPIRED")


class InvalidTokenError(AuthenticationError):
    """
    Exception raised when JWT token is invalid.

    Attributes:
        Default code: "INVALID_TOKEN"
    """

    def __init__(self, message: str = "Invalid token"):
        """
        Initialize InvalidTokenError.

        Args:
            message: Error message
        """
        super().__init__(message=message, code="INVALID_TOKEN")


# =============================================================================
# Resource Exceptions
# =============================================================================


class ResourceNotFoundError(YesButException):
    """
    Exception raised when a requested resource is not found.

    Attributes:
        resource_type: Type of resource (e.g., "Session", "Node", "Branch")
        resource_id: ID of the resource that was not found
        Default status_code: 404 Not Found
    """

    def __init__(
        self,
        resource_type: str,
        resource_id: str,
        message: Optional[str] = None,
    ):
        """
        Initialize ResourceNotFoundError.

        Args:
            resource_type: Type of resource (e.g., "Session", "Node")
            resource_id: ID of the resource
            message: Custom error message (optional)
        """
        self.resource_type = resource_type
        self.resource_id = resource_id
        super().__init__(
            message=message or f"{resource_type} with ID '{resource_id}' not found",
            code=f"{resource_type.upper()}_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"resource_type": resource_type, "resource_id": resource_id},
        )


class ResourceAlreadyExistsError(YesButException):
    """
    Exception raised when attempting to create a resource that already exists.

    Attributes:
        resource_type: Type of resource
        identifier: Identifier that already exists
        Default status_code: 409 Conflict
    """

    def __init__(
        self,
        resource_type: str,
        identifier: str,
        message: Optional[str] = None,
    ):
        """
        Initialize ResourceAlreadyExistsError.

        Args:
            resource_type: Type of resource
            identifier: Identifier that already exists
            message: Custom error message (optional)
        """
        super().__init__(
            message=message or f"{resource_type} with identifier '{identifier}' already exists",
            code=f"{resource_type.upper()}_ALREADY_EXISTS",
            status_code=status.HTTP_409_CONFLICT,
            details={"resource_type": resource_type, "identifier": identifier},
        )


# =============================================================================
# Session Exceptions
# =============================================================================


class SessionNotFoundError(ResourceNotFoundError):
    """
    Exception raised when a session is not found.
    """

    def __init__(self, session_id: str):
        """
        Initialize SessionNotFoundError.

        Args:
            session_id: ID of the session that was not found
        """
        super().__init__(resource_type="Session", resource_id=session_id)


class SessionStateError(YesButException):
    """
    Exception raised when session is in an invalid state for the requested operation.

    Attributes:
        session_id: ID of the session
        current_state: Current state of the session
        required_state: Required state for the operation
        Default status_code: 409 Conflict
    """

    def __init__(
        self,
        session_id: str,
        current_state: str,
        required_state: str,
        message: Optional[str] = None,
    ):
        """
        Initialize SessionStateError.

        Args:
            session_id: ID of the session
            current_state: Current state of the session
            required_state: Required state for the operation
            message: Custom error message (optional)
        """
        super().__init__(
            message=message or f"Session is in '{current_state}' state, but '{required_state}' is required",
            code="INVALID_SESSION_STATE",
            status_code=status.HTTP_409_CONFLICT,
            details={
                "session_id": session_id,
                "current_state": current_state,
                "required_state": required_state,
            },
        )


# =============================================================================
# Lock Exceptions
# =============================================================================


class LockAcquisitionError(YesButException):
    """
    Exception raised when unable to acquire a lock.

    Used for distributed locking failures in Redis.

    Attributes:
        resource_type: Type of resource being locked
        resource_id: ID of the resource
        holder_id: ID of current lock holder (if known)
        Default status_code: 423 Locked
    """

    def __init__(
        self,
        resource_type: str,
        resource_id: str,
        holder_id: Optional[str] = None,
        message: Optional[str] = None,
    ):
        """
        Initialize LockAcquisitionError.

        Args:
            resource_type: Type of resource being locked
            resource_id: ID of the resource
            holder_id: ID of current lock holder (optional)
            message: Custom error message (optional)
        """
        super().__init__(
            message=message or f"Unable to acquire lock on {resource_type} '{resource_id}'",
            code="LOCK_ACQUISITION_FAILED",
            status_code=status.HTTP_423_LOCKED,
            details={
                "resource_type": resource_type,
                "resource_id": resource_id,
                "holder_id": holder_id,
            },
        )


class LockNotHeldError(YesButException):
    """
    Exception raised when attempting to release a lock not held by the requester.

    Attributes:
        Default status_code: 409 Conflict
    """

    def __init__(
        self,
        resource_type: str,
        resource_id: str,
        requester_id: str,
    ):
        """
        Initialize LockNotHeldError.

        Args:
            resource_type: Type of resource
            resource_id: ID of the resource
            requester_id: ID of the requester attempting to release
        """
        super().__init__(
            message=f"Lock on {resource_type} '{resource_id}' is not held by requester",
            code="LOCK_NOT_HELD",
            status_code=status.HTTP_409_CONFLICT,
            details={
                "resource_type": resource_type,
                "resource_id": resource_id,
                "requester_id": requester_id,
            },
        )


# =============================================================================
# Graph Exceptions
# =============================================================================


class NodeNotFoundError(ResourceNotFoundError):
    """
    Exception raised when a node is not found.
    """

    def __init__(self, node_id: str):
        """
        Initialize NodeNotFoundError.

        Args:
            node_id: ID of the node that was not found
        """
        super().__init__(resource_type="Node", resource_id=node_id)


class EdgeNotFoundError(ResourceNotFoundError):
    """
    Exception raised when an edge is not found.
    """

    def __init__(self, edge_id: str):
        """
        Initialize EdgeNotFoundError.

        Args:
            edge_id: ID of the edge that was not found
        """
        super().__init__(resource_type="Edge", resource_id=edge_id)


class BranchNotFoundError(ResourceNotFoundError):
    """
    Exception raised when a branch is not found.
    """

    def __init__(self, branch_id: str):
        """
        Initialize BranchNotFoundError.

        Args:
            branch_id: ID of the branch that was not found
        """
        super().__init__(resource_type="Branch", resource_id=branch_id)


class InvalidGraphOperationError(YesButException):
    """
    Exception raised when an invalid graph operation is attempted.

    Examples:
    - Creating a cycle in a DAG
    - Connecting nodes from different sessions
    - Invalid edge type for node types

    Attributes:
        operation: Description of the attempted operation
        Default status_code: 400 Bad Request
    """

    def __init__(
        self,
        operation: str,
        reason: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize InvalidGraphOperationError.

        Args:
            operation: Description of the attempted operation
            reason: Reason why the operation is invalid
            details: Additional error details
        """
        super().__init__(
            message=f"Invalid graph operation '{operation}': {reason}",
            code="INVALID_GRAPH_OPERATION",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"operation": operation, "reason": reason, **(details or {})},
        )


# =============================================================================
# Agent Exceptions
# =============================================================================


class AgentExecutionError(YesButException):
    """
    Exception raised when an agent execution fails.

    Attributes:
        agent_type: Type of agent that failed
        agent_id: ID of the agent instance
        Default status_code: 500 Internal Server Error
    """

    def __init__(
        self,
        agent_type: str,
        agent_id: str,
        reason: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize AgentExecutionError.

        Args:
            agent_type: Type of agent (e.g., "GEN", "ISA", "ACA")
            agent_id: ID of the agent instance
            reason: Reason for the failure
            details: Additional error details
        """
        super().__init__(
            message=f"Agent {agent_type} ({agent_id}) execution failed: {reason}",
            code="AGENT_EXECUTION_FAILED",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"agent_type": agent_type, "agent_id": agent_id, "reason": reason, **(details or {})},
        )


class AgentTimeoutError(AgentExecutionError):
    """
    Exception raised when an agent execution times out.

    Attributes:
        timeout_seconds: Timeout duration in seconds
    """

    def __init__(
        self,
        agent_type: str,
        agent_id: str,
        timeout_seconds: int,
    ):
        """
        Initialize AgentTimeoutError.

        Args:
            agent_type: Type of agent
            agent_id: ID of the agent instance
            timeout_seconds: Timeout duration in seconds
        """
        super().__init__(
            agent_type=agent_type,
            agent_id=agent_id,
            reason=f"Execution timed out after {timeout_seconds} seconds",
            details={"timeout_seconds": timeout_seconds},
        )


# =============================================================================
# Validation Exceptions
# =============================================================================


class ValidationError(YesButException):
    """
    Exception raised when input validation fails.

    Attributes:
        errors: List of validation error details
        Default status_code: 422 Unprocessable Entity
    """

    def __init__(
        self,
        errors: List[Dict[str, Any]],
        message: str = "Validation failed",
    ):
        """
        Initialize ValidationError.

        Args:
            errors: List of validation error details
            message: Error message
        """
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"errors": errors},
        )


# =============================================================================
# Exception Handlers
# =============================================================================


async def yesbut_exception_handler(request: Request, exc: YesButException) -> JSONResponse:
    """
    Handle YesButException and return consistent JSON response.

    Args:
        request: FastAPI request object
        exc: YesButException instance

    Returns:
        JSONResponse: Formatted error response with code, message, and details
    """
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict(),
        headers=exc.headers,
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    Handle Starlette HTTPException and convert to consistent format.

    Args:
        request: FastAPI request object
        exc: StarletteHTTPException instance

    Returns:
        JSONResponse: Formatted error response
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": f"HTTP_{exc.status_code}",
            "message": str(exc.detail),
            "details": {},
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handle Pydantic validation errors and convert to consistent format.

    Args:
        request: FastAPI request object
        exc: RequestValidationError instance

    Returns:
        JSONResponse: Formatted error response with validation details
    """
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
        })
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "code": "VALIDATION_ERROR",
            "message": "Request validation failed",
            "details": {"errors": errors},
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle unexpected exceptions and return generic error response.

    Logs the full exception for debugging while returning safe error to client.

    Args:
        request: FastAPI request object
        exc: Exception instance

    Returns:
        JSONResponse: Generic error response (500 Internal Server Error)
    """
    import logging
    logging.exception(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": "INTERNAL_ERROR",
            "message": "An unexpected error occurred",
            "details": {},
        },
    )


def register_exception_handlers(app) -> None:
    """
    Register all exception handlers with the FastAPI application.

    Should be called during application startup.

    Args:
        app: FastAPI application instance
    """
    app.add_exception_handler(YesButException, yesbut_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

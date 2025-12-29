"""
Agent Streaming Utilities Module

Utilities for streaming agent outputs via SSE.

@module agents/streaming
"""

from typing import Optional, Dict, Any, AsyncGenerator, Callable, List
from datetime import datetime
from enum import Enum
import json
import uuid
import asyncio
from functools import wraps


class StreamEventType(str, Enum):
    """Stream event type enumeration."""

    # Node events
    NODE_CREATED = "node_created"
    NODE_UPDATED = "node_updated"
    NODE_DELETED = "node_deleted"
    NODE_PREVIEW = "node_preview"

    # Edge events
    EDGE_CREATED = "edge_created"
    EDGE_UPDATED = "edge_updated"
    EDGE_DELETED = "edge_deleted"
    EDGE_PREVIEW = "edge_preview"

    # Branch events
    BRANCH_CREATED = "branch_created"
    BRANCH_UPDATED = "branch_updated"
    BRANCH_DELETED = "branch_deleted"
    BRANCH_FORKED = "branch_forked"
    BRANCH_MERGED = "branch_merged"
    BRANCH_PRUNED = "branch_pruned"

    # Agent events
    AGENT_STARTED = "agent_started"
    AGENT_COMPLETED = "agent_completed"
    AGENT_ERROR = "agent_error"
    AGENT_THINKING = "agent_thinking"

    # Session events
    PHASE_CHANGED = "phase_changed"
    PROGRESS_UPDATED = "progress_updated"
    SESSION_COMPLETED = "session_completed"

    # Lock events
    LOCK_ACQUIRED = "lock_acquired"
    LOCK_RELEASED = "lock_released"
    LOCK_EXPIRED = "lock_expired"

    # System events
    HEARTBEAT = "heartbeat"
    ERROR = "error"
    RECONNECT = "reconnect"


class StreamEvent:
    """
    Stream event wrapper.

    Represents a single SSE event with type, data, and metadata.

    Attributes:
        event_type: Type of event
        data: Event payload data
        event_id: Unique event ID for resumption
        timestamp: Event timestamp
        session_id: Associated session ID
        agent_id: Associated agent ID (if applicable)
    """

    def __init__(
        self,
        event_type: StreamEventType,
        data: Dict[str, Any],
        event_id: Optional[str] = None,
        session_id: Optional[str] = None,
        agent_id: Optional[str] = None,
    ):
        """
        Initialize stream event.

        Args:
            event_type: Type of event
            data: Event payload
            event_id: Unique event ID
            session_id: Session ID
            agent_id: Agent ID
        """
        self.event_type = event_type
        self.data = data
        self.event_id = event_id or str(uuid.uuid4())
        self.session_id = session_id
        self.agent_id = agent_id
        self.timestamp = datetime.utcnow().isoformat()

    def to_sse(self) -> str:
        """
        Convert to SSE format string.

        Returns:
            str: SSE formatted event string

        Format:
            id: {event_id}
            event: {event_type}
            data: {json_data}
        """
        lines = []
        lines.append(f"id: {self.event_id}")
        lines.append(f"event: {self.event_type.value if isinstance(self.event_type, StreamEventType) else self.event_type}")
        lines.append(f"data: {json.dumps(self.to_dict())}")
        lines.append("")  # Empty line to end event
        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary.

        Returns:
            Dict: Event as dictionary
        """
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value if isinstance(self.event_type, StreamEventType) else self.event_type,
            "session_id": self.session_id,
            "agent_id": self.agent_id,
            "timestamp": self.timestamp,
            "data": self.data,
        }


class StreamBuffer:
    """
    Buffer for managing stream events.

    Provides buffering and batching of events for efficient streaming.

    Attributes:
        max_size: Maximum buffer size
        flush_interval: Interval for automatic flushing (seconds)
        events: Buffered events
    """

    def __init__(
        self,
        max_size: int = 100,
        flush_interval: float = 0.1,
    ):
        """
        Initialize stream buffer.

        Args:
            max_size: Maximum events to buffer
            flush_interval: Auto-flush interval in seconds
        """
        self.max_size = max_size
        self.flush_interval = flush_interval
        self.events: List[StreamEvent] = []
        self._last_flush = datetime.utcnow()

    def add(self, event: StreamEvent) -> bool:
        """
        Add event to buffer.

        Args:
            event: Event to add

        Returns:
            bool: True if buffer should be flushed
        """
        self.events.append(event)

        # Check if should flush
        should_flush = (
            len(self.events) >= self.max_size or
            (datetime.utcnow() - self._last_flush).total_seconds() >= self.flush_interval
        )

        return should_flush

    def flush(self) -> List[StreamEvent]:
        """
        Flush and return all buffered events.

        Returns:
            list: List of buffered events
        """
        events = self.events.copy()
        self.events = []
        self._last_flush = datetime.utcnow()
        return events

    def clear(self) -> None:
        """Clear the buffer."""
        self.events = []
        self._last_flush = datetime.utcnow()

    def __len__(self) -> int:
        return len(self.events)


class StreamManager:
    """
    Manager for agent output streaming.

    Coordinates streaming of agent outputs to connected clients.

    Attributes:
        redis: Redis client for pub/sub
        session_streams: Active session streams
    """

    def __init__(self, redis=None):
        """
        Initialize stream manager.

        Args:
            redis: Redis client for pub/sub
        """
        self.redis = redis
        self.session_streams: Dict[str, asyncio.Queue] = {}
        self._event_history: Dict[str, List[StreamEvent]] = {}
        self._max_history = 100

    async def publish_event(
        self,
        session_id: str,
        event: StreamEvent,
    ) -> None:
        """
        Publish event to session stream.

        Publishes event via Redis pub/sub for distribution to all
        connected clients.

        Args:
            session_id: Session ID
            event: Event to publish
        """
        event.session_id = session_id

        # Store in history for resumption
        if session_id not in self._event_history:
            self._event_history[session_id] = []
        self._event_history[session_id].append(event)

        # Trim history
        if len(self._event_history[session_id]) > self._max_history:
            self._event_history[session_id] = self._event_history[session_id][-self._max_history:]

        # Publish via Redis if available
        if self.redis:
            channel = self.get_channel_name(session_id)
            await self.redis.publish(channel, json.dumps(event.to_dict()))

        # Also publish to local queue if exists
        if session_id in self.session_streams:
            await self.session_streams[session_id].put(event)

    async def subscribe_session(
        self,
        session_id: str,
        last_event_id: Optional[str] = None,
    ) -> AsyncGenerator[StreamEvent, None]:
        """
        Subscribe to session event stream.

        Yields events for the specified session. Supports resumption
        from last_event_id.

        Args:
            session_id: Session ID to subscribe to
            last_event_id: Last received event ID for resumption

        Yields:
            StreamEvent: Stream events
        """
        # Create queue for this session
        if session_id not in self.session_streams:
            self.session_streams[session_id] = asyncio.Queue()

        queue = self.session_streams[session_id]

        # Replay missed events if resuming
        if last_event_id and session_id in self._event_history:
            found = False
            for event in self._event_history[session_id]:
                if found:
                    yield event
                elif event.event_id == last_event_id:
                    found = True

        # Subscribe to Redis if available
        if self.redis:
            channel = self.get_channel_name(session_id)
            pubsub = await self.redis.subscribe(channel)

            try:
                async for message in pubsub.listen():
                    if message["type"] == "message":
                        data = json.loads(message["data"])
                        event = StreamEvent(
                            event_type=StreamEventType(data["event_type"]),
                            data=data["data"],
                            event_id=data["event_id"],
                            session_id=data["session_id"],
                            agent_id=data.get("agent_id"),
                        )
                        yield event
            finally:
                await pubsub.unsubscribe(channel)
        else:
            # Use local queue
            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield event
                except asyncio.TimeoutError:
                    # Send heartbeat
                    yield create_heartbeat_event(session_id)

    async def unsubscribe_session(self, session_id: str) -> None:
        """
        Unsubscribe from session stream.

        Args:
            session_id: Session ID
        """
        if session_id in self.session_streams:
            del self.session_streams[session_id]

    async def broadcast_to_session(
        self,
        session_id: str,
        event_type: StreamEventType,
        data: Dict[str, Any],
    ) -> None:
        """
        Broadcast event to all session subscribers.

        Args:
            session_id: Session ID
            event_type: Event type
            data: Event data
        """
        event = StreamEvent(
            event_type=event_type,
            data=data,
            session_id=session_id,
        )
        await self.publish_event(session_id, event)

    def get_channel_name(self, session_id: str) -> str:
        """
        Get Redis channel name for session.

        Args:
            session_id: Session ID

        Returns:
            str: Channel name
        """
        return f"yesbut:session:{session_id}:events"


# =============================================================================
# Event Factory Functions
# =============================================================================


def create_node_event(
    event_type: StreamEventType,
    node_data: Dict[str, Any],
    session_id: str,
    agent_id: Optional[str] = None,
) -> StreamEvent:
    """
    Create a node-related stream event.

    Args:
        event_type: Event type (NODE_CREATED, NODE_UPDATED, etc.)
        node_data: Node data
        session_id: Session ID
        agent_id: Agent ID

    Returns:
        StreamEvent: Node event
    """
    return StreamEvent(
        event_type=event_type,
        data={"node": node_data},
        session_id=session_id,
        agent_id=agent_id,
    )


def create_edge_event(
    event_type: StreamEventType,
    edge_data: Dict[str, Any],
    session_id: str,
    agent_id: Optional[str] = None,
) -> StreamEvent:
    """
    Create an edge-related stream event.

    Args:
        event_type: Event type
        edge_data: Edge data
        session_id: Session ID
        agent_id: Agent ID

    Returns:
        StreamEvent: Edge event
    """
    return StreamEvent(
        event_type=event_type,
        data={"edge": edge_data},
        session_id=session_id,
        agent_id=agent_id,
    )


def create_branch_event(
    event_type: StreamEventType,
    branch_data: Dict[str, Any],
    session_id: str,
    agent_id: Optional[str] = None,
) -> StreamEvent:
    """
    Create a branch-related stream event.

    Args:
        event_type: Event type
        branch_data: Branch data
        session_id: Session ID
        agent_id: Agent ID

    Returns:
        StreamEvent: Branch event
    """
    return StreamEvent(
        event_type=event_type,
        data={"branch": branch_data},
        session_id=session_id,
        agent_id=agent_id,
    )


def create_agent_event(
    event_type: StreamEventType,
    agent_type: str,
    agent_id: str,
    session_id: str,
    data: Optional[Dict[str, Any]] = None,
) -> StreamEvent:
    """
    Create an agent-related stream event.

    Args:
        event_type: Event type
        agent_type: Type of agent
        agent_id: Agent ID
        session_id: Session ID
        data: Additional data

    Returns:
        StreamEvent: Agent event
    """
    return StreamEvent(
        event_type=event_type,
        data={
            "agent_type": agent_type,
            **(data or {}),
        },
        session_id=session_id,
        agent_id=agent_id,
    )


def create_phase_event(
    previous_phase: str,
    current_phase: str,
    session_id: str,
    progress: float = 0.0,
) -> StreamEvent:
    """
    Create a phase change event.

    Args:
        previous_phase: Previous phase
        current_phase: New phase
        session_id: Session ID
        progress: Initial progress in new phase

    Returns:
        StreamEvent: Phase change event
    """
    return StreamEvent(
        event_type=StreamEventType.PHASE_CHANGED,
        data={
            "previous_phase": previous_phase,
            "current_phase": current_phase,
            "progress": progress,
        },
        session_id=session_id,
    )


def create_heartbeat_event(session_id: str) -> StreamEvent:
    """
    Create a heartbeat event.

    Used to keep SSE connection alive.

    Args:
        session_id: Session ID

    Returns:
        StreamEvent: Heartbeat event
    """
    return StreamEvent(
        event_type=StreamEventType.HEARTBEAT,
        data={"timestamp": datetime.utcnow().isoformat()},
        session_id=session_id,
    )


def create_error_event(
    error_message: str,
    session_id: str,
    error_code: Optional[str] = None,
    agent_id: Optional[str] = None,
) -> StreamEvent:
    """
    Create an error event.

    Args:
        error_message: Error message
        session_id: Session ID
        error_code: Error code
        agent_id: Agent ID (if agent-related)

    Returns:
        StreamEvent: Error event
    """
    return StreamEvent(
        event_type=StreamEventType.ERROR,
        data={
            "message": error_message,
            "code": error_code,
        },
        session_id=session_id,
        agent_id=agent_id,
    )


def create_progress_event(
    session_id: str,
    progress: float,
    phase: str,
    message: Optional[str] = None,
) -> StreamEvent:
    """
    Create a progress update event.

    Args:
        session_id: Session ID
        progress: Progress value (0-1)
        phase: Current phase
        message: Optional progress message

    Returns:
        StreamEvent: Progress event
    """
    return StreamEvent(
        event_type=StreamEventType.PROGRESS_UPDATED,
        data={
            "progress": progress,
            "phase": phase,
            "message": message,
        },
        session_id=session_id,
    )


# =============================================================================
# Streaming Decorators
# =============================================================================


def stream_output(event_type: StreamEventType):
    """
    Decorator for streaming agent outputs.

    Wraps agent methods to automatically stream their outputs.

    Args:
        event_type: Type of event to emit

    Returns:
        Decorator function

    Example:
        @stream_output(StreamEventType.NODE_CREATED)
        async def create_node(self, content: str) -> Dict:
            # Create node logic
            return node_data
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            # Execute the function
            result = await func(self, *args, **kwargs)

            # Emit event if agent has streaming callback
            if hasattr(self, 'emit_event'):
                await self.emit_event(event_type.value, {"result": result})

            return result
        return wrapper
    return decorator


def with_preview(preview_event_type: StreamEventType):
    """
    Decorator for streaming preview before final output.

    Emits preview events during processing, then final event on completion.

    Args:
        preview_event_type: Type of preview event

    Returns:
        Decorator function

    Example:
        @with_preview(StreamEventType.NODE_PREVIEW)
        async def generate_node(self, prompt: str) -> Dict:
            # Generation logic with intermediate previews
            return final_node_data
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            # Check if function is a generator
            result = func(self, *args, **kwargs)

            if hasattr(result, '__anext__'):
                # It's an async generator - emit previews
                final_result = None
                async for item in result:
                    if hasattr(self, 'emit_event'):
                        await self.emit_event(preview_event_type.value, {"preview": item})
                    final_result = item
                return final_result
            else:
                # Regular async function
                return await result
        return wrapper
    return decorator


def with_thinking(thinking_message: str = "Processing..."):
    """
    Decorator to emit thinking event before execution.

    Args:
        thinking_message: Message to show while thinking

    Returns:
        Decorator function
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            # Emit thinking event
            if hasattr(self, 'think'):
                await self.think(thinking_message)

            # Execute function
            return await func(self, *args, **kwargs)
        return wrapper
    return decorator

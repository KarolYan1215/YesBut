"""
Lock Service

Redis-based distributed locking service for branch-level concurrency control.
Prevents race conditions between agent streaming and user modifications.
"""

from typing import Optional
from datetime import datetime
import json
import asyncio

from app.db.redis import RedisClient


class LockType:
    """
    Lock type enumeration for branch-level locking.

    Lock types:
    - AGENT_WRITE: Exclusive lock held by an agent during streaming
    - USER_WRITE: Exclusive lock held by user during editing
    - GLOBAL_PAUSE: Exclusive lock for global interrupt
    """
    AGENT_WRITE = "agent_write"
    USER_WRITE = "user_write"
    GLOBAL_PAUSE = "global_pause"


class LockState:
    """
    UI lock state enumeration.

    States:
    - EDITABLE: Full user control, agents paused on this branch
    - OBSERVATION: Agent working, user can only view + global interrupt
    - PAUSED: User triggered pause, awaiting user decision
    """
    EDITABLE = "EDITABLE"
    OBSERVATION = "OBSERVATION"
    PAUSED = "PAUSED"


# Lua script for atomic compare-and-delete
RELEASE_LOCK_SCRIPT = """
local key = KEYS[1]
local holder_id = ARGV[1]

local lock_data = redis.call('GET', key)
if not lock_data then
    return 0
end

local data = cjson.decode(lock_data)
if data.holder_id == holder_id then
    redis.call('DEL', key)
    return 1
end
return 0
"""

# Lua script for atomic TTL extension
EXTEND_TTL_SCRIPT = """
local key = KEYS[1]
local holder_id = ARGV[1]
local additional_ttl = tonumber(ARGV[2])

local lock_data = redis.call('GET', key)
if not lock_data then
    return 0
end

local data = cjson.decode(lock_data)
if data.holder_id == holder_id then
    local current_ttl = redis.call('TTL', key)
    if current_ttl > 0 then
        redis.call('EXPIRE', key, current_ttl + additional_ttl)
        return 1
    end
end
return 0
"""


class BranchLockService:
    """
    Service for managing branch-level distributed locks.

    This service uses Redis for distributed locking to prevent race conditions
    when agents are streaming updates while users attempt modifications.

    Lock Granularity: BRANCH-LEVEL
    - Each branch has an independent lock
    - Agents acquire lock before modifying branch
    - Users cannot edit locked branches (observation mode only)

    Lock Implementation:
    - Redis SET with NX (only if not exists) and EX (expiration)
    - Lua scripts for atomic compare-and-delete operations
    - Automatic TTL-based expiration if agent crashes

    Attributes:
        redis: Redis client instance
        default_ttl: Default lock TTL in seconds (default: 300)
        lock_prefix: Redis key prefix for locks
    """

    def __init__(
        self,
        redis: RedisClient,
        default_ttl: int = 300,
        lock_prefix: str = "yesbut:lock:branch:",
    ):
        """
        Initialize the lock service.

        Args:
            redis: Redis client instance
            default_ttl: Default lock TTL in seconds
            lock_prefix: Redis key prefix for lock keys
        """
        self.redis = redis
        self.default_ttl = default_ttl
        self.lock_prefix = lock_prefix
        self._release_script_sha: Optional[str] = None
        self._extend_script_sha: Optional[str] = None

    def _get_lock_key(self, branch_id: str) -> str:
        """Get Redis key for branch lock."""
        return f"{self.lock_prefix}{branch_id}"

    def _get_session_locks_key(self, session_id: str) -> str:
        """Get Redis key for session's branch locks set."""
        return f"yesbut:session:{session_id}:locks"

    async def _ensure_scripts_loaded(self) -> None:
        """Load Lua scripts into Redis if not already loaded."""
        if self._release_script_sha is None:
            self._release_script_sha = await self.redis.script_load(RELEASE_LOCK_SCRIPT)
        if self._extend_script_sha is None:
            self._extend_script_sha = await self.redis.script_load(EXTEND_TTL_SCRIPT)

    async def acquire_agent_lock(
        self,
        branch_id: str,
        agent_id: str,
        agent_name: str,
        agent_type: str,
        ttl: Optional[int] = None,
    ) -> bool:
        """
        Acquire an exclusive write lock for an agent on a branch.

        This method:
        1. Attempts to acquire lock using Redis SET NX EX
        2. If successful, stores agent metadata in lock value
        3. Publishes lock state change event via Redis pub/sub

        Args:
            branch_id: ID of the branch to lock
            agent_id: ID of the agent acquiring the lock
            agent_name: Display name of the agent
            agent_type: Type of the agent (e.g., 'BM', 'GEN')
            ttl: Optional custom TTL (uses default if not specified)

        Returns:
            bool: True if lock acquired, False if already locked

        Side Effects:
            - Publishes 'branch_lock_changed' event with state='OBSERVATION'
        """
        lock_key = self._get_lock_key(branch_id)
        lock_ttl = ttl or self.default_ttl

        lock_data = {
            "holder_id": agent_id,
            "holder_name": agent_name,
            "holder_type": agent_type,
            "lock_type": LockType.AGENT_WRITE,
            "locked_at": datetime.utcnow().isoformat(),
        }

        acquired = await self.redis.set(
            lock_key,
            lock_data,
            ex=lock_ttl,
            nx=True,
        )

        if acquired:
            # Publish lock state change event
            await self.redis.publish(
                f"yesbut:branch:{branch_id}:lock",
                json.dumps({
                    "event": "lock_changed",
                    "branch_id": branch_id,
                    "state": LockState.OBSERVATION,
                    "holder_id": agent_id,
                    "holder_name": agent_name,
                    "holder_type": agent_type,
                })
            )

        return acquired

    async def release_lock(
        self,
        branch_id: str,
        holder_id: str,
    ) -> bool:
        """
        Release a lock held by a specific holder.

        Uses Lua script for atomic compare-and-delete:
        1. Check if lock exists and is held by holder_id
        2. If yes, delete the lock
        3. Publish lock state change event

        Args:
            branch_id: ID of the branch to unlock
            holder_id: ID of the current lock holder (agent or user)

        Returns:
            bool: True if lock released, False if not held by holder

        Side Effects:
            - Publishes 'branch_lock_changed' event with state='EDITABLE'
        """
        await self._ensure_scripts_loaded()
        lock_key = self._get_lock_key(branch_id)

        result = await self.redis.evalsha(
            self._release_script_sha,
            [lock_key],
            [holder_id],
        )

        if result == 1:
            # Publish lock state change event
            await self.redis.publish(
                f"yesbut:branch:{branch_id}:lock",
                json.dumps({
                    "event": "lock_changed",
                    "branch_id": branch_id,
                    "state": LockState.EDITABLE,
                    "holder_id": None,
                    "holder_name": None,
                    "holder_type": None,
                })
            )
            return True

        return False

    async def check_user_can_edit(
        self,
        branch_id: str,
    ) -> bool:
        """
        Check if a user can edit a specific branch.

        A user can edit if:
        - No lock exists on the branch, OR
        - Lock is held by the user (USER_WRITE type)

        Args:
            branch_id: ID of the branch to check

        Returns:
            bool: True if user can edit, False if locked by agent
        """
        lock_key = self._get_lock_key(branch_id)
        lock_data = await self.redis.get(lock_key)

        if lock_data is None:
            return True

        try:
            data = json.loads(lock_data)
            return data.get("lock_type") == LockType.USER_WRITE
        except (json.JSONDecodeError, KeyError):
            return False

    async def get_lock_state(
        self,
        branch_id: str,
    ) -> dict:
        """
        Get the current lock state for a branch.

        Returns:
            dict: Lock state information containing:
                - state: LockState (EDITABLE, OBSERVATION, PAUSED)
                - holder_id: ID of lock holder (if locked)
                - holder_name: Name of lock holder (if locked)
                - holder_type: Type of lock holder (if locked)
                - locked_at: Timestamp when locked (if locked)
                - ttl_remaining: Seconds until lock expires (if locked)
        """
        lock_key = self._get_lock_key(branch_id)
        lock_data = await self.redis.get(lock_key)

        if lock_data is None:
            return {
                "state": LockState.EDITABLE,
                "holder_id": None,
                "holder_name": None,
                "holder_type": None,
                "locked_at": None,
                "ttl_remaining": None,
            }

        try:
            data = json.loads(lock_data)
            ttl = await self.redis.ttl(lock_key)

            lock_type = data.get("lock_type")
            if lock_type == LockType.GLOBAL_PAUSE:
                state = LockState.PAUSED
            elif lock_type == LockType.AGENT_WRITE:
                state = LockState.OBSERVATION
            else:
                state = LockState.EDITABLE

            return {
                "state": state,
                "holder_id": data.get("holder_id"),
                "holder_name": data.get("holder_name"),
                "holder_type": data.get("holder_type"),
                "locked_at": data.get("locked_at"),
                "ttl_remaining": ttl if ttl > 0 else None,
            }
        except (json.JSONDecodeError, KeyError):
            return {
                "state": LockState.EDITABLE,
                "holder_id": None,
                "holder_name": None,
                "holder_type": None,
                "locked_at": None,
                "ttl_remaining": None,
            }

    async def request_user_lock(
        self,
        branch_id: str,
        user_id: str,
        ttl: Optional[int] = None,
    ) -> bool:
        """
        Request an edit lock for a user on a branch.

        This will fail if an agent currently holds the lock.
        Users must wait for agent to complete or trigger global interrupt.

        Args:
            branch_id: ID of the branch to lock
            user_id: ID of the user requesting the lock
            ttl: Optional custom TTL

        Returns:
            bool: True if lock acquired, False if agent is working
        """
        lock_key = self._get_lock_key(branch_id)
        lock_ttl = ttl or self.default_ttl

        lock_data = {
            "holder_id": user_id,
            "holder_name": "User",
            "holder_type": "user",
            "lock_type": LockType.USER_WRITE,
            "locked_at": datetime.utcnow().isoformat(),
        }

        acquired = await self.redis.set(
            lock_key,
            lock_data,
            ex=lock_ttl,
            nx=True,
        )

        return acquired

    async def trigger_global_interrupt(
        self,
        session_id: str,
        user_id: str,
    ) -> None:
        """
        Trigger a global interrupt for a session.

        This method:
        1. Acquires GLOBAL_PAUSE lock on all branches
        2. Signals all active agents to stop
        3. Waits for agents to acknowledge stop
        4. Transitions all branches to PAUSED state

        Args:
            session_id: ID of the session to interrupt
            user_id: ID of the user triggering the interrupt

        Side Effects:
            - All agents stop processing
            - All branches transition to PAUSED state
            - Publishes 'branch_lock_changed' events for all branches
        """
        # Publish global interrupt signal
        await self.redis.publish(
            f"yesbut:session:{session_id}:interrupt",
            json.dumps({
                "event": "global_interrupt",
                "session_id": session_id,
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
            })
        )

        # Get all branch locks for this session
        session_locks_key = self._get_session_locks_key(session_id)
        branch_ids = await self.redis.lrange(session_locks_key, 0, -1)

        # Force release all locks and set to PAUSED state
        for branch_id in branch_ids:
            lock_key = self._get_lock_key(branch_id)

            # Delete existing lock
            await self.redis.delete(lock_key)

            # Set PAUSED lock
            pause_data = {
                "holder_id": user_id,
                "holder_name": "User (Paused)",
                "holder_type": "user",
                "lock_type": LockType.GLOBAL_PAUSE,
                "locked_at": datetime.utcnow().isoformat(),
            }
            await self.redis.set(lock_key, pause_data, ex=self.default_ttl)

            # Publish state change
            await self.redis.publish(
                f"yesbut:branch:{branch_id}:lock",
                json.dumps({
                    "event": "lock_changed",
                    "branch_id": branch_id,
                    "state": LockState.PAUSED,
                    "holder_id": user_id,
                    "holder_name": "User (Paused)",
                    "holder_type": "user",
                })
            )

    async def extend_lock_ttl(
        self,
        branch_id: str,
        holder_id: str,
        additional_ttl: int,
    ) -> bool:
        """
        Extend the TTL of an existing lock.

        Used by agents during long-running operations to prevent
        lock expiration while still processing.

        Args:
            branch_id: ID of the branch
            holder_id: ID of the current lock holder
            additional_ttl: Additional seconds to add to TTL

        Returns:
            bool: True if TTL extended, False if lock not held by holder
        """
        await self._ensure_scripts_loaded()
        lock_key = self._get_lock_key(branch_id)

        result = await self.redis.evalsha(
            self._extend_script_sha,
            [lock_key],
            [holder_id, str(additional_ttl)],
        )

        return result == 1

    async def register_branch_for_session(
        self,
        session_id: str,
        branch_id: str,
    ) -> None:
        """
        Register a branch as belonging to a session for global interrupt tracking.

        Args:
            session_id: ID of the session
            branch_id: ID of the branch
        """
        session_locks_key = self._get_session_locks_key(session_id)
        await self.redis.rpush(session_locks_key, branch_id)

    async def unregister_branch_for_session(
        self,
        session_id: str,
        branch_id: str,
    ) -> None:
        """
        Unregister a branch from a session.

        Args:
            session_id: ID of the session
            branch_id: ID of the branch
        """
        session_locks_key = self._get_session_locks_key(session_id)
        # Use LREM to remove the branch_id from the list
        await self.redis.client.lrem(session_locks_key, 0, branch_id)


# Global lock service instance
_lock_service: Optional[BranchLockService] = None


def get_lock_service() -> BranchLockService:
    """
    Get global lock service instance.

    Returns:
        BranchLockService: Global lock service

    Raises:
        RuntimeError: If lock service is not initialized
    """
    if _lock_service is None:
        raise RuntimeError("Lock service not initialized. Call init_lock_service() first.")
    return _lock_service


async def init_lock_service(redis: RedisClient, **kwargs) -> BranchLockService:
    """
    Initialize global lock service.

    Args:
        redis: Redis client instance
        **kwargs: Additional service configuration

    Returns:
        BranchLockService: Initialized lock service
    """
    global _lock_service
    _lock_service = BranchLockService(redis, **kwargs)
    return _lock_service


async def close_lock_service() -> None:
    """
    Close global lock service.

    Should be called during application shutdown.
    """
    global _lock_service
    _lock_service = None

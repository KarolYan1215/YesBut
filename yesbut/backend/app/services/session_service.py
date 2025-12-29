"""
Session Service Module

Business logic for session lifecycle management.

@module app/services/session_service
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
import json


class SessionService:
    """
    Service for session lifecycle management.

    Provides business logic for:
    - Session CRUD operations
    - Phase transitions
    - Session state management
    - Agent orchestration triggers
    """

    def __init__(self, db=None, redis=None, lock_service=None):
        self.db = db
        self.redis = redis
        self.lock_service = lock_service
        self._memory_store: Dict[str, Dict[str, Any]] = {}

    async def create_session(
        self,
        user_id: str,
        title: str,
        description: Optional[str] = None,
        initial_goal: str = "",
        mode: str = "sync",
        settings: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a new brainstorming session."""
        session_id = str(uuid.uuid4())
        now = datetime.utcnow()

        goal_node_id = str(uuid.uuid4())
        goal_node = {
            "id": goal_node_id,
            "type": "goal",
            "content": initial_goal,
            "layer": 0,
            "branch_id": None,
            "parent_id": None,
            "confidence": 1.0,
            "utility": 1.0,
            "sensitivity": None,
            "metadata": {"created_at": now.isoformat(), "created_by": "system"},
        }

        main_branch_id = str(uuid.uuid4())
        main_branch = {
            "id": main_branch_id,
            "name": "main",
            "status": "active",
            "utility_score": 0.5,
            "lock_state": "EDITABLE",
            "lock_holder_id": None,
        }

        goal_node["branch_id"] = main_branch_id

        session_data = {
            "id": session_id,
            "user_id": user_id,
            "title": title,
            "description": description,
            "status": "draft",
            "mode": mode,
            "phase": "divergence",
            "phase_progress": 0.0,
            "settings": settings or {},
            "nodes": {goal_node_id: goal_node},
            "edges": {},
            "branches": {main_branch_id: main_branch},
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
        }

        self._memory_store[session_id] = session_data

        if self.redis:
            await self.redis.set(f"session:{session_id}", json.dumps(session_data), ex=86400)

        return session_data

    async def get_session(
        self,
        session_id: str,
        include_statistics: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """Get session by ID."""
        if self.redis:
            data = await self.redis.get(f"session:{session_id}")
            if data:
                session = json.loads(data)
                if include_statistics:
                    session["statistics"] = await self.get_session_statistics(session_id)
                return session

        session = self._memory_store.get(session_id)
        if session and include_statistics:
            session["statistics"] = await self.get_session_statistics(session_id)
        return session

    async def list_sessions(
        self,
        user_id: str,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> Dict[str, Any]:
        """List sessions for a user."""
        items = [s for s in self._memory_store.values() if s.get("user_id") == user_id]
        if status:
            items = [s for s in items if s.get("status") == status]
        total = len(items)
        items = items[skip:skip + limit]
        return {"items": items, "total": total, "skip": skip, "limit": limit}

    async def update_session(
        self,
        session_id: str,
        updates: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Update session properties."""
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        for key, value in updates.items():
            if key in ["title", "description", "settings", "mode"]:
                session[key] = value

        session["updated_at"] = datetime.utcnow().isoformat()
        self._memory_store[session_id] = session

        if self.redis:
            await self.redis.set(f"session:{session_id}", json.dumps(session), ex=86400)

        return session

    async def delete_session(self, session_id: str) -> bool:
        """Delete a session and all related data."""
        if session_id in self._memory_store:
            del self._memory_store[session_id]
        if self.redis:
            await self.redis.delete(f"session:{session_id}")
        return True

    async def start_session(self, session_id: str) -> Dict[str, Any]:
        """Start a session (transition from draft to active)."""
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        if session.get("status") != "draft":
            raise ValueError("Session must be in draft state to start")

        session["status"] = "active"
        session["updated_at"] = datetime.utcnow().isoformat()
        self._memory_store[session_id] = session

        if self.redis:
            await self.redis.set(f"session:{session_id}", json.dumps(session), ex=86400)

        return session

    async def pause_session(self, session_id: str) -> Dict[str, Any]:
        """Pause an active session."""
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        session["status"] = "paused"
        session["updated_at"] = datetime.utcnow().isoformat()
        self._memory_store[session_id] = session

        if self.redis:
            await self.redis.set(f"session:{session_id}", json.dumps(session), ex=86400)

        return session

    async def resume_session(self, session_id: str) -> Dict[str, Any]:
        """Resume a paused session."""
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        session["status"] = "active"
        session["updated_at"] = datetime.utcnow().isoformat()
        self._memory_store[session_id] = session

        if self.redis:
            await self.redis.set(f"session:{session_id}", json.dumps(session), ex=86400)

        return session

    async def complete_session(self, session_id: str) -> Dict[str, Any]:
        """Mark session as completed."""
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        session["status"] = "completed"
        session["phase"] = "completed"
        session["phase_progress"] = 1.0
        session["updated_at"] = datetime.utcnow().isoformat()
        self._memory_store[session_id] = session

        if self.redis:
            await self.redis.set(f"session:{session_id}", json.dumps(session), ex=86400)

        return session

    async def transition_phase(
        self,
        session_id: str,
        target_phase: str,
        force: bool = False,
    ) -> Dict[str, Any]:
        """Transition session to a new phase."""
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        valid_transitions = {
            "divergence": ["filtering"],
            "filtering": ["convergence"],
            "convergence": ["completed"],
        }

        current_phase = session.get("phase", "divergence")
        if target_phase not in valid_transitions.get(current_phase, []) and not force:
            raise ValueError(f"Invalid phase transition: {current_phase} -> {target_phase}")

        previous_phase = current_phase
        session["phase"] = target_phase
        session["phase_progress"] = 0.0
        session["updated_at"] = datetime.utcnow().isoformat()
        self._memory_store[session_id] = session

        if self.redis:
            await self.redis.set(f"session:{session_id}", json.dumps(session), ex=86400)

        return {
            "session": session,
            "previous_phase": previous_phase,
            "current_phase": target_phase,
            "transition_time": datetime.utcnow().isoformat(),
        }

    async def check_phase_transition_conditions(self, session_id: str) -> Dict[str, Any]:
        """Check if conditions for phase transition are met."""
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        current_phase = session.get("phase", "divergence")
        nodes = session.get("nodes", {})
        node_count = len(nodes)

        conditions = {}
        can_transition = False
        next_phase = None

        if current_phase == "divergence":
            conditions["node_count"] = node_count
            conditions["min_required"] = 15
            can_transition = node_count >= 15
            next_phase = "filtering" if can_transition else None

        elif current_phase == "filtering":
            conditions["pareto_stability"] = 0.8
            can_transition = True
            next_phase = "convergence"

        elif current_phase == "convergence":
            conditions["nash_distance"] = 0.05
            can_transition = True
            next_phase = "completed"

        return {
            "current_phase": current_phase,
            "can_transition": can_transition,
            "next_phase": next_phase,
            "conditions": conditions,
        }

    async def update_phase_progress(self, session_id: str, progress: float) -> Dict[str, Any]:
        """Update phase progress."""
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        session["phase_progress"] = min(1.0, max(0.0, progress))
        session["updated_at"] = datetime.utcnow().isoformat()
        self._memory_store[session_id] = session

        if self.redis:
            await self.redis.set(f"session:{session_id}", json.dumps(session), ex=86400)

        return session

    async def toggle_mode(self, session_id: str) -> Dict[str, Any]:
        """Toggle session mode between sync and async."""
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        current_mode = session.get("mode", "sync")
        session["mode"] = "async" if current_mode == "sync" else "sync"
        session["updated_at"] = datetime.utcnow().isoformat()
        self._memory_store[session_id] = session

        if self.redis:
            await self.redis.set(f"session:{session_id}", json.dumps(session), ex=86400)

        return session

    async def get_session_statistics(self, session_id: str) -> Dict[str, Any]:
        """Get detailed session statistics."""
        session = self._memory_store.get(session_id)
        if not session:
            return {}

        nodes = session.get("nodes", {})
        edges = session.get("edges", {})
        branches = session.get("branches", {})

        node_types = {}
        for node in nodes.values():
            node_type = node.get("type", "unknown")
            node_types[node_type] = node_types.get(node_type, 0) + 1

        return {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "branch_count": len(branches),
            "node_types": node_types,
            "phase": session.get("phase"),
            "phase_progress": session.get("phase_progress", 0),
        }

    async def get_active_agents(self, session_id: str) -> List[Dict[str, Any]]:
        """Get currently active agents for session."""
        return []

    async def get_recent_activity(self, session_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent activity for session."""
        return []


def get_session_service(db=None, redis=None, lock_service=None) -> SessionService:
    """Factory function for SessionService."""
    return SessionService(db=db, redis=redis, lock_service=lock_service)

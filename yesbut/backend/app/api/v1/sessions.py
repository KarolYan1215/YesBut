"""
Sessions API Router

Provides RESTful endpoints for managing brainstorming sessions.
Sessions are the top-level container for all brainstorming activities.
"""

from fastapi import APIRouter, HTTPException, Query, Body
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

from ...services.session_service import SessionService, get_session_service


router = APIRouter(prefix="/sessions", tags=["sessions"])

# Global service instance (would be injected via dependency in production)
_session_service: Optional[SessionService] = None


def get_service() -> SessionService:
    global _session_service
    if _session_service is None:
        _session_service = get_session_service()
    return _session_service


class SessionCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    initial_goal: str = Field(..., min_length=1)
    mode: str = Field("sync", pattern="^(sync|async)$")
    settings: Optional[Dict[str, Any]] = None


class SessionUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    mode: Optional[str] = Field(None, pattern="^(sync|async)$")
    settings: Optional[Dict[str, Any]] = None


@router.post("")
async def create_session(request: SessionCreateRequest) -> Dict[str, Any]:
    """Create a new brainstorming session."""
    service = get_service()
    try:
        session = await service.create_session(
            user_id="default_user",  # Would come from auth in production
            title=request.title,
            description=request.description,
            initial_goal=request.initial_goal,
            mode=request.mode,
            settings=request.settings,
        )
        return {"success": True, "data": session}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}")
async def get_session(
    session_id: str,
    include_statistics: bool = Query(False),
) -> Dict[str, Any]:
    """Get a session by ID."""
    service = get_service()
    session = await service.get_session(session_id, include_statistics=include_statistics)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"success": True, "data": session}


@router.get("")
async def list_sessions(
    status: Optional[str] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0, description="Skip items"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
) -> Dict[str, Any]:
    """List all sessions for the current user."""
    service = get_service()
    result = await service.list_sessions(
        user_id="default_user",
        status=status,
        skip=skip,
        limit=limit,
    )
    return {"success": True, "data": result}


@router.patch("/{session_id}")
async def update_session(
    session_id: str,
    request: SessionUpdateRequest,
) -> Dict[str, Any]:
    """Update session properties."""
    service = get_service()
    try:
        updates = request.model_dump(exclude_none=True)
        session = await service.update_session(session_id, updates)
        return {"success": True, "data": session}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{session_id}")
async def delete_session(session_id: str) -> Dict[str, Any]:
    """Delete a session and all associated data."""
    service = get_service()
    try:
        await service.delete_session(session_id)
        return {"success": True, "message": "Session deleted"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{session_id}/start")
async def start_session(session_id: str) -> Dict[str, Any]:
    """Start a session (transition from draft to active)."""
    service = get_service()
    try:
        session = await service.start_session(session_id)
        return {"success": True, "data": session}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{session_id}/pause")
async def pause_session(session_id: str) -> Dict[str, Any]:
    """Pause an active session."""
    service = get_service()
    try:
        session = await service.pause_session(session_id)
        return {"success": True, "data": session}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{session_id}/resume")
async def resume_session(session_id: str) -> Dict[str, Any]:
    """Resume a paused session."""
    service = get_service()
    try:
        session = await service.resume_session(session_id)
        return {"success": True, "data": session}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{session_id}/complete")
async def complete_session(session_id: str) -> Dict[str, Any]:
    """Mark session as completed."""
    service = get_service()
    try:
        session = await service.complete_session(session_id)
        return {"success": True, "data": session}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{session_id}/toggle-mode")
async def toggle_session_mode(session_id: str) -> Dict[str, Any]:
    """Toggle session between sync and async mode."""
    service = get_service()
    try:
        session = await service.toggle_mode(session_id)
        return {"success": True, "data": session}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{session_id}/transition-phase")
async def transition_phase(
    session_id: str,
    target_phase: str = Body(..., embed=True),
    force: bool = Body(False, embed=True),
) -> Dict[str, Any]:
    """Transition session to a new phase."""
    service = get_service()
    try:
        result = await service.transition_phase(session_id, target_phase, force)
        return {"success": True, "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{session_id}/statistics")
async def get_session_statistics(session_id: str) -> Dict[str, Any]:
    """Get detailed session statistics."""
    service = get_service()
    stats = await service.get_session_statistics(session_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"success": True, "data": stats}


@router.get("/{session_id}/phase-conditions")
async def check_phase_conditions(session_id: str) -> Dict[str, Any]:
    """Check if conditions for phase transition are met."""
    service = get_service()
    try:
        result = await service.check_phase_transition_conditions(session_id)
        return {"success": True, "data": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

"""
Branches API Router

Provides RESTful endpoints for managing reasoning branches.
"""

from fastapi import APIRouter, HTTPException, Body
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

from ...services.session_service import get_session_service
from ...services.graph_service import get_graph_service


router = APIRouter(prefix="/sessions/{session_id}/branches", tags=["branches"])


def get_service(session_id: str):
    session_service = get_session_service()
    return get_graph_service(session_service=session_service)


class BranchCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    parent_branch_id: Optional[str] = None
    fork_node_id: Optional[str] = None


class BranchUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    status: Optional[str] = Field(None, pattern="^(active|paused|merged|pruned)$")
    utility_score: Optional[float] = Field(None, ge=0, le=1)


class ForkBranchRequest(BaseModel):
    fork_node_id: str = Field(...)
    new_branch_name: str = Field(..., min_length=1, max_length=100)


class MergeBranchRequest(BaseModel):
    target_branch_id: str = Field(...)
    merge_strategy: str = Field("synthesis", pattern="^(synthesis|compromise|transcendence)$")


@router.post("")
async def create_branch(
    session_id: str,
    request: BranchCreateRequest,
) -> Dict[str, Any]:
    """Create a new branch."""
    service = get_service(session_id)
    try:
        branch = await service.create_branch(
            session_id=session_id,
            name=request.name,
            parent_branch_id=request.parent_branch_id,
            fork_node_id=request.fork_node_id,
        )
        return {"success": True, "data": branch}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{branch_id}")
async def get_branch(session_id: str, branch_id: str) -> Dict[str, Any]:
    """Get a branch by ID."""
    service = get_service(session_id)
    branch = await service.get_branch(session_id, branch_id)
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    return {"success": True, "data": branch}


@router.get("")
async def list_branches(session_id: str) -> Dict[str, Any]:
    """List all branches in a session."""
    service = get_service(session_id)
    branches = await service.list_branches(session_id)
    return {"success": True, "data": branches}


@router.patch("/{branch_id}")
async def update_branch(
    session_id: str,
    branch_id: str,
    request: BranchUpdateRequest,
) -> Dict[str, Any]:
    """Update a branch."""
    service = get_service(session_id)
    try:
        updates = request.model_dump(exclude_none=True)
        branch = await service.update_branch(session_id, branch_id, updates)
        return {"success": True, "data": branch}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{branch_id}")
async def delete_branch(session_id: str, branch_id: str) -> Dict[str, Any]:
    """Delete a branch."""
    service = get_service(session_id)
    try:
        deleted = await service.delete_branch(session_id, branch_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Branch not found")
        return {"success": True, "message": "Branch deleted"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{branch_id}/fork")
async def fork_branch(
    session_id: str,
    branch_id: str,
    request: ForkBranchRequest,
) -> Dict[str, Any]:
    """Fork a branch at a specific node."""
    service = get_service(session_id)
    try:
        new_branch = await service.fork_branch(
            session_id=session_id,
            source_branch_id=branch_id,
            fork_node_id=request.fork_node_id,
            new_branch_name=request.new_branch_name,
        )
        return {"success": True, "data": new_branch}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{branch_id}/merge")
async def merge_branches(
    session_id: str,
    branch_id: str,
    request: MergeBranchRequest,
) -> Dict[str, Any]:
    """Merge two branches."""
    service = get_service(session_id)
    try:
        result = await service.merge_branches(
            session_id=session_id,
            source_branch_id=branch_id,
            target_branch_id=request.target_branch_id,
            merge_strategy=request.merge_strategy,
        )
        return {"success": True, "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

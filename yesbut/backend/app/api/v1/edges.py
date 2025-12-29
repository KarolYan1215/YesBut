"""
Edges API Router

Provides RESTful endpoints for managing graph edges.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

from ...services.session_service import get_session_service
from ...services.graph_service import get_graph_service


router = APIRouter(prefix="/sessions/{session_id}/edges", tags=["edges"])


def get_service(session_id: str):
    session_service = get_session_service()
    return get_graph_service(session_service=session_service)


class EdgeCreateRequest(BaseModel):
    source_id: str = Field(...)
    target_id: str = Field(...)
    type: str = Field(..., pattern="^(decompose|derive|support|attack|conflict|entail)$")
    weight: float = Field(1.0, ge=0, le=1)
    metadata: Optional[Dict[str, Any]] = None


class EdgeUpdateRequest(BaseModel):
    weight: Optional[float] = Field(None, ge=0, le=1)
    validated: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


@router.post("")
async def create_edge(
    session_id: str,
    request: EdgeCreateRequest,
) -> Dict[str, Any]:
    """Create a new edge in the graph."""
    service = get_service(session_id)
    try:
        edge = await service.create_edge(
            session_id=session_id,
            source_id=request.source_id,
            target_id=request.target_id,
            edge_type=request.type,
            weight=request.weight,
            metadata=request.metadata,
        )
        return {"success": True, "data": edge}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{edge_id}")
async def get_edge(session_id: str, edge_id: str) -> Dict[str, Any]:
    """Get an edge by ID."""
    service = get_service(session_id)
    edge = await service.get_edge(session_id, edge_id)
    if not edge:
        raise HTTPException(status_code=404, detail="Edge not found")
    return {"success": True, "data": edge}


@router.get("")
async def list_edges(
    session_id: str,
    edge_type: Optional[str] = Query(None, description="Filter by edge type"),
    source_id: Optional[str] = Query(None, description="Filter by source node"),
    target_id: Optional[str] = Query(None, description="Filter by target node"),
) -> Dict[str, Any]:
    """List edges with optional filtering."""
    service = get_service(session_id)
    edges = await service.list_edges(
        session_id=session_id,
        edge_type=edge_type,
        source_id=source_id,
        target_id=target_id,
    )
    return {"success": True, "data": edges}


@router.patch("/{edge_id}")
async def update_edge(
    session_id: str,
    edge_id: str,
    request: EdgeUpdateRequest,
) -> Dict[str, Any]:
    """Update an edge."""
    service = get_service(session_id)
    try:
        updates = request.model_dump(exclude_none=True)
        edge = await service.update_edge(session_id, edge_id, updates)
        return {"success": True, "data": edge}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{edge_id}")
async def delete_edge(session_id: str, edge_id: str) -> Dict[str, Any]:
    """Delete an edge."""
    service = get_service(session_id)
    try:
        deleted = await service.delete_edge(session_id, edge_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Edge not found")
        return {"success": True, "message": "Edge deleted"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

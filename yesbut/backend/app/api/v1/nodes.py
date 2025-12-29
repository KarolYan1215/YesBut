"""
Nodes API Router

Provides RESTful endpoints for managing graph nodes.
"""

from fastapi import APIRouter, HTTPException, Query, Body
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

from ...services.session_service import get_session_service
from ...services.graph_service import GraphService, get_graph_service


router = APIRouter(prefix="/sessions/{session_id}/nodes", tags=["nodes"])


def get_service(session_id: str) -> GraphService:
    session_service = get_session_service()
    return get_graph_service(session_service=session_service)


class NodeCreateRequest(BaseModel):
    type: str = Field(..., pattern="^(goal|claim|fact|constraint|atomic_topic|pending|synthesis)$")
    content: str = Field(..., min_length=1)
    layer: int = Field(1, ge=0)
    branch_id: Optional[str] = None
    parent_id: Optional[str] = None
    confidence: float = Field(0.8, ge=0, le=1)
    utility: float = Field(0.5, ge=0, le=1)
    metadata: Optional[Dict[str, Any]] = None


class NodeUpdateRequest(BaseModel):
    content: Optional[str] = Field(None, min_length=1)
    confidence: Optional[float] = Field(None, ge=0, le=1)
    utility: Optional[float] = Field(None, ge=0, le=1)
    sensitivity: Optional[float] = Field(None, ge=0, le=1)
    metadata: Optional[Dict[str, Any]] = None


@router.post("")
async def create_node(
    session_id: str,
    request: NodeCreateRequest,
) -> Dict[str, Any]:
    """Create a new node in the graph."""
    service = get_service(session_id)
    try:
        node = await service.create_node(
            session_id=session_id,
            node_type=request.type,
            content=request.content,
            layer=request.layer,
            branch_id=request.branch_id,
            parent_id=request.parent_id,
            confidence=request.confidence,
            utility=request.utility,
            metadata=request.metadata,
        )
        return {"success": True, "data": node}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{node_id}")
async def get_node(session_id: str, node_id: str) -> Dict[str, Any]:
    """Get a node by ID."""
    service = get_service(session_id)
    node = await service.get_node(session_id, node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return {"success": True, "data": node}


@router.get("")
async def list_nodes(
    session_id: str,
    node_type: Optional[str] = Query(None, description="Filter by node type"),
    branch_id: Optional[str] = Query(None, description="Filter by branch"),
    layer: Optional[int] = Query(None, description="Filter by layer"),
) -> Dict[str, Any]:
    """List nodes with optional filtering."""
    service = get_service(session_id)
    nodes = await service.list_nodes(
        session_id=session_id,
        node_type=node_type,
        branch_id=branch_id,
        layer=layer,
    )
    return {"success": True, "data": nodes}


@router.patch("/{node_id}")
async def update_node(
    session_id: str,
    node_id: str,
    request: NodeUpdateRequest,
) -> Dict[str, Any]:
    """Update a node."""
    service = get_service(session_id)
    try:
        updates = request.model_dump(exclude_none=True)
        node = await service.update_node(session_id, node_id, updates)
        return {"success": True, "data": node}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{node_id}")
async def delete_node(session_id: str, node_id: str) -> Dict[str, Any]:
    """Delete a node and its connected edges."""
    service = get_service(session_id)
    try:
        deleted = await service.delete_node(session_id, node_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Node not found")
        return {"success": True, "message": "Node deleted"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{node_id}/ancestors")
async def get_node_ancestors(session_id: str, node_id: str) -> Dict[str, Any]:
    """Get all ancestor nodes of a node."""
    service = get_service(session_id)
    ancestors = await service.get_ancestors(session_id, node_id)
    return {"success": True, "data": ancestors}


@router.get("/{node_id}/descendants")
async def get_node_descendants(session_id: str, node_id: str) -> Dict[str, Any]:
    """Get all descendant nodes of a node."""
    service = get_service(session_id)
    descendants = await service.get_descendants(session_id, node_id)
    return {"success": True, "data": descendants}


@router.get("/{node_id}/path-to-root")
async def get_path_to_root(session_id: str, node_id: str) -> Dict[str, Any]:
    """Get path from node to root goal node."""
    service = get_service(session_id)
    path = await service.get_path_to_root(session_id, node_id)
    return {"success": True, "data": path}

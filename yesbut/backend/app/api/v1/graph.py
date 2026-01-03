"""
Graph API Router

Provides RESTful endpoints for graph-level operations and analysis.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from app.services.session_service import get_session_service
from app.services.graph_service import get_graph_service
from algorithms.sensitivity import SensitivityAnalyzer
from algorithms.path_analysis import PathAnalyzer


router = APIRouter(prefix="/sessions/{session_id}/graph", tags=["graph"])


def get_service(session_id: str):
    session_service = get_session_service()
    return get_graph_service(session_service=session_service)


@router.get("/statistics")
async def get_graph_statistics(session_id: str) -> Dict[str, Any]:
    """Get comprehensive graph statistics."""
    service = get_service(session_id)
    stats = await service.get_graph_statistics(session_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"success": True, "data": stats}


@router.get("/sensitivity")
async def analyze_sensitivity(session_id: str) -> Dict[str, Any]:
    """Run sensitivity analysis on the graph."""
    session_service = get_session_service()
    session = await session_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    nodes = list(session.get("nodes", {}).values())
    edges = list(session.get("edges", {}).values())

    if not nodes:
        return {"success": True, "data": {"stability_score": 1.0, "critical_nodes": [], "recommendations": []}}

    goal_node = next((n for n in nodes if n.get("type") == "goal"), None)
    if not goal_node:
        return {"success": True, "data": {"stability_score": 1.0, "critical_nodes": [], "recommendations": []}}

    graph_data = {"nodes": nodes, "edges": edges}
    analyzer = SensitivityAnalyzer(graph=graph_data, goal_node_id=goal_node["id"])
    result = analyzer.analyze()

    return {"success": True, "data": result}


@router.get("/path-analysis")
async def analyze_paths(session_id: str) -> Dict[str, Any]:
    """Run path analysis on the graph."""
    session_service = get_session_service()
    session = await session_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    nodes = list(session.get("nodes", {}).values())
    edges = list(session.get("edges", {}).values())

    if not nodes:
        return {"success": True, "data": {"critical_paths": [], "redundant_paths": [], "redundancy_ratio": 1.0}}

    goal_node = next((n for n in nodes if n.get("type") == "goal"), None)
    if not goal_node:
        return {"success": True, "data": {"critical_paths": [], "redundant_paths": [], "redundancy_ratio": 1.0}}

    graph_data = {"nodes": nodes, "edges": edges}
    analyzer = PathAnalyzer(graph=graph_data, goal_node_id=goal_node["id"])
    result = analyzer.analyze()

    return {"success": True, "data": result}


@router.get("/visualization")
async def get_visualization_data(session_id: str) -> Dict[str, Any]:
    """Get data formatted for graph visualization."""
    session_service = get_session_service()
    session = await session_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    nodes = list(session.get("nodes", {}).values())
    edges = list(session.get("edges", {}).values())

    # Format for React Flow
    react_flow_nodes = []
    for node in nodes:
        react_flow_nodes.append({
            "id": node.get("id"),
            "type": node.get("type"),
            "data": {
                "label": node.get("content", "")[:100],
                "content": node.get("content"),
                "confidence": node.get("confidence"),
                "utility": node.get("utility"),
                "layer": node.get("layer"),
            },
            "position": {"x": 0, "y": node.get("layer", 0) * 150},
        })

    react_flow_edges = []
    for edge in edges:
        react_flow_edges.append({
            "id": edge.get("id"),
            "source": edge.get("source_id"),
            "target": edge.get("target_id"),
            "type": edge.get("type"),
            "data": {
                "weight": edge.get("weight"),
                "validated": edge.get("validated"),
            },
        })

    return {
        "success": True,
        "data": {
            "nodes": react_flow_nodes,
            "edges": react_flow_edges,
        }
    }


@router.get("/export")
async def export_graph(session_id: str, format: str = "json") -> Dict[str, Any]:
    """Export graph data in various formats."""
    session_service = get_session_service()
    session = await session_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if format == "json":
        return {
            "success": True,
            "data": {
                "nodes": list(session.get("nodes", {}).values()),
                "edges": list(session.get("edges", {}).values()),
                "branches": list(session.get("branches", {}).values()),
                "metadata": {
                    "session_id": session_id,
                    "phase": session.get("phase"),
                    "exported_at": session.get("updated_at"),
                }
            }
        }
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")

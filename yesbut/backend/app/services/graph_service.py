"""
Graph Service Module

Business logic for graph operations (nodes, edges, branches).

@module app/services/graph_service
"""

from typing import Optional, List, Dict, Any, Set
from datetime import datetime
import uuid
import json


class GraphService:
    """
    Service for graph operations.

    Provides business logic for:
    - Node CRUD operations
    - Edge CRUD operations
    - Branch management
    - Graph traversal and queries
    """

    def __init__(self, session_service=None, redis=None, lock_service=None):
        self.session_service = session_service
        self.redis = redis
        self.lock_service = lock_service

    # =========================================================================
    # Node Operations
    # =========================================================================

    async def create_node(
        self,
        session_id: str,
        node_type: str,
        content: str,
        layer: int = 1,
        branch_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        confidence: float = 0.8,
        utility: float = 0.5,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a new node in the graph."""
        session = await self.session_service.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        node_id = str(uuid.uuid4())
        now = datetime.utcnow()

        node = {
            "id": node_id,
            "type": node_type,
            "content": content,
            "layer": layer,
            "branch_id": branch_id,
            "parent_id": parent_id,
            "confidence": confidence,
            "utility": utility,
            "sensitivity": None,
            "metadata": {
                **(metadata or {}),
                "created_at": now.isoformat(),
                "updated_at": now.isoformat(),
            },
        }

        session["nodes"][node_id] = node
        session["updated_at"] = now.isoformat()

        await self._save_session(session)

        return node

    async def get_node(self, session_id: str, node_id: str) -> Optional[Dict[str, Any]]:
        """Get a node by ID."""
        session = await self.session_service.get_session(session_id)
        if not session:
            return None
        return session.get("nodes", {}).get(node_id)

    async def update_node(
        self,
        session_id: str,
        node_id: str,
        updates: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Update a node."""
        session = await self.session_service.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        node = session.get("nodes", {}).get(node_id)
        if not node:
            raise ValueError(f"Node {node_id} not found")

        allowed_fields = ["content", "confidence", "utility", "sensitivity", "metadata"]
        for key, value in updates.items():
            if key in allowed_fields:
                if key == "metadata":
                    node["metadata"] = {**node.get("metadata", {}), **value}
                else:
                    node[key] = value

        node["metadata"]["updated_at"] = datetime.utcnow().isoformat()
        session["updated_at"] = datetime.utcnow().isoformat()

        await self._save_session(session)

        return node

    async def delete_node(self, session_id: str, node_id: str) -> bool:
        """Delete a node and its connected edges."""
        session = await self.session_service.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        if node_id not in session.get("nodes", {}):
            return False

        # Delete connected edges
        edges_to_delete = [
            edge_id for edge_id, edge in session.get("edges", {}).items()
            if edge.get("source_id") == node_id or edge.get("target_id") == node_id
        ]
        for edge_id in edges_to_delete:
            del session["edges"][edge_id]

        del session["nodes"][node_id]
        session["updated_at"] = datetime.utcnow().isoformat()

        await self._save_session(session)

        return True

    async def list_nodes(
        self,
        session_id: str,
        node_type: Optional[str] = None,
        branch_id: Optional[str] = None,
        layer: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """List nodes with optional filtering."""
        session = await self.session_service.get_session(session_id)
        if not session:
            return []

        nodes = list(session.get("nodes", {}).values())

        if node_type:
            nodes = [n for n in nodes if n.get("type") == node_type]
        if branch_id:
            nodes = [n for n in nodes if n.get("branch_id") == branch_id]
        if layer is not None:
            nodes = [n for n in nodes if n.get("layer") == layer]

        return nodes

    # =========================================================================
    # Edge Operations
    # =========================================================================

    async def create_edge(
        self,
        session_id: str,
        source_id: str,
        target_id: str,
        edge_type: str,
        weight: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a new edge in the graph."""
        session = await self.session_service.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        # Validate source and target exist
        if source_id not in session.get("nodes", {}):
            raise ValueError(f"Source node {source_id} not found")
        if target_id not in session.get("nodes", {}):
            raise ValueError(f"Target node {target_id} not found")

        edge_id = str(uuid.uuid4())
        now = datetime.utcnow()

        edge = {
            "id": edge_id,
            "source_id": source_id,
            "target_id": target_id,
            "type": edge_type,
            "weight": weight,
            "validated": None,
            "metadata": {
                **(metadata or {}),
                "created_at": now.isoformat(),
            },
        }

        session["edges"][edge_id] = edge
        session["updated_at"] = now.isoformat()

        await self._save_session(session)

        return edge

    async def get_edge(self, session_id: str, edge_id: str) -> Optional[Dict[str, Any]]:
        """Get an edge by ID."""
        session = await self.session_service.get_session(session_id)
        if not session:
            return None
        return session.get("edges", {}).get(edge_id)

    async def update_edge(
        self,
        session_id: str,
        edge_id: str,
        updates: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Update an edge."""
        session = await self.session_service.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        edge = session.get("edges", {}).get(edge_id)
        if not edge:
            raise ValueError(f"Edge {edge_id} not found")

        allowed_fields = ["weight", "validated", "metadata"]
        for key, value in updates.items():
            if key in allowed_fields:
                edge[key] = value

        session["updated_at"] = datetime.utcnow().isoformat()

        await self._save_session(session)

        return edge

    async def delete_edge(self, session_id: str, edge_id: str) -> bool:
        """Delete an edge."""
        session = await self.session_service.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        if edge_id not in session.get("edges", {}):
            return False

        del session["edges"][edge_id]
        session["updated_at"] = datetime.utcnow().isoformat()

        await self._save_session(session)

        return True

    async def list_edges(
        self,
        session_id: str,
        edge_type: Optional[str] = None,
        source_id: Optional[str] = None,
        target_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List edges with optional filtering."""
        session = await self.session_service.get_session(session_id)
        if not session:
            return []

        edges = list(session.get("edges", {}).values())

        if edge_type:
            edges = [e for e in edges if e.get("type") == edge_type]
        if source_id:
            edges = [e for e in edges if e.get("source_id") == source_id]
        if target_id:
            edges = [e for e in edges if e.get("target_id") == target_id]

        return edges

    # =========================================================================
    # Branch Operations
    # =========================================================================

    async def create_branch(
        self,
        session_id: str,
        name: str,
        parent_branch_id: Optional[str] = None,
        fork_node_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new branch."""
        session = await self.session_service.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        branch_id = str(uuid.uuid4())
        now = datetime.utcnow()

        branch = {
            "id": branch_id,
            "name": name,
            "status": "active",
            "utility_score": 0.5,
            "lock_state": "EDITABLE",
            "lock_holder_id": None,
            "parent_branch_id": parent_branch_id,
            "fork_node_id": fork_node_id,
            "metadata": {
                "created_at": now.isoformat(),
            },
        }

        session["branches"][branch_id] = branch
        session["updated_at"] = now.isoformat()

        await self._save_session(session)

        return branch

    async def get_branch(self, session_id: str, branch_id: str) -> Optional[Dict[str, Any]]:
        """Get a branch by ID."""
        session = await self.session_service.get_session(session_id)
        if not session:
            return None
        return session.get("branches", {}).get(branch_id)

    async def update_branch(
        self,
        session_id: str,
        branch_id: str,
        updates: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Update a branch."""
        session = await self.session_service.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        branch = session.get("branches", {}).get(branch_id)
        if not branch:
            raise ValueError(f"Branch {branch_id} not found")

        allowed_fields = ["name", "status", "utility_score", "lock_state", "lock_holder_id"]
        for key, value in updates.items():
            if key in allowed_fields:
                branch[key] = value

        session["updated_at"] = datetime.utcnow().isoformat()

        await self._save_session(session)

        return branch

    async def delete_branch(self, session_id: str, branch_id: str) -> bool:
        """Delete a branch and optionally its nodes."""
        session = await self.session_service.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        if branch_id not in session.get("branches", {}):
            return False

        del session["branches"][branch_id]
        session["updated_at"] = datetime.utcnow().isoformat()

        await self._save_session(session)

        return True

    async def list_branches(self, session_id: str) -> List[Dict[str, Any]]:
        """List all branches in a session."""
        session = await self.session_service.get_session(session_id)
        if not session:
            return []
        return list(session.get("branches", {}).values())

    async def fork_branch(
        self,
        session_id: str,
        source_branch_id: str,
        fork_node_id: str,
        new_branch_name: str,
    ) -> Dict[str, Any]:
        """Fork a branch at a specific node."""
        session = await self.session_service.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        source_branch = session.get("branches", {}).get(source_branch_id)
        if not source_branch:
            raise ValueError(f"Source branch {source_branch_id} not found")

        fork_node = session.get("nodes", {}).get(fork_node_id)
        if not fork_node:
            raise ValueError(f"Fork node {fork_node_id} not found")

        new_branch = await self.create_branch(
            session_id=session_id,
            name=new_branch_name,
            parent_branch_id=source_branch_id,
            fork_node_id=fork_node_id,
        )

        return new_branch

    async def merge_branches(
        self,
        session_id: str,
        source_branch_id: str,
        target_branch_id: str,
        merge_strategy: str = "synthesis",
    ) -> Dict[str, Any]:
        """Merge two branches."""
        session = await self.session_service.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        source_branch = session.get("branches", {}).get(source_branch_id)
        target_branch = session.get("branches", {}).get(target_branch_id)

        if not source_branch or not target_branch:
            raise ValueError("Source or target branch not found")

        # Create synthesis node
        synthesis_node = await self.create_node(
            session_id=session_id,
            node_type="synthesis",
            content=f"Synthesis of branches {source_branch['name']} and {target_branch['name']}",
            branch_id=target_branch_id,
            metadata={"merge_strategy": merge_strategy, "source_branches": [source_branch_id, target_branch_id]},
        )

        # Mark source branch as merged
        source_branch["status"] = "merged"
        session["updated_at"] = datetime.utcnow().isoformat()

        await self._save_session(session)

        return {
            "synthesis_node": synthesis_node,
            "source_branch": source_branch,
            "target_branch": target_branch,
        }

    # =========================================================================
    # Graph Traversal
    # =========================================================================

    async def get_ancestors(self, session_id: str, node_id: str) -> List[Dict[str, Any]]:
        """Get all ancestor nodes of a node."""
        session = await self.session_service.get_session(session_id)
        if not session:
            return []

        nodes = session.get("nodes", {})
        edges = session.get("edges", {})

        ancestors = []
        visited: Set[str] = set()
        queue = [node_id]

        while queue:
            current_id = queue.pop(0)
            if current_id in visited:
                continue
            visited.add(current_id)

            for edge in edges.values():
                if edge.get("target_id") == current_id and edge.get("type") == "decompose":
                    parent_id = edge.get("source_id")
                    if parent_id and parent_id not in visited:
                        parent_node = nodes.get(parent_id)
                        if parent_node:
                            ancestors.append(parent_node)
                            queue.append(parent_id)

        return ancestors

    async def get_descendants(self, session_id: str, node_id: str) -> List[Dict[str, Any]]:
        """Get all descendant nodes of a node."""
        session = await self.session_service.get_session(session_id)
        if not session:
            return []

        nodes = session.get("nodes", {})
        edges = session.get("edges", {})

        descendants = []
        visited: Set[str] = set()
        queue = [node_id]

        while queue:
            current_id = queue.pop(0)
            if current_id in visited:
                continue
            visited.add(current_id)

            for edge in edges.values():
                if edge.get("source_id") == current_id and edge.get("type") == "decompose":
                    child_id = edge.get("target_id")
                    if child_id and child_id not in visited:
                        child_node = nodes.get(child_id)
                        if child_node:
                            descendants.append(child_node)
                            queue.append(child_id)

        return descendants

    async def get_path_to_root(self, session_id: str, node_id: str) -> List[Dict[str, Any]]:
        """Get path from node to root goal node."""
        session = await self.session_service.get_session(session_id)
        if not session:
            return []

        nodes = session.get("nodes", {})
        edges = session.get("edges", {})

        path = []
        current_id = node_id

        while current_id:
            node = nodes.get(current_id)
            if not node:
                break
            path.append(node)

            if node.get("type") == "goal":
                break

            parent_id = None
            for edge in edges.values():
                if edge.get("target_id") == current_id and edge.get("type") == "decompose":
                    parent_id = edge.get("source_id")
                    break

            current_id = parent_id

        return path

    async def get_graph_statistics(self, session_id: str) -> Dict[str, Any]:
        """Get comprehensive graph statistics."""
        session = await self.session_service.get_session(session_id)
        if not session:
            return {}

        nodes = session.get("nodes", {})
        edges = session.get("edges", {})
        branches = session.get("branches", {})

        node_types = {}
        edge_types = {}
        layers = {}

        for node in nodes.values():
            node_type = node.get("type", "unknown")
            node_types[node_type] = node_types.get(node_type, 0) + 1

            layer = node.get("layer", 0)
            layers[layer] = layers.get(layer, 0) + 1

        for edge in edges.values():
            edge_type = edge.get("type", "unknown")
            edge_types[edge_type] = edge_types.get(edge_type, 0) + 1

        avg_confidence = sum(n.get("confidence", 0) for n in nodes.values()) / len(nodes) if nodes else 0
        avg_utility = sum(n.get("utility", 0) for n in nodes.values()) / len(nodes) if nodes else 0

        return {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "branch_count": len(branches),
            "node_types": node_types,
            "edge_types": edge_types,
            "layers": layers,
            "avg_confidence": avg_confidence,
            "avg_utility": avg_utility,
        }

    # =========================================================================
    # Helper Methods
    # =========================================================================

    async def _save_session(self, session: Dict[str, Any]) -> None:
        """Save session to storage."""
        session_id = session.get("id")
        if self.session_service:
            self.session_service._memory_store[session_id] = session
            if self.session_service.redis:
                await self.session_service.redis.set(
                    f"session:{session_id}",
                    json.dumps(session),
                    ex=86400
                )


def get_graph_service(session_service=None, redis=None, lock_service=None) -> GraphService:
    """Factory function for GraphService."""
    return GraphService(session_service=session_service, redis=redis, lock_service=lock_service)

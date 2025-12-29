"""
PostgreSQL Graph Queries

PostgreSQL CTE-based graph traversal queries for the layered graph network.
Replaces Neo4j for MVP phase with recursive Common Table Expressions.
"""

from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text


class GraphQueryService:
    """
    Service for executing graph traversal queries using PostgreSQL CTEs.

    This service provides graph operations using PostgreSQL's recursive
    Common Table Expressions (WITH RECURSIVE) instead of a dedicated
    graph database like Neo4j.

    Supported operations:
    - Ancestor lookup (recursive parent traversal)
    - Descendant lookup (recursive child traversal)
    - Path finding between nodes
    - Cycle detection for deadlock prevention
    - Layer-based queries

    Performance considerations:
    - Optimized for graph depths <= 10 layers
    - Uses indexes on (session_id, layer) and (source_id, target_id)
    - Max depth is configurable to prevent runaway queries

    Attributes:
        db: SQLAlchemy async session
        max_depth: Maximum traversal depth (default: 10)
    """

    def __init__(
        self,
        db: AsyncSession,
        max_depth: int = 10,
    ):
        """
        Initialize the graph query service.

        Args:
            db: SQLAlchemy async session for database operations
            max_depth: Maximum recursion depth for CTE queries
        """
        self.db = db
        self.max_depth = max_depth

    async def get_ancestors(
        self,
        node_id: str,
        max_depth: Optional[int] = None,
    ) -> List[dict]:
        """
        Get all ancestors of a node using recursive CTE.

        Traverses the graph upward through 'decompose' edges to find
        all parent nodes up to the root (GoalNode).

        Args:
            node_id: ID of the node to find ancestors for
            max_depth: Optional override for maximum depth

        Returns:
            List[dict]: List of ancestor nodes ordered by depth (closest first)
        """
        depth_limit = max_depth or self.max_depth

        query = text("""
            WITH RECURSIVE ancestors AS (
                -- Base case: start from the given node
                SELECT n.id, n.session_id, n.branch_id, n.type, n.content,
                       n.layer, n.status, n.metadata, n.created_at, n.updated_at,
                       0 as depth
                FROM nodes n
                WHERE n.id = :node_id

                UNION ALL

                -- Recursive case: follow decompose edges upward
                SELECT parent.id, parent.session_id, parent.branch_id, parent.type,
                       parent.content, parent.layer, parent.status, parent.metadata,
                       parent.created_at, parent.updated_at,
                       a.depth + 1
                FROM nodes parent
                JOIN edges e ON e.source_id = parent.id
                JOIN ancestors a ON e.target_id = a.id
                WHERE e.type = 'decompose'
                AND a.depth < :max_depth
            )
            SELECT id, session_id, branch_id, type, content, layer, status,
                   metadata, created_at, updated_at, depth
            FROM ancestors
            WHERE id != :node_id
            ORDER BY depth ASC
        """)

        result = await self.db.execute(
            query,
            {"node_id": node_id, "max_depth": depth_limit}
        )
        rows = result.fetchall()

        return [
            {
                "id": str(row.id),
                "session_id": str(row.session_id),
                "branch_id": str(row.branch_id) if row.branch_id else None,
                "type": row.type,
                "content": row.content,
                "layer": row.layer,
                "status": row.status,
                "metadata": row.metadata,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "updated_at": row.updated_at.isoformat() if row.updated_at else None,
                "depth": row.depth,
            }
            for row in rows
        ]

    async def get_descendants(
        self,
        node_id: str,
        max_depth: Optional[int] = None,
    ) -> List[dict]:
        """
        Get all descendants of a node using recursive CTE.

        Traverses the graph downward through 'decompose' edges to find
        all child nodes down to the leaf layer.

        Args:
            node_id: ID of the node to find descendants for
            max_depth: Optional override for maximum depth

        Returns:
            List[dict]: List of descendant nodes ordered by depth
        """
        depth_limit = max_depth or self.max_depth

        query = text("""
            WITH RECURSIVE descendants AS (
                -- Base case: start from the given node
                SELECT n.id, n.session_id, n.branch_id, n.type, n.content,
                       n.layer, n.status, n.metadata, n.created_at, n.updated_at,
                       0 as depth
                FROM nodes n
                WHERE n.id = :node_id

                UNION ALL

                -- Recursive case: follow decompose edges downward
                SELECT child.id, child.session_id, child.branch_id, child.type,
                       child.content, child.layer, child.status, child.metadata,
                       child.created_at, child.updated_at,
                       d.depth + 1
                FROM nodes child
                JOIN edges e ON e.target_id = child.id
                JOIN descendants d ON e.source_id = d.id
                WHERE e.type = 'decompose'
                AND d.depth < :max_depth
            )
            SELECT id, session_id, branch_id, type, content, layer, status,
                   metadata, created_at, updated_at, depth
            FROM descendants
            WHERE id != :node_id
            ORDER BY depth ASC
        """)

        result = await self.db.execute(
            query,
            {"node_id": node_id, "max_depth": depth_limit}
        )
        rows = result.fetchall()

        return [
            {
                "id": str(row.id),
                "session_id": str(row.session_id),
                "branch_id": str(row.branch_id) if row.branch_id else None,
                "type": row.type,
                "content": row.content,
                "layer": row.layer,
                "status": row.status,
                "metadata": row.metadata,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "updated_at": row.updated_at.isoformat() if row.updated_at else None,
                "depth": row.depth,
            }
            for row in rows
        ]

    async def get_causal_path(
        self,
        from_node_id: str,
        to_node_id: str,
    ) -> List[dict]:
        """
        Find the causal path between two nodes.

        Searches for a path following 'decompose', 'support', and 'entail'
        edges (causal view projection).

        Uses bidirectional BFS implemented with CTEs for efficiency.

        Args:
            from_node_id: Source node ID
            to_node_id: Target node ID

        Returns:
            List[dict]: Ordered list of nodes forming the path,
                       empty list if no path exists
        """
        query = text("""
            WITH RECURSIVE path_search AS (
                -- Base case: start from source node
                SELECT
                    n.id,
                    n.session_id,
                    n.type,
                    n.content,
                    n.layer,
                    ARRAY[n.id] as path,
                    0 as depth
                FROM nodes n
                WHERE n.id = :from_node_id

                UNION ALL

                -- Recursive case: follow causal edges
                SELECT
                    next_node.id,
                    next_node.session_id,
                    next_node.type,
                    next_node.content,
                    next_node.layer,
                    ps.path || next_node.id,
                    ps.depth + 1
                FROM path_search ps
                JOIN edges e ON (e.source_id = ps.id OR e.target_id = ps.id)
                JOIN nodes next_node ON (
                    (e.target_id = next_node.id AND e.source_id = ps.id) OR
                    (e.source_id = next_node.id AND e.target_id = ps.id)
                )
                WHERE e.type IN ('decompose', 'support', 'entail')
                AND NOT next_node.id = ANY(ps.path)
                AND ps.depth < :max_depth
            )
            SELECT path
            FROM path_search
            WHERE id = :to_node_id
            ORDER BY depth ASC
            LIMIT 1
        """)

        result = await self.db.execute(
            query,
            {
                "from_node_id": from_node_id,
                "to_node_id": to_node_id,
                "max_depth": self.max_depth
            }
        )
        row = result.fetchone()

        if not row:
            return []

        # Fetch full node data for the path
        path_ids = row.path
        nodes_query = text("""
            SELECT id, session_id, branch_id, type, content, layer, status,
                   metadata, created_at, updated_at
            FROM nodes
            WHERE id = ANY(:path_ids)
        """)

        nodes_result = await self.db.execute(
            nodes_query,
            {"path_ids": path_ids}
        )
        nodes_map = {
            str(r.id): {
                "id": str(r.id),
                "session_id": str(r.session_id),
                "branch_id": str(r.branch_id) if r.branch_id else None,
                "type": r.type,
                "content": r.content,
                "layer": r.layer,
                "status": r.status,
                "metadata": r.metadata,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "updated_at": r.updated_at.isoformat() if r.updated_at else None,
            }
            for r in nodes_result.fetchall()
        }

        return [nodes_map[str(nid)] for nid in path_ids if str(nid) in nodes_map]

    async def detect_cycles(
        self,
        session_id: str,
    ) -> List[List[str]]:
        """
        Detect cycles in the graph for deadlock prevention.

        Cycles in the reasoning graph indicate logical circular dependencies
        that must be resolved before convergence.

        Uses Tarjan's algorithm adapted for SQL with recursive CTE.

        Args:
            session_id: ID of the session to check

        Returns:
            List[List[str]]: List of cycles, each cycle is a list of node IDs
        """
        query = text("""
            WITH RECURSIVE cycle_detection AS (
                -- Start from each node in the session
                SELECT
                    n.id as start_id,
                    n.id as current_id,
                    ARRAY[n.id] as path,
                    false as is_cycle
                FROM nodes n
                WHERE n.session_id = :session_id
                AND n.status = 'active'

                UNION ALL

                -- Follow edges and detect cycles
                SELECT
                    cd.start_id,
                    e.target_id as current_id,
                    cd.path || e.target_id,
                    e.target_id = cd.start_id as is_cycle
                FROM cycle_detection cd
                JOIN edges e ON e.source_id = cd.current_id
                WHERE NOT cd.is_cycle
                AND array_length(cd.path, 1) < :max_depth
                AND (
                    NOT e.target_id = ANY(cd.path[2:])
                    OR e.target_id = cd.start_id
                )
            )
            SELECT DISTINCT path
            FROM cycle_detection
            WHERE is_cycle
            AND array_length(path, 1) > 2
        """)

        result = await self.db.execute(
            query,
            {"session_id": session_id, "max_depth": self.max_depth}
        )
        rows = result.fetchall()

        return [[str(nid) for nid in row.path] for row in rows]

    async def get_nodes_at_layer(
        self,
        session_id: str,
        layer: int,
    ) -> List[dict]:
        """
        Get all nodes at a specific layer in the graph.

        Args:
            session_id: ID of the session
            layer: Layer index (0 = root layer)

        Returns:
            List[dict]: List of nodes at the specified layer
        """
        query = text("""
            SELECT id, session_id, branch_id, type, content, layer, status,
                   metadata, created_at, updated_at
            FROM nodes
            WHERE session_id = :session_id
            AND layer = :layer
            AND status = 'active'
            ORDER BY created_at ASC
        """)

        result = await self.db.execute(
            query,
            {"session_id": session_id, "layer": layer}
        )
        rows = result.fetchall()

        return [
            {
                "id": str(row.id),
                "session_id": str(row.session_id),
                "branch_id": str(row.branch_id) if row.branch_id else None,
                "type": row.type,
                "content": row.content,
                "layer": row.layer,
                "status": row.status,
                "metadata": row.metadata,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "updated_at": row.updated_at.isoformat() if row.updated_at else None,
            }
            for row in rows
        ]

    async def get_horizontal_edges(
        self,
        session_id: str,
        layer: int,
    ) -> List[dict]:
        """
        Get all horizontal edges (support, attack, conflict, entail)
        between nodes at a specific layer.

        Args:
            session_id: ID of the session
            layer: Layer index

        Returns:
            List[dict]: List of horizontal edges at the layer
        """
        query = text("""
            SELECT e.id, e.session_id, e.source_id, e.target_id, e.type,
                   e.direction, e.weight, e.metadata, e.created_at
            FROM edges e
            JOIN nodes source_node ON e.source_id = source_node.id
            JOIN nodes target_node ON e.target_id = target_node.id
            WHERE e.session_id = :session_id
            AND source_node.layer = :layer
            AND target_node.layer = :layer
            AND e.direction = 'horizontal'
            ORDER BY e.created_at ASC
        """)

        result = await self.db.execute(
            query,
            {"session_id": session_id, "layer": layer}
        )
        rows = result.fetchall()

        return [
            {
                "id": str(row.id),
                "session_id": str(row.session_id),
                "source_id": str(row.source_id),
                "target_id": str(row.target_id),
                "type": row.type,
                "direction": row.direction,
                "weight": row.weight,
                "metadata": row.metadata,
                "created_at": row.created_at.isoformat() if row.created_at else None,
            }
            for row in rows
        ]

    async def get_branch_subgraph(
        self,
        branch_id: str,
    ) -> Tuple[List[dict], List[dict]]:
        """
        Get all nodes and edges belonging to a specific branch.

        Args:
            branch_id: ID of the branch

        Returns:
            Tuple[List[dict], List[dict]]: (nodes, edges) for the branch
        """
        # Get nodes
        nodes_query = text("""
            SELECT id, session_id, branch_id, type, content, layer, status,
                   metadata, created_at, updated_at
            FROM nodes
            WHERE branch_id = :branch_id
            ORDER BY layer ASC, created_at ASC
        """)

        nodes_result = await self.db.execute(
            nodes_query,
            {"branch_id": branch_id}
        )
        nodes_rows = nodes_result.fetchall()

        nodes = [
            {
                "id": str(row.id),
                "session_id": str(row.session_id),
                "branch_id": str(row.branch_id) if row.branch_id else None,
                "type": row.type,
                "content": row.content,
                "layer": row.layer,
                "status": row.status,
                "metadata": row.metadata,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "updated_at": row.updated_at.isoformat() if row.updated_at else None,
            }
            for row in nodes_rows
        ]

        # Get edges between branch nodes
        node_ids = [n["id"] for n in nodes]
        if not node_ids:
            return nodes, []

        edges_query = text("""
            SELECT id, session_id, source_id, target_id, type, direction,
                   weight, metadata, created_at
            FROM edges
            WHERE source_id = ANY(:node_ids)
            AND target_id = ANY(:node_ids)
            ORDER BY created_at ASC
        """)

        edges_result = await self.db.execute(
            edges_query,
            {"node_ids": node_ids}
        )
        edges_rows = edges_result.fetchall()

        edges = [
            {
                "id": str(row.id),
                "session_id": str(row.session_id),
                "source_id": str(row.source_id),
                "target_id": str(row.target_id),
                "type": row.type,
                "direction": row.direction,
                "weight": row.weight,
                "metadata": row.metadata,
                "created_at": row.created_at.isoformat() if row.created_at else None,
            }
            for row in edges_rows
        ]

        return nodes, edges

    async def get_conflict_graph(
        self,
        session_id: str,
    ) -> Tuple[List[dict], List[dict]]:
        """
        Get the conflict view projection of the graph.

        Returns only nodes connected by 'attack' or 'conflict' edges,
        used for game-theoretic analysis and Nash equilibrium computation.

        Args:
            session_id: ID of the session

        Returns:
            Tuple[List[dict], List[dict]]: (nodes, edges) in conflict view
        """
        # Get conflict edges
        edges_query = text("""
            SELECT id, session_id, source_id, target_id, type, direction,
                   weight, metadata, created_at
            FROM edges
            WHERE session_id = :session_id
            AND type IN ('attack', 'conflict')
            ORDER BY created_at ASC
        """)

        edges_result = await self.db.execute(
            edges_query,
            {"session_id": session_id}
        )
        edges_rows = edges_result.fetchall()

        edges = [
            {
                "id": str(row.id),
                "session_id": str(row.session_id),
                "source_id": str(row.source_id),
                "target_id": str(row.target_id),
                "type": row.type,
                "direction": row.direction,
                "weight": row.weight,
                "metadata": row.metadata,
                "created_at": row.created_at.isoformat() if row.created_at else None,
            }
            for row in edges_rows
        ]

        # Get unique node IDs from edges
        node_ids = set()
        for edge in edges:
            node_ids.add(edge["source_id"])
            node_ids.add(edge["target_id"])

        if not node_ids:
            return [], []

        # Get nodes
        nodes_query = text("""
            SELECT id, session_id, branch_id, type, content, layer, status,
                   metadata, created_at, updated_at
            FROM nodes
            WHERE id = ANY(:node_ids)
            ORDER BY layer ASC, created_at ASC
        """)

        nodes_result = await self.db.execute(
            nodes_query,
            {"node_ids": list(node_ids)}
        )
        nodes_rows = nodes_result.fetchall()

        nodes = [
            {
                "id": str(row.id),
                "session_id": str(row.session_id),
                "branch_id": str(row.branch_id) if row.branch_id else None,
                "type": row.type,
                "content": row.content,
                "layer": row.layer,
                "status": row.status,
                "metadata": row.metadata,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "updated_at": row.updated_at.isoformat() if row.updated_at else None,
            }
            for row in nodes_rows
        ]

        return nodes, edges

    async def get_support_graph(
        self,
        session_id: str,
    ) -> Tuple[List[dict], List[dict]]:
        """
        Get the support view projection of the graph.

        Returns only nodes connected by 'support' or 'entail' edges,
        used for argument strength analysis.

        Args:
            session_id: ID of the session

        Returns:
            Tuple[List[dict], List[dict]]: (nodes, edges) in support view
        """
        edges_query = text("""
            SELECT id, session_id, source_id, target_id, type, direction,
                   weight, metadata, created_at
            FROM edges
            WHERE session_id = :session_id
            AND type IN ('support', 'entail')
            ORDER BY created_at ASC
        """)

        edges_result = await self.db.execute(
            edges_query,
            {"session_id": session_id}
        )
        edges_rows = edges_result.fetchall()

        edges = [
            {
                "id": str(row.id),
                "session_id": str(row.session_id),
                "source_id": str(row.source_id),
                "target_id": str(row.target_id),
                "type": row.type,
                "direction": row.direction,
                "weight": row.weight,
                "metadata": row.metadata,
                "created_at": row.created_at.isoformat() if row.created_at else None,
            }
            for row in edges_rows
        ]

        node_ids = set()
        for edge in edges:
            node_ids.add(edge["source_id"])
            node_ids.add(edge["target_id"])

        if not node_ids:
            return [], []

        nodes_query = text("""
            SELECT id, session_id, branch_id, type, content, layer, status,
                   metadata, created_at, updated_at
            FROM nodes
            WHERE id = ANY(:node_ids)
            ORDER BY layer ASC, created_at ASC
        """)

        nodes_result = await self.db.execute(
            nodes_query,
            {"node_ids": list(node_ids)}
        )
        nodes_rows = nodes_result.fetchall()

        nodes = [
            {
                "id": str(row.id),
                "session_id": str(row.session_id),
                "branch_id": str(row.branch_id) if row.branch_id else None,
                "type": row.type,
                "content": row.content,
                "layer": row.layer,
                "status": row.status,
                "metadata": row.metadata,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "updated_at": row.updated_at.isoformat() if row.updated_at else None,
            }
            for row in nodes_rows
        ]

        return nodes, edges

    async def compute_node_degree(
        self,
        node_id: str,
    ) -> Dict[str, int]:
        """
        Compute in-degree and out-degree for a node.

        Args:
            node_id: ID of the node

        Returns:
            Dict with 'in_degree', 'out_degree', 'total_degree'
        """
        query = text("""
            SELECT
                COUNT(CASE WHEN target_id = :node_id THEN 1 END) as in_degree,
                COUNT(CASE WHEN source_id = :node_id THEN 1 END) as out_degree
            FROM edges
            WHERE source_id = :node_id OR target_id = :node_id
        """)

        result = await self.db.execute(query, {"node_id": node_id})
        row = result.fetchone()

        in_deg = row.in_degree or 0
        out_deg = row.out_degree or 0

        return {
            "in_degree": in_deg,
            "out_degree": out_deg,
            "total_degree": in_deg + out_deg,
        }

    async def get_leaf_nodes(
        self,
        session_id: str,
    ) -> List[dict]:
        """
        Get all leaf nodes (nodes with no outgoing decompose edges).

        Args:
            session_id: ID of the session

        Returns:
            List[dict]: List of leaf nodes
        """
        query = text("""
            SELECT n.id, n.session_id, n.branch_id, n.type, n.content,
                   n.layer, n.status, n.metadata, n.created_at, n.updated_at
            FROM nodes n
            WHERE n.session_id = :session_id
            AND n.status = 'active'
            AND NOT EXISTS (
                SELECT 1 FROM edges e
                WHERE e.source_id = n.id
                AND e.type = 'decompose'
            )
            ORDER BY n.layer DESC, n.created_at ASC
        """)

        result = await self.db.execute(query, {"session_id": session_id})
        rows = result.fetchall()

        return [
            {
                "id": str(row.id),
                "session_id": str(row.session_id),
                "branch_id": str(row.branch_id) if row.branch_id else None,
                "type": row.type,
                "content": row.content,
                "layer": row.layer,
                "status": row.status,
                "metadata": row.metadata,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "updated_at": row.updated_at.isoformat() if row.updated_at else None,
            }
            for row in rows
        ]

    async def get_root_nodes(
        self,
        session_id: str,
    ) -> List[dict]:
        """
        Get all root nodes (nodes with no incoming decompose edges).

        Args:
            session_id: ID of the session

        Returns:
            List[dict]: List of root nodes
        """
        query = text("""
            SELECT n.id, n.session_id, n.branch_id, n.type, n.content,
                   n.layer, n.status, n.metadata, n.created_at, n.updated_at
            FROM nodes n
            WHERE n.session_id = :session_id
            AND n.status = 'active'
            AND n.layer = 0
            ORDER BY n.created_at ASC
        """)

        result = await self.db.execute(query, {"session_id": session_id})
        rows = result.fetchall()

        return [
            {
                "id": str(row.id),
                "session_id": str(row.session_id),
                "branch_id": str(row.branch_id) if row.branch_id else None,
                "type": row.type,
                "content": row.content,
                "layer": row.layer,
                "status": row.status,
                "metadata": row.metadata,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "updated_at": row.updated_at.isoformat() if row.updated_at else None,
            }
            for row in rows
        ]

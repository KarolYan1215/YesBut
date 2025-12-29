"""
Path Failure Analysis Algorithm

Identifies critical paths (statically determinate) and redundant supports
(statically indeterminate) in the reasoning graph. Computes minimal cut sets.
"""

from typing import Dict, Any, List, Set, Tuple, Optional
from collections import defaultdict


class PathAnalyzer:
    """
    Path failure analyzer for reasoning graph stability.

    Identifies structural properties of the reasoning graph:
    - Critical paths: Single paths where any node failure collapses conclusion
    - Redundant paths: Multiple paths that can compensate for failures
    - Minimal cut sets: Smallest node sets whose failure disconnects goal

    Structural Mechanics Analogy:
    - Critical paths = statically determinate structures (no redundancy)
    - Redundant paths = statically indeterminate structures (backup support)

    Attributes:
        graph: Graph data (nodes and edges)
        goal_node_id: ID of the root goal node
    """

    def __init__(
        self,
        graph: Dict[str, Any],
        goal_node_id: str,
    ):
        """
        Initialize the path analyzer.

        Args:
            graph: Graph data containing nodes and edges
            goal_node_id: ID of the root goal node
        """
        self.graph = graph
        self.goal_node_id = goal_node_id
        self._build_adjacency()

    def _build_adjacency(self) -> None:
        """Build adjacency lists from graph data."""
        self.nodes = {n["id"]: n for n in self.graph.get("nodes", [])}
        self.edges = self.graph.get("edges", [])

        # Build adjacency lists
        self.children = defaultdict(list)  # parent -> children
        self.parents = defaultdict(list)   # child -> parents

        for edge in self.edges:
            source = edge.get("source_id")
            target = edge.get("target_id")
            edge_type = edge.get("type")

            if edge_type == "decompose":
                self.children[source].append(target)
                self.parents[target].append(source)

    def analyze(self) -> Dict[str, Any]:
        """
        Run full path analysis.

        Returns:
            Dict containing:
            - critical_paths: List of critical path info
            - redundant_paths: List of redundant path info
            - minimal_cut_sets: List of minimal cut sets
            - redundancy_ratio: Overall redundancy ratio
            - structural_classification: 'determinate' or 'indeterminate'
        """
        # Find all leaf nodes
        leaf_nodes = self._find_leaf_nodes()

        # Find all paths from goal to leaves
        all_paths = []
        for leaf in leaf_nodes:
            paths = self.find_all_paths(self.goal_node_id, leaf)
            all_paths.extend(paths)

        # Classify paths
        critical_paths = []
        redundant_paths = []

        for i, path in enumerate(all_paths):
            classification = self.classify_path(path, all_paths)
            path_info = {
                "path_id": f"path_{i}",
                "node_ids": path,
                **classification,
            }

            if classification["classification"] == "critical":
                critical_paths.append(path_info)
            else:
                redundant_paths.append(path_info)

        # Compute minimal cut sets
        minimal_cut_sets = self.compute_minimal_cut_sets()

        # Compute redundancy ratio
        redundancy_ratio = self.compute_redundancy_ratio()

        # Determine structural classification
        if len(critical_paths) > len(redundant_paths):
            structural_classification = "determinate"
        else:
            structural_classification = "indeterminate"

        return {
            "critical_paths": critical_paths,
            "redundant_paths": redundant_paths,
            "minimal_cut_sets": [list(s) for s in minimal_cut_sets],
            "redundancy_ratio": redundancy_ratio,
            "structural_classification": structural_classification,
            "total_paths": len(all_paths),
        }

    def _find_leaf_nodes(self) -> List[str]:
        """Find all leaf nodes (nodes with no children)."""
        return [
            node_id for node_id in self.nodes
            if not self.children[node_id]
        ]

    def find_all_paths(
        self,
        from_node_id: str,
        to_node_id: str,
        visited: Optional[Set[str]] = None,
        max_depth: int = 20,
    ) -> List[List[str]]:
        """
        Find all paths between two nodes.

        Uses DFS to enumerate all simple paths.

        Args:
            from_node_id: Source node ID
            to_node_id: Target node ID
            visited: Set of visited nodes (for recursion)
            max_depth: Maximum path depth to prevent infinite loops

        Returns:
            List[List[str]]: List of paths (each path is list of node IDs)
        """
        if visited is None:
            visited = set()

        if from_node_id == to_node_id:
            return [[from_node_id]]

        if from_node_id in visited or max_depth <= 0:
            return []

        visited.add(from_node_id)
        paths = []

        for child in self.children[from_node_id]:
            child_paths = self.find_all_paths(
                child, to_node_id, visited.copy(), max_depth - 1
            )
            for path in child_paths:
                paths.append([from_node_id] + path)

        return paths

    def classify_path(
        self,
        path: List[str],
        all_paths: List[List[str]],
    ) -> Dict[str, Any]:
        """
        Classify a path as critical or redundant.

        A path is critical if no alternative paths exist for any
        of its nodes. Otherwise it's redundant.

        Args:
            path: Path to classify (list of node IDs)
            all_paths: All paths in the graph

        Returns:
            Dict containing:
            - classification: 'critical' or 'redundant'
            - critical_nodes: Nodes that are critical on this path
            - alternative_count: Number of alternative paths
        """
        if not path or len(path) < 2:
            return {
                "classification": "critical",
                "critical_nodes": path,
                "alternative_count": 0,
            }

        # Find nodes that appear only in this path
        path_set = set(path)
        critical_nodes = []

        for node_id in path[1:-1]:  # Exclude start and end
            # Count paths containing this node
            paths_with_node = sum(
                1 for p in all_paths if node_id in p
            )

            # If only one path contains this node, it's critical
            if paths_with_node == 1:
                critical_nodes.append(node_id)

        # Count alternative paths (paths with same start/end but different middle)
        start, end = path[0], path[-1]
        alternative_paths = [
            p for p in all_paths
            if p[0] == start and p[-1] == end and p != path
        ]

        classification = "critical" if critical_nodes else "redundant"

        return {
            "classification": classification,
            "critical_nodes": critical_nodes,
            "alternative_count": len(alternative_paths),
        }

    def compute_minimal_cut_sets(self) -> List[Set[str]]:
        """
        Compute minimal cut sets for the graph.

        A minimal cut set is the smallest set of nodes whose removal
        disconnects the goal from all supporting evidence.

        Uses Karger's algorithm or Ford-Fulkerson for min-cut.

        Returns:
            List[Set[str]]: List of minimal cut sets
        """
        leaf_nodes = self._find_leaf_nodes()
        if not leaf_nodes:
            return []

        all_cut_sets = []

        # For each leaf, find nodes that disconnect goal from leaf
        for leaf in leaf_nodes:
            paths = self.find_all_paths(self.goal_node_id, leaf)
            if not paths:
                continue

            # Find nodes common to all paths (excluding goal and leaf)
            if len(paths) == 1:
                # Single path: every intermediate node is a cut set
                for node in paths[0][1:-1]:
                    all_cut_sets.append({node})
            else:
                # Multiple paths: find intersection
                common = set(paths[0][1:-1])
                for path in paths[1:]:
                    common &= set(path[1:-1])

                for node in common:
                    all_cut_sets.append({node})

        # Remove duplicate and non-minimal sets
        minimal_sets = self._minimize_cut_sets(all_cut_sets)

        return minimal_sets

    def _minimize_cut_sets(
        self,
        cut_sets: List[Set[str]],
    ) -> List[Set[str]]:
        """Remove non-minimal cut sets."""
        if not cut_sets:
            return []

        # Sort by size
        sorted_sets = sorted(cut_sets, key=len)
        minimal = []

        for cut_set in sorted_sets:
            # Check if any existing minimal set is a subset
            is_minimal = True
            for existing in minimal:
                if existing <= cut_set:
                    is_minimal = False
                    break

            if is_minimal:
                # Remove any existing sets that are supersets
                minimal = [m for m in minimal if not cut_set < m]
                if cut_set not in minimal:
                    minimal.append(cut_set)

        return minimal

    def compute_node_criticality(
        self,
        node_id: str,
    ) -> float:
        """
        Compute criticality score for a single node.

        Criticality = 1 / (number of alternative paths bypassing this node)

        Args:
            node_id: ID of the node

        Returns:
            float: Criticality score (0-1, higher = more critical)
        """
        if node_id not in self.nodes:
            return 0.0

        leaf_nodes = self._find_leaf_nodes()
        total_paths = 0
        paths_with_node = 0

        for leaf in leaf_nodes:
            paths = self.find_all_paths(self.goal_node_id, leaf)
            for path in paths:
                total_paths += 1
                if node_id in path:
                    paths_with_node += 1

        if total_paths == 0:
            return 0.0

        # Criticality based on path coverage
        coverage = paths_with_node / total_paths

        # If node is in all paths, it's maximally critical
        if paths_with_node == total_paths:
            return 1.0

        # Otherwise, criticality is proportional to coverage
        return coverage

    def compute_redundancy_ratio(self) -> float:
        """
        Compute overall redundancy ratio.

        Redundancy ratio = |redundant paths| / |critical paths|

        Returns:
            float: Redundancy ratio (higher = more robust)
        """
        leaf_nodes = self._find_leaf_nodes()
        critical_count = 0
        redundant_count = 0

        for leaf in leaf_nodes:
            paths = self.find_all_paths(self.goal_node_id, leaf)
            if len(paths) == 1:
                critical_count += 1
            else:
                redundant_count += len(paths)

        if critical_count == 0:
            return float('inf') if redundant_count > 0 else 1.0

        return redundant_count / critical_count

    def identify_bottlenecks(self) -> List[Dict[str, Any]]:
        """
        Identify structural bottlenecks in the graph.

        Bottlenecks are nodes that appear in all paths to certain conclusions.

        Returns:
            List[Dict]: Bottleneck nodes with affected conclusions
        """
        leaf_nodes = self._find_leaf_nodes()
        bottlenecks = []

        # Count how many leaves each node is required for
        node_to_leaves = defaultdict(set)

        for leaf in leaf_nodes:
            paths = self.find_all_paths(self.goal_node_id, leaf)
            if not paths:
                continue

            # Find nodes in all paths to this leaf
            common_nodes = set(paths[0])
            for path in paths[1:]:
                common_nodes &= set(path)

            # Exclude goal and leaf
            common_nodes -= {self.goal_node_id, leaf}

            for node in common_nodes:
                node_to_leaves[node].add(leaf)

        # Create bottleneck info
        for node_id, affected_leaves in node_to_leaves.items():
            if len(affected_leaves) > 0:
                bottlenecks.append({
                    "node_id": node_id,
                    "affected_conclusions": list(affected_leaves),
                    "impact_score": len(affected_leaves) / len(leaf_nodes),
                })

        # Sort by impact
        bottlenecks.sort(key=lambda x: x["impact_score"], reverse=True)

        return bottlenecks

    def simulate_path_failure(
        self,
        path: List[str],
    ) -> Dict[str, Any]:
        """
        Simulate failure of an entire path.

        Args:
            path: Path to simulate failure for

        Returns:
            Dict containing:
            - remaining_paths: Paths still valid after failure
            - affected_conclusions: Conclusions affected
            - can_recover: Whether graph can recover via alternatives
        """
        if not path:
            return {
                "remaining_paths": [],
                "affected_conclusions": [],
                "can_recover": True,
            }

        leaf_nodes = self._find_leaf_nodes()
        path_set = set(path)

        remaining_paths = []
        affected_conclusions = []

        for leaf in leaf_nodes:
            paths = self.find_all_paths(self.goal_node_id, leaf)

            # Filter out paths that share nodes with failed path
            valid_paths = [
                p for p in paths
                if not (set(p[1:-1]) & path_set)  # No shared intermediate nodes
            ]

            if valid_paths:
                remaining_paths.extend(valid_paths)
            else:
                affected_conclusions.append(leaf)

        can_recover = len(affected_conclusions) == 0

        return {
            "remaining_paths": remaining_paths,
            "affected_conclusions": affected_conclusions,
            "can_recover": can_recover,
        }

    def get_path_visualization_data(self) -> Dict[str, Any]:
        """
        Get data for path criticality visualization.

        Returns:
            Dict containing:
            - edges: List of edges with criticality classification
            - nodes: List of nodes with criticality scores
            - cut_set_nodes: Nodes in minimal cut sets
        """
        # Compute node criticality
        node_data = []
        for node_id in self.nodes:
            criticality = self.compute_node_criticality(node_id)
            node_data.append({
                "id": node_id,
                "criticality": criticality,
                "is_critical": criticality > 0.8,
            })

        # Classify edges
        edge_data = []
        for edge in self.edges:
            source = edge.get("source_id")
            target = edge.get("target_id")

            # Edge is critical if both endpoints are critical
            source_crit = self.compute_node_criticality(source)
            target_crit = self.compute_node_criticality(target)

            edge_data.append({
                "source_id": source,
                "target_id": target,
                "type": edge.get("type"),
                "criticality": (source_crit + target_crit) / 2,
                "is_critical": source_crit > 0.8 and target_crit > 0.8,
            })

        # Get cut set nodes
        cut_sets = self.compute_minimal_cut_sets()
        cut_set_nodes = set()
        for cut_set in cut_sets:
            cut_set_nodes.update(cut_set)

        return {
            "nodes": node_data,
            "edges": edge_data,
            "cut_set_nodes": list(cut_set_nodes),
        }

    def get_path_statistics(self) -> Dict[str, Any]:
        """
        Get statistical summary of paths in the graph.

        Returns:
            Dict with path statistics
        """
        leaf_nodes = self._find_leaf_nodes()
        all_paths = []

        for leaf in leaf_nodes:
            paths = self.find_all_paths(self.goal_node_id, leaf)
            all_paths.extend(paths)

        if not all_paths:
            return {
                "total_paths": 0,
                "avg_path_length": 0,
                "max_path_length": 0,
                "min_path_length": 0,
                "unique_nodes_in_paths": 0,
            }

        path_lengths = [len(p) for p in all_paths]
        unique_nodes = set()
        for path in all_paths:
            unique_nodes.update(path)

        return {
            "total_paths": len(all_paths),
            "avg_path_length": sum(path_lengths) / len(path_lengths),
            "max_path_length": max(path_lengths),
            "min_path_length": min(path_lengths),
            "unique_nodes_in_paths": len(unique_nodes),
        }

"""
Sensitivity Analysis Algorithm

Structural mechanics-inspired sensitivity analysis for reasoning graph stability.
Identifies critical paths and redundant supports in the reasoning structure.
"""

from typing import Dict, Any, List, Tuple, Set, Optional
import random
import math
from collections import defaultdict


class SensitivityAnalyzer:
    """
    Sensitivity analyzer for reasoning graph stability.

    Inspired by structural mechanics, analyzes how node and path
    invalidation affects the overall reasoning structure.

    Key Concepts:
    - Statically Determinate Core: Paths where every node is critical;
      any failure collapses the conclusion
    - Redundant Support: Alternative paths that can compensate for
      localized failures

    Structural Analogy:
    - Critical paths = load-bearing members in a structure
    - Redundant paths = backup supports that redistribute load

    Analysis Types:
    1. Single-node sensitivity: Impact of individual node failure
    2. Path failure analysis: Impact of entire path invalidation
    3. Minimal cut sets: Smallest node sets whose failure disconnects goal

    Attributes:
        graph: Graph data (nodes and edges)
        goal_node_id: ID of the root goal node
        monte_carlo_samples: Number of samples for Monte Carlo analysis
    """

    def __init__(
        self,
        graph: Dict[str, Any],
        goal_node_id: str,
        monte_carlo_samples: int = 1000,
    ):
        """
        Initialize the sensitivity analyzer.

        Args:
            graph: Graph data containing nodes and edges
            goal_node_id: ID of the root goal node
            monte_carlo_samples: Number of Monte Carlo samples for analysis
        """
        self.graph = graph
        self.goal_node_id = goal_node_id
        self.monte_carlo_samples = monte_carlo_samples
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
        Run full sensitivity analysis.

        Returns:
            Dict containing:
            - stability_score: Overall stability (0-1)
            - critical_nodes: List of critical node info
            - path_analysis: Path classification results
            - minimal_cut_sets: Minimal cut sets
            - recommendations: Stability improvement suggestions
        """
        # Find all paths from goal to leaf nodes
        leaf_nodes = self._find_leaf_nodes()
        all_paths = []
        for leaf in leaf_nodes:
            paths = self._find_all_paths(self.goal_node_id, leaf)
            all_paths.extend(paths)

        # Identify critical paths
        critical_paths = self.identify_critical_paths()

        # Identify redundant paths
        redundant_paths = self.identify_redundant_paths()

        # Compute minimal cut sets
        minimal_cut_sets = self.compute_minimal_cut_sets()

        # Compute node sensitivities
        critical_nodes = []
        for node_id in self.nodes:
            if node_id == self.goal_node_id:
                continue
            sensitivity = self.compute_single_node_sensitivity(node_id)
            if sensitivity["sensitivity_score"] > 0.5:
                critical_nodes.append({
                    "node_id": node_id,
                    **sensitivity
                })

        # Sort by sensitivity
        critical_nodes.sort(key=lambda x: x["sensitivity_score"], reverse=True)

        # Compute overall stability
        redundancy_ratio = self.compute_redundancy_ratio()
        stability_score = min(1.0, redundancy_ratio / 2.0)  # Normalize

        # Generate recommendations
        recommendations = self.get_stability_recommendations()

        return {
            "stability_score": stability_score,
            "critical_nodes": critical_nodes[:10],  # Top 10
            "path_analysis": {
                "critical_paths": critical_paths,
                "redundant_paths": redundant_paths,
                "total_paths": len(all_paths),
            },
            "minimal_cut_sets": [list(s) for s in minimal_cut_sets[:5]],
            "recommendations": recommendations,
        }

    def _find_leaf_nodes(self) -> List[str]:
        """Find all leaf nodes (nodes with no children)."""
        return [
            node_id for node_id in self.nodes
            if not self.children[node_id]
        ]

    def _find_all_paths(
        self,
        from_node: str,
        to_node: str,
        visited: Optional[Set[str]] = None,
    ) -> List[List[str]]:
        """Find all paths between two nodes using DFS."""
        if visited is None:
            visited = set()

        if from_node == to_node:
            return [[from_node]]

        if from_node in visited:
            return []

        visited.add(from_node)
        paths = []

        for child in self.children[from_node]:
            child_paths = self._find_all_paths(child, to_node, visited.copy())
            for path in child_paths:
                paths.append([from_node] + path)

        return paths

    def compute_single_node_sensitivity(
        self,
        node_id: str,
    ) -> Dict[str, Any]:
        """
        Compute sensitivity score for a single node.

        Uses Monte Carlo perturbation:
        1. Sample confidence perturbations for the node
        2. Propagate through graph to compute utility impact
        3. Compute sensitivity as variance of utility

        Args:
            node_id: ID of the node to analyze

        Returns:
            Dict containing:
            - sensitivity_score: Sensitivity (0-1, higher = more critical)
            - collapse_threshold: Confidence below which utility collapses
            - utility_gradient: Rate of utility change per confidence change
        """
        node = self.nodes.get(node_id)
        if not node:
            return {
                "sensitivity_score": 0.0,
                "collapse_threshold": 0.0,
                "utility_gradient": 0.0,
            }

        base_confidence = node.get("metadata", {}).get("confidence", 0.8)
        base_utility = self._compute_graph_utility()

        # Monte Carlo sampling
        utilities = []
        collapse_threshold = 0.0

        for _ in range(self.monte_carlo_samples):
            # Perturb confidence
            perturbation = random.gauss(0, 0.2)
            new_confidence = max(0, min(1, base_confidence + perturbation))

            # Temporarily update node confidence
            old_conf = node.get("metadata", {}).get("confidence", 0.8)
            if "metadata" not in node:
                node["metadata"] = {}
            node["metadata"]["confidence"] = new_confidence

            # Compute utility with perturbation
            utility = self._compute_graph_utility()
            utilities.append(utility)

            # Check for collapse
            if utility < 0.1 * base_utility and new_confidence > collapse_threshold:
                collapse_threshold = new_confidence

            # Restore
            node["metadata"]["confidence"] = old_conf

        # Compute sensitivity metrics
        if utilities:
            mean_utility = sum(utilities) / len(utilities)
            variance = sum((u - mean_utility) ** 2 for u in utilities) / len(utilities)
            sensitivity_score = min(1.0, math.sqrt(variance) / max(0.01, base_utility))

            # Estimate gradient
            utility_gradient = (base_utility - min(utilities)) / 0.2 if utilities else 0
        else:
            sensitivity_score = 0.0
            utility_gradient = 0.0

        return {
            "sensitivity_score": sensitivity_score,
            "collapse_threshold": collapse_threshold,
            "utility_gradient": utility_gradient,
        }

    def _compute_graph_utility(self) -> float:
        """Compute overall graph utility based on node confidences."""
        if not self.nodes:
            return 0.0

        # Simple utility: product of confidences along paths
        leaf_nodes = self._find_leaf_nodes()
        if not leaf_nodes:
            return 1.0

        total_utility = 0.0
        path_count = 0

        for leaf in leaf_nodes:
            paths = self._find_all_paths(self.goal_node_id, leaf)
            for path in paths:
                path_utility = 1.0
                for node_id in path:
                    node = self.nodes.get(node_id, {})
                    confidence = node.get("metadata", {}).get("confidence", 0.8)
                    path_utility *= confidence
                total_utility += path_utility
                path_count += 1

        return total_utility / max(1, path_count)

    def identify_critical_paths(self) -> List[Dict[str, Any]]:
        """
        Identify statically determinate (critical) paths.

        A path is critical if:
        - It's the only path from goal to a supporting fact
        - Every node on the path is essential (no redundancy)

        Returns:
            List[Dict]: List of critical paths with:
            - path_id: Unique path identifier
            - node_ids: Ordered list of node IDs
            - criticality_score: How critical this path is
            - weakest_node: Node with lowest confidence on path
        """
        leaf_nodes = self._find_leaf_nodes()
        critical_paths = []

        for i, leaf in enumerate(leaf_nodes):
            paths = self._find_all_paths(self.goal_node_id, leaf)

            # If only one path to this leaf, it's critical
            if len(paths) == 1:
                path = paths[0]

                # Find weakest node
                weakest_node = None
                min_confidence = 1.0
                for node_id in path:
                    node = self.nodes.get(node_id, {})
                    confidence = node.get("metadata", {}).get("confidence", 0.8)
                    if confidence < min_confidence:
                        min_confidence = confidence
                        weakest_node = node_id

                critical_paths.append({
                    "path_id": f"critical_{i}",
                    "node_ids": path,
                    "criticality_score": 1.0,
                    "weakest_node": weakest_node,
                    "weakest_confidence": min_confidence,
                })

        return critical_paths

    def identify_redundant_paths(self) -> List[Dict[str, Any]]:
        """
        Identify statically indeterminate (redundant) paths.

        A path is redundant if:
        - Alternative paths exist to the same conclusion
        - Single node failure can be compensated

        Returns:
            List[Dict]: List of redundant paths with:
            - path_id: Unique path identifier
            - node_ids: Ordered list of node IDs
            - redundancy_ratio: Number of alternative paths
            - backup_paths: IDs of alternative paths
        """
        leaf_nodes = self._find_leaf_nodes()
        redundant_paths = []

        for i, leaf in enumerate(leaf_nodes):
            paths = self._find_all_paths(self.goal_node_id, leaf)

            # If multiple paths to this leaf, they're redundant
            if len(paths) > 1:
                for j, path in enumerate(paths):
                    backup_ids = [f"path_{i}_{k}" for k in range(len(paths)) if k != j]
                    redundant_paths.append({
                        "path_id": f"path_{i}_{j}",
                        "node_ids": path,
                        "redundancy_ratio": len(paths) - 1,
                        "backup_paths": backup_ids,
                    })

        return redundant_paths

    def compute_minimal_cut_sets(self) -> List[Set[str]]:
        """
        Compute minimal cut sets for the graph.

        A minimal cut set is the smallest set of nodes whose
        failure disconnects the goal from all supporting evidence.

        Uses graph algorithms (min-cut) adapted for reasoning graphs.

        Returns:
            List[Set[str]]: List of minimal cut sets (node ID sets)
        """
        leaf_nodes = self._find_leaf_nodes()
        if not leaf_nodes:
            return []

        # Find nodes that appear in all paths to any leaf
        cut_sets = []

        for leaf in leaf_nodes:
            paths = self._find_all_paths(self.goal_node_id, leaf)
            if not paths:
                continue

            # Find nodes common to all paths (excluding goal and leaf)
            if paths:
                common_nodes = set(paths[0][1:-1]) if len(paths[0]) > 2 else set()
                for path in paths[1:]:
                    path_nodes = set(path[1:-1]) if len(path) > 2 else set()
                    common_nodes &= path_nodes

                if common_nodes:
                    # Each common node is a single-node cut set for this leaf
                    for node in common_nodes:
                        cut_sets.append({node})

        # Find minimal cut sets (remove supersets)
        minimal_sets = []
        for cut_set in cut_sets:
            is_minimal = True
            for other in cut_sets:
                if other != cut_set and other < cut_set:
                    is_minimal = False
                    break
            if is_minimal and cut_set not in minimal_sets:
                minimal_sets.append(cut_set)

        return minimal_sets

    def compute_redundancy_ratio(self) -> float:
        """
        Compute overall redundancy ratio for the graph.

        Redundancy ratio = |alternative paths| / |critical paths|

        Higher ratio indicates more robust reasoning structure.

        Returns:
            float: Redundancy ratio
        """
        critical = self.identify_critical_paths()
        redundant = self.identify_redundant_paths()

        n_critical = len(critical)
        n_redundant = len(redundant)

        if n_critical == 0:
            return float('inf') if n_redundant > 0 else 1.0

        return n_redundant / n_critical

    def simulate_node_failure(
        self,
        node_id: str,
    ) -> Dict[str, Any]:
        """
        Simulate the impact of a node failure.

        Args:
            node_id: ID of the node to simulate failure for

        Returns:
            Dict containing:
            - utility_before: Utility before failure
            - utility_after: Utility after failure
            - utility_drop: Percentage drop
            - affected_nodes: Nodes affected by the failure
            - is_catastrophic: Whether failure causes total collapse
        """
        utility_before = self._compute_graph_utility()

        # Temporarily remove node
        node = self.nodes.pop(node_id, None)
        if not node:
            return {
                "utility_before": utility_before,
                "utility_after": utility_before,
                "utility_drop": 0.0,
                "affected_nodes": [],
                "is_catastrophic": False,
            }

        # Find affected nodes (descendants)
        affected_nodes = self._find_descendants(node_id)

        # Compute utility after failure
        utility_after = self._compute_graph_utility()

        # Restore node
        self.nodes[node_id] = node

        utility_drop = (utility_before - utility_after) / max(0.01, utility_before)
        is_catastrophic = utility_after < 0.1 * utility_before

        return {
            "utility_before": utility_before,
            "utility_after": utility_after,
            "utility_drop": utility_drop,
            "affected_nodes": list(affected_nodes),
            "is_catastrophic": is_catastrophic,
        }

    def _find_descendants(self, node_id: str) -> Set[str]:
        """Find all descendants of a node."""
        descendants = set()
        queue = list(self.children[node_id])

        while queue:
            current = queue.pop(0)
            if current not in descendants:
                descendants.add(current)
                queue.extend(self.children[current])

        return descendants

    def get_stability_recommendations(self) -> List[Dict[str, Any]]:
        """
        Generate recommendations for improving stability.

        Recommendations may include:
        - Add supporting evidence for critical nodes
        - Create alternative reasoning paths
        - Strengthen weak links in critical paths

        Returns:
            List[Dict]: List of recommendations with:
            - type: Recommendation type
            - target_node: Node to address
            - description: Human-readable description
            - priority: Priority level (high/medium/low)
        """
        recommendations = []

        # Check critical paths
        critical_paths = self.identify_critical_paths()
        for path_info in critical_paths:
            weakest = path_info.get("weakest_node")
            if weakest:
                recommendations.append({
                    "type": "strengthen_node",
                    "target_node": weakest,
                    "description": f"Add supporting evidence for node {weakest} (confidence: {path_info.get('weakest_confidence', 0):.2f})",
                    "priority": "high",
                })

        # Check for single points of failure
        cut_sets = self.compute_minimal_cut_sets()
        for cut_set in cut_sets:
            if len(cut_set) == 1:
                node_id = list(cut_set)[0]
                recommendations.append({
                    "type": "add_redundancy",
                    "target_node": node_id,
                    "description": f"Create alternative path bypassing node {node_id}",
                    "priority": "high",
                })

        # Check redundancy ratio
        ratio = self.compute_redundancy_ratio()
        if ratio < 1.0:
            recommendations.append({
                "type": "increase_redundancy",
                "target_node": None,
                "description": "Overall redundancy is low. Consider adding alternative reasoning paths.",
                "priority": "medium",
            })

        return recommendations

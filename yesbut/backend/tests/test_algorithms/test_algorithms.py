"""
Unit tests for algorithms module.
"""

import pytest
import asyncio
from typing import Dict, Any, List

# Import algorithms
import sys
sys.path.insert(0, '..')

from algorithms.pareto import ParetoOptimizer
from algorithms.oscillation import SemanticEntropyCalculator, OscillationDetector
from algorithms.sensitivity import SensitivityAnalyzer
from algorithms.path_analysis import PathAnalyzer


class TestParetoOptimizer:
    """Tests for ParetoOptimizer class."""

    def test_dominates_basic(self):
        """Test basic dominance checking."""
        optimizer = ParetoOptimizer(objectives=["utility", "confidence"])

        sol_a = {"utility": 0.8, "confidence": 0.9}
        sol_b = {"utility": 0.6, "confidence": 0.7}

        assert optimizer.dominates(sol_a, sol_b) is True
        assert optimizer.dominates(sol_b, sol_a) is False

    def test_dominates_equal(self):
        """Test dominance with equal values."""
        optimizer = ParetoOptimizer(objectives=["utility", "confidence"])

        sol_a = {"utility": 0.8, "confidence": 0.8}
        sol_b = {"utility": 0.8, "confidence": 0.8}

        assert optimizer.dominates(sol_a, sol_b) is False
        assert optimizer.dominates(sol_b, sol_a) is False

    def test_dominates_partial(self):
        """Test partial dominance (no dominance)."""
        optimizer = ParetoOptimizer(objectives=["utility", "confidence"])

        sol_a = {"utility": 0.9, "confidence": 0.5}
        sol_b = {"utility": 0.5, "confidence": 0.9}

        assert optimizer.dominates(sol_a, sol_b) is False
        assert optimizer.dominates(sol_b, sol_a) is False

    def test_compute_pareto_front(self):
        """Test Pareto front computation."""
        optimizer = ParetoOptimizer(objectives=["utility", "confidence"])

        solutions = [
            {"id": "1", "utility": 0.9, "confidence": 0.9},
            {"id": "2", "utility": 0.8, "confidence": 0.7},
            {"id": "3", "utility": 0.5, "confidence": 0.95},
            {"id": "4", "utility": 0.3, "confidence": 0.3},
        ]

        front = optimizer.compute_pareto_front(solutions)

        # Solutions 1 and 3 should be on the front
        front_ids = {s["id"] for s in front}
        assert "1" in front_ids
        assert "3" in front_ids
        assert "4" not in front_ids

    def test_compute_pareto_front_empty(self):
        """Test Pareto front with empty input."""
        optimizer = ParetoOptimizer(objectives=["utility", "confidence"])
        front = optimizer.compute_pareto_front([])
        assert front == []

    def test_filter_solutions(self):
        """Test solution filtering with max limit."""
        optimizer = ParetoOptimizer(objectives=["utility", "confidence"])

        solutions = [
            {"id": str(i), "utility": i * 0.1, "confidence": (10 - i) * 0.1}
            for i in range(10)
        ]

        filtered = optimizer.filter_solutions(solutions, max_solutions=5)
        assert len(filtered) <= 5

    def test_rank_solutions(self):
        """Test solution ranking by Pareto layers."""
        optimizer = ParetoOptimizer(objectives=["utility", "confidence"])

        solutions = [
            {"id": "1", "utility": 0.9, "confidence": 0.9},
            {"id": "2", "utility": 0.5, "confidence": 0.5},
            {"id": "3", "utility": 0.3, "confidence": 0.3},
        ]

        ranked = optimizer.rank_solutions(solutions)

        # First solution should be rank 0
        rank_0 = [s for s, r in ranked if r == 0]
        assert any(s["id"] == "1" for s in rank_0)


class TestSemanticEntropyCalculator:
    """Tests for SemanticEntropyCalculator class."""

    @pytest.mark.asyncio
    async def test_compute_entropy_single_response(self):
        """Test entropy with single response."""
        calculator = SemanticEntropyCalculator()
        entropy = await calculator.compute_entropy(["Single response"])
        assert entropy == 0.0

    @pytest.mark.asyncio
    async def test_compute_entropy_identical_responses(self):
        """Test entropy with identical responses."""
        calculator = SemanticEntropyCalculator()
        responses = ["Same response", "Same response", "Same response"]
        entropy = await calculator.compute_entropy(responses)
        assert entropy == 0.0

    @pytest.mark.asyncio
    async def test_compute_entropy_diverse_responses(self):
        """Test entropy with diverse responses."""
        calculator = SemanticEntropyCalculator()
        responses = [
            "The answer is A because of X",
            "The answer is B because of Y",
            "The answer is C because of Z",
        ]
        entropy = await calculator.compute_entropy(responses)
        assert entropy > 0

    def test_compute_cluster_entropy(self):
        """Test cluster entropy computation."""
        calculator = SemanticEntropyCalculator()

        # Single cluster - zero entropy
        clusters = [[0, 1, 2]]
        entropy = calculator.compute_cluster_entropy(clusters, 3)
        assert entropy == 0.0

        # Multiple equal clusters - maximum entropy
        clusters = [[0], [1], [2]]
        entropy = calculator.compute_cluster_entropy(clusters, 3)
        assert entropy > 0


class TestOscillationDetector:
    """Tests for OscillationDetector class."""

    def test_record_round(self):
        """Test recording debate rounds."""
        detector = OscillationDetector()
        detector.record_round({"branch_1": "Position A"}, 0.5)
        detector.record_round({"branch_1": "Position B"}, 0.4)

        assert len(detector.position_history) == 2
        assert len(detector.entropy_history) == 2

    @pytest.mark.asyncio
    async def test_check_oscillation_insufficient_rounds(self):
        """Test oscillation check with insufficient rounds."""
        detector = OscillationDetector()
        detector.record_round({"branch_1": "Position A"}, 0.5)

        result = await detector.check_oscillation()
        assert result["is_oscillating"] is False
        assert result["details"]["reason"] == "insufficient_rounds"

    def test_check_entropy_stagnation(self):
        """Test entropy stagnation detection."""
        detector = OscillationDetector(stagnation_rounds=3, entropy_decrease_threshold=0.1)

        # Record stagnating entropy
        detector.entropy_history = [0.5, 0.5, 0.5, 0.5]

        assert detector.check_entropy_stagnation() is True

    def test_check_entropy_not_stagnating(self):
        """Test non-stagnating entropy."""
        detector = OscillationDetector(stagnation_rounds=3, entropy_decrease_threshold=0.1)

        # Record decreasing entropy
        detector.entropy_history = [0.8, 0.6, 0.4, 0.2]

        assert detector.check_entropy_stagnation() is False

    def test_reset(self):
        """Test detector reset."""
        detector = OscillationDetector()
        detector.record_round({"branch_1": "Position A"}, 0.5)
        detector.reset()

        assert len(detector.position_history) == 0
        assert len(detector.entropy_history) == 0


class TestSensitivityAnalyzer:
    """Tests for SensitivityAnalyzer class."""

    def create_test_graph(self) -> Dict[str, Any]:
        """Create a test graph for analysis."""
        return {
            "nodes": [
                {"id": "goal", "type": "goal", "content": "Main goal", "metadata": {"confidence": 1.0}},
                {"id": "claim1", "type": "claim", "content": "Claim 1", "metadata": {"confidence": 0.8}},
                {"id": "claim2", "type": "claim", "content": "Claim 2", "metadata": {"confidence": 0.7}},
                {"id": "fact1", "type": "fact", "content": "Fact 1", "metadata": {"confidence": 0.9}},
            ],
            "edges": [
                {"source_id": "goal", "target_id": "claim1", "type": "decompose"},
                {"source_id": "goal", "target_id": "claim2", "type": "decompose"},
                {"source_id": "claim1", "target_id": "fact1", "type": "decompose"},
            ],
        }

    def test_analyze(self):
        """Test full sensitivity analysis."""
        graph = self.create_test_graph()
        analyzer = SensitivityAnalyzer(graph=graph, goal_node_id="goal", monte_carlo_samples=100)

        result = analyzer.analyze()

        assert "stability_score" in result
        assert "critical_nodes" in result
        assert "path_analysis" in result
        assert "recommendations" in result

    def test_identify_critical_paths(self):
        """Test critical path identification."""
        graph = self.create_test_graph()
        analyzer = SensitivityAnalyzer(graph=graph, goal_node_id="goal")

        critical_paths = analyzer.identify_critical_paths()

        # Should identify paths with no alternatives
        assert isinstance(critical_paths, list)

    def test_identify_redundant_paths(self):
        """Test redundant path identification."""
        graph = self.create_test_graph()
        analyzer = SensitivityAnalyzer(graph=graph, goal_node_id="goal")

        redundant_paths = analyzer.identify_redundant_paths()

        assert isinstance(redundant_paths, list)

    def test_compute_redundancy_ratio(self):
        """Test redundancy ratio computation."""
        graph = self.create_test_graph()
        analyzer = SensitivityAnalyzer(graph=graph, goal_node_id="goal")

        ratio = analyzer.compute_redundancy_ratio()

        assert isinstance(ratio, float)
        assert ratio >= 0


class TestPathAnalyzer:
    """Tests for PathAnalyzer class."""

    def create_test_graph(self) -> Dict[str, Any]:
        """Create a test graph for analysis."""
        return {
            "nodes": [
                {"id": "goal", "type": "goal", "content": "Main goal"},
                {"id": "claim1", "type": "claim", "content": "Claim 1"},
                {"id": "claim2", "type": "claim", "content": "Claim 2"},
                {"id": "fact1", "type": "fact", "content": "Fact 1"},
                {"id": "fact2", "type": "fact", "content": "Fact 2"},
            ],
            "edges": [
                {"source_id": "goal", "target_id": "claim1", "type": "decompose"},
                {"source_id": "goal", "target_id": "claim2", "type": "decompose"},
                {"source_id": "claim1", "target_id": "fact1", "type": "decompose"},
                {"source_id": "claim2", "target_id": "fact2", "type": "decompose"},
            ],
        }

    def test_analyze(self):
        """Test full path analysis."""
        graph = self.create_test_graph()
        analyzer = PathAnalyzer(graph=graph, goal_node_id="goal")

        result = analyzer.analyze()

        assert "critical_paths" in result
        assert "redundant_paths" in result
        assert "minimal_cut_sets" in result
        assert "redundancy_ratio" in result
        assert "structural_classification" in result

    def test_find_all_paths(self):
        """Test path finding."""
        graph = self.create_test_graph()
        analyzer = PathAnalyzer(graph=graph, goal_node_id="goal")

        paths = analyzer.find_all_paths("goal", "fact1")

        assert len(paths) > 0
        assert paths[0][0] == "goal"
        assert paths[0][-1] == "fact1"

    def test_compute_node_criticality(self):
        """Test node criticality computation."""
        graph = self.create_test_graph()
        analyzer = PathAnalyzer(graph=graph, goal_node_id="goal")

        criticality = analyzer.compute_node_criticality("claim1")

        assert 0 <= criticality <= 1

    def test_identify_bottlenecks(self):
        """Test bottleneck identification."""
        graph = self.create_test_graph()
        analyzer = PathAnalyzer(graph=graph, goal_node_id="goal")

        bottlenecks = analyzer.identify_bottlenecks()

        assert isinstance(bottlenecks, list)

    def test_get_path_statistics(self):
        """Test path statistics."""
        graph = self.create_test_graph()
        analyzer = PathAnalyzer(graph=graph, goal_node_id="goal")

        stats = analyzer.get_path_statistics()

        assert "total_paths" in stats
        assert "avg_path_length" in stats
        assert "max_path_length" in stats


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""
Unit tests for agents module.
"""

import pytest
import asyncio
from typing import Dict, Any, List

import sys
sys.path.insert(0, '..')

from agents.base.agent import BaseAgent
from agents.rpa.agent import RequirementParsingAgent, BayesianPrior
from agents.gen.agent import GeneratorAgent, FeatureSpace, MAPElitesArchive
from agents.isa.agent import InformationScoutAgent
from agents.aca.agent import AuditComplianceAgent
from agents.bm.agent import BranchManagerAgent
from agents.ga.agent import GameArbiterAgent
from agents.uoa.agent import UtilityOptimizationAgent
from agents.rec.agent import ReverseEngineeringCompilerAgent


class TestBayesianPrior:
    """Tests for BayesianPrior class."""

    def test_initialization(self):
        """Test prior initialization."""
        dimensions = ["risk", "value", "time"]
        prior = BayesianPrior(dimensions)

        assert len(prior.dimensions) == 3
        for dim in dimensions:
            assert prior.get_mean(dim) == 0.5
            assert prior.get_variance(dim) == 0.25

    def test_update(self):
        """Test posterior update."""
        prior = BayesianPrior(["risk"])

        prior.update("risk", 0.8)

        assert prior.get_mean("risk") != 0.5
        assert prior.get_variance("risk") < 0.25

    def test_convergence(self):
        """Test convergence detection."""
        prior = BayesianPrior(["risk"])

        # Initially not converged
        assert prior.is_converged(threshold=0.05) is False

        # Update many times to converge
        for _ in range(20):
            prior.update("risk", 0.7)

        assert prior.get_variance("risk") < 0.05


class TestFeatureSpace:
    """Tests for FeatureSpace class."""

    def test_get_cell_index(self):
        """Test cell index computation."""
        space = FeatureSpace()

        features = {
            "risk_level": 0.5,
            "innovation_degree": 0.5,
            "implementation_time": 0.5,
            "resource_requirement": 0.5,
        }

        index = space.get_cell_index(features)

        assert isinstance(index, tuple)
        assert len(index) == 4

    def test_get_total_cells(self):
        """Test total cells computation."""
        space = FeatureSpace()
        total = space.get_total_cells()

        # Default: 5 bins per dimension, 4 dimensions = 5^4 = 625
        assert total == 625


class TestMAPElitesArchive:
    """Tests for MAPElitesArchive class."""

    def test_update_new_cell(self):
        """Test adding to empty cell."""
        space = FeatureSpace()
        archive = MAPElitesArchive(space)

        solution = {"id": "1", "content": "Test"}
        features = {"risk_level": 0.5, "innovation_degree": 0.5, "implementation_time": 0.5, "resource_requirement": 0.5}

        result = archive.update(solution, features, quality=0.8)

        assert result is True
        assert archive.get_coverage() > 0

    def test_update_better_solution(self):
        """Test replacing with better solution."""
        space = FeatureSpace()
        archive = MAPElitesArchive(space)

        features = {"risk_level": 0.5, "innovation_degree": 0.5, "implementation_time": 0.5, "resource_requirement": 0.5}

        archive.update({"id": "1"}, features, quality=0.5)
        result = archive.update({"id": "2"}, features, quality=0.8)

        assert result is True

    def test_update_worse_solution(self):
        """Test not replacing with worse solution."""
        space = FeatureSpace()
        archive = MAPElitesArchive(space)

        features = {"risk_level": 0.5, "innovation_degree": 0.5, "implementation_time": 0.5, "resource_requirement": 0.5}

        archive.update({"id": "1"}, features, quality=0.8)
        result = archive.update({"id": "2"}, features, quality=0.5)

        assert result is False


class TestRequirementParsingAgent:
    """Tests for RequirementParsingAgent class."""

    @pytest.fixture
    def agent(self):
        """Create an RPA instance."""
        return RequirementParsingAgent(agent_id="test_rpa")

    def test_simple_parse(self, agent):
        """Test simple requirement parsing."""
        result = agent._simple_parse("Build a web application for task management")

        assert "main_goal" in result
        assert result["main_goal"] == "Build a web application for task management"

    @pytest.mark.asyncio
    async def test_create_goal_node(self, agent):
        """Test goal node creation."""
        parsed = {"main_goal": "Test goal", "domain_context": "testing"}
        node = await agent.create_goal_node(parsed)

        assert node["type"] == "goal"
        assert node["content"] == "Test goal"
        assert node["confidence"] == 1.0

    def test_generate_utility_function(self, agent):
        """Test utility function generation."""
        code = agent.generate_utility_function()

        assert "def utility_function" in code
        assert "return" in code


class TestGeneratorAgent:
    """Tests for GeneratorAgent class."""

    @pytest.fixture
    def agent(self):
        """Create a GEN instance."""
        return GeneratorAgent(agent_id="test_gen")

    def test_generate_mock_solution(self, agent):
        """Test mock solution generation."""
        solution = agent._generate_mock_solution("high_temperature")

        assert "id" in solution
        assert "content" in solution
        assert "strategy" in solution
        assert solution["strategy"] == "high_temperature"

    def test_compute_features(self, agent):
        """Test feature computation."""
        solution = {"content": "Test solution", "strategy": "high_temperature"}
        features = agent.compute_features(solution)

        assert "risk_level" in features
        assert "innovation_degree" in features
        assert 0 <= features["risk_level"] <= 1
        assert 0 <= features["innovation_degree"] <= 1

    def test_evaluate_quality(self, agent):
        """Test quality evaluation."""
        solution = {
            "content": "Test",
            "key_steps": ["Step 1", "Step 2"],
            "benefits": ["Benefit 1"],
            "risks": ["Risk 1"],
            "approach": "test",
        }
        quality = agent.evaluate_quality(solution)

        assert 0 <= quality <= 1


class TestAuditComplianceAgent:
    """Tests for AuditComplianceAgent class."""

    @pytest.fixture
    def agent(self):
        """Create an ACA instance."""
        return AuditComplianceAgent(agent_id="test_aca")

    def test_violates_constraint_must(self, agent):
        """Test constraint violation detection for 'must' constraints."""
        claim = "We will use Python for development"
        constraint = "Must use Python programming language"

        result = agent._violates_constraint(claim, constraint)
        assert result is False

    def test_violates_constraint_must_not(self, agent):
        """Test constraint violation detection for 'must not' constraints."""
        claim = "We will use external APIs"
        constraint = "Must not use external APIs"

        result = agent._violates_constraint(claim, constraint)
        assert result is True

    @pytest.mark.asyncio
    async def test_detect_circular_dependencies(self, agent):
        """Test circular dependency detection."""
        edges = [
            {"source_id": "A", "target_id": "B"},
            {"source_id": "B", "target_id": "C"},
            {"source_id": "C", "target_id": "A"},  # Creates cycle
        ]

        cycles = await agent.detect_circular_dependencies(edges)

        assert len(cycles) > 0


class TestBranchManagerAgent:
    """Tests for BranchManagerAgent class."""

    @pytest.fixture
    def agent(self):
        """Create a BM instance."""
        return BranchManagerAgent(agent_id="test_bm", branch_id="branch_1")

    def test_default_utility(self, agent):
        """Test default utility function."""
        solution = {"confidence": 0.8, "utility": 0.6}
        utility = agent._default_utility(solution)

        assert utility == 0.8 * 0.6

    @pytest.mark.asyncio
    async def test_socratic_question(self, agent):
        """Test Socratic question generation."""
        claim = {"id": "claim_1", "content": "The solution is optimal"}
        question = await agent.socratic_question(claim)

        assert "question" in question
        assert "question_type" in question
        assert question["target_claim_id"] == "claim_1"

    def test_select_response_strategy(self, agent):
        """Test response strategy selection."""
        agent.current_position = {"utility_score": 0.8}

        # Strong attack, high confidence -> defend
        attack = {"confidence": 0.6}
        strategy = agent._select_response_strategy(attack)
        assert strategy == "defend"

        # Very strong attack, low confidence -> concede
        agent.current_position = {"utility_score": 0.3}
        attack = {"confidence": 0.9}
        strategy = agent._select_response_strategy(attack)
        assert strategy == "concede"


class TestGameArbiterAgent:
    """Tests for GameArbiterAgent class."""

    @pytest.fixture
    def agent(self):
        """Create a GA instance."""
        return GameArbiterAgent(agent_id="test_ga")

    @pytest.mark.asyncio
    async def test_compute_pareto_front(self, agent):
        """Test Pareto front computation."""
        branches = [
            {"id": "1", "utility_score": 0.9, "confidence": 0.9, "risk": 0.1},
            {"id": "2", "utility_score": 0.5, "confidence": 0.5, "risk": 0.5},
            {"id": "3", "utility_score": 0.3, "confidence": 0.3, "risk": 0.7},
        ]

        front = await agent.compute_pareto_front(branches)

        assert len(front) >= 1
        assert any(b["id"] == "1" for b in front)

    @pytest.mark.asyncio
    async def test_compute_resource_allocation(self, agent):
        """Test resource allocation."""
        branches = [
            {"id": "1", "utility_score": 0.8},
            {"id": "2", "utility_score": 0.6},
        ]
        pareto_front = [branches[0]]

        allocation = await agent.compute_resource_allocation(branches, pareto_front)

        assert "1" in allocation
        assert "2" in allocation
        assert sum(allocation.values()) <= agent.resource_budget


class TestUtilityOptimizationAgent:
    """Tests for UtilityOptimizationAgent class."""

    @pytest.fixture
    def agent(self):
        """Create a UOA instance."""
        return UtilityOptimizationAgent(agent_id="test_uoa")

    def test_generate_utility_function(self, agent):
        """Test utility function generation."""
        preferences = {"weights": {"risk": 0.3, "value": 0.7}}
        utility_fn = agent.generate_utility_function(preferences)

        node = {"risk": 0.5, "value": 0.8, "confidence": 0.9}
        result = utility_fn(node)

        assert 0 <= result <= 1

    def test_update_posterior(self, agent):
        """Test posterior update."""
        query = {"dimension": "risk"}
        response = {"value": 0.7}

        posterior = agent.update_posterior("risk", query, response)

        assert "mean" in posterior
        assert "variance" in posterior
        assert posterior["observations"] == 1


class TestReverseEngineeringCompilerAgent:
    """Tests for ReverseEngineeringCompilerAgent class."""

    @pytest.fixture
    def agent(self):
        """Create a REC instance."""
        return ReverseEngineeringCompilerAgent(agent_id="test_rec")

    @pytest.mark.asyncio
    async def test_extract_winning_path(self, agent):
        """Test winning path extraction."""
        graph_state = {
            "nodes": {
                "goal": {"id": "goal", "type": "goal", "content": "Main goal", "utility": 1.0, "confidence": 1.0},
                "claim1": {"id": "claim1", "type": "claim", "content": "Claim 1", "utility": 0.8, "confidence": 0.9},
            },
            "edges": {},
        }

        path = await agent.extract_winning_path(graph_state)

        assert len(path) > 0
        assert path[0]["type"] == "goal"

    @pytest.mark.asyncio
    async def test_compile_markdown(self, agent):
        """Test markdown compilation."""
        path = [
            {"type": "goal", "content": "Main goal"},
            {"type": "claim", "content": "Supporting claim"},
        ]
        evidence = [{"content": "Evidence 1", "confidence": 0.9}]
        trace = {"steps": [{"step": 1, "type": "goal", "content": "Main goal", "confidence": 1.0}]}

        output = await agent.compile_markdown(path, evidence, trace, {})

        assert "# Action Plan" in output
        assert "Main goal" in output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

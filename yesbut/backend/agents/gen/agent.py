"""
Generator Agent (GEN)

Generates diverse solutions during the divergence phase using
Quality-Diversity (QD) algorithms inspired by MAP-Elites.
"""

from typing import Dict, Any, AsyncGenerator, List, Optional, Tuple
from datetime import datetime
import uuid
import random

from ..base.agent import BaseAgent
from ..streaming import StreamEventType


class FeatureSpace:
    """Feature space definition for QD optimization."""

    DEFAULT_DIMENSIONS = {
        "risk_level": {"min": 0.0, "max": 1.0, "bins": 5},
        "innovation_degree": {"min": 0.0, "max": 1.0, "bins": 5},
        "implementation_time": {"min": 0.0, "max": 1.0, "bins": 5},
        "resource_requirement": {"min": 0.0, "max": 1.0, "bins": 5},
    }

    def __init__(self, dimensions: Optional[Dict[str, Dict[str, Any]]] = None):
        self.dimensions = dimensions or self.DEFAULT_DIMENSIONS

    def get_cell_index(self, features: Dict[str, float]) -> Tuple[int, ...]:
        """Convert feature vector to cell index."""
        indices = []
        for dim_name, dim_config in self.dimensions.items():
            value = features.get(dim_name, 0.5)
            bins = dim_config.get("bins", 5)
            min_val = dim_config.get("min", 0.0)
            max_val = dim_config.get("max", 1.0)
            normalized = (value - min_val) / (max_val - min_val) if max_val > min_val else 0.5
            index = min(int(normalized * bins), bins - 1)
            indices.append(index)
        return tuple(indices)

    def get_total_cells(self) -> int:
        """Get total number of cells in feature space."""
        total = 1
        for dim_config in self.dimensions.values():
            total *= dim_config.get("bins", 5)
        return total


class MAPElitesArchive:
    """MAP-Elites style archive for storing best solutions per cell."""

    def __init__(self, feature_space: FeatureSpace):
        self.feature_space = feature_space
        self.archive: Dict[Tuple[int, ...], Dict[str, Any]] = {}

    def update(self, solution: Dict[str, Any], features: Dict[str, float], quality: float) -> bool:
        """Update archive with new solution if better than existing."""
        cell_index = self.feature_space.get_cell_index(features)
        existing = self.archive.get(cell_index)
        if existing is None or quality > existing.get("quality", 0):
            self.archive[cell_index] = {"solution": solution, "features": features, "quality": quality}
            return True
        return False

    def get_coverage(self) -> float:
        """Get coverage ratio of archive."""
        total = self.feature_space.get_total_cells()
        return len(self.archive) / total if total > 0 else 0.0

    def get_all_solutions(self) -> List[Dict[str, Any]]:
        """Get all solutions in archive."""
        return [entry["solution"] for entry in self.archive.values()]

    def get_empty_cells(self) -> List[Tuple[int, ...]]:
        """Get indices of empty cells."""
        total_cells = self.feature_space.get_total_cells()
        dims = list(self.feature_space.dimensions.values())
        all_indices = []

        def generate_indices(current: List[int], dim_idx: int):
            if dim_idx >= len(dims):
                all_indices.append(tuple(current))
                return
            bins = dims[dim_idx].get("bins", 5)
            for i in range(bins):
                generate_indices(current + [i], dim_idx + 1)

        generate_indices([], 0)
        return [idx for idx in all_indices if idx not in self.archive]


class GeneratorAgent(BaseAgent):
    """Generator Agent for diverse solution generation using QD algorithms."""

    STRATEGIES = ["high_temperature", "cross_domain_analogy", "constraint_relaxation", "reverse_thinking", "combination"]

    def __init__(self, agent_id: str, llm_client=None, streaming_callback=None,
                 feature_space: Optional[FeatureSpace] = None, target_coverage: float = 0.6):
        super().__init__(agent_id=agent_id, agent_type="GEN", agent_name="Generator Agent",
                         llm_client=llm_client, streaming_callback=streaming_callback)
        self.feature_space = feature_space or FeatureSpace()
        self.archive = MAPElitesArchive(self.feature_space)
        self.target_coverage = target_coverage
        self.goal: Optional[Dict[str, Any]] = None
        self.constraints: List[Dict[str, Any]] = []
        self._register_prompts()

    def _register_prompts(self) -> None:
        self.register_prompt("generate_solution", """Generate a solution for the goal: {goal}
Constraints: {constraints}
Strategy: {strategy}
Generate a creative and feasible solution. Respond in JSON with: content, approach, key_steps, risks, benefits""")

        self.register_prompt("evaluate_features", """Evaluate the following solution on these dimensions (0-1 scale):
Solution: {solution}
Dimensions: risk_level, innovation_degree, implementation_time, resource_requirement
Respond in JSON with scores for each dimension.""")

    async def run(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> AsyncGenerator[Dict[str, Any], None]:
        self.goal = input_data.get("goal", {})
        self.constraints = input_data.get("constraints", [])
        target_count = input_data.get("target_count", 100)

        await self.think("Starting divergence phase generation...")
        yield {"type": StreamEventType.AGENT_STARTED.value, "data": {"target_count": target_count}}

        generated_count = 0
        round_num = 0
        max_rounds = target_count // 5 + 10

        while generated_count < target_count and round_num < max_rounds:
            strategy = self._select_strategy()
            batch = await self.generate_batch(strategy, batch_size=5)

            for solution in batch:
                features = self.compute_features(solution)
                quality = self.evaluate_quality(solution)

                if self.update_archive(solution, features, quality):
                    node = self._create_solution_node(solution, features, quality)
                    yield {"type": StreamEventType.NODE_PREVIEW.value, "data": {"node": node}}
                    generated_count += 1

            progress = min(1.0, generated_count / target_count)
            yield {"type": StreamEventType.PROGRESS_UPDATED.value, "data": {"progress": progress, "phase": "divergence", "generated": generated_count}}

            if self.archive.get_coverage() >= self.target_coverage:
                break
            round_num += 1

        yield {"type": StreamEventType.AGENT_COMPLETED.value, "data": {"total_generated": generated_count, "coverage": self.archive.get_coverage()}}

    def _select_strategy(self) -> str:
        """Select generation strategy based on archive state."""
        coverage = self.archive.get_coverage()
        if coverage < 0.2:
            return random.choice(["high_temperature", "cross_domain_analogy"])
        elif coverage < 0.5:
            return random.choice(["constraint_relaxation", "reverse_thinking"])
        else:
            return random.choice(["combination", "high_temperature"])

    async def generate_batch(self, strategy: str, batch_size: int = 10) -> List[Dict[str, Any]]:
        """Generate a batch of solutions using specified strategy."""
        solutions = []
        goal_content = self.goal.get("content", "") if self.goal else ""
        constraints_text = ", ".join([c.get("content", "") for c in self.constraints])

        for _ in range(batch_size):
            if self.llm_client is None:
                solution = self._generate_mock_solution(strategy)
            else:
                prompt = self.get_prompt("generate_solution", goal=goal_content, constraints=constraints_text, strategy=strategy)
                response_text = ""
                async for chunk in self.invoke_llm(messages=[{"role": "user", "content": prompt}], stream=True):
                    response_text += chunk
                solution = self._parse_solution_response(response_text, strategy)
            solutions.append(solution)
        return solutions

    def _generate_mock_solution(self, strategy: str) -> Dict[str, Any]:
        """Generate mock solution for testing without LLM."""
        return {
            "id": str(uuid.uuid4()),
            "content": f"Solution generated using {strategy} strategy",
            "approach": strategy,
            "key_steps": ["Step 1", "Step 2", "Step 3"],
            "risks": ["Risk 1"],
            "benefits": ["Benefit 1"],
            "strategy": strategy,
        }

    def _parse_solution_response(self, response: str, strategy: str) -> Dict[str, Any]:
        """Parse LLM response into solution dict."""
        try:
            import json
            start, end = response.find("{"), response.rfind("}") + 1
            if start >= 0 and end > start:
                data = json.loads(response[start:end])
                data["id"] = str(uuid.uuid4())
                data["strategy"] = strategy
                return data
        except json.JSONDecodeError:
            pass
        return self._generate_mock_solution(strategy)

    def compute_features(self, solution: Dict[str, Any]) -> Dict[str, float]:
        """Compute feature vector for a solution."""
        strategy = solution.get("strategy", "")
        content = solution.get("content", "")

        risk_level = 0.5
        if "risky" in content.lower() or strategy == "high_temperature":
            risk_level = 0.7 + random.uniform(0, 0.3)
        elif "safe" in content.lower() or strategy == "constraint_relaxation":
            risk_level = 0.2 + random.uniform(0, 0.3)

        innovation_degree = 0.5
        if strategy in ["cross_domain_analogy", "reverse_thinking"]:
            innovation_degree = 0.6 + random.uniform(0, 0.4)
        elif strategy == "combination":
            innovation_degree = 0.3 + random.uniform(0, 0.4)

        implementation_time = random.uniform(0.2, 0.8)
        resource_requirement = random.uniform(0.2, 0.8)

        return {
            "risk_level": min(1.0, max(0.0, risk_level)),
            "innovation_degree": min(1.0, max(0.0, innovation_degree)),
            "implementation_time": implementation_time,
            "resource_requirement": resource_requirement,
        }

    def evaluate_quality(self, solution: Dict[str, Any]) -> float:
        """Evaluate quality score for a solution."""
        score = 0.5
        if solution.get("key_steps"):
            score += 0.1 * min(len(solution["key_steps"]), 5) / 5
        if solution.get("benefits"):
            score += 0.1 * min(len(solution["benefits"]), 3) / 3
        if solution.get("risks"):
            score += 0.1
        if solution.get("approach"):
            score += 0.1
        score += random.uniform(-0.1, 0.1)
        return min(1.0, max(0.0, score))

    def update_archive(self, solution: Dict[str, Any], features: Dict[str, float], quality: float) -> bool:
        """Update MAP-Elites archive with new solution."""
        return self.archive.update(solution, features, quality)

    def _create_solution_node(self, solution: Dict[str, Any], features: Dict[str, float], quality: float) -> Dict[str, Any]:
        """Create a node from solution data."""
        return {
            "id": solution.get("id", str(uuid.uuid4())),
            "type": "claim",
            "content": solution.get("content", ""),
            "layer": 2,
            "branch_id": None,
            "parent_id": self.goal.get("id") if self.goal else None,
            "confidence": quality,
            "utility": quality,
            "sensitivity": None,
            "metadata": {
                "features": features,
                "strategy": solution.get("strategy"),
                "key_steps": solution.get("key_steps", []),
                "created_at": datetime.utcnow().isoformat(),
                "created_by": self.agent_id,
            },
        }

    def get_coverage_map(self) -> Dict[str, Any]:
        """Get current archive coverage map for visualization."""
        return {
            "total_cells": self.feature_space.get_total_cells(),
            "filled_cells": len(self.archive.archive),
            "coverage_ratio": self.archive.get_coverage(),
            "cell_data": [{"index": idx, "quality": entry["quality"], "features": entry["features"]}
                          for idx, entry in self.archive.archive.items()],
        }

    def identify_gaps(self) -> List[Dict[str, float]]:
        """Identify unexplored regions in feature space."""
        empty_cells = self.archive.get_empty_cells()
        gaps = []
        dims = list(self.feature_space.dimensions.items())
        for cell_idx in empty_cells[:10]:
            features = {}
            for i, (dim_name, dim_config) in enumerate(dims):
                bins = dim_config.get("bins", 5)
                min_val = dim_config.get("min", 0.0)
                max_val = dim_config.get("max", 1.0)
                center = (cell_idx[i] + 0.5) / bins
                features[dim_name] = min_val + center * (max_val - min_val)
            gaps.append(features)
        return gaps

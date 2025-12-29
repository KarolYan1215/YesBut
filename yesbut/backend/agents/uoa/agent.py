"""
Utility Optimization Agent (UOA)

Maintains and updates utility functions using Bayesian preference elicitation
and semantic anchoring quantification with variance reduction.
"""

from typing import Dict, Any, AsyncGenerator, List, Callable, Optional
from datetime import datetime
import uuid
import math

from ..base.agent import BaseAgent
from ..streaming import StreamEventType


class UtilityOptimizationAgent(BaseAgent):
    """
    Utility Optimization Agent for maintaining and updating utility functions.

    LIMITED Agent: Only query strategies are optimized by TextGrad.
    """

    DEFAULT_ANCHORS = {
        "risk": ["no risk", "minimal risk", "moderate risk", "significant risk", "extreme risk"],
        "value": ["no value", "low value", "moderate value", "high value", "exceptional value"],
        "time": ["immediate", "short-term", "medium-term", "long-term", "indefinite"],
        "cost": ["free", "cheap", "moderate", "expensive", "prohibitive"],
    }

    def __init__(self, agent_id: str, llm_client=None, streaming_callback=None,
                 semantic_anchors: Optional[Dict[str, List[str]]] = None):
        super().__init__(agent_id=agent_id, agent_type="UOA", agent_name="Utility Optimization Agent",
                         llm_client=llm_client, streaming_callback=streaming_callback)
        self.semantic_anchors = semantic_anchors or self.DEFAULT_ANCHORS
        self.posteriors: Dict[str, Dict[str, float]] = {}
        self.calibration_params: Dict[str, Dict[str, float]] = {}
        self.queries_asked = 0
        self._register_prompts()

    def _register_prompts(self) -> None:
        self.register_prompt("quantify", """Rate this concept on a scale of 0-1 for the dimension '{dimension}':
Concept: {concept}
Anchors: {anchors}
Respond with just a number between 0 and 1.""")

        self.register_prompt("elicit", """Generate a preference question for the dimension '{dimension}':
Current understanding: {current}
Generate a question with 3 options that will help clarify the user's preference.""")

    async def run(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> AsyncGenerator[Dict[str, Any], None]:
        branch = input_data.get("branch", {})
        nodes = branch.get("nodes", [])

        await self.think("Optimizing utility scores...")
        yield {"type": StreamEventType.AGENT_STARTED.value, "data": {"node_count": len(nodes)}}

        utility_function = self.generate_utility_function(context.get("preferences", {}))

        updated_nodes = []
        for node in nodes:
            utility = await self.compute_node_utility(node, utility_function)
            node["utility"] = utility
            updated_nodes.append(node)
            yield {"type": "node_utility_updated", "data": {"node_id": node.get("id"), "utility": utility}}

        branch_utility = await self.compute_branch_utility(branch, utility_function)
        yield {"type": "branch_utility_computed", "data": {"branch_id": branch.get("id"), "utility": branch_utility}}

        yield {"type": StreamEventType.AGENT_COMPLETED.value, "data": {"branch_utility": branch_utility}}

    async def elicit_preference(self, dimension: str, current_posterior: Dict[str, Any]) -> Dict[str, Any]:
        """Generate preference elicitation query using Bayesian optimization."""
        self.queries_asked += 1
        mean = current_posterior.get("mean", 0.5)
        variance = current_posterior.get("variance", 0.25)

        std = math.sqrt(variance)
        options = [
            {"label": "A", "value": max(0, mean - std), "description": f"Lower {dimension}"},
            {"label": "B", "value": mean, "description": f"Moderate {dimension}"},
            {"label": "C", "value": min(1, mean + std), "description": f"Higher {dimension}"},
        ]

        expected_info_gain = 0.5 * math.log(variance / (variance * 0.5)) if variance > 0 else 0

        return {
            "query_text": f"How important is {dimension} in your decision?",
            "options": options,
            "dimension": dimension,
            "expected_info_gain": expected_info_gain,
        }

    def update_posterior(self, dimension: str, query: Dict[str, Any], response: Any) -> Dict[str, Any]:
        """Update posterior distribution based on user response."""
        if dimension not in self.posteriors:
            self.posteriors[dimension] = {"mean": 0.5, "variance": 0.25, "observations": 0}

        posterior = self.posteriors[dimension]
        observation = response.get("value", 0.5) if isinstance(response, dict) else float(response)

        old_mean = posterior["mean"]
        old_var = posterior["variance"]
        n = posterior["observations"]

        prior_precision = 1.0 / old_var if old_var > 0 else 1.0
        new_precision = prior_precision + 1.0
        new_mean = (prior_precision * old_mean + observation) / new_precision
        new_var = 1.0 / new_precision

        self.posteriors[dimension] = {"mean": new_mean, "variance": new_var, "observations": n + 1}
        return self.posteriors[dimension]

    async def quantify_semantic(self, concept: str, dimension: str) -> float:
        """Convert semantic concept to scalar using anchoring."""
        anchors = self.semantic_anchors.get(dimension, ["low", "medium", "high"])

        if self.llm_client is None:
            concept_lower = concept.lower()
            for i, anchor in enumerate(anchors):
                if anchor.lower() in concept_lower:
                    return i / (len(anchors) - 1) if len(anchors) > 1 else 0.5
            return 0.5

        prompt = self.get_prompt("quantify", concept=concept, dimension=dimension, anchors=", ".join(anchors))
        response = ""
        async for chunk in self.invoke_llm(messages=[{"role": "user", "content": prompt}], stream=True):
            response += chunk

        try:
            value = float(response.strip())
            return min(1.0, max(0.0, value))
        except ValueError:
            return 0.5

    async def reduce_variance(self, raw_scores: List[float], dimension: str) -> List[float]:
        """Apply variance reduction to raw LLM scores."""
        if not raw_scores:
            return []

        params = self.calibration_params.get(dimension, {"bias": 0.0, "scale": 1.0})
        bias = params.get("bias", 0.0)
        scale = params.get("scale", 1.0)

        calibrated = [(s - bias) * scale for s in raw_scores]

        mean = sum(calibrated) / len(calibrated)
        variance = sum((s - mean) ** 2 for s in calibrated) / len(calibrated) if len(calibrated) > 1 else 0

        if variance > 0.1:
            std = math.sqrt(variance)
            calibrated = [(s - mean) / std * 0.3 + mean for s in calibrated]

        return [min(1.0, max(0.0, s)) for s in calibrated]

    def generate_utility_function(self, preferences: Dict[str, Any]) -> Callable:
        """Generate executable utility function from preferences."""
        weights = preferences.get("weights", {})
        if not weights:
            weights = {dim: 1.0 / len(self.semantic_anchors) for dim in self.semantic_anchors}

        total = sum(weights.values())
        if total > 0:
            weights = {k: v / total for k, v in weights.items()}

        def utility_fn(node: Dict[str, Any]) -> float:
            score = 0.0
            for dim, weight in weights.items():
                dim_value = node.get(dim, node.get("metadata", {}).get(dim, 0.5))
                if isinstance(dim_value, str):
                    dim_value = 0.5
                score += weight * dim_value
            confidence = node.get("confidence", 0.5)
            return score * (0.5 + 0.5 * confidence)

        return utility_fn

    async def compute_node_utility(self, node: Dict[str, Any], utility_function: Callable) -> float:
        """Compute utility score for a single node."""
        return utility_function(node)

    async def compute_branch_utility(self, branch: Dict[str, Any], utility_function: Callable) -> float:
        """Compute aggregate utility score for a branch."""
        nodes = branch.get("nodes", [])
        if not nodes:
            return 0.5

        utilities = [utility_function(n) for n in nodes]

        weights = []
        for node in nodes:
            layer = node.get("layer", 1)
            weight = 1.0 / (layer + 1)
            weights.append(weight)

        total_weight = sum(weights)
        if total_weight > 0:
            weighted_utility = sum(u * w for u, w in zip(utilities, weights)) / total_weight
        else:
            weighted_utility = sum(utilities) / len(utilities)

        return weighted_utility

    async def calibrate_with_benchmark(self, benchmark_data: List[Dict[str, Any]]) -> None:
        """Calibrate scoring model using external benchmark data."""
        for item in benchmark_data:
            dimension = item.get("dimension")
            if not dimension:
                continue

            predicted = item.get("predicted", [])
            actual = item.get("actual", [])

            if not predicted or not actual or len(predicted) != len(actual):
                continue

            pred_mean = sum(predicted) / len(predicted)
            actual_mean = sum(actual) / len(actual)
            bias = pred_mean - actual_mean

            pred_var = sum((p - pred_mean) ** 2 for p in predicted) / len(predicted)
            actual_var = sum((a - actual_mean) ** 2 for a in actual) / len(actual)
            scale = math.sqrt(actual_var / pred_var) if pred_var > 0 else 1.0

            self.calibration_params[dimension] = {"bias": bias, "scale": scale}

    def get_preference_summary(self) -> Dict[str, Any]:
        """Get summary of elicited preferences."""
        return {
            "dimensions": list(self.posteriors.keys()),
            "posteriors": self.posteriors,
            "calibration_params": self.calibration_params,
            "queries_asked": self.queries_asked,
        }

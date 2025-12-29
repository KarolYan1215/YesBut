"""
Requirement Parsing Agent (RPA)

Parses natural language requirements and elicits user preferences
using Bayesian optimization for information-gain maximization.
"""

from typing import Dict, Any, AsyncGenerator, List, Optional
from datetime import datetime
import uuid
import math

from ..base.agent import BaseAgent
from ..streaming import StreamEventType


class BayesianPrior:
    """Bayesian prior distribution for preference parameters."""

    def __init__(self, dimensions: List[str]):
        self.dimensions = dimensions
        self.means: Dict[str, float] = {d: 0.5 for d in dimensions}
        self.variances: Dict[str, float] = {d: 0.25 for d in dimensions}
        self.observation_counts: Dict[str, int] = {d: 0 for d in dimensions}

    def update(self, dimension: str, observation: float) -> None:
        if dimension not in self.dimensions:
            return
        old_mean = self.means[dimension]
        old_var = self.variances[dimension]
        prior_precision = 1.0 / old_var if old_var > 0 else 1.0
        new_precision = prior_precision + 1.0
        self.means[dimension] = (prior_precision * old_mean + observation) / new_precision
        self.variances[dimension] = 1.0 / new_precision
        self.observation_counts[dimension] += 1

    def get_variance(self, dimension: str) -> float:
        return self.variances.get(dimension, 0.25)

    def get_mean(self, dimension: str) -> float:
        return self.means.get(dimension, 0.5)

    def get_entropy(self, dimension: str) -> float:
        var = self.variances.get(dimension, 0.25)
        return 0.5 * math.log(2 * math.pi * math.e * var) if var > 0 else 0.0

    def is_converged(self, threshold: float = 0.05) -> bool:
        return all(v < threshold for v in self.variances.values())


class RequirementParsingAgent(BaseAgent):
    """Requirement Parsing Agent for parsing requirements and eliciting preferences."""

    DEFAULT_DIMENSIONS = ["risk_tolerance", "time_preference", "cost_sensitivity", "quality_priority", "innovation_openness"]

    def __init__(self, agent_id: str, llm_client=None, streaming_callback=None, dimensions: Optional[List[str]] = None,
                 convergence_threshold: float = 0.05, max_elicitation_rounds: int = 10):
        super().__init__(agent_id=agent_id, agent_type="RPA", agent_name="Requirement Parsing Agent",
                         llm_client=llm_client, streaming_callback=streaming_callback)
        self.dimensions = dimensions or self.DEFAULT_DIMENSIONS
        self.prior = BayesianPrior(self.dimensions)
        self.query_history: List[Dict[str, Any]] = []
        self.convergence_threshold = convergence_threshold
        self.max_elicitation_rounds = max_elicitation_rounds
        self._register_prompts()

    def _register_prompts(self) -> None:
        self.register_prompt("parse_requirement", "Analyze: {requirement_text}\nRespond JSON: main_goal, hard_constraints, soft_constraints, implicit_preferences, domain_context, ambiguities")

    async def run(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> AsyncGenerator[Dict[str, Any], None]:
        requirement_text = input_data.get("requirement_text", "")
        await self.think("Analyzing requirement text...")
        yield {"type": StreamEventType.AGENT_THINKING.value, "data": {"thought": "Parsing requirement"}}

        parsed = await self.parse_requirement(requirement_text)
        yield {"type": "requirement_parsed", "data": {"parsed": parsed}}

        goal_node = await self.create_goal_node(parsed)
        yield {"type": StreamEventType.NODE_CREATED.value, "data": {"node": goal_node}}

        constraints = parsed.get("hard_constraints", []) + parsed.get("soft_constraints", [])
        constraint_nodes = await self.create_constraint_nodes([{"content": c, "is_hard": i < len(parsed.get("hard_constraints", []))} for i, c in enumerate(constraints)])
        for node in constraint_nodes:
            yield {"type": StreamEventType.NODE_CREATED.value, "data": {"node": node}}

        if parsed.get("implicit_preferences"):
            async for event in self.elicit_preferences(parsed["implicit_preferences"], context):
                yield event

        utility_code = self.generate_utility_function()
        yield {"type": "utility_function_generated", "data": {"code": utility_code}}
        yield {"type": StreamEventType.AGENT_COMPLETED.value, "data": {"goal_node_id": goal_node["id"]}}

    async def parse_requirement(self, text: str) -> Dict[str, Any]:
        if self.llm_client is None:
            return self._simple_parse(text)
        prompt = self.get_prompt("parse_requirement", requirement_text=text)
        response_text = ""
        async for chunk in self.invoke_llm(messages=[{"role": "user", "content": prompt}], stream=True):
            response_text += chunk
        try:
            import json
            start, end = response_text.find("{"), response_text.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(response_text[start:end])
        except json.JSONDecodeError:
            pass
        return self._simple_parse(text)

    def _simple_parse(self, text: str) -> Dict[str, Any]:
        sentences = [s.strip() for s in text.replace("\n", ". ").split(".") if s.strip()]
        return {"main_goal": sentences[0] if sentences else text, "hard_constraints": [], "soft_constraints": [],
                "implicit_preferences": self.dimensions[:3], "domain_context": "general", "ambiguities": []}

    async def elicit_preferences(self, implicit_preferences: List[str], context: Dict[str, Any]) -> AsyncGenerator[Dict[str, Any], None]:
        round_num = 0
        while round_num < self.max_elicitation_rounds and not self.prior.is_converged(self.convergence_threshold):
            dimension = self._select_next_dimension()
            if dimension is None:
                break
            query = self.generate_query(dimension)
            yield {"type": "preference_query", "data": {"round": round_num, "query": query, "dimension": dimension}}
            simulated_response = query.get("options", [{}])[1] if len(query.get("options", [])) > 1 else {"implied_value": 0.5}
            self.update_posterior(query, simulated_response)
            yield {"type": "preference_updated", "data": {"dimension": dimension, "new_mean": self.prior.get_mean(dimension)}}
            round_num += 1

    def _select_next_dimension(self) -> Optional[str]:
        max_entropy, selected = -float("inf"), None
        for dim in self.dimensions:
            entropy = self.prior.get_entropy(dim)
            if entropy > max_entropy:
                max_entropy, selected = entropy, dim
        return selected if max_entropy > math.log(self.convergence_threshold) else None

    def generate_query(self, preference_dimension: str) -> Dict[str, Any]:
        mean = self.prior.get_mean(preference_dimension)
        std = math.sqrt(self.prior.get_variance(preference_dimension))
        options = [{"label": "A", "description": f"Low {preference_dimension}", "implied_value": max(0, mean - 1.5 * std)},
                   {"label": "B", "description": f"Moderate {preference_dimension}", "implied_value": mean},
                   {"label": "C", "description": f"High {preference_dimension}", "implied_value": min(1, mean + 1.5 * std)}]
        return {"question": f"How important is {preference_dimension}?", "options": options, "dimension": preference_dimension}

    def update_posterior(self, query: Dict[str, Any], response: Any) -> None:
        dimension = query.get("dimension")
        if dimension is None:
            return
        implied_value = response.get("implied_value", 0.5) if isinstance(response, dict) else float(response) if isinstance(response, (int, float)) else 0.5
        self.prior.update(dimension, implied_value)
        self.query_history.append({"query": query, "response": response, "timestamp": datetime.utcnow().isoformat()})

    def generate_utility_function(self) -> str:
        weights = {dim: self.prior.get_mean(dim) for dim in self.dimensions}
        total = sum(weights.values())
        if total > 0:
            weights = {k: v / total for k, v in weights.items()}
        lines = ["def utility_function(solution: Dict[str, Any]) -> float:", "    score = 0.0"]
        for dim, w in weights.items():
            lines.append(f"    score += {w:.3f} * solution.get('{dim}', 0.5)")
        lines.append("    return min(1.0, max(0.0, score))")
        return "\n".join(lines)

    async def create_goal_node(self, parsed_requirement: Dict[str, Any]) -> Dict[str, Any]:
        return {"id": str(uuid.uuid4()), "type": "goal", "content": parsed_requirement.get("main_goal", ""),
                "layer": 0, "branch_id": None, "parent_id": None, "confidence": 1.0, "utility": 1.0, "sensitivity": None,
                "metadata": {"domain_context": parsed_requirement.get("domain_context", "general"), "created_at": datetime.utcnow().isoformat(), "created_by": self.agent_id}}

    async def create_constraint_nodes(self, constraints: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [{"id": str(uuid.uuid4()), "type": "constraint", "content": c.get("content", ""), "layer": 1, "branch_id": None,
                 "parent_id": None, "confidence": 0.9, "utility": 0.8, "sensitivity": None,
                 "metadata": {"is_hard": c.get("is_hard", False), "created_at": datetime.utcnow().isoformat(), "created_by": self.agent_id}} for c in constraints]

    def get_preference_summary(self) -> Dict[str, Any]:
        return {"dimensions": self.dimensions, "means": {d: self.prior.get_mean(d) for d in self.dimensions},
                "variances": {d: self.prior.get_variance(d) for d in self.dimensions},
                "is_converged": self.prior.is_converged(self.convergence_threshold), "queries_asked": len(self.query_history)}

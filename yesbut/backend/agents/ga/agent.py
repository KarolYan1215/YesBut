"""
Game Arbiter Agent (GA)

Manages multi-branch resource allocation and game-theoretic coordination.
Uses qEHVI for resource scheduling and Nash equilibrium for conflict resolution.
"""

from typing import Dict, Any, AsyncGenerator, List, Optional
from datetime import datetime
import uuid
import random

from ..base.agent import BaseAgent
from ..streaming import StreamEventType


class GameArbiterAgent(BaseAgent):
    """
    Game Arbiter Agent for resource allocation and game-theoretic coordination.

    FROZEN Agent: Prompts are never optimized by TextGrad to maintain fairness.
    """

    def __init__(self, agent_id: str, llm_client=None, streaming_callback=None,
                 convergence_controller=None, resource_budget: float = 1.0):
        super().__init__(agent_id=agent_id, agent_type="GA", agent_name="Game Arbiter Agent",
                         llm_client=llm_client, streaming_callback=streaming_callback)
        self.convergence_controller = convergence_controller
        self.resource_budget = resource_budget
        self.round_number = 0
        self.pareto_front: List[Dict[str, Any]] = []
        self._register_prompts()

    def _register_prompts(self) -> None:
        self.register_prompt("arbitrate", """Arbitrate between these branch positions:
{positions}
Determine which arguments are strongest and why.""")

    async def run(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> AsyncGenerator[Dict[str, Any], None]:
        branches = input_data.get("branches", [])
        self.round_number += 1

        await self.think(f"Starting arbitration round {self.round_number}...")
        yield {"type": StreamEventType.AGENT_STARTED.value, "data": {"round": self.round_number, "branch_count": len(branches)}}

        self.pareto_front = await self.compute_pareto_front(branches)
        yield {"type": "pareto_front_computed", "data": {"size": len(self.pareto_front)}}

        allocation = await self.compute_resource_allocation(branches, self.pareto_front)
        yield {"type": "resources_allocated", "data": {"allocation": allocation}}

        convergence_trigger = await self.check_convergence(branches)
        if convergence_trigger:
            branch_ids = [b.get("id") for b in branches]
            async for event in self.trigger_synthesis(branch_ids, convergence_trigger):
                yield event
        else:
            if len(branches) >= 2:
                async for event in self.coordinate_debate_round(branches[0].get("id", ""), branches[1].get("id", ""), "main_topic"):
                    yield event

        yield {"type": StreamEventType.AGENT_COMPLETED.value, "data": self.get_arbitration_status()}

    async def compute_resource_allocation(self, branches: List[Dict[str, Any]], pareto_front: List[Dict[str, Any]]) -> Dict[str, float]:
        """Compute resource allocation using qEHVI."""
        if not branches:
            return {}

        allocation = {}
        total_utility = sum(b.get("utility_score", 0.5) for b in branches)

        for branch in branches:
            branch_id = branch.get("id", "")
            utility = branch.get("utility_score", 0.5)

            is_on_front = any(p.get("id") == branch_id for p in pareto_front)
            base_allocation = (utility / total_utility) * self.resource_budget if total_utility > 0 else self.resource_budget / len(branches)

            if is_on_front:
                base_allocation *= 1.2

            allocation[branch_id] = min(base_allocation, self.resource_budget * 0.5)

        total_allocated = sum(allocation.values())
        if total_allocated > self.resource_budget:
            scale = self.resource_budget / total_allocated
            allocation = {k: v * scale for k, v in allocation.items()}

        return allocation

    async def compute_pareto_front(self, branches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Compute Pareto front from branch utilities."""
        if not branches:
            return []

        def dominates(a: Dict[str, Any], b: Dict[str, Any]) -> bool:
            a_scores = [a.get("utility_score", 0), a.get("confidence", 0), 1 - a.get("risk", 0.5)]
            b_scores = [b.get("utility_score", 0), b.get("confidence", 0), 1 - b.get("risk", 0.5)]
            better_in_one = False
            for a_s, b_s in zip(a_scores, b_scores):
                if a_s < b_s:
                    return False
                if a_s > b_s:
                    better_in_one = True
            return better_in_one

        pareto = []
        for branch in branches:
            is_dominated = False
            for other in branches:
                if other.get("id") != branch.get("id") and dominates(other, branch):
                    is_dominated = True
                    break
            if not is_dominated:
                pareto.append(branch)

        return pareto

    async def compute_nash_equilibrium(self, branches: List[Dict[str, Any]], conflict_matrix: List[List[float]]) -> Dict[str, Any]:
        """Compute Nash equilibrium for branch conflicts."""
        n = len(branches)
        if n == 0:
            return {"equilibrium_strategies": {}, "stable_branches": [], "eliminated_branches": []}

        strategies = {b.get("id", ""): 1.0 / n for b in branches}

        for _ in range(10):
            new_strategies = {}
            for i, branch in enumerate(branches):
                branch_id = branch.get("id", "")
                payoff = 0.0
                for j, other in enumerate(branches):
                    if i < len(conflict_matrix) and j < len(conflict_matrix[i]):
                        payoff += strategies.get(other.get("id", ""), 0) * conflict_matrix[i][j]
                new_strategies[branch_id] = max(0.1, min(0.9, strategies[branch_id] + 0.1 * payoff))

            total = sum(new_strategies.values())
            strategies = {k: v / total for k, v in new_strategies.items()}

        threshold = 0.1 / n
        stable = [b.get("id") for b in branches if strategies.get(b.get("id", ""), 0) > threshold]
        eliminated = [b.get("id") for b in branches if strategies.get(b.get("id", ""), 0) <= threshold]

        return {"equilibrium_strategies": strategies, "stable_branches": stable, "eliminated_branches": eliminated}

    async def coordinate_debate_round(self, branch_a_id: str, branch_b_id: str, topic: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Coordinate a debate round between two branches."""
        yield {"type": "debate_round_started", "data": {"branch_a": branch_a_id, "branch_b": branch_b_id, "topic": topic, "round": self.round_number}}
        yield {"type": "debate_round_completed", "data": {"branch_a": branch_a_id, "branch_b": branch_b_id}}

    async def check_convergence(self, branches: List[Dict[str, Any]]) -> Optional[str]:
        """Check if convergence should be triggered."""
        if self.convergence_controller:
            return await self.convergence_controller.check(branches)

        if len(branches) <= 1:
            return "single_branch"

        utilities = [b.get("utility_score", 0.5) for b in branches]
        if max(utilities) - min(utilities) < 0.1:
            return "utility_convergence"

        if self.round_number >= 10:
            return "max_rounds"

        return None

    async def trigger_synthesis(self, branch_ids: List[str], trigger_reason: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Trigger Hegelian synthesis between branches."""
        yield {"type": "synthesis_triggered", "data": {"branch_ids": branch_ids, "reason": trigger_reason}}
        yield {"type": StreamEventType.PHASE_CHANGED.value, "data": {"previous_phase": "filtering", "current_phase": "convergence"}}

    async def compute_branch_similarity(self, branch_a: Dict[str, Any], branch_b: Dict[str, Any]) -> float:
        """Compute similarity between two branch positions."""
        content_a = branch_a.get("main_claim", "")
        content_b = branch_b.get("main_claim", "")

        words_a = set(content_a.lower().split())
        words_b = set(content_b.lower().split())

        if not words_a or not words_b:
            return 0.0

        intersection = len(words_a & words_b)
        union = len(words_a | words_b)
        return intersection / union if union > 0 else 0.0

    def get_arbitration_status(self) -> Dict[str, Any]:
        """Get current arbitration status."""
        return {
            "round": self.round_number,
            "pareto_front_size": len(self.pareto_front),
            "resource_budget": self.resource_budget,
            "timestamp": datetime.utcnow().isoformat(),
        }

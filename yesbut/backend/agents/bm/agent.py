"""
Branch Manager Agent (BM)

Manages individual reasoning branches and participates in
multi-agent debate during the convergence phase.
"""

from typing import Dict, Any, AsyncGenerator, List, Optional, Callable
from datetime import datetime
import uuid
import random

from ..base.agent import BaseAgent
from ..streaming import StreamEventType


class BranchManagerAgent(BaseAgent):
    """
    Branch Manager Agent for managing reasoning branches and participating in debates.

    Each BM agent is bound to a specific branch and its utility function.
    """

    QUESTION_TYPES = ["clarification", "assumption_probing", "evidence_request", "implication_exploration", "alternative_viewpoint"]
    RESPONSE_STRATEGIES = ["defend", "concede", "counter_attack", "redirect"]

    def __init__(self, agent_id: str, branch_id: str, llm_client=None, streaming_callback=None,
                 utility_function: Optional[Callable] = None):
        super().__init__(agent_id=agent_id, agent_type="BM", agent_name=f"Branch Manager ({branch_id[:8]})",
                         llm_client=llm_client, streaming_callback=streaming_callback)
        self.branch_id = branch_id
        self.utility_function = utility_function or self._default_utility
        self.position_history: List[Dict[str, Any]] = []
        self.current_position: Optional[Dict[str, Any]] = None
        self._register_prompts()

    def _default_utility(self, solution: Dict[str, Any]) -> float:
        return solution.get("confidence", 0.5) * solution.get("utility", 0.5)

    def _register_prompts(self) -> None:
        self.register_prompt("expand_branch", """Given the current branch state, suggest the next action:
Current claims: {claims}
Goal: {goal}
Available actions: add_node, add_edge, query_ISA, attack_node
Respond with: action, target, reasoning.""")

        self.register_prompt("generate_argument", """Generate an argument for this position:
Position: {position}
Topic: {topic}
Respond with a compelling argument.""")

        self.register_prompt("socratic_question", """Generate a Socratic question to challenge this claim:
Claim: {claim}
Question type: {question_type}
Respond with just the question.""")

        self.register_prompt("respond_to_attack", """Respond to this attack on your position:
Your position: {position}
Attack: {attack}
Strategy: {strategy}
Respond with your defense or counter-argument.""")

    async def run(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> AsyncGenerator[Dict[str, Any], None]:
        await self.think(f"Managing branch {self.branch_id[:8]}...")
        yield {"type": StreamEventType.AGENT_STARTED.value, "data": {"branch_id": self.branch_id}}

        branch_state = input_data.get("branch_state", {})
        self._update_current_position(branch_state)

        async for event in self.expand_branch(branch_state):
            yield event

        attacks = input_data.get("pending_attacks", [])
        for attack in attacks:
            async for event in self.respond_to_attack(attack):
                yield event

        yield {"type": StreamEventType.AGENT_COMPLETED.value, "data": {"branch_id": self.branch_id, "position": self.current_position}}

    def _update_current_position(self, branch_state: Dict[str, Any]) -> None:
        nodes = branch_state.get("nodes", [])
        claims = [n for n in nodes if n.get("type") == "claim"]
        facts = [n for n in nodes if n.get("type") == "fact"]
        goal = next((n for n in nodes if n.get("type") == "goal"), None)

        self.current_position = {
            "main_claim": claims[0].get("content") if claims else "",
            "supporting_claims": [c.get("content") for c in claims[1:5]],
            "evidence": [f.get("content") for f in facts[:5]],
            "goal": goal.get("content") if goal else "",
            "utility_score": self._compute_branch_utility(branch_state),
        }

    def _compute_branch_utility(self, branch_state: Dict[str, Any]) -> float:
        nodes = branch_state.get("nodes", [])
        if not nodes:
            return 0.5
        total_utility = sum(self.utility_function(n) for n in nodes)
        return total_utility / len(nodes)

    async def expand_branch(self, current_state: Dict[str, Any]) -> AsyncGenerator[Dict[str, Any], None]:
        """Expand the branch through state space search."""
        nodes = current_state.get("nodes", [])
        goal = next((n for n in nodes if n.get("type") == "goal"), {})

        if self.llm_client is None:
            action = random.choice(["add_node", "query_ISA"])
            if action == "add_node":
                new_node = self._create_claim_node(f"Supporting claim for {goal.get('content', '')[:50]}")
                yield {"type": StreamEventType.NODE_CREATED.value, "data": {"node": new_node}}
            else:
                yield {"type": "isa_query_requested", "data": {"query": goal.get("content", ""), "branch_id": self.branch_id}}
            return

        claims_text = "\n".join([n.get("content", "")[:100] for n in nodes if n.get("type") == "claim"][:5])
        prompt = self.get_prompt("expand_branch", claims=claims_text, goal=goal.get("content", ""))
        response = ""
        async for chunk in self.invoke_llm(messages=[{"role": "user", "content": prompt}], stream=True):
            response += chunk

        if "add_node" in response.lower():
            new_node = self._create_claim_node(response[:200])
            yield {"type": StreamEventType.NODE_CREATED.value, "data": {"node": new_node}}
        elif "query_isa" in response.lower():
            yield {"type": "isa_query_requested", "data": {"query": response[:200], "branch_id": self.branch_id}}
        elif "attack" in response.lower():
            yield {"type": "attack_proposed", "data": {"reasoning": response[:200], "branch_id": self.branch_id}}

    def _create_claim_node(self, content: str) -> Dict[str, Any]:
        return {
            "id": str(uuid.uuid4()),
            "type": "claim",
            "content": content,
            "layer": 2,
            "branch_id": self.branch_id,
            "parent_id": None,
            "confidence": 0.7,
            "utility": 0.6,
            "sensitivity": None,
            "metadata": {"created_at": datetime.utcnow().isoformat(), "created_by": self.agent_id},
        }

    async def engage_debate(self, opponent_branch_id: str, topic: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Engage in debate with another branch's BM agent."""
        yield {"type": "debate_started", "data": {"branch_id": self.branch_id, "opponent": opponent_branch_id, "topic": topic}}

        if self.llm_client is None:
            argument = f"Our position on {topic} is supported by evidence and logical reasoning."
        else:
            prompt = self.get_prompt("generate_argument", position=self.current_position.get("main_claim", ""), topic=topic)
            argument = ""
            async for chunk in self.invoke_llm(messages=[{"role": "user", "content": prompt}], stream=True):
                argument += chunk

        yield {"type": "debate_argument", "data": {"branch_id": self.branch_id, "argument": argument, "round": 1}}
        self.record_position({"argument": argument, "topic": topic})

    async def socratic_question(self, target_claim: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Socratic question to challenge a claim."""
        question_type = random.choice(self.QUESTION_TYPES)
        claim_content = target_claim.get("content", "")

        if self.llm_client is None:
            questions = {
                "clarification": f"What exactly do you mean by '{claim_content[:50]}'?",
                "assumption_probing": f"What assumptions underlie the claim that {claim_content[:50]}?",
                "evidence_request": f"What evidence supports the assertion that {claim_content[:50]}?",
                "implication_exploration": f"If {claim_content[:50]} is true, what follows?",
                "alternative_viewpoint": f"Have you considered alternatives to {claim_content[:50]}?",
            }
            question = questions.get(question_type, questions["clarification"])
        else:
            prompt = self.get_prompt("socratic_question", claim=claim_content, question_type=question_type)
            question = ""
            async for chunk in self.invoke_llm(messages=[{"role": "user", "content": prompt}], stream=True):
                question += chunk

        return {"question": question.strip(), "question_type": question_type, "target_claim_id": target_claim.get("id")}

    async def respond_to_attack(self, attack: Dict[str, Any]) -> AsyncGenerator[Dict[str, Any], None]:
        """Respond to an attack from another branch."""
        attack_content = attack.get("content", "")
        strategy = self._select_response_strategy(attack)

        yield {"type": "attack_response_started", "data": {"attack_id": attack.get("id"), "strategy": strategy}}

        if self.llm_client is None:
            responses = {
                "defend": f"Our position is supported by the following evidence: {self.current_position.get('evidence', ['evidence'])[0]}",
                "concede": "We acknowledge this point and will adjust our position accordingly.",
                "counter_attack": f"However, this attack fails to consider: {self.current_position.get('main_claim', '')}",
                "redirect": "Let us focus on the more fundamental question at hand.",
            }
            response = responses.get(strategy, responses["defend"])
        else:
            prompt = self.get_prompt("respond_to_attack", position=self.current_position.get("main_claim", ""),
                                     attack=attack_content, strategy=strategy)
            response = ""
            async for chunk in self.invoke_llm(messages=[{"role": "user", "content": prompt}], stream=True):
                response += chunk

        yield {"type": "attack_response", "data": {"response": response, "strategy": strategy, "branch_id": self.branch_id}}

        if strategy == "concede":
            yield {"type": "position_modified", "data": {"branch_id": self.branch_id, "reason": "concession"}}

    def _select_response_strategy(self, attack: Dict[str, Any]) -> str:
        attack_strength = attack.get("confidence", 0.5)
        our_confidence = self.current_position.get("utility_score", 0.5) if self.current_position else 0.5

        if attack_strength > 0.8 and our_confidence < 0.4:
            return "concede"
        elif attack_strength < 0.5:
            return "counter_attack"
        elif our_confidence > 0.7:
            return "defend"
        else:
            return "redirect"

    async def participate_synthesis(self, other_branches: List[str], synthesis_type: str) -> Dict[str, Any]:
        """Participate in Hegelian dialectical synthesis."""
        contribution = {
            "branch_id": self.branch_id,
            "synthesis_type": synthesis_type,
            "main_claim": self.current_position.get("main_claim", "") if self.current_position else "",
            "key_points": self.current_position.get("supporting_claims", [])[:3] if self.current_position else [],
            "evidence": self.current_position.get("evidence", [])[:3] if self.current_position else [],
            "utility_score": self.current_position.get("utility_score", 0.5) if self.current_position else 0.5,
        }

        if synthesis_type == "integration":
            contribution["integration_points"] = ["Compatible elements that can be merged"]
        elif synthesis_type == "compromise":
            contribution["compromise_points"] = ["Areas where we can find middle ground"]
        elif synthesis_type == "transcendence":
            contribution["transcendence_points"] = ["Higher-level insights that resolve the conflict"]

        return contribution

    def get_current_position(self) -> Dict[str, Any]:
        """Get the current position/stance of this branch."""
        return self.current_position or {"main_claim": "", "supporting_claims": [], "evidence": [], "utility_score": 0.5}

    def record_position(self, position: Dict[str, Any]) -> None:
        """Record position in history for oscillation detection."""
        position["timestamp"] = datetime.utcnow().isoformat()
        position["branch_id"] = self.branch_id
        self.position_history.append(position)
        if len(self.position_history) > 20:
            self.position_history = self.position_history[-20:]

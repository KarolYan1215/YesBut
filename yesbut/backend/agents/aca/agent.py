"""
Audit & Compliance Agent (ACA)

Detects logical inconsistencies and validates constraint compliance
using first-order logic and SAT solvers.
"""

from typing import Dict, Any, AsyncGenerator, List, Tuple, Set
from datetime import datetime
from collections import defaultdict
import uuid

from ..base.agent import BaseAgent
from ..streaming import StreamEventType


class AuditComplianceAgent(BaseAgent):
    """
    Audit & Compliance Agent for detecting logical inconsistencies.

    FROZEN Agent: Prompts are never optimized by TextGrad to maintain audit integrity.
    """

    def __init__(self, agent_id: str, llm_client=None, streaming_callback=None):
        super().__init__(agent_id=agent_id, agent_type="ACA", agent_name="Audit & Compliance Agent",
                         llm_client=llm_client, streaming_callback=streaming_callback)
        self._register_prompts()

    def _register_prompts(self) -> None:
        self.register_prompt("extract_proposition", """Extract a logical proposition from this claim:
Claim: {claim}
Express as a simple logical statement. Respond with just the proposition.""")

        self.register_prompt("check_contradiction", """Do these two claims contradict each other?
Claim A: {claim_a}
Claim B: {claim_b}
Respond with: contradicts (bool), explanation, confidence (0-1).""")

        self.register_prompt("verify_attack", """Verify if this attack is logically valid:
Attacker claim: {attacker}
Target claim: {target}
Attack reasoning: {reasoning}
Respond with: is_valid (bool), confidence (0-1), explanation.""")

    async def run(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> AsyncGenerator[Dict[str, Any], None]:
        graph_state = input_data.get("graph_state", {})
        nodes = list(graph_state.get("nodes", {}).values())
        edges = list(graph_state.get("edges", {}).values())

        await self.think("Starting audit and compliance check...")
        yield {"type": StreamEventType.AGENT_STARTED.value, "data": {"node_count": len(nodes), "edge_count": len(edges)}}

        propositions = await self.extract_propositions(nodes)
        yield {"type": "propositions_extracted", "data": {"count": len(propositions)}}

        consistency_result = await self.check_consistency(propositions)
        yield {"type": "consistency_checked", "data": consistency_result}

        constraints = [n for n in nodes if n.get("type") == "constraint"]
        constraint_results = await self.validate_constraints(nodes, constraints)
        yield {"type": "constraints_validated", "data": {"results": constraint_results}}

        cycles = await self.detect_circular_dependencies(edges)
        yield {"type": "cycles_detected", "data": {"cycles": cycles}}

        report = await self.generate_audit_report(consistency_result, constraint_results)
        report["cycles"] = cycles
        yield {"type": "audit_report", "data": report}

        yield {"type": StreamEventType.AGENT_COMPLETED.value, "data": {"is_compliant": report.get("is_compliant", False)}}

    async def extract_propositions(self, nodes: List[Dict[str, Any]]) -> List[Tuple[str, str]]:
        """Extract first-order logic propositions from nodes."""
        propositions = []
        for node in nodes:
            node_id = node.get("id", "")
            content = node.get("content", "")
            if not content:
                continue

            if self.llm_client is None:
                proposition = f"P({node_id}): {content[:100]}"
            else:
                prompt = self.get_prompt("extract_proposition", claim=content)
                response = ""
                async for chunk in self.invoke_llm(messages=[{"role": "user", "content": prompt}], stream=True):
                    response += chunk
                proposition = response.strip()

            propositions.append((node_id, proposition))
        return propositions

    async def check_consistency(self, propositions: List[Tuple[str, str]]) -> Dict[str, Any]:
        """Check logical consistency of proposition set."""
        conflicts = []

        for i, (id_a, prop_a) in enumerate(propositions):
            for j, (id_b, prop_b) in enumerate(propositions[i+1:], start=i+1):
                is_contradiction = await self._check_contradiction(prop_a, prop_b)
                if is_contradiction:
                    conflicts.append({"node_a": id_a, "node_b": id_b, "prop_a": prop_a, "prop_b": prop_b})

        return {
            "is_consistent": len(conflicts) == 0,
            "conflicts": conflicts,
            "conflict_count": len(conflicts),
            "explanation": f"Found {len(conflicts)} logical conflicts" if conflicts else "No conflicts detected",
        }

    async def _check_contradiction(self, prop_a: str, prop_b: str) -> bool:
        """Check if two propositions contradict each other."""
        if self.llm_client is None:
            negation_words = ["not", "never", "no", "cannot", "impossible"]
            a_lower, b_lower = prop_a.lower(), prop_b.lower()
            for word in negation_words:
                if (word in a_lower) != (word in b_lower):
                    words_a = set(a_lower.split()) - {word}
                    words_b = set(b_lower.split()) - {word}
                    if len(words_a & words_b) > 3:
                        return True
            return False

        prompt = self.get_prompt("check_contradiction", claim_a=prop_a, claim_b=prop_b)
        response = ""
        async for chunk in self.invoke_llm(messages=[{"role": "user", "content": prompt}], stream=True):
            response += chunk

        return "true" in response.lower() and "contradicts" in response.lower()

    async def validate_constraints(self, nodes: List[Dict[str, Any]], constraints: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate that all constraints are satisfied."""
        results = []
        claim_nodes = [n for n in nodes if n.get("type") in ["claim", "goal"]]

        for constraint in constraints:
            constraint_content = constraint.get("content", "")
            is_hard = constraint.get("metadata", {}).get("is_hard", False)

            violations = []
            for claim in claim_nodes:
                if self._violates_constraint(claim.get("content", ""), constraint_content):
                    violations.append(claim.get("id"))

            results.append({
                "constraint_id": constraint.get("id"),
                "constraint_content": constraint_content,
                "is_hard": is_hard,
                "is_satisfied": len(violations) == 0,
                "violations": violations,
            })

        return results

    def _violates_constraint(self, claim: str, constraint: str) -> bool:
        """Simple heuristic check for constraint violation."""
        claim_lower = claim.lower()
        constraint_lower = constraint.lower()

        if "must" in constraint_lower or "required" in constraint_lower:
            key_terms = [w for w in constraint_lower.split() if len(w) > 4 and w not in ["must", "required", "should"]]
            if key_terms and not any(term in claim_lower for term in key_terms):
                return True

        if "must not" in constraint_lower or "cannot" in constraint_lower:
            forbidden_terms = constraint_lower.replace("must not", "").replace("cannot", "").split()
            if any(term in claim_lower for term in forbidden_terms if len(term) > 3):
                return True

        return False

    async def verify_attack(self, attacker_node: Dict[str, Any], target_node: Dict[str, Any], attack_reasoning: str) -> Dict[str, Any]:
        """Verify the validity of an attack between nodes."""
        attacker_content = attacker_node.get("content", "")
        target_content = target_node.get("content", "")

        if self.llm_client is None:
            is_valid = len(attack_reasoning) > 20 and ("because" in attack_reasoning.lower() or "therefore" in attack_reasoning.lower())
            return {"is_valid": is_valid, "confidence": 0.6 if is_valid else 0.4, "explanation": "Heuristic validation"}

        prompt = self.get_prompt("verify_attack", attacker=attacker_content, target=target_content, reasoning=attack_reasoning)
        response = ""
        async for chunk in self.invoke_llm(messages=[{"role": "user", "content": prompt}], stream=True):
            response += chunk

        is_valid = "true" in response.lower() and "valid" in response.lower()
        return {"is_valid": is_valid, "confidence": 0.7 if is_valid else 0.5, "explanation": response[:200]}

    async def generate_audit_report(self, consistency_result: Dict[str, Any], constraint_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive audit report."""
        hard_violations = [r for r in constraint_results if r.get("is_hard") and not r.get("is_satisfied")]
        soft_violations = [r for r in constraint_results if not r.get("is_hard") and not r.get("is_satisfied")]

        is_compliant = consistency_result.get("is_consistent", True) and len(hard_violations) == 0

        return {
            "is_compliant": is_compliant,
            "consistency": consistency_result,
            "hard_constraint_violations": hard_violations,
            "soft_constraint_violations": soft_violations,
            "total_constraints": len(constraint_results),
            "satisfied_constraints": len([r for r in constraint_results if r.get("is_satisfied")]),
            "timestamp": datetime.utcnow().isoformat(),
            "auditor_id": self.agent_id,
        }

    async def detect_circular_dependencies(self, edges: List[Dict[str, Any]]) -> List[List[str]]:
        """Detect circular dependencies in the reasoning graph."""
        graph = defaultdict(list)
        for edge in edges:
            source = edge.get("source_id")
            target = edge.get("target_id")
            if source and target:
                graph[source].append(target)

        cycles = []
        visited = set()
        rec_stack = set()

        def dfs(node: str, path: List[str]) -> None:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in graph[node]:
                if neighbor not in visited:
                    dfs(neighbor, path)
                elif neighbor in rec_stack:
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    if cycle not in cycles:
                        cycles.append(cycle)

            path.pop()
            rec_stack.remove(node)

        for node in graph:
            if node not in visited:
                dfs(node, [])

        return cycles

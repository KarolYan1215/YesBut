"""
Reverse Engineering Compiler Agent (REC)

Compiles the converged reasoning graph into executable action plans
with complete reasoning traces and confidence assessments.
"""

from typing import Dict, Any, AsyncGenerator, List, Optional
from datetime import datetime
import uuid

from ..base.agent import BaseAgent
from ..streaming import StreamEventType


class ReverseEngineeringCompilerAgent(BaseAgent):
    """REC Agent for compiling reasoning graphs into action plans."""

    def __init__(self, agent_id: str, llm_client=None, streaming_callback=None,
                 output_templates: Optional[Dict[str, str]] = None):
        super().__init__(agent_id=agent_id, agent_type="REC", agent_name="Reverse Engineering Compiler",
                         llm_client=llm_client, streaming_callback=streaming_callback)
        self.output_templates = output_templates or {}
        self._register_prompts()

    def _register_prompts(self) -> None:
        self.register_prompt("compile", """Compile this reasoning path into an action plan:
Path: {path}
Evidence: {evidence}
Format: {format}""")

    async def run(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> AsyncGenerator[Dict[str, Any], None]:
        graph_state = input_data.get("graph_state", {})
        output_format = input_data.get("output_format", "markdown")

        await self.think("Compiling reasoning graph...")
        yield {"type": StreamEventType.AGENT_STARTED.value, "data": {"format": output_format}}

        path = await self.extract_winning_path(graph_state)
        yield {"type": "path_extracted", "data": {"path_length": len(path)}}

        evidence = await self.collect_evidence(path)
        yield {"type": "evidence_collected", "data": {"evidence_count": len(evidence)}}

        trace = await self.generate_reasoning_trace(path, evidence)
        yield {"type": "trace_generated", "data": {"step_count": len(trace.get("steps", []))}}

        confidence = await self.compute_confidence_assessment(path, evidence)
        yield {"type": "confidence_computed", "data": confidence}

        if output_format == "markdown":
            output = await self.compile_markdown(path, evidence, trace, {})
        elif output_format == "json":
            output = await self.compile_json(path, evidence, trace, {})
        else:
            output = await self.compile_structured("default", path, evidence, trace, {})

        yield {"type": "compilation_complete", "data": {"output": output}}
        yield {"type": StreamEventType.AGENT_COMPLETED.value, "data": {"format": output_format}}

    async def extract_winning_path(self, graph_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        nodes = list(graph_state.get("nodes", {}).values())
        edges = list(graph_state.get("edges", {}).values())

        goal = next((n for n in nodes if n.get("type") == "goal"), None)
        if not goal:
            return []

        sorted_nodes = sorted(nodes, key=lambda n: (-n.get("utility", 0), -n.get("confidence", 0)))
        path = [goal]

        for node in sorted_nodes[:10]:
            if node.get("type") != "goal" and node not in path:
                path.append(node)

        return path

    async def collect_evidence(self, path: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        evidence = []
        for node in path:
            if node.get("type") == "fact":
                evidence.append({
                    "content": node.get("content", ""),
                    "sources": node.get("metadata", {}).get("sources", []),
                    "confidence": node.get("confidence", 0.5),
                })
        return evidence

    async def generate_reasoning_trace(self, path: List[Dict[str, Any]], evidence: List[Dict[str, Any]]) -> Dict[str, Any]:
        steps = []
        for i, node in enumerate(path):
            steps.append({
                "step": i + 1,
                "type": node.get("type", "unknown"),
                "content": node.get("content", ""),
                "confidence": node.get("confidence", 0.5),
                "reasoning": f"This {node.get('type', 'step')} contributes to the overall solution.",
            })

        return {"steps": steps, "total_steps": len(steps), "evidence_used": len(evidence)}

    async def elicit_user_conditions(self, required_conditions: List[str]) -> Dict[str, Any]:
        return {condition: "unknown" for condition in required_conditions}

    async def compile_markdown(self, path: List[Dict[str, Any]], evidence: List[Dict[str, Any]],
                               reasoning_trace: Dict[str, Any], user_conditions: Dict[str, Any]) -> str:
        lines = ["# Action Plan\n"]

        goal = next((n for n in path if n.get("type") == "goal"), None)
        if goal:
            lines.append(f"## Goal\n{goal.get('content', '')}\n")

        lines.append("## Steps\n")
        for step in reasoning_trace.get("steps", []):
            lines.append(f"{step['step']}. **{step['type'].title()}**: {step['content'][:200]}")
            lines.append(f"   - Confidence: {step['confidence']:.0%}\n")

        if evidence:
            lines.append("## Supporting Evidence\n")
            for e in evidence[:5]:
                lines.append(f"- {e['content'][:150]}")

        return "\n".join(lines)

    async def compile_json(self, path: List[Dict[str, Any]], evidence: List[Dict[str, Any]],
                           reasoning_trace: Dict[str, Any], user_conditions: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "goal": next((n.get("content") for n in path if n.get("type") == "goal"), ""),
            "steps": reasoning_trace.get("steps", []),
            "evidence": evidence,
            "conditions": user_conditions,
            "generated_at": datetime.utcnow().isoformat(),
        }

    async def compile_structured(self, template_name: str, path: List[Dict[str, Any]], evidence: List[Dict[str, Any]],
                                 reasoning_trace: Dict[str, Any], user_conditions: Dict[str, Any]) -> Dict[str, Any]:
        return await self.compile_json(path, evidence, reasoning_trace, user_conditions)

    async def compute_confidence_assessment(self, path: List[Dict[str, Any]], evidence: List[Dict[str, Any]]) -> Dict[str, Any]:
        confidences = [n.get("confidence", 0.5) for n in path]
        overall = sum(confidences) / len(confidences) if confidences else 0.5

        weak_points = [{"step": i+1, "confidence": c} for i, c in enumerate(confidences) if c < 0.5]

        return {
            "overall_confidence": overall,
            "step_confidences": confidences,
            "weak_points": weak_points,
            "evidence_support": len(evidence),
        }

    async def generate_alternative_summary(self, graph_state: Dict[str, Any], winning_path: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        nodes = list(graph_state.get("nodes", {}).values())
        winning_ids = {n.get("id") for n in winning_path}

        alternatives = []
        for node in nodes:
            if node.get("id") not in winning_ids and node.get("type") == "claim":
                alternatives.append({
                    "content": node.get("content", "")[:100],
                    "utility": node.get("utility", 0),
                    "reason_not_selected": "Lower utility score",
                })

        return sorted(alternatives, key=lambda x: -x.get("utility", 0))[:5]

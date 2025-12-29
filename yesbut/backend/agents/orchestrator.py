"""
LangGraph Agent Orchestrator

Main orchestrator for the multi-agent collaborative brainstorming system.
Coordinates 8 agent types through the three-phase pipeline using LangGraph.
"""

from typing import Dict, Any, AsyncGenerator, Optional, List, Callable
from enum import Enum
from datetime import datetime
import uuid
import asyncio

from anthropic import AsyncAnthropic

from .state import (
    AgentState, PhaseType, create_initial_state,
    create_node_state, create_edge_state, create_branch_state,
    should_transition_phase, get_next_phase, update_convergence_metrics
)
from .streaming import StreamManager, StreamEventType, create_phase_event, create_progress_event
from .rpa.agent import RequirementParsingAgent
from .gen.agent import GeneratorAgent
from .isa.agent import InformationScoutAgent
from .aca.agent import AuditComplianceAgent
from .bm.agent import BranchManagerAgent
from .ga.agent import GameArbiterAgent
from .uoa.agent import UtilityOptimizationAgent
from .rec.agent import ReverseEngineeringCompilerAgent
from .convergence_controller import ConvergenceController


class Phase(str, Enum):
    """Three-phase pipeline phases."""
    DIVERGENCE = "divergence"
    FILTERING = "filtering"
    CONVERGENCE = "convergence"


class AgentOrchestrator:
    """
    LangGraph-based orchestrator for multi-agent brainstorming.

    This orchestrator manages the three-phase pipeline:
    1. Divergence: GEN agent generates diverse solutions using QD
    2. Filtering: ACA and UOA filter candidates via Pareto optimization
    3. Convergence: BM agents debate, GA arbitrates, synthesis occurs
    """

    def __init__(
        self,
        session_id: str,
        llm_client: Optional[AsyncAnthropic] = None,
        db=None,
        redis=None,
        streaming_callback: Optional[Callable] = None,
    ):
        self.session_id = session_id
        self.llm_client = llm_client
        self.db = db
        self.redis = redis
        self.streaming_callback = streaming_callback

        self.state: Optional[AgentState] = None
        self.stream_manager = StreamManager(redis=redis)
        self.convergence_controller = ConvergenceController()

        # Initialize agents
        self._init_agents()

    def _init_agents(self) -> None:
        """Initialize all agent instances."""
        base_kwargs = {
            "llm_client": self.llm_client,
            "streaming_callback": self._emit_event,
        }

        self.rpa = RequirementParsingAgent(
            agent_id=f"rpa_{self.session_id[:8]}",
            **base_kwargs
        )
        self.gen = GeneratorAgent(
            agent_id=f"gen_{self.session_id[:8]}",
            **base_kwargs
        )
        self.isa = InformationScoutAgent(
            agent_id=f"isa_{self.session_id[:8]}",
            **base_kwargs
        )
        self.aca = AuditComplianceAgent(
            agent_id=f"aca_{self.session_id[:8]}",
            **base_kwargs
        )
        self.ga = GameArbiterAgent(
            agent_id=f"ga_{self.session_id[:8]}",
            convergence_controller=self.convergence_controller,
            **base_kwargs
        )
        self.uoa = UtilityOptimizationAgent(
            agent_id=f"uoa_{self.session_id[:8]}",
            **base_kwargs
        )
        self.rec = ReverseEngineeringCompilerAgent(
            agent_id=f"rec_{self.session_id[:8]}",
            **base_kwargs
        )

        self.bm_agents: Dict[str, BranchManagerAgent] = {}

    async def _emit_event(self, event: Dict[str, Any]) -> None:
        """Emit event via streaming callback."""
        if self.streaming_callback:
            if asyncio.iscoroutinefunction(self.streaming_callback):
                await self.streaming_callback(event)
            else:
                self.streaming_callback(event)

    async def run(
        self,
        initial_requirement: str,
        mode: str = "async",
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Run the full orchestration pipeline."""
        # Initialize state
        self.state = create_initial_state(self.session_id, initial_requirement)

        yield {"type": "orchestration_started", "data": {"session_id": self.session_id, "mode": mode}}

        # Phase 1: Parse requirements with RPA
        yield {"type": "phase_started", "data": {"phase": "initialization"}}
        async for event in self._run_rpa(initial_requirement):
            yield event

        # Phase 2: Divergence
        yield create_phase_event("initialization", "divergence", self.session_id).to_dict()
        self.state["phase"] = PhaseType.DIVERGENCE
        async for event in self.run_divergence_phase():
            yield event

        # Phase 3: Filtering
        yield create_phase_event("divergence", "filtering", self.session_id).to_dict()
        self.state["phase"] = PhaseType.FILTERING
        async for event in self.run_filtering_phase():
            yield event

        # Phase 4: Convergence
        yield create_phase_event("filtering", "convergence", self.session_id).to_dict()
        self.state["phase"] = PhaseType.CONVERGENCE
        async for event in self.run_convergence_phase():
            yield event

        # Phase 5: Compile output with REC
        yield {"type": "phase_started", "data": {"phase": "compilation"}}
        async for event in self._run_rec():
            yield event

        yield {"type": "orchestration_completed", "data": {"session_id": self.session_id}}

    async def _run_rpa(self, requirement: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Run RPA agent to parse requirements."""
        input_data = {"requirement_text": requirement}
        context = {"session_id": self.session_id, "state": self.state}

        async for event in self.rpa.run(input_data, context):
            yield event

            # Update state with created nodes
            if event.get("type") == StreamEventType.NODE_CREATED.value:
                node = event.get("data", {}).get("node", {})
                if node.get("id"):
                    self.state["nodes"][node["id"]] = node

    async def run_divergence_phase(self) -> AsyncGenerator[Dict[str, Any], None]:
        """Execute the divergence phase."""
        yield {"type": "divergence_started", "data": {"target_solutions": 100}}

        # Get goal node
        goal_node = None
        for node in self.state["nodes"].values():
            if node.get("type") == "goal":
                goal_node = node
                break

        if not goal_node:
            yield {"type": "error", "data": {"message": "No goal node found"}}
            return

        # Get constraints
        constraints = [n for n in self.state["nodes"].values() if n.get("type") == "constraint"]

        input_data = {
            "goal": goal_node,
            "constraints": constraints,
            "target_count": 50,
        }
        context = {"session_id": self.session_id, "state": self.state}

        async for event in self.gen.run(input_data, context):
            yield event

            # Update state with created nodes
            if event.get("type") in [StreamEventType.NODE_CREATED.value, StreamEventType.NODE_PREVIEW.value]:
                node = event.get("data", {}).get("node", {})
                if node.get("id"):
                    self.state["nodes"][node["id"]] = node

            # Update progress
            if event.get("type") == StreamEventType.PROGRESS_UPDATED.value:
                progress = event.get("data", {}).get("progress", 0)
                self.state["phase_progress"] = progress

        # Check phase transition
        if should_transition_phase(self.state):
            yield {"type": "phase_transition_ready", "data": {"next_phase": "filtering"}}

    async def run_filtering_phase(self) -> AsyncGenerator[Dict[str, Any], None]:
        """Execute the filtering phase."""
        yield {"type": "filtering_started", "data": {"candidate_count": len(self.state["nodes"])}}

        # Run ACA for consistency check
        input_data = {"graph_state": self.state}
        context = {"session_id": self.session_id}

        async for event in self.aca.run(input_data, context):
            yield event

        # Run UOA for utility scoring
        branches = list(self.state["branches"].values())
        for branch in branches:
            branch_nodes = [n for n in self.state["nodes"].values() if n.get("branch_id") == branch.get("id")]
            input_data = {"branch": {"id": branch.get("id"), "nodes": branch_nodes}}
            context = {"session_id": self.session_id, "preferences": {}}

            async for event in self.uoa.run(input_data, context):
                yield event

        # Update Pareto front
        from ..algorithms.pareto import ParetoOptimizer
        optimizer = ParetoOptimizer(objectives=["utility", "confidence"])

        solutions = [
            {"id": n.get("id"), "utility": n.get("utility", 0), "confidence": n.get("confidence", 0)}
            for n in self.state["nodes"].values()
            if n.get("type") == "claim"
        ]

        pareto_front = optimizer.compute_pareto_front(solutions)
        self.state = update_convergence_metrics(
            self.state,
            pareto_size=len(pareto_front),
            pareto_stability=0.8
        )

        yield {"type": "pareto_front_computed", "data": {"size": len(pareto_front)}}

    async def run_convergence_phase(self) -> AsyncGenerator[Dict[str, Any], None]:
        """Execute the convergence phase."""
        yield {"type": "convergence_started", "data": {"branch_count": len(self.state["branches"])}}

        # Create BM agents for each branch
        for branch_id, branch in self.state["branches"].items():
            if branch_id not in self.bm_agents:
                self.bm_agents[branch_id] = BranchManagerAgent(
                    agent_id=f"bm_{branch_id[:8]}",
                    branch_id=branch_id,
                    llm_client=self.llm_client,
                    streaming_callback=self._emit_event,
                )

        # Run GA for coordination
        branches_data = [
            {
                "id": b.get("id"),
                "name": b.get("name"),
                "utility_score": b.get("utility_score", 0.5),
                "confidence": 0.7,
                "risk": 0.3,
            }
            for b in self.state["branches"].values()
        ]

        input_data = {"branches": branches_data}
        context = {"session_id": self.session_id}

        async for event in self.ga.run(input_data, context):
            yield event

        # Run debate rounds
        max_rounds = 5
        for round_num in range(max_rounds):
            yield {"type": "debate_round", "data": {"round": round_num + 1}}

            # Check for oscillation
            oscillation_result = await self.convergence_controller.check_oscillation()
            if oscillation_result.get("is_oscillating"):
                yield {"type": "oscillation_detected", "data": oscillation_result}
                break

            # Run BM agents
            for branch_id, bm in self.bm_agents.items():
                branch_nodes = [n for n in self.state["nodes"].values() if n.get("branch_id") == branch_id]
                input_data = {"branch_state": {"nodes": branch_nodes}, "pending_attacks": []}
                context = {"session_id": self.session_id}

                async for event in bm.run(input_data, context):
                    yield event

        # Trigger synthesis if needed
        if len(self.state["branches"]) > 1:
            branch_ids = list(self.state["branches"].keys())
            async for event in self.trigger_synthesis(branch_ids):
                yield event

    async def _run_rec(self) -> AsyncGenerator[Dict[str, Any], None]:
        """Run REC agent to compile final output."""
        input_data = {"graph_state": self.state, "output_format": "markdown"}
        context = {"session_id": self.session_id}

        async for event in self.rec.run(input_data, context):
            yield event

    async def handle_user_input(
        self,
        message: str,
        message_type: str = "chat",
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Handle user input in synchronous mode."""
        yield {"type": "user_input_received", "data": {"message": message, "type": message_type}}

        if message_type == "constraint":
            # Add as constraint node
            node = create_node_state(
                node_id=str(uuid.uuid4()),
                node_type="constraint",
                content=message,
                layer=1,
            )
            self.state["nodes"][node["id"]] = node
            yield {"type": StreamEventType.NODE_CREATED.value, "data": {"node": node}}

        elif message_type == "directive":
            # Process as ISA query
            input_data = {"query": message, "search_depth": "basic"}
            context = {"session_id": self.session_id}
            async for event in self.isa.run(input_data, context):
                yield event

    async def trigger_synthesis(
        self,
        branch_ids: List[str],
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Trigger Hegelian dialectical synthesis between branches."""
        yield {"type": "synthesis_started", "data": {"branch_ids": branch_ids}}

        # Collect contributions from BM agents
        contributions = []
        for branch_id in branch_ids:
            if branch_id in self.bm_agents:
                contribution = await self.bm_agents[branch_id].participate_synthesis(
                    other_branches=[b for b in branch_ids if b != branch_id],
                    synthesis_type="integration"
                )
                contributions.append(contribution)

        # Create synthesis node
        synthesis_content = "Synthesis of: " + ", ".join([c.get("main_claim", "")[:50] for c in contributions])
        synthesis_node = create_node_state(
            node_id=str(uuid.uuid4()),
            node_type="synthesis",
            content=synthesis_content,
            layer=max(n.get("layer", 0) for n in self.state["nodes"].values()) + 1,
        )
        synthesis_node["metadata"]["source_branches"] = branch_ids
        synthesis_node["metadata"]["contributions"] = contributions

        self.state["nodes"][synthesis_node["id"]] = synthesis_node

        yield {"type": StreamEventType.NODE_CREATED.value, "data": {"node": synthesis_node}}
        yield {"type": "synthesis_completed", "data": {"synthesis_node_id": synthesis_node["id"]}}

    async def pause(self) -> None:
        """Pause the orchestration."""
        # Save state checkpoint
        if self.redis:
            import json
            await self.redis.set(
                f"checkpoint:{self.session_id}",
                json.dumps(self.state),
                ex=86400
            )

    async def resume(self) -> AsyncGenerator[Dict[str, Any], None]:
        """Resume paused orchestration."""
        if self.redis:
            import json
            data = await self.redis.get(f"checkpoint:{self.session_id}")
            if data:
                self.state = json.loads(data)
                yield {"type": "orchestration_resumed", "data": {"session_id": self.session_id}}

    def get_current_state(self) -> Dict[str, Any]:
        """Get the current orchestration state."""
        if not self.state:
            return {}

        return {
            "phase": self.state.get("phase", PhaseType.DIVERGENCE).value if isinstance(self.state.get("phase"), PhaseType) else self.state.get("phase"),
            "progress": self.state.get("phase_progress", 0),
            "active_agents": list(self.bm_agents.keys()),
            "branch_count": len(self.state.get("branches", {})),
            "node_count": len(self.state.get("nodes", {})),
            "convergence_metrics": self.state.get("convergence_metrics", {}),
        }


class ConvergenceController:
    """Controller for monitoring convergence and detecting oscillation."""

    def __init__(
        self,
        max_rounds: int = 10,
        similarity_threshold: float = 0.85,
        entropy_threshold: float = 0.1,
    ):
        self.max_rounds = max_rounds
        self.similarity_threshold = similarity_threshold
        self.entropy_threshold = entropy_threshold
        self.round_count = 0
        self.position_history: List[Dict[str, Any]] = []
        self.entropy_history: List[float] = []

    def record_round(self, positions: Dict[str, str], entropy: float) -> None:
        """Record a debate round."""
        self.round_count += 1
        self.position_history.append(positions)
        self.entropy_history.append(entropy)

    async def check_oscillation(self) -> Dict[str, Any]:
        """Check for oscillation patterns."""
        if self.round_count < 3:
            return {"is_oscillating": False, "trigger": None}

        # Check max rounds
        if self.round_count >= self.max_rounds:
            return {"is_oscillating": True, "trigger": "max_rounds"}

        # Check entropy stagnation
        if len(self.entropy_history) >= 3:
            recent = self.entropy_history[-3:]
            if all(abs(recent[i] - recent[i+1]) < self.entropy_threshold for i in range(len(recent)-1)):
                return {"is_oscillating": True, "trigger": "entropy_stagnation"}

        return {"is_oscillating": False, "trigger": None}

    def reset(self) -> None:
        """Reset controller state."""
        self.round_count = 0
        self.position_history = []
        self.entropy_history = []

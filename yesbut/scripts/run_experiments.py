"""
YesBut Use Case Experiments

This script runs specific use case experiments to validate the system's
end-to-end functionality with realistic scenarios.
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List
import httpx


BASE_URL = "http://localhost:8001/api/v1"


class ExperimentRunner:
    """Runs use case experiments against the YesBut API."""

    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=60.0)
        self.results: List[Dict[str, Any]] = []

    async def close(self):
        await self.client.aclose()

    async def create_session(self, title: str, goal: str, mode: str = "async") -> Dict:
        """Create a new brainstorming session."""
        response = await self.client.post(
            f"{self.base_url}/sessions",
            json={
                "title": title,
                "description": f"Experiment: {title}",
                "initial_goal": goal,
                "mode": mode,
            },
        )
        response.raise_for_status()
        return response.json()["data"]

    async def start_session(self, session_id: str) -> Dict:
        """Start a session."""
        response = await self.client.post(
            f"{self.base_url}/sessions/{session_id}/start"
        )
        response.raise_for_status()
        return response.json()["data"]

    async def get_session(self, session_id: str) -> Dict:
        """Get session details."""
        response = await self.client.get(
            f"{self.base_url}/sessions/{session_id}",
            params={"include_statistics": "true"},
        )
        response.raise_for_status()
        return response.json()["data"]

    async def transition_phase(self, session_id: str, target_phase: str) -> Dict:
        """Transition to a new phase."""
        response = await self.client.post(
            f"{self.base_url}/sessions/{session_id}/transition-phase",
            json={"target_phase": target_phase},
        )
        response.raise_for_status()
        return response.json()["data"]

    async def get_nodes(self, session_id: str) -> List[Dict]:
        """Get all nodes in a session."""
        response = await self.client.get(
            f"{self.base_url}/sessions/{session_id}/nodes"
        )
        response.raise_for_status()
        return response.json()["data"]

    async def get_statistics(self, session_id: str) -> Dict:
        """Get session statistics."""
        response = await self.client.get(
            f"{self.base_url}/sessions/{session_id}/statistics"
        )
        response.raise_for_status()
        return response.json()["data"]

    def log_result(self, experiment: str, step: str, success: bool, details: Dict = None):
        """Log experiment result."""
        result = {
            "experiment": experiment,
            "step": step,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "details": details or {},
        }
        self.results.append(result)
        status = "PASS" if success else "FAIL"
        print(f"[{status}] {experiment} - {step}")
        if details:
            print(f"       Details: {json.dumps(details, indent=2)}")


async def experiment_1_product_strategy(runner: ExperimentRunner):
    """
    Experiment 1: Product Strategy Brainstorming

    Scenario: A product manager wants to brainstorm Q1 product strategy
    """
    experiment_name = "Product Strategy Brainstorming"
    print(f"\n{'='*60}")
    print(f"Experiment 1: {experiment_name}")
    print(f"{'='*60}")

    try:
        # Step 1: Create session
        session = await runner.create_session(
            title="Product Strategy Q1 2025",
            goal="Develop a comprehensive product roadmap for Q1 2025 that balances "
                 "user growth, revenue targets, and technical debt reduction",
            mode="async",
        )
        runner.log_result(experiment_name, "Create Session", True, {"session_id": session["id"]})

        # Step 2: Start session
        session = await runner.start_session(session["id"])
        runner.log_result(experiment_name, "Start Session", session["status"] == "active")

        # Step 3: Wait for divergence phase to generate solutions
        print("       Waiting for divergence phase (simulated)...")
        await asyncio.sleep(2)

        # Step 4: Check node count (should have solutions)
        nodes = await runner.get_nodes(session["id"])
        runner.log_result(
            experiment_name,
            "Divergence Phase",
            len(nodes) >= 1,
            {"node_count": len(nodes)},
        )

        # Step 5: Transition to filtering
        result = await runner.transition_phase(session["id"], "filtering")
        runner.log_result(
            experiment_name,
            "Transition to Filtering",
            result.get("phase") == "filtering",
        )

        # Step 6: Transition to convergence
        result = await runner.transition_phase(session["id"], "convergence")
        runner.log_result(
            experiment_name,
            "Transition to Convergence",
            result.get("phase") == "convergence",
        )

        # Step 7: Get final statistics
        stats = await runner.get_statistics(session["id"])
        runner.log_result(
            experiment_name,
            "Final Statistics",
            True,
            stats,
        )

    except Exception as e:
        runner.log_result(experiment_name, "Error", False, {"error": str(e)})


async def experiment_2_architecture_decision(runner: ExperimentRunner):
    """
    Experiment 2: Technical Architecture Decision

    Scenario: An architect needs to decide on microservices vs monolith
    """
    experiment_name = "Architecture Decision"
    print(f"\n{'='*60}")
    print(f"Experiment 2: {experiment_name}")
    print(f"{'='*60}")

    try:
        # Step 1: Create session
        session = await runner.create_session(
            title="E-commerce Platform Architecture",
            goal="Determine the optimal architecture for our e-commerce platform "
                 "considering scalability, team expertise, and time-to-market",
            mode="async",
        )
        runner.log_result(experiment_name, "Create Session", True, {"session_id": session["id"]})

        # Step 2: Start session
        session = await runner.start_session(session["id"])
        runner.log_result(experiment_name, "Start Session", session["status"] == "active")

        # Step 3: Get session details
        session_details = await runner.get_session(session["id"])
        runner.log_result(
            experiment_name,
            "Get Session Details",
            session_details is not None,
            {"phase": session_details.get("phase")},
        )

    except Exception as e:
        runner.log_result(experiment_name, "Error", False, {"error": str(e)})


async def experiment_3_api_validation(runner: ExperimentRunner):
    """
    Experiment 3: API Validation

    Validates all API endpoints work correctly
    """
    experiment_name = "API Validation"
    print(f"\n{'='*60}")
    print(f"Experiment 3: {experiment_name}")
    print(f"{'='*60}")

    try:
        # Test session CRUD
        session = await runner.create_session(
            title="API Test Session",
            goal="Test API endpoints",
            mode="sync",
        )
        runner.log_result(experiment_name, "POST /sessions", True)

        # Test GET session
        session_data = await runner.get_session(session["id"])
        runner.log_result(experiment_name, "GET /sessions/{id}", session_data is not None)

        # Test list sessions
        response = await runner.client.get(f"{runner.base_url}/sessions")
        runner.log_result(experiment_name, "GET /sessions", response.status_code == 200)

        # Test update session
        response = await runner.client.patch(
            f"{runner.base_url}/sessions/{session['id']}",
            json={"title": "Updated Title"},
        )
        runner.log_result(experiment_name, "PATCH /sessions/{id}", response.status_code == 200)

        # Test node creation
        response = await runner.client.post(
            f"{runner.base_url}/sessions/{session['id']}/nodes",
            json={
                "type": "goal",
                "content": "Test goal node",
                "layer": 0,
            },
        )
        runner.log_result(experiment_name, "POST /sessions/{id}/nodes", response.status_code == 200)

        # Test delete session
        response = await runner.client.delete(f"{runner.base_url}/sessions/{session['id']}")
        runner.log_result(experiment_name, "DELETE /sessions/{id}", response.status_code == 200)

    except Exception as e:
        runner.log_result(experiment_name, "Error", False, {"error": str(e)})


async def main():
    """Run all experiments."""
    print("\n" + "="*60)
    print("YesBut Use Case Experiments")
    print("="*60)
    print(f"Started at: {datetime.now().isoformat()}")
    print(f"API Base URL: {BASE_URL}")

    runner = ExperimentRunner()

    try:
        # Run experiments
        await experiment_1_product_strategy(runner)
        await experiment_2_architecture_decision(runner)
        await experiment_3_api_validation(runner)

        # Summary
        print("\n" + "="*60)
        print("Experiment Summary")
        print("="*60)

        passed = sum(1 for r in runner.results if r["success"])
        failed = sum(1 for r in runner.results if not r["success"])

        print(f"Total Steps: {len(runner.results)}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {passed / len(runner.results) * 100:.1f}%")

        # Save results
        with open("experiment_results.json", "w") as f:
            json.dump(runner.results, f, indent=2)
        print(f"\nResults saved to: experiment_results.json")

    finally:
        await runner.close()


if __name__ == "__main__":
    asyncio.run(main())

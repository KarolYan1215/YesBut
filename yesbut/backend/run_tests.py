"""
Quick Test Script for YesBut

Run this script to verify core functionality without external dependencies.
Usage: python run_tests.py
"""

import asyncio
import sys
import os

# Ensure backend is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_algorithms():
    """Test core algorithms."""
    print("\n=== Testing Algorithms ===")
    
    # Test Pareto Optimizer
    from algorithms.pareto import ParetoOptimizer
    optimizer = ParetoOptimizer(objectives=["utility", "confidence"])
    solutions = [
        {"id": "1", "utility": 0.9, "confidence": 0.9},
        {"id": "2", "utility": 0.5, "confidence": 0.5},
        {"id": "3", "utility": 0.3, "confidence": 0.95},
    ]
    front = optimizer.compute_pareto_front(solutions)
    print(f"  Pareto Optimizer: OK (front size: {len(front)})")
    
    # Test Sensitivity Analyzer
    from algorithms.sensitivity import SensitivityAnalyzer
    graph = {
        "nodes": [
            {"id": "goal", "type": "goal", "content": "Test", "metadata": {"confidence": 1.0}},
            {"id": "claim1", "type": "claim", "content": "Claim", "metadata": {"confidence": 0.8}},
        ],
        "edges": [{"source_id": "goal", "target_id": "claim1", "type": "decompose"}],
    }
    analyzer = SensitivityAnalyzer(graph=graph, goal_node_id="goal", monte_carlo_samples=10)
    result = analyzer.analyze()
    print(f"  Sensitivity Analyzer: OK (stability: {result['stability_score']:.2f})")
    
    # Test Path Analyzer
    from algorithms.path_analysis import PathAnalyzer
    path_analyzer = PathAnalyzer(graph=graph, goal_node_id="goal")
    path_result = path_analyzer.analyze()
    print(f"  Path Analyzer: OK (paths: {path_result['total_paths']})")
    
    # Test Oscillation Detector
    from algorithms.oscillation import OscillationDetector
    detector = OscillationDetector()
    detector.record_round({"branch_1": "Position A"}, 0.5)
    detector.record_round({"branch_1": "Position B"}, 0.4)
    print(f"  Oscillation Detector: OK (rounds: {len(detector.entropy_history)})")
    
    print("  All algorithm tests passed!")


async def test_services():
    """Test service layer."""
    print("\n=== Testing Services ===")
    
    from app.services.session_service import get_session_service
    from app.services.graph_service import get_graph_service
    
    # Test Session Service
    session_service = get_session_service()
    session = await session_service.create_session(
        user_id="test_user",
        title="Test Session",
        initial_goal="Test the system",
    )
    print(f"  Session created: {session['id'][:8]}...")
    
    retrieved = await session_service.get_session(session["id"])
    assert retrieved is not None
    print(f"  Session retrieved: OK")
    
    # Test Graph Service
    graph_service = get_graph_service(session_service=session_service)
    node = await graph_service.create_node(
        session_id=session["id"],
        node_type="claim",
        content="Test claim",
    )
    print(f"  Node created: {node['id'][:8]}...")
    
    stats = await graph_service.get_graph_statistics(session["id"])
    print(f"  Graph stats: {stats['node_count']} nodes, {stats['branch_count']} branches")
    
    # Cleanup
    await session_service.delete_session(session["id"])
    print("  Session deleted: OK")
    
    print("  All service tests passed!")


async def test_agents():
    """Test agent functionality."""
    print("\n=== Testing Agents ===")
    
    # Test RPA
    from agents.rpa.agent import RequirementParsingAgent
    rpa = RequirementParsingAgent(agent_id="test_rpa")
    parsed = rpa._simple_parse("Build a web application for task management")
    print(f"  RPA parse: OK (goal: {parsed['main_goal'][:30]}...)")
    
    # Test GEN
    from agents.gen.agent import GeneratorAgent
    gen = GeneratorAgent(agent_id="test_gen")
    solution = gen._generate_mock_solution("high_temperature")
    features = gen.compute_features(solution)
    print(f"  GEN generate: OK (risk: {features['risk_level']:.2f})")
    
    # Test ACA
    from agents.aca.agent import AuditComplianceAgent
    aca = AuditComplianceAgent(agent_id="test_aca")
    violation = aca._violates_constraint("Use Python", "Must use Python")
    print(f"  ACA validate: OK (violation: {violation})")
    
    # Test BM
    from agents.bm.agent import BranchManagerAgent
    bm = BranchManagerAgent(agent_id="test_bm", branch_id="branch_1")
    utility = bm._default_utility({"confidence": 0.8, "utility": 0.6})
    print(f"  BM utility: OK (value: {utility:.2f})")
    
    # Test GA
    from agents.ga.agent import GameArbiterAgent
    ga = GameArbiterAgent(agent_id="test_ga")
    branches = [{"id": "1", "utility_score": 0.8, "confidence": 0.9, "risk": 0.1}]
    front = await ga.compute_pareto_front(branches)
    print(f"  GA pareto: OK (front: {len(front)})")
    
    # Test UOA
    from agents.uoa.agent import UtilityOptimizationAgent
    uoa = UtilityOptimizationAgent(agent_id="test_uoa")
    utility_fn = uoa.generate_utility_function({"weights": {"risk": 0.5, "value": 0.5}})
    score = utility_fn({"risk": 0.5, "value": 0.8, "confidence": 0.9})
    print(f"  UOA utility fn: OK (score: {score:.2f})")
    
    # Test REC
    from agents.rec.agent import ReverseEngineeringCompilerAgent
    rec = ReverseEngineeringCompilerAgent(agent_id="test_rec")
    graph_state = {
        "nodes": {"goal": {"id": "goal", "type": "goal", "content": "Test", "utility": 1.0, "confidence": 1.0}},
        "edges": {},
    }
    path = await rec.extract_winning_path(graph_state)
    print(f"  REC extract: OK (path length: {len(path)})")
    
    print("  All agent tests passed!")


def main():
    """Run all tests."""
    print("=" * 50)
    print("YesBut Quick Test Suite")
    print("=" * 50)
    
    try:
        test_algorithms()
        asyncio.run(test_services())
        asyncio.run(test_agents())
        
        print("\n" + "=" * 50)
        print("ALL TESTS PASSED!")
        print("=" * 50)
        return 0
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

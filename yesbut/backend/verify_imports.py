"""
Verify imports work correctly.
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing imports...")

# Test config
try:
    from app.config import Settings, get_settings, get_anthropic_config
    print("  app.config: OK")
except Exception as e:
    print(f"  app.config: FAILED - {e}")

# Test algorithms
try:
    from algorithms.pareto import ParetoOptimizer
    from algorithms.oscillation import SemanticEntropyCalculator, OscillationDetector
    from algorithms.sensitivity import SensitivityAnalyzer
    from algorithms.path_analysis import PathAnalyzer
    print("  algorithms: OK")
except Exception as e:
    print(f"  algorithms: FAILED - {e}")

# Test agents
try:
    from agents.base.agent import BaseAgent
    from agents.rpa.agent import RequirementParsingAgent, BayesianPrior
    from agents.gen.agent import GeneratorAgent, FeatureSpace, MAPElitesArchive
    from agents.isa.agent import InformationScoutAgent
    from agents.aca.agent import AuditComplianceAgent
    from agents.bm.agent import BranchManagerAgent
    from agents.ga.agent import GameArbiterAgent
    from agents.uoa.agent import UtilityOptimizationAgent
    from agents.rec.agent import ReverseEngineeringCompilerAgent
    print("  agents: OK")
except Exception as e:
    print(f"  agents: FAILED - {e}")

# Test services
try:
    from app.services.session_service import SessionService, get_session_service
    from app.services.graph_service import GraphService, get_graph_service
    print("  services: OK")
except Exception as e:
    print(f"  services: FAILED - {e}")

print("\nAll imports verified!")

"""
Agents Package

Multi-agent system for collaborative brainstorming.

Agent Types:
    RPA: Requirement Parsing Agent - Parses user requirements into structured goals
    GEN: Generator Agent - Generates diverse solutions using QD algorithms
    ISA: Information Scout Agent - Retrieves external information via MCP
    ACA: Audit & Compliance Agent - Validates claims and checks compliance
    BM: Branch Manager Agent - Manages reasoning branches
    GA: Game Arbiter Agent - Resolves conflicts using game theory
    UOA: Utility Optimization Agent - Optimizes utility functions
    REC: Reverse Engineering Compiler - Synthesizes final solutions

Modules:
    orchestrator: LangGraph-based agent orchestration
    convergence_controller: Convergence detection and control
    state: Shared agent state definitions
    streaming: Agent output streaming utilities
    base: Base agent class and utilities

@package agents
"""

__all__ = [
    "orchestrator",
    "convergence_controller",
    "state",
    "streaming",
    "base",
    "rpa",
    "gen",
    "isa",
    "aca",
    "bm",
    "ga",
    "uoa",
    "rec",
]

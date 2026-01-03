"""
Unit tests for services module.
"""

import pytest
import asyncio
from typing import Dict, Any

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.services.session_service import SessionService, get_session_service
from app.services.graph_service import GraphService, get_graph_service


class TestSessionService:
    """Tests for SessionService class."""

    @pytest.fixture
    def service(self):
        """Create a session service instance."""
        return get_session_service()

    @pytest.mark.asyncio
    async def test_create_session(self, service):
        """Test session creation."""
        session = await service.create_session(
            user_id="test_user",
            title="Test Session",
            description="A test session",
            initial_goal="Test the system",
            mode="sync",
        )

        assert session["id"] is not None
        assert session["title"] == "Test Session"
        assert session["status"] == "draft"
        assert session["phase"] == "divergence"
        assert len(session["nodes"]) == 1  # Goal node
        assert len(session["branches"]) == 1  # Main branch

    @pytest.mark.asyncio
    async def test_get_session(self, service):
        """Test session retrieval."""
        created = await service.create_session(
            user_id="test_user",
            title="Test Session",
            initial_goal="Test goal",
        )

        retrieved = await service.get_session(created["id"])

        assert retrieved is not None
        assert retrieved["id"] == created["id"]
        assert retrieved["title"] == created["title"]

    @pytest.mark.asyncio
    async def test_get_session_not_found(self, service):
        """Test session retrieval for non-existent session."""
        retrieved = await service.get_session("non_existent_id")
        assert retrieved is None

    @pytest.mark.asyncio
    async def test_update_session(self, service):
        """Test session update."""
        created = await service.create_session(
            user_id="test_user",
            title="Original Title",
            initial_goal="Test goal",
        )

        updated = await service.update_session(
            created["id"],
            {"title": "Updated Title"}
        )

        assert updated["title"] == "Updated Title"

    @pytest.mark.asyncio
    async def test_delete_session(self, service):
        """Test session deletion."""
        created = await service.create_session(
            user_id="test_user",
            title="To Delete",
            initial_goal="Test goal",
        )

        result = await service.delete_session(created["id"])
        assert result is True

        retrieved = await service.get_session(created["id"])
        assert retrieved is None

    @pytest.mark.asyncio
    async def test_start_session(self, service):
        """Test starting a session."""
        created = await service.create_session(
            user_id="test_user",
            title="Test Session",
            initial_goal="Test goal",
        )

        started = await service.start_session(created["id"])

        assert started["status"] == "active"

    @pytest.mark.asyncio
    async def test_pause_resume_session(self, service):
        """Test pausing and resuming a session."""
        created = await service.create_session(
            user_id="test_user",
            title="Test Session",
            initial_goal="Test goal",
        )

        await service.start_session(created["id"])
        paused = await service.pause_session(created["id"])
        assert paused["status"] == "paused"

        resumed = await service.resume_session(created["id"])
        assert resumed["status"] == "active"

    @pytest.mark.asyncio
    async def test_transition_phase(self, service):
        """Test phase transition."""
        created = await service.create_session(
            user_id="test_user",
            title="Test Session",
            initial_goal="Test goal",
        )

        result = await service.transition_phase(
            created["id"],
            "filtering",
            force=True
        )

        assert result["previous_phase"] == "divergence"
        assert result["current_phase"] == "filtering"

    @pytest.mark.asyncio
    async def test_toggle_mode(self, service):
        """Test mode toggle."""
        created = await service.create_session(
            user_id="test_user",
            title="Test Session",
            initial_goal="Test goal",
            mode="sync",
        )

        toggled = await service.toggle_mode(created["id"])
        assert toggled["mode"] == "async"

        toggled_back = await service.toggle_mode(created["id"])
        assert toggled_back["mode"] == "sync"


class TestGraphService:
    """Tests for GraphService class."""

    @pytest.fixture
    def services(self):
        """Create service instances."""
        session_service = get_session_service()
        graph_service = get_graph_service(session_service=session_service)
        return session_service, graph_service

    @pytest.mark.asyncio
    async def test_create_node(self, services):
        """Test node creation."""
        session_service, graph_service = services

        session = await session_service.create_session(
            user_id="test_user",
            title="Test Session",
            initial_goal="Test goal",
        )

        node = await graph_service.create_node(
            session_id=session["id"],
            node_type="claim",
            content="Test claim",
            layer=1,
        )

        assert node["id"] is not None
        assert node["type"] == "claim"
        assert node["content"] == "Test claim"

    @pytest.mark.asyncio
    async def test_get_node(self, services):
        """Test node retrieval."""
        session_service, graph_service = services

        session = await session_service.create_session(
            user_id="test_user",
            title="Test Session",
            initial_goal="Test goal",
        )

        created = await graph_service.create_node(
            session_id=session["id"],
            node_type="claim",
            content="Test claim",
        )

        retrieved = await graph_service.get_node(session["id"], created["id"])

        assert retrieved is not None
        assert retrieved["id"] == created["id"]

    @pytest.mark.asyncio
    async def test_update_node(self, services):
        """Test node update."""
        session_service, graph_service = services

        session = await session_service.create_session(
            user_id="test_user",
            title="Test Session",
            initial_goal="Test goal",
        )

        created = await graph_service.create_node(
            session_id=session["id"],
            node_type="claim",
            content="Original content",
        )

        updated = await graph_service.update_node(
            session["id"],
            created["id"],
            {"content": "Updated content", "confidence": 0.9}
        )

        assert updated["content"] == "Updated content"
        assert updated["confidence"] == 0.9

    @pytest.mark.asyncio
    async def test_delete_node(self, services):
        """Test node deletion."""
        session_service, graph_service = services

        session = await session_service.create_session(
            user_id="test_user",
            title="Test Session",
            initial_goal="Test goal",
        )

        created = await graph_service.create_node(
            session_id=session["id"],
            node_type="claim",
            content="To delete",
        )

        result = await graph_service.delete_node(session["id"], created["id"])
        assert result is True

        retrieved = await graph_service.get_node(session["id"], created["id"])
        assert retrieved is None

    @pytest.mark.asyncio
    async def test_create_edge(self, services):
        """Test edge creation."""
        session_service, graph_service = services

        session = await session_service.create_session(
            user_id="test_user",
            title="Test Session",
            initial_goal="Test goal",
        )

        # Get goal node
        goal_node_id = list(session["nodes"].keys())[0]

        # Create claim node
        claim = await graph_service.create_node(
            session_id=session["id"],
            node_type="claim",
            content="Test claim",
        )

        # Create edge
        edge = await graph_service.create_edge(
            session_id=session["id"],
            source_id=goal_node_id,
            target_id=claim["id"],
            edge_type="decompose",
        )

        assert edge["id"] is not None
        assert edge["source_id"] == goal_node_id
        assert edge["target_id"] == claim["id"]
        assert edge["type"] == "decompose"

    @pytest.mark.asyncio
    async def test_create_branch(self, services):
        """Test branch creation."""
        session_service, graph_service = services

        session = await session_service.create_session(
            user_id="test_user",
            title="Test Session",
            initial_goal="Test goal",
        )

        branch = await graph_service.create_branch(
            session_id=session["id"],
            name="alternative",
        )

        assert branch["id"] is not None
        assert branch["name"] == "alternative"
        assert branch["status"] == "active"

    @pytest.mark.asyncio
    async def test_fork_branch(self, services):
        """Test branch forking."""
        session_service, graph_service = services

        session = await session_service.create_session(
            user_id="test_user",
            title="Test Session",
            initial_goal="Test goal",
        )

        main_branch_id = list(session["branches"].keys())[0]
        goal_node_id = list(session["nodes"].keys())[0]

        forked = await graph_service.fork_branch(
            session_id=session["id"],
            source_branch_id=main_branch_id,
            fork_node_id=goal_node_id,
            new_branch_name="forked",
        )

        assert forked["name"] == "forked"
        assert forked["parent_branch_id"] == main_branch_id

    @pytest.mark.asyncio
    async def test_get_graph_statistics(self, services):
        """Test graph statistics."""
        session_service, graph_service = services

        session = await session_service.create_session(
            user_id="test_user",
            title="Test Session",
            initial_goal="Test goal",
        )

        # Add some nodes
        await graph_service.create_node(
            session_id=session["id"],
            node_type="claim",
            content="Claim 1",
        )
        await graph_service.create_node(
            session_id=session["id"],
            node_type="fact",
            content="Fact 1",
        )

        stats = await graph_service.get_graph_statistics(session["id"])

        assert stats["node_count"] >= 3  # Goal + 2 created
        assert "node_types" in stats
        assert "goal" in stats["node_types"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""
Node API Integration Tests

Tests for /api/v1/sessions/{session_id}/nodes endpoints.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch

from app.main import app


@pytest.fixture
def mock_graph_service():
    """Mock GraphService for API tests."""
    with patch('app.api.v1.nodes.get_service') as mock:
        service = AsyncMock()
        mock.return_value = service
        yield service


@pytest.fixture
async def client():
    """Create async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


class TestNodeCreate:
    """Tests for POST /api/v1/sessions/{sid}/nodes"""

    @pytest.mark.asyncio
    async def test_create_goal_node(self, client, mock_graph_service):
        """TC-N001: Create goal node."""
        mock_graph_service.create_node.return_value = {
            "id": "node-goal-1",
            "type": "goal",
            "content": "Develop product strategy",
            "layer": 0,
            "confidence": 1.0,
        }

        response = await client.post(
            "/api/v1/sessions/session-123/nodes",
            json={
                "type": "goal",
                "content": "Develop product strategy",
                "layer": 0,
                "confidence": 1.0,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["type"] == "goal"

    @pytest.mark.asyncio
    async def test_create_claim_node_with_parent(self, client, mock_graph_service):
        """TC-N002: Create claim node with parent."""
        mock_graph_service.create_node.return_value = {
            "id": "node-claim-1",
            "type": "claim",
            "content": "Focus on user acquisition",
            "layer": 1,
            "parent_id": "node-goal-1",
            "confidence": 0.8,
        }

        response = await client.post(
            "/api/v1/sessions/session-123/nodes",
            json={
                "type": "claim",
                "content": "Focus on user acquisition",
                "layer": 1,
                "parent_id": "node-goal-1",
                "confidence": 0.8,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["type"] == "claim"
        assert data["data"]["parent_id"] == "node-goal-1"

    @pytest.mark.asyncio
    async def test_create_fact_node(self, client, mock_graph_service):
        """TC-N003: Create fact node."""
        mock_graph_service.create_node.return_value = {
            "id": "node-fact-1",
            "type": "fact",
            "content": "Market research shows 30% growth",
            "layer": 2,
            "confidence": 0.95,
        }

        response = await client.post(
            "/api/v1/sessions/session-123/nodes",
            json={
                "type": "fact",
                "content": "Market research shows 30% growth",
                "layer": 2,
                "confidence": 0.95,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["type"] == "fact"

    @pytest.mark.asyncio
    async def test_create_constraint_node(self, client, mock_graph_service):
        """TC-N004: Create constraint node."""
        mock_graph_service.create_node.return_value = {
            "id": "node-constraint-1",
            "type": "constraint",
            "content": "Budget limit: $500K",
            "layer": 1,
            "confidence": 1.0,
        }

        response = await client.post(
            "/api/v1/sessions/session-123/nodes",
            json={
                "type": "constraint",
                "content": "Budget limit: $500K",
                "layer": 1,
                "confidence": 1.0,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["type"] == "constraint"

    @pytest.mark.asyncio
    async def test_create_node_invalid_type(self, client, mock_graph_service):
        """TC-N005: Reject invalid node type."""
        response = await client.post(
            "/api/v1/sessions/session-123/nodes",
            json={
                "type": "invalid_type",
                "content": "Test content",
                "layer": 1,
            },
        )

        assert response.status_code == 422


class TestNodeGet:
    """Tests for GET /api/v1/sessions/{sid}/nodes/{nid}"""

    @pytest.mark.asyncio
    async def test_get_node_success(self, client, mock_graph_service):
        """TC-N006: Return node details."""
        mock_graph_service.get_node.return_value = {
            "id": "node-123",
            "type": "claim",
            "content": "Test claim",
            "layer": 1,
            "confidence": 0.8,
        }

        response = await client.get("/api/v1/sessions/session-123/nodes/node-123")

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["id"] == "node-123"


class TestNodeList:
    """Tests for GET /api/v1/sessions/{sid}/nodes"""

    @pytest.mark.asyncio
    async def test_list_nodes_by_type(self, client, mock_graph_service):
        """TC-N007: List nodes with type filter."""
        mock_graph_service.list_nodes.return_value = [
            {"id": "node-1", "type": "claim", "content": "Claim 1"},
            {"id": "node-2", "type": "claim", "content": "Claim 2"},
        ]

        response = await client.get(
            "/api/v1/sessions/session-123/nodes?node_type=claim"
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 2

    @pytest.mark.asyncio
    async def test_list_nodes_by_branch(self, client, mock_graph_service):
        """TC-N008: List nodes with branch filter."""
        mock_graph_service.list_nodes.return_value = [
            {"id": "node-1", "type": "claim", "branch_id": "branch-1"},
        ]

        response = await client.get(
            "/api/v1/sessions/session-123/nodes?branch_id=branch-1"
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1


class TestNodeUpdate:
    """Tests for PATCH /api/v1/sessions/{sid}/nodes/{nid}"""

    @pytest.mark.asyncio
    async def test_update_node_content(self, client, mock_graph_service):
        """TC-N009: Update node content."""
        mock_graph_service.update_node.return_value = {
            "id": "node-123",
            "content": "Updated content",
        }

        response = await client.patch(
            "/api/v1/sessions/session-123/nodes/node-123",
            json={"content": "Updated content"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["content"] == "Updated content"

    @pytest.mark.asyncio
    async def test_update_node_confidence(self, client, mock_graph_service):
        """TC-N010: Update node confidence."""
        mock_graph_service.update_node.return_value = {
            "id": "node-123",
            "confidence": 0.9,
        }

        response = await client.patch(
            "/api/v1/sessions/session-123/nodes/node-123",
            json={"confidence": 0.9},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["confidence"] == 0.9


class TestNodeDelete:
    """Tests for DELETE /api/v1/sessions/{sid}/nodes/{nid}"""

    @pytest.mark.asyncio
    async def test_delete_node_success(self, client, mock_graph_service):
        """TC-N011: Delete node and edges."""
        mock_graph_service.delete_node.return_value = True

        response = await client.delete(
            "/api/v1/sessions/session-123/nodes/node-123"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestNodeTraversal:
    """Tests for node traversal operations."""

    @pytest.mark.asyncio
    async def test_get_ancestors(self, client, mock_graph_service):
        """TC-N012: Return ancestor nodes."""
        mock_graph_service.get_ancestors.return_value = [
            {"id": "node-parent", "type": "claim"},
            {"id": "node-grandparent", "type": "goal"},
        ]

        response = await client.get(
            "/api/v1/sessions/session-123/nodes/node-123/ancestors"
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 2

    @pytest.mark.asyncio
    async def test_get_descendants(self, client, mock_graph_service):
        """TC-N013: Return descendant nodes."""
        mock_graph_service.get_descendants.return_value = [
            {"id": "node-child-1", "type": "claim"},
            {"id": "node-child-2", "type": "fact"},
        ]

        response = await client.get(
            "/api/v1/sessions/session-123/nodes/node-123/descendants"
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 2

    @pytest.mark.asyncio
    async def test_get_path_to_root(self, client, mock_graph_service):
        """TC-N014: Return path to root."""
        mock_graph_service.get_path_to_root.return_value = [
            {"id": "node-123", "type": "fact"},
            {"id": "node-claim", "type": "claim"},
            {"id": "node-goal", "type": "goal"},
        ]

        response = await client.get(
            "/api/v1/sessions/session-123/nodes/node-123/path-to-root"
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 3
        assert data["data"][-1]["type"] == "goal"

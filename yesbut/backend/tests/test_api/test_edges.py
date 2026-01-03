"""
Edge API Integration Tests

Tests for /api/v1/sessions/{session_id}/edges endpoints.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch

from app.main import app


@pytest.fixture
def mock_graph_service():
    """Mock GraphService for API tests."""
    with patch('app.api.v1.edges.get_service') as mock:
        service = AsyncMock()
        mock.return_value = service
        yield service


@pytest.fixture
async def client():
    """Create async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


class TestEdgeCreate:
    """Tests for POST /api/v1/sessions/{sid}/edges"""

    @pytest.mark.asyncio
    async def test_create_support_edge(self, client, mock_graph_service):
        """TC-E001: Create support edge."""
        mock_graph_service.create_edge.return_value = {
            "id": "edge-1",
            "type": "support",
            "source_id": "node-fact-1",
            "target_id": "node-claim-1",
            "weight": 0.8,
        }

        response = await client.post(
            "/api/v1/sessions/session-123/edges",
            json={
                "type": "support",
                "source_id": "node-fact-1",
                "target_id": "node-claim-1",
                "weight": 0.8,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["type"] == "support"

    @pytest.mark.asyncio
    async def test_create_attack_edge(self, client, mock_graph_service):
        """TC-E002: Create attack edge."""
        mock_graph_service.create_edge.return_value = {
            "id": "edge-2",
            "type": "attack",
            "source_id": "node-fact-2",
            "target_id": "node-claim-1",
            "weight": 0.7,
        }

        response = await client.post(
            "/api/v1/sessions/session-123/edges",
            json={
                "type": "attack",
                "source_id": "node-fact-2",
                "target_id": "node-claim-1",
                "weight": 0.7,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["type"] == "attack"

    @pytest.mark.asyncio
    async def test_create_decompose_edge(self, client, mock_graph_service):
        """TC-E003: Create decompose edge."""
        mock_graph_service.create_edge.return_value = {
            "id": "edge-3",
            "type": "decompose",
            "source_id": "node-goal-1",
            "target_id": "node-claim-1",
        }

        response = await client.post(
            "/api/v1/sessions/session-123/edges",
            json={
                "type": "decompose",
                "source_id": "node-goal-1",
                "target_id": "node-claim-1",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["type"] == "decompose"

    @pytest.mark.asyncio
    async def test_reject_self_loop_edge(self, client, mock_graph_service):
        """TC-E004: Reject self-loop edge."""
        mock_graph_service.create_edge.side_effect = ValueError(
            "Self-loop edges are not allowed"
        )

        response = await client.post(
            "/api/v1/sessions/session-123/edges",
            json={
                "type": "support",
                "source_id": "node-1",
                "target_id": "node-1",
            },
        )

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_reject_duplicate_edge(self, client, mock_graph_service):
        """TC-E005: Reject duplicate edge."""
        mock_graph_service.create_edge.side_effect = ValueError(
            "Edge already exists"
        )

        response = await client.post(
            "/api/v1/sessions/session-123/edges",
            json={
                "type": "support",
                "source_id": "node-1",
                "target_id": "node-2",
            },
        )

        assert response.status_code == 400


class TestEdgeList:
    """Tests for GET /api/v1/sessions/{sid}/edges"""

    @pytest.mark.asyncio
    async def test_list_edges_by_type(self, client, mock_graph_service):
        """TC-E006: List edges with type filter."""
        mock_graph_service.list_edges.return_value = [
            {"id": "edge-1", "type": "support", "source_id": "n1", "target_id": "n2"},
            {"id": "edge-2", "type": "support", "source_id": "n3", "target_id": "n4"},
        ]

        response = await client.get(
            "/api/v1/sessions/session-123/edges?edge_type=support"
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 2


class TestEdgeDelete:
    """Tests for DELETE /api/v1/sessions/{sid}/edges/{eid}"""

    @pytest.mark.asyncio
    async def test_delete_edge_success(self, client, mock_graph_service):
        """TC-E007: Delete edge."""
        mock_graph_service.delete_edge.return_value = True

        response = await client.delete(
            "/api/v1/sessions/session-123/edges/edge-123"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

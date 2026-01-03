"""
Session API Integration Tests

Tests for /api/v1/sessions endpoints.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch, MagicMock

from app.main import app


@pytest.fixture
def mock_session_service():
    """Mock SessionService for API tests."""
    with patch('app.api.v1.sessions.get_service') as mock:
        service = AsyncMock()
        mock.return_value = service
        yield service


@pytest.fixture
async def client():
    """Create async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


class TestSessionCreate:
    """Tests for POST /api/v1/sessions"""

    @pytest.mark.asyncio
    async def test_create_session_success(self, client, mock_session_service):
        """TC-S001: Create session with valid data."""
        mock_session_service.create_session.return_value = {
            "id": "session-123",
            "title": "Test Session",
            "status": "draft",
            "phase": "divergence",
            "mode": "async",
        }

        response = await client.post(
            "/api/v1/sessions",
            json={
                "title": "Test Session",
                "description": "Test description",
                "initial_goal": "Test goal",
                "mode": "async",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == "session-123"

    @pytest.mark.asyncio
    async def test_create_session_empty_title(self, client, mock_session_service):
        """TC-S002: Reject empty title."""
        response = await client.post(
            "/api/v1/sessions",
            json={
                "title": "",
                "initial_goal": "Test goal",
                "mode": "async",
            },
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_session_invalid_mode(self, client, mock_session_service):
        """TC-S003: Reject invalid mode."""
        response = await client.post(
            "/api/v1/sessions",
            json={
                "title": "Test Session",
                "initial_goal": "Test goal",
                "mode": "invalid",
            },
        )

        assert response.status_code == 422


class TestSessionGet:
    """Tests for GET /api/v1/sessions/{id}"""

    @pytest.mark.asyncio
    async def test_get_session_success(self, client, mock_session_service):
        """TC-S004: Return session details."""
        mock_session_service.get_session.return_value = {
            "id": "session-123",
            "title": "Test Session",
            "status": "active",
            "phase": "divergence",
        }

        response = await client.get("/api/v1/sessions/session-123")

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["id"] == "session-123"

    @pytest.mark.asyncio
    async def test_get_session_not_found(self, client, mock_session_service):
        """TC-S005: Return 404 for non-existent session."""
        mock_session_service.get_session.return_value = None

        response = await client.get("/api/v1/sessions/nonexistent")

        assert response.status_code == 404


class TestSessionList:
    """Tests for GET /api/v1/sessions"""

    @pytest.mark.asyncio
    async def test_list_sessions_success(self, client, mock_session_service):
        """TC-S006: List sessions with pagination."""
        mock_session_service.list_sessions.return_value = {
            "items": [
                {"id": "session-1", "title": "Session 1"},
                {"id": "session-2", "title": "Session 2"},
            ],
            "total": 2,
            "skip": 0,
            "limit": 20,
        }

        response = await client.get("/api/v1/sessions?skip=0&limit=20")

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]["items"]) == 2


class TestSessionUpdate:
    """Tests for PATCH /api/v1/sessions/{id}"""

    @pytest.mark.asyncio
    async def test_update_session_title(self, client, mock_session_service):
        """TC-S007: Update session title."""
        mock_session_service.update_session.return_value = {
            "id": "session-123",
            "title": "Updated Title",
        }

        response = await client.patch(
            "/api/v1/sessions/session-123",
            json={"title": "Updated Title"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["title"] == "Updated Title"


class TestSessionDelete:
    """Tests for DELETE /api/v1/sessions/{id}"""

    @pytest.mark.asyncio
    async def test_delete_session_success(self, client, mock_session_service):
        """TC-S008: Delete session."""
        mock_session_service.delete_session.return_value = None

        response = await client.delete("/api/v1/sessions/session-123")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestSessionLifecycle:
    """Tests for session lifecycle operations."""

    @pytest.mark.asyncio
    async def test_start_session(self, client, mock_session_service):
        """TC-S009: Start draft session."""
        mock_session_service.start_session.return_value = {
            "id": "session-123",
            "status": "active",
        }

        response = await client.post("/api/v1/sessions/session-123/start")

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["status"] == "active"

    @pytest.mark.asyncio
    async def test_pause_session(self, client, mock_session_service):
        """TC-S010: Pause active session."""
        mock_session_service.pause_session.return_value = {
            "id": "session-123",
            "status": "paused",
        }

        response = await client.post("/api/v1/sessions/session-123/pause")

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["status"] == "paused"

    @pytest.mark.asyncio
    async def test_resume_session(self, client, mock_session_service):
        """TC-S011: Resume paused session."""
        mock_session_service.resume_session.return_value = {
            "id": "session-123",
            "status": "active",
        }

        response = await client.post("/api/v1/sessions/session-123/resume")

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["status"] == "active"

    @pytest.mark.asyncio
    async def test_complete_session(self, client, mock_session_service):
        """TC-S012: Complete session."""
        mock_session_service.complete_session.return_value = {
            "id": "session-123",
            "status": "completed",
        }

        response = await client.post("/api/v1/sessions/session-123/complete")

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["status"] == "completed"


class TestSessionMode:
    """Tests for session mode operations."""

    @pytest.mark.asyncio
    async def test_toggle_mode(self, client, mock_session_service):
        """TC-S013: Toggle sync/async mode."""
        mock_session_service.toggle_mode.return_value = {
            "id": "session-123",
            "mode": "sync",
        }

        response = await client.post("/api/v1/sessions/session-123/toggle-mode")

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["mode"] == "sync"


class TestSessionPhase:
    """Tests for session phase operations."""

    @pytest.mark.asyncio
    async def test_transition_phase(self, client, mock_session_service):
        """TC-S014: Transition divergence -> filtering."""
        mock_session_service.transition_phase.return_value = {
            "id": "session-123",
            "phase": "filtering",
            "previous_phase": "divergence",
        }

        response = await client.post(
            "/api/v1/sessions/session-123/transition-phase",
            json={"target_phase": "filtering"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["phase"] == "filtering"


class TestSessionStatistics:
    """Tests for session statistics."""

    @pytest.mark.asyncio
    async def test_get_statistics(self, client, mock_session_service):
        """TC-S015: Return session statistics."""
        mock_session_service.get_session_statistics.return_value = {
            "node_count": 50,
            "edge_count": 75,
            "branch_count": 3,
            "phase_durations": {
                "divergence": 120,
                "filtering": 60,
            },
        }

        response = await client.get("/api/v1/sessions/session-123/statistics")

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["node_count"] == 50

"""
Pytest Configuration and Fixtures

Provides shared fixtures for all tests including:
- Database session fixtures
- Redis client fixtures
- Test data factories
- Mock LLM clients
"""

import asyncio
import pytest
from typing import AsyncGenerator, Generator
from unittest.mock import MagicMock, AsyncMock


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """
    Create an event loop for the test session.

    Yields:
        asyncio.AbstractEventLoop: Event loop for async tests
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_settings():
    """
    Create mock settings for testing.

    Returns:
        MagicMock: Mock settings object
    """
    from app.config import Settings, DatabaseSettings, RedisSettings, LLMSettings

    settings = Settings(
        app_name="YesBut-Test",
        debug=True,
        environment="test",
        secret_key="test-secret-key-for-testing-only",
        database=DatabaseSettings(
            host="localhost",
            port=5432,
            user="test",
            password="test",
            name="yesbut_test",
        ),
        redis=RedisSettings(
            host="localhost",
            port=6379,
            db=15,  # Use separate DB for tests
        ),
        llm=LLMSettings(
            provider="anthropic",
            model="claude-3-5-sonnet-20241022",
            api_key="1",
            api_base="http://localhost:8000",
        ),
    )
    return settings


@pytest.fixture
def mock_llm_client():
    """
    Create a mock LLM client for testing.

    Returns:
        AsyncMock: Mock LLM client
    """
    client = AsyncMock()
    client.messages.create = AsyncMock(return_value=MagicMock(
        content=[MagicMock(text="Mock LLM response")]
    ))
    return client


@pytest.fixture
def mock_redis_client():
    """
    Create a mock Redis client for testing.

    Returns:
        AsyncMock: Mock Redis client
    """
    client = AsyncMock()
    client.get = AsyncMock(return_value=None)
    client.set = AsyncMock(return_value=True)
    client.delete = AsyncMock(return_value=1)
    client.exists = AsyncMock(return_value=0)
    client.expire = AsyncMock(return_value=True)
    return client


@pytest.fixture
def sample_node_data():
    """
    Create sample node data for testing.

    Returns:
        dict: Sample node data
    """
    return {
        "id": "test-node-001",
        "type": "ClaimNode",
        "label": "Test Claim",
        "layer": 1,
        "confidence": 0.85,
        "data": {
            "reasoning": "This is a test reasoning",
            "validity": 0.9,
            "utility": 0.8,
            "novelty": 0.7,
        },
    }


@pytest.fixture
def sample_edge_data():
    """
    Create sample edge data for testing.

    Returns:
        dict: Sample edge data
    """
    return {
        "id": "test-edge-001",
        "source_id": "test-node-001",
        "target_id": "test-node-002",
        "type": "support",
        "weight": 0.8,
    }


@pytest.fixture
def sample_session_data():
    """
    Create sample session data for testing.

    Returns:
        dict: Sample session data
    """
    return {
        "id": "test-session-001",
        "title": "Test Brainstorming Session",
        "description": "A test session for unit testing",
        "mode": "async",
        "phase": "divergence",
    }

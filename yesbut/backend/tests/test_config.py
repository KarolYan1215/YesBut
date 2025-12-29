"""
Tests for Application Configuration Module

Tests configuration loading, validation, and URL construction.
"""

import pytest
from unittest.mock import patch
import os


class TestDatabaseSettings:
    """Tests for DatabaseSettings class."""

    def test_url_construction(self):
        """Test PostgreSQL URL construction."""
        from app.config import DatabaseSettings

        settings = DatabaseSettings(
            host="localhost",
            port=5432,
            user="testuser",
            password="testpass",
            name="testdb",
        )

        expected_url = "postgresql+asyncpg://testuser:testpass@localhost:5432/testdb"
        assert settings.url == expected_url

    def test_sync_url_construction(self):
        """Test synchronous PostgreSQL URL construction."""
        from app.config import DatabaseSettings

        settings = DatabaseSettings(
            host="localhost",
            port=5432,
            user="testuser",
            password="testpass",
            name="testdb",
        )

        expected_url = "postgresql://testuser:testpass@localhost:5432/testdb"
        assert settings.sync_url == expected_url

    def test_default_values(self):
        """Test default database settings values."""
        from app.config import DatabaseSettings

        settings = DatabaseSettings()

        assert settings.host == "localhost"
        assert settings.port == 5432
        assert settings.user == "yesbut"
        assert settings.pool_size == 10
        assert settings.max_overflow == 20
        assert settings.echo is False


class TestRedisSettings:
    """Tests for RedisSettings class."""

    def test_url_without_password(self):
        """Test Redis URL construction without password."""
        from app.config import RedisSettings

        settings = RedisSettings(
            host="localhost",
            port=6379,
            db=0,
            password=None,
        )

        expected_url = "redis://localhost:6379/0"
        assert settings.url == expected_url

    def test_url_with_password(self):
        """Test Redis URL construction with password."""
        from app.config import RedisSettings

        settings = RedisSettings(
            host="localhost",
            port=6379,
            db=1,
            password="secret",
        )

        expected_url = "redis://:secret@localhost:6379/1"
        assert settings.url == expected_url

    def test_default_values(self):
        """Test default Redis settings values."""
        from app.config import RedisSettings

        settings = RedisSettings()

        assert settings.host == "localhost"
        assert settings.port == 6379
        assert settings.db == 0
        assert settings.max_connections == 50
        assert settings.lock_timeout == 30


class TestLLMSettings:
    """Tests for LLMSettings class."""

    def test_default_anthropic_config(self):
        """Test default LLM settings for Anthropic."""
        from app.config import LLMSettings

        settings = LLMSettings()

        assert settings.provider == "anthropic"
        assert settings.model == "claude-3-5-sonnet-20241022"
        assert settings.api_key == "1"
        assert settings.api_base == "http://localhost:8000"
        assert settings.temperature == 0.7
        assert settings.max_tokens == 4096

    def test_custom_llm_config(self):
        """Test custom LLM settings."""
        from app.config import LLMSettings

        settings = LLMSettings(
            provider="openai",
            model="gpt-4",
            api_key="custom-key",
            api_base="https://api.openai.com/v1",
            temperature=0.5,
        )

        assert settings.provider == "openai"
        assert settings.model == "gpt-4"
        assert settings.api_key == "custom-key"
        assert settings.temperature == 0.5


class TestSettings:
    """Tests for main Settings class."""

    def test_cors_origins_from_string(self):
        """Test CORS origins parsing from comma-separated string."""
        from app.config import Settings

        settings = Settings(
            cors_origins="http://localhost:3000,http://localhost:8080",
            secret_key="test-key",
        )

        assert "http://localhost:3000" in settings.cors_origins
        assert "http://localhost:8080" in settings.cors_origins

    def test_cors_origins_from_list(self):
        """Test CORS origins from list."""
        from app.config import Settings

        settings = Settings(
            cors_origins=["http://localhost:3000", "http://example.com"],
            secret_key="test-key",
        )

        assert settings.cors_origins == ["http://localhost:3000", "http://example.com"]

    def test_secret_key_generation_in_development(self):
        """Test secret key auto-generation in development."""
        from app.config import Settings

        settings = Settings(environment="development", secret_key="")

        # Should auto-generate a key
        assert settings.secret_key is not None
        assert len(settings.secret_key) > 0

    def test_secret_key_required_in_production(self):
        """Test secret key is required in production."""
        from app.config import Settings

        with pytest.raises(ValueError, match="SECRET_KEY must be set"):
            Settings(environment="production", secret_key="")

    def test_nested_settings(self):
        """Test nested settings are properly initialized."""
        from app.config import Settings

        settings = Settings(secret_key="test-key")

        assert settings.database is not None
        assert settings.redis is not None
        assert settings.llm is not None
        assert settings.embedding is not None
        assert settings.celery is not None
        assert settings.agent is not None


class TestGetSettings:
    """Tests for get_settings function."""

    def test_get_settings_returns_settings(self):
        """Test get_settings returns Settings instance."""
        from app.config import get_settings

        # Clear cache first
        get_settings.cache_clear()

        settings = get_settings()

        assert settings is not None
        assert settings.app_name == "YesBut"

    def test_get_settings_is_cached(self):
        """Test get_settings returns cached instance."""
        from app.config import get_settings

        get_settings.cache_clear()

        settings1 = get_settings()
        settings2 = get_settings()

        assert settings1 is settings2


class TestGetAnthropicConfig:
    """Tests for get_anthropic_config function."""

    def test_anthropic_config_structure(self):
        """Test Anthropic config has correct structure."""
        from app.config import get_anthropic_config, get_settings

        get_settings.cache_clear()

        config = get_anthropic_config()

        assert "api_key" in config
        assert "base_url" in config
        assert "timeout" in config
        assert "max_retries" in config

    def test_anthropic_config_values(self):
        """Test Anthropic config has correct default values."""
        from app.config import get_anthropic_config, get_settings

        get_settings.cache_clear()

        config = get_anthropic_config()

        assert config["api_key"] == "1"
        assert config["base_url"] == "http://localhost:8000"

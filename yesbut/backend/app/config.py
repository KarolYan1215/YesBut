"""
Application Configuration Module

Centralized configuration management using Pydantic Settings.
Loads configuration from environment variables with validation.

@module app/config
"""

from functools import lru_cache
from typing import Optional, List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator, model_validator


class DatabaseSettings(BaseSettings):
    """Database connection configuration."""

    host: str = "localhost"
    port: int = 5432
    user: str = "yesbut"
    password: str = ""
    name: str = "yesbut"
    pool_size: int = 10
    max_overflow: int = 20
    echo: bool = False

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

    @property
    def sync_url(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

    model_config = SettingsConfigDict(env_prefix="DB_")


class RedisSettings(BaseSettings):
    """Redis connection configuration."""

    host: str = "localhost"
    port: int = 6379
    password: Optional[str] = None
    db: int = 0
    max_connections: int = 50
    socket_timeout: float = 5.0
    lock_timeout: int = 30
    lock_retry_interval: int = 100

    @property
    def url(self) -> str:
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"

    model_config = SettingsConfigDict(env_prefix="REDIS_")


class LLMSettings(BaseSettings):
    """LLM (Large Language Model) configuration."""

    provider: str = "anthropic"
    model: str = "claude-3-5-sonnet-20241022"
    api_key: str = "1"
    api_base: Optional[str] = "http://localhost:8000"
    temperature: float = 0.7
    max_tokens: int = 4096
    timeout: int = 60
    max_retries: int = 3

    model_config = SettingsConfigDict(env_prefix="LLM_")


class EmbeddingSettings(BaseSettings):
    """Embedding model configuration for semantic operations."""

    provider: str = "openai"
    model: str = "text-embedding-3-small"
    api_key: Optional[str] = None
    dimension: int = 1536
    batch_size: int = 100

    model_config = SettingsConfigDict(env_prefix="EMBEDDING_")


class CelerySettings(BaseSettings):
    """Celery task queue configuration."""

    broker_url: str = "redis://localhost:6379/1"
    result_backend: str = "redis://localhost:6379/2"
    task_serializer: str = "json"
    result_serializer: str = "json"
    accept_content: List[str] = ["json"]
    timezone: str = "UTC"
    task_track_started: bool = True
    task_time_limit: int = 3600
    task_soft_time_limit: int = 3300

    model_config = SettingsConfigDict(env_prefix="CELERY_")


class AgentSettings(BaseSettings):
    """Multi-agent system configuration."""

    max_concurrent_agents: int = 10
    default_timeout: int = 300
    max_iterations: int = 100
    convergence_threshold: float = 0.95
    oscillation_window: int = 5
    entropy_threshold: float = 0.3
    pruning_threshold: float = 0.2

    model_config = SettingsConfigDict(env_prefix="AGENT_")


class Settings(BaseSettings):
    """Main application settings aggregating all configuration sections."""

    app_name: str = "YesBut"
    app_version: str = "0.1.0"
    debug: bool = False
    environment: str = "development"
    secret_key: str = ""
    cors_origins: List[str] = ["http://localhost:3000"]
    api_prefix: str = "/api/v1"

    # Nested settings
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    llm: LLMSettings = Field(default_factory=LLMSettings)
    embedding: EmbeddingSettings = Field(default_factory=EmbeddingSettings)
    celery: CelerySettings = Field(default_factory=CelerySettings)
    agent: AgentSettings = Field(default_factory=AgentSettings)

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v) -> List[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        if isinstance(v, list):
            return v
        return ["http://localhost:3000"]

    @model_validator(mode="after")
    def validate_secret_key(self) -> "Settings":
        if self.environment == "production" and not self.secret_key:
            raise ValueError("SECRET_KEY must be set in production environment")
        if not self.secret_key:
            import secrets
            object.__setattr__(self, "secret_key", secrets.token_urlsafe(32))
        return self

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings instance."""
    return Settings()


def get_anthropic_config() -> dict:
    """Get Anthropic API client configuration."""
    settings = get_settings()
    return {
        "api_key": settings.llm.api_key,
        "base_url": settings.llm.api_base,
        "timeout": settings.llm.timeout,
        "max_retries": settings.llm.max_retries,
    }


def create_llm_client():
    """Create and return an AsyncAnthropic client with configured settings."""
    from anthropic import AsyncAnthropic
    config = get_anthropic_config()
    return AsyncAnthropic(
        api_key=config["api_key"],
        base_url=config["base_url"],
        timeout=config["timeout"],
        max_retries=config["max_retries"],
    )

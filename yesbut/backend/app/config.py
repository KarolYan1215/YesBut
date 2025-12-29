"""
Application Configuration Module

Centralized configuration management using Pydantic Settings.
Loads configuration from environment variables with validation.

@module app/config
"""

from functools import lru_cache
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field, validator


class DatabaseSettings(BaseSettings):
    """
    Database connection configuration.

    Attributes:
        host: PostgreSQL host address
        port: PostgreSQL port number
        user: Database username
        password: Database password
        name: Database name
        pool_size: Connection pool size
        max_overflow: Maximum overflow connections
        echo: Whether to echo SQL statements (debug)

    Environment Variables:
        DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME,
        DB_POOL_SIZE, DB_MAX_OVERFLOW, DB_ECHO
    """

    host: str = Field(default="localhost", env="DB_HOST")
    port: int = Field(default=5432, env="DB_PORT")
    user: str = Field(default="yesbut", env="DB_USER")
    password: str = Field(default="", env="DB_PASSWORD")
    name: str = Field(default="yesbut", env="DB_NAME")
    pool_size: int = Field(default=10, env="DB_POOL_SIZE")
    max_overflow: int = Field(default=20, env="DB_MAX_OVERFLOW")
    echo: bool = Field(default=False, env="DB_ECHO")

    @property
    def url(self) -> str:
        """
        Construct PostgreSQL connection URL.

        Returns:
            str: SQLAlchemy-compatible database URL
        """
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

    @property
    def sync_url(self) -> str:
        """
        Construct synchronous PostgreSQL connection URL for Alembic.

        Returns:
            str: SQLAlchemy-compatible synchronous database URL
        """
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

    class Config:
        env_prefix = "DB_"


class RedisSettings(BaseSettings):
    """
    Redis connection configuration.

    Attributes:
        host: Redis host address
        port: Redis port number
        password: Redis password (optional)
        db: Redis database number
        max_connections: Maximum connection pool size
        socket_timeout: Socket timeout in seconds
        lock_timeout: Default lock timeout in seconds
        lock_retry_interval: Lock retry interval in milliseconds

    Environment Variables:
        REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, REDIS_DB,
        REDIS_MAX_CONNECTIONS, REDIS_SOCKET_TIMEOUT,
        REDIS_LOCK_TIMEOUT, REDIS_LOCK_RETRY_INTERVAL
    """

    host: str = Field(default="localhost", env="REDIS_HOST")
    port: int = Field(default=6379, env="REDIS_PORT")
    password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    db: int = Field(default=0, env="REDIS_DB")
    max_connections: int = Field(default=50, env="REDIS_MAX_CONNECTIONS")
    socket_timeout: float = Field(default=5.0, env="REDIS_SOCKET_TIMEOUT")
    lock_timeout: int = Field(default=30, env="REDIS_LOCK_TIMEOUT")
    lock_retry_interval: int = Field(default=100, env="REDIS_LOCK_RETRY_INTERVAL")

    @property
    def url(self) -> str:
        """
        Construct Redis connection URL.

        Returns:
            str: Redis connection URL
        """
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"

    class Config:
        env_prefix = "REDIS_"


class LLMSettings(BaseSettings):
    """
    LLM (Large Language Model) configuration.

    Attributes:
        provider: LLM provider (openai, anthropic, etc.)
        model: Model name/identifier
        api_key: API key for the provider
        api_base: Custom API base URL (optional)
        temperature: Default temperature for generation
        max_tokens: Maximum tokens per request
        timeout: Request timeout in seconds
        max_retries: Maximum retry attempts

    Environment Variables:
        LLM_PROVIDER, LLM_MODEL, LLM_API_KEY, LLM_API_BASE,
        LLM_TEMPERATURE, LLM_MAX_TOKENS, LLM_TIMEOUT, LLM_MAX_RETRIES
    """

    provider: str = Field(default="anthropic", env="LLM_PROVIDER")
    model: str = Field(default="claude-3-5-sonnet-20241022", env="LLM_MODEL")
    api_key: str = Field(default="1", env="LLM_API_KEY")
    api_base: Optional[str] = Field(default="http://localhost:8000", env="LLM_API_BASE")
    temperature: float = Field(default=0.7, env="LLM_TEMPERATURE")
    max_tokens: int = Field(default=4096, env="LLM_MAX_TOKENS")
    timeout: int = Field(default=60, env="LLM_TIMEOUT")
    max_retries: int = Field(default=3, env="LLM_MAX_RETRIES")

    class Config:
        env_prefix = "LLM_"


class EmbeddingSettings(BaseSettings):
    """
    Embedding model configuration for semantic operations.

    Attributes:
        provider: Embedding provider (openai, sentence-transformers, etc.)
        model: Embedding model name
        api_key: API key (if using API-based provider)
        dimension: Embedding vector dimension
        batch_size: Batch size for embedding requests

    Environment Variables:
        EMBEDDING_PROVIDER, EMBEDDING_MODEL, EMBEDDING_API_KEY,
        EMBEDDING_DIMENSION, EMBEDDING_BATCH_SIZE
    """

    provider: str = Field(default="openai", env="EMBEDDING_PROVIDER")
    model: str = Field(default="text-embedding-3-small", env="EMBEDDING_MODEL")
    api_key: Optional[str] = Field(default=None, env="EMBEDDING_API_KEY")
    dimension: int = Field(default=1536, env="EMBEDDING_DIMENSION")
    batch_size: int = Field(default=100, env="EMBEDDING_BATCH_SIZE")

    class Config:
        env_prefix = "EMBEDDING_"


class CelerySettings(BaseSettings):
    """
    Celery task queue configuration.

    Attributes:
        broker_url: Message broker URL (Redis)
        result_backend: Result backend URL (Redis)
        task_serializer: Task serialization format
        result_serializer: Result serialization format
        accept_content: Accepted content types
        timezone: Celery timezone
        task_track_started: Whether to track task start
        task_time_limit: Hard time limit for tasks (seconds)
        task_soft_time_limit: Soft time limit for tasks (seconds)

    Environment Variables:
        CELERY_BROKER_URL, CELERY_RESULT_BACKEND, etc.
    """

    broker_url: str = Field(default="redis://localhost:6379/1", env="CELERY_BROKER_URL")
    result_backend: str = Field(default="redis://localhost:6379/2", env="CELERY_RESULT_BACKEND")
    task_serializer: str = Field(default="json", env="CELERY_TASK_SERIALIZER")
    result_serializer: str = Field(default="json", env="CELERY_RESULT_SERIALIZER")
    accept_content: List[str] = Field(default=["json"], env="CELERY_ACCEPT_CONTENT")
    timezone: str = Field(default="UTC", env="CELERY_TIMEZONE")
    task_track_started: bool = Field(default=True, env="CELERY_TASK_TRACK_STARTED")
    task_time_limit: int = Field(default=3600, env="CELERY_TASK_TIME_LIMIT")
    task_soft_time_limit: int = Field(default=3300, env="CELERY_TASK_SOFT_TIME_LIMIT")

    class Config:
        env_prefix = "CELERY_"


class AgentSettings(BaseSettings):
    """
    Multi-agent system configuration.

    Attributes:
        max_concurrent_agents: Maximum concurrent agent executions
        default_timeout: Default agent execution timeout (seconds)
        max_iterations: Maximum iterations per agent run
        convergence_threshold: Threshold for convergence detection
        oscillation_window: Window size for oscillation detection
        entropy_threshold: Semantic entropy threshold
        pruning_threshold: Utility threshold for branch pruning

    Environment Variables:
        AGENT_MAX_CONCURRENT, AGENT_DEFAULT_TIMEOUT, etc.
    """

    max_concurrent_agents: int = Field(default=10, env="AGENT_MAX_CONCURRENT")
    default_timeout: int = Field(default=300, env="AGENT_DEFAULT_TIMEOUT")
    max_iterations: int = Field(default=100, env="AGENT_MAX_ITERATIONS")
    convergence_threshold: float = Field(default=0.95, env="AGENT_CONVERGENCE_THRESHOLD")
    oscillation_window: int = Field(default=5, env="AGENT_OSCILLATION_WINDOW")
    entropy_threshold: float = Field(default=0.3, env="AGENT_ENTROPY_THRESHOLD")
    pruning_threshold: float = Field(default=0.2, env="AGENT_PRUNING_THRESHOLD")

    class Config:
        env_prefix = "AGENT_"


class Settings(BaseSettings):
    """
    Main application settings aggregating all configuration sections.

    Attributes:
        app_name: Application name
        app_version: Application version
        debug: Debug mode flag
        environment: Environment name (development, staging, production)
        secret_key: Secret key for JWT and encryption
        cors_origins: Allowed CORS origins
        api_prefix: API route prefix
        database: Database settings
        redis: Redis settings
        llm: LLM settings
        embedding: Embedding settings
        celery: Celery settings
        agent: Agent settings

    Environment Variables:
        APP_NAME, APP_VERSION, DEBUG, ENVIRONMENT, SECRET_KEY,
        CORS_ORIGINS, API_PREFIX
    """

    app_name: str = Field(default="YesBut", env="APP_NAME")
    app_version: str = Field(default="0.1.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    environment: str = Field(default="development", env="ENVIRONMENT")
    secret_key: str = Field(default="", env="SECRET_KEY")
    cors_origins: List[str] = Field(default=["http://localhost:3000"], env="CORS_ORIGINS")
    api_prefix: str = Field(default="/api/v1", env="API_PREFIX")

    # Nested settings
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    llm: LLMSettings = Field(default_factory=LLMSettings)
    embedding: EmbeddingSettings = Field(default_factory=EmbeddingSettings)
    celery: CelerySettings = Field(default_factory=CelerySettings)
    agent: AgentSettings = Field(default_factory=AgentSettings)

    @validator("secret_key")
    def validate_secret_key(cls, v: str, values: dict) -> str:
        """
        Validate secret key is set in production.

        Args:
            v: Secret key value
            values: Other field values

        Returns:
            str: Validated secret key

        Raises:
            ValueError: If secret key is empty in production
        """
        environment = values.get("environment", "development")
        if environment == "production" and not v:
            raise ValueError("SECRET_KEY must be set in production environment")
        if not v:
            # Generate a default key for development
            import secrets
            return secrets.token_urlsafe(32)
        return v

    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v) -> List[str]:
        """
        Parse CORS origins from comma-separated string or list.

        Args:
            v: Raw CORS origins value

        Returns:
            List[str]: List of CORS origin URLs
        """
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        if isinstance(v, list):
            return v
        return ["http://localhost:3000"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached application settings instance.

    Uses LRU cache to ensure settings are loaded only once.
    Call get_settings.cache_clear() to reload settings.

    Returns:
        Settings: Application settings instance
    """
    return Settings()


# Convenience function to get Anthropic client configuration
def get_anthropic_config() -> dict:
    """
    Get Anthropic API client configuration.

    Returns:
        dict: Configuration for Anthropic client with base_url and api_key
    """
    settings = get_settings()
    return {
        "api_key": settings.llm.api_key,
        "base_url": settings.llm.api_base,
        "timeout": settings.llm.timeout,
        "max_retries": settings.llm.max_retries,
    }

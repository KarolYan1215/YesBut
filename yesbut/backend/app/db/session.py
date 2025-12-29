"""
Database Session Module

SQLAlchemy async engine and session configuration.

@module app/db/session
"""

from typing import AsyncGenerator, Optional
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import text

from app.models.base import Base


def create_engine(database_url: str, **kwargs) -> AsyncEngine:
    """
    Create SQLAlchemy async engine.

    Creates an async engine with connection pooling configured for
    production use. Supports PostgreSQL with asyncpg driver.

    Args:
        database_url: PostgreSQL connection URL
            Format: postgresql+asyncpg://user:pass@host:port/dbname
        **kwargs: Additional engine configuration options
            - pool_size: Connection pool size (default: 10)
            - max_overflow: Max overflow connections (default: 20)
            - pool_pre_ping: Enable connection health checks (default: True)
            - echo: Echo SQL statements for debugging (default: False)

    Returns:
        AsyncEngine: Configured SQLAlchemy async engine
    """
    default_kwargs = {
        "pool_size": 10,
        "max_overflow": 20,
        "pool_pre_ping": True,
        "echo": False,
    }
    default_kwargs.update(kwargs)
    return create_async_engine(database_url, **default_kwargs)


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """
    Create async session factory.

    Creates a sessionmaker configured for async operations with
    the provided engine.

    Args:
        engine: SQLAlchemy async engine

    Returns:
        async_sessionmaker: Configured session factory

    Session Configuration:
        - autocommit: False (explicit commits required)
        - autoflush: False (explicit flushes for control)
        - expire_on_commit: False (objects remain usable after commit)
    """
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )


async def get_session(session_factory: async_sessionmaker[AsyncSession]) -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session generator.

    Yields an async session and ensures proper cleanup after use.
    Used as a FastAPI dependency.

    Args:
        session_factory: Session factory from create_session_factory

    Yields:
        AsyncSession: Database session
    """
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db(engine: AsyncEngine) -> None:
    """
    Initialize database schema.

    Creates all tables defined in SQLAlchemy models.
    Should be called once during application startup.

    Args:
        engine: SQLAlchemy async engine

    Note:
        In production, use Alembic migrations instead of this function.
        This is primarily for development and testing.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db(engine: AsyncEngine) -> None:
    """
    Close database connections.

    Disposes of the engine and closes all connections in the pool.
    Should be called during application shutdown.

    Args:
        engine: SQLAlchemy async engine
    """
    await engine.dispose()


class DatabaseManager:
    """
    Database connection manager.

    Manages database engine and session lifecycle.
    Provides context manager interface for session handling.

    Attributes:
        engine: SQLAlchemy async engine
        session_factory: Session factory for creating sessions
    """

    def __init__(self, database_url: str, **engine_kwargs):
        """
        Initialize database manager.

        Args:
            database_url: PostgreSQL connection URL
            **engine_kwargs: Additional engine configuration
        """
        self.database_url = database_url
        self.engine_kwargs = engine_kwargs
        self.engine: Optional[AsyncEngine] = None
        self.session_factory: Optional[async_sessionmaker[AsyncSession]] = None

    async def connect(self) -> None:
        """
        Establish database connection.

        Creates engine and session factory.
        Should be called during application startup.
        """
        self.engine = create_engine(self.database_url, **self.engine_kwargs)
        self.session_factory = create_session_factory(self.engine)

    async def disconnect(self) -> None:
        """
        Close database connection.

        Disposes of engine and cleans up resources.
        Should be called during application shutdown.
        """
        if self.engine:
            await close_db(self.engine)
            self.engine = None
            self.session_factory = None

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get database session context manager.

        Yields:
            AsyncSession: Database session with automatic cleanup
        """
        if not self.session_factory:
            raise RuntimeError("Database not connected. Call connect() first.")

        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def health_check(self) -> bool:
        """
        Check database connectivity.

        Executes a simple query to verify database is accessible.

        Returns:
            bool: True if database is healthy, False otherwise
        """
        if not self.engine:
            return False
        try:
            async with self.engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False


# Global database manager instance (initialized in main.py)
db_manager: Optional[DatabaseManager] = None


def get_db_manager() -> DatabaseManager:
    """
    Get global database manager instance.

    Returns:
        DatabaseManager: Global database manager

    Raises:
        RuntimeError: If database manager is not initialized
    """
    if db_manager is None:
        raise RuntimeError("Database manager not initialized. Call init_db_manager() first.")
    return db_manager


async def init_db_manager(database_url: str, **kwargs) -> DatabaseManager:
    """
    Initialize global database manager.

    Args:
        database_url: PostgreSQL connection URL
        **kwargs: Additional engine configuration

    Returns:
        DatabaseManager: Initialized database manager
    """
    global db_manager
    db_manager = DatabaseManager(database_url, **kwargs)
    await db_manager.connect()
    return db_manager


async def close_db_manager() -> None:
    """
    Close global database manager.

    Should be called during application shutdown.
    """
    global db_manager
    if db_manager:
        await db_manager.disconnect()
        db_manager = None

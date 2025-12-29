"""
Redis Client Module

Redis connection management for caching and distributed locking.

@module app/db/redis
"""

from typing import Optional, Any, List, Dict
from datetime import timedelta
import json
import redis.asyncio as redis
from redis.asyncio.connection import ConnectionPool


class RedisClient:
    """
    Redis client wrapper with connection pooling.

    Provides async Redis operations with automatic connection management.
    Used for caching, distributed locking, and pub/sub messaging.

    Attributes:
        url: Redis connection URL
        pool: Connection pool instance
        client: Redis client instance
    """

    def __init__(
        self,
        url: str,
        max_connections: int = 50,
        socket_timeout: float = 5.0,
        decode_responses: bool = True,
    ):
        """
        Initialize Redis client.

        Args:
            url: Redis connection URL (redis://host:port/db)
            max_connections: Maximum connections in pool
            socket_timeout: Socket timeout in seconds
            decode_responses: Whether to decode bytes to strings
        """
        self.url = url
        self.max_connections = max_connections
        self.socket_timeout = socket_timeout
        self.decode_responses = decode_responses
        self.pool: Optional[ConnectionPool] = None
        self.client: Optional[redis.Redis] = None

    async def connect(self) -> None:
        """
        Establish Redis connection.

        Creates connection pool and client instance.
        Should be called during application startup.
        """
        self.pool = ConnectionPool.from_url(
            self.url,
            max_connections=self.max_connections,
            socket_timeout=self.socket_timeout,
            decode_responses=self.decode_responses,
        )
        self.client = redis.Redis(connection_pool=self.pool)

    async def disconnect(self) -> None:
        """
        Close Redis connection.

        Closes client and connection pool.
        Should be called during application shutdown.
        """
        if self.client:
            await self.client.close()
            self.client = None
        if self.pool:
            await self.pool.disconnect()
            self.pool = None

    async def health_check(self) -> bool:
        """
        Check Redis connectivity.

        Executes PING command to verify Redis is accessible.

        Returns:
            bool: True if Redis is healthy, False otherwise
        """
        if not self.client:
            return False
        try:
            return await self.client.ping()
        except Exception:
            return False

    # =========================================================================
    # Basic Operations
    # =========================================================================

    async def get(self, key: str) -> Optional[str]:
        """
        Get value by key.

        Args:
            key: Redis key

        Returns:
            Optional[str]: Value if exists, None otherwise
        """
        return await self.client.get(key)

    async def set(
        self,
        key: str,
        value: Any,
        ex: Optional[int] = None,
        px: Optional[int] = None,
        nx: bool = False,
        xx: bool = False,
    ) -> bool:
        """
        Set key-value pair.

        Args:
            key: Redis key
            value: Value to set (will be serialized)
            ex: Expiration in seconds
            px: Expiration in milliseconds
            nx: Only set if key does not exist
            xx: Only set if key exists

        Returns:
            bool: True if set successfully, False otherwise
        """
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        result = await self.client.set(key, value, ex=ex, px=px, nx=nx, xx=xx)
        return result is not None and result is not False

    async def delete(self, *keys: str) -> int:
        """
        Delete one or more keys.

        Args:
            *keys: Keys to delete

        Returns:
            int: Number of keys deleted
        """
        if not keys:
            return 0
        return await self.client.delete(*keys)

    async def exists(self, *keys: str) -> int:
        """
        Check if keys exist.

        Args:
            *keys: Keys to check

        Returns:
            int: Number of keys that exist
        """
        if not keys:
            return 0
        return await self.client.exists(*keys)

    async def expire(self, key: str, seconds: int) -> bool:
        """
        Set key expiration.

        Args:
            key: Redis key
            seconds: Expiration time in seconds

        Returns:
            bool: True if expiration was set, False if key doesn't exist
        """
        return await self.client.expire(key, seconds)

    async def ttl(self, key: str) -> int:
        """
        Get time-to-live for key.

        Args:
            key: Redis key

        Returns:
            int: TTL in seconds, -1 if no expiry, -2 if key doesn't exist
        """
        return await self.client.ttl(key)

    # =========================================================================
    # Hash Operations
    # =========================================================================

    async def hget(self, name: str, key: str) -> Optional[str]:
        """
        Get hash field value.

        Args:
            name: Hash name
            key: Field key

        Returns:
            Optional[str]: Field value if exists
        """
        return await self.client.hget(name, key)

    async def hset(self, name: str, key: str, value: Any) -> int:
        """
        Set hash field value.

        Args:
            name: Hash name
            key: Field key
            value: Field value

        Returns:
            int: 1 if new field, 0 if updated existing
        """
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        return await self.client.hset(name, key, value)

    async def hgetall(self, name: str) -> Dict[str, str]:
        """
        Get all hash fields and values.

        Args:
            name: Hash name

        Returns:
            Dict[str, str]: All field-value pairs
        """
        return await self.client.hgetall(name)

    async def hdel(self, name: str, *keys: str) -> int:
        """
        Delete hash fields.

        Args:
            name: Hash name
            *keys: Fields to delete

        Returns:
            int: Number of fields deleted
        """
        if not keys:
            return 0
        return await self.client.hdel(name, *keys)

    # =========================================================================
    # List Operations
    # =========================================================================

    async def lpush(self, name: str, *values: Any) -> int:
        """
        Push values to list head.

        Args:
            name: List name
            *values: Values to push

        Returns:
            int: List length after push
        """
        serialized = [json.dumps(v) if isinstance(v, (dict, list)) else v for v in values]
        return await self.client.lpush(name, *serialized)

    async def rpush(self, name: str, *values: Any) -> int:
        """
        Push values to list tail.

        Args:
            name: List name
            *values: Values to push

        Returns:
            int: List length after push
        """
        serialized = [json.dumps(v) if isinstance(v, (dict, list)) else v for v in values]
        return await self.client.rpush(name, *serialized)

    async def lrange(self, name: str, start: int, end: int) -> List[str]:
        """
        Get list range.

        Args:
            name: List name
            start: Start index
            end: End index (-1 for all)

        Returns:
            List[str]: List elements in range
        """
        return await self.client.lrange(name, start, end)

    # =========================================================================
    # Pub/Sub Operations
    # =========================================================================

    async def publish(self, channel: str, message: str) -> int:
        """
        Publish message to channel.

        Args:
            channel: Channel name
            message: Message to publish

        Returns:
            int: Number of subscribers that received the message
        """
        if isinstance(message, (dict, list)):
            message = json.dumps(message)
        return await self.client.publish(channel, message)

    async def subscribe(self, *channels: str):
        """
        Subscribe to channels.

        Args:
            *channels: Channel names to subscribe to

        Returns:
            PubSub: Pub/sub instance for receiving messages
        """
        pubsub = self.client.pubsub()
        await pubsub.subscribe(*channels)
        return pubsub

    # =========================================================================
    # Lua Script Execution
    # =========================================================================

    async def eval(
        self,
        script: str,
        keys: List[str],
        args: List[Any],
    ) -> Any:
        """
        Execute Lua script.

        Args:
            script: Lua script code
            keys: KEYS array for script
            args: ARGV array for script

        Returns:
            Any: Script return value
        """
        return await self.client.eval(script, len(keys), *keys, *args)

    async def evalsha(
        self,
        sha: str,
        keys: List[str],
        args: List[Any],
    ) -> Any:
        """
        Execute cached Lua script by SHA.

        Args:
            sha: Script SHA hash
            keys: KEYS array for script
            args: ARGV array for script

        Returns:
            Any: Script return value
        """
        return await self.client.evalsha(sha, len(keys), *keys, *args)

    async def script_load(self, script: str) -> str:
        """
        Load Lua script into cache.

        Args:
            script: Lua script code

        Returns:
            str: Script SHA hash
        """
        return await self.client.script_load(script)


# Global Redis client instance (initialized in main.py)
redis_client: Optional[RedisClient] = None


def get_redis_client() -> RedisClient:
    """
    Get global Redis client instance.

    Returns:
        RedisClient: Global Redis client

    Raises:
        RuntimeError: If Redis client is not initialized
    """
    if redis_client is None:
        raise RuntimeError("Redis client not initialized. Call init_redis() first.")
    return redis_client


async def init_redis(url: str, **kwargs) -> RedisClient:
    """
    Initialize global Redis client.

    Args:
        url: Redis connection URL
        **kwargs: Additional client configuration

    Returns:
        RedisClient: Initialized Redis client
    """
    global redis_client
    redis_client = RedisClient(url, **kwargs)
    await redis_client.connect()
    return redis_client


async def close_redis() -> None:
    """
    Close global Redis client.

    Should be called during application shutdown.
    """
    global redis_client
    if redis_client:
        await redis_client.disconnect()
        redis_client = None

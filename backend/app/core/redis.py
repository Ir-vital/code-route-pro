"""
Client Redis async (redis-py).
Utilisé pour : cache, rate-limiting, blacklist tokens, sessions d'examen en cours.
"""

from collections.abc import AsyncGenerator

import redis.asyncio as aioredis
from redis.asyncio import Redis

from app.core.config import settings

# ─── Pool de connexions ───────────────────────────────────────────────────────
_redis_pool: Redis | None = None


async def get_redis_pool() -> Redis:
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
    return _redis_pool


async def close_redis_pool() -> None:
    global _redis_pool
    if _redis_pool:
        await _redis_pool.aclose()
        _redis_pool = None


# ─── Dépendance FastAPI ───────────────────────────────────────────────────────
async def get_redis() -> AsyncGenerator[Redis, None]:
    """Dépendance FastAPI qui fournit un client Redis."""
    redis = await get_redis_pool()
    yield redis


# ─── Helpers cache ────────────────────────────────────────────────────────────
class RedisCache:
    """Wrapper simple pour les opérations de cache Redis."""

    def __init__(self, redis: Redis, prefix: str = "cache"):
        self._redis = redis
        self._prefix = prefix

    def _key(self, key: str) -> str:
        return f"{self._prefix}:{key}"

    async def get(self, key: str) -> str | None:
        return await self._redis.get(self._key(key))

    async def set(self, key: str, value: str, ttl: int = settings.REDIS_CACHE_TTL) -> None:
        await self._redis.setex(self._key(key), ttl, value)

    async def delete(self, key: str) -> None:
        await self._redis.delete(self._key(key))

    async def exists(self, key: str) -> bool:
        return bool(await self._redis.exists(self._key(key)))

    async def increment(self, key: str, ttl: int | None = None) -> int:
        count = await self._redis.incr(self._key(key))
        if ttl and count == 1:
            await self._redis.expire(self._key(key), ttl)
        return count

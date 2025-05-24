import time
import logging
from typing import Dict, Tuple

logger = logging.getLogger(__name__)

class Cache:
    def __init__(self, ttl_seconds: int = 3600):  # Default TTL of 1 hour
        self._cache: Dict[str, Tuple[str, float]] = {}
        self.ttl_seconds = ttl_seconds
        logger.info(f"Initialized cache with TTL of {ttl_seconds} seconds")

    def get(self, key: str) -> str | None:
        if key in self._cache:
            value, timestamp = self._cache[key]
            if time.time() - timestamp <= self.ttl_seconds:
                logger.info(f"Cache hit for key: {key[:50]}...")
                return value
            else:
                logger.info(f"Cache entry expired for key: {key[:50]}...")
                del self._cache[key]
        return None

    def set(self, key: str, value: str):
        logger.info(f"Caching response for key: {key[:50]}...")
        self._cache[key] = (value, time.time())

    def clear(self):
        logger.info("Clearing cache")
        self._cache.clear()

    def remove_expired(self):
        current_time = time.time()
        expired_keys = [
            key for key, (_, timestamp) in self._cache.items()
            if current_time - timestamp > self.ttl_seconds
        ]
        for key in expired_keys:
            del self._cache[key]
        if expired_keys:
            logger.info(f"Removed {len(expired_keys)} expired cache entries")

    def get_cache_size(self) -> int:
        return len(self._cache) 
import redis
import pickle
import json
from typing import Any, Optional
from datetime import datetime, timedelta
import hashlib
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    """Simple cache manager without vector embeddings"""
    
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_client = None
        self._in_memory_cache = {}
        self._setup_redis(redis_url or settings.redis_url)
    
    def _setup_redis(self, redis_url: str):
        """Setup Redis connection with fallback"""
        try:
            self.redis_client = redis.Redis.from_url(
                redis_url,
                decode_responses=False,
                socket_timeout=5,
                socket_connect_timeout=5
            )
            self.redis_client.ping()
            logger.info("✅ Connected to Redis cache")
        except Exception as e:
            logger.warning(f"⚠️  Redis not available: {e}. Using in-memory cache.")
            self.redis_client = None
    
    def _generate_key(self, prefix: str, data: Any) -> str:
        """Generate consistent cache key"""
        if isinstance(data, str):
            data_str = data
        else:
            data_str = json.dumps(data, sort_keys=True, default=str)
        return f"{prefix}:{hashlib.md5(data_str.encode()).hexdigest()}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        try:
            if self.redis_client:
                cached = self.redis_client.get(key)
                return pickle.loads(cached) if cached else None
            else:
                # Check in-memory cache expiration
                cached_item = self._in_memory_cache.get(key)
                if cached_item:
                    expires = cached_item.get("expires")
                    if expires and datetime.now() < expires:
                        return cached_item["value"]
                    else:
                        # Remove expired item
                        del self._in_memory_cache[key]
                return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set cache value with TTL"""
        try:
            if self.redis_client:
                self.redis_client.setex(
                    key,
                    ttl or settings.CACHE_TTL,
                    pickle.dumps(value)
                )
            else:
                expires = datetime.now() + timedelta(seconds=ttl or settings.CACHE_TTL)
                self._in_memory_cache[key] = {
                    "value": value,
                    "expires": expires
                }
        except Exception as e:
            logger.error(f"Cache set error: {e}")
    
    def clear(self, prefix: str = None):
        """Clear cache entries"""
        try:
            if self.redis_client and prefix:
                # Iterate through keys with pattern
                cursor = 0
                while True:
                    cursor, keys = self.redis_client.scan(
                        cursor=cursor,
                        match=f"{prefix}:*",
                        count=100
                    )
                    if keys:
                        self.redis_client.delete(*keys)
                    if cursor == 0:
                        break
            elif self.redis_client:
                self.redis_client.flushdb()
            else:
                if prefix:
                    # Filter in-memory cache
                    keys_to_delete = [k for k in self._in_memory_cache.keys() 
                                    if k.startswith(f"{prefix}:")]
                    for k in keys_to_delete:
                        del self._in_memory_cache[k]
                else:
                    self._in_memory_cache.clear()
        except Exception as e:
            logger.error(f"Cache clear error: {e}")

# Global cache instance
cache_manager = CacheManager()
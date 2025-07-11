import redis
import json
import pickle
from typing import Any, Optional, Union
from datetime import timedelta
import hashlib
from app.utils.config import settings

class CacheService:
    """Redis-based caching service for improved performance"""
    
    def __init__(self):
        self.redis_client = None
        self.cache_enabled = settings.REDIS_ENABLED
        
        if self.cache_enabled:
            try:
                self.redis_client = redis.Redis(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    db=settings.REDIS_DB,
                    decode_responses=False  # Keep as bytes for pickle
                )
                # Test connection
                self.redis_client.ping()
            except Exception as e:
                print(f"Warning: Redis connection failed: {e}")
                self.cache_enabled = False
    
    def _generate_key(self, prefix: str, identifier: str) -> str:
        """Generate a cache key"""
        return f"{prefix}:{identifier}"
    
    def _serialize_value(self, value: Any) -> bytes:
        """Serialize value for storage"""
        try:
            return pickle.dumps(value)
        except Exception:
            # Fallback to JSON for simple types
            return json.dumps(value, default=str).encode('utf-8')
    
    def _deserialize_value(self, value: bytes) -> Any:
        """Deserialize value from storage"""
        try:
            return pickle.loads(value)
        except Exception:
            # Fallback to JSON
            return json.loads(value.decode('utf-8'))
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.cache_enabled or not self.redis_client:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value is not None:
                return self._deserialize_value(value)
            return None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    def set(self, key: str, value: Any, expire: Optional[Union[int, timedelta]] = None) -> bool:
        """Set value in cache with optional expiration"""
        if not self.cache_enabled or not self.redis_client:
            return False
        
        try:
            serialized_value = self._serialize_value(value)
            
            if isinstance(expire, timedelta):
                expire_seconds = int(expire.total_seconds())
            else:
                expire_seconds = expire
            
            if expire_seconds:
                return self.redis_client.setex(key, expire_seconds, serialized_value)
            else:
                return self.redis_client.set(key, serialized_value)
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        if not self.cache_enabled or not self.redis_client:
            return False
        
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        if not self.cache_enabled or not self.redis_client:
            return False
        
        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            print(f"Cache exists error: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        if not self.cache_enabled or not self.redis_client:
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            print(f"Cache clear pattern error: {e}")
            return 0
    
    def get_cache_stats(self) -> dict:
        """Get cache statistics"""
        if not self.cache_enabled or not self.redis_client:
            return {"enabled": False}
        
        try:
            info = self.redis_client.info()
            return {
                "enabled": True,
                "connected_clients": info.get("connected_clients", 0),
                "used_memory_human": info.get("used_memory_human", "0B"),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "total_commands_processed": info.get("total_commands_processed", 0)
            }
        except Exception as e:
            return {"enabled": True, "error": str(e)}
    
    # Specific cache methods for our application
    def cache_analysis_result(self, file_id: str, result: dict, expire: int = 3600) -> bool:
        """Cache analysis result"""
        key = self._generate_key("analysis", file_id)
        return self.set(key, result, expire)
    
    def get_cached_analysis(self, file_id: str) -> Optional[dict]:
        """Get cached analysis result"""
        key = self._generate_key("analysis", file_id)
        return self.get(key)
    
    def cache_prediction_result(self, file_id: str, result: dict, expire: int = 3600) -> bool:
        """Cache prediction result"""
        key = self._generate_key("prediction", file_id)
        return self.set(key, result, expire)
    
    def get_cached_prediction(self, file_id: str) -> Optional[dict]:
        """Get cached prediction result"""
        key = self._generate_key("prediction", file_id)
        return self.get(key)
    
    def cache_file_metadata(self, file_id: str, metadata: dict, expire: int = 7200) -> bool:
        """Cache file metadata"""
        key = self._generate_key("metadata", file_id)
        return self.set(key, metadata, expire)
    
    def get_cached_metadata(self, file_id: str) -> Optional[dict]:
        """Get cached file metadata"""
        key = self._generate_key("metadata", file_id)
        return self.get(key)
    
    def invalidate_file_cache(self, file_id: str) -> int:
        """Invalidate all cache entries for a file"""
        patterns = [
            f"analysis:{file_id}",
            f"prediction:{file_id}",
            f"metadata:{file_id}"
        ]
        total_deleted = 0
        for pattern in patterns:
            total_deleted += self.clear_pattern(pattern)
        return total_deleted

# Global cache service instance
cache_service = CacheService() 
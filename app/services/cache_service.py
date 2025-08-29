import redis
import json
import hashlib
import logging
from typing import Optional, Dict, Any

from app.config import settings


logger = logging.getLogger(__name__)


class CacheService:
    def __init__(self):
        self.redis_client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True
        )

    def _generate_key(
        self,
        text: str,
        summary_type: str,
        max_words: Optional[int] = None
    ) -> str:
        """Generate cache key from request parameters."""
        cache_data = {
            "text": text,
            "summary_type": summary_type,
            "max_words": max_words
        }
        cache_string = json.dumps(cache_data, sort_keys=True)
        return f"summary:{hashlib.md5(cache_string.encode()).hexdigest()}"

    async def get(
        self,
        text: str,
        summary_type: str,
        max_words: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Get cached summary if exists."""
        try:
            cache_key = self._generate_key(text, summary_type, max_words)
            cached_data = self.redis_client.get(cache_key)

            if cached_data:
                logger.info(f"Cache hit for key: {cache_key}")
                return json.loads(cached_data)

            logger.info(f"Cache miss for key: {cache_key}")
            return None

        except Exception as e:
            logger.error(f"Cache get error: {str(e)}")
            return None

    async def set(
        self,
        text: str,
        summary_type: str,
        summary_data: Dict[str, Any],
        max_words: Optional[int] = None
    ) -> bool:
        """Cache summary data."""
        try:
            cache_key = self._generate_key(text, summary_type, max_words)
            self.redis_client.setex(
                cache_key,
                settings.CACHE_TTL,
                json.dumps(summary_data)
            )
            logger.info(f"Cached data for key: {cache_key}")
            return True

        except Exception as e:
            logger.error(f"Cache set error: {str(e)}")
            return False

    def health_check(self) -> bool:
        """Check Redis connection health."""
        try:
            return self.redis_client.ping()
        except Exception:
            return False


# Global instance
cache_service = CacheService() 
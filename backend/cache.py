"""
Simple in-memory cache with 24-hour expiration.
Uses Python dict for storage - no external dependencies.
"""

import hashlib
import time
from typing import Any, Optional

# Cache expiration time in seconds (24 hours)
CACHE_EXPIRATION = 24 * 60 * 60  # 86400 seconds


class SimpleCache:
    """
    Simple dictionary-based cache with timestamp-based expiration.
    Thread-safe for basic operations.
    """

    def __init__(self):
        self._cache = {}

    def _generate_key(self, topic: str) -> str:
        """
        Generate a cache key from a research topic.
        Normalizes the topic (lowercase, trimmed) and hashes it.
        """
        normalized = topic.lower().strip()
        return hashlib.md5(normalized.encode()).hexdigest()

    def get(self, topic: str) -> Optional[dict]:
        """
        Retrieve cached results for a topic if not expired.

        Args:
            topic: Research topic string

        Returns:
            Cached results dict or None if not found/expired
        """
        key = self._generate_key(topic)

        if key not in self._cache:
            return None

        entry = self._cache[key]
        current_time = time.time()

        # Check if cache entry has expired
        if current_time - entry['timestamp'] > CACHE_EXPIRATION:
            # Remove expired entry
            del self._cache[key]
            return None

        return entry['results']

    def set(self, topic: str, results: dict) -> None:
        """
        Store results in cache with current timestamp.

        Args:
            topic: Research topic string
            results: Results dictionary to cache
        """
        key = self._generate_key(topic)

        self._cache[key] = {
            'results': results,
            'timestamp': time.time()
        }

    def clear_expired(self) -> int:
        """
        Remove all expired entries from cache.

        Returns:
            Number of entries removed
        """
        current_time = time.time()
        expired_keys = []

        for key, entry in self._cache.items():
            if current_time - entry['timestamp'] > CACHE_EXPIRATION:
                expired_keys.append(key)

        for key in expired_keys:
            del self._cache[key]

        return len(expired_keys)

    def clear_all(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()

    def size(self) -> int:
        """Return number of items in cache."""
        return len(self._cache)


# Global cache instance
cache = SimpleCache()

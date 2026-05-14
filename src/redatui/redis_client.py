import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Union

import redis
from redis import Redis


logger = logging.getLogger(__name__)


class RedisClient:
    """Async-friendly wrapper around redis-py for TUI operations."""

    def __init__(self, host: str, port: int, db: int, password: Optional[str] = None):
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.client: Optional[Redis] = None
        self._connect()

    def _connect(self) -> None:
        """Connect to Redis instance."""
        try:
            self.client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=True,
            )
            self.client.ping()
            logger.info(f"Connected to Redis at {self.host}:{self.port}/{self.db}")
        except redis.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    async def list_keys(self, pattern: str = "*") -> List[str]:
        """Async wrapper to list keys matching pattern."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._list_keys, pattern)

    def _list_keys(self, pattern: str = "*") -> List[str]:
        """List keys matching pattern (blocking)."""
        if not self.client:
            return []
        try:
            return self.client.keys(pattern)
        except Exception as e:
            logger.error(f"Failed to list keys: {e}")
            return []

    async def get_key_data(self, key: str) -> Optional[Dict[str, Any]]:
        """Async wrapper to fetch key data and metadata."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._get_key_data, key)

    def _get_key_data(self, key: str) -> Optional[Dict[str, Any]]:
        """Fetch key data and metadata (blocking)."""
        if not self.client:
            return None

        try:
            key_type = self.client.type(key)
            ttl = self.client.ttl(key)
            pttl = self.client.pttl(key)

            data = {
                "key": key,
                "type": key_type,
                "ttl": ttl if ttl != -1 else None,
                "pttl": pttl if pttl != -1 else None,
                "value": None,
            }

            if key_type == "string":
                data["value"] = self.client.get(key)
            elif key_type == "hash":
                data["value"] = self.client.hgetall(key)
            elif key_type == "list":
                data["value"] = self.client.lrange(key, 0, -1)
            elif key_type == "set":
                data["value"] = list(self.client.smembers(key))
            elif key_type == "zset":
                data["value"] = self.client.zrange(key, 0, -1, withscores=True)
            elif key_type == "stream":
                data["value"] = self.client.xrange(key)
            elif key_type == "json":
                try:
                    data["value"] = json.loads(self.client.get(key) or "{}")
                except json.JSONDecodeError:
                    data["value"] = self.client.get(key)

            return data

        except Exception as e:
            logger.error(f"Failed to fetch key data for {key}: {e}")
            return None

    async def delete_key(self, key: str) -> bool:
        """Async wrapper to delete a key."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._delete_key, key)

    def _delete_key(self, key: str) -> bool:
        """Delete key (blocking)."""
        if not self.client:
            return False
        try:
            result = self.client.delete(key)
            logger.info(f"Deleted key: {key}")
            return result > 0
        except Exception as e:
            logger.error(f"Failed to delete key {key}: {e}")
            return False

    async def get_info(self) -> Dict[str, Any]:
        """Async wrapper to fetch Redis info."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._get_info)

    def _get_info(self) -> Dict[str, Any]:
        """Fetch Redis server info (blocking)."""
        if not self.client:
            return {}
        try:
            info = self.client.info()
            return {
                "version": info.get("redis_version", "unknown"),
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory_human", "0B"),
                "total_keys": self.client.dbsize(),
            }
        except Exception as e:
            logger.error(f"Failed to fetch info: {e}")
            return {}

    def close(self) -> None:
        """Close Redis connection."""
        if self.client:
            self.client.close()
            logger.info("Closed Redis connection")

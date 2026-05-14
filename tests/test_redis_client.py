import pytest
from unittest.mock import MagicMock, patch

from redatui.redis_client import RedisClient


@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    with patch("redatui.redis_client.redis.Redis") as mock:
        yield mock.return_value


class TestRedisClient:
    def test_connection(self, mock_redis):
        """Test successful connection."""
        mock_redis.ping.return_value = True

        client = RedisClient("localhost", 6379, 0)

        assert client.host == "localhost"
        assert client.port == 6379
        assert client.db == 0

    def test_connection_error(self, mock_redis):
        """Test connection failure."""
        import redis
        mock_redis.ping.side_effect = redis.ConnectionError("Connection refused")

        with pytest.raises(redis.ConnectionError):
            RedisClient("localhost", 6379, 0)

    def test_list_keys(self, mock_redis):
        """Test listing keys."""
        mock_redis.keys.return_value = ["user:1", "user:2", "session:abc"]

        client = RedisClient("localhost", 6379, 0)
        keys = client._list_keys()

        assert len(keys) == 3
        assert "user:1" in keys

    def test_get_string_key(self, mock_redis):
        """Test fetching string key."""
        mock_redis.type.return_value = "string"
        mock_redis.ttl.return_value = 3600
        mock_redis.pttl.return_value = 3600000
        mock_redis.get.return_value = "hello"

        client = RedisClient("localhost", 6379, 0)
        data = client._get_key_data("greeting")

        assert data["key"] == "greeting"
        assert data["type"] == "string"
        assert data["value"] == "hello"
        assert data["ttl"] == 3600

    def test_get_hash_key(self, mock_redis):
        """Test fetching hash key."""
        mock_redis.type.return_value = "hash"
        mock_redis.ttl.return_value = -1
        mock_redis.pttl.return_value = -1
        mock_redis.hgetall.return_value = {"name": "Alice", "age": "30"}

        client = RedisClient("localhost", 6379, 0)
        data = client._get_key_data("user:1")

        assert data["type"] == "hash"
        assert data["value"] == {"name": "Alice", "age": "30"}
        assert data["ttl"] is None

    def test_delete_key(self, mock_redis):
        """Test deleting key."""
        mock_redis.delete.return_value = 1

        client = RedisClient("localhost", 6379, 0)
        result = client._delete_key("somekey")

        assert result is True
        mock_redis.delete.assert_called_once_with("somekey")

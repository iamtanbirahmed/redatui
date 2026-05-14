import pytest
from unittest.mock import MagicMock, patch

from redatui.app import RedatuiApp


@pytest.fixture
def mock_redis_client():
    """Mock Redis client."""
    with patch("redatui.app.RedisClient") as mock:
        instance = MagicMock()
        mock.return_value = instance
        yield instance


class TestRedatuiApp:
    def test_app_initialization(self, mock_redis_client):
        """Test app initialization with config."""
        config = {
            "host": "localhost",
            "port": 6379,
            "db": 0,
            "password": None,
        }

        app = RedatuiApp(config)

        assert app.redis_config == config
        assert app.redis_client is None

    def test_app_title(self):
        """Test app title."""
        config = {"host": "localhost", "port": 6379}
        app = RedatuiApp(config)

        assert "Redatui" in app.TITLE
        assert "Redis" in app.TITLE

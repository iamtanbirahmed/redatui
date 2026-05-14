import logging
from typing import Any, Dict, Optional

from textual.app import ComposeResult, CSSFile, Widgets
from textual.app import App as TextualApp

from .redis_client import RedisClient
from .screens import KeyBrowserScreen


logger = logging.getLogger(__name__)


class RedatuiApp(TextualApp):
    """Main Textual application for Redatui."""

    TITLE = "Redatui — Redis TUI Client"
    SUB_TITLE = "Key browser and data viewer"

    DEFAULT_CSS = """
    Screen {
        background: $surface;
        color: $text;
    }

    #key-panel {
        width: 35%;
    }

    #data-viewer {
        width: 65%;
    }

    InfoBar {
        background: $accent 20%;
        color: $text;
    }
    """

    BINDINGS = [
        ("ctrl+c", "quit", "Quit"),
    ]

    def __init__(self, redis_config: Dict[str, Any]):
        super().__init__()
        self.redis_config = redis_config
        self.redis_client: Optional[RedisClient] = None

    def on_mount(self) -> None:
        """Initialize Redis connection and display screen."""
        try:
            self.redis_client = RedisClient(
                host=self.redis_config.get("host", "127.0.0.1"),
                port=self.redis_config.get("port", 6379),
                db=self.redis_config.get("db", 0),
                password=self.redis_config.get("password"),
            )

            screen = KeyBrowserScreen(self.redis_client)
            self.install_screen(screen, name="key-browser")
            self.switch_screen("key-browser")

            logger.info("Redatui app started")

        except Exception as e:
            logger.error(f"Failed to initialize app: {e}")
            self.exit(message=f"Connection failed: {e}")

    def on_unmount(self) -> None:
        """Clean up on exit."""
        if self.redis_client:
            self.redis_client.close()

    def action_quit(self) -> None:
        """Quit the app."""
        self.exit()

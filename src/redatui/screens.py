import logging
from typing import Optional

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.binding import Binding

from .filters import filter_keys
from .redis_client import RedisClient
from .widgets import DataViewer, InfoBar, NamespaceTree, SearchInput


logger = logging.getLogger(__name__)


class KeyBrowserScreen(Screen):
    """Main screen: left pane with key tree, right pane with data viewer."""

    TITLE = "Redatui — Redis Key Browser"

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("r", "refresh", "Refresh", show=True),
        Binding("slash", "search", "Search", show=True),
        Binding("j", "down", "Down", show=False),
        Binding("k", "up", "Up", show=False),
        Binding("enter", "select_key", "Select", show=True),
        Binding("d", "delete_key", "Delete", show=True),
        Binding("i", "show_info", "Info", show=True),
        Binding("escape", "clear_search", "Clear", show=True),
    ]

    DEFAULT_CSS = """
    Screen {
        layout: grid;
        grid-size: 2 2;
        grid-columns: 1fr 2fr;
        grid-rows: 1fr auto;
    }

    #key-panel {
        border-right: solid $accent;
        height: 100%;
    }

    #search-input {
        dock: top;
        width: 100%;
        height: 1;
    }

    #data-viewer {
        grid-column: 2;
        grid-row: 1;
        overflow: auto;
    }

    #info-bar {
        grid-column: 1 / 3;
        grid-row: 2;
    }
    """

    def __init__(self, redis_client: RedisClient):
        super().__init__()
        self.redis_client = redis_client
        self.all_keys: list[str] = []
        self.filtered_keys: list[str] = []
        self.selected_key: Optional[str] = None
        self.search_pattern: str = ""

    def compose(self) -> ComposeResult:
        """Compose screen layout."""
        with Vertical(id="key-panel"):
            yield SearchInput()
            yield NamespaceTree(self.all_keys)

        yield DataViewer()
        yield InfoBar()

    async def on_mount(self) -> None:
        """Load initial data when screen mounts."""
        await self.refresh_keys()

    async def refresh_keys(self) -> None:
        """Refresh key list from Redis."""
        try:
            self.all_keys = await self.redis_client.list_keys()
            self.filtered_keys = self.all_keys.copy()
            self._update_tree()
            self._update_info_bar()
        except Exception as e:
            logger.error(f"Failed to refresh keys: {e}")
            self._update_info_bar()

    def _update_tree(self) -> None:
        """Update namespace tree with current keys."""
        tree = self.query_one("#namespace-tree", NamespaceTree)
        tree.keys = self.filtered_keys
        tree._build_tree()

    def _update_info_bar(self) -> None:
        """Update info bar with current stats."""
        info_bar = self.query_one("#info-bar", InfoBar)
        connection = f"{self.redis_client.host}:{self.redis_client.port}"
        info_bar.update_stats(len(self.all_keys), len(self.filtered_keys), connection)

    async def action_refresh(self) -> None:
        """Refresh key list."""
        await self.refresh_keys()

    def action_search(self) -> None:
        """Focus search input."""
        search = self.query_one("#search-input", SearchInput)
        search.focus()

    def action_clear_search(self) -> None:
        """Clear search and show all keys."""
        self.search_pattern = ""
        self.filtered_keys = self.all_keys.copy()
        search = self.query_one("#search-input", SearchInput)
        search.value = ""
        self._update_tree()
        self._update_info_bar()

    async def action_select_key(self) -> None:
        """Display selected key in right pane."""
        tree = self.query_one("#namespace-tree", NamespaceTree)
        if not tree.cursor_node:
            return

        # Extract key from tree node label
        label = tree.cursor_node.label.rstrip().split(" ", 1)[-1]
        key = label.lstrip("🔑 ")

        # Find actual key in filtered list
        matching = [k for k in self.filtered_keys if k.endswith(key)]
        if matching:
            self.selected_key = matching[0]
            key_data = await self.redis_client.get_key_data(self.selected_key)

            viewer = self.query_one("#data-viewer", DataViewer)
            if key_data:
                viewer.display_key(self.selected_key, key_data)

    async def action_delete_key(self) -> None:
        """Delete selected key with confirmation."""
        if not self.selected_key:
            return

        # TODO: Add confirmation dialog
        success = await self.redis_client.delete_key(self.selected_key)
        if success:
            await self.refresh_keys()

    def action_show_info(self) -> None:
        """Show connection info."""
        if not self.selected_key:
            return

        # TODO: Show detailed key info in modal/panel
        pass

    def on_input_changed(self, event) -> None:
        """Handle search input changes."""
        if event.input.id == "search-input":
            self.search_pattern = event.input.value
            self.filtered_keys = filter_keys(self.all_keys, self.search_pattern)
            self._update_tree()
            self._update_info_bar()

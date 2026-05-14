import logging
from typing import List

from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Input, Static, Tree
from textual.widgets.tree import TreeNode


logger = logging.getLogger(__name__)


class NamespaceTree(Tree):
    """Tree widget for browsing Redis keys organized by namespace."""

    def __init__(self, keys: List[str], delimiter: str = ":"):
        super().__init__(label="Keys", id="namespace-tree")
        self.keys = keys
        self.delimiter = delimiter
        self._build_tree()

    def _build_tree(self) -> None:
        """Build tree from flat key list using namespace delimiter."""
        root = self.root
        root.children.clear()

        # Build namespace hierarchy
        namespaces: dict = {}
        for key in sorted(self.keys):
            parts = key.split(self.delimiter)
            current = namespaces

            for i, part in enumerate(parts[:-1]):
                if part not in current:
                    current[part] = {}
                current = current[part]

            # Add leaf key
            leaf_key = parts[-1] if parts else key
            current[leaf_key] = key  # Store actual key for reference

        # Render tree
        self._render_namespace(root, namespaces)

    def _render_namespace(self, parent: TreeNode, ns: dict) -> None:
        """Recursively render namespace dict as tree."""
        for name, value in sorted(ns.items()):
            if isinstance(value, dict):
                # Namespace folder
                node = parent.add(f"📁 {name}")
                self._render_namespace(node, value)
            else:
                # Key leaf - add type icon placeholder
                parent.add(f"🔑 {name}")


class SearchInput(Input):
    """Search/filter input with live updates."""

    DEFAULT_CSS = """
    SearchInput {
        height: 1;
        border: solid $accent;
    }
    """

    def __init__(self):
        super().__init__(
            id="search-input",
            placeholder="Search (fuzzy, glob: *key?, regex: /pattern/)",
        )


class InfoBar(Static):
    """Status/info bar showing connection and key stats."""

    DEFAULT_CSS = """
    InfoBar {
        dock: bottom;
        height: 1;
        background: $panel;
        color: $text-muted;
        border-top: solid $accent;
    }
    """

    def __init__(self):
        super().__init__()
        self.id = "info-bar"
        self._update_text()

    def update_stats(self, total_keys: int, filtered_keys: int, connection: str) -> None:
        """Update info display."""
        self.update(
            f"  {connection} • {total_keys} keys • {filtered_keys} shown  "
        )

    def _update_text(self) -> None:
        self.update("  Connecting...  ")


class DataViewer(Static):
    """Right pane for viewing selected key data."""

    DEFAULT_CSS = """
    DataViewer {
        border-left: solid $accent;
        background: $panel;
        padding: 1;
    }
    """

    def __init__(self):
        super().__init__()
        self.id = "data-viewer"
        self._show_empty()

    def _show_empty(self) -> None:
        self.update("Select a key to view its data")

    def display_key(self, key: str, data: dict) -> None:
        """Display key data in right pane."""
        if not data:
            self._show_empty()
            return

        key_type = data.get("type", "unknown")
        value = data.get("value")
        ttl = data.get("ttl")

        output = f"Key: {key}\nType: {key_type}\n"
        if ttl:
            output += f"TTL: {ttl}s\n"
        output += "\n" + self._format_value(value, key_type)

        self.update(output)

    def _format_value(self, value: any, key_type: str) -> str:
        """Format value for display based on type."""
        if value is None:
            return "(empty)"

        if key_type == "string":
            return value
        elif key_type == "hash":
            lines = ["Hash:"]
            for k, v in value.items():
                lines.append(f"  {k}: {v}")
            return "\n".join(lines)
        elif key_type == "list":
            lines = ["List:"]
            for i, item in enumerate(value):
                lines.append(f"  [{i}]: {item}")
            return "\n".join(lines)
        elif key_type == "set":
            lines = ["Set:"]
            for item in sorted(value):
                lines.append(f"  • {item}")
            return "\n".join(lines)
        elif key_type == "zset":
            lines = ["Sorted Set:"]
            for item, score in value:
                lines.append(f"  {item}: {score}")
            return "\n".join(lines)
        elif key_type == "stream":
            lines = ["Stream:"]
            for entry_id, data in value:
                lines.append(f"  {entry_id}: {data}")
            return "\n".join(lines)
        elif key_type == "json":
            import json
            return json.dumps(value, indent=2)
        else:
            return str(value)

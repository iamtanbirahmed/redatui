# redatui

Redis TUI client — keyboard-first key browser and data viewer with Vim keybindings.

Browse Redis keys organized by namespace (`:` delimiter), filter with fuzzy/glob/regex patterns, and inspect all data types (string, hash, list, set, zset, stream, JSON) in a rich right pane.

**Status**: v1 scope — key browser + data viewer, local connections only.

## Installation

```bash
pip install redatui
```

Or from source:

```bash
git clone https://github.com/yourusername/redatui.git
cd redatui
make install
```

## Usage

```bash
# Start redatui
redatui

# Or use the short alias
rdt
```

Connect to a local Redis instance (defaults to `127.0.0.1:6379`). Use the keyboard to navigate keys, search, and inspect data.

## Keybindings

| Key | Action |
|-----|--------|
| `j`/`k` | Navigate keys up/down |
| `/` | Search/filter (fuzzy, glob, regex) |
| `Enter` | Inspect selected key |
| `d` | Delete selected key (with confirmation) |
| `r` | Refresh key list |
| `i` | Show key info (type, TTL, size) |
| `Escape` | Close panels/dialogs |
| `q` | Quit |

## Configuration

redatui stores config at `~/.config/redatui/config.toml`:

```toml
[redis]
host = "127.0.0.1"
port = 6379
db = 0
password = ""

[ui]
theme = "dark"
namespace_delimiter = ":"
```

## Features

- **Namespace Tree** — Keys organized by `:` delimiter with collapsible hierarchy
- **Smart Filtering** — Fuzzy, glob pattern, and regex search
- **Rich Display** — Type icons, TTL, and data size for each key
- **Data Viewer** — Dedicated right pane rendering all Redis data types
  - Strings (plain text + hex)
  - Hashes (key-value table)
  - Lists (indexed rows)
  - Sets/Zsets (with scores)
  - Streams (entry timeline)
  - JSON (syntax-highlighted)
- **Vim Keybindings** — hjkl navigation, motions, and modal commands
- **Async Loading** — Non-blocking I/O for responsive UI

## Development

```bash
# Install with dev dependencies
make dev

# Run tests
make test

# Run with debug logging
make debug

# Format and lint
make format
make lint
```

## Architecture

```
src/redatui/
├── __init__.py          # Package initialization
├── __main__.py          # Entry point, CLI args, config loading
├── app.py               # TUI app (Textual), screen & widget setup
├── screens.py           # KeyBrowserScreen, DataViewerPane
├── widgets.py           # NamespaceTree, SearchInput, InfoBar
├── redis_client.py      # Redis wrapper (list keys, get data, etc)
├── filters.py           # Fuzzy/glob/regex filter logic
└── config.py            # Config file parsing and defaults

tests/
├── test_app.py          # App init, keybindings, screen switching
├── test_redis_client.py # Redis backend (list keys, data types, etc)
└── test_filters.py      # Filter logic
```

## Requirements

- Python 3.11+
- Redis 6.0+ (local or remote, but v1 is local-only)

## License

MIT. See `LICENSE` for details.

## Contributing

Open an issue or PR. Follow the code style (ruff lint/format).

## Roadmap

**v1.0** (current)
- Key browser with namespace tree
- Data viewer for all Redis types
- Fuzzy/glob/regex filtering
- Vim keybindings
- Config file support

**v2.0** (planned)
- Remote connection dialog
- Key creation/editing
- Key expiration management
- Export/import (RDB, JSON)
- Pub/Sub monitoring

**v3.0** (planned)
- Cluster support
- Sentinel monitoring
- Performance insights
- Batch operations

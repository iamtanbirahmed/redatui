import logging
from pathlib import Path
from typing import Any, Dict

try:
    import toml
except ImportError:
    toml = None  # type: ignore


logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    "redis": {
        "host": "127.0.0.1",
        "port": 6379,
        "db": 0,
        "password": None,
    },
    "ui": {
        "theme": "dark",
        "namespace_delimiter": ":",
    },
}


def get_config_path() -> Path:
    """Get path to config file: ~/.config/redatui/config.toml"""
    config_home = Path.home() / ".config" / "redatui"
    return config_home / "config.toml"


def load_config() -> Dict[str, Any]:
    """Load config from ~/.config/redatui/config.toml, merging with defaults."""
    if toml is None:
        logger.warning("toml module not found, using default config")
        return DEFAULT_CONFIG.copy()

    config_path = get_config_path()

    if not config_path.exists():
        logger.debug(f"Config file not found at {config_path}, using defaults")
        return DEFAULT_CONFIG.copy()

    try:
        user_config = toml.load(config_path)
        logger.debug(f"Loaded config from {config_path}")

        # Merge with defaults (user config overrides defaults)
        merged = DEFAULT_CONFIG.copy()
        for section in user_config:
            if section in merged:
                merged[section].update(user_config[section])
            else:
                merged[section] = user_config[section]

        return merged

    except Exception as e:
        logger.error(f"Failed to load config from {config_path}: {e}")
        return DEFAULT_CONFIG.copy()


def save_config(config: Dict[str, Any]) -> None:
    """Save config to ~/.config/redatui/config.toml"""
    if toml is None:
        logger.warning("toml module not found, cannot save config")
        return

    config_path = get_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(config_path, "w") as f:
            toml.dump(config, f)
        logger.debug(f"Saved config to {config_path}")
    except Exception as e:
        logger.error(f"Failed to save config to {config_path}: {e}")

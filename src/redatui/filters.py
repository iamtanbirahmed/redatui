import fnmatch
import logging
import re
from collections.abc import Callable

logger = logging.getLogger(__name__)


def fuzzy_match(pattern: str, text: str) -> bool:
    """Check if text matches pattern using fuzzy matching.

    Matches if all characters in pattern appear in text in order.
    Case-insensitive.
    """
    pattern = pattern.lower()
    text = text.lower()
    pattern_idx = 0

    for char in text:
        if pattern_idx < len(pattern) and char == pattern[pattern_idx]:
            pattern_idx += 1

    return pattern_idx == len(pattern)


def glob_match(pattern: str, text: str) -> bool:
    """Check if text matches glob pattern (fnmatch).

    Supports * and ? wildcards.
    """
    return fnmatch.fnmatch(text, pattern)


def regex_match(pattern: str, text: str) -> bool:
    """Check if text matches regex pattern."""
    try:
        return bool(re.search(pattern, text))
    except re.error as e:
        logger.warning(f"Invalid regex pattern '{pattern}': {e}")
        return False


def get_filter_function(pattern: str) -> Callable[[str], bool]:
    """Determine filter type from pattern and return matching function.

    Logic:
    - If pattern starts with /, use regex
    - Else if pattern contains * or ?, use glob
    - Else use fuzzy match
    """
    if pattern.startswith("/") and pattern.endswith("/"):
        regex_pattern = pattern[1:-1]
        return lambda text: regex_match(regex_pattern, text)
    elif "*" in pattern or "?" in pattern:
        return lambda text: glob_match(pattern, text)
    else:
        return lambda text: fuzzy_match(pattern, text)


def filter_keys(keys: list[str], pattern: str) -> list[str]:
    """Filter list of keys by pattern."""
    if not pattern.strip():
        return keys

    filter_fn = get_filter_function(pattern)
    return [key for key in keys if filter_fn(key)]

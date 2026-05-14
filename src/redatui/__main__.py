import argparse
import logging
import sys
from pathlib import Path

from .app import RedatuiApp
from .config import load_config


def setup_logging(debug: bool = False) -> None:
    log_level = logging.DEBUG if debug else logging.WARNING
    log_file = Path("redatui.log")

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.setLevel(log_level)
    logger.addHandler(file_handler)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="redatui",
        description="Redis TUI client — keyboard-first key browser and data viewer",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging to redatui.log",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Redis host (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=6379,
        help="Redis port (default: 6379)",
    )
    parser.add_argument(
        "--db",
        type=int,
        default=0,
        help="Redis database (default: 0)",
    )

    args = parser.parse_args()
    setup_logging(args.debug)

    try:
        config = load_config()

        # CLI args override config file
        redis_config = config.get("redis", {})
        redis_config.update({
            "host": args.host if args.host != "127.0.0.1" else redis_config.get("host", "127.0.0.1"),
            "port": args.port if args.port != 6379 else redis_config.get("port", 6379),
            "db": args.db if args.db != 0 else redis_config.get("db", 0),
        })

        app = RedatuiApp(redis_config)
        app.run()

    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.exception(f"Unhandled exception: {e}")
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

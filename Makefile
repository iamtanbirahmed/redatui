.PHONY: help install dev lint test run debug clean

help:
	@echo "Redatui development commands:"
	@echo "  make install   - Install project with dev dependencies"
	@echo "  make dev       - Install in editable mode"
	@echo "  make lint      - Run ruff linter"
	@echo "  make format    - Format code with ruff"
	@echo "  make test      - Run tests"
	@echo "  make run       - Run redatui"
	@echo "  make debug     - Run with debug logging"
	@echo "  make clean     - Clean build artifacts"

install:
	uv sync

dev:
	uv sync --all-extras

lint:
	uv run ruff check src/ tests/

format:
	uv run ruff format src/ tests/

test:
	uv run pytest tests/ -v

test-watch:
	uv run pytest tests/ -v --tb=short -x

run:
	uv run python -m redatui

debug:
	uv run python -m redatui --debug

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf build/ dist/ *.egg-info .pytest_cache .mypy_cache

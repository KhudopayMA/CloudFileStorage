uv sync --frozen
uv run ruff check .
uv run ruff format
uv run mypy .
uv run typos


uv sync --frozen
uv run ruff check .
uv run ruff format
uv run mypy .
uv run typos
uv run pytest --cov=. --cov-fail-under=90 --cov-report=term-missing

# Leadsheet - Just command runner
# Run `just --list` to see all available commands.

# Install all dependencies (including dev) into the virtual environment
setup:
    uv sync

# Run the full test suite
test:
    uv run pytest tests/

# Run pyright type checker
typecheck:
    uv run pyright

# Run ruff linter and format check
lint:
    uv run ruff check .
    uv run ruff format --check .

# Run all checks (typecheck, lint, and format)
check:
    just typecheck
    just lint

# Auto-fix lint issues and format code
fix:
    uv run ruff check --fix .
    uv run ruff format .

# Build example PDF and PNG
build-examples:
    uv run python -m leadsheet "examples/No Escape.tex" "examples/No Escape" --format pdf png

# Build a distributable wheel and sdist
build:
    uv build

# Remove build artifacts and caches
clean:
    rm -rf dist/ .pytest_cache/ __pycache__/ leadsheet/__pycache__/ tests/__pycache__/
    find . -name "*.pyc" -delete

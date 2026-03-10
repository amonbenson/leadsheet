# Leadsheet - Just command runner
# Run `just --list` to see all available commands.

# Install all dependencies (including dev) into the virtual environment
setup:
    uv sync

# Run the full test suite
test:
    uv run pytest tests/

# Run ruff linter
lint:
    uv run ruff check .

# Run ruff formatter check (no changes)
lint-format:
    uv run ruff format --check .

# Auto-fix lint issues and format code
format:
    uv run ruff check --fix .
    uv run ruff format .

# Convert example PDF to PNG
build-examples:
    uv run python -m leadsheet examples/maniac.tex examples/maniac --format png

# Build a distributable wheel and sdist
build:
    uv build

# Remove build artifacts and caches
clean:
    rm -rf dist/ .pytest_cache/ __pycache__/ leadsheet/__pycache__/ tests/__pycache__/
    find . -name "*.pyc" -delete

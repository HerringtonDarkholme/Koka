# Koka

A Python package built with modern tooling.

## Installation

```bash
# Install the package
pip install koka

# Install with development dependencies
pip install koka[dev]
```

## Development Setup

This project uses [uv](https://github.com/astral-sh/uv) for package management.

```bash
# Install dependencies
uv sync --dev

# Activate virtual environment
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows
```

## Development Commands

### Linting

```bash
# Run linting checks
uv run ruff check .

# Auto-fix linting issues
uv run ruff check --fix .
```

### Formatting

```bash
# Format code
uv run ruff format .

# Check formatting without making changes
uv run ruff format --check .
```

### Type Checking

```bash
# Run type checking
uv run pyright

# Run type checking on specific files
uv run pyright src/koka/example.py

# Check types in watch mode
uv run pyright --watch
```

### Testing

```bash
# Run tests
uv run pytest

# Run tests with coverage report
uv run pytest --cov=koka --cov-report=html

# Run specific test file
uv run pytest tests/test_example.py
```

### Run All Checks

```bash
# Run all checks (linting, type checking, and tests)
uv run ruff check . && uv run pyright && uv run pytest
```

## Project Structure

```
koka/
├── src/
│   └── koka/           # Main package
│       ├── __init__.py
│       └── example.py
├── tests/              # Test files
│   └── test_example.py
├── pyproject.toml      # Project configuration
├── LICENSE
└── README.md
```

## License

MIT

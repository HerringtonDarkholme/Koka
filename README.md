# Koka

**Algebraic Effects for Python** - A lightweight library for effect-based programming inspired by the [Koka language](https://koka-lang.github.io/).

Koka enables:
- 🎯 **Type-safe dependency injection** using effect handlers
- 🚨 **Typed error handling** with pattern matching (no exceptions!)
- 🔗 **Effect composition** - effects can call other effects
- 🎨 **Functional style** - immutable handlers, pure functions

Requires Python 3.13+ (uses modern type parameter syntax)

## Quick Start

```python
from koka import Dep, Err, Koka

# Define a dependency
class Database:
    def get_user(self, id: str):
        return {"id": id, "name": "Alice"}
# Define an error type
class UserNotFound(Exception): pass

# Write an effect that uses dependencies and can fail
def get_user_name(user_id: str):
    if not user_id:
        return (yield from Err(UserNotFound("Empty ID")))
    db = yield from Dep(Database)  # Request dependency
    user = db.get_user(user_id)
    return user["name"]

# Set up dependencies and run the effect
result = Koka().provide(Database()).run(get_user_name("123"))

# Pattern match is statically typed
match result:
    case UserNotFound() as e:
        print(f"Error: {e}")
    case name:
        print(f"User: {name}")  # Output: User: Alice
```

## Installation

```bash
# Note: Not yet published to PyPI
# For now, install from source:
git clone https://github.com/HerringtonDarkholme/koka
cd koka
uv sync --all-extras
```

## Core Concepts

### Effects

An effect is a generator function that can `yield from` effect objects to request capabilities:

```python
def my_effect():
    config = yield from Dep(Config)  # Request a dependency
    if config.invalid:
        return (yield from Err(ValidationError()))  # Signal an error
    return config.value
```

### Effect Types

**`Dep[T]`** - Dependency injection effect
```python
db = yield from Dep(Database)  # Request a Database instance
```

**`Err[E]`** - Error effect (alternative to exceptions)
```python
return (yield from Err(NotFoundError("Resource not found")))
```

### Effect Handlers

The `Koka` class provides and handles effects:

```python
result = (
    Koka()
    .provide(Database())      # Provide a Database instance
    .provide(AuthService())   # Provide an AuthService instance
    .run(my_effect())        # Run the effect
)
```

Returns either the success value or an error, which you can pattern match:

```python
match result:
    case ValidationError():
        print("Validation failed")
    case NotFoundError():
        print("Not found")
    case value:
        print(f"Success: {value}")
```

## Examples

See the [`examples/`](examples/) directory for complete examples:

- [`01_basic_di.py`](examples/01_basic_di.py) - Basic dependency injection
- [`02_error_handling.py`](examples/02_error_handling.py) - Typed error handling with pattern matching
- [`03_composition.py`](examples/03_composition.py) - Composing effects together

Run examples:
```bash
uv run python examples/01_basic_di.py
```

## Development Setup

This project uses [uv](https://github.com/astral-sh/uv) for package management.

```bash
# Install dependencies
uv sync --all-extras

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

## Why Koka?

The answer can be found in effect.ts homepage. To summarize, make as much type checked and compiler managed as possible.

## Project Structure

```
koka/
├── src/
│   └── koka/           # Main package
│       └── __init__.py # Core effect system
├── tests/              # Test files
│   ├── test_koka.py    # Integration example
│   └── test_unit.py    # Unit tests
├── examples/           # Example scripts
│   ├── 01_basic_di.py
│   ├── 02_error_handling.py
│   └── 03_composition.py
├── pyproject.toml      # Project configuration
├── LICENSE
└── README.md
```

## API Reference

### `Koka[K]`

Effect handler runtime.

**Methods:**
- `provide[N](instance: N) -> Koka[Dep[N] | K]` - Register a dependency
- `run[E, T](eff: Eff[K | E, T]) -> T | E` - Execute an effect computation

### `Dep[T]`

Dependency injection effect.

**Usage:** `value = yield from Dep(MyClass)`

### `Err[E: Exception]`

Error effect for typed error handling.

**Usage:** `return (yield from Err(MyError()))`

### `Eff[K, R]`

Type alias for effect computations: `Generator[K, Never, R]`

## Inspiration & Credits

This project draws inspiration from several excellent projects in the algebraic effects and functional programming space:

### 🌟 Primary Inspirations

- **[Koka Language](https://github.com/koka-lang/koka)** - The pioneering research language for algebraic effect handlers by Daan Leijen. Koka's elegant design of effect types and handlers is the foundation for this library's approach to effects in Python.

- **[Effect-TS](https://effect.website/)** - A powerful effect system for TypeScript that brings functional programming patterns to the JavaScript ecosystem. Effect-TS demonstrates how algebraic effects can be practical and ergonomic in mainstream languages.

### 💡 Related Projects

- **[koka-ts](https://github.com/koka-ts/koka)** - TypeScript implementation of Koka-style effect handlers, showing how these concepts can be adapted to languages with different type systems.

- **[stateless](https://github.com/suned/stateless/)** - A Python library for building type-safe, composable state machines and effects. Demonstrates how generator-based effects can work elegantly in Python.

### 🙏 Acknowledgments

Special thanks to:
- **Daan Leijen** for the groundbreaking research on algebraic effects in Koka
- The **Effect-TS** team for showing how effects can be practical and developer-friendly
- The maintainers of **koka-ts** and **stateless** for exploring effect systems in TypeScript and Python

This project stands on the shoulders of giants. While it's a toy implementation for learning and fun, it aims to bring some of the elegance of Koka-style effects to modern Python.

## Contributing

This is a toy project for fun and learning! Feel free to:
- Open issues with questions or ideas
- Submit PRs with improvements
- Fork and experiment

## License

MIT

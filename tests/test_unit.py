"""Unit tests for the Koka effect system."""

import pytest

from koka import Dep, Err, Koka


# Test fixtures and helper classes
class Config:
    def __init__(self, value: str = "test-config"):
        self.value = value


class Database:
    def __init__(self, data: dict[str, str] | None = None):
        self.data = data or {"user1": "Alice", "user2": "Bob"}

    def get(self, key: str) -> str | None:
        return self.data.get(key)


class NotFoundError(Exception):
    pass


class ValidationError(Exception):
    pass


# Test: Basic dependency injection
def test_dep_single_dependency():
    """Test requesting a single dependency."""

    def get_config_value():
        config = yield from Dep(Config)
        return config.value

    result = Koka().provide(Config("my-value")).run(get_config_value())
    assert result == "my-value"


def test_dep_multiple_dependencies():
    """Test requesting multiple dependencies in sequence."""

    def use_both():
        config = yield from Dep(Config)
        db = yield from Dep(Database)
        return f"{config.value}-{db.get('user1')}"

    result = (
        Koka()
        .provide(Config("app"))
        .provide(Database())
        .run(use_both())
    )
    assert result == "app-Alice"


def test_dep_same_dependency_multiple_times():
    """Test requesting the same dependency multiple times."""

    def use_config_twice():
        config1 = yield from Dep(Config)
        config2 = yield from Dep(Config)
        return config1.value == config2.value

    result = Koka().provide(Config()).run(use_config_twice())
    assert result is True


def test_dep_missing_dependency():
    """Test that missing dependency raises RuntimeError."""

    def needs_config():
        config = yield from Dep(Config)
        return config.value

    with pytest.raises(RuntimeError, match="No handler provided for dependency: Config"):
        Koka().run(needs_config())


# Test: Error handling
def test_err_basic():
    """Test basic error effect."""

    def failing():
        yield from Err(ValidationError("bad input"))

    result = Koka().run(failing())
    assert isinstance(result, ValidationError)
    assert str(result) == "bad input"


def test_err_early_return():
    """Test that error stops execution early."""
    executed = []

    def partial_execution():
        executed.append(1)
        yield from Err(ValidationError("error"))
        executed.append(2)  # Should never execute

    result = Koka().run(partial_execution())
    assert isinstance(result, ValidationError)
    assert executed == [1]  # Second append never happened


def test_err_with_deps():
    """Test error handling combined with dependency injection."""

    def validate_and_use_db(key: str):
        if not key:
            return (yield from Err(ValidationError("empty key")))
        db = yield from Dep(Database)
        value = db.get(key)
        if value is None:
            return (yield from Err(NotFoundError(f"{key} not found")))
        return value

    # Test successful path
    result = Koka().provide(Database()).run(validate_and_use_db("user1"))
    assert result == "Alice"

    # Test validation error
    result = Koka().provide(Database()).run(validate_and_use_db(""))
    assert isinstance(result, ValidationError)

    # Test not found error
    result = Koka().provide(Database()).run(validate_and_use_db("user999"))
    assert isinstance(result, NotFoundError)


# Test: Effect composition
def test_effect_calling_effect():
    """Test that effects can call other effects."""

    def inner_effect():
        config = yield from Dep(Config)
        return config.value

    def outer_effect():
        value = yield from inner_effect()
        return f"wrapped-{value}"

    result = Koka().provide(Config("test")).run(outer_effect())
    assert result == "wrapped-test"


def test_nested_error_propagation():
    """Test that errors propagate through nested effects."""

    def inner():
        yield from Err(ValidationError("inner error"))

    def outer():
        result = yield from inner()
        return result  # Should never reach here

    result = Koka().run(outer())
    assert isinstance(result, ValidationError)
    assert str(result) == "inner error"


# Test: Koka immutability
def test_koka_immutability():
    """Test that provide() returns a new Koka instance."""
    k1 = Koka()
    k2 = k1.provide(Config())

    assert k1 is not k2
    # k1 should still have no handlers
    with pytest.raises(RuntimeError):
        def needs_config():
            config = yield from Dep(Config)
            return config.value
        k1.run(needs_config())


def test_koka_chaining():
    """Test that multiple provide() calls can be chained."""

    def use_all():
        config = yield from Dep(Config)
        db = yield from Dep(Database)
        return f"{config.value}-{db.get('user2')}"

    result = (
        Koka()
        .provide(Config("chain"))
        .provide(Database())
        .run(use_all())
    )
    assert result == "chain-Bob"


# Test: Return values
def test_simple_return():
    """Test returning a simple value without effects."""

    def simple():
        return 42
        yield  # Make it a generator

    result = Koka().run(simple())
    assert result == 42


def test_none_return():
    """Test returning None."""

    def returns_none():
        _ = yield from Dep(Config)
        return None

    result = Koka().provide(Config()).run(returns_none())
    assert result is None


# Test: Pattern matching
def test_pattern_matching():
    """Test that errors can be pattern matched."""

    def maybe_fail(should_fail: bool):
        if should_fail:
            return (yield from Err(ValidationError("failed")))
        return "success"

    # Success case
    result = Koka().run(maybe_fail(False))
    match result:
        case ValidationError():
            pytest.fail("Should not be an error")
        case value:
            assert value == "success"

    # Error case
    result = Koka().run(maybe_fail(True))
    match result:
        case ValidationError() as e:
            assert str(e) == "failed"
        case _:
            pytest.fail("Should be an error")

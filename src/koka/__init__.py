"""
Koka - Algebraic Effects for Python

A lightweight library for effect-based programming inspired by the Koka language.
Provides dependency injection and typed error handling through algebraic effects.
"""

from collections.abc import Generator
from typing import Any, Never, Self

__all__ = ["Koka", "Dep", "Err", "Eff"]

type Eff[K, R] = Generator[K, Never, R]
"""Effect type: a generator that yields effects of type K and returns R."""


class Koka[K = Never]:
    """
    Effect handler runtime that manages and executes effects.

    The Koka class provides a functional API for:
    - Dependency injection via `provide()`
    - Effect execution via `run()`

    Example:
        >>> def get_config():
        ...     config = yield from Dep(Config)
        ...     return config.value
        >>>
        >>> result = Koka().provide(Config()).run(get_config())
    """

    def __init__(self, handlers: dict[type[Any], Any] | None = None) -> None:
        """Initialize the effect handler with an optional handler context."""
        self._handlers: dict[type[Any], Any] = handlers or {}

    def provide[N](self, instance: N) -> "Koka[Dep[N] | K]":
        """
        Register a dependency instance for dependency injection.

        Returns a new Koka instance with the dependency registered,
        following an immutable/functional style.

        Args:
            instance: The dependency instance to provide

        Returns:
            A new Koka handler with the dependency registered

        Example:
            >>> koka = Koka().provide(Database()).provide(AuthService())
        """
        new_handlers = self._handlers.copy()
        new_handlers[type(instance)] = instance
        return Koka(new_handlers)

    def run[E, T](self, eff: Eff[K | E, T]) -> T | E:
        """
        Execute an effect computation, handling all effects it yields.

        This drives the generator forward, handling:
        - Dep[T]: Dependency injection - provides registered instances
        - Err[E]: Error effects - returns the error as a value

        Args:
            eff: The effect computation to execute

        Returns:
            Either the successful result (T) or an error (E)

        Raises:
            RuntimeError: If an effect cannot be handled

        Example:
            >>> result = Koka().provide(Config()).run(my_effect())
            >>> match result:
            ...     case MyError(): print("Error occurred")
            ...     case value: print(f"Success: {value}")
        """
        gen = eff
        value: Any = None

        while True:
            try:
                effect = gen.send(value)

                # Handle Dep[T] - dependency injection
                if isinstance(effect, Dep):
                    dep_type = effect.tpe
                    if dep_type in self._handlers:
                        value = self._handlers[dep_type]
                    else:
                        raise RuntimeError(
                            f"No handler provided for dependency: {dep_type.__name__}"
                        )

                # Handle Err[E] - error effect
                elif isinstance(effect, Exception):
                    return effect  # type: ignore[return-value]

                # Unknown effect
                else:
                    raise RuntimeError(f"Unhandled effect type: {type(effect).__name__}")

            except StopIteration as e:
                # Generator completed successfully
                return e.value


class Dep[T]:
    """
    Dependency injection effect.

    Yields a request for a dependency of type T, which will be provided
    by the Koka runtime if available.

    Example:
        >>> def my_function():
        ...     db = yield from Dep(Database)
        ...     return db.query()
    """

    def __init__(self, tpe: type[T]) -> None:
        """
        Initialize a dependency request.

        Args:
            tpe: The type of dependency to request
        """
        self.tpe = tpe

    def __iter__(self) -> Generator[Self, T, T]:
        """
        Yield this dependency request and return the provided instance.

        Returns:
            The dependency instance provided by the handler
        """
        return (yield self)


class Err[E: Exception]:
    """
    Error effect for typed error handling.

    Yields an error that will be returned as a value by the Koka runtime,
    enabling pattern matching on error types.

    Example:
        >>> def validate(value: str):
        ...     if not value:
        ...         return (yield from Err(ValidationError()))
        ...     return value
    """

    def __init__(self, err: E) -> None:
        """
        Initialize an error effect.

        Args:
            err: The error to yield
        """
        self.error = err

    def __iter__(self) -> Generator[E, Never, Never]:
        """
        Yield this error effect. Never returns normally.

        Raises:
            StopIteration: Never raised, as error propagates
        """
        yield self.error
        raise RuntimeError("Err effect should never return")  # Type system guard

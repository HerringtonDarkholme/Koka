"""
Basic Dependency Injection Example

This example demonstrates how to use Koka for simple dependency injection.
"""

from koka import Dep, Koka


class Logger:
    """A simple logger service."""

    def log(self, message: str) -> None:
        print(f"[LOG] {message}")


class Config:
    """Application configuration."""

    def __init__(self, app_name: str, debug: bool = False):
        self.app_name = app_name
        self.debug = debug


def greet_user(name: str):
    """
    A function that uses dependency injection to access Config and Logger.

    This is an effect - it yields to request dependencies.
    """
    # Request the Config dependency
    config = yield from Dep(Config)

    # Request the Logger dependency
    logger = yield from Dep(Logger)

    # Use the injected dependencies
    if config.debug:
        logger.log(f"Debug mode enabled for {config.app_name}")

    message = f"Hello, {name}! Welcome to {config.app_name}"
    logger.log(message)

    return message


# Set up the effect handler with dependencies
def main():
    print("=== Basic Dependency Injection Example ===\n")

    # Create instances of our dependencies
    config = Config(app_name="Koka Demo", debug=True)
    logger = Logger()

    # Provide dependencies and run the effect
    result = (
        Koka()
        .provide(config)
        .provide(logger)
        .run(greet_user("Alice"))
    )

    print(f"\nResult: {result}")


if __name__ == "__main__":
    main()

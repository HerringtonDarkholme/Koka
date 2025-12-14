"""
Typed Error Handling Example

This example shows how to use Err effects for typed error handling
with pattern matching.
"""

from koka import Dep, Err, Koka


class ValidationError(Exception):
    """Raised when input validation fails."""
    pass


class NotFoundError(Exception):
    """Raised when a resource is not found."""
    pass


class Database:
    """A mock database."""

    def __init__(self):
        self.users = {
            "alice": {"name": "Alice", "email": "alice@example.com"},
            "bob": {"name": "Bob", "email": "bob@example.com"},
        }

    def find_user(self, user_id: str):
        """Look up a user in the database."""
        if user_id in self.users:
            return self.users[user_id]
        return None


def get_user_email(user_id: str):
    """
    Fetch a user's email with validation and error handling.

    This effect can yield:
    - ValidationError if the input is invalid
    - NotFoundError if the user doesn't exist
    - Or return the email address on success
    """
    # Validate input
    if not user_id:
        return (yield from Err(ValidationError("User ID cannot be empty")))

    if not user_id.isalpha():
        return (yield from Err(ValidationError("User ID must contain only letters")))

    # Get database dependency
    db = yield from Dep(Database)

    # Look up user
    user = db.find_user(user_id.lower())
    if user is None:
        return (yield from Err(NotFoundError(f"User '{user_id}' not found")))

    # Return the email
    return user["email"]


def main():
    print("=== Typed Error Handling Example ===\n")

    db = Database()
    koka = Koka().provide(db)

    # Test cases
    test_cases = [
        ("alice", "✓ Valid user"),
        ("", "✗ Empty ID"),
        ("alice123", "✗ Invalid characters"),
        ("charlie", "✗ Non-existent user"),
    ]

    for user_id, description in test_cases:
        print(f"{description}: user_id='{user_id}'")
        result = koka.run(get_user_email(user_id))

        # Pattern match on the result
        match result:
            case ValidationError() as e:
                print(f"  → Validation error: {e}\n")
            case NotFoundError() as e:
                print(f"  → Not found: {e}\n")
            case email:
                print(f"  → Success! Email: {email}\n")


if __name__ == "__main__":
    main()

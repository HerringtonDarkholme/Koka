"""
Effect Composition Example

This example demonstrates how effects can call other effects,
creating a composable architecture.
"""

from koka import Dep, Err, Koka


class AuthError(Exception):
    """Raised when authentication fails."""
    pass


class PermissionError(Exception):
    """Raised when user lacks permissions."""
    pass


class Auth:
    """Authentication service."""

    def __init__(self):
        self.tokens = {
            "token-123": "alice",
            "token-456": "bob",
        }

    def verify_token(self, token: str) -> str | None:
        """Verify a token and return the username."""
        return self.tokens.get(token)


class UserStore:
    """User data store."""

    def __init__(self):
        self.users = {
            "alice": {"role": "admin"},
            "bob": {"role": "user"},
        }

    def get_user(self, username: str):
        """Get user data."""
        return self.users.get(username)


# Effect: Authenticate user
def authenticate(token: str):
    """Authenticate a user by token."""
    auth = yield from Dep(Auth)
    username = auth.verify_token(token)

    if username is None:
        return (yield from Err(AuthError("Invalid token")))

    return username


# Effect: Check if user is admin
def require_admin(username: str):
    """Check if user has admin role."""
    store = yield from Dep(UserStore)
    user = store.get_user(username)

    if user is None or user["role"] != "admin":
        return (yield from Err(PermissionError(f"User {username} is not an admin")))

    return user


# Effect: Protected operation that composes other effects
def delete_user(token: str, target_username: str):
    """
    Delete a user (admin only).

    This effect composes multiple other effects:
    1. authenticate() - verify the token
    2. require_admin() - check admin permission
    3. Perform the deletion
    """
    # Authenticate the requesting user
    username = yield from authenticate(token)
    print(f"  Authenticated as: {username}")

    # Check admin permission
    user = yield from require_admin(username)
    print(f"  Verified admin role: {user['role']}")

    # Perform the deletion (mocked)
    print(f"  Deleting user: {target_username}")
    return f"User {target_username} deleted by {username}"


def main():
    print("=== Effect Composition Example ===\n")

    # Set up dependencies
    koka = Koka().provide(Auth()).provide(UserStore())

    # Test case 1: Admin deleting a user
    print("Test 1: Admin user (alice) deleting bob")
    result = koka.run(delete_user("token-123", "bob"))
    match result:
        case AuthError() as e:
            print(f"  ✗ Auth error: {e}\n")
        case PermissionError() as e:
            print(f"  ✗ Permission error: {e}\n")
        case message:
            print(f"  ✓ Success: {message}\n")

    # Test case 2: Non-admin trying to delete
    print("Test 2: Regular user (bob) trying to delete alice")
    result = koka.run(delete_user("token-456", "alice"))
    match result:
        case AuthError() as e:
            print(f"  ✗ Auth error: {e}\n")
        case PermissionError() as e:
            print(f"  ✗ Permission error: {e}\n")
        case message:
            print(f"  ✓ Success: {message}\n")

    # Test case 3: Invalid token
    print("Test 3: Invalid token")
    result = koka.run(delete_user("token-invalid", "bob"))
    match result:
        case AuthError() as e:
            print(f"  ✗ Auth error: {e}\n")
        case PermissionError() as e:
            print(f"  ✗ Permission error: {e}\n")
        case message:
            print(f"  ✓ Success: {message}\n")


if __name__ == "__main__":
    main()

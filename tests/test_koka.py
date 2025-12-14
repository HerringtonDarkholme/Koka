from koka import Dep, Eff, Err, Koka


class User:
    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name

    def __repr__(self) -> str:
        return f"User(id={self.id}, name={self.name})"


class InvalidUserName(Exception):
    pass


class UserNotFound(Exception):
    pass


class AuthService:
    def get_token(self) -> str:
        return "token-12345"


class UserDatabase:
    def get_user(self, token: str, id: str) -> Eff[UserNotFound, User]:
        # Simulate database lookup
        if id == "123":
            return User(id, "Alice")
        else:
            return (yield from Err(UserNotFound(f"User {id} not found")))


def get_user(id: str):
    if not id:
        return (yield from Err(InvalidUserName()))
    auth = yield from Dep(AuthService)
    token = auth.get_token()
    db = yield from Dep(UserDatabase)
    user = yield from db.get_user(token, id)
    return user


# Test 1: Successful user retrieval
print("Test 1: Valid user ID")
a = get_user("123")
ret = Koka().provide(AuthService()).provide(UserDatabase()).run(a)

match ret:
    case InvalidUserName():
        print("  ❌ invalid name")
    case UserNotFound():
        print("  ❌ user not found")
    case user:
        print(f" ✅ find user: {user}")


# Test 2: Empty user ID (validation error)
print("\nTest 2: Empty user ID")
b = get_user("")
ret2 = Koka().provide(AuthService()).provide(UserDatabase()).run(b)

match ret2:
    case InvalidUserName():
        print("  ✅ invalid name (expected)")
    case UserNotFound():
        print("  ❌ user not found")
    case user:
        print(f"  ❌ find user: {user}")


# Test 3: Non-existent user
print("\nTest 3: Non-existent user ID")
c = get_user("999")
ret3 = Koka().provide(AuthService()).provide(UserDatabase()).run(c)

match ret3:
    case InvalidUserName():
        print("  ❌ invalid name")
    case UserNotFound() as e:
        print(f"  ✅ user not found (expected): {e}")
    case user:
        print(f"  ❌ find user: {user}")

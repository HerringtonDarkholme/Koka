from koka import Dep, Err, Eff, Koka

class User: pass

class InvalidUserName(Exception): pass
class UserNotFound(Exception): pass
class AuthService:
    def get_token(self) -> str: ...
class UserDatabase:
    def get_user(self, token: str, id: str) -> Eff[UserNotFound, User]:
        ...



def get_user(id: str):
    if not id:
        return (yield from Err(InvalidUserName()))
    auth = yield from Dep(AuthService)
    token = auth.get_token()
    db = yield from Dep(UserDatabase)
    user = yield from db.get_user(token, id)
    return user


a = get_user("123")
ret = (
  Koka()
  .provide(AuthService())
  .provide(UserDatabase())
).run(a)

match ret:
    case InvalidUserName():
        print("invalid name")
    case UserNotFound():
        print("invalid name")
    case user:
        print(f"find user: {user}")

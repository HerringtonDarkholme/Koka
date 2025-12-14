# This file can be empty but is required for the package to be importable

from typing import Generator, Never, Type, Self

type Eff[K, R] = Generator[K, Never, R]

class Koka[K = Never]:
    def provide[N](self, t: N) -> 'Koka[Dep[N] | K]':
        ...

    def run[E, T](self, eff: Eff[K | E, T]) -> T | E:
        ...


class Dep[T]:
    def __init__(self, tpe: Type[T]) -> None:
        super().__init__()
    def __iter__(self) -> Eff[Self, T]: ...

class Err[E: Exception]:
    error: E
    def __iter__(self) -> Eff[E, Never]: ...
    def __init__(self, err: E) -> None:
        super().__init__()
        self.error = err
    pass

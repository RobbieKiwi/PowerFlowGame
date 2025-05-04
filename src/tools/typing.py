from typing import TypeVar

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")


class IntWrapper(int):
    def as_int(self) -> int:
        return int(self)


from typing import TypeVar

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")


class WrappedInt(int):
    def as_int(self) -> int:
        return int(self)


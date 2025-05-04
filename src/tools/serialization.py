import json
from enum import Enum
from typing import Protocol, Self, runtime_checkable, TypeVar

from src.tools.typing import IntWrapper, T


@runtime_checkable
class Serializable(Protocol):
    def to_simple_dict(self) -> dict: ...

    @classmethod
    def from_simple_dict(cls, simple_dict: dict) -> Self: ...


GenericSerializable = TypeVar("GenericSerializable", bound=Serializable)


def serialize(x: Serializable) -> str:
    return json.dumps(x.to_simple_dict())


def deserialize(x: str, cls: type[GenericSerializable]) -> GenericSerializable:
    return cls.from_simple_dict(json.loads(x))


def simplify_type(x: Enum | IntWrapper | int | float | str) -> int | float | str:
    if isinstance(x, Enum):
        return x.value
    if isinstance(x, IntWrapper):
        return x.as_int()
    if isinstance(x, (int, float, str)):
        return x
    raise TypeError(f"Unsupported type {type(x)}")


def un_simplify_type(x: int | float | str, t: type[T]) -> T:
    if t in [int, float, str]:
        return t(x)
    if issubclass(t, Enum):
        return t(x)
    if issubclass(t, IntWrapper):
        return t(x)
    raise TypeError(f"Unsupported type {t}")

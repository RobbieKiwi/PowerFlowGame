import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Protocol, Self, runtime_checkable, TypeVar

from src.tools.typing import WrappedInt, T

Primitive = int | float | str | bool
SimpleDict = dict[str, Primitive]
primitives = (int, float, str, bool)


@runtime_checkable
class Serializable(Protocol):
    def to_simple_dict(self) -> SimpleDict: ...

    @classmethod
    def from_simple_dict(cls, simple_dict: SimpleDict) -> Self: ...


GenericSerializable = TypeVar("GenericSerializable", bound=Serializable)


def serialize(x: Serializable) -> str:
    return json.dumps(x.to_simple_dict())


def deserialize(x: str, cls: type[GenericSerializable]) -> GenericSerializable:
    return cls.from_simple_dict(json.loads(x))


def simplify_type(x: Enum | WrappedInt | Primitive) -> Primitive:
    if isinstance(x, Enum):
        return x.value
    if isinstance(x, WrappedInt):
        return x.as_int()
    if isinstance(x, primitives):
        return x
    raise TypeError(f"Unsupported type {type(x)}")


def simplify_optional_type(
    x: Enum | WrappedInt | Primitive | None,
) -> Primitive | None:
    if x is None:
        return None
    return simplify_type(x)


def un_simplify_type(x: Primitive, t: type[T]) -> T:
    if t in primitives:
        return t(x)
    if issubclass(t, Enum):
        return t(x)
    if issubclass(t, WrappedInt):
        return t(x)
    raise TypeError(f"Unsupported type {t}")


def un_simplify_optional_type(x: int | float | str | None, t: type[T]) -> T | None:
    if x is None:
        return None
    return un_simplify_type(x, t)


@dataclass(frozen=True)
class SerializableBase(ABC):
    @abstractmethod
    def to_simple_dict(self) -> SimpleDict:
        pass

    @classmethod
    @abstractmethod
    def from_simple_dict(cls, simple_dict: SimpleDict) -> Self:
        pass

from typing import Protocol, Self, runtime_checkable, TypeVar
import json


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

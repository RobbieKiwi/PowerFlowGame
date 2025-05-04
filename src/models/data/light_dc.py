from dataclasses import dataclass
from typing import Self, TypeVar

from src.tools.serialization import simplify_type, un_simplify_type

SimpleDict = dict[str, int | float | str]

@dataclass(frozen=True)
class LightDc:
    # An indexed light weight dataclass with no complex types. It can easily be turned into a row of a dataframe
    id: int

    def to_simple_dict(self) -> SimpleDict:
        return {k: simplify_type(x=v) for k, v in self.__dict__.items()}

    @classmethod
    def from_simple_dict(cls, simple_dict: SimpleDict) -> Self:
        init_dict = {
            k: un_simplify_type(x=simple_dict[k], t=v.type)
            for k, v in cls.__dataclass_fields__.items()   # noqa
        }
        return cls(**init_dict)  # noqa



GenericLightDc = TypeVar("GenericLightDc", bound=LightDc)
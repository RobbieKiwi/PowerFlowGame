from dataclasses import dataclass
from typing import Self

from src.tools.typing import IntWrapper


class PlayerId(IntWrapper):
    @property
    def is_npc(self) -> bool:
        return self == PlayerId.get_npc()

    @classmethod
    def get_npc(cls) -> Self:  # noqa
        return cls(-1)


@dataclass(frozen=True)
class Player:
    id: PlayerId
    name: str

    def to_simple_dict(self) -> dict:
        return {"id": self.id.as_int(), "name": self.name}

    @classmethod
    def from_simple_dict(cls, simple_dict: dict) -> Self:
        return cls(
            id=PlayerId(simple_dict["id"]),
            name=simple_dict["name"],
        )

from dataclasses import dataclass
from typing import Self


class PlayerId(int):
    def as_int(self) -> int:
        return int(self)


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

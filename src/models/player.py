from dataclasses import dataclass
from typing import Self


class PlayerId(int):
    def as_int(self) -> int:
        return int(self)


@dataclass
class Player:
    id: PlayerId
    name: str

    # Mutable attributes
    is_alive: bool
    lives: int
    cash: int

    def lose_life(self) -> None:
        """
        Lose a life. If the player has no lives left, mark them as dead.
        The player loses a life when they cannot supply their demand.
        """
        self.lives -= 1

    def die(self) -> None:
        """
        Mark the player as dead.
        """
        self.is_alive = False

    def to_simple_dict(self) -> dict:
        return {"id": self.id.as_int(), "name": self.name}

    @classmethod
    def from_simple_dict(cls, simple_dict: dict) -> Self:
        return cls(
            id=PlayerId(simple_dict["id"]),
            name=simple_dict["name"],
        )


class NPC(Player):
    """
    Non-Player Character (NPC) class. Inherits from Player.
    """
    pass
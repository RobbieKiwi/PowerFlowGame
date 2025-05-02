from dataclasses import dataclass
from typing import Self
import json


@dataclass(frozen=True)
class GameState:
    # A complete description of the current state of the game.
    game_id: int
    # TODO Fill in more stuff

    def to_json(self) -> str:
        return json.dumps({"game_id": self.game_id})

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        json_dict = json.loads(json_str)
        return cls(**json_dict)

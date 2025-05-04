from dataclasses import dataclass
from enum import Enum
from functools import cached_property
from typing import Self, Optional
import json

from src.models.player import Player, PlayerId
import pandas as pd


class Phase(Enum):
    # Values are just placeholders
    CONSTRUCTION = 0
    SNEAKY_TRICKS = 1
    DA_AUCTION = 2


@dataclass
class GameState:
    # A complete description of the current state of the game.
    def __init__(
        self,
        game_id: int,
        players: list[Player],
        phase: Phase,
        current_player: Optional[PlayerId],
    ) -> None:
        # Read only attributes
        self._game_id = game_id
        self._players = players

        # Mutable attributes
        self.phase = phase
        self.current_player = current_player
        self._asset_frame: pd.DataFrame = pd.DataFrame()  #  Placeholder for asset frame
        # Index: AssetId
        # Columns: AssetType, OwnerPlayerId, Bus1Id, Bus2Id, X, Y, reactance, marginal_price, operating_cost,

    @property
    def game_id(self) -> int:
        return self._game_id

    @property
    def players(self) -> list[Player]:
        return self._players

    @cached_property
    def n_players(self) -> int:
        return len(self.players)

    def to_simple_dict(self) -> dict:
        return {
            "game_id": self.game_id,
            "players": [player.to_simple_dict() for player in self.players],
            "phase": self.phase.value,
            "current_player": (
                self.current_player.as_int()
                if self.current_player is not None
                else None
            ),
        }

    @classmethod
    def from_simple_dict(cls, simple_dict: dict) -> Self:
        return cls(
            game_id=simple_dict["game_id"],
            players=[
                Player.from_simple_dict(player) for player in simple_dict["players"]
            ],
            phase=Phase(simple_dict["phase"]),
            current_player=(
                PlayerId(simple_dict["current_player"])
                if simple_dict["current_player"] is not None
                else None
            ),
        )

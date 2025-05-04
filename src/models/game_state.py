from dataclasses import dataclass
from enum import Enum
from functools import cached_property
from typing import Self, Optional
import json

from src.models.player import Player, PlayerId
from src.models.game_map import GameMap


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
        map: GameMap,
        round: int,
        phase: Phase,
        current_player: Optional[PlayerId],
        is_game_over: bool = False,
    ) -> None:
        # Read only attributes
        self._game_id = game_id
        self._players = players
        self._map = map

        # Mutable attributes
        self.round = round
        self.phase = phase
        self.current_player = current_player
        self.is_game_over = is_game_over

    def next_phase(self) -> None:
        """
        Increment the phase number.
        """
        self.phase = Phase(self.phase.value + 1)

    def next_round(self) -> None:
        """
        Increment the round number and reset to the first phase.
        """
        self.phase = Phase(0)
        self.round += 1

    def end_game(self) -> None:
        """
        End the game.
        """
        self.is_game_over = True

    @property
    def game_id(self) -> int:
        return self._game_id

    @property
    def players(self) -> list[Player]:
        return self._players

    @property
    def players_alive(self) -> list[Player]:
        return [player for player in self.players if player.is_alive]

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
            "is_game_over": self.is_game_over,
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
            is_game_over=simple_dict["is_game_over"],
        )

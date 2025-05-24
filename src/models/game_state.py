from dataclasses import dataclass
from enum import IntEnum
from typing import Self, Optional

from src.models.assets import AssetRepo
from src.models.buses import BusRepo
from src.models.ids import (
    PlayerId,
    GameId,
)
from src.models.market_coupling_result import MarketCouplingResult
from src.models.player import PlayerRepo
from src.models.transmission import TransmissionRepo
from src.models.game_settings import GameSettings
from src.tools.serialization import (
    simplify_type,
    un_simplify_type,
)


class Phase(IntEnum):
    # Values are just placeholders
    CONSTRUCTION = 0
    SNEAKY_TRICKS = 1
    DA_AUCTION = 2


@dataclass
class GameState:
    # A complete description of the current state of the game.
    game_id: GameId
    game_settings: GameSettings
    phase: Phase
    players: PlayerRepo
    buses: BusRepo
    assets: AssetRepo
    transmission: TransmissionRepo
    market_coupling_result: Optional[MarketCouplingResult]

    @property
    def current_players(self) -> list[PlayerId]:
        return self.players.get_currently_playing().player_ids

    def to_simple_dict(self) -> dict:
        return {
            "game_id": self.game_id,
            "game_settings": self.game_settings.to_simple_dict(),
            "phase": simplify_type(self.phase),
            "players": self.players.to_simple_dict(),
            "buses": self.buses.to_simple_dict(),
            "assets": self.assets.to_simple_dict(),
            "transmission": self.transmission.to_simple_dict(),
            "market_coupling_result": self.market_coupling_result.to_simple_dict(),
        }

    @classmethod
    def from_simple_dict(cls, simple_dict: dict) -> Self:
        return cls(
            game_id=simple_dict["game_id"],
            game_settings=GameSettings.from_simple_dict(simple_dict["game_settings"]),
            phase=un_simplify_type(x=simple_dict["phase"], t=Phase),
            players=PlayerRepo.from_simple_dict(simple_dict["players"]),
            buses=BusRepo.from_simple_dict(simple_dict["buses"]),
            assets=AssetRepo.from_simple_dict(simple_dict["assets"]),
            transmission=TransmissionRepo.from_simple_dict(simple_dict["transmission"]),
            market_coupling_result=MarketCouplingResult.from_simple_dict(simple_dict["market_coupling_result"]),
        )

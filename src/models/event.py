from abc import ABC
from dataclasses import dataclass

from src.models.game_state import GameState, Phase
from src.models.ids import PlayerId, AssetId


@dataclass(frozen=True)
class Event(ABC):
    pass


@dataclass(frozen=True)
class NewPhase(Event):
    phase: Phase


@dataclass(frozen=True)
class PlayerEvent(Event, ABC):
    # An event triggered by a player that is sent to the game engine
    player_id: PlayerId

    def __str__(self) -> str:
        return f"<{self.__class__.__name__}({self.player_id} -> Game Engine)>"

    def __repr__(self) -> str:
        return str(self)


@dataclass(frozen=True)
class EngineEvent(Event, ABC):
    # An event triggered by the game engine that is sent to the player
    player_id: PlayerId
    game_state: GameState

    def __str__(self) -> str:
        return f"<{self.__class__.__name__}(Game Engine -> {self.player_id})>"

    def __repr__(self) -> str:
        return str(self)


@dataclass(frozen=True)
class GameUpdate(EngineEvent):
    # The basic message that gets sent to a player to let them know the game state has
    pass


@dataclass(frozen=True)
class UpdateBidRequest(PlayerEvent):
    asset_id: AssetId
    bid_price: float


@dataclass(frozen=True)
class UpdateBidResponse(EngineEvent):
    game_state: GameState
    success: bool
    asset_id: AssetId


@dataclass(frozen=True)
class BuyAssetRequest(PlayerEvent):
    asset_id: AssetId


@dataclass(frozen=True)
class BuyAssetResponse(EngineEvent):
    game_state: GameState
    success: bool
    asset_id: AssetId


@dataclass(frozen=True)
class EndTurn(PlayerEvent):
    asset_id: AssetId

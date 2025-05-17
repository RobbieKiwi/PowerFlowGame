from abc import ABC
from dataclasses import dataclass
from typing import Self

from src.models.game_state import GameState
from src.models.ids import PlayerId, AssetId
from src.tools.serialization import (
    SerializableBase,
    SimpleDict,
    simplify_type,
    un_simplify_type,
)


@dataclass(frozen=True)
class Event(SerializableBase, ABC):
    pass


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
class GameUpdateEvent(EngineEvent):
    # The basic message that gets sent to a player to let them know the game state has changed
    def to_simple_dict(self) -> SimpleDict:
        return {
            "player_id": simplify_type(self.player_id),
            "game_state": self.game_state.to_simple_dict(),
        }

    @classmethod
    def from_simple_dict(cls, simple_dict: SimpleDict) -> Self:
        return cls(
            player_id=un_simplify_type(x=simple_dict["player_id"], t=PlayerId),
            game_state=GameState.from_simple_dict(simple_dict["game_state"]),
        )


@dataclass(frozen=True)
class UpdateBidEvent(PlayerEvent):
    asset_id: AssetId
    bid_price: float


@dataclass(frozen=True)
class BuyAssetEvent(PlayerEvent):
    asset_id: AssetId


@dataclass(frozen=True)
class EndTurnEvent(PlayerEvent):
    asset_id: AssetId

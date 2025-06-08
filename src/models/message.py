from abc import ABC
from dataclasses import dataclass
from typing import Union

from src.models.game_state import GameState, Phase
from src.models.ids import PlayerId, AssetId


@dataclass(frozen=True)
class Message(ABC):
    pass


@dataclass(frozen=True)
class InternalMessage(Message, ABC):
    # A message from the game to itself
    def __str__(self) -> str:
        return f"<{self.__class__.__name__}>"

    def __repr__(self) -> str:
        return str(self)


@dataclass(frozen=True)
class PlayerToGameMessage(Message, ABC):
    player_id: PlayerId

    def __str__(self) -> str:
        return f"<{self.__class__.__name__}({self.player_id} -> Game)>"

    def __repr__(self) -> str:
        return str(self)


@dataclass(frozen=True)
class GameToPlayerMessage(Message, ABC):
    player_id: PlayerId
    game_state: GameState

    def __str__(self) -> str:
        return f"<{self.__class__.__name__}(Engine -> {self.player_id})>"

    def __repr__(self) -> str:
        return str(self)


ToGameMessage = Union[PlayerToGameMessage, InternalMessage]
FromGameMessage = Union[InternalMessage, GameToPlayerMessage]


@dataclass(frozen=True)
class NewPhase(InternalMessage):
    phase: Phase


@dataclass(frozen=True)
class GameUpdate(GameToPlayerMessage):
    # The basic message that gets sent to a player to let them know the game state has
    pass


@dataclass(frozen=True)
class UpdateBidRequest(PlayerToGameMessage):
    asset_id: AssetId
    bid_price: float


@dataclass(frozen=True)
class UpdateBidResponse(GameToPlayerMessage):
    game_state: GameState
    success: bool
    asset_id: AssetId


@dataclass(frozen=True)
class BuyAssetRequest(PlayerToGameMessage):
    asset_id: AssetId


@dataclass(frozen=True)
class BuyAssetResponse(GameToPlayerMessage):
    game_state: GameState
    success: bool
    asset_id: AssetId


@dataclass(frozen=True)
class EndTurn(PlayerToGameMessage):
    asset_id: AssetId

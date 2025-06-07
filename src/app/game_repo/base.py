from abc import ABC, abstractmethod

from src.models.game_state import GameState
from src.models.ids import GameId


class BaseGameStateRepo(ABC):
    @abstractmethod
    def generate_game_id(self) -> GameId:
        pass

    @abstractmethod
    def add_game_state(self, game: GameState) -> None:
        pass

    @abstractmethod
    def update_game_state(self, game: GameState) -> None:
        pass

    @abstractmethod
    def get_game_state(self, game_id: GameId) -> GameState:
        pass

    @abstractmethod
    def list_game_ids(self) -> list[GameId]:
        pass

    @abstractmethod
    def delete_game_state(self, game_id: GameId, missing_ok: bool = True) -> None:
        pass

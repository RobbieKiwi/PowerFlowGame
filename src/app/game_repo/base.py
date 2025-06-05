from abc import ABC, abstractmethod

from src.models.game_state import GameState
from src.models.ids import GameId


class BaseGameRepo(ABC):
    @abstractmethod
    def generate_game_id(self) -> GameId:
        pass

    @abstractmethod
    def create_game(self, game: GameState) -> None:
        pass

    @abstractmethod
    def update_game(self, game: GameState) -> None:
        pass

    @abstractmethod
    def get_game(self, game_id: GameId) -> GameState:
        pass

    @abstractmethod
    def list_game_ids(self) -> list[GameId]:
        pass

    @abstractmethod
    def delete_game(self, game_id: GameId, missing_ok: bool = True) -> None:
        pass

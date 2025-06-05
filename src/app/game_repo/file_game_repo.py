from pathlib import Path

from src.app.game_repo.base import BaseGameRepo
from src.directories import game_cache_dir
from src.models.game_state import GameState
from src.models.ids import GameId
from src.tools.serialization import serialize, deserialize


class FileGameRepo(BaseGameRepo):
    def __init__(self, cache_dir: Path = game_cache_dir) -> None:
        self.cache_dir = cache_dir

    def generate_game_id(self) -> GameId:
        game_ids = self.list_games()
        return GameId(max(game_ids).as_int() + 1 if game_ids else 0)

    def create_game(self, game: GameState) -> None:
        path = self.game_id_to_file_path(game.game_id)
        if path.exists():  # Todo make these checks threadsafe
            raise FileExistsError(f"Game with ID {game.game_id} already exists.")
        with open(path, "w") as file:
            file.write(serialize(game))

    def update_game(self, game: GameState) -> None:
        path = self.game_id_to_file_path(game.game_id)
        if not path.exists():
            raise FileNotFoundError(f"Game with ID {game.game_id} does not exist.")
        with open(path, "w") as file:
            file.write(serialize(game))

    def get_game(self, game_id: GameId) -> GameState:
        path = self.game_id_to_file_path(game_id)
        if not path.exists():
            raise FileNotFoundError(f"Game with ID {game_id} does not exist.")
        with open(path, "r") as file:
            data = file.read()
        return deserialize(x=data, cls=GameState)

    def list_games(self) -> list[GameId]:
        game_files = self.cache_dir.glob("game_*.json")
        return [self.file_path_to_game_id(file_path) for file_path in game_files if file_path.is_file()]

    def delete_game(self, game_id: GameId, missing_ok: bool = True) -> None:
        path = self.game_id_to_file_path(game_id)
        path.unlink(missing_ok=missing_ok)

    def game_id_to_file_path(self, game_id: GameId) -> Path:
        """Get the file path for a specific game ID."""
        return self.cache_dir / f"game_{game_id}.json"

    @staticmethod
    def file_path_to_game_id(file_path: Path) -> GameId:
        """Extract the game ID from a file path."""
        if not file_path.name.startswith("game_") or not file_path.name.endswith(".json"):
            raise ValueError(f"Invalid game file name: {file_path.name}")
        game_id_str = file_path.name[len("game_"):-len(".json")]
        return GameId(int(game_id_str))

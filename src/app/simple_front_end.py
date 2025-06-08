from src.app.game_manager import GameManager
from src.app.game_repo.file_game_repo import FileGameStateRepo
from src.engine.engine import Engine


class Joystick:
    def __init__(self, game_manager: GameManager) -> None:
        game_repo = FileGameStateRepo()
        engine = Engine()

        self._game_manager = GameManager(
            game_repo=game_repo, game_engine=game_manager.game_engine, front_end=game_manager.front_end
        )

    def __str__(self) -> str:
        return f"<Joystick>"

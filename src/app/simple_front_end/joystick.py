from typing import Optional, Iterator

from src.app.game_manager import GameManager
from src.app.game_repo.file_game_repo import FileGameStateRepo
from src.app.simple_front_end.plotting.grid_plotter import GridPlotter
from src.engine.engine import Engine
from src.models.game_state import GameState
from src.models.ids import GameId, PlayerId
from src.models.message import GameToPlayerMessage, PlayerToGameMessage


class MessageHandler:
    def __init__(self) -> None:
        self._received_msgs: list[GameToPlayerMessage] = []

    @property
    def last_msg(self) -> Optional[GameToPlayerMessage]:
        if not self._received_msgs:
            return None
        return self._received_msgs[-1]

    @property
    def last_state_update(self) -> Optional[GameState]:
        last_msg = self.last_msg
        if last_msg is None:
            return None
        return last_msg.game_state

    def handle_player_messages(self, msgs: list[GameToPlayerMessage]) -> None:
        print(f"Received {len(msgs)} messages")
        for msg in msgs:
            print(msg)
            self._received_msgs.append(msg)


class Joystick:
    def __init__(self, game_id: GameId) -> None:
        self._message_handler = MessageHandler()
        self._game_manager = self._make_game_manager(handler=self._message_handler)
        self._game_id = game_id

        def _cycle_players() -> Iterator[PlayerId]:
            while True:
                for player_id in self.latest_game_state.players.player_ids:
                    yield player_id

        self._player_cycler = _cycle_players()
        self._current_player_id = PlayerId.get_npc()
        self.change_player()

    def __str__(self) -> str:
        return f"<Joystick (game_id={self._game_id}, current_player={self.current_player})>"

    def __repr__(self) -> str:
        return str(self)

    @property
    def current_player(self) -> str:
        return self.latest_game_state.players[self._current_player_id].name

    def change_player(self) -> None:
        self._current_player_id = next(self._player_cycler)
        print(f"Now it is {self.current_player}'s turn")

    def plot_network(self) -> None:
        GridPlotter().plot(self.latest_game_state)

    @property
    def latest_game_state(self) -> GameState:
        return self._game_manager.game_repo.get_game_state(game_id=self._game_id)

    def send_message(self, message: PlayerToGameMessage) -> None:
        self._game_manager.handle_player_message(game_id=self._game_id, msg=message)

    @staticmethod
    def _make_game_manager(handler: Optional[MessageHandler] = None) -> GameManager:
        """
        Create a new GameManager instance.
        :param handler: Optional MessageHandler to use
        :return: A new GameManager instance
        """
        game_repo = FileGameStateRepo()
        engine = Engine()
        if handler is None:
            handler = MessageHandler()
        return GameManager(game_repo=game_repo, game_engine=engine, front_end=handler)

    @classmethod
    def new_game(cls, player_names: list[str]) -> "Joystick":
        game_manager = cls._make_game_manager()
        game_id = game_manager.new_game(player_names=player_names)
        return cls(game_id=game_id)

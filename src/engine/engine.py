from src.models.event import Event
from src.models.game_state import GameState


class Engine:
    def __init__(self, game_state: GameState) -> None:
        self.game_state = game_state

    def handle_event(self, event: Event) -> None:
        """
        Events happen every time a player takes an action or a timer runs out.
        Every time an event occurs, the engine is informed and it can then:
        -Update the game state
        -Send messages back to the player interface if required
        :param event:
        """
        raise NotImplementedError()

from typing import Callable

from src.app.game_repo.base import BaseGameRepo
from src.engine.engine import Engine
from src.models.event import EngineEvent, Event, NewPhase, PlayerEvent
from src.models.game_state import GameState
from src.models.ids import GameId

FrontEndHandler = Callable[[EngineEvent], None]


class GameManager:
    def __init__(self, game_repo: BaseGameRepo, game_engine: Engine, front_end_handler: FrontEndHandler) -> None:
        self.game_repo = game_repo
        self.game_engine = game_engine
        self.front_end_handler = front_end_handler

    def handle_player_event(self, game_id: GameId, event: PlayerEvent) -> None:
        # TODO Make this atomic
        game_state = self.game_repo.get_game(game_id)
        updated_game_state = self.handle_event(game_state=game_state, event=event)
        self.game_repo.update_game(updated_game_state)

    def handle_event(self, game_state: GameState, event: Event) -> GameState:
        game_state, response_events = self.game_engine.handle_event(game_state=game_state, event=event)

        engine_events = [e for e in response_events if isinstance(e, EngineEvent)]
        for event in engine_events:
            self.front_end_handler(event)

        new_phase_events = [e for e in response_events if isinstance(e, NewPhase)]
        if not len(new_phase_events):
            return game_state

        assert len(new_phase_events) == 1, "There should be at most one NewPhase event per handle_event call."
        return self.handle_event(game_state=game_state, event=new_phase_events[0])

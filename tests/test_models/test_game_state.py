from unittest import TestCase

from src.models.game_state import GameState
from src.tools.serialization import serialize, deserialize
from tests.utils.comparisons import assert_game_states_are_equal
from tests.utils.game_state_maker import GameStateMaker


class TestGameState(TestCase):
    def test_make_random_game_state(self) -> None:
        GameStateMaker().make()

    def test_serialization(self) -> None:
        # Test the serialization of the GameState object
        game_state = GameStateMaker().make()
        json_str = serialize(game_state)
        re_built_state = deserialize(x=json_str, cls=GameState)

        assert_game_states_are_equal(game_state1=game_state, game_state2=re_built_state)

from unittest import TestCase

from src.models.game_state import GameState
from src.tools.serialization import serialize, deserialize
from tests.utils.game_state_maker import GameStateMaker


class TestGameState(TestCase):
    def test_make_random_game_state(self) -> None:
        GameStateMaker().make()

    def test_serialization(self) -> None:
        # Test the serialization of the GameState object
        game_state = GameStateMaker().make()
        json_str = serialize(game_state)
        re_built_state = deserialize(x=json_str, cls=GameState)

        self.assertEqual(game_state.game_id, re_built_state.game_id)
        self.assertEqual(game_state.game_settings, re_built_state.game_settings)
        self.assertEqual(game_state.phase, re_built_state.phase)
        self.assertEqual(game_state.players, re_built_state.players)
        self.assertEqual(game_state.buses, re_built_state.buses)
        self.assertEqual(game_state.transmission, re_built_state.transmission)
        if game_state.market_coupling_result is None:
            self.assertIsNone(re_built_state.market_coupling_result)
        else:
            self.assertEqual(game_state.market_coupling_result, re_built_state.market_coupling_result)

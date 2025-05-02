from unittest import TestCase

from src.models.game_state import GameState


class TestGameState(TestCase):
    def test_serialization(self) -> None:
        # Test the serialization of the GameState object
        game_state = GameState(game_id=1)
        json_str = game_state.to_json()
        re_built_state = GameState.from_json(json_str)
        self.assertEqual(game_state.game_id, re_built_state.game_id)

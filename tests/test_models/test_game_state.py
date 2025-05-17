"""
from unittest import TestCase

from src.models.game_state import GameState, Phase
from src.models.player import Player, PlayerId
from src.tools.serialization import serialize, deserialize

# TODO Finish this

class TestGameState(TestCase):
    def test_serialization(self) -> None:
        # Test the serialization of the GameState object
        game_state = GameState(
            game_id=1,
            players=[
                Player(id=PlayerId(1), color="#000000", name="Alice", money=0.0, is_having_turn=False),
                Player(id=PlayerId(2), color="#00FF00", name="Bob", money=0.0, is_having_turn=True),
            ],
            phase=Phase.CONSTRUCTION,
        )
        json_str = serialize(game_state)
        re_built_state = deserialize(x=json_str, cls=GameState)
        self.assertEqual(game_state.game_id, re_built_state.game_id)
        for (
            p1,
            p2,
        ) in zip(game_state.players, re_built_state.players):
            self.assertEqual(p1, p2)
        self.assertEqual(game_state.phase, re_built_state.phase)
"""

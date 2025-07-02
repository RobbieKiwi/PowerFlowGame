from typing import Callable
from unittest import TestCase

from src.engine.engine import Engine
from src.models.ids import PlayerId, AssetId
from src.models.message import PlayerToGameMessage, BuyAssetRequest, BuyAssetResponse
from src.models.player import Player
from tests.utils.comparisons import assert_game_states_are_equal, assert_game_states_are_not_equal
from tests.utils.game_state_maker import GameStateMaker
from tests.utils.repo_maker import PlayerRepoMaker


class DummyMessage(PlayerToGameMessage):
    pass


class TestAssets(TestCase):
    def test_bad_message(self) -> None:
        game_state = GameStateMaker().make()
        dumb_message = DummyMessage(player_id=PlayerId(5))
        with self.assertRaises(NotImplementedError):
            Engine.handle_message(game_state=game_state, msg=dumb_message)  # noqa

    def test_update_bid_message(self) -> None:
        player_repo = PlayerRepoMaker.make_quick()
        rich_player = Player(id=PlayerId(100), name="Rich player", color="#000000", money=1000000, is_having_turn=True)
        player_repo += rich_player
        game_state = GameStateMaker().add_player_repo(player_repo).make()

        is_for_sale_ids = game_state.assets.filter(condition={"is_for_sale": True}).asset_ids
        not_for_sale_ids = game_state.assets.filter(condition={"is_for_sale": False}).asset_ids

        def assert_fails_with_message_matching(request: BuyAssetRequest, x: Callable[[str], bool]) -> None:
            new_game_state, msgs = Engine.handle_message(game_state=game_state, msg=request)
            self.assertEqual(len(msgs), 1)
            message = msgs[0]
            self.assertIsInstance(message, BuyAssetResponse)
            self.assertFalse(message.success)
            self.assertTrue(x(message.message))
            assert_game_states_are_equal(game_state1=game_state, game_state2=new_game_state)

        msg = BuyAssetRequest(player_id=rich_player.id, asset_id=AssetId(-5))
        assert_fails_with_message_matching(request=msg, x=lambda s: "asset" in s.lower())

        msg = BuyAssetRequest(player_id=rich_player.id, asset_id=not_for_sale_ids[0])
        assert_fails_with_message_matching(request=msg, x=lambda s: "for sale" in s.lower())

        msg = BuyAssetRequest(player_id=rich_player.id, asset_id=is_for_sale_ids[0])
        result_game_state, messages = Engine.handle_message(game_state=game_state, msg=msg)
        self.assertEqual(len(messages), 1)
        success_msg = messages[0]
        self.assertIsInstance(success_msg, BuyAssetResponse)
        self.assertTrue(success_msg.success)
        assert_game_states_are_not_equal(game_state1=game_state, game_state2=result_game_state)

        sold_asset = result_game_state.assets[is_for_sale_ids[0]]
        self.assertEqual(sold_asset.owner_player, rich_player.id)
        self.assertFalse(sold_asset.is_for_sale)

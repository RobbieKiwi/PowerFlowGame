from unittest import TestCase

from tests.utils.repo_maker import AssetRepoMaker
from tests.utils.comparisons import assert_game_states_are_equal, assert_game_states_are_not_equal
from tests.utils.game_state_maker import GameStateMaker
from src.engine.market_coupling import MarketCouplingCalculator


class TestMarketCoupling(TestCase):
    def test_run_market_coupling(self) -> None:
        game_maker = GameStateMaker()
        many_assets = AssetRepoMaker.make_quick(n_normal_assets=15)
        game_state = game_maker.add_asset_repo(many_assets).make()
        market_result = MarketCouplingCalculator.run(game_state)
        self.assertEqual(market_result.solve_status, "optimal")  # ToDo sometimes the clearing is infeasible, maybe we have to fix the asset mix for this test
        self.assertGreaterEqual(market_result.assets_dispatch.shape[0], 1)
        self.assertGreaterEqual(market_result.bus_prices.shape[0], 1)
        self.assertGreaterEqual(market_result.transmission_flows.shape[0], 1)
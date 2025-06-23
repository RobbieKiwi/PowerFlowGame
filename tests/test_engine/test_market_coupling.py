from unittest import TestCase

from tests.utils.repo_maker import AssetRepoMaker, BusRepoMaker
from tests.utils.game_state_maker import GameStateMaker
from src.engine.market_coupling import MarketCouplingCalculator


class TestMarketCoupling(TestCase):
    def test_run_market_coupling(self) -> None:
        game_maker = GameStateMaker()

        buses = BusRepoMaker.make_quick(n_npc_buses=1)
        asset_maker = AssetRepoMaker(bus_repo=buses)

        for _ in range(6):
            asset_maker.add_asset(cat="Generator", power_std=0)
        assets = asset_maker.make()
        game_state = game_maker.add_bus_repo(buses).add_asset_repo(assets).make()
        market_result = MarketCouplingCalculator.run(game_state)

        self.assertGreaterEqual(market_result.assets_dispatch.shape[0], 1)
        self.assertGreaterEqual(market_result.bus_prices.shape[0], 1)
        self.assertGreaterEqual(market_result.transmission_flows.shape[0], 1)

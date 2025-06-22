from unittest import TestCase

from tests.utils.repo_maker import AssetRepoMaker, BusRepoMaker, TransmissionRepoMaker
from tests.utils.game_state_maker import GameStateMaker
from src.engine.market_coupling import MarketCouplingCalculator
from src.app.simple_front_end.plotting.grid_plotter import GridPlotter


class TestMarketCoupling(TestCase):
    def test_run_market_coupling(self) -> None:
        game_maker = GameStateMaker()

        buses = BusRepoMaker.make_quick(n_npc_buses=1)
        asset_maker = AssetRepoMaker(bus_repo=buses)

        for _ in range(3):
            asset_maker.add_asset(cat="Generator")
        assets = asset_maker.make()
        game_state = game_maker.add_bus_repo(buses).add_asset_repo(assets).make()

        market_result = MarketCouplingCalculator.run(game_state)
        # GridPlotter().plot(game_state=game_state) ##

        self.assertEqual(market_result.solve_status, "optimal")  # ToDo sometimes the clearing is infeasible, maybe we have to fix the asset mix for this test
        self.assertGreaterEqual(market_result.assets_dispatch.shape[0], 1)
        self.assertGreaterEqual(market_result.bus_prices.shape[0], 1)
        self.assertGreaterEqual(market_result.transmission_flows.shape[0], 1)
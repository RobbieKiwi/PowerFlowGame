from unittest import TestCase

from tests.utils.repo_maker import AssetRepoMaker, BusRepoMaker
from tests.utils.game_state_maker import GameStateMaker
from src.engine.market_coupling import MarketCouplingCalculator
from src.models.assets import AssetType


class TestMarketCoupling(TestCase):
    @staticmethod
    def create_game_state():
        game_maker = GameStateMaker()

        buses = BusRepoMaker.make_quick(n_npc_buses=1)
        asset_maker = AssetRepoMaker(bus_repo=buses)

        for _ in range(6):
            asset_maker.add_asset(cat="Generator", power_std=0)
        assets = asset_maker.make()
        game_state = game_maker.add_bus_repo(buses).add_asset_repo(assets).make()

        return game_state

    def test_run_market_coupling(self) -> None:

        game_state = self.create_game_state()
        market_result = MarketCouplingCalculator.run(game_state)

        self.assertGreaterEqual(market_result.assets_dispatch.shape[0], 1)
        self.assertGreaterEqual(market_result.bus_prices.shape[0], 1)
        self.assertGreaterEqual(market_result.transmission_flows.shape[0], 1)

    def test_no_paradoxes(self) -> None:
        game_state = self.create_game_state()
        market_result = MarketCouplingCalculator.run(game_state)

        small_number = 1e-3
        for mtu in market_result.bus_prices.index:
            for bus in game_state.buses:
                bus_price = market_result.bus_prices.loc[mtu, bus.id]
                assets_in_bus = game_state.assets.filter({"bus": bus.id})
                generators_in_the_money = assets_in_bus.filter(
                    lambda x: x["bid_price"] <= bus_price + small_number, 'and', {"asset_type": AssetType.GENERATOR}
                ).asset_ids
                loads_in_the_money = assets_in_bus.filter(
                    lambda x: x["bid_price"] >= bus_price - small_number, 'and', {"asset_type": AssetType.LOAD}
                ).asset_ids
                asset_dispatch = market_result.assets_dispatch.loc[mtu]

                dispatched_assets = set(asset_dispatch[asset_dispatch.abs() > 0].index) & set(assets_in_bus.asset_ids)

                self.assertSetEqual(set(generators_in_the_money) | set(loads_in_the_money), dispatched_assets)

    def test_energy_balance(self) -> None:
        game_state = self.create_game_state()
        market_result = MarketCouplingCalculator.run(game_state)

        for mtu in market_result.assets_dispatch.index:
            total_generation = market_result.assets_dispatch.loc[mtu][
                game_state.assets.filter({"asset_type": AssetType.GENERATOR}).asset_ids
            ].sum()
            total_load = market_result.assets_dispatch.loc[mtu][
                game_state.assets.filter({"asset_type": AssetType.LOAD}).asset_ids
            ].sum()

            self.assertAlmostEqual(total_generation, -total_load, places=5)

    def test_rent_only_for_congested_lines(self) -> None:
        game_state = self.create_game_state()
        market_result = MarketCouplingCalculator.run(game_state)

        for mtu in market_result.transmission_flows.index:
            for transmission in game_state.transmission:
                flow = market_result.transmission_flows.loc[mtu, transmission.id]
                if flow == transmission.capacity:
                    self.assertGreater(
                        abs(
                            market_result.bus_prices.loc[mtu, transmission.bus1]
                            - market_result.bus_prices.loc[mtu, transmission.bus2]
                        ),
                        0,
                    )
                else:
                    self.assertAlmostEqual(
                        market_result.bus_prices.loc[mtu, transmission.bus1],
                        market_result.bus_prices.loc[mtu, transmission.bus2],
                    )

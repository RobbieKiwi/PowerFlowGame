from dataclasses import replace

from src.models.assets import AssetId, AssetType
from src.models.transmission import TransmissionId
from src.models.buses import BusId
from src.models.game_state import GameState
from src.models.market_coupling_result import MarketCouplingResult

import numpy as np
import pypsa


class MarketCouplingCalculator:
    @classmethod
    def run(cls, game_state: GameState) -> MarketCouplingResult:
        """
        Run the market coupling algorithm.
        :param game_state: A copy of the game state
        :return: The market coupling result
        """
        network = cls.create_pypsa_network(game_state)
        return MarketCouplingResult(
            solve_status=network.optimize()[1],
            bus_prices=network.buses_t.marginal_price,
            transmission_flows=network.lines_t.p0,
            assets_dispatch=network.generators_t.p
        )

    @classmethod
    def create_pypsa_network(cls, game_state: GameState) -> pypsa.Network:
        """
        Create a PyPSA network from the game state.
        :param game_state: The current state of the game
        :return: A PyPSA network object
        """
        network = pypsa.Network()
        for bus in game_state.buses:
            network.add(
                class_name="Bus",
                name=cls.get_pypsa_name(bus.id),
                carrier="AC"
            )
        for line in game_state.transmission:
            network.add(
                class_name="Line",
                name=cls.get_pypsa_name(line.id),
                bus0=cls.get_pypsa_name(line.bus1),
                bus1=cls.get_pypsa_name(line.bus2),
                x=line.reactance,
                s_nom=line.capacity
            )
        for generator in game_state.assets.filter({"asset_type": AssetType.GENERATOR}):
            network.add(
                class_name="Generator",
                name=cls.get_pypsa_name(generator.id),
                bus=cls.get_pypsa_name(generator.bus),
                marginal_cost=generator.marginal_price,
                p_nom=np.random.normal(loc=generator.power_expected, scale=generator.power_std),
            )
        for load in game_state.assets.filter({"asset_type": AssetType.LOAD}):
            # Loads are treated as generators with negative power in PyPSA
            network.add(
                class_name="Generator",
                name=cls.get_pypsa_name(load.id),
                bus=cls.get_pypsa_name(load.bus),
                p_max_pu=0,
                p_min_pu=-1.0,
                p_nom=np.random.normal(loc=load.power_expected, scale=load.power_std),
                marginal_cost=load.marginal_price,
            )
        return network

    @classmethod
    def adjust_players_money(cls,
        game_state: GameState,
        market_coupling_result: MarketCouplingResult,
    ) -> GameState:
        """
        Adjust the players' money based on the market coupling result.
        :param game_state: The current state of the game
        :param market_coupling_result: The result of the market coupling
        :return: The updated game state with adjusted player balances
        """
        new_game_state = replace(game_state)
        for player in game_state.players:
            operating_cost = 0.0
            market_cashflow = 0.0
            for asset in game_state.assets.get_all_for_player(player.id):
                if asset.is_active:
                    dispatched_volume = market_coupling_result.assets_dispatch[cls.get_pypsa_name(asset.id)]
                    operating_cost += abs(dispatched_volume) * asset.operating_cost
                    market_cashflow += dispatched_volume * asset.marginal_price
            new_game_state = replace(new_game_state, players=game_state.players.add_money(player.id, market_cashflow - operating_cost))
        return new_game_state

    @staticmethod
    def get_pypsa_name(id_in_game: BusId | TransmissionId | AssetId) -> str:
        """
        Convert a bus, transmission, or asset ID to a PyPSA-compatible name.
        :param id_in_game: The ID of the bus, transmission, or asset
        :return: A string representation of the ID for PyPSA
        """
        if isinstance(id_in_game, BusId):
            return f"bus_{id_in_game}"
        elif isinstance(id_in_game, TransmissionId):
            return f"line_{id_in_game}"
        elif isinstance(id_in_game, AssetId):
            return f"asset_{id_in_game}"
        raise ValueError(f"Unsupported ID type: {type(id_in_game)}")

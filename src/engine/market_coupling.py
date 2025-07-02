from dataclasses import replace

from src.models.assets import AssetId, AssetType
from src.models.transmission import TransmissionId
from src.models.buses import BusId
from src.models.game_state import GameState
from src.models.market_coupling_result import MarketCouplingResult

import pandas as pd
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
        network.optimize()
        return MarketCouplingResult(
            bus_prices=cls.get_bus_prices(network),
            transmission_flows=cls.get_transmission_flows(network),
            assets_dispatch=cls.get_assets_dispatch(network),
        )

    @classmethod
    def create_pypsa_network(cls, game_state: GameState) -> pypsa.Network:
        """
        Create a PyPSA network from the game state.
        :param game_state: The current state of the game
        :return: A PyPSA network object
        """
        network = pypsa.Network()
        network.add(class_name="Carrier", name="AC")
        for bus in game_state.buses:
            network.add(class_name="Bus", name=cls.get_pypsa_name(bus.id), carrier="AC")
        for line in game_state.transmission:
            network.add(
                class_name="Line",
                name=cls.get_pypsa_name(line.id),
                bus0=cls.get_pypsa_name(line.bus1),
                bus1=cls.get_pypsa_name(line.bus2),
                x=line.reactance,
                # r=0.01 * line.reactance,  # Assuming a small resistance for numerical stability
                s_nom=line.capacity,
                carrier="AC",
            )
        for generator in game_state.assets.filter({"asset_type": AssetType.GENERATOR}):
            network.add(
                class_name="Generator",
                name=cls.get_pypsa_name(generator.id),
                bus=cls.get_pypsa_name(generator.bus),
                marginal_cost=generator.bid_price,
                p_nom=np.random.normal(loc=generator.power_expected, scale=generator.power_std),
                carrier="AC",
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
                marginal_cost=load.bid_price,
                carrier="AC",
            )
        return network

    @classmethod
    def get_bus_prices(cls, network: pypsa.Network) -> pd.DataFrame:
        bus_prices = network.buses_t.marginal_price
        bus_prices.columns = [cls.get_game_id(pypsa_name) for pypsa_name in bus_prices.columns]
        return bus_prices

    @classmethod
    def get_transmission_flows(cls, network: pypsa.Network) -> pd.DataFrame:
        transmission_flows = network.lines_t.p0
        transmission_flows.columns = [cls.get_game_id(pypsa_name) for pypsa_name in transmission_flows.columns]
        return transmission_flows

    @classmethod
    def get_assets_dispatch(cls, network: pypsa.Network) -> pd.DataFrame:
        assets_dispatch = network.generators_t.p
        assets_dispatch.columns = [cls.get_game_id(pypsa_name) for pypsa_name in assets_dispatch.columns]
        return assets_dispatch

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

    @staticmethod
    def get_game_id(pypsa_name: str) -> BusId | TransmissionId | AssetId:
        def get_id_substring(name: str) -> str:
            return name.split("_")[-1]

        if pypsa_name.startswith("bus_"):
            return BusId(get_id_substring(pypsa_name))
        elif pypsa_name.startswith("line_"):
            return TransmissionId(get_id_substring(pypsa_name))
        elif pypsa_name.startswith("asset_"):
            return AssetId(get_id_substring(pypsa_name))
        else:
            raise ValueError(f"Unknown PyPSA name format: {pypsa_name}")

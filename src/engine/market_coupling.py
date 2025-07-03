import logging
import warnings
from typing import Optional

import numpy as np
import pandas as pd
import pypsa

from src.models.assets import AssetId, AssetType
from src.models.buses import BusId
from src.models.game_state import GameState
from src.models.market_coupling_result import MarketCouplingResult
from src.models.transmission import TransmissionId


class MarketCouplingCalculator:
    @classmethod
    def run(cls, game_state: GameState) -> MarketCouplingResult:
        network = cls.create_pypsa_network(game_state)
        cls.optimize_network(network=network)

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
        network.set_snapshots(pd.Index([0], name="time"))  # Single snapshot for simplicity

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
    def optimize_network(cls, network: pypsa.Network) -> None:
        # TODO All solver logs have been silenced apart from the Highs Banner. Maybe there is an option here?
        #  https://github.com/ERGO-Code/HiGHS/blob/364c83a51e44ba6c27def9c8fc1a49b1daf5ad5c/highs/highspy/_core/__init__.pyi#L401
        with warnings.catch_warnings(action="ignore"):
            logging.getLogger("linopy").setLevel(logging.ERROR)
            logging.getLogger("pypsa").setLevel(logging.ERROR)
            network.optimize(solver_name="highs", solver_options={"log_to_console": False, "output_flag": False})
        return

    @classmethod
    def get_bus_prices(cls, network: pypsa.Network) -> pd.DataFrame:
        return cls._tidy_df(df=network.buses_t.marginal_price, column_name="Bus")

    @classmethod
    def get_transmission_flows(cls, network: pypsa.Network) -> pd.DataFrame:
        return cls._tidy_df(df=network.lines_t.p0, column_name="Line")

    @classmethod
    def get_assets_dispatch(cls, network: pypsa.Network) -> pd.DataFrame:
        # Note that all values are positive. For generators this means production, for loads it means consumption.
        return cls._tidy_df(df=network.generators_t.p, column_name="Asset").abs()

    @classmethod
    def _tidy_df(cls, df: pd.DataFrame, column_name: Optional[str] = None) -> pd.DataFrame:
        df = df.copy()
        df.rename(columns=cls.get_game_id, inplace=True)
        df.index = df.index.rename("time")
        if column_name is not None:
            df.columns = df.columns.rename(column_name)
        return df

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

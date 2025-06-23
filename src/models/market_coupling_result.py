from dataclasses import dataclass
from typing import Self
import pandas as pd

from src.models.buses import BusId
from src.models.transmission import TransmissionId
from src.models.assets import AssetId

from src.tools.serialization import SimpleDict


@dataclass
class MarketCouplingResult:

    def __init__(self, bus_prices: pd.DataFrame, transmission_flows: pd.DataFrame, assets_dispatch: pd.DataFrame, is_from_pypsa: bool=True) -> None:
        self._bus_prices = bus_prices
        self._transmission_flows = transmission_flows
        self._assets_dispatch = assets_dispatch

        market_time_units = self._bus_prices.index
        assert self._transmission_flows.index.equals(market_time_units), "Transmission flows index does not match bus prices index"
        assert self._assets_dispatch.index.equals(market_time_units), "Assets dispatch index does not match bus prices index"

        if is_from_pypsa:
            try:
                self._bus_prices.columns = [self.get_game_id(x) for x in self._bus_prices.columns]
                self._transmission_flows.columns = [self.get_game_id(x) for x in self._transmission_flows.columns]
                self._assets_dispatch.columns = [self.get_game_id(x) for x in self._assets_dispatch.columns]
            except ValueError as e:
                raise ValueError("Failed to convert PyPSA names to game IDs. Ensure that PyPSA variables are named correctly.") from e

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

    @property
    def bus_prices(self) -> pd.DataFrame:
        """
        Get the bus prices from the market coupling result.
        The DataFrame has a multi-index with time units and columns representing bus IDs.
        The values are the marginal prices at each bus for each time unit.
        | time_unit | bus_id_1 | bus_id_2 | ... |
        |-----------|----------|----------|-----|
        :return: DataFrame with bus prices after market coupling.
        """
        return self._bus_prices

    @property
    def transmission_flows(self) -> pd.DataFrame:
        """
        Get the transmission flows from the market coupling result.
        The DataFrame has a multi-index with time units and columns representing transmission line IDs.
        The values are the power flows on each transmission line for each time unit.
        | time_unit | transmission_id_1 | transmission_id_2 | ... |
        |-----------|-------------------|-------------------|-----|
        :return: DataFrame with transmission flows after market coupling.
        """
        return self._transmission_flows

    @property
    def assets_dispatch(self) -> pd.DataFrame:
        """
        Get the assets dispatch from the market coupling result.
        The DataFrame has a multi-index with time units and columns representing asset IDs.
        The values are the dispatched power for each asset for each time unit.
        | time_unit | asset_id_1 | asset_id_2 | ... |
        |-----------|------------|------------|-----|
        :return: DataFrame with assets dispatch after market coupling.
        """
        return self._assets_dispatch

    def to_simple_dict(self) -> SimpleDict:
        return {
            "bus_prices": self._bus_prices.to_dict(),
            "transmission_flows": self._transmission_flows.to_dict(),
            "assets_dispatch": self._assets_dispatch.to_dict(),
        }

    @classmethod
    def from_simple_dict(cls, simple_dict: SimpleDict) -> Self:
        return cls(
            bus_prices=pd.DataFrame.from_dict(simple_dict["bus_prices"]),
            transmission_flows=pd.DataFrame.from_dict(simple_dict["transmission_flows"]),
            assets_dispatch=pd.DataFrame.from_dict(simple_dict["assets_dispatch"]),
            is_from_pypsa=False
        )

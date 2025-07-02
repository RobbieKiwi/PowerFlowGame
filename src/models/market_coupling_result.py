from typing import Self
import pandas as pd

from src.tools.serialization import SimpleDict
from src.models.ids import BusId, TransmissionId, AssetId


class MarketCouplingResult:

    def __init__(
        self, bus_prices: pd.DataFrame, transmission_flows: pd.DataFrame, assets_dispatch: pd.DataFrame
    ) -> None:
        self._bus_prices = self.clean_pypsa_metadata(bus_prices)
        self._transmission_flows = self.clean_pypsa_metadata(transmission_flows)
        self._assets_dispatch = self.clean_pypsa_metadata(assets_dispatch)

        market_time_units = self._bus_prices.index
        assert self._transmission_flows.index.equals(
            market_time_units
        ), "Transmission flows index does not match bus prices index"
        assert self._assets_dispatch.index.equals(
            market_time_units
        ), "Assets dispatch index does not match bus prices index"

    @property
    def bus_prices(self) -> pd.DataFrame:
        """
        Get the bus prices from the market coupling result.
        The DataFrame index with represent market time units and columns representing bus IDs.
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
        The DataFrame index with represent market time units and columns representing transmission line IDs.
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
        The DataFrame index with represent market time units and columns representing asset IDs.
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
            bus_prices=pd.DataFrame.from_dict({BusId(k): v for k, v in simple_dict["bus_prices"].items()}),
            transmission_flows=pd.DataFrame.from_dict(
                {TransmissionId(k): v for k, v in simple_dict["transmission_flows"].items()}
            ),
            assets_dispatch=pd.DataFrame.from_dict({AssetId(k): v for k, v in simple_dict["assets_dispatch"].items()}),
        )

    @staticmethod
    def clean_pypsa_metadata(df: pd.DataFrame) -> pd.DataFrame:
        return pd.DataFrame.from_dict(df.to_dict())

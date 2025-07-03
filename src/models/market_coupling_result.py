from typing import Self

import pandas as pd

from src.tools.serialization import SimpleDict


class MarketCouplingResult:
    def __init__(
        self, bus_prices: pd.DataFrame, transmission_flows: pd.DataFrame, assets_dispatch: pd.DataFrame
    ) -> None:
        self._bus_prices = bus_prices
        self._transmission_flows = transmission_flows
        self._assets_dispatch = assets_dispatch

        self._validate()

    def _validate(self) -> None:
        assert (
            self.market_time_units.name == "time"
        ), f"Expected time index to have name 'time', but got '{self.market_time_units.name}'"

        dfs_and_expectations = [
            (self.bus_prices, "Bus"),
            (self.transmission_flows, "Line"),
            (self.assets_dispatch, "Asset"),
        ]
        for df, expected_name in dfs_and_expectations:
            assert isinstance(df, pd.DataFrame), f"Expected a DataFrame, but got {type(df)}"
            assert df.index.equals(self.market_time_units)
            assert (
                df.columns.name == expected_name
            ), f"Expected DataFrame columns to be named '{expected_name}', but got '{df.columns.name}'"

        market_time_units = self._bus_prices.index
        assert self._transmission_flows.index.equals(
            market_time_units
        ), "Transmission flows index does not match bus prices index"
        assert self._assets_dispatch.index.equals(
            market_time_units
        ), "Assets dispatch index does not match bus prices index"

    def __str__(self) -> str:
        return f"<{self.__class__.__name__}>"

    def __repr__(self) -> str:
        return self.__str__()

    @property
    def market_time_units(self) -> pd.Index:
        """
        :return: Market time units (index of the DataFrames)
        """
        return self._bus_prices.index

    @property
    def bus_prices(self) -> pd.DataFrame:
        """
        :return: DataFrame with
        * Index: Market time units
        * Columns: Bus IDs (as ints)
        * Values: Marginal prices
        """
        return self._bus_prices.copy()

    @property
    def transmission_flows(self) -> pd.DataFrame:
        """
        :return: DataFrame with
        * Index: Market time units
        * Columns: Transmission IDs (as ints)
        * Values: Flows
        """
        return self._transmission_flows.copy()

    @property
    def assets_dispatch(self) -> pd.DataFrame:
        """
        :return: DataFrame with
        * Index: Market time units
        * Columns: Asset IDs (as ints)
        * Values: Produced power for generators or consumed power for loads, always positive.
        """
        return self._assets_dispatch.copy()

    def to_simple_dict(self) -> SimpleDict:
        return {
            "bus_prices": self._bus_prices.to_dict(),
            "transmission_flows": self._transmission_flows.to_dict(),
            "assets_dispatch": self._assets_dispatch.to_dict(),
        }

    @classmethod
    def from_simple_dict(cls, simple_dict: SimpleDict) -> Self:
        def get_one(key: str, column_index_name: str) -> pd.DataFrame:
            df = pd.DataFrame.from_dict(simple_dict[key])
            df.index.name = "time"
            df.index = df.index.map(int)
            df.columns.name = column_index_name
            df.columns = df.columns.map(int)
            return df

        return cls(
            bus_prices=get_one(key="bus_prices", column_index_name="Bus"),
            transmission_flows=get_one(key="transmission_flows", column_index_name="Line"),
            assets_dispatch=get_one(key="assets_dispatch", column_index_name="Asset"),
        )

from dataclasses import dataclass
from typing import Self

import pandas as pd
from src.tools.serialization import SimpleDict


@dataclass(frozen=True)
class MarketCouplingResult:
    # A complete description of the transmission flows, activated powers of assets and prices in the market coupling
    # TODO Add fields. these fields should be improved
    solve_status: str
    bus_prices: pd.DataFrame
    transmission_flows: pd.DataFrame
    assets_dispatch: pd.DataFrame

    def to_simple_dict(self) -> SimpleDict:
        raise NotImplementedError()

    @classmethod
    def from_simple_dict(cls, simple_dict: SimpleDict) -> Self:
        raise NotImplementedError()

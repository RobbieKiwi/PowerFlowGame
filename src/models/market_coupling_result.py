from dataclasses import dataclass
from typing import Self

from src.tools.serialization import SimpleDict, simplify_type


@dataclass(frozen=True)
class MarketCouplingResult:
    # A complete description of the transmission flows, activated powers of assets and prices in the market coupling
    # TODO Add fields

    def to_simple_dict(self) -> SimpleDict:
        raise NotImplementedError()

    @classmethod
    def from_simple_dict(cls, simple_dict: SimpleDict) -> Self:
        raise NotImplementedError()

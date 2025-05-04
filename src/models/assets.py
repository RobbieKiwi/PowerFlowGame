from dataclasses import dataclass
from enum import IntEnum
from typing import Self

from src.models.data.ldc_frame import LdcFrame
from src.models.data.light_dc import LightDc
from src.models.player import PlayerId


class AssetType(IntEnum):
    BUS = 0
    GENERATOR = 1
    LOAD = 2
    TRANSMISSION = 3


@dataclass(frozen=True)
class AssetInfo(LightDc):
    asset_type: AssetType
    owner_player: PlayerId
    bus1: int
    bus2: int
    x: float
    y: float
    reactance: float
    marginal_price: float
    operating_cost: float
    health: int
    profit: float

    def __post_init__(self) -> None:
        assert self.health >= 0, f"health must be non-negative"
        if self.asset_type == AssetType.TRANSMISSION:
            assert (
                self.bus1 != self.bus2
            ), f"bus1 and bus2 must be different for transmission assets"
            assert self.bus1 < self.bus2, f"bus1 must be less than bus2. Got {self.bus1} and {self.bus2}"
            assert self.marginal_price == 0.0
        else:
            assert self.reactance == 0.0
            assert (
                self.bus1 == self.bus2
            ), f"bus1 and bus2 must be equal for {self.asset_type.name} type"


class AssetFrame(LdcFrame[AssetInfo]):
    @classmethod
    def _get_dc_type(cls) -> type[AssetInfo]:
        return AssetInfo

    # READ
    def get_all_assets_for_player(self, player_id: PlayerId) -> Self:
        return self.filter({"owner_player": player_id})

    def get_all_assets_at_bus(self, bus_id: int) -> Self:
        return self.filter(condition=lambda x: bus_id in [x["bus2"], x["bus1"]])

    def get_all_transmission_lines_on_bus(self, bus_id: int) -> Self:
        return self.get_all_assets_at_bus(bus_id=bus_id).filter({"asset_type": AssetType.TRANSMISSION})

    def get_all_transmission_lines_between_buses(self, buses: tuple[int, int]) -> Self:
        bus1 = min(buses)
        bus2 = max(buses)
        assert bus1 != bus2, f"bus1 and bus2 must be different. Got {bus1} and {bus2}"
        return self.filter({"bus1": bus1, "bus2": bus2, "asset_type": AssetType.TRANSMISSION})

    def get_total_profit_for_player(self, player: PlayerId) -> float:
        return float(self.filter({"owner_player": player})["profit"].sum())

    # UPDATE
    def add_asset(self, asset: AssetInfo) -> Self:
        return self + asset

    # DELETE
    def delete_assets_for_player(self, player_id: PlayerId) -> Self:
        return self.drop_items(condition={"owner_player": player_id})


def _test():
    asset_infos = [
        AssetInfo(
            id=1,
            asset_type=AssetType.BUS,
            owner_player=PlayerId(1),
            bus1=1,
            bus2=1,
            x=0.0,
            y=0.0,
            reactance=0.0,
            marginal_price=0.0,
            operating_cost=5.0,
            health=10,
            profit=1.0
        ),
        AssetInfo(
            id=2,
            asset_type=AssetType.BUS,
            owner_player=PlayerId(2),
            bus1=2,
            bus2=2,
            x=1.0,
            y=1.0,
            reactance=0.0,
            marginal_price=0.0,
            operating_cost=10.0,
            health=10,
            profit=2.0
        ),
        AssetInfo(
            id=3,
            asset_type=AssetType.BUS,
            owner_player=PlayerId(2),
            bus1=2,
            bus2=2,
            x=1.0,
            y=1.0,
            reactance=0.0,
            marginal_price=0.0,
            operating_cost=10.0,
            health=10,
            profit=2.0
        ),
        AssetInfo(
            id=4,
            asset_type=AssetType.TRANSMISSION,
            owner_player=PlayerId.get_npc(),
            bus1=1,
            bus2=2,
            x=1.0,
            y=1.0,
            reactance=0.0,
            marginal_price=0.0,
            operating_cost=10.0,
            health=10,
            profit=2.0
        ),
    ]

    asset_frame = AssetFrame(asset_infos)
    asset_frame.get_all_assets_for_player(PlayerId(1))
    asset_frame.get_all_assets_at_bus(1)
    asset_frame.get_total_profit_for_player(PlayerId(1))
    asset_frame.get_total_profit_for_player(PlayerId(2))
    asset_frame.delete_assets_for_player(PlayerId(2))
    asset_frame.get_all_transmission_lines_between_buses((1, 2))


if __name__ == "__main__":
    _test()

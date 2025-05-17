from dataclasses import dataclass

from src.models.assets import AssetType
from src.models.data.ldc_repo import LdcRepo
from src.models.data.light_dc import LightDc
from src.models.ids import PlayerId, BusId


@dataclass(frozen=True)
class Bus(LightDc):
    id: BusId
    x: float
    y: float
    asset_type: AssetType
    player_id: PlayerId = PlayerId.get_npc()

    @property
    def is_ice_cream_bus(self) -> bool:
        return self.player_id != PlayerId.get_npc()

    def __post_init__(self) -> None:
        if self.is_ice_cream_bus:
            assert self.asset_type == AssetType.LOAD, "Ice cream bus must be of type LOAD"


class BusRepo(LdcRepo[Bus]):
    @classmethod
    def _get_dc_type(cls) -> type[Bus]:
        return Bus

    # GET
    @property
    def bus_ids(self) -> list[BusId]:
        return [BusId(x) for x in self.df.index.tolist()]

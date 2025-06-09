from dataclasses import dataclass
from typing import Self

from src.models.data.ldc_repo import LdcRepo
from src.models.data.light_dc import LightDc
from src.models.ids import TransmissionId, BusId, PlayerId


@dataclass(frozen=True)
class TransmissionInfo(LightDc):
    id: TransmissionId
    owner_player: PlayerId
    bus1: BusId
    bus2: BusId
    reactance: float = 0.0
    health: int = 5
    operating_cost: float = 0.0
    is_for_sale: bool = False
    purchase_cost: float = 0.0  # 0 = Not for sale

    def __post_init__(self) -> None:
        assert self.bus2 > self.bus1, f"bus2 must be greater than bus1. Got {self.bus2} and {self.bus1}"
        assert self.reactance > 0, f"Reactance must be positive. Got {self.reactance}"


class TransmissionRepo(LdcRepo[TransmissionInfo]):
    @classmethod
    def _get_dc_type(cls) -> type[TransmissionInfo]:
        return TransmissionInfo

    # GET
    @property
    def transmission_ids(self) -> list[TransmissionId]:
        return [TransmissionId(x) for x in self.df.index.tolist()]

    def get_all_for_player(self, player_id: PlayerId) -> Self:
        return self.filter({"owner_player": player_id})

    def get_all_at_bus(self, bus: BusId) -> Self:
        return self.filter({"bus1": bus}, "or", {"bus2": bus})

    def get_all_between_buses(self, bus1: BusId, bus2: BusId) -> Self:
        assert bus1 != bus2, f"bus1 and bus2 must be different. Got {bus1} and {bus2}"
        min_bus = min(bus1, bus2)
        max_bus = max(bus1, bus2)
        return self.filter({"bus1": min_bus, "bus2": max_bus})

    # DELETE
    def delete_for_player(self, player_id: PlayerId) -> Self:
        return self.drop_items({"owner_player": player_id})

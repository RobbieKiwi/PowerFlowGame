from dataclasses import dataclass

from src.models.data.ldc_repo import LdcRepo
from src.models.data.light_dc import LightDc
from src.models.ids import PlayerId, BusId


@dataclass(frozen=True)
class Bus(LightDc):
    id: BusId
    x: float
    y: float
    player_id: PlayerId = PlayerId.get_npc()

    @property
    def is_ice_cream_bus(self) -> bool:
        return self.player_id != PlayerId.get_npc()


class BusRepo(LdcRepo[Bus]):
    @classmethod
    def _get_dc_type(cls) -> type[Bus]:
        return Bus

    # GET
    @property
    def bus_ids(self) -> list[BusId]:
        return [BusId(x) for x in self.df.index.tolist()]

    @property
    def npc_bus_ids(self) -> list[BusId]:
        return self.filter({"player_id": PlayerId.get_npc()}).bus_ids

    @property
    def player_bus_ids(self) -> list[BusId]:
        return self.filter(operator="not", condition={"player_id": PlayerId.get_npc()}).bus_ids

    def get_bus_for_player(self, player_id: PlayerId) -> Bus:
        """Get the bus for a specific player."""
        player_buses = self.filter({"player_id": player_id})
        assert len(player_buses) == 1
        return player_buses[0]

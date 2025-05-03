from dataclasses import dataclass
from src.models.grid_assets.branch import ListBranches


class BusId(int):
    def as_int(self) -> int:
        return int(self)


@dataclass
class Bus:
    id: BusId
    is_connected: bool
    clearing_price: float

    def set_price(self, price: float):
        """
        Set the clearing price for the bus only if the bus is connected.
        Their clearing prices will be zero to not affect the players'
         revenues and costs.
        :param price: Clearing price
        """
        if self.is_connected:
            self.clearing_price = price
        else:
            self.clearing_price = 0

    def set_is_connected(self, is_connected: bool):
        """
        Set the connection status of the bus.
        :param is_connected: Connection status
        """
        self.is_connected = is_connected


class ListBuses(list):
    """
    List of Bus objects. Allows for easy management of multiple buses.
    """
    def __init__(self):
        super().__init__()

    def add_bus(self, bus: Bus):
        self.append(bus)

    def set_disconnected_buses(self, list_branches: ListBranches) -> None:
        """
        Detect disconnected buses in the grid.
        :param list_branches: List of branches in the grid
        """
        connected_buses = set()

        for branch in list_branches:
            connected_buses.add(branch.bus_from)
            connected_buses.add(branch.bus_to)

        for bus in self:
            if bus not in connected_buses:
                bus.set_is_connected(False)

from dataclasses import dataclass
from src.models.player import Player, NPC
from src.models.grid_assets.bus import Bus


class BranchId(int):
    def as_int(self) -> int:
        return int(self)


@dataclass
class Branch:
    id: BranchId
    owner: Player | NPC
    bus_from: Bus
    bus_to: Bus
    max_power_direct: float
    max_power_reverse: float
    power_flow: float
    lifespan: int

    def get_price_spread(self) -> float:
        """
        Calculate the price spread between the two buses connected by this branch.
        :return: Price spread between connected buses
        """
        return self.bus_from.clearing_price - self.bus_to.clearing_price

    def get_congestion_rent(self):
        """
        Calculate the congestion rent for the branch.
        :return: Congestion rent value
        """
        return self.power_flow * self.get_price_spread()

    def set_power_flow(self, power_flow: float):
        """
        Set the power flow through the branch.
        :param power_flow: Power flow value
        """
        self.power_flow = power_flow


class ListBranches(list):
    """
    List of Branch objects. Allows for easy management of multiple branches.
    """
    def __init__(self):
        super().__init__()

    def add_branch(self, branch: Branch):
        self.append(branch)

    def filter_by_owner(self, owner: Player | NPC) -> list[Branch]:
        """
        Filter branches by owner.
        :param owner: Owner of the branches
        :return: List of branches owned by the specified owner
        """
        return [branch for branch in self if branch.owner == owner]

    @property
    def power_flow(self) -> list[float]:
        """
        Get the power flow of all branches.
        :return: List of power flows for each branch
        """
        return [branch.power_flow for branch in self]

    def get_congestion_rent(self) -> list[float]:
        """
        Get the congestion rent of all branches.
        :return: List of congestion rents for each branch
        """
        return [branch.get_congestion_rent() for branch in self]
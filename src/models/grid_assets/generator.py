from dataclasses import dataclass
from src.models.player import Player, NPC
from src.models.grid_assets.bus import Bus


@dataclass
class Generator:
    owner: Player | NPC
    bus: Bus
    max_power: float
    marginal_cost: float
    fixed_cost: float
    power_flow: float

    def get_revenue(self) -> float:
        """
        Calculate the revenue for the generator.
        :return: Revenue value
        """
        return self.power_flow * self.bus.clearing_price

    def get_cost(self) -> float:
        """
        Calculate the cost for the generator.
        :return: Cost value
        """
        return self.fixed_cost + (self.power_flow * self.marginal_cost)

    def get_surplus(self) -> float:
        """
        Calculate the surplus for the generator.
        :return: Surplus value
        """
        return self.get_revenue() - self.get_cost()


class ListGenerators(list):
    """
    List of Generator objects. Allows for easy management of multiple generators.
    """
    def __init__(self):
        super().__init__()

    def add_generator(self, generator: Generator):
        self.append(generator)

    def filter_by_owner(self, owner: Player | NPC) -> list[Generator]:
        """
        Filter generators by owner.
        :param owner: Owner of the generators
        :return: List of generators owned by the specified owner
        """
        return [gen for gen in self if gen.owner == owner]

    def get_surplus(self) -> list[float]:
        """
        Calculate the total surplus for each generator.
        :return: Surplus values for each generator
        """
        return [gen.get_surplus() for gen in self]

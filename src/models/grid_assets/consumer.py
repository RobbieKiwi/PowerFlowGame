from dataclasses import dataclass
from src.models.player import Player, NPC
from src.models.grid_assets.bus import Bus


@dataclass
class Consumer:
    owner: Player | NPC
    bus: Bus
    max_power: float
    revenue_per_power_consumed: float
    fixed_cost: float
    power_flow: float

    def get_revenue(self) -> float:
        """
        Calculate the revenue for the consumer.
        :return: Revenue value
        """
        return self.power_flow * self.revenue_per_power_consumed

    def get_cost(self) -> float:
        """
        Calculate the cost for the consumer.
        :return: Cost value
        """
        return self.fixed_cost + (self.power_flow * self.bus.clearing_price)

    def get_surplus(self) -> float:
        """
        Calculate the surplus for the consumer.
        :return: Surplus value
        """
        return self.get_revenue() - self.get_cost()

    def set_power_flow(self, power_flow: float):
        """
        Set the power flow for the consumer.
        :param power_flow: Power flow value
        """
        self.power_flow = power_flow


class ListConsumers(list):
    """
    List of Consumer objects. Allows for easy management of multiple consumers.
    """
    def __init__(self):
        super().__init__()

    def add_consumer(self, consumer: Consumer):
        self.append(consumer)

    def filter_by_owner(self, owner: Player | NPC) -> list[Consumer]:
        """
        Filter consumers by owner.
        :param owner: Owner of the consumers
        :return: List of consumers owned by the specified owner
        """
        return [cons for cons in self if cons.owner == owner]

    def get_surplus(self) -> list[float]:
        """
        Calculate the surplus for each consumer.
        :return: surplus value for each consumer
        """
        return [cons.get_surplus() for cons in self]

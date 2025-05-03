from dataclasses import dataclass
from src.models.grid_assets.bus import Bus, ListBuses
from src.models.grid_assets.branch import Branch, ListBranches
from src.models.grid_assets.consumer import Consumer, ListConsumers
from src.models.grid_assets.generator import Generator, ListGenerators


@dataclass
class GameMap:
    buses: ListBuses
    branches: ListBranches
    consumers: ListConsumers
    generators: ListGenerators

    def add_bus(self, bus: Bus):
        self.buses.add_bus(bus)

    def add_branch(self, branch: Branch):
        self.branches.add_branch(branch)

    def add_consumer(self, consumer: Consumer):
        self.consumers.add_consumer(consumer)

    def add_generator(self, generator: Generator):
        self.generators.add_generator(generator)
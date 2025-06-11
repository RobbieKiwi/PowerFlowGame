from itertools import combinations
from typing import List, Dict, Optional
from abc import ABC, abstractmethod
import math
import numpy as np

from matplotlib import cm

from src.models.assets import AssetRepo, AssetInfo, AssetId, AssetType
from src.models.buses import BusRepo, Bus
from src.models.game_settings import GameSettings
from src.models.game_state import GameState, Phase
from src.models.ids import GameId, PlayerId, BusId
from src.models.player import Player, PlayerRepo
from src.models.transmission import TransmissionRepo, TransmissionInfo, TransmissionId


class BusTopology:

    @staticmethod
    def _x_circle(i: int, n: int):
        """
        Calculate the x-coordinate of a point on a circle.
        :param i: Index of the point.
        :param n: Total number of points.
        :return: x-coordinate of the point.
        """
        return math.cos(2 * math.pi * i / n).real

    @staticmethod
    def _y_circle(i: int, n: int):
        """
        Calculate the y-coordinate of a point on a circle.
        :param i: Index of the point.
        :param n: Total number of points.
        :return: y-coordinate of the point.
        """
        return math.sin(2 * math.pi * i / n).real

    @staticmethod
    def make_line(n_buses: int, length: int) -> List[Dict[str, float]]:
        """
        Create a linear bus topology with the specified number of buses.
        :param n_buses: Number of buses to create.
        :param length: Length of the line on which the buses are placed.
        :return: List of dictionaries containing x and y coordinates for each bus.
        """
        return [{'x': float(i) * length / n_buses, 'y': 0.0} for i in range(1, n_buses + 1)]

    @staticmethod
    def make_grid(n_buses: int, n_buses_per_row: int) -> List[Dict[str, float]]:
        """
        Create a grid bus topology with the specified number of buses.
        :param n_buses: Number of buses to create.
        :param n_buses_per_row: Number of buses per row in the grid.
        :return: List of dictionaries containing x and y coordinates for each bus.
        """
        return [{'x': float(i % n_buses_per_row), 'y': float(i // n_buses_per_row)} for i in range(1, n_buses + 1)]

    @staticmethod
    def make_random(n_buses: int, x_range: float = 10.0, y_range: float = 10.0) -> List[Dict[str, float]]:
        """
        Create a random bus topology with the specified number of buses.
        :param n_buses: Number of buses to create.
        :param x_range: Range for x coordinates.
        :param y_range: Range for y coordinates.
        :return: List of dictionaries containing x and y coordinates for each bus.
        """
        return [{'x': np.random.uniform(0, x_range), 'y': np.random.uniform(0, y_range)} for _ in range(1, n_buses + 1)]

    @classmethod
    def make_round(cls, n_buses: int, radius: float = 10.0) -> List[Dict[str, float]]:
        """
        Create a round bus topology with the specified number of buses.
        :param n_buses: Number of buses to create.
        :param radius: Radius of the circle on which the buses are placed.
        :return: List of dictionaries containing x and y coordinates for each bus.
        """
        return [
            {'x': radius * cls._x_circle(i, n_buses), 'y': radius * cls._y_circle(i, n_buses)}
            for i in range(1, n_buses + 1)
        ]

    @classmethod
    def make_layered_round(cls, n_buses: int, n_buses_per_layer: int, radius: float = 10.0) -> List[Dict[str, float]]:
        """
        Create a topology of concentric bus rings with the specified number of buses.
        :param n_buses: Number of buses to create.
        :param n_buses_per_layer: Number of buses per layer.
        :param radius: Radius of the circle on which the outer layer of buses is placed.
        :return: List of dictionaries containing x and y coordinates for each bus.
        """
        n_layers = math.ceil(n_buses / n_buses_per_layer)
        return [
            {
                'x': radius * math.ceil(i / n_buses_per_layer) / n_layers * cls._x_circle(i, n_buses),
                'y': radius * math.ceil(i / n_buses_per_layer) / n_layers * cls._y_circle(i, n_buses),
            }
            for i in range(1, n_buses + 1)
        ]


class TransmissionTopology:
    @staticmethod
    def _get_bus_combinations(n_buses: int) -> List[tuple[BusId, BusId]]:
        """
        Generate all unique combinations of bus pairs for transmission lines.
        :return: List of tuples containing bus pairs.
        """
        return sorted(combinations([BusId(i) for i in range(1, n_buses + 1)], 2))

    @staticmethod
    def make_sequential(n_buses: int) -> List[Dict[str, BusId]]:
        """
        Create a linear transmission topology with the specified number of buses.
        :param n_buses: Number of buses to connect.
        :return: List of dictionaries containing bus connections.
        """
        return [{'bus1': BusId(i), 'bus2': BusId(i + 1)} for i in range(n_buses - 1)]

    @staticmethod
    def make_random(n_buses: int, n_connections: int) -> List[Dict[str, BusId]]:
        """
        Create a random transmission topology with the specified number of buses and connections.
        :param n_buses: Number of buses to connect.
        :param n_connections: Number of connections to create.
        :return: List of dictionaries containing bus connections.
        """
        connections = []
        possible_connections = TransmissionTopology._get_bus_combinations(n_buses)
        for _ in range(n_connections):
            bus1, bus2 = np.random.choice(possible_connections)
            connections.append({'bus1': bus1, 'bus2': bus2})
        return connections

    @staticmethod
    def make_grid(n_buses: int, n_buses_per_row: int) -> List[Dict[str, BusId]]:
        """
        To use in combination with BusTopology.make_grid().
        Create a grid transmission topology with the specified number of buses.
        :param n_buses: Number of buses to connect.
        :param n_buses_per_row: Number of buses per row in the grid.
        :return: List of dictionaries containing bus connections.
        """
        connections = []
        for i in range(1, n_buses + 1):
            if i % n_buses_per_row != 0:  # Connect to the right bus
                connections.append({'bus1': BusId(i), 'bus2': BusId(i + 1)})
            if i + n_buses_per_row < n_buses:  # Connect to the bus below
                connections.append({'bus1': BusId(i), 'bus2': BusId(i + n_buses_per_row)})
        return connections

    @staticmethod
    def make_spiderweb(n_buses: int, n_buses_per_layer: int) -> List[Dict[str, BusId]]:
        """
        To use in combination with BusTopology.make_layered_round().
        Create a spiderweb-like transmission topology.
        :param n_buses: Total number of buses.
        :param n_buses_per_layer: Number of buses per layer.
        :return: List of dictionaries containing bus connections.
        """
        connections = []
        n_layers = math.ceil(n_buses / n_buses_per_layer)
        for layer in range(n_layers):
            for i in range(1, n_buses_per_layer + 1):
                bus1 = BusId(layer * n_buses_per_layer + i)
                if i % n_buses_per_layer == 1:  # there is a bus to the left of the first bus in the layer
                    connections.append({'bus1': bus1, 'bus2': BusId((layer + 1) * n_buses_per_layer + i - 1)})
                if layer < n_layers - 1:  # there is a bus in the upper layer
                    connections.append({'bus1': bus1, 'bus2': BusId((layer + 1) * n_buses_per_layer + i)})
                if i < n_buses_per_layer:  # there is a bus to the right in the same layer
                    connections.append({'bus1': bus1, 'bus2': BusId(layer * n_buses_per_layer + i + 1)})

        return connections

    def make_connect_n_closest(self, buses: BusRepo, n_connections: int) -> List[Dict[str, BusId]]:
        """
        Create a transmission topology that connects each bus to its n closest buses.
        :param buses: BusRepo containing the buses to connect.
        :param n_connections: Number of connections per bus.
        :return: List of dictionaries containing bus connections.
        """
        # TODO: Autogenerated by Github Copilot, needs review
        connections = []
        for bus in buses:
            distances = [
                (other_bus, np.linalg.norm(np.array([bus.x, bus.y]) - np.array([other_bus.x, other_bus.y])))
                for other_bus in buses if other_bus.id != bus.id
            ]
            closest_buses = sorted(distances, key=lambda x: x[1])[:n_connections]
            for other_bus, _ in closest_buses:
                connections.append({'bus1': bus.id, 'bus2': other_bus.id})
        return connections


class BaseGameInitializer(ABC):
    """
    Abstract base class for initializing game components.
    Subclasses should implement methods to initialize buses, assets, and transmission.
    """

    def __init__(self, settings: GameSettings) -> None:
        """
        Initialize the game initializer with the provided game settings.
        :param settings: GameSettings instance containing the game configuration.
        """
        self.settings = settings

    def create_new_game(
        self, game_id: GameId, player_names: list[str], player_colors: Optional[list[str]] = None
    ) -> GameState:
        """
        Create a new game state with the given game ID and settings.
        :param game_id: Unique identifier for the game.
        :param player_names: List of player names.
        :param player_colors: List of player colors.
        :return: A new GameState instance with the provided game ID and settings.
        """
        assert (
            len(player_names) == self.settings.n_players == len(player_colors) if player_colors else True
        ), "Number of player names and colors must match the number of players defined in game settings."

        if player_colors is None:
            color_map = cm.get_cmap('hsv', self.settings.n_players)
            player_colors = [color_map(i / self.settings.n_players)[:3] for i in range(self.settings.n_players)]
            player_colors = [f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}" for r, g, b in player_colors]

        new_game = GameState(
            game_id=game_id,
            game_settings=self.settings,
            phase=Phase(0),
            players=self._create_players_repo(names=player_names, colors=player_colors),
            buses=self._create_buses_repo(),
            assets=self._create_assets_repo(),
            transmission=self._create_transmission_repo(),
            market_coupling_result=None,
        )
        return new_game

    def _create_players_repo(self, names: List[str], colors: List[str]) -> PlayerRepo:
        """
        Create a PlayerRepo with the given player names and colors.
        :param names: List of player names.
        :param colors: List of player colors.
        :return: A PlayerRepo instance with the initialized players.
        """
        assert (
            len(names) == len(colors) == self.settings.n_players
        ), "Number of names and colors must match the number of players."

        ids = [PlayerId(i) for i in range(len(names))]

        players = [
            Player(
                id=player_id,
                name=name,
                color=color,
                money=self.settings.initial_funds,
                is_having_turn=False,  # Initial state, no player has a turn yet
            )
            for player_id, name, color in zip(ids, names, colors)
        ]

        return PlayerRepo(players)

    @abstractmethod
    def _create_buses_repo(self) -> BusRepo:
        """
        Create an initial BusRepo.
        :return: A new BusRepo instance.
        """
        # there must be at least one bus per player
        raise NotImplementedError("Initial bus configuration not implemented.")

    @abstractmethod
    def _create_assets_repo(self) -> AssetRepo:
        """
        Create an initial AssetRepo.
        :return: A new AssetRepo instance.
        """
        # there must be at least one ice_cream load per player
        raise NotImplementedError("Initial asset configuration not implemented.")

    @abstractmethod
    def _create_transmission_repo(self) -> TransmissionRepo:
        """
        Create an initial TransmissionRepo.
        :return: A new TransmissionRepo instance.
        """
        # all buses need to be connected
        raise NotImplementedError("Initial transmission configuration not implemented.")


class DefaultGameInitializer(BaseGameInitializer):
    """
    Concrete implementation of NewGameInitializer for initializing game components with default settings.
    This class provides methods to create initial repositories for buses, assets, and transmission.
    """

    def create_buses_repo(self) -> BusRepo:
        topology = BusTopology.make_layered_round(
            n_buses=self.settings.n_buses, n_buses_per_layer=self.settings.n_players, radius=10.0
        )
        buses = [
            (
                Bus(id=BusId(i), player_id=PlayerId(i), **topology[i])
                if i < self.settings.n_players
                else Bus(id=BusId(i), **topology[i])
            )  # Neutral bus not owned by any player
            for i in range(1, self.settings.n_buses + 1)
        ]
        return BusRepo(buses)

    def create_assets_repo(self) -> AssetRepo:
        assets = []
        # Create one ice cream load for each player
        for i in range(1, self.settings.n_players + 1):
            assets.append(
                AssetInfo(
                    id=AssetId(i),
                    owner_player=PlayerId(i),
                    asset_type=AssetType.LOAD,
                    bus=BusId(i),
                    power_expected=50.0,
                    power_std=0.0,
                    is_for_sale=False,
                    purchase_cost=0.0,
                    operating_cost=self.settings.initial_funds / 20,
                    marginal_price=0.0,
                    bid_price=self.settings.initial_funds / 2,
                    is_ice_cream=True,
                )
            )
        # Create the rest of the assets as npc generators
        for i in range(self.settings.n_players + 1, self.settings.n_init_assets + 1):
            assets.append(
                AssetInfo(
                    id=AssetId(i),
                    owner_player=PlayerId.get_npc(),
                    asset_type=AssetType.GENERATOR,
                    bus=BusId(np.random.uniform(0, self.settings.n_buses)),  # Assign to a bus
                    power_expected=60.0,
                    power_std=0.5,
                    is_for_sale=True,
                    purchase_cost=self.settings.initial_funds / 4,
                    operating_cost=self.settings.initial_funds / 20,
                    marginal_price=self.settings.initial_funds / 20,
                    bid_price=np.random.uniform(self.settings.initial_funds / 20, self.settings.initial_funds / 2),
                    is_ice_cream=False,
                )
            )
        return AssetRepo(assets)

    def create_transmission_repo(self) -> TransmissionRepo:
        topology = TransmissionTopology.make_spiderweb(
            n_buses=self.settings.n_buses, n_buses_per_layer=self.settings.n_players
        )
        lines = [
            TransmissionInfo(
                id=TransmissionId(i),
                owner_player=PlayerId.get_npc(),  # NPC owns all initial transmissions
                bus1=bus_pair["bus1"],
                bus2=bus_pair["bus2"],
                reactance=np.random.uniform(0.1, 1.0),  # Random reactance for each transmission
                health=5,
                operating_cost=np.random.uniform(0.01, 0.1),
                is_for_sale=True,
                purchase_cost=np.random.uniform(10, 100),  # Random purchase cost for each transmission
            )
            for i, bus_pair in enumerate(topology)
        ]

        return TransmissionRepo(lines)

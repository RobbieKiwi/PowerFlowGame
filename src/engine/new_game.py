from itertools import combinations
from typing import List, Dict, Optional
from abc import ABC, abstractmethod
import math
import numpy as np

from matplotlib import cm
from pandas.core.methods.describe import select_describe_func

from src.models.assets import AssetRepo, AssetInfo, AssetId, AssetType
from src.models.buses import BusRepo, Bus
from src.models.game_settings import GameSettings
from src.models.game_state import GameState, Phase
from src.models.ids import GameId, PlayerId, BusId
from src.models.player import Player, PlayerRepo
from src.models.transmission import TransmissionRepo, TransmissionInfo, TransmissionId


class BusTopologyMaker:
    # TODO: to be updated once the geometrical tools are available

    @staticmethod
    def _x_circle(i: int, n: int) -> float:
        """
        Calculate the x-coordinate of a point on a circle.
        :param i: Index of the point.
        :param n: Total number of points.
        :return: x-coordinate of the point.
        """
        return math.cos(2 * math.pi * i / n).real

    @staticmethod
    def _y_circle(i: int, n: int) -> float:
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
        n_bins = n_buses
        position_bins = np.linspace(0, 1, n_bins)
        grid_x, grid_y = np.meshgrid(position_bins, position_bins, indexing='ij')
        position_grid = np.column_stack([grid_x.ravel(), grid_y.ravel()])
        possible_indices = list(range(n_bins ** 2))
        selection = np.random.choice(possible_indices, n_buses, replace=False)
        return [
            {
                'x': float(position_grid[idx, 0]) * x_range,
                'y': float(position_grid[idx, 1]) * y_range
            }
            for idx in selection
        ]

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


class TransmissionTopologyMaker:
    @staticmethod
    def _get_bus_combinations(bus_repo: BusRepo) -> List[tuple[BusId, BusId]]:
        """
        Generate all unique combinations of bus pairs for transmission lines.
        :param bus_repo: BusRepo containing the buses in the game.
        :return: List of tuples containing bus pairs.
        """
        return sorted(combinations(bus_repo.bus_ids, 2))

    @staticmethod
    def make_sequential(bus_repo: BusRepo) -> List[Dict[str, BusId]]:
        """
        Create a linear transmission topology with the specified number of buses.
        :param bus_repo: BusRepo containing the buses in the game.
        :return: List of dictionaries containing bus connections.
        """
        return [{'bus1': bus_repo.bus_ids[i], 'bus2': bus_repo.bus_ids[i + 1]} for i in range(len(bus_repo))]

    @staticmethod
    def make_random(bus_repo: BusRepo, n_connections: int) -> List[Dict[str, BusId]]:
        """
        Create a random transmission topology with the specified number of buses and connections.
        :param bus_repo: BusRepo containing the buses in the game.
        :param n_connections: Number of connections to create.
        :return: List of dictionaries containing bus connections.
        """
        connections = []
        possible_connections = TransmissionTopologyMaker._get_bus_combinations(bus_repo)
        for _ in range(n_connections):
            bus1, bus2 = np.random.choice(possible_connections, replace=False)
            connections.append({'bus1': BusId(bus1), 'bus2': BusId(bus2)})
        return connections

    @staticmethod
    def make_grid(bus_repo: BusRepo, n_buses_per_row: int) -> List[Dict[str, BusId]]:
        """
        Create a grid transmission topology with the specified number of buses.
        :param bus_repo: BusRepo containing the buses in the game.
        :param n_buses_per_row: Number of buses per row in the grid.
        :return: List of dictionaries containing bus connections.
        """
        connections = []
        n_buses = len(bus_repo)
        for i in range(n_buses):
            if (i + 1) % n_buses_per_row != 0:  # Connect to the right bus
                connections.append({'bus1': bus_repo.bus_ids[i], 'bus2': bus_repo.bus_ids[i + 1]})
            if i + n_buses_per_row < n_buses:  # Connect to the bus below
                connections.append({'bus1': bus_repo.bus_ids[i], 'bus2': bus_repo.bus_ids[i + n_buses_per_row]})
        return connections

    @staticmethod
    def make_spiderweb(bus_repo: BusRepo, n_buses_per_layer: int) -> List[Dict[str, BusId]]:
        """
        Create a spiderweb-like transmission topology.
        :param bus_repo: BusRepo containing the buses in the game.
        :param n_buses_per_layer: Number of buses per layer.
        :return: List of dictionaries containing bus connections.
        """
        connections = []
        n_buses = len(bus_repo)
        n_layers = math.ceil(n_buses / n_buses_per_layer)
        for layer in range(n_layers):
            for i in range(n_buses_per_layer):
                if layer * n_buses_per_layer + i >= n_buses:
                    break
                bus1 = bus_repo.bus_ids[layer * n_buses_per_layer + i]

                ccw_bus_idx = (layer + 1) * n_buses_per_layer + i - 1
                cw_bus_idx = layer * n_buses_per_layer + i + 1
                upper_layer_bus_idx = (layer + 1) * n_buses_per_layer + i

                if i + 1 < n_buses_per_layer and cw_bus_idx < n_buses:
                    connections.append({'bus1': bus1, 'bus2': bus_repo.bus_ids[cw_bus_idx]})
                if i % n_buses_per_layer == 0 and ccw_bus_idx < n_buses:
                    connections.append({'bus1': bus1, 'bus2': bus_repo.bus_ids[ccw_bus_idx]})
                if layer + 1 < n_layers and upper_layer_bus_idx < n_buses:
                    connections.append({'bus1': bus1, 'bus2': bus_repo.bus_ids[upper_layer_bus_idx]})

        return connections

    def make_connect_n_closest(self, bus_repo: BusRepo, n_connections: int) -> List[Dict[str, BusId]]:
        """
        Create a transmission topology that connects each bus to its n closest buses.
        :param bus_repo: BusRepo containing the buses to connect.
        :param n_connections: Number of connections per bus.
        :return: List of dictionaries containing bus connections.
        """
        # TODO: Autogenerated by Github Copilot, needs review
        connections = []
        for bus in bus_repo:
            distances = [
                (other_bus, np.linalg.norm(np.array([bus.x, bus.y]) - np.array([other_bus.x, other_bus.y])))
                for other_bus in bus_repo
                if other_bus.id != bus.id
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

        player_repo = self._create_player_repo(names=player_names, colors=player_colors)
        bus_repo = self._create_bus_repo(player_repo=player_repo)
        assets_repo = self._create_asset_repo(player_repo=player_repo, bus_repo=bus_repo)
        transmission_repo = self._ensure_no_islanded_buses(
            bus_repo=bus_repo,
            transmission_repo=self._create_transmission_repo(player_repo=player_repo, bus_repo=bus_repo),
        )

        new_game = GameState(
            game_id=game_id,
            game_settings=self.settings,
            phase=Phase(0),
            players=player_repo,
            buses=bus_repo,
            assets=assets_repo,
            transmission=transmission_repo,
            market_coupling_result=None,
        )
        return new_game

    def _create_player_repo(self, names: List[str], colors: List[str]) -> PlayerRepo:
        """
        Create a PlayerRepo with the given player names and colors.
        :param names: List of player names.
        :param colors: List of player colors.
        :return: A PlayerRepo instance with the initialized players.
        """
        assert (
            len(names) == len(colors) == self.settings.n_players
        ), "Number of names and colors must match the number of players."

        players = [
            Player(
                id=PlayerId(i),
                name=name,
                color=color,
                money=self.settings.initial_funds,
                is_having_turn=False,  # Initial state, no player has a turn yet
            )
            for i, (name, color) in enumerate(zip(names, colors), start=1)
        ]

        return PlayerRepo(players)

    @staticmethod
    def _ensure_no_islanded_buses(bus_repo: BusRepo, transmission_repo: TransmissionRepo) -> TransmissionRepo:
        """
        Ensure that all buses are connected and no bus is islanded.
        :param bus_repo: The BusRepo containing all buses.
        :param transmission_repo: The TransmissionRepo containing all transmission lines.
        :return: A TransmissionRepo with no islanded buses.
        """
        additional_connections = []
        for bus in bus_repo:
            if len(transmission_repo.get_all_at_bus(bus.id)) == 0:
                bus_to_connect = bus_repo.get_random()
                id_bus1, id_bus2 = sorted([bus.id, bus_to_connect.id])
                additional_connections.append(
                    TransmissionInfo(
                        id=TransmissionId(transmission_repo.next_id()),
                        owner_player=PlayerId.get_npc(),  # NPC owns all initial transmissions
                        bus1=id_bus1,
                        bus2=id_bus2,
                        reactance=np.random.uniform(0.1, 1.0),  # Random reactance for each transmission
                        health=5,
                        operating_cost=np.random.uniform(0.01, 0.1),
                        is_for_sale=True,
                        purchase_cost=np.random.uniform(10, 100),  # Random purchase cost for each transmission
                    )
                )
        if not additional_connections:
            return transmission_repo
        else:
            return transmission_repo + TransmissionRepo(additional_connections)

    @abstractmethod
    def _create_bus_repo(self, player_repo: PlayerRepo) -> BusRepo:
        """
        Create an initial BusRepo.
        :return: A new BusRepo instance.
        """
        # there must be at least one bus per player
        raise NotImplementedError("Initial bus configuration not implemented.")

    @abstractmethod
    def _create_asset_repo(self, player_repo: PlayerRepo, bus_repo: BusRepo) -> AssetRepo:
        """
        Create an initial AssetRepo.
        :return: A new AssetRepo instance.
        """
        # there must be at least one ice_cream load per player
        raise NotImplementedError("Initial asset configuration not implemented.")

    @abstractmethod
    def _create_transmission_repo(self, player_repo: PlayerRepo, bus_repo: BusRepo) -> TransmissionRepo:
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

    def _create_bus_repo(self, player_repo: PlayerRepo) -> BusRepo:
        topology = BusTopologyMaker.make_layered_round(
            n_buses=self.settings.n_buses,
            n_buses_per_layer=self.settings.n_players,
            radius=self.settings.map_size.height * 0.9 / 2,
        )
        buses = [
            (
                Bus(id=BusId(i + 1), player_id=player_repo.player_ids[i], **topology[i])
                if i < self.settings.n_players
                else Bus(id=BusId(i + 1), **topology[i])
            )  # Neutral bus not owned by any player
            for i in range(self.settings.n_buses)
        ]
        return BusRepo(buses)

    def _create_asset_repo(self, player_repo: PlayerRepo, bus_repo: BusRepo) -> AssetRepo:
        assets = []
        # Create one ice cream load for each player
        for i in range(self.settings.n_players):
            assets.append(
                AssetInfo(
                    id=AssetId(i + 1),
                    owner_player=player_repo.player_ids[i],
                    asset_type=AssetType.LOAD,
                    bus=bus_repo.bus_ids[i],
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
        for i in range(self.settings.n_players, self.settings.n_init_assets):
            assets.append(
                AssetInfo(
                    id=AssetId(i + 1),
                    owner_player=PlayerId.get_npc(),
                    asset_type=AssetType.GENERATOR,
                    bus=BusId(np.random.choice(bus_repo.bus_ids)),
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

    def _create_transmission_repo(self, player_repo: PlayerRepo, bus_repo: BusRepo) -> TransmissionRepo:
        topology = TransmissionTopologyMaker.make_spiderweb(
            bus_repo=bus_repo, n_buses_per_layer=self.settings.n_players
        )
        lines = [
            TransmissionInfo(
                id=TransmissionId(i + 1),
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

from typing import List, Dict, Optional

from matplotlib import cm

from src.models.assets import AssetRepo
from src.models.buses import BusRepo, Bus
from src.models.game_settings import GameSettings
from src.models.game_state import GameState, Phase
from src.models.ids import GameId, PlayerId, BusId
from src.models.player import Player, PlayerRepo
from src.models.transmission import TransmissionRepo

__all__ = ["create_new_game"]


def create_new_game(
    game_id: GameId, settings: GameSettings, player_names: list[str], player_colors: Optional[list[str]] = None
) -> GameState:
    """
    Create a new game state with the given game ID and settings.
    :param game_id: Unique identifier for the game.
    :param settings: Game settings to initialize the game state.
    :param player_names: List of player names.
    :param player_colors: List of player colors.
    :return: A new GameState instance with the provided game ID and settings.
    """
    n_players = len(player_names)

    if player_colors is None:
        color_map = cm.get_cmap('hsv', n_players)
        player_colors = [color_map(i / n_players)[:3] for i in range(n_players)]
        player_colors = [f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}" for r, g, b in player_colors]

    new_game = GameState(
        game_id=game_id,
        game_settings=settings,
        phase=Phase(0),
        players=initialize_players_repo(names=player_names, colors=player_colors, settings=settings),
        buses=initialize_buses_repo(n_players=n_players, settings=settings),
        assets=initialize_assets_repo(),
        transmission=initialize_transmission_repo(),
        market_coupling_result=None,
    )
    return new_game


def initialize_players_repo(names: List[str], colors: List[str], settings: GameSettings) -> PlayerRepo:
    """
    Create a PlayerRepo with the given player names and colors.
    :param names: List of player names.
    :param colors: List of player colors.
    :param settings: Game settings to initialize the players.
    :return: A PlayerRepo instance with the initialized players.
    """
    assert len(names) == len(colors), "Number of names and colors must match the number of players."

    ids = [PlayerId(i) for i in range(len(names))]

    players = [
        Player(
            id=player_id,
            name=name,
            color=color,
            money=settings.initial_funds,
            is_having_turn=False,  # Initial state, no player has a turn yet
        )
        for player_id, name, color in zip(ids, names, colors)
    ]

    return PlayerRepo(players)


def initialize_buses_repo(n_players: int, settings: GameSettings) -> BusRepo:
    """
    Create an initial BusRepo.
    :return: A new BusRepo instance.
    """

    def _assign_bus_location(i: int) -> Dict[str, float]:
        """
        Assign a location to the bus based on its index.
        :param i: Index of the bus.
        :return: Tuple of (x, y) coordinates for the bus.
        """
        return {'x': float(i), 'y': float(i)}  # TODO define logic for bus location (e.g., from map library)

    buses = [
        (
            Bus(id=BusId(i), player_id=PlayerId(i), **_assign_bus_location(i))
            if i < n_players
            else Bus(id=BusId(i), **_assign_bus_location(i))
        )  # Neutral bus not owned by any player
        for i in range(1, settings.n_buses + 1)
    ]
    return BusRepo(buses)


def initialize_assets_repo() -> AssetRepo:
    """
    Create an initial AssetRepo.
    :return: A new AssetRepo instance.
    """
    # TODO there must be at least one ice_cream load per player
    raise NotImplementedError("Initial asset configuration not implemented.")


def initialize_transmission_repo() -> TransmissionRepo:
    """
    Create an initial TransmissionRepo.
    :return: A new TransmissionRepo instance.
    """
    # TODO all buses need to be connected
    raise NotImplementedError("Initial transmission configuration not implemented.")

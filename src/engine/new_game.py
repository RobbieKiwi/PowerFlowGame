from src.models.game_settings import GameSettings
from src.models.ids import (
    GameId,
    PlayerId,
    BusId,
    AssetId,
    TransmissionId
)
from src.models.game_state import (
    GameState,
    Phase
)
from src.models.player import (
    Player,
    PlayerRepo
)
from src.models.buses import (
    BusRepo,
    Bus
)
from src.models.assets import (
    AssetRepo,
    AssetInfo
)
from src.models.transmission import (
    TransmissionRepo,
    TransmissionInfo
)
from typing import (
    List,
    Dict
)


all = ["create_new_game"]


def create_new_game(
        game_id: GameId,
        settings: GameSettings,
        player_names: List[str],
        player_colors: List[str]
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
    new_game = GameState(
        game_id=game_id,
        game_settings=settings,
        phase=Phase(0),
        players=_initialize_players_repo(player_names, player_colors, settings),
        buses=_initialize_buses_repo(n_players, settings),
        assets=_initialize_assets_repo(),
        transmission=_initialize_transmission_repo(),
        market_coupling_result=None,
    )
    return new_game


def _initialize_players_repo(names: List[str], colors: List[str], settings: GameSettings) -> PlayerRepo:
    """
    Create a PlayerRepo with the given player names and colors.
    :param names: List of player names.
    :param colors: List of player colors.
    :param settings: Game settings to initialize the players.
    :return: A PlayerRepo instance with the initialized players.
    """
    assert len(names) == len(colors), "Number of names and colors must match the number of players."

    players = [
        Player(
            id=PlayerId(i),
            name=name,
            color=colors[i],
            money=settings.initial_funds,
            is_having_turn=False,  # Initial state, no player has a turn yet
        )
        for i, name in enumerate(names, start=1)
    ]

    return PlayerRepo(players)


def _initialize_buses_repo(n_players: int, settings: GameSettings) -> BusRepo:
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
        Bus(id=BusId(i), player_id=PlayerId(i), **_assign_bus_location(i)) if i < n_players
        else Bus(id=BusId(i), **_assign_bus_location(i))  # Neutral bus not owned by any player
        for i in range(1, settings.n_buses + 1)
    ]
    return BusRepo(buses)


def _initialize_assets_repo() -> AssetRepo:
    """
    Create an initial AssetRepo.
    :return: A new AssetRepo instance.
    """
    # TODO there must be at least one ice_cream load per player
    raise NotImplementedError("Initial asset configuration not implemented.")


def _initialize_transmission_repo() -> TransmissionRepo:
    """
    Create an initial TransmissionRepo.
    :return: A new TransmissionRepo instance.
    """
    # TODO all buses need to be connected
    raise NotImplementedError("Initial transmission configuration not implemented.")

from typing import Optional, Self, TypeVar

import numpy as np

from src.models.assets import AssetRepo
from src.models.buses import BusRepo
from src.models.game_state import GameState, Phase
from src.models.player import PlayerRepo
from src.models.transmission import TransmissionRepo
from tests.utils.repo_maker import PlayerRepoMaker, BusRepoMaker, AssetRepoMaker, TransmissionRepoMaker

T = TypeVar("T")


def safe_random_choice(x: list[T]) -> T:
    ix = np.random.randint(len(x))
    return x[ix]


class GameStateMaker:
    def __init__(self) -> None:
        self.game_id: Optional[int] = None
        self.phase: Optional[Phase] = None
        self.player_repo: Optional[PlayerRepo] = None
        self.bus_repo: Optional[BusRepo] = None
        self.asset_repo: Optional[AssetRepo] = None
        self.transmission_repo: Optional[TransmissionRepo] = None

    def add_game_id(self, game_id: int) -> Self:
        self.game_id = game_id
        return self

    def add_phase(self, phase: Phase) -> Self:
        self.phase = phase
        return self

    def add_player_repo(self, player_repo: PlayerRepo) -> Self:
        self.player_repo = player_repo
        return self

    def add_bus_repo(self, bus_repo: BusRepo) -> Self:
        self.bus_repo = bus_repo
        return self

    def add_asset_repo(self, asset_repo: AssetRepo) -> Self:
        self.asset_repo = asset_repo
        return self

    def add_transmission_repo(self, transmission_repo: TransmissionRepo) -> Self:
        self.transmission_repo = transmission_repo
        return self

    def make(self) -> GameState:
        if self.game_id is None:
            self.game_id = 1
        if self.phase is None:
            self.phase = safe_random_choice([p for p in Phase])
        if self.player_repo is None:
            self.player_repo = PlayerRepoMaker.make_quick()
        if self.bus_repo is None:
            self.bus_repo = BusRepoMaker.make_quick(player_ids=self.player_repo.player_ids)
        if self.asset_repo is None:
            self.asset_repo = AssetRepoMaker.make_quick(player_ids=self.player_repo.player_ids, bus_repo=self.bus_repo)
        if self.transmission_repo is None:
            self.transmission_repo = TransmissionRepoMaker.make_quick(
                player_ids=self.player_repo.player_ids, bus_ids=self.bus_repo.bus_ids
            )

        return GameState(
            game_id=1,
            phase=Phase.CONSTRUCTION,
            players=self.player_repo,
            buses=self.bus_repo,
            assets=self.asset_repo,
            transmission=self.transmission_repo,
            market_coupling_result=None,
        )

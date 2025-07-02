from typing import Optional, Self

import numpy as np
import pandas as pd

from src.models.assets import AssetRepo
from src.models.buses import BusRepo
from src.models.game_settings import GameSettings
from src.models.game_state import GameState, Phase
from src.models.ids import GameId
from src.models.market_coupling_result import MarketCouplingResult
from src.models.player import PlayerRepo
from src.models.transmission import TransmissionRepo
from tests.utils.random_choice import random_choice
from tests.utils.repo_maker import PlayerRepoMaker, BusRepoMaker, AssetRepoMaker, TransmissionRepoMaker


class MarketResultMaker:
    @staticmethod
    def make_quick(
        player_repo: Optional[PlayerRepo] = None,
        bus_repo: Optional[BusRepo] = None,
        asset_repo: Optional[AssetRepo] = None,
        transmission_repo: Optional[TransmissionRepo] = None,
        n_timesteps: int = 1,
    ) -> MarketCouplingResult:
        market_time_units = pd.Index([k for k in range(n_timesteps)], name="time")

        if bus_repo is None:
            bus_repo = BusRepoMaker.make_quick(player_ids=player_repo.player_ids)
        if asset_repo is None:
            asset_repo = AssetRepoMaker.make_quick(bus_repo=bus_repo, player_ids=player_repo.player_ids)
        if transmission_repo is None:
            transmission_repo = TransmissionRepoMaker.make_quick(
                bus_ids=bus_repo.bus_ids, player_ids=player_repo.player_ids
            )

        bus_columns = pd.Index([b.as_int() for b in bus_repo.bus_ids], name="Bus")
        bus_data = np.random.rand(n_timesteps, len(bus_columns))
        bus_prices = pd.DataFrame(index=market_time_units, columns=bus_columns, data=bus_data)

        tx_columns = pd.Index([t.as_int() for t in transmission_repo.transmission_ids], name="Line")
        tx_data = np.random.rand(n_timesteps, len(tx_columns))
        transmission_flows = pd.DataFrame(index=market_time_units, columns=tx_columns, data=tx_data)

        asset_columns = pd.Index([a.as_int() for a in asset_repo.asset_ids], name="Asset")
        asset_data = np.random.rand(n_timesteps, len(asset_columns))
        assets_dispatch = pd.DataFrame(index=market_time_units, columns=asset_columns, data=asset_data)

        return MarketCouplingResult(
            bus_prices=bus_prices, transmission_flows=transmission_flows, assets_dispatch=assets_dispatch
        )


class GameStateMaker:
    def __init__(self) -> None:
        self.game_id: Optional[int] = None
        self.game_settings: Optional[GameSettings] = None
        self.phase: Optional[Phase] = None
        self.player_repo: Optional[PlayerRepo] = None
        self.bus_repo: Optional[BusRepo] = None
        self.asset_repo: Optional[AssetRepo] = None
        self.transmission_repo: Optional[TransmissionRepo] = None
        self.market_coupling_result: Optional[MarketCouplingResult] = None

    def add_game_id(self, game_id: GameId) -> Self:
        self.game_id = game_id
        return self

    def add_game_settings(self, game_settings: GameSettings) -> Self:
        self.game_settings = game_settings
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
            self.game_id = GameId(1)
        if self.game_settings is None:
            self.game_settings = GameSettings()
        if self.phase is None:
            self.phase = random_choice([p for p in Phase])
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
        if self.market_coupling_result is None:
            self.market_coupling_result = MarketResultMaker.make_quick(
                player_repo=self.player_repo,
                bus_repo=self.bus_repo,
                asset_repo=self.asset_repo,
                transmission_repo=self.transmission_repo,
            )

        return GameState(
            game_id=self.game_id,
            game_settings=self.game_settings,
            phase=Phase.CONSTRUCTION,
            players=self.player_repo,
            buses=self.bus_repo,
            assets=self.asset_repo,
            transmission=self.transmission_repo,
            market_coupling_result=self.market_coupling_result,
        )

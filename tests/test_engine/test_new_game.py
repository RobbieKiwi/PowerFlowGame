from typing import Callable
from unittest import TestCase

from src.engine.new_game import DefaultGameInitializer


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


class TestDefaultGameInitializer(TestCase):
    def setUp(self) -> None:
        self.game_id = GameId(1)
        self.player_names = ["Alice", "Bob", "Charlie"]
        self.settings = GameSettings(n_players=3, n_buses=10)

    def test_create_new_game(self) -> None:
        game_initializer = DefaultGameInitializer(settings=self.settings)
        game_state = game_initializer.create_new_game(game_id=self.game_id, player_names=self.player_names)

        self.assertIsInstance(game_state, GameState)
        self.assertEqual(game_state.game_id, self.game_id)
        self.assertEqual(len(game_state.players), len(self.player_names))
        for i, player_name in enumerate(self.player_names):
            player = game_state.players[PlayerId(i + 1)]
            self.assertEqual(player.name, player_name)
            self.assertEqual(player.money, 1000)  # Default money
            self.assertFalse(player.is_having_turn)

        self.assertIsInstance(game_state.assets, AssetRepo)
        self.assertIsInstance(game_state.buses, BusRepo)
        self.assertIsInstance(game_state.transmission, TransmissionRepo)

        # check that settings are applied correctly
        self.assertEqual(len(game_state.players), self.settings.n_players)
        self.assertEqual(len(game_state.buses), self.settings.n_buses)

        # check that every player owns an ice cream asset
        for player_id in game_state.players.player_ids:
            ice_cream_assets = game_state.assets.get_all_for_player(player_id).filter({"is_ice_cream": True})
            self.assertEqual(len(ice_cream_assets), 1, f"Player {player_id} should own at least one ice cream asset")

        # check that all buses are connected
        for bus_id in game_state.buses.bus_ids:
            bus = game_state.buses[bus_id]
            self.assertIsInstance(bus, Bus)
            self.assertGreater(
                len(game_state.transmission.get_all_at_bus(bus_id)), 0, f"Bus {bus_id} should be connected"
            )

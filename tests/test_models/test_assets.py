from itertools import count
from unittest import TestCase

import numpy as np

from src.models.assets import AssetRepo, AssetType, AssetInfo
from src.models.player import PlayerId


class TestAssets(TestCase):
    def test_make_repo(self) -> None:
        repo = self._make_repo()
        self.assertIsInstance(repo, AssetRepo)
        self.assertEqual(len(repo), 6)

    def test_query_player_assets(self) -> None:
        repo = self._make_repo()

        for p, expected_count in {PlayerId(1): 2, PlayerId(2): 1}.items():
            p_assets = repo.get_all_assets_for_player(p)
            self.assertEqual(len(p_assets), expected_count)
            for a in p_assets:
                self.assertEqual(a.owner_player, p)

    def test_query_bus_assets(self) -> None:
        repo = self._make_repo()
        for b, expected_count in {1: 1, 2: 1, 3: 0}.items():
            b_assets = repo.get_all_assets_at_bus(b)
            self.assertEqual(len(b_assets), expected_count)

    def test_query_profit_for_player(self) -> None:
        repo = self._make_repo()
        for p, expected_profit in {PlayerId(1): 4.0, PlayerId(2): 2.0}.items():
            profit = repo.get_total_profit_for_player(p)
            self.assertEqual(profit, expected_profit)

    def test_query_transmission_lines_between_buses(self) -> None:
        repo = self._make_repo()
        for pair, expected_count in {(1, 2): 1, (2, 3): 0, (1, 3): 0, (2, 1): 1}.items():
            lines = repo.get_all_transmission_lines_between_buses(pair)
            self.assertEqual(len(lines), expected_count)

    def test_delete_assets(self) -> None:
        repo = self._make_repo()
        new_repo = repo.delete_assets_for_player(PlayerId(1))
        self.assertEqual(len(repo.get_all_assets_for_player(PlayerId(1))), 2)
        self.assertEqual(len(new_repo.get_all_assets_for_player(PlayerId(1))), 0)

    def test_add_asset(self) -> None:
        # Cannot have duplicate ids
        with self.assertRaises(AssertionError):
            repo = self._make_repo()
            repo + repo

        bus_id = len(repo) + 1
        new_repo = repo + AssetInfo(id=bus_id, asset_type=AssetType.BUS, owner_player=PlayerId.get_npc(), bus1=bus_id, bus2=bus_id, x=float(np.random.rand()), y=float(np.random.rand()))
        self.assertEqual(len(new_repo), len(repo) + 1)

    @staticmethod
    def _make_repo() -> AssetRepo:
        counter = count(0)

        asset_infos: list[AssetInfo] = []
        for k in range(3):
            bus_id = next(counter)
            asset_infos.append(
                AssetInfo(
                    id=bus_id,
                    asset_type=AssetType.BUS,
                    owner_player=PlayerId.get_npc(),
                    bus1=bus_id,
                    bus2=bus_id,
                    x=float(np.random.rand()),
                    y=float(np.random.rand()),
                )
            )

        more_asset_infos = [
            AssetInfo(
                id=next(counter),
                asset_type=AssetType.GENERATOR,
                owner_player=PlayerId(1),
                bus1=1,
                bus2=1,
                x=float(np.random.rand()),
                y=float(np.random.rand()),
                marginal_price=20.0,
                operating_cost=10.0,
                health=10,
                profit=2.0
            ),
            AssetInfo(
                id=next(counter),
                asset_type=AssetType.LOAD,
                owner_player=PlayerId(1),
                bus1=2,
                bus2=2,
                x=float(np.random.rand()),
                y=float(np.random.rand()),
                marginal_price=20.0,
                operating_cost=10.0,
                health=10,
                profit=2.0
            ),
            AssetInfo(
                id=next(counter),
                asset_type=AssetType.TRANSMISSION,
                owner_player=PlayerId(2),
                bus1=1,
                bus2=2,
                x=1.0,
                y=1.0,
                reactance=0.5,
                operating_cost=10.0,
                health=10,
                profit=2.0
            ),
        ]
        asset_infos.extend(more_asset_infos)
        return AssetRepo(asset_infos)
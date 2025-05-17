from itertools import count
from unittest import TestCase

from src.models.assets import AssetRepo, AssetType, AssetInfo
from src.models.ids import BusId, AssetId
from src.models.player import PlayerId


class TestAssets(TestCase):
    def test_make_repo(self) -> None:
        repo = self._make_repo()
        self.assertIsInstance(repo, AssetRepo)
        self.assertEqual(len(repo), 3)

    def test_query_player_assets(self) -> None:
        repo = self._make_repo()

        for p, expected_count in {PlayerId(1): 2, PlayerId(2): 1}.items():
            p_assets = repo.get_all_for_player(p)
            self.assertEqual(len(p_assets), expected_count)
            for a in p_assets:
                self.assertEqual(a.owner_player, p)

    def test_query_bus_assets(self) -> None:
        repo = self._make_repo()

        for b, expected_count in {BusId(1): 1, BusId(2): 2, BusId(3): 0}.items():
            b_assets = repo.get_all_assets_at_bus(b)
            self.assertEqual(len(b_assets), expected_count)

    def test_delete_assets(self) -> None:
        repo = self._make_repo()

        new_repo = repo.delete_for_player(PlayerId(1))
        self.assertEqual(len(repo.get_all_for_player(PlayerId(1))), 2)
        self.assertEqual(len(new_repo.get_all_for_player(PlayerId(1))), 0)

    def test_add_asset(self) -> None:
        # Cannot have duplicate ids
        with self.assertRaises(AssertionError):
            repo = self._make_repo()
            repo + repo

        asset_id = AssetId(len(repo) + 1)
        new_repo = repo + AssetInfo(
            id=asset_id,
            asset_type=AssetType.GENERATOR,
            owner_player=PlayerId.get_npc(),
            bus=BusId(3),
        )
        self.assertEqual(len(new_repo), len(repo) + 1)

    @staticmethod
    def _make_repo() -> AssetRepo:
        counter = count(0)

        asset_infos = [
            AssetInfo(
                id=AssetId(next(counter)),
                asset_type=AssetType.GENERATOR,
                owner_player=PlayerId(1),
                bus=BusId(1),
                bid_price=20.0,
                operating_cost=10.0,
            ),
            AssetInfo(
                id=AssetId(next(counter)),
                asset_type=AssetType.LOAD,
                owner_player=PlayerId(1),
                bus=BusId(2),
                marginal_price=20.0,
                operating_cost=10.0,
                bid_price=0.0,
            ),
            AssetInfo(
                id=AssetId(next(counter)),
                asset_type=AssetType.LOAD,
                owner_player=PlayerId(2),
                bus=BusId(2),
                marginal_price=20.0,
                operating_cost=10.0,
                bid_price=0.0,
            ),
        ]
        return AssetRepo(asset_infos)

from unittest import TestCase

from src.models.assets import AssetRepo, AssetType, AssetInfo
from src.models.ids import BusId, AssetId
from src.models.player import PlayerId
from tests.utils.repo_maker import AssetRepoMaker, BusRepoMaker


class TestAssets(TestCase):
    def test_make_repo(self) -> None:
        repo = AssetRepoMaker.make_quick()
        self.assertIsInstance(repo, AssetRepo)

    def test_query_player_assets(self) -> None:
        player_ids = [PlayerId(1), PlayerId(2)]
        repo = AssetRepoMaker(player_ids=player_ids).add_asset(owner=PlayerId(1)).make()

        for p, expected_count in {PlayerId(1): 2, PlayerId(2): 1}.items():
            p_assets = repo.get_all_for_player(p)
            self.assertEqual(len(p_assets), expected_count)
            for a in p_assets:
                self.assertEqual(a.owner_player, p)

    def test_query_bus_assets(self) -> None:
        player_ids = [PlayerId(1), PlayerId(2)]
        bus_repo = BusRepoMaker.make_quick(n_npc_buses=10)

        buses = [BusId(1), BusId(2), BusId(2)]
        repo = AssetRepoMaker(player_ids=player_ids, bus_repo=bus_repo).add_assets_to_buses(buses=buses).make()

        for b, expected_count in {BusId(1): 1, BusId(2): 2, BusId(3): 0}.items():
            b_assets = repo.get_all_assets_at_bus(b)
            self.assertEqual(len(b_assets), expected_count)

    def test_delete_assets(self) -> None:
        player_ids = [PlayerId(1), PlayerId(2)]
        repo = AssetRepoMaker.make_quick(n_normal_assets=20, player_ids=player_ids)

        original_assets_for_p1 = len(repo.get_all_for_player(PlayerId(1)))
        self.assertGreater(original_assets_for_p1, 0)

        new_repo = repo.delete_for_player(PlayerId(1))
        new_assets_for_p1 = len(new_repo.get_all_for_player(PlayerId(1)))
        self.assertEqual(new_assets_for_p1, 0)

        # Make sure original was not modified
        self.assertEqual(original_assets_for_p1, len(repo.get_all_for_player(PlayerId(1))))

    def test_add_asset(self) -> None:
        # Cannot have duplicate ids
        repo = AssetRepoMaker.make_quick(n_normal_assets=20)

        with self.assertRaises(AssertionError):
            repo + repo

        asset_id = AssetId(len(repo) + 1)
        new_repo = repo + AssetInfo(
            id=asset_id,
            asset_type=AssetType.GENERATOR,
            owner_player=PlayerId.get_npc(),
            bus=BusId(3),
            power_expected=10.0,
            power_std=0.0,
        )
        self.assertEqual(len(new_repo), len(repo) + 1)

from itertools import count
from unittest import TestCase

from src.models.assets import AssetRepo, AssetType, AssetInfo
from src.models.ids import BusId, AssetId
from src.models.player import PlayerId
from tests.utils.repo_maker import AssetRepoMaker, BusRepoMaker


class TestPlayers(TestCase):
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
        repo = AssetRepoMaker(player_ids=player_ids).add_asset(owner=PlayerId(1)).add_asset(owner=PlayerId(1)).make()
        n_assets = len(repo.get_all_for_player(PlayerId(1)))
        new_repo = repo.delete_for_player(PlayerId(1))
        self.assertEqual(len(repo.get_all_for_player(PlayerId(1))), n_assets)
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
            power_expected=10.0,
            power_std=0.0,
        )
        self.assertEqual(len(new_repo), len(repo) + 1)

    @staticmethod
    def _make_repo() -> AssetRepo:
        player_ids = [PlayerId(1), PlayerId(2)]
        bus_repo = BusRepoMaker().add_bus(PlayerId(1)).add_bus(PlayerId(2)).add_bus().make()
        npc_bus_id = bus_repo.npc_bus_ids[0]
        p1_bus_id = bus_repo.get_bus_for_player(PlayerId(1)).id
        p2_bus_id = bus_repo.get_bus_for_player(PlayerId(2)).id

        asset_repo = (
            AssetRepoMaker(player_ids=player_ids, bus_repo=bus_repo)
            .add_asset(
                cat="Generator",
                owner=PlayerId(1),
                bus=npc_bus_id,
            )
            .add_asset(
                cat="Load",
                owner=PlayerId(2),
                bus=npc_bus_id,
            )
            .add_asset(
                cat="Generator",
                owner=PlayerId(1),
                bus=npc_bus_id,
            )
            .add_asset(
                cat="IceCream",
                owner=PlayerId(1),
                bus=p1_bus_id,
            )
            .add_asset(
                cat="IceCream",
                owner=PlayerId(2),
                bus=p2_bus_id,
            )
            .make()
        )
        return asset_repo

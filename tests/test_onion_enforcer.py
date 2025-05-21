from itertools import count
from unittest import TestCase

from src.models.assets import AssetRepo, AssetType, AssetInfo
from src.models.ids import BusId, AssetId
from src.models.player import PlayerId

from src.onion_enforcer import check_repo  # noqa


class TestOnionEnforcer(TestCase):
    def test_onion_enforcer(self) -> None:
        check_repo()

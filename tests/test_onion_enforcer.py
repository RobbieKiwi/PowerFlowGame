from unittest import TestCase

from src.onion_enforcer import check_repo  # noqa


class TestOnionEnforcer(TestCase):
    def test_onion_enforcer(self) -> None:
        check_repo()

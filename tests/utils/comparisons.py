from typing import Optional, Callable

import pandas as pd

from src.models.game_state import GameState
from src.models.market_coupling_result import MarketCouplingResult


class GameStateComparator:
    @classmethod
    def game_states_are(cls, game_state1: GameState, game_state2: GameState, equal: bool) -> bool:
        comparators = cls.get_game_state_comparator(game_state1, game_state2)
        return all(comparator() == equal for comparator in comparators.values())

    @classmethod
    def assert_game_states_are(cls, game_state1: GameState, game_state2: GameState, equal: bool) -> None:
        comparator_dict = cls.get_game_state_comparator(game_state1, game_state2)

        different_keys = [k for k, v in comparator_dict.items() if not v()]
        if equal:
            assert not len(
                different_keys
            ), f"Game states should be equal but they are different. Failed keys: {different_keys}"
        else:
            assert len(different_keys), "Game states should be different but they are equal"

    @classmethod
    def get_game_state_comparator(cls, game_state1: GameState, game_state2: GameState) -> dict[str, Callable[[], bool]]:
        return {
            "game_id": lambda: game_state1.game_id == game_state2.game_id,
            "game_settings": lambda: game_state1.game_settings == game_state2.game_settings,
            "phase": lambda: game_state1.phase == game_state2.phase,
            "players": lambda: game_state1.players == game_state2.players,
            "buses": lambda: game_state1.buses == game_state2.buses,
            "assets": lambda: game_state1.assets == game_state2.assets,
            "transmission": lambda: game_state1.transmission == game_state2.transmission,
            "market_coupling_result": lambda: cls.market_coupling_result_is_equal(
                game_state1.market_coupling_result, game_state2.market_coupling_result
            ),
        }

    @staticmethod
    def market_coupling_result_is_equal(
        result1: Optional[MarketCouplingResult], result2: Optional[MarketCouplingResult]
    ) -> bool:
        if result1 is None and result2 is None:
            return True
        if result1 is None or result2 is None:
            return False

        def check_df(df1: pd.DataFrame, df2: pd.DataFrame) -> bool:
            if df1.empty and df2.empty:
                return True
            return df1.equals(df2)

        if not check_df(result1.bus_prices, result2.bus_prices):
            return False
        if not check_df(result1.transmission_flows, result2.transmission_flows):
            return False
        if not check_df(result1.assets_dispatch, result2.assets_dispatch):
            return False
        return True


def game_states_are_equal(game_state1: GameState, game_state2: GameState) -> bool:
    return GameStateComparator.game_states_are(game_state1=game_state1, game_state2=game_state2, equal=True)


def assert_game_states_are_equal(game_state1: GameState, game_state2: GameState) -> None:
    GameStateComparator.assert_game_states_are(game_state1=game_state1, game_state2=game_state2, equal=True)


def assert_game_states_are_not_equal(game_state1: GameState, game_state2: GameState) -> None:
    GameStateComparator.assert_game_states_are(game_state1=game_state1, game_state2=game_state2, equal=False)

from src.models.game_state import GameState
import pandas as pd


def game_states_are_equal(game_state1: GameState, game_state2: GameState) -> bool:

    if not (
        game_state1.game_id == game_state2.game_id
        and game_state1.game_settings == game_state2.game_settings
        and game_state1.phase == game_state2.phase
        and game_state1.players == game_state2.players
        and game_state1.buses == game_state2.buses
        and game_state1.assets == game_state2.assets
        and game_state1.transmission == game_state2.transmission
    ):
        return False
    if game_state1.market_coupling_result is None:
        if not game_state2.market_coupling_result is None:
            return False
    else:
        for attribute, df in vars(game_state1.market_coupling_result).items():
            if not isinstance(df, pd.DataFrame):
                raise NotImplementedError(f"Attribute {attribute} in MarketCouplingResult is not a DataFrame")
            if not df.equals(getattr(game_state2.market_coupling_result, attribute)):
                return False
    return True


def assert_game_states_are_equal(game_state1: GameState, game_state2: GameState) -> None:
    assert game_states_are_equal(game_state1=game_state1, game_state2=game_state2)


def assert_game_states_are_not_equal(game_state1: GameState, game_state2: GameState) -> None:
    assert not game_states_are_equal(
        game_state1=game_state1, game_state2=game_state2
    ), "Game states should not be equal, but they are."

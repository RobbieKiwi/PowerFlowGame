# These are the game settings that might change


class Settings:
    """
    Game settings that might change at the start of the game.
    """
    def __init__(self,
                 n_players: int = 2,
                 max_rounds: int = 100,
                 starting_lives: int = 3,
                 starting_cash: int = 500,
                 min_cash: int = 0,
                 max_cash: int = 10_000
                 ) -> None:
        self._n_players = n_players
        self._max_rounds = max_rounds
        self._starting_lives = starting_lives
        self._starting_cash = starting_cash
        self._min_cash = min_cash
        self._max_cash = max_cash

    @property
    def n_players(self) -> int:
        return self._n_players
    @property
    def max_rounds(self) -> int:
        return self._max_rounds
    @property
    def starting_lives(self) -> int:
        return self._starting_lives
    @property
    def starting_cash(self) -> int:
        return self._starting_cash
    @property
    def min_cash(self) -> int:
        return self._min_cash
    @property
    def max_cash(self) -> int:
        return self._max_cash
from src.models.event import Event
from src.models.game_state import GameState
from src.models.settings import Settings


class Engine:
    def __init__(self, settings: Settings) -> None:
        self.game_state = self.setup_game(settings)

    def handle_event(self, event: Event) -> None:
        """
        Events happen every time a player takes an action or a timer runs out.
        Every time an event occurs, the engine is informed and it can then:
        -Update the game state
        -Send messages back to the player interface if required
        :param event:
        """
        raise NotImplementedError()

    def setup_game(self, settings: Settings) -> GameState:
        """
        Set up the game. This includes setting up the players, the game state,
        and any other necessary components.
        :param settings: The game settings.
        :return: The initial game state.
        """
        raise NotImplementedError()

    def play_game(self) -> None:
        """
        Play the game. This includes running the game loop, handling events,
        and updating the game state.
        """
        while not self.game_state.is_game_over:
            self.initialize_round()
            # phase 1: phases.construction
            # phase 2: phases.sneaky_tricks
            # phase 3: phases.da_auction
            self.finalize_round()

    def initialize_round(self) -> None:
        """
        Initialize the game state. This includes setting up the players'
        turn order, the game state, and any other necessary components.
        """
        raise NotImplementedError()

    def finalize_round(self) -> None:
        """
        Finalize the game state. This includes updating the players,
        the game state, and any other necessary components.
        """
        self.update_alive_players()
        self.update_game_over_condition()
        self.game_state.next_round()

    def update_alive_players(self) -> None:
        """
        Check if any players died this round and update their status.
        If not, skip to the next player.
        """
        for player in self.game_state.players:
            if player.is_alive:
                if player.lives == 0 and player.cash <= 0:
                    player.die()

    def update_game_over_condition(self) -> None:
        """
        Check if the game is over and update the game state accordingly.
        The game is over when less than two players are alive.
        This condition is checked at the end of DA_AUCTION phase.
        """
        players_alive = self.game_state.players_alive
        if len(players_alive) < 2:
            self.game_state.end_game()
            if players_alive:
                # There is only one player alive, they are the winner.
                raise NotImplementedError()
            else:
                # All players are dead, what happens then?
                raise NotImplementedError()


if __name__ == "__main__":
    # Example usage
    settings = Settings()
    engine = Engine(settings)
    engine.play_game()
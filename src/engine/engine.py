from src.models.game_state import GameState
from src.models.message import (
    UpdateBidRequest,
    BuyAssetRequest,
    EndTurn,
    UpdateBidResponse,
    BuyAssetResponse,
    NewPhase,
    ToGameMessage,
    FromGameMessage,
)


class Engine:
    @classmethod
    def handle_message(cls, game_state: GameState, msg: ToGameMessage) -> tuple[GameState, list[FromGameMessage]]:
        """
        Messages can come from players or from the game itself
        Every time a message occurs, the engine is informed and it can then:
        -Update the game state
        -Send messages back to the players OR to itself
        :param game_state: The current state of the game
        :param msg: The triggering message
        :return: The new game state and a list of messages to be sent
        """
        # Handle the message based on its type
        if isinstance(msg, NewPhase):
            return cls.handle_new_phase_message(game_state, msg)
        elif isinstance(msg, UpdateBidRequest):
            return cls.handle_update_bid_message(game_state, msg)
        elif isinstance(msg, BuyAssetRequest):
            return cls.handle_buy_asset_message(game_state, msg)
        elif isinstance(msg, EndTurn):
            return cls.handle_end_turn_message(game_state, msg)
        else:
            raise NotImplementedError(f"message type {type(msg)} not implemented.")

    @classmethod
    def handle_new_phase_message(
        cls,
        game_state: GameState,
        msg: NewPhase,
    ) -> tuple[GameState, list[FromGameMessage]]:
        """
        Handle a new phase message.
        :param game_state: The current state of the game
        :param msg: The triggering message
        :return: The new game state and a list of messages to be sent to the player interface
        """
        # TODO Do something depending on what phase we are in
        # TODO if we are in the da_auction phase, we need to run the market coupling algorithm
        raise NotImplementedError()

    @classmethod
    def handle_update_bid_message(
        cls,
        game_state: GameState,
        msg: UpdateBidRequest,
    ) -> tuple[GameState, list[UpdateBidResponse]]:
        """
        Handle an update bid message.
        :param game_state: The current state of the game
        :param msg: The triggering message
        :return: The new game state and a list of messages to be sent to the player interface
        """
        # TODO Check if the bid is valid (including if the player can afford it).
        # TODO Update bids in the game state
        # TODO Return one UpdateBidResponse for the player who made the bid
        raise NotImplementedError()

    @classmethod
    def handle_buy_asset_message(
        cls,
        game_state: GameState,
        msg: BuyAssetRequest,
    ) -> tuple[GameState, list[BuyAssetResponse]]:
        """
        Handle a buy asset message.
        :param game_state: The current state of the game
        :param msg: The triggering message
        :return: The new game state and a list of messages to be sent to the player interface
        """
        # TODO Check if the request is valid (including if the asset is for sale and the player can afford it).
        # TODO Update asset ownership
        # TODO Return a BuyAssetResponse
        raise NotImplementedError()

    @classmethod
    def handle_end_turn_message(
        cls,
        game_state: GameState,
        msg: EndTurn,
    ) -> tuple[GameState, list[NewPhase]]:
        """
        Handle an end turn message.
        :param game_state: The current state of the game
        :param msg: The triggering message
        :return: The new game state and a list of messages to be sent to the player interface
        """
        # TODO Update the player to indicate that their turn has ended
        # TODO If this phase requires players to play one by one (Do we need such a phase?) Then cycle to the next player
        # TODO Check if all players have ended their turns and we need to move on to the next phase
        # TODO If necessary, return an message to signal yourself to go to a different phase
        raise NotImplementedError()

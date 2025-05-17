from src.models.event import (
    Event,
    EngineEvent,
    UpdateBidEvent,
    BuyAssetEvent,
    EndTurnEvent,
)
from src.models.game_state import GameState


class Engine:
    @classmethod
    def handle_event(
        cls, game_state: GameState, event: Event
    ) -> tuple[GameState, list[EngineEvent]]:
        """
        Events happen every time a player takes an action or a timer runs out.
        Every time an event occurs, the engine is informed and it can then:
        -Update the game state
        -Send messages back to the player interface if required
        :param game_state: The current state of the game
        :param event: The triggering event
        :return: The new game state and a list of events to be sent to the player interface
        """
        # Handle the event based on its type
        if isinstance(event, UpdateBidEvent):
            return cls.handle_update_bid_event(game_state, event)
        elif isinstance(event, BuyAssetEvent):
            return cls.handle_buy_asset_event(game_state, event)
        elif isinstance(event, EndTurnEvent):
            return cls.handle_end_turn_event(game_state, event)
        else:
            raise NotImplementedError(f"Event type {type(event)} not implemented.")

    @classmethod
    def handle_update_bid_event(
        cls,
        game_state: GameState,
        event: Event,
    ) -> tuple[GameState, list[EngineEvent]]:
        """
        Handle an update bid event.
        :param game_state: The current state of the game
        :param event: The triggering event
        :return: The new game state and a list of events to be sent to the player interface
        """
        # TODO Update bids in the game state and then return updated game state and maybe engine events
        raise NotImplementedError()

    @classmethod
    def handle_buy_asset_event(
        cls,
        game_state: GameState,
        event: Event,
    ) -> tuple[GameState, list[EngineEvent]]:
        """
        Handle a buy asset event.
        :param game_state: The current state of the game
        :param event: The triggering event
        :return: The new game state and a list of events to be sent to the player interface
        """
        # TODO Update assets ownership in the game state and then return updated game state and maybe engine events
        raise NotImplementedError()

    @classmethod
    def handle_end_turn_event(
        cls,
        game_state: GameState,
        event: Event,
    ) -> tuple[GameState, list[EngineEvent]]:
        """
        Handle an end turn event.
        :param game_state: The current state of the game
        :param event: The triggering event
        :return: The new game state and a list of events to be sent to the player interface
        """
        # TODO Update the player to indicate that their turn has ended.
        # If in the current phase the players need to take turns (asynchronous), then go to the next player
        # If all turns are over, then do some special action and go to the next phase?
        raise NotImplementedError()

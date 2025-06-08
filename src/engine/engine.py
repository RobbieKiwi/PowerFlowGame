from src.models.event import (
    Event,
    UpdateBidRequest,
    BuyAssetRequest,
    EndTurn,
    UpdateBidResponse,
    BuyAssetResponse,
    NewPhase,
)
from src.models.game_state import GameState


class Engine:
    @classmethod
    def handle_event(cls, game_state: GameState, event: Event) -> tuple[GameState, list[Event]]:
        """
        Events happen every time a player takes an action or a timer runs out.
        Every time an event occurs, the engine is informed and it can then:
        -Update the game state
        -Send messages back to the players OR to itself to trigger a new phase
        :param game_state: The current state of the game
        :param event: The triggering event
        :return: The new game state and a list of events to be sent
        """
        # Handle the event based on its type
        if isinstance(event, NewPhase):
            return cls.handle_new_phase_event(game_state, event)
        elif isinstance(event, UpdateBidRequest):
            return cls.handle_update_bid_event(game_state, event)
        elif isinstance(event, BuyAssetRequest):
            return cls.handle_buy_asset_event(game_state, event)
        elif isinstance(event, EndTurn):
            return cls.handle_end_turn_event(game_state, event)
        else:
            raise NotImplementedError(f"Event type {type(event)} not implemented.")

    @classmethod
    def handle_new_phase_event(
        cls,
        game_state: GameState,
        event: NewPhase,
    ) -> tuple[GameState, list[Event]]:
        """
        Handle a new phase event.
        :param game_state: The current state of the game
        :param event: The triggering event
        :return: The new game state and a list of events to be sent to the player interface
        """
        # TODO Do something depending on what phase we are in
        # TODO if we are in the da_auction phase, we need to run the market coupling algorithm
        raise NotImplementedError()

    @classmethod
    def handle_update_bid_event(
        cls,
        game_state: GameState,
        event: UpdateBidRequest,
    ) -> tuple[GameState, list[UpdateBidResponse]]:
        """
        Handle an update bid event.
        :param game_state: The current state of the game
        :param event: The triggering event
        :return: The new game state and a list of events to be sent to the player interface
        """
        # TODO Check if the bid is valid (including if the player can afford it).
        # TODO Update bids in the game state
        # TODO Return one UpdateBidResponseEvent for the player who made the bid
        raise NotImplementedError()

    @classmethod
    def handle_buy_asset_event(
        cls,
        game_state: GameState,
        event: BuyAssetRequest,
    ) -> BuyAssetResponse:
        """
        Handle a buy asset event.
        :param game_state: The current state of the game
        :param event: The triggering event
        :return: The new game state and a list of events to be sent to the player interface
        """
        asset = game_state.assets[event.asset_id]
        player = game_state.players[event.player_id]

        success = False
        if not asset in game_state.assets:
            message = f"Asset {asset.id} does not exist."
        elif not asset.is_for_sale:
            message = f"Asset {asset.id} is not for sale."
        elif player.money < asset.purchase_cost:
            message = f"Player {player.id} cannot afford asset {asset.id}."
        else:
            success = True
            message = f"Player {player.id} successfully bought asset {asset.id}."
            game_state.players.subtract_money(player_id=player.id, amount=asset.purchase_cost)
            game_state.assets.change_owner(asset_id=asset.id, new_owner=player.id)

        return BuyAssetResponse(
            player_id=player.id, game_state=game_state, success=success, message=message, asset_id=asset.id
        )

    @classmethod
    def handle_end_turn_event(
        cls,
        game_state: GameState,
        event: EndTurn,
    ) -> tuple[GameState, list[NewPhase]]:
        """
        Handle an end turn event.
        :param game_state: The current state of the game
        :param event: The triggering event
        :return: The new game state and a list of events to be sent to the player interface
        """
        # TODO Update the player to indicate that their turn has ended
        # TODO If this phase requires players to play one by one (Do we need such a phase?) Then cycle to the next player
        # TODO Check if all players have ended their turns and we need to move on to the next phase
        # TODO If necessary, return an event to signal yourself to go to a different phase
        raise NotImplementedError()

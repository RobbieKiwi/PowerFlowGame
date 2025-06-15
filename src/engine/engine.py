from dataclasses import replace

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

        def make_failed_response(failed_message: str) -> tuple[GameState, list[UpdateBidResponse]]:
            failed_response = UpdateBidResponse(
                player_id=msg.player_id,
                game_state=game_state,
                success=False,
                message=failed_message,
                asset_id=msg.asset_id,
            )
            return game_state, [failed_response]

        if msg.asset_id not in game_state.assets.asset_ids:
            return make_failed_response("Asset does not exist.")

        player = game_state.players[msg.player_id]
        asset = game_state.assets[msg.asset_id]
        sign_cashflow = game_state.assets.get_cashflow_sign(msg.asset_id)
        min_bid = game_state.game_settings.min_bid_price
        max_bid = game_state.game_settings.max_bid_price

        if player.id != asset.owner_player:
            return make_failed_response(f"Player {player.id} cannot bid on asset {asset.id} as they do not own it.")

        if min_bid > msg.bid_price or msg.bid_price > max_bid:
            return make_failed_response(
                f"Bid price {msg.bid_price} is not within the allowed range "
                f"[{min_bid}, {max_bid}]."
            )

        if msg.bid_price * sign_cashflow * asset.power_expected - player.money < 0:  # todo: clarify what power expected and power std mean, and correct this condition if necessary
            return make_failed_response(
                f"Player {player.id} cannot afford the bid price of {msg.bid_price} for asset {asset.id}."
            )

        new_asset = game_state.assets.update_bid_price(asset_id=msg.asset_id, bid_price=msg.bid_price)
        new_game_state = replace(game_state, assets=new_asset)

        response = UpdateBidResponse(
            player_id=player.id,
            game_state=new_game_state,
            success=True,
            message=f"Player {player.id} successfully updated bid for asset {asset.id} to {msg.bid_price}.",
            asset_id=msg.asset_id,
        )

        return new_game_state, [response]

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

        def make_failed_response(failed_message: str) -> tuple[GameState, list[BuyAssetResponse]]:
            failed_response = BuyAssetResponse(
                player_id=msg.player_id,
                game_state=game_state,
                success=False,
                message=failed_message,
                asset_id=msg.asset_id,
            )
            return game_state, [failed_response]

        player = game_state.players[msg.player_id]

        if not msg.asset_id in game_state.assets.asset_ids:
            return make_failed_response(f"Asset {msg.asset_id} does not exist.")

        asset = game_state.assets[msg.asset_id]
        if not asset.is_for_sale:
            return make_failed_response(f"Asset {asset.id} is not for sale.")
        elif player.money < asset.purchase_cost:
            return make_failed_response(f"Player {player.id} cannot afford asset {asset.id}.")

        message = f"Player {player.id} successfully bought asset {asset.id}."
        new_players = game_state.players.subtract_money(player_id=player.id, amount=asset.purchase_cost)
        new_assets = game_state.assets.change_owner(asset_id=asset.id, new_owner=player.id)

        new_game_state = replace(game_state, players=new_players, assets=new_assets)

        response = BuyAssetResponse(
            player_id=player.id, game_state=new_game_state, success=True, message=message, asset_id=asset.id
        )
        return new_game_state, [response]

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
        new_players = game_state.players.end_turn(player_id=msg.player_id)
        # TODO If this phase requires players to play one by one (Do we need such a phase?) Then cycle to the next player
        if game_state.players.are_all_players_finished():
            new_game_state = replace(game_state, players=new_players, phase=game_state.phase.get_next())
            return new_game_state, [NewPhase(phase=new_game_state.phase)]
        else:
            new_game_state = replace(game_state, players=new_players)
            return new_game_state, []


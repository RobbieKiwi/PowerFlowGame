from dataclasses import replace

from src.engine.market_coupling import MarketCouplingCalculator
from src.models.game_state import GameState, Phase
from src.models.ids import AssetId, TransmissionId, BusId
from src.models.market_coupling_result import MarketCouplingResult
from src.models.message import (
    UpdateBidRequest,
    BuyAssetRequest,
    EndTurn,
    UpdateBidResponse,
    BuyAssetResponse,
    ConcludePhase,
    ToGameMessage,
    FromGameMessage,
    GameUpdate,
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
        if isinstance(msg, ConcludePhase):
            return cls.handle_new_phase_message(game_state, msg)
        elif isinstance(msg, UpdateBidRequest):
            return cls.handle_update_bid_message(game_state, msg)
        elif isinstance(msg, BuyAssetRequest):
            return cls.handle_buy_asset_message(game_state, msg)
        elif isinstance(msg, EndTurn):
            return cls.handle_end_turn_message(game_state, msg)
        else:
            raise NotImplementedError(f"message type {type(msg)} not implemented.")

    @staticmethod
    def update_game_state_with_market_coupling_result(
        game_state: GameState,
        market_coupling_result: MarketCouplingResult,
    ) -> GameState:
        new_game_state = replace(game_state)

        # Only take first timestep
        # TODO This typing is technically a lie because the keys are ints
        assets_dispatch: dict[AssetId, float] = market_coupling_result.assets_dispatch.loc[0, :].to_dict()
        transmission_flows: dict[TransmissionId, float] = market_coupling_result.transmission_flows.loc[0, :].to_dict()
        bus_prices: dict[BusId, float] = market_coupling_result.bus_prices.loc[0, :].to_dict()

        for player in game_state.players:
            operating_cost = 0.0
            market_cashflow = 0.0
            congestion_payments = 0.0
            for asset in game_state.assets.get_all_for_player(player.id, only_active=True):
                dispatched_volume = assets_dispatch[asset.id]
                operating_cost += abs(dispatched_volume) * asset.marginal_cost + asset.fixed_operating_cost
                market_cashflow += dispatched_volume * asset.bid_price
            for line in game_state.transmission.get_all_for_player(player.id, only_active=True):
                volume = transmission_flows[line.id]
                price_spread = bus_prices[line.bus1] - bus_prices[line.bus2]
                congestion_payments += volume * price_spread
            delta_money = market_cashflow + congestion_payments - operating_cost
            new_game_state = replace(
                new_game_state,
                players=game_state.players.add_money(player_id=player.id, amount=delta_money),
            )

        new_game_state = replace(
            new_game_state,
            market_coupling_result=market_coupling_result,
        )
        return new_game_state

    @classmethod
    def handle_new_phase_message(
        cls,
        game_state: GameState,
        msg: ConcludePhase,
    ) -> tuple[GameState, list[GameUpdate]]:
        """
        Handle a new phase message.
        :param game_state: The current state of the game
        :param msg: The triggering message
        :return: The new game state and a list of messages to be sent to the player interface
        """

        def increment_phase_and_start_turns(gs: GameState) -> GameState:
            return replace(gs, phase=msg.phase.get_next(), players=game_state.players.start_all_turns())

        if msg.phase == Phase.CONSTRUCTION:
            new_game_state = increment_phase_and_start_turns(game_state)
            return new_game_state, cls._make_phase_update_messages(new_game_state)

        elif msg.phase == Phase.DA_AUCTION:
            market_result = MarketCouplingCalculator.run(game_state)
            new_game_state = cls.update_game_state_with_market_coupling_result(
                game_state=game_state, market_coupling_result=market_result
            )
            new_game_state = increment_phase_and_start_turns(new_game_state)
            msgs = cls._make_phase_update_messages(new_game_state)

            for player_id in new_game_state.players.player_ids:
                old_money = game_state.players[player_id].money
                new_money = new_game_state.players[player_id].money
                text = f"Day-ahead market cleared. Your balance was adjusted accordingly from ${old_money} to ${new_money}."
                msgs.append(
                    GameUpdate(
                        player_id=player_id,
                        game_state=new_game_state,
                        message=text,
                    )
                )
            return new_game_state, msgs

        elif msg.phase == Phase.SNEAKY_TRICKS:
            new_game_state = increment_phase_and_start_turns(game_state)
            return new_game_state, cls._make_phase_update_messages(new_game_state)

        # TODO in the new phase, one or all players have turns, so we need to update the game state accordingly
        else:
            raise NotImplementedError(f"Phase {msg.phase} not implemented.")

    @staticmethod
    def _make_phase_update_messages(game_state: GameState) -> list[GameUpdate]:
        messages: list[GameUpdate] = []
        for player_id in game_state.players.player_ids:
            messages.append(
                GameUpdate(
                    player_id=player_id,
                    game_state=game_state,
                    message=f"Phase changed to {game_state.phase.name}",
                )
            )
        return messages

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
        min_bid = game_state.game_settings.min_bid_price
        max_bid = game_state.game_settings.max_bid_price

        if player.id != asset.owner_player:
            return make_failed_response(f"Player {player.id} cannot bid on asset {asset.id} as they do not own it.")

        if not (min_bid <= msg.bid_price <= max_bid):
            return make_failed_response(
                f"Bid price {msg.bid_price} is not within the allowed range " f"[{min_bid}, {max_bid}]."
            )

        reliability_coefficient = 5  # 5 sigma covers ~99.9999% of the normal distribution
        safe_expected_market_cashflow = 0
        for asset in game_state.assets.get_all_for_player(player.id, only_active=True):
            max_expected_volume = asset.power_expected + reliability_coefficient * asset.power_std
            bid_price = asset.bid_price if asset.id != msg.asset_id else msg.bid_price
            sign = game_state.assets.get_cashflow_sign(asset.id)
            safe_expected_market_cashflow += bid_price * sign * max_expected_volume
        if player.money - safe_expected_market_cashflow < 0:
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
        elif player.money < asset.minimum_acquisition_price:
            return make_failed_response(f"Player {player.id} cannot afford asset {asset.id}.")

        message = f"Player {player.id} successfully bought asset {asset.id}."
        new_players = game_state.players.subtract_money(player_id=player.id, amount=asset.minimum_acquisition_price)
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
    ) -> tuple[GameState, list[ConcludePhase]]:
        """
        Handle an end turn message.
        :param game_state: The current state of the game
        :param msg: The triggering message
        :return: The new game state and a list of messages to be sent to the player interface
        """
        # TODO If this phase requires players to play one by one (Do we need such a phase?) Then cycle to the next player
        game_state = replace(game_state, players=game_state.players.end_turn(player_id=msg.player_id))
        if game_state.players.are_all_players_finished():
            return game_state, [ConcludePhase(phase=game_state.phase)]
        else:
            return game_state, []

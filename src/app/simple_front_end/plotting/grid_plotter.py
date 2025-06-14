import plotly.graph_objects as go

from src.app.simple_front_end.plotting.base_plot_object import PlotObject
from src.app.simple_front_end.plotting.po_asset import PlotAsset
from src.app.simple_front_end.plotting.po_bus import PlotBus
from src.app.simple_front_end.plotting.po_line import PlotTxLine
from src.app.simple_front_end.plotting.po_player_legend import PlayerLegend
from src.models.game_state import GameState
from src.models.geometry import Point
from src.models.ids import BusId


class GridPlotter:
    def plot(self, game_state: GameState) -> None:
        plot_objects = self.get_plot_objects(game_state)

        hover_texts = [po.render_hover_text() for po in plot_objects]
        shapes = [po.render_shape() for po in plot_objects]
        data = shapes + hover_texts

        fig = go.Figure(
            data=data,
            layout=go.Layout(
                title=dict(text="PowerFlowGame", font=dict(size=16)),
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20, l=5, r=5, t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, scaleanchor="y"),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            ),
        )
        fig.show()

    @staticmethod
    def get_plot_objects(game_state: GameState) -> list[PlotObject]:
        bus_dict: dict[BusId, PlotBus] = {}
        for bus in game_state.buses:
            owner = game_state.players[bus.player_id]
            bus_dict[bus.id] = PlotBus(bus=bus, owner=owner)
        buses = list(bus_dict.values())

        txs: list[PlotTxLine] = []
        for tx in game_state.transmission:
            owner = game_state.players[tx.owner_player]
            bus1 = bus_dict[tx.bus1]
            bus2 = bus_dict[tx.bus2]
            txs.append(PlotTxLine(line=tx, owner=owner, buses=(bus1, bus2)))

        assets: list[PlotAsset] = []
        for asset in game_state.assets:
            owner = game_state.players[asset.owner_player]
            bus = bus_dict[asset.bus]
            assets.append(PlotAsset(asset=asset, owner=owner, bus=bus))

        # TODO Add playable map area to state and use that to determine legend location
        legend_location = Point(x=21, y=19)
        offset_vector = Point(x=0, y=1)

        player_legends: list[PlayerLegend] = []
        players = sorted(game_state.players.as_objs(), key=lambda p: p.id, reverse=True)
        for k, player in enumerate(players):
            location = legend_location + offset_vector * k
            player_legends.append(PlayerLegend(player=player, location=location))

        return buses + txs + assets + player_legends

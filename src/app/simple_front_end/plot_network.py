import networkx as nx
import plotly.graph_objects as go
from plotly.graph_objs import Scatter

from src.app.simple_front_end.models import PlotBus, PlotTxLine, PlotAsset
from src.models.game_state import GameState
from src.models.ids import BusId


class GridPlotter:
    def plot(self, game_state: GameState) -> None:
        data = self.get_scatters(game_state)

        fig = go.Figure(
            data=data,
            layout=go.Layout(
                title=dict(text="<br>PowerFlowGame", font=dict(size=16)),
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20, l=5, r=5, t=40),
                annotations=[
                    dict(
                        showarrow=False,
                        xref="paper",
                        yref="paper",
                        x=0.005,
                        y=-0.002,
                    )
                ],
                xaxis=dict(showgrid=True, zeroline=False, showticklabels=True, scaleanchor="y"),
                yaxis=dict(showgrid=True, zeroline=False, showticklabels=True),
            ),
        )
        fig.show()

    @staticmethod
    def get_scatters(game_state: GameState) -> list[Scatter]:
        bus_dict: dict[BusId, PlotBus] = {}
        for bus in game_state.buses:
            owner = game_state.players[bus.player_id]
            bus_dict[bus.id] = PlotBus(bus=bus, owner=owner)

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

        return (
            [bus.render() for bus in bus_dict.values()]
            + [tx.render() for tx in txs]
            + [asset.render() for asset in assets]
        )

from dataclasses import dataclass
from functools import cached_property

import plotly.graph_objects as go
from plotly.graph_objs import Scatter

from src.app.simple_front_end.plotting.base_plot_object import PlotObject
from src.app.simple_front_end.plotting.po_bus import PlotBus
from src.models.colors import Color
from src.models.geometry import Point, Geometry
from src.models.player import Player
from src.models.transmission import TransmissionInfo


@dataclass(frozen=True)
class PlotTxLine(PlotObject):
    line: TransmissionInfo
    owner: Player
    buses: tuple[PlotBus, PlotBus]

    @property
    def title(self) -> str:
        return f"Line{self.line.id}"

    @property
    def color(self) -> Color:
        return self.owner.color

    @property
    def data_dict(self) -> dict[str, str]:
        return {"Owner": self.owner.name, "Health": self.line.health}

    @cached_property
    def centre(self) -> Point:
        bus1, bus2 = self.buses
        return (bus1.centre + bus2.centre) / 2

    @cached_property
    def vertices(self) -> list[Point]:
        bus1, bus2 = self.buses
        vector = bus2.centre - bus1.centre

        if bus1.is_horizontal:
            preferred_side = "tr" if vector.y > 0 else "bl"
        else:
            preferred_side = "tr" if vector.x > 0 else "bl"
        start = bus1.get_socket(preferred_side=preferred_side)  # type: ignore

        if bus2.is_horizontal:
            preferred_side = "bl" if vector.y > 0 else "tr"
        else:
            preferred_side = "bl" if vector.x > 0 else "tr"
        end = bus2.get_socket(preferred_side=preferred_side)  # type: ignore

        if bus1.is_horizontal:
            p1 = start + Point(x=0, y=vector.y * 0.1)
        else:
            p1 = start + Point(x=vector.x * 0.1, y=0)
        if bus2.is_horizontal:
            p2 = end - Point(x=0, y=vector.y * 0.1)
        else:
            p2 = end - Point(x=vector.x * 0.1, y=0)

        mid_points = Geometry.make_line(start=p1, end=p2, n_points=5)
        points = [start, *mid_points.points, end]
        return points

    @property
    def text_locations(self) -> list[Point]:
        return self.vertices

    def render_shape(self) -> Scatter:
        points = self.vertices

        if self.line.is_active:
            color = self.color
        else:
            color = self.deactivate_color(self.color)

        scatter = go.Scatter(
            x=[p.x for p in points],
            y=[p.y for p in points],
            line=dict(color=color.rgb_hex_str, width=3),
            opacity=0.8,
            mode="lines",
            hoverinfo="skip",
        )
        return scatter

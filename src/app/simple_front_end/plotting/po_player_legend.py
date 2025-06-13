from dataclasses import dataclass
from functools import cached_property

import plotly.graph_objects as go
from plotly.graph_objs import Scatter

from src.app.simple_front_end.plotting.base_plot_object import PlotObject
from src.app.simple_front_end.plotting.colors import get_contrasting_color
from src.models.geometry import Point
from src.models.player import Player


@dataclass(frozen=True)
class PlayerLegend(PlotObject):
    player: Player
    location: Point
    width: float = 1.0
    length: float = 5.0

    @property
    def title(self) -> str:
        return self.player.name

    @property
    def color(self) -> str:
        return self.player.color

    @property
    def data_dict(self) -> dict[str, str]:
        return {}

    def render_shape(self) -> Scatter:
        corner_points = [*self.corners, self.corners[0]]
        points = [p for p in corner_points]
        points.append(self.centre)

        scatter = go.Scatter(
            x=[p.x for p in points],
            y=[p.y for p in points],
            mode="lines+text",
            text=[""] * (len(points) - 1) + [self.player.name],
            fill="toself",
            fillcolor=self.color,
            line=dict(color="black", width=0),
            textfont={"size": 10, "color": get_contrasting_color(self.color)},
            hoverinfo="skip",
        )
        return scatter

    @cached_property
    def centre(self) -> Point:
        return self.location

    @cached_property
    def corners(self) -> list[Point]:
        right = Point(x=self.length / 2, y=0)
        up = Point(x=0, y=self.width / 2)
        left = right * -1
        down = up * -1

        dl = self.centre + down + left
        dr = self.centre + down + right
        ur = self.centre + up + right
        ul = self.centre + up + left

        return [dl, dr, ur, ul]

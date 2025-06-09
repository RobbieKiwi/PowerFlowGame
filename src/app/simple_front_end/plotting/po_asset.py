from dataclasses import dataclass
from functools import cached_property

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.graph_objs import Scatter

from src.app.simple_front_end.plotting.base_plot_object import Point, PlotObject
from src.app.simple_front_end.plotting.colors import get_contrasting_color
from src.app.simple_front_end.plotting.po_bus import PlotBus
from src.models.assets import AssetInfo, AssetType
from src.models.player import Player


@dataclass(frozen=True)
class PlotAsset(PlotObject):
    asset: AssetInfo
    owner: Player
    bus: PlotBus
    radius: float = 0.5

    @property
    def title(self) -> str:
        if self.asset.asset_type is AssetType.GENERATOR:
            a_type = "Gen"
        elif self.asset.asset_type is AssetType.LOAD:
            a_type = "Load"
        else:
            raise ValueError(f"Unknown asset type: {self.asset.asset_type}")
        return f"{a_type}{self.asset.id}"

    @property
    def color(self) -> str:
        return self.owner.color

    @property
    def data_dict(self) -> dict[str, str]:
        return {
            "Owner": self.owner.name,
            "Expected Power": f"{self.asset.power_expected:.0f} MW",
        }

    @cached_property
    def centre(self) -> Point:
        socket = self.bus.get_socket()
        bus_to_socket_vector = socket - self.bus.centre
        if self.bus.is_horizontal:
            unit_offset_vector = Point(x=0, y=np.sign(bus_to_socket_vector.y))
        else:
            unit_offset_vector = Point(x=np.sign(bus_to_socket_vector.x), y=0)
        return socket + unit_offset_vector * self.radius

    def render_shape(self) -> Scatter:
        theta = np.linspace(0, 2 * np.pi, 100)
        x = self.centre.x + self.radius * np.cos(theta)
        y = self.centre.y + self.radius * np.sin(theta)
        # append one value to the array
        x = np.append(x, self.centre.x)
        y = np.append(y, self.centre.y)

        if self.asset.asset_type is AssetType.GENERATOR:
            text = "G"
        else:
            text = "L"

        main = go.Scatter(
            x=x,
            y=y,
            mode="lines+text",
            text=[""] * (len(x) - 1) + [text],
            fill="toself",
            fillcolor=self.color,
            line={"width": 0.0},
            hoverinfo="skip",
            textfont={"size": 10, "color": get_contrasting_color(self.color)},
        )
        return main

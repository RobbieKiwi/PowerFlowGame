from abc import ABC, abstractmethod
from dataclasses import dataclass

import plotly.graph_objs as go
from plotly.graph_objs import Scatter

from src.models.geometry import Point


@dataclass(frozen=True)
class PlotObject(ABC):
    @abstractmethod
    def render_shape(self) -> Scatter:
        pass

    @property
    @abstractmethod
    def centre(self) -> Point:
        pass

    @property
    @abstractmethod
    def color(self) -> str:
        pass

    @property
    @abstractmethod
    def title(self) -> str:
        pass

    @property
    @abstractmethod
    def data_dict(self) -> dict[str, str]:
        pass

    @property
    def text_locations(self) -> list[Point]:
        return [self.centre]

    def render_hover_text(self) -> Scatter:
        hover_template = (
            f"<b>{self.title}</b><br><br>"
            f"{"<br>".join([f"<b>{k}</b>: {v}" for k, v in self.data_dict.items()])}<extra></extra>"
        )
        marker = go.Scatter(
            x=[p.x for p in self.text_locations],
            y=[p.y for p in self.text_locations],
            mode="markers",
            marker={
                "size": 10,
                "color": self.color,
                "symbol": "circle",
                "line": {"width": 0.0},
                "opacity": 0.0,  # Make the marker invisible
            },
            line={"width": 0.0},
            hovertemplate=hover_template,
        )
        return marker

from abc import ABC, abstractmethod
from dataclasses import dataclass

import numpy as np
import plotly.graph_objs as go
from plotly.graph_objs import Scatter

from src.models.colors import Color


@dataclass(frozen=True)
class Point:
    x: float
    y: float

    @property
    def euclidean_distance(self) -> float:
        return np.sqrt(self.x**2 + self.y**2)

    def transpose(self) -> "Point":
        return Point(x=self.y, y=self.x)

    def __str__(self) -> str:
        return f"<Point {round(self.x)}, {round(self.y)}>"

    def __add__(self, other: "Point") -> "Point":
        return Point(x=self.x + other.x, y=self.y + other.y)

    def __sub__(self, other: "Point") -> "Point":
        return Point(x=self.x - other.x, y=self.y - other.y)

    def __mul__(self, other: float) -> "Point":
        return Point(x=self.x * other, y=self.y * other)

    def __truediv__(self, other: float) -> "Point":
        return Point(x=self.x / other, y=self.y / other)


def point_linspace(start: Point, end: Point, num: int) -> list[Point]:
    """Generates a list of points linearly spaced between start and end."""
    x_values = np.linspace(start.x, end.x, num)
    y_values = np.linspace(start.y, end.y, num)
    return [Point(x=x, y=y) for x, y in zip(x_values, y_values)]


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
    def color(self) -> Color:
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
                "color": self.color.hex_str,
                "symbol": "circle",
                "line": {"width": 0.0},
                "opacity": 0.0,  # Make the marker invisible
            },
            line={"width": 0.0},
            hovertemplate=hover_template,
        )
        return marker

from dataclasses import dataclass
from functools import cached_property

import numpy as np
from plotly.graph_objs import Scatter


@dataclass(frozen=True)
class Point:
    x: float
    y: float

    @cached_property
    def length(self) -> float:
        return float(np.linalg.norm(x=[self.x, self.y], ord=2))

    def transpose(self) -> "Point":
        return Point(x=self.y, y=self.x)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Point):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def __str__(self) -> str:
        places = max(0, round(np.ceil(-np.log10(self.length)) + 2))
        return f"<Point ({round(self.x, places)},{round(self.y, places)})>"

    def __repr__(self) -> str:
        return str(self)

    def __add__(self, other: "Point") -> "Point":
        return Point(x=self.x + other.x, y=self.y + other.y)

    def __sub__(self, other: "Point") -> "Point":
        return Point(x=self.x - other.x, y=self.y - other.y)

    def __mul__(self, other: float) -> "Point":
        other = float(other)
        return Point(x=self.x * other, y=self.y * other)

    def __truediv__(self, other: float) -> "Point":
        other = float(other)
        return Point(x=self.x / other, y=self.y / other)


def point_linspace(start: Point, end: Point, num: int) -> list[Point]:
    x_values = np.linspace(start.x, end.x, num)
    y_values = np.linspace(start.y, end.y, num)
    return [Point(x=float(x), y=float(y)) for x, y in zip(x_values, y_values)]


def make_circle(center: Point, radius: float, num_points: int = 100, closed: bool = False) -> list[Point]:
    # If closed is true, the first and last points will be the same, creating a closed circle.
    if not closed:
        return make_circle(center=center, radius=radius, num_points=num_points + 1, closed=True)[:-1]

    assert num_points >= 4, "At least 4 points are required to create a closed circle."
    angles = np.linspace(0, 2 * np.pi, num_points)
    return [center + Point(x=float(radius * np.cos(angle)), y=float(radius * np.sin(angle))) for angle in angles]

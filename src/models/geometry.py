from dataclasses import dataclass
from functools import cached_property
from typing import Self, List
from enum import Enum

import numpy as np


@dataclass(frozen=True)
class Point:
    x: float
    y: float

    @cached_property
    def length(self) -> float:
        return float(np.linalg.norm(x=[self.x, self.y], ord=2))

    def transpose(self) -> "Point":
        return Point(x=self.y, y=self.x)

    def to_dict(self) -> dict[str, float]:
        return {"x": self.x, "y": self.y}

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


class Geometry:
    class ShapeType(Enum):
        EMPTY = "empty"
        LINE = "line"
        GRID = "grid"
        TRIANGLE = "triangle"
        SQUARE = "square"
        PENTAGON = "pentagon"
        HEXAGON = "hexagon"
        CIRCLE = "circle"
        COMPOSITE = "composite"

    def __init__(self, points: List[Point], shape_type: ShapeType):
        self.shape_type = shape_type
        self.points = points

    def __add__(self, other: Self | Point | List[Point]) -> Self:
        if isinstance(other, Point):
            return Geometry(points=self.points + [other], shape_type=self.ShapeType.COMPOSITE)
        if isinstance(other, List):
            return Geometry(points=self.points + other, shape_type=self.ShapeType.COMPOSITE)
        if isinstance(other, Geometry):
            return Geometry(points=self.points + other.points, shape_type=self.ShapeType.COMPOSITE)
        raise TypeError(f"Cannot add {type(other)} to Geometry")

    @classmethod
    def make_empty(cls) -> Self:
        return cls(points=[], shape_type=cls.ShapeType.EMPTY)

    @classmethod
    def make_line(cls, start: Point, end: Point, n_points: int) -> Self:
        x_values = np.linspace(start.x, end.x, n_points)
        y_values = np.linspace(start.y, end.y, n_points)
        line_points = [Point(x=float(x), y=float(y)) for x, y in zip(x_values, y_values)]
        return cls(points=line_points, shape_type=cls.ShapeType.LINE)

    @classmethod
    def make_regular_polygon(cls, center: Point, radius: float, n_points: int = 100, closed: bool = False) -> Self:
        # If closed is true, the first and last points will be the same, creating a closed circle.
        if not closed:
            polygon = cls.make_regular_polygon(center=center, radius=radius, n_points=n_points + 1, closed=True)
            polygon.points.pop(-1)
            return polygon

        assert n_points >= 3, "At least 3 points are required to create a regular polygon."

        angles = np.linspace(0, 2 * np.pi, n_points)
        polygon_points = [
            center + Point(x=float(radius * np.cos(angle)), y=float(radius * np.sin(angle))) for angle in angles
        ]
        match n_points:
            case 3:
                return cls(points=polygon_points, shape_type=cls.ShapeType.TRIANGLE)
            case 4:
                return cls(points=polygon_points, shape_type=cls.ShapeType.SQUARE)
            case 5:
                return cls(points=polygon_points, shape_type=cls.ShapeType.PENTAGON)
            case 6:
                return cls(points=polygon_points, shape_type=cls.ShapeType.HEXAGON)
        return cls(points=polygon_points, shape_type=cls.ShapeType.CIRCLE)

    @classmethod
    def make_grid(cls, start_corner: Point, width: float, height: float, n_points_per_direction: int = 10) -> Self:
        x_values = np.linspace(start_corner.x, start_corner.x + width, n_points_per_direction)
        y_values = np.linspace(start_corner.y, start_corner.y + height, n_points_per_direction)
        numpy_grid = np.meshgrid(x_values, y_values, indexing='ij')
        grid_points = [Point(x=float(x), y=float(y)) for x, y in zip(numpy_grid[0].flatten(), numpy_grid[1].flatten())]
        return cls(points=grid_points, shape_type=cls.ShapeType.GRID)

from dataclasses import dataclass
from functools import cached_property, lru_cache
from typing import Iterator, Literal, Optional

import numpy as np
import plotly.graph_objects as go
from plotly.graph_objs import Scatter

from src.models.assets import AssetInfo, AssetType
from src.models.buses import Bus
from src.models.player import Player
from src.models.transmission import TransmissionInfo


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


SocketSide = Literal["tr", "bl"]


class SocketProvider:
    def __init__(self, tr_sockets: list[Point], bl_sockets: list[Point]) -> None:
        self._tr_sockets = tr_sockets
        self._bl_sockets = bl_sockets
        self._tr_assigned = 0
        self._bl_assigned = 0

    def __str__(self) -> str:
        return f"<SocketProvider>"

    def __repr__(self) -> str:
        return f"<SocketProvider>"

    def get_socket(self, preferred_side: Optional[SocketSide] = None) -> Point:
        if not self._has_remaining_sockets():
            raise IndexError("No remaining sockets available.")

        if preferred_side is None:
            if self._tr_assigned == self._bl_assigned:
                preferred_side = np.random.choice(["tr", "bl"])
            elif self._tr_assigned < self._bl_assigned:
                preferred_side = "tr"
            else:
                preferred_side = "bl"

        if self._has_remaining_sockets(preferred_side):
            if preferred_side is "tr":
                socket = self._tr_sockets[self._tr_assigned]
                self._tr_assigned += 1
            else:
                socket = self._bl_sockets[self._bl_assigned]
                self._bl_assigned += 1
            return socket
        return self.get_socket()

    @staticmethod
    def _other_side(side: SocketSide) -> SocketSide:
        if side == "tr":
            return "bl"
        elif side == "bl":
            return "tr"
        else:
            raise ValueError(f"Invalid side: {side}. Must be 'tr' or 'bl'.")

    def _has_remaining_sockets(self, side: Optional[SocketSide] = None) -> bool:
        if side == "tr":
            return len(self._tr_sockets) > self._tr_assigned
        elif side == "bl":
            return len(self._bl_sockets) > self._bl_assigned
        elif side is None:
            return self._has_remaining_sockets("tr") or self._has_remaining_sockets("bl")
        else:
            raise ValueError(f"Invalid side: {side}. Must be 'tr', 'bl', or None.")


@dataclass(frozen=True)
class PlotBus:
    bus: Bus
    owner: Player
    width: float = 1.0
    length: float = 5.0

    def render(self) -> Scatter:
        corner_points = [*self.corners, self.corners[0]]
        points = [p for p in corner_points]
        return go.Scatter(
            x=[p.x for p in points],
            y=[p.y for p in points],
            fill="toself",
            fillcolor=self.owner.color,
            line=dict(color="black", width=1),
            mode="lines",
            name=f"Bus{self.bus.id} ({self.owner.name})",
        )

    def get_socket(self, preferred_side: Optional[SocketSide] = None) -> Point:
        return self._socket_provider.get_socket(preferred_side=preferred_side)

    @cached_property
    def _socket_provider(self) -> SocketProvider:
        relative_offsets = np.linspace(start=-0.4, stop=0.4, num=5)

        tr_offsets = [Point(x=float(offset) * self.length, y=self.width / 2) for offset in relative_offsets]
        bl_offsets = [Point(x=float(offset) * self.length, y=-1 * self.width / 2) for offset in relative_offsets]
        if self.is_horizontal:
            tr_sockets = [self.centre + o for o in tr_offsets]
            bl_sockets = [self.centre + o for o in bl_offsets]
        else:
            tr_sockets = [self.centre + o.transpose() for o in tr_offsets]
            bl_sockets = [self.centre + o.transpose() for o in bl_offsets]

        return SocketProvider(tr_sockets=tr_sockets, bl_sockets=bl_sockets)

    @cached_property
    def centre(self) -> Point:
        return Point(x=self.bus.x, y=self.bus.y)

    @cached_property
    def is_horizontal(self) -> bool:
        return bool(np.random.choice([True, False]))

    @cached_property
    def corners(self) -> list[Point]:
        right = Point(x=self.length / 2, y=0) if self.is_horizontal else Point(x=self.width / 2, y=0)
        up = Point(x=0, y=self.width / 2) if self.is_horizontal else Point(x=0, y=self.length / 2)
        left = right * -1
        down = up * -1

        dl = self.centre + down + left
        dr = self.centre + down + right
        ur = self.centre + up + right
        ul = self.centre + up + left

        return [dl, dr, ur, ul]


@dataclass(frozen=True)
class PlotTxLine:
    line: TransmissionInfo
    owner: Player
    buses: tuple[PlotBus, PlotBus]

    def get_points(self) -> list[Point]:
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

        points = [start]
        if bus1.is_horizontal:
            points.append(start + Point(x=0, y=vector.y * 0.1))
        else:
            points.append(start + Point(x=vector.x * 0.1, y=0))
        if bus2.is_horizontal:
            points.append(end - Point(x=0, y=vector.y * 0.1))
        else:
            points.append(end - Point(x=vector.x * 0.1, y=0))
        points.append(end)
        return points

    def render(self) -> Scatter:
        points = self.get_points()
        return go.Scatter(
            x=[p.x for p in points],
            y=[p.y for p in points],
            line=dict(color=self.owner.color, width=1),
            mode="lines",
            hovertemplate=f"Line{self.line.id} ({self.owner.name})",
        )


@dataclass(frozen=True)
class PlotAsset:
    asset: AssetInfo
    owner: Player
    bus: PlotBus
    radius: float = 0.5

    @cached_property
    def centre(self) -> Point:
        socket = self.bus.get_socket()
        bus_to_socket_vector = socket - self.bus.centre
        if self.bus.is_horizontal:
            unit_offset_vector = Point(x=0, y=np.sign(bus_to_socket_vector.y))
        else:
            unit_offset_vector = Point(x=np.sign(bus_to_socket_vector.x), y=0)
        return socket + unit_offset_vector * self.radius

    def render(self) -> Scatter:
        theta = np.linspace(0, 2 * np.pi, 100)
        x = self.centre.x + self.radius * np.cos(theta)
        y = self.centre.y + self.radius * np.sin(theta)
        if self.asset.asset_type is AssetType.GENERATOR:
            a_type = "Gen"
        elif self.asset.asset_type is AssetType.LOAD:
            a_type = "Load"
        else:
            raise ValueError(f"Unknown asset type: {self.asset.asset_type}")

        return go.Scatter(
            x=x,
            y=y,
            mode="lines",
            fill="toself",
            fillcolor=self.owner.color,
            line={"width": 0.0},
            name=f"{a_type}{self.asset.id} ({self.owner.name})",
        )

from dataclasses import dataclass
from functools import cached_property
from typing import Literal, Optional

import numpy as np
import plotly.graph_objects as go
from plotly.graph_objs import Scatter

from src.app.simple_front_end.plotting.base_plot_object import Point, PlotObject
from src.models.buses import Bus
from src.models.player import Player

SocketSide = Literal["tr", "bl"]


class SocketProvider:
    def __init__(self, tr_sockets: list[Point], bl_sockets: list[Point]) -> None:
        self._tr_sockets = tr_sockets
        self._bl_sockets = bl_sockets
        self._tr_assigned = 0
        self._bl_assigned = 0

    def __str__(self) -> str:
        return "<SocketProvider>"

    def __repr__(self) -> str:
        return "<SocketProvider>"

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
            if preferred_side == "tr":
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
class PlotBus(PlotObject):
    bus: Bus
    owner: Player
    width: float = 1.0
    length: float = 5.0

    @property
    def title(self) -> str:
        return f"Bus{self.bus.id}"

    @property
    def color(self) -> str:
        return self.owner.color

    @property
    def data_dict(self) -> dict[str, str]:
        return {"Owner": self.owner.name}

    def render_shape(self) -> Scatter:
        corner_points = [*self.corners, self.corners[0]]
        points = [p for p in corner_points]

        scatter = go.Scatter(
            x=[p.x for p in points],
            y=[p.y for p in points],
            fill="toself",
            fillcolor=self.owner.color,
            line=dict(color="black", width=1),
            mode="lines",
            hoverinfo="skip",
        )
        return scatter

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
        return abs(self.centre.y) > abs(self.centre.x)

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

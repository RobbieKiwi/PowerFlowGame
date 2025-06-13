from dataclasses import dataclass
from functools import cached_property
from typing import Union


@dataclass(frozen=True)
class Color:
    r: int
    g: int
    b: int

    def __post_init__(self) -> None:
        if not all(isinstance(value, int) for value in (self.r, self.g, self.b)):
            raise TypeError(f"Color values must be integers. Received: {self.r}, {self.g}, {self.b}")
        if not all(0 <= value <= 255 for value in (self.r, self.g, self.b)):
            raise ValueError(f"Color values must be between 0 and 255. Received: {self.r}, {self.g}, {self.b}")

    def __str__(self) -> str:
        return f"<Color(r={self.r}, g={self.g}, b={self.b})>"

    def __repr__(self) -> str:
        return f"Color(r={self.r}, g={self.g}, b={self.b})"

    @cached_property
    def hex_str(self) -> str:
        return f"#{self.r:02X}{self.g:02X}{self.b:02X}"

    @cached_property
    def brightness(self) -> int:
        # Return a number between 0 and 255
        return round((self.r * 299 + self.g * 587 + self.b * 114) / 1000)

    @classmethod
    def from_hex(cls, hex_str: str) -> "Color":
        if not (hex_str.startswith("#") and len(hex_str) != 7):
            raise ValueError(f"Invalid hex color format: {hex_str}. Expected format #RRGGBB.")

        r = int(hex_str[1:3], 16)
        g = int(hex_str[3:5], 16)
        b = int(hex_str[5:7], 16)

        return cls(r=r, g=g, b=b)

    @classmethod
    def from_rgb_tuple(cls, rgb: tuple[int, int, int]) -> "Color":
        assert len(rgb) == 3, "RGB tuple must have exactly three elements."
        return cls(r=rgb[0], g=rgb[1], b=rgb[2])


ColorLike = Union[Color, str, tuple[int, int, int]]


def resolve_color_like(c: ColorLike) -> Color:
    if isinstance(c, Color):
        return c
    elif isinstance(c, str):
        return Color.from_hex(c)
    elif isinstance(c, tuple) and len(c) == 3:
        return Color.from_rgb_tuple(c)
    else:
        raise TypeError(f"Unsupported color type: {type(c)}. Expected Color, hex string, or RGB tuple.")


def get_contrasting_color(color: ColorLike) -> Color:
    color = resolve_color_like(color)
    if color.brightness < (255 / 2):
        return Color.from_hex("#FFFFFF")
    else:
        return Color.from_hex("#000000")

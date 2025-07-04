import colorsys
from functools import cached_property
from typing import Union, Literal, Self

import numpy as np
from matplotlib import colormaps


class Color:
    def __init__(
        self,
        x: Union[str, tuple[int, int, int], Literal["red", "green", "blue", "black", "gray", "white"]],
        color_model: Literal["rgb", "hsv", "hls"] = "rgb",
    ):
        """
        You can create a color using a pre-defined color name, e.g. "red", "green", "blue", "black", "gray" "white".
        >>> Color("red")

        Or pass an RGB hex string, e.g. "#FF5733".
        >>> Color("#FF5733")

        You can pass a tuple of unsigned 8bit integers if you prefer
        >>> Color((255, 87, 51))

        The default model is RGB but if you want you can specify the color as hsv or hls
        >>> Color((255, 87, 51), color_model="hsv")
        """
        assert color_model in ["rgb", "hsv", "hls"], f"Invalid color model: {color_model}."

        expected_format = {"rgb": "#RRGGBB", "hsv": "#HHSSVV", "hls": "#HHLLSS"}[color_model]

        if isinstance(x, str):
            if not x.startswith("#"):
                x = {
                    "red": "#FF0000",
                    "blue": "#0000FF",
                    "green": "#00FF00",
                    "black": "#000000",
                    "gray": "#808080",
                    "white": "#FFFFFF",
                }[x]
            if not len(x) == 7:
                raise ValueError(f"Invalid hex color format: {x}. Expected format {expected_format}.")
            a = int(x[1:3], 16)
            b = int(x[3:5], 16)
            c = int(x[5:7], 16)
        else:
            assert len(x) == 3, f"{color_model.upper()} tuple must have exactly three elements. Received {x}."
            assert all(
                isinstance(value, int) for value in x
            ), f"{color_model.upper()} values must be integers. Received {x}."
            a, b, c = x

        abc = (a, b, c)
        assert all(0 <= value <= 255 for value in abc), f"Values must be between 0 and 255. Received {abc}."

        self._color_model = color_model
        self._abc = abc

    def __str__(self) -> str:
        al, bl, cl = self._color_model
        a, b, c = self._abc
        return f"<Color({al}={a}, {bl}={b}, {cl}={c})>"

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other: "Color") -> bool:
        if not isinstance(other, Color):
            return False
        return self.rgb_hex_str == other.rgb_hex_str

    def calculate_distance_factor(self, other: "Color") -> float:
        # Returns a number between 0 and 1, where 0 means the colors are identical
        assert isinstance(other, Color), f"Expected a Color instance, got {type(other)}."
        diff = (np.array(self.rgb) - np.array(other.rgb)) / 255
        return float(np.linalg.norm(x=diff, ord=2) / np.sqrt(3))

    @cached_property
    def rgb(self) -> tuple[int, int, int]:
        if self._color_model == "rgb":
            r, g, b = self._abc
            return r, g, b
        if self._color_model == "hsv":
            h, s, v = self._abc
            r, g, b = colorsys.hsv_to_rgb(h / 255, s / 255, v / 255)
        else:
            h, l, s = self._abc
            r, g, b = colorsys.hls_to_rgb(h / 255, l / 255, s / 255)
        r, g, b = round(r * 255), round(g * 255), round(b * 255)
        return r, g, b

    @cached_property
    def hsv(self) -> tuple[int, int, int]:
        if self._color_model == "hsv":
            h, s, v = self._abc
        else:
            r, g, b = self.rgb
            h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            h, s, v = round(h * 255), round(s * 255), round(v * 255)
        return h, s, v

    @cached_property
    def hls(self) -> tuple[int, int, int]:
        if self._color_model == "hls":
            h, l, s = self._abc
        else:
            r, g, b = self.rgb
            h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
            h, l, s = round(h * 255), round(l * 255), round(s * 255)
        return h, l, s

    @cached_property
    def rgb_hex_str(self) -> str:
        r, g, b = self.rgb
        return f"#{r:02X}{g:02X}{b:02X}"

    @cached_property
    def brightness_factor(self) -> float:
        # A number between 0 and 1, where 0 is black and 1 is white.
        return self.hls[1] / Color("white").hls[1]

    def to_string(self) -> str:
        return self.rgb_hex_str

    @classmethod
    def from_string(cls, s: str) -> Self:
        return cls(x=s, color_model="rgb")


def get_contrasting_color(color: Color) -> Color:
    if color.brightness_factor < 0.5:
        return Color("#FFFFFF")
    else:
        return Color("#000000")


def get_random_player_colors(n: int) -> list[Color]:
    color_map = colormaps.get_cmap('hsv')
    colors_np = [color_map(i / n) for i in range(n)]

    def convert_color(color: tuple[float, float, float, float]) -> Color:
        return Color(x=(round(color[0] * 255), int(color[1] * 255), int(color[2] * 255)), color_model="rgb")

    return [convert_color(color) for color in colors_np]

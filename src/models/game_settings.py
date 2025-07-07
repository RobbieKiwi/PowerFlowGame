from dataclasses import dataclass, field
from typing import Self

from src.models.geometry import Point, Shape, ShapeType


@dataclass(frozen=True)
class GameSettings:
    """A class to hold game settings."""

    n_buses: int = 5
    max_rounds: int = 20
    n_init_ice_cream: int = 5
    n_init_assets: int = 10
    min_bid_price: float = -100
    max_bid_price: float = 100
    initial_funds: int = 1000
    max_connections_per_bus: int = 7
    map_area: Shape = field(
        default_factory=lambda: Shape.make_rectangle(bottom_left=Point(0, 0), top_right=Point(30, 30))
    )

    def __post_init__(self) -> None:
        assert self.map_area.shape_type is ShapeType.Rectangle
        assert not self.map_area.is_closed

    def to_simple_dict(self) -> dict:
        """Convert the game settings to a simple dictionary."""
        return {
            "n_buses": self.n_buses,
            "max_rounds": self.max_rounds,
            "n_init_ice_cream": self.n_init_ice_cream,
            "n_init_assets": self.n_init_assets,
            "min_bid_price": self.min_bid_price,
            "max_bid_price": self.max_bid_price,
            "initial_funds": self.initial_funds,
            "max_connections_per_bus": self.max_connections_per_bus,
            "map_area": self.map_area.to_simple_dict(),
        }

    @classmethod
    def from_simple_dict(cls, simple_dict: dict) -> Self:
        """Create a GameSettings instance from a simple dictionary."""
        return cls(
            n_buses=simple_dict["n_buses"],
            max_rounds=simple_dict["max_rounds"],
            n_init_ice_cream=simple_dict["n_init_ice_cream"],
            n_init_assets=simple_dict["n_init_assets"],
            min_bid_price=simple_dict["min_bid_price"],
            max_bid_price=simple_dict["max_bid_price"],
            initial_funds=simple_dict["initial_funds"],
            max_connections_per_bus=simple_dict["max_connections_per_bus"],
            map_area=Shape.from_simple_dict(simple_dict["map_area"]),
        )

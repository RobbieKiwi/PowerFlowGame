from dataclasses import dataclass
from typing import Self


@dataclass(frozen=True)
class GameSettings:
    """A class to hold game settings."""

    n_players: int = 2
    n_buses: int = 5
    max_rounds: int = 20
    n_init_ice_cream: int = 5
    n_init_assets: int = 10
    initial_funds: int = 1000
    max_connections_per_bus: int = 7

    def to_simple_dict(self) -> dict:
        """Convert the game settings to a simple dictionary."""
        return {
            "n_buses": self.n_buses,
            "max_rounds": self.max_rounds,
            "n_ice_cream": self.n_init_ice_cream,
            "n_init_assets": self.n_init_assets,
            "initial_funds": self.initial_funds,
            "max_connections_per_bus": self.max_connections_per_bus,
        }

    @classmethod
    def from_simple_dict(cls, simple_dict: dict) -> Self:
        """Create a GameSettings instance from a simple dictionary."""
        return cls(
            n_buses=simple_dict["n_buses"],
            max_rounds=simple_dict["max_rounds"],
            n_init_ice_cream=simple_dict["n_ice_cream"],
            n_init_assets=simple_dict["n_init_assets"],
            initial_funds=simple_dict["initial_funds"],
            max_connections_per_bus=simple_dict["max_connections_per_bus"],
        )

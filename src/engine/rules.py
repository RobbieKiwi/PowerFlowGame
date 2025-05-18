from dataclasses import dataclass


@dataclass(frozen=True)
class Rules:
    max_connections_per_bus: int


def get_rules() -> Rules:
    return Rules(max_connections_per_bus=7)

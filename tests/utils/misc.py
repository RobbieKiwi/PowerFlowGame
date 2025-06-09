from typing import TypeVar

T = TypeVar('T')


def flatten(x: list[list[T]]) -> list[T]:
    """Flatten a list of lists into a single list."""
    return [item for sublist in x for item in sublist]

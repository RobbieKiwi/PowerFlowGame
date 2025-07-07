from typing import TypeVar

import numpy as np

T = TypeVar('T')


def random_choice_multi(x: list[T], size: int, **kwargs) -> list[T]:
    ixs = np.random.choice(a=[k for k in range(len(x))], size=size, **kwargs)
    return [x[ix] for ix in ixs]


def random_choice(x: list[T]) -> T:
    return random_choice_multi(x=x, size=1)[0]

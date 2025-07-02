from abc import ABC, abstractmethod
from functools import lru_cache, cached_property
from typing import Callable

import numpy as np

class RandomVariable(ABC):
    @abstractmethod
    def sample_numpy(self, n: int) -> np.ndarray: ...

    @abstractmethod
    def get_mean(self, exact: bool = False) -> float: ...

    @abstractmethod
    def get_variance(self, exact: bool = False) -> float: ...

    def sample(self, n: int) -> list[float]:
        return self.sample_numpy(n).tolist()

    def sample_one(self) -> float:
        return self.sample(1)[0]

    def __str__(self) -> str:
        mean = float(np.format_float_positional(x=self._mean_estimate, precision=3, fractional=False))
        var = float(np.format_float_positional(x=self._variance_estimate, precision=3, fractional=False))
        return f"<{self.__class__.__name__}: {mean=}, {var=}>"

    def __add__(self, other: "RandomVariable") -> "AnonymousRandomVariable":
        return AnonymousRandomVariable(func=lambda n: self.sample_numpy(n) + other.sample_numpy(n))

    @cached_property
    def _mean_estimate(self) -> float:
        return self.get_mean(exact=False)

    @cached_property
    def _variance_estimate(self) -> float:
        return self.get_variance(exact=False)

    # TODO add pdf and confidence interval methods

class AnonymousRandomVariable(RandomVariable):
    def __init__(self, func: Callable[[int], np.ndarray]) -> None:
        self._func = func

    def sample_numpy(self, n: int) -> np.ndarray:
        return self._func(n)

    def get_mean(self, exact: bool = False) -> float:
        if exact:
            raise NotImplementedError("Exact mean is not defined for anonymous random variables")
        return float(np.mean(self.sample(1000)))

    def get_variance(self, exact: bool = False) -> float:
        if exact:
            raise NotImplementedError("Exact variance is not defined for anonymous random variables")
        return float(np.var(self.sample(1000)))



class TransparentRandomVariable(RandomVariable, ABC):
    """
    A transparent random variable has a pdf that is clearly defined
    """
    @property
    @abstractmethod
    def mean(self) -> float: ...

    @property
    @abstractmethod
    def variance(self) -> float: ...

    def get_mean(self, exact: bool = False) -> float:
        return self.mean

    def get_variance(self, exact: bool = False) -> float:
        return self.variance


class NormalRandomVariable(TransparentRandomVariable):
    def __init__(self, mean: float, std_dev: float) -> None:
        self._mean = mean
        self._std_dev = std_dev

    @property
    def mean(self) -> float:
        return self._mean

    @property
    def variance(self) -> float:
        return self._std_dev ** 2

    def sample_numpy(self, n: int) -> np.ndarray:
        return np.random.normal(self.mean, self._std_dev, n)

class UniformRandomVariable(TransparentRandomVariable):
    def __init__(self, low: float, high: float) -> None:
        self._low = low
        self._high = high

    @property
    def mean(self) -> float:
        return (self._low + self._high) / 2

    @property
    def variance(self) -> float:
        return ((self._high - self._low) ** 2) / 12

    def sample_numpy(self, n: int) -> np.ndarray:
        return np.random.uniform(self._low, self._high, n)


if __name__ == "__main__":
    # Example usage
    rv_a = NormalRandomVariable(mean=1, std_dev=1)
    rv_b = NormalRandomVariable(mean=3, std_dev=1)
    assert rv_a.get_mean() == 1
    assert rv_b.get_mean() == 3
    rv_c = rv_a + rv_b
    assert isinstance(rv_c, AnonymousRandomVariable)
    print(rv_c.get_mean())
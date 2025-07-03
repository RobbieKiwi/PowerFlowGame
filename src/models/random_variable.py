from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import cached_property
from typing import Callable, TypeVar, Generic

import numpy as np

T = TypeVar("T")


@dataclass(frozen=True)
class Uncertainty(Generic[T]):
    value: T
    is_certain: bool


class RandomVariable(ABC):
    @abstractmethod
    def sample_numpy(self, n: int) -> np.ndarray: ...

    @abstractmethod
    def _get_mean(self) -> Uncertainty[float]: ...

    @abstractmethod
    def _get_variance(self) -> Uncertainty[float]: ...

    def get_mean(self, exact: bool = False) -> float:
        mean = self._get_mean()
        if exact and not mean.is_certain:
            raise NotImplementedError(f"Exact mean is not defined for {self.__class__.__name__}")
        return mean.value

    def get_variance(self, exact: bool = False) -> float:
        variance = self._get_variance()
        if exact and not variance.is_certain:
            raise NotImplementedError(f"Exact variance is not defined for {self.__class__.__name__}")
        return variance.value

    def sample(self, n: int) -> list[float]:
        return self.sample_numpy(n).tolist()

    def sample_one(self) -> float:
        return self.sample(1)[0]

    @cached_property
    def _mean_var_estimates(self) -> tuple[float, float]:
        return self.get_mean(), self.get_variance()

    def __str__(self) -> str:
        mean, var = self._mean_var_estimates
        mean = float(np.format_float_positional(x=mean, precision=3, fractional=False))
        var = float(np.format_float_positional(x=var, precision=3, fractional=False))
        return f"<{self.__class__.__name__}: {mean=}, {var=}>"

    def __add__(self, other: "RandomVariable") -> "AnonymousRandomVariable":
        return AnonymousRandomVariable(func=lambda n: self.sample_numpy(n) + other.sample_numpy(n))

    # TODO add pdf and confidence interval methods


class AnonymousRandomVariable(RandomVariable):
    def __init__(self, func: Callable[[int], np.ndarray]) -> None:
        self._func = func

    def sample_numpy(self, n: int) -> np.ndarray:
        return self._func(n)

    def _get_mean(self) -> Uncertainty[float]:
        return Uncertainty(value=float(np.mean(self.sample(1000))), is_certain=False)

    def _get_variance(self) -> Uncertainty[float]:
        return Uncertainty(value=float(np.var(self.sample(1000))), is_certain=False)


class NormalRandomVariable(RandomVariable):
    def __init__(self, mean: float, std_dev: float) -> None:
        self._mean = mean
        self._std_dev = std_dev

    def _get_mean(self) -> Uncertainty[float]:
        return Uncertainty(value=self._mean, is_certain=True)

    def _get_variance(self) -> Uncertainty[float]:
        return Uncertainty(value=self._std_dev**2, is_certain=True)

    def sample_numpy(self, n: int) -> np.ndarray:
        return np.random.normal(self._mean, self._std_dev, n)


class UniformRandomVariable(RandomVariable):
    def __init__(self, low: float, high: float) -> None:
        self._low = low
        self._high = high

    def _get_mean(self) -> Uncertainty[float]:
        return Uncertainty(value=(self._low + self._high) / 2, is_certain=True)

    def _get_variance(self) -> Uncertainty[float]:
        return Uncertainty(value=((self._high - self._low) ** 2) / 12, is_certain=True)

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

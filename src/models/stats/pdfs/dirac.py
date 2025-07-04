from functools import cached_property
from typing import Self

import numpy as np
from matplotlib.axes import Axes

from src.models.stats.models import Statistics, Uncertainty
from src.models.stats.pdfs.base import ProbabilityDistributionFunction


class DiracDeltaDistributionFunction(ProbabilityDistributionFunction):
    def __init__(self, value: float) -> None:
        self._value = value

    @cached_property
    def statistics(self) -> Statistics:
        return Statistics(
            mean=Uncertainty(value=self._value, is_certain=True),
            variance=Uncertainty(value=0.0, is_certain=True),
            min_value=Uncertainty(value=self._value, is_certain=True),
            max_value=Uncertainty(value=self._value, is_certain=True),
        )

    def scale_x(self, other: float) -> Self:
        return DiracDeltaDistributionFunction(value=self.mean * other)

    def sample_numpy(self, n: int) -> np.ndarray:
        return np.ones(n) * self._value

    def chance_that_rv_is_le(self, value: float) -> float:
        return 1.0 if value >= self._value else 0.0

    def value_that_is_at_le_chance(self, chance: float) -> float:
        return self._value

    def _get_plot_range(self) -> tuple[float, float]:
        plot_range = max(1.0, abs(self._value))
        start = self._value - plot_range
        end = self._value + plot_range
        return start, end

    def plot_pdf_on_axis(self, ax: Axes) -> None:
        ax.plot([self._value, self._value], [0, 1], linewidth=2)
        ax.scatter([self._value], [1], s=100, zorder=5)

    def plot_cdf_on_axis(self, ax: Axes) -> None:
        start, end = self._get_plot_range()
        ax.step([start, self._value, end], [0, 1, 1], where='post')
